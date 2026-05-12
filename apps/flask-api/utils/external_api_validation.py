"""Validation utilities for consuming third-party APIs securely."""

import logging
import requests
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError as JsonSchemaError
from utils.error_handlers import KIUError

log = logging.getLogger(__name__)


def validate_external_api_response(
    response: requests.Response,
    expected_schema: Dict[str, Any],
    timeout_seconds: int = 5,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Safely consume a third-party API response with validation.
    
    Args:
        response: The requests Response object
        expected_schema: JSON schema to validate response against
        timeout_seconds: Request timeout (should be enforced in caller)
        max_retries: Maximum retry attempts (should be enforced in caller)
        
    Returns:
        Validated response data as dict
        
    Raises:
        KIUError: If validation fails or response is invalid
    """
    
    # 1. Verify HTTPS
    if not response.url.startswith("https://"):
        raise KIUError("External API must use HTTPS", 422)
    
    # 2. Check HTTP status code
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        log.warning(f"External API returned error status: {response.status_code}")
        raise KIUError(
            f"External API error: {response.status_code}",
            422,
            error_code="EXTERNAL_API_ERROR"
        ) from e
    
    # 3. Validate Content-Type
    content_type = response.headers.get("content-type", "").lower()
    if "application/json" not in content_type:
        log.warning(f"Unexpected content-type from external API: {content_type}")
        raise KIUError("External API returned non-JSON response", 422)
    
    # 4. Parse JSON
    try:
        data = response.json()
    except ValueError as e:
        log.error("Failed to parse external API response as JSON")
        raise KIUError("Invalid JSON from external API", 422) from e
    
    # 5. Validate against schema
    try:
        validate(instance=data, schema=expected_schema)
    except JsonSchemaError as e:
        log.warning(f"External API response failed schema validation: {e.message}")
        raise KIUError(
            "External API response format invalid",
            422,
            error_code="EXTERNAL_API_SCHEMA_ERROR"
        ) from e
    
    return data


def safe_external_api_call(
    url: str,
    method: str = "GET",
    timeout: int = 5,
    max_retries: int = 1,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> requests.Response:
    """
    Make a secure call to an external API with safety checks.
    
    Args:
        url: HTTPS URL to call
        method: HTTP method (GET, POST, etc.)
        timeout: Request timeout in seconds
        max_retries: Number of retries on failure
        headers: Additional headers
        **kwargs: Additional arguments to pass to requests
        
    Returns:
        Response object
        
    Raises:
        KIUError: If URL is invalid or request fails
    """
    
    # 1. Validate URL is HTTPS
    if not url.startswith("https://"):
        raise KIUError("External API URL must use HTTPS", 422)
    
    # 2. Block internal network ranges
    from urllib.parse import urlparse
    parsed = urlparse(url)
    hostname = parsed.hostname
    
    blocked_hosts = [
        "localhost", "127.0.0.1", "::1",
        "0.0.0.0",  # All interfaces
        "169.254",  # Link-local
    ]
    
    if hostname and any(hostname.startswith(blocked) for blocked in blocked_hosts):
        raise KIUError("Cannot call internal/local URLs", 422)
    
    # 3. Enforce timeout
    if timeout <= 0 or timeout > 30:
        timeout = 5  # Default safe timeout
    
    # 4. Make request with retries
    request_headers = {
        "User-Agent": "KIU-Admission-Portal/1.0",
        **(headers or {})
    }
    
    last_exception = None
    for attempt in range(max_retries):
        try:
            log.debug(f"External API call attempt {attempt + 1}/{max_retries}: {method} {url}")
            
            response = requests.request(
                method=method,
                url=url,
                timeout=timeout,
                headers=request_headers,
                verify=True,  # Always verify SSL certificates
                **kwargs
            )
            
            return response
            
        except requests.Timeout as e:
            log.warning(f"External API call timed out after {timeout}s")
            last_exception = e
            continue
        
        except requests.ConnectionError as e:
            log.warning(f"Failed to connect to external API: {e}")
            last_exception = e
            continue
        
        except Exception as e:
            log.error(f"Unexpected error calling external API: {e}")
            last_exception = e
            break
    
    # If all retries exhausted
    raise KIUError(
        "Failed to call external API after retries",
        503,
        error_code="EXTERNAL_API_UNAVAILABLE"
    ) from last_exception


def validate_certificate_service_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate certificate verification service response.
    
    Args:
        data: Response data from certificate verification service
        
    Returns:
        Validated data
        
    Raises:
        KIUError: If validation fails
    """
    
    expected_schema = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["valid", "invalid", "pending", "error"]
            },
            "issue_date": {
                "type": "string",
                "pattern": r"^\d{4}-\d{2}-\d{2}$"
            },
            "certificate_number": {"type": "string"},
            "institution": {"type": "string"},
            "subject_area": {"type": "string"},
            "grade": {"type": "string"}
        },
        "required": ["status"]
    }
    
    try:
        validate(instance=data, schema=expected_schema)
        return data
    except JsonSchemaError as e:
        log.warning(f"Certificate service response validation failed: {e.message}")
        raise KIUError(
            "Invalid certificate verification response",
            422,
            error_code="CERT_VERIFICATION_INVALID"
        ) from e

"""OpenAPI/Swagger documentation for KIU Portal API."""
from flask import Blueprint, jsonify

docs_bp = Blueprint("docs", __name__)


@docs_bp.route("/openapi.json", methods=["GET"])
def openapi_spec():
    """Return OpenAPI 3.0 specification for the KIU Portal API."""
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "KIU Admission & Career Portal API",
            "version": "1.0.0",
            "description": "REST API for Kampala International University's admission and career portal.",
            "contact": {"email": "admissions@kiu.ac.ug"},
            "license": {"name": "MIT"},
        },
        "servers": [
            {"url": "/api", "description": "API Base URL"},
        ],
        "tags": [
            {"name": "Auth", "description": "Authentication endpoints"},
            {"name": "Admission", "description": "Admission application management"},
            {"name": "Career", "description": "Career paths and finalist profiles"},
            {"name": "Opportunities", "description": "Job and internship opportunities"},
            {"name": "Users", "description": "User management"},
        ],
        "paths": {
            "/auth/register": {
                "post": {
                    "tags": ["Auth"],
                    "summary": "Register a new user account",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/RegisterRequest"},
                            }
                        },
                    },
                    "responses": {
                        "201": {"description": "Account created, OTP sent"},
                        "400": {"description": "Validation error"},
                        "409": {"description": "Email already exists"},
                    },
                }
            },
            "/auth/login": {
                "post": {
                    "tags": ["Auth"],
                    "summary": "Authenticate user and obtain JWT token",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/LoginRequest"},
                            }
                        },
                    },
                    "responses": {
                        "200": {"description": "Login successful, returns JWT token"},
                        "401": {"description": "Invalid credentials"},
                        "403": {"description": "Email not verified"},
                    },
                }
            },
            "/auth/verify-otp": {
                "post": {
                    "tags": ["Auth"],
                    "summary": "Verify email with OTP code",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/VerifyOtpRequest"},
                            }
                        },
                    },
                    "responses": {
                        "200": {"description": "Email verified"},
                        "404": {"description": "Email not found"},
                        "410": {"description": "OTP expired"},
                        "422": {"description": "Invalid OTP"},
                    },
                }
            },
            "/auth/me": {
                "get": {
                    "tags": ["Auth"],
                    "summary": "Get current authenticated user",
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {"description": "User data"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/admission/programs": {
                "get": {
                    "tags": ["Admission"],
                    "summary": "List all academic programs",
                    "parameters": [
                        {"name": "level", "in": "query", "schema": {"type": "string", "enum": ["degree", "diploma", "hec", "masters", "phd"]}},
                        {"name": "campus", "in": "query", "schema": {"type": "string", "enum": ["kampala", "western"]}},
                    ],
                    "responses": {
                        "200": {"description": "List of programs"},
                    },
                }
            },
            "/admission/applications": {
                "post": {
                    "tags": ["Admission"],
                    "summary": "Submit a new admission application",
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ApplicationRequest"},
                            }
                        },
                    },
                    "responses": {
                        "201": {"description": "Application created"},
                        "400": {"description": "Validation error"},
                        "409": {"description": "User already has an application"},
                    },
                },
                "get": {
                    "tags": ["Admission"],
                    "summary": "List applications (admin only)",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                        {"name": "perPage", "in": "query", "schema": {"type": "integer", "default": 20}},
                        {"name": "status", "in": "query", "schema": {"type": "string"}},
                        {"name": "search", "in": "query", "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"description": "Paginated list of applications"},
                        "403": {"description": "Forbidden"},
                    },
                },
            },
            "/opportunities": {
                "get": {
                    "tags": ["Opportunities"],
                    "summary": "List active opportunities",
                    "parameters": [
                        {"name": "type", "in": "query", "schema": {"type": "string", "enum": ["job", "internship"]}},
                        {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                        {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 20}},
                    ],
                    "responses": {
                        "200": {"description": "List of opportunities"},
                    },
                },
                "post": {
                    "tags": ["Opportunities"],
                    "summary": "Create a new opportunity (admin only)",
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/OpportunityRequest"},
                            }
                        },
                    },
                    "responses": {
                        "201": {"description": "Opportunity created"},
                        "403": {"description": "Forbidden"},
                    },
                },
            },
            "/career/paths": {
                "get": {
                    "tags": ["Career"],
                    "summary": "List career paths",
                    "parameters": [
                        {"name": "program", "in": "query", "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"description": "List of career paths"},
                    },
                }
            },
            "/healthz": {
                "get": {
                    "tags": ["System"],
                    "summary": "Health check endpoint",
                    "responses": {
                        "200": {"description": "Service is healthy"},
                    },
                }
            },
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            },
            "schemas": {
                "RegisterRequest": {
                    "type": "object",
                    "required": ["email", "password", "firstName", "lastName"],
                    "properties": {
                        "email": {"type": "string", "format": "email", "example": "student@example.com"},
                        "password": {"type": "string", "minLength": 8, "description": "Must contain uppercase, lowercase, and digit", "example": "Secure123"},
                        "firstName": {"type": "string", "example": "John"},
                        "lastName": {"type": "string", "example": "Doe"},
                        "phone": {"type": "string", "example": "+256700000000"},
                        "nationalId": {"type": "string"},
                        "role": {"type": "string", "enum": ["applicant", "finalist"], "default": "applicant"},
                    },
                },
                "LoginRequest": {
                    "type": "object",
                    "required": ["email", "password"],
                    "properties": {
                        "email": {"type": "string", "format": "email"},
                        "password": {"type": "string"},
                    },
                },
                "VerifyOtpRequest": {
                    "type": "object",
                    "required": ["email", "code"],
                    "properties": {
                        "email": {"type": "string", "format": "email"},
                        "code": {"type": "string", "pattern": "^[0-9]{6}$"},
                    },
                },
                "ApplicationRequest": {
                    "type": "object",
                    "required": ["programIds", "examLevel", "examYear", "indexNumber", "unebGrades", "dateOfBirth", "gender"],
                    "properties": {
                        "programIds": {"type": "array", "items": {"type": "integer"}, "minItems": 1, "maxItems": 3},
                        "examLevel": {"type": "string", "enum": ["o_level", "a_level", "diploma", "hec", "masters", "phd"]},
                        "examYear": {"type": "integer"},
                        "indexNumber": {"type": "string"},
                        "unebGrades": {"type": "object"},
                        "dateOfBirth": {"type": "string", "format": "date"},
                        "gender": {"type": "string", "enum": ["male", "female", "other"]},
                    },
                },
                "OpportunityRequest": {
                    "type": "object",
                    "required": ["title", "organization", "type", "description", "requirements", "applicationDeadline"],
                    "properties": {
                        "title": {"type": "string"},
                        "organization": {"type": "string"},
                        "type": {"type": "string", "enum": ["job", "internship"]},
                        "description": {"type": "string"},
                        "requirements": {"type": "string"},
                        "applicationDeadline": {"type": "string", "format": "date"},
                    },
                },
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "email": {"type": "string"},
                        "firstName": {"type": "string"},
                        "lastName": {"type": "string"},
                        "role": {"type": "string", "enum": ["applicant", "finalist", "admin"]},
                        "isVerified": {"type": "boolean"},
                    },
                },
                "Program": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "code": {"type": "string"},
                        "faculty": {"type": "string"},
                        "level": {"type": "string"},
                        "campus": {"type": "string"},
                    },
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string"},
                        "message": {"type": "string"},
                    },
                },
            },
        },
    }
    return jsonify(spec)
"""
Strict Input Validation Schemas
OWASP-compliant validation for all API inputs
"""
import re
from marshmallow import Schema, fields, validate, ValidationError, pre_load, RAISE
from email_validator import validate_email, EmailNotValidError


class StrictSchema(Schema):
    """Base schema with strict validation - rejects unknown fields"""
    class Meta:
        unknown = RAISE  # Strict: reject unknown fields
        ordered = True


class EmailField(fields.String):
    """Email field with strict validation"""
    def _validate(self, value):
        super()._validate(value)
        try:
            validate_email(value, check_deliverability=False)
        except EmailNotValidError as e:
            raise ValidationError(f"Invalid email: {str(e)}")


class PasswordField(fields.String):
    """Password field with strength requirements"""
    def __init__(self, min_length=8, require_upper=True, require_lower=True, 
                 require_digit=True, require_special=True, **kwargs):
        self.min_length = min_length
        self.require_upper = require_upper
        self.require_lower = require_lower
        self.require_digit = require_digit
        self.require_special = require_special
        super().__init__(**kwargs)
    
    def _validate(self, value):
        super()._validate(value)
        errors = []
        
        if len(value) < self.min_length:
            errors.append(f"at least {self.min_length} characters")
        if self.require_upper and not re.search(r'[A-Z]', value):
            errors.append("one uppercase letter")
        if self.require_lower and not re.search(r'[a-z]', value):
            errors.append("one lowercase letter")
        if self.require_digit and not re.search(r'\d', value):
            errors.append("one digit")
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            errors.append("one special character")
        
        if errors:
            raise ValidationError(f"Password must contain: {', '.join(errors)}")


class LoginSchema(StrictSchema):
    """Strict login validation"""
    email = EmailField(required=True)
    password = fields.String(required=True, validate=validate.Length(min=1, max=128))
    
    @pre_load
    def normalize_email(self, data, **kwargs):
        if isinstance(data, dict) and 'email' in data:
            data['email'] = str(data['email']).strip().lower()
        return data


class RegisterSchema(StrictSchema):
    """Strict registration validation"""
    email = EmailField(required=True)
    password = PasswordField(required=True, min_length=8)
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    phone = fields.String(validate=validate.Regexp(r'^[\d\s\-\+\(\)]+$', error="Invalid phone number"), 
                          load_default=None)
    
    @pre_load
    def strip_whitespace(self, data, **kwargs):
        if isinstance(data, dict):
            for field in ['first_name', 'last_name']:
                if field in data:
                    data[field] = str(data[field]).strip()
        return data


class VerifyOtpSchema(StrictSchema):
    """OTP verification validation"""
    email = EmailField(required=True)
    otp = fields.String(required=True, validate=validate.Regexp(r'^\d{6}$', error="OTP must be 6 digits"))


class ForgotPasswordSchema(StrictSchema):
    """Forgot password validation"""
    email = EmailField(required=True)


class ResetPasswordSchema(StrictSchema):
    """Reset password validation"""
    token = fields.String(required=True, validate=validate.Length(min=10))
    new_password = PasswordField(required=True, min_length=8)


class RefreshTokenSchema(StrictSchema):
    """Refresh token validation"""
    refresh_token = fields.String(required=True, validate=validate.Length(min=10))


class PaginationSchema(StrictSchema):
    """Pagination parameters"""
    page = fields.Integer(validate=validate.Range(min=1), load_default=1, missing=1)
    per_page = fields.Integer(validate=validate.Range(min=1, max=100), load_default=20, missing=20)


def validate_json(schema_class):
    """Decorator to validate JSON input against schema"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.get_json(silent=True) or {}
            schema = schema_class()
            try:
                validated = schema.load(data)
                request.validated_data = validated
                return f(*args, **kwargs)
            except ValidationError as e:
                return jsonify({
                    "status": "fail",
                    "message": "Validation error",
                    "errors": e.messages
                }), 400
        return wrapper
    return decorator


from functools import wraps
from flask import request, jsonify

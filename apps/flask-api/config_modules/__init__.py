"""
Configuration package for KIU Portal
"""
from .linkedin import LinkedInConfig, LINKEDIN_TOKEN_URL, LINKEDIN_USERINFO_URL, LINKEDIN_OAUTH_URL, LINKEDIN_SCOPES

__all__ = [
    'LinkedInConfig',
    'LINKEDIN_TOKEN_URL',
    'LINKEDIN_USERINFO_URL',
    'LINKEDIN_OAUTH_URL',
    'LINKEDIN_SCOPES'
]

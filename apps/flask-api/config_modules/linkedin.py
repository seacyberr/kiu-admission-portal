"""
LinkedIn OAuth Configuration for KIU Admission Portal
"""
import os
from typing import Dict, Optional

# LinkedIn OAuth Settings
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")
LINKEDIN_REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:5000/api/auth/linkedin/callback")

# OAuth Scopes needed
# - openid: Basic profile info
# - profile: Full profile details
# - email: Email address
# - w_member_social: Post on behalf of user (optional)
LINKEDIN_SCOPES = ["openid", "profile", "email"]

# LinkedIn API Endpoints
LINKEDIN_OAUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_API_BASE = "https://api.linkedin.com/v2"
LINKEDIN_USERINFO_URL = "https://api.linkedin.com/v2/userinfo"

# Profile fields we want to import
LINKEDIN_PROFILE_FIELDS = [
    "id",
    "firstName",
    "lastName",
    "profilePicture",
    "email",
    "headline",
    "industry",
    "location",
    "summary",
    "positions",
    "educations",
    "skills",
    "publicProfileUrl"
]

def get_linkedin_oauth_url(state: str) -> str:
    """Generate LinkedIn OAuth authorization URL"""
    from urllib.parse import urlencode
    
    params = {
        "response_type": "code",
        "client_id": LINKEDIN_CLIENT_ID,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "scope": " ".join(LINKEDIN_SCOPES),
        "state": state
    }
    
    return f"{LINKEDIN_OAUTH_URL}?{urlencode(params)}"


def validate_linkedin_config() -> bool:
    """Check if LinkedIn OAuth is properly configured"""
    return bool(LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET and LINKEDIN_REDIRECT_URI)


class LinkedInConfig:
    """LinkedIn configuration class"""
    
    CLIENT_ID = LINKEDIN_CLIENT_ID
    CLIENT_SECRET = LINKEDIN_CLIENT_SECRET
    REDIRECT_URI = LINKEDIN_REDIRECT_URI
    SCOPES = LINKEDIN_SCOPES
    
    @classmethod
    def is_configured(cls) -> bool:
        return bool(cls.CLIENT_ID and cls.CLIENT_SECRET)
    
    @classmethod
    def get_auth_url(cls, state: str) -> str:
        from urllib.parse import urlencode
        
        params = {
            "response_type": "code",
            "client_id": cls.CLIENT_ID,
            "redirect_uri": cls.REDIRECT_URI,
            "scope": " ".join(cls.SCOPES),
            "state": state
        }
        
        return f"{LINKEDIN_OAUTH_URL}?{urlencode(params)}"

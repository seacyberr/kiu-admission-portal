"""
Application Configuration - Environment-based settings
"""
import os
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    uri: str
    track_modifications: bool = False
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20


@dataclass
class SecurityConfig:
    """Security-related configuration"""
    jwt_secret: str
    jwt_access_token_hours: int = 24
    jwt_refresh_token_days: int = 30
    bcrypt_log_rounds: int = 12
    enable_security_headers: bool = True
    enable_hsts: bool = False


@dataclass
class AppConfig:
    """Main application configuration"""
    env: str
    debug: bool
    testing: bool
    secret_key: str
    database: DatabaseConfig
    security: SecurityConfig
    upload_folder: str
    max_content_length: int = 16 * 1024 * 1024  # 16MB
    cors_origins: List[str]
    sentry_dsn: Optional[str] = None


class ConfigFactory:
    """Factory for creating environment-specific configurations"""
    
    @staticmethod
    def create(env: str = None) -> AppConfig:
        env = env or os.environ.get("FLASK_ENV", "development")
        
        base_db_uri = os.environ.get(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/kiu_portal"
        )
        
        jwt_secret = os.environ.get("JWT_SECRET") or os.environ.get("SECRET_KEY", "dev-secret-key")
        
        configs = {
            "development": AppConfig(
                env="development",
                debug=True,
                testing=False,
                secret_key=jwt_secret,
                database=DatabaseConfig(
                    uri=base_db_uri,
                    echo=True
                ),
                security=SecurityConfig(
                    jwt_secret=jwt_secret,
                    enable_hsts=False
                ),
                upload_folder=os.environ.get("UPLOAD_FOLDER", "/tmp/uploads"),
                cors_origins=["http://localhost:5173", "http://localhost:3000"]
            ),
            "production": AppConfig(
                env="production",
                debug=False,
                testing=False,
                secret_key=jwt_secret,
                database=DatabaseConfig(
                    uri=base_db_uri,
                    echo=False,
                    pool_size=20,
                    max_overflow=30
                ),
                security=SecurityConfig(
                    jwt_secret=jwt_secret,
                    jwt_access_token_hours=12,
                    enable_hsts=True
                ),
                upload_folder=os.environ.get("UPLOAD_FOLDER", "/var/www/uploads"),
                cors_origins=os.environ.get("CORS_ORIGINS", "https://kiu.ac.ug").split(","),
                sentry_dsn=os.environ.get("SENTRY_DSN")
            ),
            "testing": AppConfig(
                env="testing",
                debug=False,
                testing=True,
                secret_key="test-secret-key",
                database=DatabaseConfig(
                    uri="sqlite:///:memory:",
                    echo=False
                ),
                security=SecurityConfig(
                    jwt_secret="test-jwt-secret",
                    jwt_access_token_hours=1
                ),
                upload_folder="/tmp/test_uploads",
                cors_origins=["*"]
            )
        }
        
        return configs.get(env, configs["development"])

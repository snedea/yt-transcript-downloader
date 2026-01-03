"""Configuration management for the application"""
import os
from typing import List
from dotenv import load_dotenv, find_dotenv

# Load environment variables from project root
load_dotenv(find_dotenv())


class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # OpenAI Configuration
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        
        # Environment Configuration
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        
        # CORS Configuration - support multiple localhost ports for development
        cors_origins_str = os.getenv(
            "CORS_ORIGINS", 
            "http://localhost:3000,http://localhost:8080"
        )
        self.CORS_ORIGINS: List[str] = cors_origins_str.split(",")
        
        # Add additional development ports
        if self.ENVIRONMENT == "development":
            self.CORS_ORIGINS.extend([
                "http://localhost:5173",
                "http://localhost:3001"
            ])
        
        # API Configuration
        self.API_RATE_LIMIT = os.getenv("API_RATE_LIMIT", "100/minute")
        
        # Auth Configuration
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-in-production-use-openssl-rand-hex-32")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        
        # OAuth Configuration
        self.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
        self.GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
        self.GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
        self.GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
        self.OAUTH_REDIRECT_BASE = os.getenv("OAUTH_REDIRECT_BASE", "http://localhost:3000")
        
    def validate_api_key(self) -> bool:
        """Validate OpenAI API key format"""
        if not self.OPENAI_API_KEY:
            return False
        return self.OPENAI_API_KEY.startswith("sk-")

    def validate_jwt_secret(self) -> bool:
        """
        Validate JWT secret key security.

        Returns:
            True if JWT secret is properly configured, False otherwise.

        Security requirements:
        - Must not be the default value in production
        - Should be at least 32 characters for security
        """
        # Check if using default secret
        default_secret = "change-this-in-production-use-openssl-rand-hex-32"
        if self.JWT_SECRET_KEY == default_secret:
            if self.ENVIRONMENT == "production":
                return False
            else:
                # Warn in development but allow
                return True

        # Check minimum length
        if len(self.JWT_SECRET_KEY) < 32:
            return False

        return True

    def validate_security_config(self) -> tuple[bool, list[str]]:
        """
        Validate all security-critical configuration.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # JWT Secret validation
        if not self.validate_jwt_secret():
            if self.ENVIRONMENT == "production" and self.JWT_SECRET_KEY == "change-this-in-production-use-openssl-rand-hex-32":
                errors.append(
                    "CRITICAL: Using default JWT_SECRET_KEY in production! "
                    "Generate a secure secret with: openssl rand -hex 32"
                )
            elif len(self.JWT_SECRET_KEY) < 32:
                errors.append(
                    "JWT_SECRET_KEY is too short. Must be at least 32 characters. "
                    "Generate with: openssl rand -hex 32"
                )

        # OAuth validation for production
        if self.ENVIRONMENT == "production":
            if not self.GOOGLE_CLIENT_ID and not self.GITHUB_CLIENT_ID:
                # Not an error, just informational
                pass

        return (len(errors) == 0, errors)


# Global settings instance
settings = Settings()

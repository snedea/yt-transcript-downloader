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
        
    def validate_api_key(self) -> bool:
        """Validate OpenAI API key format"""
        if not self.OPENAI_API_KEY:
            return False
        return self.OPENAI_API_KEY.startswith("sk-")


# Global settings instance
settings = Settings()

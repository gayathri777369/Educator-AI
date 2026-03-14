"""
Configuration settings for EducatorAI
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # Model configuration
    model_name: str = "ibm-granite/granite-3.3-2b-instruct"
    model_cache_dir: Optional[str] = None
    max_length: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    
    # API configuration
    api_title: str = "EducatorAI"
    api_version: str = "1.0.0"
    
    # Hugging Face configuration
    HF_TOKEN = os.getenv("HF_TOKEN")
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = True
    
    # Rate limiting
    max_requests_per_minute: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
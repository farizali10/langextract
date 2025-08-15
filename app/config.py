"""Configuration settings for the FastAPI LangExtract application."""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    langextract_api_key: str = ""
    openai_api_key: str = ""
    
    # File upload settings
    max_file_size_mb: int = 10
    allowed_file_types: str = "txt,pdf,docx,xlsx,png,jpg,jpeg"
    
    # LangExtract settings
    default_model: str = "gemini-2.5-flash"
    max_workers: int = 10
    extraction_passes: int = 2
    max_char_buffer: int = 1000
    
    # Application settings
    app_title: str = "LangExtract Document Processing API"
    app_description: str = "Extract structured information from documents using Google's LangExtract library"
    app_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Get allowed file types as a list."""
        return [ext.strip().lower() for ext in self.allowed_file_types.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024


# Global settings instance
settings = Settings()

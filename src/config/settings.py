"""
Configuration settings for Hackademia AI Pipeline
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # GitHub Configuration
    github_token: Optional[str] = None
    github_webhook_secret: Optional[str] = None
    
    # AI Model Configuration
    gemini_api_key: Optional[str] = None
    
    # CodeGPT Configuration (for MCP)
    codegpt_api_key: Optional[str] = None
    codegpt_org_id: Optional[str] = None
    codegpt_graph_id: Optional[str] = None
    
    # Application Configuration
    port: int = 8000
    debug: bool = True
    
    # Agent Configuration
    max_confidence_threshold: float = 0.8
    auto_fix_enabled: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()

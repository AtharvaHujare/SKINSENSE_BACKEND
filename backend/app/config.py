"""
SkinSense AI - Core Configuration Module.

Manages application settings, environment variables, and configuration options.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application Settings schema loaded from environment variables or defaults.
    """
    APP_NAME: str = "SkinSense AI Backend"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Production-grade FastAPI backend for AI Skin Cancer Detection System"
    ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database Configuration Placeholder
    # DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/skinsense"

    # Storage Settings
    UPLOADS_DIR: str = "uploads"
    REPORTS_DIR: str = "reports"
    TRAINED_MODELS_DIR: str = "trained_models"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instantiate configuration object for global use
settings = Settings()

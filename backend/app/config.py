"""
SkinSense AI - Core Configuration Module.

Manages application settings, environment variables, security tokens, and database parameters.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_DIR = BASE_DIR / "backend" / "database"
DB_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_DB_FILE = DB_DIR / "skinsense.db"


class Settings(BaseSettings):
    """
    Application Settings schema loaded from environment variables (.env) or defaults.
    Uses SQLite database engine for local development.
    """

    # Core Application Settings
    APP_NAME: str = "SkinSense AI Backend"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = (
        "Production-grade FastAPI backend for AI Skin Cancer Detection System"
    )
    ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Security & JWT Configuration
    SECRET_KEY: str = "skinsense-super-secret-key-change-in-production-32bytes"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database Configuration Parameters (SQLite Development Engine)
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DEFAULT_DB_FILE.as_posix()}"

    # Storage Settings
    UPLOADS_DIR: str = "uploads"
    REPORTS_DIR: str = "reports"
    TRAINED_MODELS_DIR: str = "trained_models"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Global settings singleton instance
settings = Settings()

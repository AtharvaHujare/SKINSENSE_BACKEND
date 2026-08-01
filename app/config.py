"""
SkinSense AI - Core Configuration Module.

Manages application settings, environment variables, and database connection settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings schema loaded from environment variables (.env) or defaults.
    Dynamically constructs database connection strings from individual environment parameters.
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

    # Database Configuration Parameters
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "skinsense_db"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"

    # Database Connection Pool Settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30

    # Storage Settings
    UPLOADS_DIR: str = "uploads"
    REPORTS_DIR: str = "reports"
    TRAINED_MODELS_DIR: str = "trained_models"

    @property
    def DATABASE_URL(self) -> str:
        """
        Dynamically constructs asynchronous PostgreSQL DSN connection string.
        Format: postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE
        """
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Global settings singleton instance
settings = Settings()

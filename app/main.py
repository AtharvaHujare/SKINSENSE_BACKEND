"""
SkinSense AI - Main Application Entry Point.

Initializes the FastAPI application, startup connection verification, and mounts routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.api.health import router as health_router
from app.database.database import verify_database_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager handling startup and shutdown events.
    Verifies database connectivity upon server startup.
    """
    # Startup logic: verify database connectivity
    await verify_database_connection()
    yield
    # Shutdown logic (if any cleanup is required)


# Initialize FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
)


@app.get("/", summary="Root status check")
async def root():
    """
    Root endpoint verifying server availability.
    """
    return {"message": "SkinSense AI Backend Running"}


# Register API Routers
app.include_router(health_router)

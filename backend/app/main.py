"""
SkinSense AI - Main Application Entry Point.

Initializes the FastAPI application, mounts API routers, middleware, and core handlers.
"""

from fastapi import FastAPI
from app.config import settings
from app.api.health import router as health_router

# Initialize FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
)


@app.get("/", summary="Root status check")
async def root():
    """
    Root endpoint verifying server availability.
    """
    return {"message": "SkinSense AI Backend Running"}


# Register API Routers
app.include_router(health_router)

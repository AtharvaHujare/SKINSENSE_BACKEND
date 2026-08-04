"""
SkinSense AI - Main Application Entry Point.

Initializes the FastAPI application, mounts API routers (auth, health, analysis), and handles startup events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.api.health import router as health_router
from app.api.analysis import router as analysis_router
from app.api.report import router as report_router
from app.api.doctor import router as doctor_router
from app.auth.routes import router as auth_router
from app.database.database import verify_database_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager handling startup and shutdown events.
    Verifies database connectivity upon server startup.
    """
    await verify_database_connection()
    yield


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
app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(report_router)
app.include_router(doctor_router)

"""
SkinSense AI - Main Application Entry Point.

Initializes the FastAPI application, mounts API routers, middleware, and core handlers.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.health import router as health_router
from app.api.predict import router as predict_router
from app.reports.pdf_report import generate_skin_report

# Initialize FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
)

# Serve Grad-CAM images
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "ai" / "outputs"

app.mount(
    "/outputs",
    StaticFiles(directory=OUTPUT_DIR),
    name="outputs",
)


@app.get("/", summary="Root status check")
async def root():
    """
    Root endpoint verifying server availability.
    """
    return {"message": "SkinSense AI Backend Running"}


# Register API Routers
app.include_router(health_router)
app.include_router(predict_router)
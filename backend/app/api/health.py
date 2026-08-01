"""
Health Check API Endpoints.
"""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Perform system health check")
async def health_check():
    """
    Health check endpoint returning system operational status.
    """
    return {"status": "healthy"}

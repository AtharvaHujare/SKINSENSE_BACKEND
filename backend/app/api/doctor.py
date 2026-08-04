"""
SkinSense AI - Doctor Dashboard API Endpoints.

Provides endpoints for physician dashboard metrics, pending analysis queues, and reviewed histories.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.auth.dependencies import RoleChecker
from app.schemas.dashboard import (
    DoctorDashboardResponse,
    PendingAnalysisItem,
    ReviewedAnalysisItem
)
from app.services.doctor_service import doctor_service

router = APIRouter(prefix="/doctor", tags=["Doctor Dashboard"])

# Enforce DOCTOR & ADMIN role access
doctor_or_admin = RoleChecker(allowed_roles=["DOCTOR", "ADMIN"])


@router.get(
    "/dashboard",
    response_model=DoctorDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get physician dashboard overview",
    description="Retrieves dashboard metric counters, recent pending cases, and recent reviewed cases for authenticated doctors."
)
async def get_doctor_dashboard(
    current_user: User = Depends(doctor_or_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Fetches physician dashboard overview metrics and recent case lists.
    """
    return await doctor_service.get_dashboard(
        session=session,
        current_user=current_user
    )


@router.get(
    "/pending",
    response_model=List[PendingAnalysisItem],
    status_code=status.HTTP_200_OK,
    summary="Get pending analysis queue",
    description="Retrieves cases where AI prediction is completed (status == COMPLETED) awaiting physician review, ordered newest first."
)
async def get_pending_queue(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(doctor_or_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Fetches list of completed analyses awaiting physician review.
    """
    return await doctor_service.get_pending(
        session=session,
        current_user=current_user,
        skip=skip,
        limit=limit
    )


@router.get(
    "/reviewed",
    response_model=List[ReviewedAnalysisItem],
    status_code=status.HTTP_200_OK,
    summary="Get reviewed analysis history",
    description="Retrieves history of cases reviewed by physicians (status == REVIEWED), including patient names, diagnosis, and timestamps."
)
async def get_reviewed_history(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(doctor_or_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Fetches list of analyses reviewed by doctors.
    """
    return await doctor_service.get_reviewed(
        session=session,
        current_user=current_user,
        skip=skip,
        limit=limit
    )

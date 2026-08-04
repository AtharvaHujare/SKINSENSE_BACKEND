"""
SkinSense AI - Report & Doctor Review API Endpoints.

Provides endpoints for physician reviews and diagnostic report management.
"""

import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.auth.dependencies import RoleChecker
from app.schemas.review import DoctorReviewRequest, DoctorReviewResponse
from app.services.report_service import report_service

router = APIRouter(prefix="/analysis", tags=["Reports & Reviews"])

# Enforce DOCTOR role authorization
doctor_only = RoleChecker(allowed_roles=["DOCTOR"])


@router.post(
    "/{analysis_id}/review",
    response_model=DoctorReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit physician review for AI analysis",
    description=(
        "Allows authenticated Doctor users to review a COMPLETED AI analysis session, "
        "providing diagnostic assessment, clinical notes, and patient treatment recommendations."
    )
)
async def submit_doctor_review(
    analysis_id: uuid.UUID,
    review_request: DoctorReviewRequest,
    current_user: User = Depends(doctor_only),
    session: AsyncSession = Depends(get_db)
):
    """
    Delegates physician review submission to ReportService.
    """
    return await report_service.review_analysis(
        session=session,
        current_user=current_user,
        analysis_id=analysis_id,
        request=review_request
    )

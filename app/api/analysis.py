"""
SkinSense AI - Lesion Analysis API Endpoints.

Provides endpoints for uploading skin lesion images, executing validations, persisting storage,
and creating Analysis database records.
"""

import uuid
from typing import List
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.auth.dependencies import RoleChecker, get_current_active_user
from app.schemas.analysis import (
    AnalysisUploadResponse,
    AnalysisDetailResponse,
    PredictionResponse
)
from app.services.analysis_service import analysis_service

router = APIRouter(prefix="/analysis", tags=["Analysis"])

# Instantiate RBAC RoleChecker permitting only PATIENT role access
patient_only = RoleChecker(allowed_roles=["PATIENT"])


@router.post(
    "/upload",
    response_model=AnalysisUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload skin lesion image for AI analysis",
    description=(
        "Accepts a skin lesion image file (multipart/form-data) from authenticated "
        "Patient users, validates file parameters, saves image to storage, and persists "
        "an Analysis session record in PostgreSQL."
    )
)
async def upload_lesion_image(
    file: UploadFile = File(..., description="Skin lesion image file (JPEG, PNG, WebP)"),
    lesion_body_location: str = Form(..., example="Left Forearm", description="Anatomical location of the skin lesion"),
    current_user: User = Depends(patient_only),
    session: AsyncSession = Depends(get_db)
):
    """
    Delegates to AnalysisService for complete upload validation, storage, and DB persistence pipeline.
    """
    return await analysis_service.process_lesion_upload(
        session=session,
        current_user=current_user,
        file=file,
        lesion_body_location=lesion_body_location
    )


@router.get(
    "/history",
    response_model=List[AnalysisDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Get patient analysis history",
    description="Retrieves a list of previous analysis sessions for the authenticated patient, ordered newest first."
)
async def get_patient_analysis_history(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(patient_only),
    session: AsyncSession = Depends(get_db)
):
    """
    Fetches historical analysis sessions for the authenticated patient user ordered newest first.
    """
    return await analysis_service.get_history(
        session=session,
        current_user=current_user,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{analysis_id}",
    response_model=AnalysisDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get analysis session information",
    description="Retrieves full analysis information, current workflow status, and AI prediction details if available."
)
async def get_analysis_by_id(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Fetches analysis session details and prediction object for authorized users.
    """
    return await analysis_service.get_analysis(
        session=session,
        current_user=current_user,
        analysis_id=analysis_id
    )


@router.get(
    "/{analysis_id}/prediction",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get analysis prediction results",
    description="Retrieves the AI prediction classification label, confidence score, risk level, and heatmap path for an analysis."
)
async def get_analysis_prediction_by_id(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Fetches the prediction result details for a specific analysis session.
    """
    return await analysis_service.get_prediction(
        session=session,
        current_user=current_user,
        analysis_id=analysis_id
    )

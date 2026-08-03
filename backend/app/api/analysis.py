"""
SkinSense AI - Lesion Analysis API Endpoints.

Provides endpoints for uploading skin lesion images, executing validations, persisting storage,
and creating Analysis database records.
"""

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.auth.dependencies import RoleChecker
from app.schemas.analysis import AnalysisUploadResponse
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

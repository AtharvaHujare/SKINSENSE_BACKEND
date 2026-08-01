"""
SkinSense AI - Lesion Analysis API Endpoints.

Provides endpoints for uploading skin lesion images and retrieving analysis session statuses.
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.auth.dependencies import get_current_active_user, RoleChecker
from app.schemas.analysis import AnalysisUploadResponse

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
        "Patient users and initializes a new AI analysis session."
    )
)
async def upload_lesion_image(
    file: UploadFile = File(..., description="Skin lesion image file (JPEG/PNG)"),
    lesion_body_location: str = Form(..., example="Left Forearm", description="Anatomical location of the skin lesion"),
    current_user: User = Depends(patient_only),
    session: AsyncSession = Depends(get_db)
):
    """
    Endpoint skeleton accepting lesion image upload and returning initial analysis status payload.
    Enforces JWT authentication and PATIENT role authorization.
    """
    # Generate placeholder analysis UUID for skeleton response
    placeholder_analysis_id = uuid.uuid4()
    
    return AnalysisUploadResponse(
        analysis_id=placeholder_analysis_id,
        status="PENDING",
        message="Lesion image uploaded successfully. Analysis session initialized.",
        image_url=f"/uploads/{placeholder_analysis_id}_{file.filename}",
        created_at=datetime.now(timezone.utc)
    )

"""
SkinSense AI - Lesion Analysis API Endpoints.

Provides endpoints for uploading skin lesion images, executing validations, and persisting storage.
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.auth.dependencies import RoleChecker
from app.schemas.analysis import AnalysisUploadResponse
from app.utils.file_validator import validate_image_file
from app.utils.file_storage import save_uploaded_image

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
        "Patient users, validates format/size, saves the file to disk, and initializes an analysis session."
    )
)
async def upload_lesion_image(
    file: UploadFile = File(..., description="Skin lesion image file (JPEG, PNG, WebP)"),
    lesion_body_location: str = Form(..., example="Left Forearm", description="Anatomical location of the skin lesion"),
    current_user: User = Depends(patient_only),
    session: AsyncSession = Depends(get_db)
):
    """
    Complete upload pipeline:
    1. Validate image format, size (<10MB), and content.
    2. Save image asynchronously to uploads/patients/{patient_id}/{uuid}.{ext}.
    3. Return analysis upload confirmation response.
    """
    # 1. Validate file payload
    await validate_image_file(file)

    # 2. Store file asynchronously on disk
    storage_result = await save_uploaded_image(file, patient_id=str(current_user.id))

    # Generate analysis ID for session reference
    analysis_id = uuid.uuid4()

    return AnalysisUploadResponse(
        analysis_id=analysis_id,
        status="PENDING",
        message="Image uploaded successfully",
        image_url=storage_result["relative_path"],
        created_at=datetime.now(timezone.utc)
    )

"""
SkinSense AI - Analysis Service Layer.

Orchestrates the skin lesion upload, validation, asynchronous storage, and database persistence pipeline.
"""

import os
import uuid
import logging
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.patient import Patient
from app.schemas.analysis import AnalysisUploadResponse
from app.repositories.analysis_repository import analysis_repository
from app.utils.file_validator import validate_image_file
from app.utils.file_storage import save_uploaded_image

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Business service orchestrating the skin lesion analysis workflow.
    """

    async def process_lesion_upload(
        self,
        session: AsyncSession,
        current_user: User,
        file: UploadFile,
        lesion_body_location: str
    ) -> AnalysisUploadResponse:
        """
        Executes complete upload workflow:
        1. Validate uploaded image (MIME, size, extension, non-empty).
        2. Resolve associated Patient profile ID.
        3. Save file asynchronously to disk.
        4. Persist Analysis record in database.
        5. Clean up stored file if database transaction fails.
        """
        # 1. Validate image payload
        await validate_image_file(file)

        # 2. Resolve Patient ID for current user
        statement = select(Patient).where(Patient.user_id == current_user.id)
        result = await session.execute(statement)
        patient_profile = result.scalar_one_or_none()

        if patient_profile:
            patient_id = patient_profile.id
        else:
            patient_id = current_user.id

        # 3. Store file asynchronously on disk
        storage_result = await save_uploaded_image(file, patient_id=str(patient_id))
        saved_abs_path = storage_result["absolute_path"]
        relative_path = storage_result["relative_path"]

        # 4. Persist Analysis database record with rollback cleanup
        try:
            analysis_record = await analysis_repository.create_analysis(
                session=session,
                patient_id=patient_id,
                image_url=relative_path,
                lesion_body_location=lesion_body_location,
                status="PENDING"
            )
        except Exception as exc:
            # Delete stored image file to prevent orphaned disk files if database insert fails
            if os.path.exists(saved_abs_path):
                try:
                    os.remove(saved_abs_path)
                    logger.warning("Cleaned up orphaned file at '%s' after database error", saved_abs_path)
                except OSError as cleanup_err:
                    logger.error("Failed to delete orphaned file at '%s': %s", saved_abs_path, cleanup_err)
            
            logger.error("Database transaction failed during Analysis creation: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to persist analysis record in database."
            )

        return AnalysisUploadResponse(
            analysis_id=analysis_record.id,
            status=analysis_record.status,
            message="Analysis created successfully.",
            image_url=analysis_record.image_url,
            created_at=analysis_record.created_at
        )


# Singleton service export
analysis_service = AnalysisService()

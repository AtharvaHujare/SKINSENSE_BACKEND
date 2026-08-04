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
from app.services.prediction_service import prediction_service
from app.ai.predict import predict
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
    ) -> dict:
        """
        Executes complete upload and analysis workflow:
        1. Validate uploaded image (MIME, size, extension, non-empty).
        2. Resolve associated Patient profile ID.
        3. Save file asynchronously to disk.
        4. Persist Analysis record in database.
        5. Run AI model prediction inference.
        6. Persist Prediction record in database.
        7. Clean up stored file/status on failure.
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

        # 4. Persist Analysis database record with initial status "PENDING"
        try:
            analysis_record = await analysis_repository.create_analysis(
                session=session,
                patient_id=patient_id,
                image_url=relative_path,
                lesion_body_location=lesion_body_location,
                status="PENDING"
            )
            logger.info("Analysis [ID: %s] created with status 'PENDING'", analysis_record.id)
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

        # Transition status to PROCESSING before AI inference
        await analysis_repository.update_analysis_status(
            session=session,
            analysis_id=analysis_record.id,
            status="PROCESSING"
        )
        logger.info("Analysis [ID: %s] status updated to 'PROCESSING'", analysis_record.id)

        # 5. Execute AI Model Prediction Inference
        try:
            prediction = predict(saved_abs_path)
        except Exception as exc:
            logger.error("AI prediction inference failed for Analysis record [ID: %s]: %s", analysis_record.id, exc)
            await analysis_repository.update_analysis_status(
                session=session,
                analysis_id=analysis_record.id,
                status="FAILED"
            )
            logger.error("Analysis [ID: %s] status updated to 'FAILED'", analysis_record.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI prediction inference failed."
            )

        # 6. Save Prediction into Database using PredictionService
        try:
            await prediction_service.create_prediction(
                session=session,
                analysis_id=analysis_record.id,
                predicted_class=prediction["prediction"],
                confidence=prediction["confidence"],
                risk_level=prediction["risk_level"],
                heatmap_path=prediction["heatmap_path"]
            )
        except HTTPException:
            await analysis_repository.update_analysis_status(
                session=session,
                analysis_id=analysis_record.id,
                status="FAILED"
            )
            logger.error("Analysis [ID: %s] status updated to 'FAILED'", analysis_record.id)
            raise
        except Exception as exc:
            await session.rollback()
            logger.error("Failed to save prediction record for Analysis [ID: %s]: %s", analysis_record.id, exc)
            await analysis_repository.update_analysis_status(
                session=session,
                analysis_id=analysis_record.id,
                status="FAILED"
            )
            logger.error("Analysis [ID: %s] status updated to 'FAILED'", analysis_record.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save prediction record in database."
            )

        # 7. Transition status to COMPLETED upon successful workflow completion
        await analysis_repository.update_analysis_status(
            session=session,
            analysis_id=analysis_record.id,
            status="COMPLETED"
        )
        logger.info("Analysis [ID: %s] status updated to 'COMPLETED'", analysis_record.id)

        return {
            "analysis_id": analysis_record.id,
            "prediction": prediction["prediction"],
            "confidence": prediction["confidence"],
            "risk_level": prediction["risk_level"],
            "heatmap_path": prediction["heatmap_path"]
        }

    async def get_analysis(
        self,
        session: AsyncSession,
        current_user: User,
        analysis_id: uuid.UUID
    ) -> dict:
        """
        Retrieves analysis session details including prediction results if available.
        Performs authorization check ensuring patients can only view their own analyses.
        """
        analysis = await analysis_repository.get_analysis_with_prediction(session, analysis_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis session not found."
            )

        # Patient authorization check
        if current_user.role == "PATIENT":
            statement = select(Patient).where(Patient.user_id == current_user.id)
            result = await session.execute(statement)
            patient_profile = result.scalar_one_or_none()
            patient_id = patient_profile.id if patient_profile else current_user.id

            if analysis.patient_id != patient_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. You do not have permission to view this analysis."
                )

        prediction_data = None
        if analysis.predictions:
            latest_pred = analysis.predictions[-1]
            conf_val = float(latest_pred.confidence_score)
            if conf_val <= 1.0:
                conf_val = round(conf_val * 100.0, 2)
            
            risk_val = "Low"
            if latest_pred.class_probabilities and isinstance(latest_pred.class_probabilities, dict):
                risk_val = latest_pred.class_probabilities.get("risk_level", "Low")

            prediction_data = {
                "predicted_class": latest_pred.predicted_class,
                "confidence": conf_val,
                "risk_level": risk_val,
                "heatmap_path": latest_pred.heatmap_url
            }

        return {
            "analysis_id": analysis.id,
            "patient_id": analysis.patient_id,
            "image_url": analysis.image_url,
            "lesion_body_location": analysis.lesion_body_location,
            "status": analysis.status,
            "created_at": analysis.created_at,
            "updated_at": analysis.updated_at,
            "prediction": prediction_data
        }

    async def get_prediction(
        self,
        session: AsyncSession,
        current_user: User,
        analysis_id: uuid.UUID
    ) -> dict:
        """
        Retrieves prediction results for a given analysis session.
        Performs authorization check ensuring patients can only view their own analyses.
        """
        analysis = await analysis_repository.get_analysis_with_prediction(session, analysis_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis session not found."
            )

        # Patient authorization check
        if current_user.role == "PATIENT":
            statement = select(Patient).where(Patient.user_id == current_user.id)
            result = await session.execute(statement)
            patient_profile = result.scalar_one_or_none()
            patient_id = patient_profile.id if patient_profile else current_user.id

            if analysis.patient_id != patient_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. You do not have permission to view this analysis."
                )

        if not analysis.predictions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prediction results not found for this analysis session."
            )

        latest_pred = analysis.predictions[-1]
        conf_val = float(latest_pred.confidence_score)
        if conf_val <= 1.0:
            conf_val = round(conf_val * 100.0, 2)

        risk_val = "Low"
        if latest_pred.class_probabilities and isinstance(latest_pred.class_probabilities, dict):
            risk_val = latest_pred.class_probabilities.get("risk_level", "Low")

        return {
            "predicted_class": latest_pred.predicted_class,
            "confidence": conf_val,
            "risk_level": risk_val,
            "heatmap_path": latest_pred.heatmap_url
        }

    async def get_history(
        self,
        session: AsyncSession,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ) -> list:
        """
        Retrieves historical analysis sessions for the authenticated patient user ordered newest first.
        """
        statement = select(Patient).where(Patient.user_id == current_user.id)
        result = await session.execute(statement)
        patient_profile = result.scalar_one_or_none()
        patient_id = patient_profile.id if patient_profile else current_user.id

        analyses = await analysis_repository.get_patient_history(
            session=session,
            patient_id=patient_id,
            skip=skip,
            limit=limit
        )

        history_items = []
        for analysis in analyses:
            prediction_data = None
            if analysis.predictions:
                latest_pred = analysis.predictions[-1]
                conf_val = float(latest_pred.confidence_score)
                if conf_val <= 1.0:
                    conf_val = round(conf_val * 100.0, 2)

                risk_val = "Low"
                if latest_pred.class_probabilities and isinstance(latest_pred.class_probabilities, dict):
                    risk_val = latest_pred.class_probabilities.get("risk_level", "Low")

                prediction_data = {
                    "predicted_class": latest_pred.predicted_class,
                    "confidence": conf_val,
                    "risk_level": risk_val,
                    "heatmap_path": latest_pred.heatmap_url
                }

            history_items.append({
                "analysis_id": analysis.id,
                "patient_id": analysis.patient_id,
                "image_url": analysis.image_url,
                "lesion_body_location": analysis.lesion_body_location,
                "status": analysis.status,
                "created_at": analysis.created_at,
                "updated_at": analysis.updated_at,
                "prediction": prediction_data
            })

        return history_items


# Singleton service export
analysis_service = AnalysisService()

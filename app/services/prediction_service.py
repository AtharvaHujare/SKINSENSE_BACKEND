"""
SkinSense AI - Prediction Service Layer.

Orchestrates business logic for storing and retrieving AI diagnostic prediction entities.
"""

import uuid
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediction import Prediction
from app.repositories.prediction_repository import prediction_repository

logger = logging.getLogger(__name__)


class PredictionService:
    """
    Business service orchestrating AI Prediction entity creation and queries.
    """

    async def create_prediction(
        self,
        session: AsyncSession,
        analysis_id: uuid.UUID,
        predicted_class: str,
        confidence: float,
        risk_level: str,
        heatmap_path: Optional[str] = None,
        model_version: str = "v1.0.0",
        class_probabilities: Optional[Dict[str, Any]] = None
    ) -> Prediction:
        """
        Persists an AI model prediction into the Prediction database table.
        If prediction save fails, rolls back the transaction, leaving Analysis record intact, and raises HTTP 500.
        """
        try:
            prediction_record = await prediction_repository.create_prediction(
                session=session,
                analysis_id=analysis_id,
                predicted_class=predicted_class,
                confidence_score=confidence,
                risk_level=risk_level,
                heatmap_url=heatmap_path,
                model_version=model_version,
                class_probabilities=class_probabilities
            )
            return prediction_record
        except Exception as exc:
            await session.rollback()
            logger.error("Failed to save prediction record for Analysis [ID: %s]: %s", analysis_id, exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save prediction record in database."
            )

    async def get_prediction(
        self,
        session: AsyncSession,
        prediction_id: uuid.UUID
    ) -> Optional[Prediction]:
        """
        Fetches prediction entity by primary key UUID.
        """
        return await prediction_repository.get_prediction(session, prediction_id)

    async def get_prediction_by_analysis_id(
        self,
        session: AsyncSession,
        analysis_id: uuid.UUID
    ) -> Optional[Prediction]:
        """
        Fetches prediction entity associated with an analysis session.
        """
        return await prediction_repository.get_prediction_by_analysis_id(session, analysis_id)


# Singleton service export
prediction_service = PredictionService()

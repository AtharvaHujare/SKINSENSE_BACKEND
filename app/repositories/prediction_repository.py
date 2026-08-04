"""
SkinSense AI - Prediction Repository Module.

Handles database queries and persistence operations for Prediction entities.
"""

import uuid
import logging
from typing import Optional, Dict, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediction import Prediction

logger = logging.getLogger(__name__)


class PredictionRepository:
    """
    Data Access Object (DAO) for managing Prediction records in PostgreSQL.
    """

    async def create_prediction(
        self,
        session: AsyncSession,
        analysis_id: uuid.UUID,
        predicted_class: str,
        confidence_score: float,
        risk_level: str,
        heatmap_url: Optional[str] = None,
        model_version: str = "v1.0.0",
        class_probabilities: Optional[Dict[str, Any]] = None
    ) -> Prediction:
        """
        Persists a new Prediction record in the database.
        """
        if class_probabilities is None:
            class_probabilities = {"risk_level": risk_level, "confidence": confidence_score}

        # Scale confidence score if provided as percentage (> 1.0) to fit Numeric(5,4)
        normalized_confidence = confidence_score / 100.0 if confidence_score > 1.0 else confidence_score

        prediction = Prediction(
            id=uuid.uuid4(),
            analysis_id=analysis_id,
            model_version=model_version,
            predicted_class=predicted_class,
            confidence_score=normalized_confidence,
            class_probabilities=class_probabilities,
            heatmap_url=heatmap_url,
        )
        session.add(prediction)
        await session.commit()
        await session.refresh(prediction)
        logger.info(
            "Successfully created Prediction record [ID: %s] for Analysis [ID: %s]",
            prediction.id,
            analysis_id
        )
        return prediction

    async def get_prediction(
        self,
        session: AsyncSession,
        prediction_id: uuid.UUID
    ) -> Optional[Prediction]:
        """
        Fetches a Prediction entity by primary key UUID.
        """
        statement = select(Prediction).where(Prediction.id == prediction_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def get_prediction_by_analysis_id(
        self,
        session: AsyncSession,
        analysis_id: uuid.UUID
    ) -> Optional[Prediction]:
        """
        Fetches a Prediction entity associated with a given Analysis ID.
        """
        statement = select(Prediction).where(Prediction.analysis_id == analysis_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def update_prediction(
        self,
        session: AsyncSession,
        prediction_id: uuid.UUID,
        **kwargs: Any
    ) -> Optional[Prediction]:
        """
        Updates fields of an existing Prediction entity.
        """
        statement = (
            update(Prediction)
            .where(Prediction.id == prediction_id)
            .values(**kwargs)
            .returning(Prediction)
        )
        result = await session.execute(statement)
        await session.commit()
        updated_prediction = result.scalar_one_or_none()
        if updated_prediction:
            logger.info("Updated Prediction record [ID: %s]", prediction_id)
        return updated_prediction


# Singleton repository export
prediction_repository = PredictionRepository()

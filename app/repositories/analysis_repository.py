"""
SkinSense AI - Analysis Repository Module.

Handles database queries and persistence operations for Analysis entities.
"""

import uuid
import logging
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis

logger = logging.getLogger(__name__)


class AnalysisRepository:
    """
    Data Access Object (DAO) for managing Analysis records in PostgreSQL.
    """

    async def create_analysis(
        self,
        session: AsyncSession,
        patient_id: uuid.UUID,
        image_url: str,
        lesion_body_location: str,
        assigned_doctor_id: Optional[uuid.UUID] = None,
        status: str = "PENDING"
    ) -> Analysis:
        """
        Persists a new Analysis record in the database.
        """
        analysis = Analysis(
            id=uuid.uuid4(),
            patient_id=patient_id,
            assigned_doctor_id=assigned_doctor_id,
            image_url=image_url,
            lesion_body_location=lesion_body_location,
            status=status,
        )
        session.add(analysis)
        await session.commit()
        await session.refresh(analysis)
        logger.info("Successfully created Analysis record [ID: %s] for Patient [ID: %s]", analysis.id, patient_id)
        return analysis

    async def get_analysis_by_id(
        self,
        session: AsyncSession,
        analysis_id: uuid.UUID
    ) -> Optional[Analysis]:
        """
        Fetches an Analysis entity by primary key UUID.
        """
        statement = select(Analysis).where(Analysis.id == analysis_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def update_analysis_status(
        self,
        session: AsyncSession,
        analysis_id: uuid.UUID,
        status: str
    ) -> Optional[Analysis]:
        """
        Updates the status field of an existing Analysis session.
        """
        statement = (
            update(Analysis)
            .where(Analysis.id == analysis_id)
            .values(status=status)
            .returning(Analysis)
        )
        result = await session.execute(statement)
        await session.commit()
        updated_analysis = result.scalar_one_or_none()
        if updated_analysis:
            logger.info("Updated Analysis record [ID: %s] status to '%s'", analysis_id, status)
        return updated_analysis


# Singleton repository export
analysis_repository = AnalysisRepository()

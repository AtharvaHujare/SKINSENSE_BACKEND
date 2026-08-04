"""
SkinSense AI - Doctor Repository Module.

Handles data access queries for doctor dashboard statistics, pending analysis queues,
and reviewed case histories.
"""

import uuid
import logging
from datetime import datetime, time
from typing import List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis
from app.models.prediction import Prediction
from app.models.report import Report
from app.models.patient import Patient

logger = logging.getLogger(__name__)


class DoctorRepository:
    """
    Data Access Object (DAO) for physician dashboard metrics and task queues.
    """

    async def get_pending_analyses(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Analysis]:
        """
        Fetches analysis records awaiting physician review (status == 'COMPLETED'),
        eagerly loading patient profiles and AI predictions, ordered newest first.
        """
        statement = (
            select(Analysis)
            .options(
                selectinload(Analysis.patient),
                selectinload(Analysis.predictions)
            )
            .where(Analysis.status == "COMPLETED")
            .order_by(Analysis.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())

    async def get_reviewed_analyses(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Analysis]:
        """
        Fetches analysis records that have been reviewed by a doctor (status == 'REVIEWED'),
        eagerly loading patient profiles, predictions, and report notes, ordered newest first.
        """
        statement = (
            select(Analysis)
            .options(
                selectinload(Analysis.patient),
                selectinload(Analysis.predictions),
                selectinload(Analysis.report)
            )
            .where(Analysis.status == "REVIEWED")
            .order_by(Analysis.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())

    async def get_dashboard_statistics(
        self,
        session: AsyncSession
    ) -> Dict[str, int]:
        """
        Calculates metric counters for physician dashboard overview:
        - total_pending: count of COMPLETED analyses awaiting doctor review
        - total_reviewed: count of REVIEWED analyses
        - today_reviews: count of reviews submitted today (UTC)
        - high_risk_cases: count of predictions assessed as High risk
        """
        # Count total pending
        pending_stmt = select(func.count(Analysis.id)).where(Analysis.status == "COMPLETED")
        pending_res = await session.execute(pending_stmt)
        total_pending = pending_res.scalar() or 0

        # Count total reviewed
        reviewed_stmt = select(func.count(Analysis.id)).where(Analysis.status == "REVIEWED")
        reviewed_res = await session.execute(reviewed_stmt)
        total_reviewed = reviewed_res.scalar() or 0

        # Count today reviews
        today_start = datetime.combine(datetime.utcnow().date(), time.min)
        today_stmt = select(func.count(Report.id)).where(Report.updated_at >= today_start)
        today_res = await session.execute(today_stmt)
        today_reviews = today_res.scalar() or 0

        # Count high risk cases
        high_risk_cases = 0
        try:
            high_risk_stmt = select(func.count(Prediction.id)).where(
                Prediction.class_probabilities["risk_level"].astext == "High"
            )
            high_risk_res = await session.execute(high_risk_stmt)
            high_risk_cases = high_risk_res.scalar() or 0
        except Exception as exc:
            logger.warning("Could not execute JSONB risk query directly: %s", exc)
            high_risk_cases = 0

        return {
            "total_pending": total_pending,
            "total_reviewed": total_reviewed,
            "today_reviews": today_reviews,
            "high_risk_cases": high_risk_cases
        }


# Singleton repository export
doctor_repository = DoctorRepository()

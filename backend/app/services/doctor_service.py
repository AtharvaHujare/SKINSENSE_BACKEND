"""
SkinSense AI - Doctor Dashboard Service Layer.

Orchestrates physician metrics aggregation, pending analysis queue parsing, and review history processing.
"""

import uuid
import logging
from typing import List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.dashboard import (
    DoctorDashboardResponse,
    DashboardStatistics,
    PendingAnalysisItem,
    ReviewedAnalysisItem
)
from app.repositories.doctor_repository import doctor_repository

logger = logging.getLogger(__name__)


class DoctorService:
    """
    Business service managing physician dashboard metrics and queues.
    """

    async def get_dashboard(
        self,
        session: AsyncSession,
        current_user: User
    ) -> DoctorDashboardResponse:
        """
        Compiles overview metrics, top 5 pending cases, and top 5 reviewed cases for the doctor.
        """
        stats_dict = await doctor_repository.get_dashboard_statistics(session)
        pending_records = await doctor_repository.get_pending_analyses(session, skip=0, limit=5)
        reviewed_records = await doctor_repository.get_reviewed_analyses(session, skip=0, limit=5)

        recent_pending = self._map_pending_items(pending_records)
        recent_reviewed = self._map_reviewed_items(reviewed_records)

        return DoctorDashboardResponse(
            statistics=DashboardStatistics(**stats_dict),
            recent_pending=recent_pending,
            recent_reviewed=recent_reviewed
        )

    async def get_pending(
        self,
        session: AsyncSession,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ) -> List[PendingAnalysisItem]:
        """
        Retrieves full queue of pending analysis cases awaiting doctor review.
        """
        pending_records = await doctor_repository.get_pending_analyses(session, skip=skip, limit=limit)
        return self._map_pending_items(pending_records)

    async def get_reviewed(
        self,
        session: AsyncSession,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReviewedAnalysisItem]:
        """
        Retrieves full history of cases reviewed by doctors.
        """
        reviewed_records = await doctor_repository.get_reviewed_analyses(session, skip=skip, limit=limit)
        return self._map_reviewed_items(reviewed_records)

    def _map_pending_items(self, records: List[Any]) -> List[PendingAnalysisItem]:
        items = []
        for analysis in records:
            patient_name = "Patient"
            if hasattr(analysis, "patient") and analysis.patient:
                patient_name = f"{analysis.patient.first_name} {analysis.patient.last_name}".strip()

            pred_class = None
            conf_val = None
            risk = None
            heatmap = None

            if hasattr(analysis, "predictions") and analysis.predictions:
                latest = analysis.predictions[-1]
                pred_class = latest.predicted_class
                c_val = float(latest.confidence_score)
                conf_val = round(c_val * 100.0, 2) if c_val <= 1.0 else round(c_val, 2)
                if latest.class_probabilities and isinstance(latest.class_probabilities, dict):
                    risk = latest.class_probabilities.get("risk_level", "Low")
                heatmap = latest.heatmap_url

            items.append(
                PendingAnalysisItem(
                    analysis_id=analysis.id,
                    patient_id=analysis.patient_id,
                    patient_name=patient_name,
                    image_url=analysis.image_url,
                    lesion_body_location=analysis.lesion_body_location,
                    status=analysis.status,
                    created_at=analysis.created_at,
                    prediction=pred_class,
                    confidence=conf_val,
                    risk_level=risk,
                    heatmap_path=heatmap
                )
            )
        return items

    def _map_reviewed_items(self, records: List[Any]) -> List[ReviewedAnalysisItem]:
        items = []
        for analysis in records:
            patient_name = "Patient"
            if hasattr(analysis, "patient") and analysis.patient:
                patient_name = f"{analysis.patient.first_name} {analysis.patient.last_name}".strip()

            pred_class = "N/A"
            conf_val = 0.0
            if hasattr(analysis, "predictions") and analysis.predictions:
                latest = analysis.predictions[-1]
                pred_class = latest.predicted_class
                c_val = float(latest.confidence_score)
                conf_val = round(c_val * 100.0, 2) if c_val <= 1.0 else round(c_val, 2)

            diagnosis_str = "Reviewed"
            reviewed_time = analysis.updated_at
            if hasattr(analysis, "report") and analysis.report and analysis.report.doctor_notes:
                notes_text = analysis.report.doctor_notes
                if "Diagnosis:" in notes_text:
                    diagnosis_str = notes_text.split("Diagnosis:")[1].split("\n")[0].strip()
                else:
                    diagnosis_str = notes_text
                reviewed_time = analysis.report.updated_at

            items.append(
                ReviewedAnalysisItem(
                    analysis_id=analysis.id,
                    patient_name=patient_name,
                    prediction=pred_class,
                    confidence=conf_val,
                    reviewed_at=reviewed_time,
                    diagnosis=diagnosis_str
                )
            )
        return items


# Singleton service export
doctor_service = DoctorService()

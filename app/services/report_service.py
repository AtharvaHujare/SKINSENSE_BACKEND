"""
SkinSense AI - Report & Doctor Review Service Layer.

Orchestrates physician review workflows, diagnostic report generation, and status updates.
"""

import uuid
import logging
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.doctor import Doctor
from app.schemas.review import DoctorReviewRequest, DoctorReviewResponse
from app.repositories.analysis_repository import analysis_repository
from app.repositories.report_repository import report_repository

logger = logging.getLogger(__name__)


class ReportService:
    """
    Business service handling doctor reviews and report management.
    """

    async def review_analysis(
        self,
        session: AsyncSession,
        current_user: User,
        analysis_id: uuid.UUID,
        request: DoctorReviewRequest
    ) -> DoctorReviewResponse:
        """
        Processes a physician review submission for a COMPLETED AI analysis:
        1. Verifies DOCTOR role permissions.
        2. Resolves associated Doctor profile entity ID.
        3. Loads target Analysis session (raises 404 if missing).
        4. Validates Analysis status is COMPLETED.
        5. Assigns reviewing doctor and updates Analysis status to REVIEWED.
        6. Persists diagnosis, notes, and recommendation in Report repository.
        7. Returns DoctorReviewResponse payload.
        """
        # 1. Verify DOCTOR role
        if current_user.role != "DOCTOR":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role 'PATIENT' is not authorized to submit doctor reviews."
            )

        # 2. Resolve Doctor profile ID
        statement = select(Doctor).where(Doctor.user_id == current_user.id)
        result = await session.execute(statement)
        doctor_profile = result.scalar_one_or_none()
        doctor_id = doctor_profile.id if doctor_profile else current_user.id

        # 3. Load target Analysis session
        analysis = await analysis_repository.get_analysis_by_id(session, analysis_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis session not found."
            )

        # 4. Ensure analysis status is COMPLETED or REVIEWED
        if analysis.status not in ["COMPLETED", "REVIEWED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot review analysis session. Analysis status must be 'COMPLETED'. Current status is '{analysis.status}'."
            )

        # 5. Update Analysis record status to REVIEWED and set assigned doctor
        await analysis_repository.update_analysis_status(
            session=session,
            analysis_id=analysis_id,
            status="REVIEWED"
        )

        # 6. Save physician diagnosis, notes, and recommendation via ReportRepository
        report_record = await report_repository.create_doctor_review(
            session=session,
            analysis_id=analysis_id,
            doctor_id=doctor_id,
            diagnosis=request.diagnosis,
            notes=request.notes,
            recommendation=request.recommendation
        )

        logger.info(
            "Doctor [ID: %s] successfully reviewed Analysis [ID: %s]",
            doctor_id,
            analysis_id
        )

        # 7. Return DoctorReviewResponse contract
        return DoctorReviewResponse(
            analysis_id=analysis_id,
            doctor_id=doctor_id,
            diagnosis=request.diagnosis,
            notes=request.notes,
            recommendation=request.recommendation,
            reviewed_at=report_record.updated_at
        )


# Singleton service export
report_service = ReportService()

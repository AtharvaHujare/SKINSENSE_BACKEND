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
from app.models.patient import Patient
from app.schemas.review import DoctorReviewRequest, DoctorReviewResponse
from app.repositories.analysis_repository import analysis_repository
from app.repositories.report_repository import report_repository
from app.services.prediction_service import prediction_service
from app.utils.pdf_generator import generate_analysis_report

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
        4. Validates Analysis status is COMPLETED or REVIEWED.
        5. Assigns reviewing doctor and updates Analysis status to REVIEWED.
        6. Persists diagnosis, notes, and recommendation in Report repository.
        7. Automatically generates PDF report document via pdf_generator utility.
        8. Updates report metadata with generated pdf_path.
        9. Returns DoctorReviewResponse payload including pdf_path.
        """
        # 1. Verify DOCTOR role
        if current_user.role != "DOCTOR":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role 'PATIENT' is not authorized to submit doctor reviews."
            )

        # 2. Resolve Doctor profile entity
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

        # Resolve Patient profile entity for PDF rendering
        patient_stmt = select(Patient).where(Patient.id == analysis.patient_id)
        patient_res = await session.execute(patient_stmt)
        patient_profile = patient_res.scalar_one_or_none()

        # Resolve Prediction record for PDF rendering
        prediction_record = await prediction_service.get_prediction_by_analysis_id(session, analysis_id)

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

        # 7. Automatically generate PDF diagnostic report using ReportLab
        pdf_path = generate_analysis_report(
            analysis=analysis,
            prediction=prediction_record,
            doctor_review=request,
            patient=patient_profile,
            doctor=doctor_profile
        )

        # 8. Save PDF metadata URL in Report table
        await report_repository.save_report_metadata(
            session=session,
            analysis_id=analysis_id,
            pdf_path=pdf_path
        )

        logger.info(
            "Doctor [ID: %s] successfully reviewed Analysis [ID: %s] and generated PDF report at '%s'",
            doctor_id,
            analysis_id,
            pdf_path
        )

        # 9. Return DoctorReviewResponse contract with pdf_path
        return DoctorReviewResponse(
            analysis_id=analysis_id,
            doctor_id=doctor_id,
            diagnosis=request.diagnosis,
            notes=request.notes,
            recommendation=request.recommendation,
            reviewed_at=report_record.updated_at,
            pdf_path=pdf_path
        )

    async def download_report(
        self,
        session: AsyncSession,
        current_user: User,
        analysis_id: uuid.UUID
    ) -> str:
        """
        Validates authorization, loads report metadata, verifies disk existence,
        and returns absolute PDF path for FileResponse download.
        """
        import os

        # 1. Load target Analysis session
        analysis = await analysis_repository.get_analysis_by_id(session, analysis_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis session not found."
            )

        # 2. Enforce Patient authorization check
        if current_user.role == "PATIENT":
            statement = select(Patient).where(Patient.user_id == current_user.id)
            result = await session.execute(statement)
            patient_profile = result.scalar_one_or_none()
            patient_id = patient_profile.id if patient_profile else current_user.id

            if analysis.patient_id != patient_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. You do not have permission to download this report."
                )

        # 3. Load Report record metadata
        report = await report_repository.get_report_by_analysis_id(session, analysis_id)
        if not report or not report.pdf_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report metadata not found for this analysis session."
            )

        # 4. Verify PDF file exists on disk
        pdf_path = os.path.abspath(report.pdf_url)
        if not os.path.exists(pdf_path):
            logger.error("Report PDF file missing from disk at '%s' for Analysis [ID: %s]", pdf_path, analysis_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF report file not found on disk."
            )

        logger.info(
            "User [ID: %s, Role: %s] authorized to download PDF report at '%s' for Analysis [ID: %s]",
            current_user.id,
            current_user.role,
            pdf_path,
            analysis_id
        )
        return pdf_path


# Singleton service export
report_service = ReportService()

"""
SkinSense AI - Report Repository Module.

Handles database queries and persistence operations for Report and Doctor Review entities.
"""

import uuid
import secrets
import logging
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report

logger = logging.getLogger(__name__)


class ReportRepository:
    """
    Data Access Object (DAO) for managing Report entities and Doctor Reviews in PostgreSQL.
    """

    async def get_report_by_analysis_id(
        self,
        session: AsyncSession,
        analysis_id: uuid.UUID
    ) -> Optional[Report]:
        """
        Fetches a Report entity associated with a given Analysis session ID.
        """
        statement = select(Report).where(Report.analysis_id == analysis_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def create_doctor_review(
        self,
        session: AsyncSession,
        analysis_id: uuid.UUID,
        doctor_id: uuid.UUID,
        diagnosis: str,
        notes: str,
        recommendation: str
    ) -> Report:
        """
        Creates a new Report record or updates an existing Report record with physician review notes.
        """
        existing_report = await self.get_report_by_analysis_id(session, analysis_id)

        formatted_notes = f"Diagnosis: {diagnosis}\nNotes: {notes}\nRecommendation: {recommendation}"

        if existing_report:
            existing_report.doctor_notes = formatted_notes
            session.add(existing_report)
            await session.commit()
            await session.refresh(existing_report)
            logger.info("Updated existing Report [ID: %s] with doctor review for Analysis [ID: %s]", existing_report.id, analysis_id)
            return existing_report
        else:
            new_report = Report(
                id=uuid.uuid4(),
                analysis_id=analysis_id,
                pdf_url=f"reports/{analysis_id}.pdf",
                doctor_notes=formatted_notes,
                severity_level="LOW",
                download_token=secrets.token_urlsafe(32)
            )
            session.add(new_report)
            await session.commit()
            await session.refresh(new_report)
            logger.info("Created new Report [ID: %s] with doctor review for Analysis [ID: %s]", new_report.id, analysis_id)
            return new_report

    async def save_report_metadata(
        self,
        session: AsyncSession,
        analysis_id: uuid.UUID,
        pdf_path: str
    ) -> Report:
        """
        Saves or updates the pdf_url for a given Report entity in PostgreSQL.
        """
        report = await self.get_report_by_analysis_id(session, analysis_id)
        if report:
            report.pdf_url = pdf_path
            session.add(report)
            await session.commit()
            await session.refresh(report)
            logger.info("Updated Report [ID: %s] pdf_url to '%s'", report.id, pdf_path)
            return report
        else:
            new_report = Report(
                id=uuid.uuid4(),
                analysis_id=analysis_id,
                pdf_url=pdf_path,
                doctor_notes="",
                severity_level="LOW",
                download_token=secrets.token_urlsafe(32)
            )
            session.add(new_report)
            await session.commit()
            await session.refresh(new_report)
            logger.info("Created new Report [ID: %s] with pdf_url '%s'", new_report.id, pdf_path)
            return new_report


# Singleton repository export
report_repository = ReportRepository()

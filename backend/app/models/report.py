"""
SkinSense AI - Report Model Entity.

Stores PDF diagnostic report metadata, physician review notes, and download security tokens.
"""

import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.analysis import Analysis


class Report(Base, TimestampMixin):
    """
    Report entity linking analysis results to generated PDF reports and doctor notes.
    """
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique report identifier"
    )

    analysis_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("analyses.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
        doc="Associated analysis session"
    )

    pdf_url: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        doc="Storage path for compiled PDF report document"
    )

    doctor_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Physician clinical notes and recommendations"
    )

    severity_level: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="LOW",
        doc="Severity triage level: LOW, MEDIUM, HIGH, CRITICAL"
    )

    download_token: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
        doc="Cryptographic token for secure public report download"
    )

    # Relationships
    analysis: Mapped["Analysis"] = relationship(
        "Analysis",
        back_populates="report",
        doc="Associated Analysis session"
    )

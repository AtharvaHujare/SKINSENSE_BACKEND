"""
SkinSense AI - Analysis Model Entity.

Tracks skin lesion image upload sessions, processing workflow states, and physician assignments.
"""

import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.doctor import Doctor
    from app.models.prediction import Prediction
    from app.models.report import Report
    from app.models.appointment import Appointment


class Analysis(Base, TimestampMixin):
    """
    Analysis session entity managing uploaded image metadata and diagnostic state.
    """
    __tablename__ = "analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique analysis session identifier"
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="Associated patient"
    )

    assigned_doctor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("doctors.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        doc="Assigned reviewing physician (optional)"
    )

    image_url: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        doc="Storage location URL of uploaded lesion image"
    )

    lesion_body_location: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Anatomical location of skin lesion"
    )

    status: Mapped[str] = mapped_column(
        String(32),
        index=True,
        nullable=False,
        default="PENDING",
        doc="Workflow status: PENDING, PROCESSING, COMPLETED, FAILED, REVIEWED"
    )

    # Relationships
    patient: Mapped["Patient"] = relationship(
        "Patient",
        doc="Associated Patient entity"
    )

    assigned_doctor: Mapped[Optional["Doctor"]] = relationship(
        "Doctor",
        doc="Assigned reviewing Doctor entity"
    )

    predictions: Mapped[List["Prediction"]] = relationship(
        "Prediction",
        back_populates="analysis",
        cascade="all, delete-orphan",
        doc="Associated model predictions"
    )

    report: Mapped[Optional["Report"]] = relationship(
        "Report",
        back_populates="analysis",
        uselist=False,
        cascade="all, delete-orphan",
        doc="Generated PDF diagnostic report"
    )

"""
SkinSense AI - Appointment Model Entity.

Manages clinical follow-up consultations between patients and dermatologists.
"""

import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.doctor import Doctor
    from app.models.analysis import Analysis


class Appointment(Base, TimestampMixin):
    """
    Appointment entity managing scheduled consultations.
    """
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique appointment identifier"
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="Associated patient participant"
    )

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("doctors.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="Associated dermatologist participant"
    )

    analysis_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("analyses.id", ondelete="SET NULL"),
        nullable=True,
        doc="Optional triggering lesion analysis session"
    )

    appointment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
        doc="Scheduled date and time of appointment"
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="SCHEDULED",
        doc="Status: SCHEDULED, COMPLETED, CANCELLED, NO_SHOW"
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Consultation notes"
    )

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", doc="Patient participant")
    doctor: Mapped["Doctor"] = relationship("Doctor", doc="Doctor participant")
    analysis: Mapped[Optional["Analysis"]] = relationship("Analysis", doc="Triggering Analysis session")

"""
SkinSense AI - Patient Model Entity.

Stores patient demographic, skin classification, and medical background data.
"""

import uuid
from datetime import date
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Patient(Base, TimestampMixin):
    """
    Patient entity holding clinical background and demographic attributes.
    """
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique patient identifier"
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
        doc="Foreign key referencing associated user account"
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Patient legal first name"
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Patient legal last name"
    )

    date_of_birth: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Patient birth date"
    )

    gender: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Gender identity"
    )

    skin_type: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        doc="Fitzpatrick scale skin classification (e.g., TYPE_I to TYPE_VI)"
    )

    medical_history: Mapped[dict] = mapped_column(
        JSONB,
        server_default="{}",
        nullable=False,
        doc="Structured JSON storage for dermatological and family history"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="patient",
        doc="Associated authentication user account"
    )

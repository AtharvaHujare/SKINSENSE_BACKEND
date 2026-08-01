"""
SkinSense AI - Doctor Model Entity.

Stores practitioner credentialing, medical license, and clinic affiliation details.
"""

import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Doctor(Base, TimestampMixin):
    """
    Doctor entity storing physician licensure and clinical affiliation details.
    """
    __tablename__ = "doctors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique practitioner identifier"
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
        doc="Doctor first name"
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Doctor last name"
    )

    license_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
        doc="State/National medical license registration number"
    )

    specialization: Mapped[str] = mapped_column(
        String(150),
        default="Dermatology",
        nullable=False,
        doc="Medical specialty"
    )

    hospital_affinity: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Primary hospital or clinic affiliation"
    )

    is_approved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True,
        nullable=False,
        doc="Admin approval and credential validation status"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="doctor",
        doc="Associated authentication user account"
    )

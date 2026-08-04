"""
SkinSense AI - User Model Entity.

Represents authentication identity and account credentials for all platform roles.
"""

import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.doctor import Doctor


class User(Base, TimestampMixin):
    """
    User entity storing core credentials and access control roles.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique user identifier"
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        doc="User email address for authentication"
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Hashed password string"
    )

    role: Mapped[str] = mapped_column(
        String(32),
        index=True,
        nullable=False,
        default="PATIENT",
        doc="User role: PATIENT, DOCTOR, or ADMIN"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Account activation status"
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Email verification status"
    )

    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp of last login"
    )

    # Relationships
    patient: Mapped[Optional["Patient"]] = relationship(
        "Patient",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        doc="Associated Patient profile (if role is PATIENT)"
    )

    doctor: Mapped[Optional["Doctor"]] = relationship(
        "Doctor",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        doc="Associated Doctor profile (if role is DOCTOR)"
    )

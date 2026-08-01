"""
SkinSense AI - Consent Model Entity.

Stores immutable patient legal consent records for HIPAA/GDPR compliance.
"""

import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Consent(Base, TimestampMixin):
    """
    Consent entity tracking user agreements to legal policies and AI processing.
    """
    __tablename__ = "consents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique consent record identifier"
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="Granting user account"
    )

    consent_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="Consent policy type: TERMS_OF_SERVICE, PRIVACY_POLICY, AI_PROCESSING_CONSENT, RESEARCH_DATA_SHARING"
    )

    is_granted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        doc="Consent granted state"
    )

    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
        doc="Client IP address during agreement"
    )

    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Timestamp when consent was granted"
    )

    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when consent was revoked (if applicable)"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", doc="Granting user account")

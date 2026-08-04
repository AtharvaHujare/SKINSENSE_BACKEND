"""
SkinSense AI - Notification Model Entity.

Stores in-app and push notification alerts for patients and doctors.
"""

import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, Boolean, ForeignKey
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Notification(Base, TimestampMixin):
    """
    Notification entity storing alert messages for users.
    """
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique notification identifier"
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="Recipient user"
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        doc="Notification header title"
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Complete notification message body"
    )

    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Type: ANALYSIS_COMPLETE, DOCTOR_REVIEW_READY, APPOINTMENT_REMINDER, SYSTEM_ALERT"
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True,
        nullable=False,
        doc="Read confirmation flag"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", doc="Recipient user account")

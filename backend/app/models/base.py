"""
SkinSense AI - Base Model & Timestamp Mixin.

Defines the SQLAlchemy 2.0 Declarative Base and reusable TimestampMixin.
"""

import uuid
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy import Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Abstract Declarative Base class for all ORM models.
    """
    pass


class TimestampMixin:
    """
    Mixin providing standard created_at and updated_at timestamps.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when record was created"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Timestamp when record was last updated"
    )

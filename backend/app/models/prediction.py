"""
SkinSense AI - Prediction Model Entity.

Stores AI model outputs, class predictions, confidence probabilities, and Grad-CAM heatmaps.
"""

import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.analysis import Analysis


class Prediction(Base, TimestampMixin):
    """
    Prediction entity storing classification probabilities and visual explainability maps.
    """
    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique prediction identifier"
    )

    analysis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analyses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="Associated analysis session"
    )

    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="AI model version tag"
    )

    predicted_class: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Top predicted diagnostic class (e.g. Melanoma, Nevus)"
    )

    confidence_score: Mapped[float] = mapped_column(
        Numeric(5, 4),
        nullable=False,
        doc="Primary classification confidence score (0.0000 - 1.0000)"
    )

    class_probabilities: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        doc="Complete probability distribution JSON"
    )

    heatmap_url: Mapped[str] = mapped_column(
        String(512),
        nullable=True,
        doc="Grad-CAM explainability visual heatmap URL"
    )

    # Relationships
    analysis: Mapped["Analysis"] = relationship(
        "Analysis",
        back_populates="predictions",
        doc="Associated Analysis session"
    )

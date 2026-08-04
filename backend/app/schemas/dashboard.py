"""
SkinSense AI - Doctor Dashboard Schemas.

Defines request forms and response contract payloads for physician metrics and queues.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class DashboardStatistics(BaseModel):
    """
    Overview metric counters for physician dashboard.
    """
    total_pending: int = Field(..., description="Count of completed analyses awaiting physician review")
    total_reviewed: int = Field(..., description="Count of analysis sessions reviewed by physicians")
    today_reviews: int = Field(..., description="Count of physician reviews submitted today")
    high_risk_cases: int = Field(..., description="Count of high-risk lesion predictions identified")

    class Config:
        from_attributes = True


class PendingAnalysisItem(BaseModel):
    """
    Item payload for pending analysis queue.
    """
    analysis_id: uuid.UUID = Field(..., description="Unique identifier for the analysis session")
    patient_id: uuid.UUID = Field(..., description="Associated patient profile ID")
    patient_name: str = Field(..., description="Patient full name")
    image_url: str = Field(..., description="Uploaded image file path")
    lesion_body_location: str = Field(..., description="Anatomical location of skin lesion")
    status: str = Field(..., description="Current analysis status")
    created_at: datetime = Field(..., description="Submission timestamp")
    prediction: Optional[str] = Field(None, description="Predicted diagnostic class label")
    confidence: Optional[float] = Field(None, description="Classification confidence percentage")
    risk_level: Optional[str] = Field(None, description="Assessed risk severity level")
    heatmap_path: Optional[str] = Field(None, description="Grad-CAM explainability heatmap path")

    class Config:
        from_attributes = True


class ReviewedAnalysisItem(BaseModel):
    """
    Item payload for reviewed analysis history.
    """
    analysis_id: uuid.UUID = Field(..., description="Unique identifier for the analysis session")
    patient_name: str = Field(..., description="Patient full name")
    prediction: str = Field(..., description="Predicted diagnostic class label")
    confidence: float = Field(..., description="Classification confidence percentage")
    reviewed_at: datetime = Field(..., description="Physician review completion timestamp")
    diagnosis: str = Field(..., description="Physician diagnostic assessment notes")

    class Config:
        from_attributes = True


class DoctorDashboardResponse(BaseModel):
    """
    Combined response payload for physician dashboard overview.
    """
    statistics: DashboardStatistics = Field(..., description="Dashboard metric summary counters")
    recent_pending: List[PendingAnalysisItem] = Field(..., description="List of recent pending analyses awaiting review")
    recent_reviewed: List[ReviewedAnalysisItem] = Field(..., description="List of recent reviewed analyses")

    class Config:
        from_attributes = True

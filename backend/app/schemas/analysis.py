"""
SkinSense AI - Analysis API Pydantic Schemas.

Defines request forms and response payloads for skin lesion analysis upload endpoints.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AnalysisUploadResponse(BaseModel):
    """
    Response schema returned upon successful lesion upload and AI inference prediction.
    """
    analysis_id: uuid.UUID = Field(..., description="Unique identifier for the analysis session")
    prediction: str = Field(..., description="Predicted skin condition label")
    confidence: float = Field(..., description="Confidence score percentage")
    risk_level: str = Field(..., description="Assessed risk level (High or Low)")
    heatmap_path: str = Field(..., description="Path to generated Grad-CAM heatmap visualization")

    class Config:
        from_attributes = True

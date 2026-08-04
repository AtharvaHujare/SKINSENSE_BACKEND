"""
SkinSense AI - Analysis API Pydantic Schemas.

Defines request forms and response payloads for skin lesion analysis upload endpoints.
"""

import uuid
from datetime import datetime
from typing import Optional, List
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


class PredictionResponse(BaseModel):
    """
    Detailed AI diagnostic prediction response schema.
    """
    predicted_class: str = Field(..., description="Top predicted diagnostic skin condition")
    confidence: float = Field(..., description="Classification confidence score percentage (0-100)")
    risk_level: str = Field(..., description="Assessed risk level (High or Low)")
    heatmap_path: Optional[str] = Field(None, description="Grad-CAM explainability visual heatmap URL/path")

    class Config:
        from_attributes = True


class AnalysisDetailResponse(BaseModel):
    """
    Detailed representation of an analysis session including status and optional prediction.
    """
    analysis_id: uuid.UUID = Field(..., description="Unique identifier for the analysis session")
    patient_id: uuid.UUID = Field(..., description="Associated patient profile ID")
    image_url: str = Field(..., description="Storage location path of uploaded lesion image")
    lesion_body_location: str = Field(..., description="Anatomical location of the skin lesion")
    status: str = Field(..., description="Workflow status (PENDING, PROCESSING, COMPLETED, FAILED)")
    created_at: datetime = Field(..., description="Submission timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    prediction: Optional[PredictionResponse] = Field(None, description="Associated prediction results if available")

    class Config:
        from_attributes = True

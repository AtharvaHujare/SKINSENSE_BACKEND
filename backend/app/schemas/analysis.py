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
    Response schema returned upon successful lesion upload and analysis initialization.
    """
    analysis_id: uuid.UUID = Field(..., description="Unique identifier for the analysis session")
    status: str = Field(default="PENDING", description="Analysis processing state (PENDING, PROCESSING, COMPLETED, FAILED)")
    message: str = Field(..., description="Status summary message")
    image_url: Optional[str] = Field(default=None, description="Uploaded image file access path")
    created_at: datetime = Field(..., description="Submission timestamp")

    class Config:
        from_attributes = True

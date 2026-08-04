"""
SkinSense AI - Doctor Review Schemas.

Defines Pydantic request and response schemas for physician analysis reviews.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class DoctorReviewRequest(BaseModel):
    """
    Request payload submitted by a doctor reviewing an AI lesion analysis.
    """
    diagnosis: str = Field(..., description="Physician diagnostic assessment or confirmation")
    notes: str = Field(..., description="Clinical observation notes and details")
    recommendation: str = Field(..., description="Recommended medical treatment or follow-up actions")

    class Config:
        json_schema_extra = {
            "example": {
                "diagnosis": "Benign Melanocytic Nevus",
                "notes": "Lesion displays regular borders and uniform pigmentation. No signs of malignant transformation.",
                "recommendation": "Routine annual skin check recommended. Monitor for any asymmetry or color changes."
            }
        }


class DoctorReviewResponse(BaseModel):
    """
    Response payload returned upon successful doctor review submission.
    """
    analysis_id: uuid.UUID = Field(..., description="Unique identifier for the reviewed analysis session")
    doctor_id: uuid.UUID = Field(..., description="Identifier of the reviewing physician")
    diagnosis: str = Field(..., description="Physician diagnostic assessment")
    notes: str = Field(..., description="Clinical observation notes")
    recommendation: str = Field(..., description="Recommended medical treatment or follow-up actions")
    reviewed_at: datetime = Field(..., description="Timestamp of physician review completion")
    pdf_path: str = Field(..., description="Absolute storage filepath of the generated PDF medical report")

    class Config:
        from_attributes = True

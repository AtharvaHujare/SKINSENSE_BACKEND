"""
SkinSense AI - Authentication Pydantic Schemas.

Defines request and response payloads for registration, login, token refresh, and user responses.
"""

import uuid
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """
    User registration payload schema.
    """
    email: EmailStr = Field(..., example="patient@example.com", description="User email address")
    password: str = Field(..., min_length=8, max_length=128, example="SecureP@ssw0rd!", description="User password")
    role: Literal["PATIENT", "DOCTOR", "ADMIN"] = Field(default="PATIENT", description="User access role")
    first_name: Optional[str] = Field(default=None, max_length=100, example="Jane")
    last_name: Optional[str] = Field(default=None, max_length=100, example="Doe")


class UserLoginRequest(BaseModel):
    """
    User login payload schema.
    """
    email: EmailStr = Field(..., example="patient@example.com")
    password: str = Field(..., example="SecureP@ssw0rd!")


class TokenResponse(BaseModel):
    """
    Authentication JWT token pair response schema.
    """
    access_token: str = Field(..., description="JWT Bearer access token (30 min expiration)")
    refresh_token: str = Field(..., description="JWT Refresh token (7 day expiration)")
    token_type: str = Field(default="bearer", description="Token type string")


class RefreshTokenRequest(BaseModel):
    """
    Refresh token rotation payload schema.
    """
    refresh_token: str = Field(..., description="Raw refresh token string to rotate")


class UserResponse(BaseModel):
    """
    Public user entity response schema.
    """
    id: uuid.UUID
    email: EmailStr
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """
    Standard message notification response payload.
    """
    message: str

"""
SkinSense AI Models Package.

Exports all ORM entities and base classes for the complete domain model.
"""

from app.models.base import Base, TimestampMixin
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.analysis import Analysis
from app.models.prediction import Prediction
from app.models.report import Report
from app.models.appointment import Appointment
from app.models.notification import Notification
from app.models.consent import Consent
from app.models.refresh_token import RefreshToken

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "Patient",
    "Doctor",
    "Analysis",
    "Prediction",
    "Report",
    "Appointment",
    "Notification",
    "Consent",
    "RefreshToken",
]

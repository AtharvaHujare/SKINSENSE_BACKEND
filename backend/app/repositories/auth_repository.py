"""
SkinSense AI - Authentication Repository Module.

Handles database queries and operations for User, Patient, Doctor, and RefreshToken entities.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.refresh_token import RefreshToken


class AuthRepository:
    """
    Data Access Object (DAO) encapsulating user identity and token database transactions.
    """

    async def get_user_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        """
        Fetches a User entity by email address.
        """
        statement = select(User).where(User.email == email.lower().strip())
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, session: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """
        Fetches a User entity by unique UUID primary key.
        """
        statement = select(User).where(User.id == user_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        session: AsyncSession,
        user: User,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """
        Persists a new User record along with linked profile records based on role.
        """
        session.add(user)
        await session.flush()  # Ensures user.id is generated

        # Create linked profile according to role
        if user.role == "PATIENT":
            patient = Patient(
                user_id=user.id,
                first_name=first_name or "Patient",
                last_name=last_name or "User",
                date_of_birth=datetime(2000, 1, 1).date(),
                gender="OTHER",
            )
            session.add(patient)
        elif user.role == "DOCTOR":
            doctor = Doctor(
                user_id=user.id,
                first_name=first_name or "Doctor",
                last_name=last_name or "User",
                license_number=f"LIC-{uuid.uuid4().hex[:8].upper()}",
                specialization="Dermatology",
                is_approved=False,
            )
            session.add(doctor)

        await session.commit()
        await session.refresh(user)
        return user

    async def update_last_login(self, session: AsyncSession, user: User) -> None:
        """
        Updates last_login_at timestamp for the authenticated user.
        """
        user.last_login_at = datetime.now(timezone.utc)
        await session.commit()

    async def store_refresh_token(
        self,
        session: AsyncSession,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> RefreshToken:
        """
        Stores a hashed refresh token in the refresh_tokens table.
        """
        token_obj = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            device_info=device_info,
            ip_address=ip_address,
            is_revoked=False
        )
        session.add(token_obj)
        await session.commit()
        return token_obj

    async def get_refresh_token_by_hash(self, session: AsyncSession, token_hash: str) -> Optional[RefreshToken]:
        """
        Retrieves a stored refresh token entity by its cryptographic SHA-256 hash.
        """
        statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, session: AsyncSession, token_obj: RefreshToken) -> None:
        """
        Marks a refresh token record as revoked and deletes it from storage.
        """
        token_obj.is_revoked = True
        await session.delete(token_obj)
        await session.commit()


# Singleton repository instance export
auth_repository = AuthRepository()

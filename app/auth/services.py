"""
SkinSense AI - Authentication Service Layer.

Orchestrates user registration, authentication verification, JWT token issuance, token rotation, and logouts.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    MessageResponse,
)
from app.repositories.auth_repository import auth_repository
from app.auth.hashing import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token, decode_token, hash_token
from app.config import settings


class AuthService:
    """
    Service class handling authentication business logic.
    """

    async def register_user(
        self,
        session: AsyncSession,
        payload: UserRegisterRequest
    ) -> UserResponse:
        """
        Registers a new user account, validating email uniqueness and hashing passwords.
        """
        # Check if email is already registered
        existing_user = await auth_repository.get_user_by_email(session, payload.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address is already registered"
            )

        # Hash account password
        hashed_pwd = hash_password(payload.password)

        # Instantiate user entity
        user = User(
            email=payload.email.lower().strip(),
            password_hash=hashed_pwd,
            role=payload.role,
            is_active=True,
            is_verified=False
        )

        # Persist user entity and role profile
        created_user = await auth_repository.create_user(
            session=session,
            user=user,
            first_name=payload.first_name,
            last_name=payload.last_name
        )

        return UserResponse.model_validate(created_user)

    async def login_user(
        self,
        session: AsyncSession,
        payload: UserLoginRequest,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> TokenResponse:
        """
        Authenticates user credentials, issues JWT access/refresh token pair, and stores token hash.
        """
        user = await auth_repository.get_user_by_email(session, payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )

        # Generate JWT access and refresh token pair
        token_payload = {"sub": str(user.id), "email": user.email, "role": user.role}
        access_token = create_access_token(data=token_payload)
        raw_refresh_token = create_refresh_token(data=token_payload)

        # Hash refresh token for secure database persistence
        token_hash = hash_token(raw_refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        await auth_repository.store_refresh_token(
            session=session,
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            device_info=user_agent,
            ip_address=ip_address
        )

        # Update last login timestamp
        await auth_repository.update_last_login(session, user)

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            token_type="bearer"
        )

    async def refresh_access_token(
        self,
        session: AsyncSession,
        payload: RefreshTokenRequest,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> TokenResponse:
        """
        Validates refresh token, rotates tokens, revokes old refresh token, and issues new token pair.
        """
        # Decode and validate JWT refresh token structure
        decoded_payload = decode_token(payload.refresh_token)
        if decoded_payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type provided for refresh",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id_str = decoded_payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload subject",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = uuid.UUID(user_id_str)
        token_hash = hash_token(payload.refresh_token)

        # Check database for active stored token hash
        stored_token = await auth_repository.get_refresh_token_by_hash(session, token_hash)
        if not stored_token or stored_token.is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked or is invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check user status
        user = await auth_repository.get_user_by_id(session, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account inactive or not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Revoke old refresh token (Token Rotation)
        await auth_repository.revoke_refresh_token(session, stored_token)

        # Generate new token pair
        token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
        new_access_token = create_access_token(data=token_data)
        new_refresh_token = create_refresh_token(data=token_data)

        # Store new refresh token hash
        new_hash = hash_token(new_refresh_token)
        new_expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        await auth_repository.store_refresh_token(
            session=session,
            user_id=user.id,
            token_hash=new_hash,
            expires_at=new_expires_at,
            device_info=user_agent,
            ip_address=ip_address
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )

    async def logout_user(
        self,
        session: AsyncSession,
        payload: RefreshTokenRequest
    ) -> MessageResponse:
        """
        Revokes a active refresh token to invalidate user session.
        """
        token_hash = hash_token(payload.refresh_token)
        stored_token = await auth_repository.get_refresh_token_by_hash(session, token_hash)
        
        if stored_token:
            await auth_repository.revoke_refresh_token(session, stored_token)

        return MessageResponse(message="Successfully logged out")


# Singleton auth service instance export
auth_service = AuthService()

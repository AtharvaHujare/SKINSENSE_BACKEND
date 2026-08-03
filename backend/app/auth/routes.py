"""
SkinSense AI - Authentication API Endpoints.

Provides registration, login, token refresh, logout, and current user profile routes.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    MessageResponse,
)
from app.auth.services import auth_service
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description="Registers a new Patient, Doctor, or Admin user account with hashed credentials."
)
async def register(
    payload: UserRegisterRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Registers a new platform user account.
    """
    return await auth_service.register_user(session, payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and issue JWT token pair",
    description="Authenticates credentials and returns a Bearer access token (30m) and refresh token (7d)."
)
async def login(
    request: Request,
    payload: UserLoginRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    User login endpoint accepting JSON payload.
    """
    user_agent = request.headers.get("user-agent")
    client_ip = request.client.host if request.client else None
    return await auth_service.login_user(
        session=session,
        payload=payload,
        user_agent=user_agent,
        ip_address=client_ip
    )


@router.post(
    "/login/form",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="OAuth2 Form login endpoint for Swagger UI testing",
    include_in_schema=True
)
async def login_form(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible login endpoint for Swagger UI Authorize button.
    """
    payload = UserLoginRequest(email=form_data.username, password=form_data.password)
    user_agent = request.headers.get("user-agent")
    client_ip = request.client.host if request.client else None
    return await auth_service.login_user(
        session=session,
        payload=payload,
        user_agent=user_agent,
        ip_address=client_ip
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Rotate refresh token and issue new access token",
    description="Validates an existing refresh token, revokes it, and issues a new access/refresh pair."
)
async def refresh_token(
    request: Request,
    payload: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Token refresh endpoint.
    """
    user_agent = request.headers.get("user-agent")
    client_ip = request.client.host if request.client else None
    return await auth_service.refresh_access_token(
        session=session,
        payload=payload,
        user_agent=user_agent,
        ip_address=client_ip
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout user session and revoke refresh token",
    description="Revokes the stored refresh token from the database to terminate session."
)
async def logout(
    payload: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    User logout endpoint.
    """
    return await auth_service.logout_user(session, payload)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve current authenticated user profile",
    description="Protected endpoint returning authenticated user account information."
)
async def get_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Returns authenticated user profile.
    """
    return UserResponse.model_validate(current_user)

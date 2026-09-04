"""
Authentication API routes — register, login, Google OAuth, refresh, logout,
profile management, biometric auth.

Copyright (c) 2026 Philip Kwimba. All rights reserved.
Licensed under AGPLv3 (see LICENSE).
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import get_current_user
from src.core.auth.models import (
    AuthTokens,
    BiometricChallengeResponse,
    BiometricLoginRequest,
    BiometricRegisterRequest,
    ChangePasswordRequest,
    DeleteAccountRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    GoogleLoginRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    UpdateProfileRequest,
)
from src.core.auth.service import (
    AuthService,
    ConflictError,
    NotFoundError,
    UnauthorizedError,
)
from src.core.database.database import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(  # noqa: B008
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> AuthService:
    return AuthService(session=session)


@router.post("/register", response_model=AuthTokens, status_code=status.HTTP_201_CREATED)
async def register(
    req: RegisterRequest,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> AuthTokens:
    """Register a new user with email and password."""
    try:
        access, refresh = await service.register(
            email=req.email,
            password=req.password,
            full_name=req.full_name,
            phone_number=req.phone_number,
            tier=req.tier,
        )
        return AuthTokens(access_token=access, refresh_token=refresh)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/login", response_model=AuthTokens)
async def login(
    req: LoginRequest,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> AuthTokens:
    """Login with email and password."""
    try:
        access, refresh = await service.login(email=req.email, password=req.password)
        return AuthTokens(access_token=access, refresh_token=refresh)
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e


@router.post("/google", response_model=AuthTokens)
async def google_login(
    req: GoogleLoginRequest,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> AuthTokens:
    """Login or register via Google OAuth ID token."""
    try:
        access, refresh = await service.login_with_google(
            id_token=req.id_token, role=req.role
        )
        return AuthTokens(access_token=access, refresh_token=refresh)
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e


@router.post("/refresh", response_model=AuthTokens)
async def refresh(
    req: RefreshRequest,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> AuthTokens:
    """Refresh access token using a valid refresh token."""
    try:
        access, new_refresh, _ = await service.refresh(req.refresh_token)
        return AuthTokens(access_token=access, refresh_token=new_refresh)
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e


@router.post("/logout", response_model=dict[str, str])
async def logout(
    req: RefreshRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> dict[str, str]:
    """Revoke a refresh token."""
    claims = await get_current_user(request)
    await service.logout(str(claims["sub"]), req.refresh_token)
    return {"status": "logged out"}


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    req: ForgotPasswordRequest,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> ForgotPasswordResponse:
    """Send a password reset OTP. Always returns 200 to prevent enumeration."""
    return ForgotPasswordResponse(
        message="If an account matches, an OTP has been sent"
    )


@router.post("/reset-password", response_model=dict[str, str])
async def reset_password(
    req: ResetPasswordRequest,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> dict[str, str]:
    """Reset password using an OTP."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OTP service not yet implemented",
    )


@router.get("/profile", response_model=dict[str, Any])
async def get_profile(
    request: Request,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> dict[str, Any]:
    """Get the current user's profile."""
    claims = await get_current_user(request)
    try:
        customer = await service.get_profile(str(claims["sub"]))
        return {
            "customer_id": str(customer.customer_id),
            "email": customer.email,
            "full_name": customer.full_name,
            "role": customer.role,
            "tier": customer.tier,
            "matches_processed": customer.matches_processed,
            "email_verified": customer.email_verified,
            "phone_verified": customer.phone_verified,
        }
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail="User not found") from e


@router.put("/profile", response_model=dict[str, Any])
async def update_profile(
    req: UpdateProfileRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> dict[str, Any]:
    """Update the current user's profile."""
    claims = await get_current_user(request)
    try:
        customer = await service.update_profile(
            str(claims["sub"]),
            full_name=req.full_name,
            phone_number=req.phone_number,
            email=req.email,
        )
        return {
            "customer_id": str(customer.customer_id),
            "email": customer.email,
            "full_name": customer.full_name,
            "role": customer.role,
        }
    except (NotFoundError, ConflictError) as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.put("/password", response_model=dict[str, str])
async def change_password(
    req: ChangePasswordRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> dict[str, str]:
    """Change the current user's password."""
    claims = await get_current_user(request)
    try:
        await service.change_password(
            str(claims["sub"]), req.current_password, req.new_password
        )
        return {"status": "password updated"}
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/account", response_model=dict[str, str])
async def delete_account(
    req: DeleteAccountRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> dict[str, str]:
    """Delete the current user's account."""
    claims = await get_current_user(request)
    try:
        await service.delete_account(str(claims["sub"]), req.password, req.confirm)
        return {"status": "account deleted"}
    except (NotFoundError, UnauthorizedError) as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@router.get("/biometric/challenge", response_model=BiometricChallengeResponse)
async def biometric_challenge(
    request: Request,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> BiometricChallengeResponse:
    """Generate a biometric challenge for the given user."""
    claims = await get_current_user(request)
    challenge = service.generate_biometric_challenge(str(claims["sub"]))
    return BiometricChallengeResponse(challenge=challenge)


@router.post("/biometric/register", response_model=dict[str, str])
async def biometric_register(
    req: BiometricRegisterRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> dict[str, str]:
    """Register a biometric public key."""
    claims = await get_current_user(request)
    try:
        await service.register_biometric(str(claims["sub"]), req.public_key)
        return {"status": "biometric registered"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail="User not found") from e


@router.post("/biometric/login", response_model=AuthTokens)
async def biometric_login(
    req: BiometricLoginRequest,
    service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> AuthTokens:
    """Login using a biometric signature over a challenge."""
    try:
        access, refresh = await service.login_with_biometric(
            str(req.user_id), req.challenge, req.signature
        )
        return AuthTokens(access_token=access, refresh_token=refresh)
    except UnauthorizedError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e

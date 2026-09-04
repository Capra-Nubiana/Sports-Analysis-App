"""
Pydantic models for authentication requests and responses.

Copyright (c) 2026 Philip Kwimba. All rights reserved.
Licensed under AGPLv3 (see LICENSE).
"""

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None
    phone_number: str | None = None
    tier: str = "free"

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("tier")
    @classmethod
    def validate_tier(cls, v: str) -> str:
        if v not in ("free", "basic", "pro"):
            raise ValueError("Tier must be free, basic, or pro")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    id_token: str
    role: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class BiometricRegisterRequest(BaseModel):
    public_key: str


class BiometricLoginRequest(BaseModel):
    user_id: str
    challenge: str
    signature: str


class UpdateProfileRequest(BaseModel):
    full_name: str | None = None
    phone_number: str | None = None
    email: EmailStr | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class DeleteAccountRequest(BaseModel):
    password: str | None = None
    confirm: bool | None = None


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105


class TokenClaims(BaseModel):
    sub: str
    role: str
    tier: str
    type: str = "access"
    iat: int
    exp: int


class UserProfile(BaseModel):
    customer_id: str
    email: str
    full_name: str | None = None
    role: str
    tier: str
    matches_processed: int = 0
    stripe_customer_id: str | None = None
    mpesa_phone_number: str | None = None
    email_verified: bool = False
    phone_verified: bool = False
    has_password: bool = False
    has_google_auth: bool = False
    has_biometric: bool = False


class ForgotPasswordResponse(BaseModel):
    message: str = "If an account matches, an OTP has been sent"


class BiometricChallengeResponse(BaseModel):
    challenge: str

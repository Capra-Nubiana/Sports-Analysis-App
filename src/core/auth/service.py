"""
Authentication service — register, login, Google auth, refresh, logout,
profile management, biometric auth.

Adapted from kioskpay-backend's AuthService.kt pattern.

Copyright (c) 2026 Philip Kwimba. All rights reserved.
Licensed under AGPLv3 (see LICENSE).
"""

import os
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.biometric import BiometricChallengeStore, BiometricVerifier
from src.core.auth.google import GoogleAuthService
from src.core.auth.jwt import JWTService
from src.core.auth.password import PasswordService
from src.core.database.models import Customer, RefreshToken, Role


class AuthService:
    """High-level authentication and user management service."""

    def __init__(
        self,
        session: AsyncSession,
        jwt_service: JWTService | None = None,
        password_service: PasswordService | None = None,
        google_service: GoogleAuthService | None = None,
        challenge_store: BiometricChallengeStore | None = None,
        admin_emails: str | None = None,
    ) -> None:
        self._session = session
        self._jwt = jwt_service or JWTService()
        self._pwd = password_service or PasswordService()
        self._google = google_service or GoogleAuthService()
        self._challenges = challenge_store or BiometricChallengeStore()
        _admin_str: str = admin_emails or os.getenv("ADMIN_EMAILS") or ""
        self._admin_emails = {
            e.strip().lower()
            for e in _admin_str.split(",")
            if e.strip()
        }

    async def register(
        self,
        email: str,
        password: str,
        full_name: str | None = None,
        phone_number: str | None = None,
        tier: str = "free",
    ) -> tuple[str, str]:
        """Register a new customer. Returns (access_token, refresh_token)."""
        email = email.lower().strip()
        self._pwd.validate(password)

        existing = await self._session.execute(
            select(Customer).where(Customer.email == email)
        )
        if existing.scalar_one_or_none() is not None:
            raise ConflictError(f"An account with email '{email}' already exists")

        password_hash = self._pwd.hash(password)

        customer = Customer(
            email=email,
            full_name=full_name,
            phone_number=phone_number,
            tier=tier,
            role=Role.USER.value,
            password_hash=password_hash,
        )
        self._session.add(customer)
        await self._session.flush()
        await self._session.refresh(customer)

        return await self._issue_tokens(customer)

    async def login(self, email: str, password: str) -> tuple[str, str]:
        """Login with email and password. Returns (access_token, refresh_token)."""
        email = email.lower().strip()
        result = await self._session.execute(
            select(Customer).where(Customer.email == email)
        )
        customer = result.scalar_one_or_none()
        if customer is None or not self._pwd.verify(password, customer.password_hash):
            raise UnauthorizedError("Invalid email or password")

        return await self._issue_tokens(customer)

    async def login_with_google(
        self, id_token: str, role: str | None = None
    ) -> tuple[str, str]:
        """Login or register via Google OAuth. Returns (access_token, refresh_token)."""
        google_info = self._google.verify_token(id_token)
        if google_info is None:
            raise UnauthorizedError("Invalid Google ID token")

        uid = google_info.uid
        email = (google_info.email or "").lower().strip()

        # Case 1: User already linked via Google UID
        result = await self._session.execute(
            select(Customer).where(Customer.google_id == uid)
        )
        customer = result.scalar_one_or_none()

        if customer is not None:
            return await self._issue_tokens(customer)

        # Case 2: Email matches existing account — link Google ID
        if email:
            result = await self._session.execute(
                select(Customer).where(Customer.email == email)
            )
            existing = result.scalar_one_or_none()
            if existing is not None:
                existing.google_id = uid
                await self._session.flush()
                return await self._issue_tokens(existing)

        # Case 3: Create new user
        safe_role = role if role in (Role.USER.value, Role.ADMIN.value) else Role.USER.value
        customer = Customer(
            email=email,
            google_id=uid,
            full_name=google_info.name,
            role=safe_role,
            tier="free",
            password_hash=None,
        )
        self._session.add(customer)
        await self._session.flush()
        await self._session.refresh(customer)

        return await self._issue_tokens(customer)

    async def refresh(self, refresh_token: str) -> tuple[str, str, str]:
        """Refresh access token. Returns (access_token, new_refresh_token, customer_id)."""
        customer_id = self._jwt.verify_refresh_token(refresh_token)
        if customer_id is None:
            raise UnauthorizedError("Invalid or expired refresh token")

        token_hash = self._jwt.hash_token(refresh_token)
        result = await self._session.execute(
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .where(RefreshToken.token_type == "refresh")  # noqa: S105
        )
        stored = result.scalar_one_or_none()
        if stored is None:
            raise UnauthorizedError("Refresh token revoked")
        if stored.replaced_by is not None:
            raise UnauthorizedError("Refresh token revoked")

        cust_result = await self._session.execute(
            select(Customer).where(Customer.customer_id == uuid.UUID(customer_id))
        )
        customer: Customer | None = cust_result.scalar_one_or_none()
        if customer is None:
            raise UnauthorizedError("User not found")

        # Revoke old refresh token
        stored.replaced_by = uuid.uuid4()
        await self._session.flush()

        # Issue new pair
        access, refresh = await self._issue_tokens(customer, rotate_refresh=True)
        return access, refresh, str(customer.customer_id)

    async def logout(self, customer_id: str, refresh_token: str) -> None:
        """Revoke a refresh token."""
        token_hash = self._jwt.hash_token(refresh_token)
        await self._session.execute(
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .where(RefreshToken.customer_id == uuid.UUID(customer_id))
            .values(replaced_by=uuid.uuid4())
        )

    async def get_profile(self, customer_id: str) -> Customer:
        """Get customer profile."""
        result = await self._session.execute(
            select(Customer).where(Customer.customer_id == uuid.UUID(customer_id))
        )
        customer = result.scalar_one_or_none()
        if customer is None:
            raise NotFoundError("User not found")
        return customer

    async def update_profile(
        self,
        customer_id: str,
        full_name: str | None = None,
        phone_number: str | None = None,
        email: str | None = None,
    ) -> Customer:
        """Update customer profile."""
        result = await self._session.execute(
            select(Customer).where(Customer.customer_id == uuid.UUID(customer_id))
        )
        customer = result.scalar_one_or_none()
        if customer is None:
            raise NotFoundError("User not found")

        if email is not None:
            existing = await self._session.execute(
                select(Customer).where(
                    Customer.email == email,
                    Customer.customer_id != customer.customer_id,
                )
            )
            if existing.scalar_one_or_none() is not None:
                raise ConflictError("Email already in use")
            customer.email = email.lower()

        if full_name is not None:
            customer.full_name = full_name
        if phone_number is not None:
            customer.phone_number = phone_number

        await self._session.flush()
        await self._session.commit()
        return customer

    async def change_password(
        self, customer_id: str, current_password: str, new_password: str
    ) -> None:
        """Change password."""
        result = await self._session.execute(
            select(Customer).where(Customer.customer_id == uuid.UUID(customer_id))
        )
        customer = result.scalar_one_or_none()
        if customer is None or not customer.password_hash:
            raise NotFoundError("User not found")
        if not self._pwd.verify(current_password, customer.password_hash):
            raise UnauthorizedError("Current password is incorrect")
        self._pwd.validate(new_password)
        customer.password_hash = self._pwd.hash(new_password)
        await self._session.flush()
        await self._session.commit()

    # ─── Biometric ───────────────────────────────────────────────────────────

    def generate_biometric_challenge(self, user_id: str) -> str:
        """Generate a biometric challenge (sync, no DB needed)."""
        return self._challenges.generate(user_id)

    async def register_biometric(self, customer_id: str, public_key: str) -> None:
        """Register a biometric public key."""
        result = await self._session.execute(
            select(Customer).where(Customer.customer_id == uuid.UUID(customer_id))
        )
        customer = result.scalar_one_or_none()
        if customer is None:
            raise NotFoundError("User not found")
        customer.biometric_public_key = public_key
        await self._session.flush()
        await self._session.commit()

    async def login_with_biometric(
        self, user_id: str, challenge: str, signature: str
    ) -> tuple[str, str]:
        """Authenticate via biometric (ECDSA signature over challenge)."""
        result = await self._session.execute(
            select(Customer).where(Customer.customer_id == uuid.UUID(user_id))
        )
        customer = result.scalar_one_or_none()
        if customer is None:
            raise UnauthorizedError("User not found")
        if customer.biometric_public_key is None:
            raise UnauthorizedError("Biometric not registered for this user")
        if not self._challenges.consume_if_valid(user_id, challenge):
            raise UnauthorizedError("Invalid or expired challenge")
        if not BiometricVerifier.verify(customer.biometric_public_key, challenge, signature):
            raise UnauthorizedError("Biometric signature verification failed")

        return await self._issue_tokens(customer)

    async def delete_account(
        self,
        customer_id: str,
        password: str | None = None,
        confirm: bool | None = None,
    ) -> None:
        """Soft-delete account and revoke all tokens."""
        result = await self._session.execute(
            select(Customer).where(Customer.customer_id == uuid.UUID(customer_id))
        )
        customer = result.scalar_one_or_none()
        if customer is None:
            raise NotFoundError("User not found")

        if customer.password_hash:
            if not password or not self._pwd.verify(password, customer.password_hash):
                raise UnauthorizedError("Incorrect password")
        else:
            if not confirm:
                raise UnauthorizedError("Set confirm=true to delete a Google-linked account")

        customer.role = customer.role  # keep role
        await self._session.execute(
            update(RefreshToken)
            .where(RefreshToken.customer_id == uuid.UUID(customer_id))
            .values(replaced_by=uuid.uuid4())
        )
        await self._session.commit()

    # ─── Internal helpers ──────────────────────────────────────────────────

    async def _issue_tokens(
        self, customer: Customer, rotate_refresh: bool = False
    ) -> tuple[str, str]:
        """Issue JWT token pair and persist refresh token."""
        customer = await self._maybe_promote_to_admin(customer)

        access, refresh = self._jwt.generate_token_pair(
            str(customer.customer_id), customer.role, customer.tier
        )
        token_hash = self._jwt.hash_token(refresh)
        expires = datetime.fromtimestamp(
            self._jwt.refresh_expiry(), tz=timezone.utc
        )

        self._session.add(
            RefreshToken(
                customer_id=customer.customer_id,
                token_hash=token_hash,
                expires_at=expires,
                device_name=None,
                token_type="refresh",  # noqa: S106
            )
        )
        await self._session.flush()
        await self._session.commit()

        return access, refresh

    async def _maybe_promote_to_admin(self, customer: Customer) -> Customer:
        """Promote to admin if email matches ADMIN_EMAILS (on every token issuance)."""
        if customer.role == Role.ADMIN.value or not self._admin_emails:
            return customer
        if customer.email and customer.email.lower() in self._admin_emails:
            customer.role = Role.ADMIN.value
            await self._session.flush()
        return customer


class AuthError(Exception):
    """Base auth exception."""


class UnauthorizedError(AuthError):
    pass


class ConflictError(AuthError):
    pass


class NotFoundError(AuthError):
    pass

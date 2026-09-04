"""
JWT token service — access tokens (15 min) and refresh tokens (7 days).

Adapted from kioskpay-backend JwtService.kt pattern.

Copyright (c) 2026 Philip Kwimba. All rights reserved.
Licensed under AGPLv3 (see LICENSE).
"""

import hashlib
import os
import time
from typing import Any

from jose import jwt


class JWTService:
    """Generate and verify JWT token pairs."""

    def __init__(
        self,
        secret: str | None = None,
        issuer: str | None = None,
        audience: str | None = None,
        access_ttl_minutes: int = 15,
        refresh_ttl_days: int = 7,
    ) -> None:
        self._secret = secret or os.getenv("JWT_SECRET", "dev-secret-change-me")
        self._issuer = issuer or os.getenv("JWT_ISSUER", "sports-analysis-app")
        self._audience = audience or os.getenv("JWT_AUDIENCE", "sports-analysis-app")
        self._access_ttl = access_ttl_minutes * 60
        self._refresh_ttl = refresh_ttl_days * 24 * 60 * 60

    def generate_token_pair(
        self, customer_id: str, role: str, tier: str = "free"
    ) -> tuple[str, str]:
        """Return (access_token, refresh_token)."""
        now = int(time.time())

        access_claims: dict[str, Any] = {
            "sub": customer_id,
            "role": role,
            "tier": tier,
            "type": "access",
            "iss": self._issuer,
            "aud": self._audience,
            "iat": now,
            "exp": now + self._access_ttl,
        }

        refresh_claims: dict[str, Any] = {
            "sub": customer_id,
            "type": "refresh",
            "iss": self._issuer,
            "aud": self._audience,
            "iat": now,
            "exp": now + self._refresh_ttl,
        }

        access_token = jwt.encode(access_claims, self._secret, algorithm="HS256")
        refresh_token = jwt.encode(refresh_claims, self._secret, algorithm="HS256")
        return access_token, refresh_token

    def verify_access_token(self, token: str) -> dict[str, Any] | None:
        try:
            claims: dict[str, Any] = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
                issuer=self._issuer,
                audience=self._audience,
                options={"verify_exp": True},
            )
            if claims.get("type") != "access":
                return None
            return claims
        except Exception:
            return None

    def verify_refresh_token(self, token: str) -> str | None:
        """Returns customer_id if valid, None otherwise."""
        try:
            claims: dict[str, Any] = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
                issuer=self._issuer,
                audience=self._audience,
                options={"verify_exp": True},
            )
            if claims.get("type") != "refresh":
                return None
            sub: str | None = claims.get("sub")
            return sub
        except Exception:
            return None

    def hash_token(self, token: str) -> str:
        """SHA-256 hash of a refresh token for storage (never store raw)."""
        return hashlib.sha256(token.encode()).hexdigest()

    def refresh_expiry(self) -> int:
        """Unix timestamp for when a new refresh token should expire."""
        return int(time.time()) + self._refresh_ttl

    @property
    def access_ttl_seconds(self) -> int:
        return self._access_ttl

    @property
    def refresh_ttl_seconds(self) -> int:
        return self._refresh_ttl

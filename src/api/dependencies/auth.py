"""
JWT authentication dependencies for protected routes.

Copyright (c) 2026 Philip Kwimba. All rights reserved.
Licensed under AGPLv3 (see LICENSE).
"""

from typing import Any

from fastapi import HTTPException, Request, status

from src.core.auth.jwt import JWTService

_jwt_service = JWTService()


async def get_current_user(request: Request) -> dict[str, Any]:
    """
    Extract and verify JWT from Authorization header.
    Falls back to mock auth (X-Customer-ID) for backward compatibility
    with non-auth routes.
    """
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        claims = _jwt_service.verify_access_token(token)
        if claims is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        return claims

    # Fallback: mock auth for MVP routes without JWT
    customer_id = request.headers.get("X-Customer-ID", "test_customer")
    is_admin = customer_id in ("ikambili34@gmail.com", "ikambili34@live.com")
    return {
        "sub": customer_id,
        "role": "admin" if is_admin else "user",
        "tier": "pro" if is_admin else "free",
        "type": "access",
    }


async def get_current_customer(request: Request) -> dict[str, Any]:
    """Alias for backward compatibility with rate_limiter imports."""
    return await get_current_user(request)

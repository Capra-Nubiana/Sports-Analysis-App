"""
Google ID token verification service.

Verifies Google OAuth ID tokens using Google's official public keys.
Follows kioskpay-backend's FirebaseService.verifyGoogleToken pattern.

Copyright (c) 2026 Philip Kwimba. All rights reserved.
Licensed under AGPLv3 (see LICENSE).
"""

import os
from dataclasses import dataclass

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token


@dataclass
class GoogleUserInfo:
    uid: str
    email: str | None
    name: str | None
    picture: str | None


class GoogleAuthService:
    """Verify Google ID tokens."""

    def __init__(self, client_id: str | None = None) -> None:
        self._client_id = client_id or os.getenv("GOOGLE_CLIENT_ID", "")

    def verify_token(self, id_token_str: str) -> GoogleUserInfo | None:
        """Verify a Google ID token and return user info, or None if invalid."""
        if not self._client_id:
            return None
        try:
            info = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                self._client_id,
            )
            return GoogleUserInfo(
                uid=info["sub"],
                email=info.get("email"),
                name=info.get("name"),
                picture=info.get("picture"),
            )
        except Exception:
            return None

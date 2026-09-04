"""
Biometric authentication: challenge-response with ECDSA.

Adapted from kioskpay-backend's BiometricChallengeStore and
AuthService.loginWithBiometric pattern.

Copyright (c) 2026 Philip Kwimba. All rights reserved.
Licensed under AGPLv3 (see LICENSE).
"""

import base64
import hashlib
import os
import time
from dataclasses import dataclass

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import (
    EllipticCurvePublicKey,
)


@dataclass
class StoredChallenge:
    challenge: str
    created_at: float
    ttl_seconds: int = 300


class BiometricChallengeStore:
    """
    In-memory store for biometric challenges.

    In production, use Redis or a database table for distributed support.
    """

    def __init__(self) -> None:
        self._challenges: dict[str, StoredChallenge] = {}

    def generate(self, user_id: str, ttl_seconds: int = 300) -> str:
        """Generate and store a random challenge for the given user."""
        raw = f"{user_id}:{time.time()}:{os.urandom(32).hex()}"
        challenge: str = hashlib.sha256(raw.encode()).hexdigest()
        self._challenges[user_id] = StoredChallenge(
            challenge=challenge, created_at=time.time(), ttl_seconds=ttl_seconds
        )
        return challenge

    def consume_if_valid(self, user_id: str, challenge: str) -> bool:
        """Return True if the challenge is valid and not expired, then consume it."""
        stored = self._challenges.get(user_id)
        if stored is None:
            return False
        if stored.challenge != challenge:
            return False
        if time.time() - stored.created_at > stored.ttl_seconds:
            del self._challenges[user_id]
            return False
        del self._challenges[user_id]
        return True


class BiometricVerifier:
    """Verify ECDSA-SHA256 signatures over a challenge string."""

    @staticmethod
    def verify(public_key_b64: str, challenge: str, signature_b64: str) -> bool:
        """Verify a base64-encoded ECDSA-SHA256 signature."""
        try:
            key_bytes = base64.b64decode(public_key_b64)
            public_key = serialization.load_der_public_key(key_bytes)

            if not isinstance(public_key, EllipticCurvePublicKey):
                return False

            sig_bytes = base64.b64decode(signature_b64)

            public_key.verify(
                sig_bytes,
                challenge.encode(),
                ec.ECDSA(hashes.SHA256()),
            )
            return True
        except Exception:
            return False

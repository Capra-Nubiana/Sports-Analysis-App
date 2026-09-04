"""
Tests for authentication services — JWT, password hashing, biometric auth.

Copyright (c) 2026 Philip Kwimba. All rights reserved.
Licensed under AGPLv3 (see LICENSE).
"""

import base64
import time as _time

import pytest

from src.core.auth.biometric import BiometricChallengeStore, BiometricVerifier
from src.core.auth.jwt import JWTService
from src.core.auth.password import PasswordService

# Shared test JWT service (test secret is fine — not used in production)
_test_jwt = JWTService(
    secret="test-secret-key-123",  # noqa: S106
    issuer="test",
    audience="test",
)


# ── JWT Service ──────────────────────────────────────────────────────────────

class TestJWTService:
    def test_generate_token_pair(self):
        access, refresh = _test_jwt.generate_token_pair("user-123", "user", "free")
        assert access != refresh
        assert len(access.split(".")) == 3
        assert len(refresh.split(".")) == 3

    def test_verify_access_token_valid(self):
        access, _ = _test_jwt.generate_token_pair("user-123", "user", "tier")
        claims = _test_jwt.verify_access_token(access)
        assert claims is not None
        assert claims["sub"] == "user-123"
        assert claims["role"] == "user"
        assert claims["tier"] == "tier"
        assert claims["type"] == "access"

    def test_verify_access_token_invalid(self):
        claims = _test_jwt.verify_access_token("invalid.token.here")
        assert claims is None

    def test_verify_access_token_wrong_type(self):
        _, refresh = _test_jwt.generate_token_pair("user-123", "user", "tier")
        claims = _test_jwt.verify_access_token(refresh)
        assert claims is None

    def test_verify_refresh_token_valid(self):
        _, refresh = _test_jwt.generate_token_pair("user-123", "user", "tier")
        uid = _test_jwt.verify_refresh_token(refresh)
        assert uid == "user-123"

    def test_verify_refresh_token_invalid(self):
        uid = _test_jwt.verify_refresh_token("invalid.token.here")
        assert uid is None

    def test_verify_refresh_token_wrong_type(self):
        access, _ = _test_jwt.generate_token_pair("user-123", "user", "tier")
        uid = _test_jwt.verify_refresh_token(access)
        assert uid is None

    def test_hash_token_deterministic(self):
        svc = JWTService(secret="test", issuer="test", audience="test")  # noqa: S106
        h1 = svc.hash_token("token-abc")
        h2 = svc.hash_token("token-abc")
        h3 = svc.hash_token("token-xyz")
        assert h1 == h2
        assert h1 != h3
        assert len(h1) == 64  # SHA-256 hex


# ── Password Service ─────────────────────────────────────────────────────────

class TestPasswordService:
    def test_hash_and_verify(self):
        pwd = PasswordService()
        hashed = pwd.hash("Password1!")
        assert hashed != "Password1!"
        assert pwd.verify("Password1!", hashed) is True
        assert pwd.verify("wrong", hashed) is False

    def test_verify_none_hash(self):
        pwd = PasswordService()
        assert pwd.verify("anything", None) is False

    def test_validate_strong_password(self):
        pwd = PasswordService()
        assert pwd.validate("Password1!") == "Password1!"

    def test_validate_short_password(self):
        pwd = PasswordService()
        with pytest.raises(ValueError, match="at least 8 characters"):
            pwd.validate("Short1!")

    def test_validate_no_uppercase(self):
        pwd = PasswordService()
        with pytest.raises(ValueError, match="uppercase"):
            pwd.validate("password1!")

    def test_validate_no_digit(self):
        pwd = PasswordService()
        with pytest.raises(ValueError, match="digit"):
            pwd.validate("Password!")


# ── Biometric Challenge Store ────────────────────────────────────────────────

class TestBiometricChallengeStore:
    def test_generate_returns_challenge(self):
        store = BiometricChallengeStore()
        challenge = store.generate("user-1")
        assert isinstance(challenge, str)
        assert len(challenge) > 0

    def test_consume_valid_challenge(self):
        store = BiometricChallengeStore()
        challenge = store.generate("user-1")
        assert store.consume_if_valid("user-1", challenge) is True
        assert store.consume_if_valid("user-1", challenge) is False

    def test_consume_invalid_challenge(self):
        store = BiometricChallengeStore()
        store.generate("user-1")
        assert store.consume_if_valid("user-1", "wrong-challenge") is False

    def test_consume_unknown_user(self):
        store = BiometricChallengeStore()
        assert store.consume_if_valid("unknown-user", "challenge") is False

    def test_challenge_expiry(self):
        store = BiometricChallengeStore()
        challenge = store.generate("user-1", ttl_seconds=0)
        _time.sleep(0.1)
        assert store.consume_if_valid("user-1", challenge) is False


# ── Biometric Verifier ───────────────────────────────────────────────────────

class TestBiometricVerifier:
    def test_verify_valid_signature(self):
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import ec

        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()
        public_der = public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        public_b64 = base64.b64encode(public_der).decode()

        challenge = "test-challenge-123"
        signature = private_key.sign(
            challenge.encode(),
            ec.ECDSA(hashes.SHA256()),
        )
        sig_b64 = base64.b64encode(signature).decode()

        assert BiometricVerifier.verify(public_b64, challenge, sig_b64) is True

    def test_verify_invalid_signature(self):
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import ec

        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()
        public_der = public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        public_b64 = base64.b64encode(public_der).decode()

        challenge = "test-challenge-123"
        wrong_sig = private_key.sign(b"different data", ec.ECDSA(hashes.SHA256()))
        sig_b64 = base64.b64encode(wrong_sig).decode()

        assert BiometricVerifier.verify(public_b64, challenge, sig_b64) is False

    def test_verify_invalid_public_key(self):
        assert BiometricVerifier.verify("not-a-valid-key", "challenge", "sig") is False

"""
Password hashing and validation service.

Uses bcrypt directly (avoids passlib 1.7.4 incompatibility with bcrypt 5.x).
Follows kioskpay-backend password policy:
- Min 8 characters
- At least 1 uppercase letter
- At least 1 digit

Copyright (c) 2026 Philip Kwimba. All rights reserved.
Licensed under AGPLv3 (see LICENSE).
"""

import bcrypt


class PasswordService:
    """Hash and verify passwords using bcrypt."""

    @staticmethod
    def hash(password: str) -> str:
        salt: bytes = bcrypt.gensalt()
        hashed: bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify(plain: str, hashed: str | None) -> bool:
        if not hashed:
            return False
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate(password: str) -> str:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one digit")
        return password

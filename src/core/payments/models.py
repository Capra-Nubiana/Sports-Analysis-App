from enum import Enum
from typing import Any

from pydantic import BaseModel


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"


class Customer(BaseModel):
    customer_id: str
    email: str
    role: Role = Role.USER
    tier: SubscriptionTier = SubscriptionTier.FREE
    matches_processed: int = 0
    stripe_customer_id: str | None = None
    mpesa_phone_number: str | None = None


class TransactionStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class Transaction(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    currency: str
    status: TransactionStatus = TransactionStatus.PENDING
    provider: str  # "stripe" or "mpesa"
    provider_reference: str | None = None
    metadata: dict[str, Any] = {}

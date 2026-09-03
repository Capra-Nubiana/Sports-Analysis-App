from abc import ABC, abstractmethod
from typing import Any

from src.core.payments.models import Customer, Transaction


class PaymentGateway(ABC):
    """Abstract base class for all payment gateways."""

    @abstractmethod
    async def initialize_payment(
        self, customer: Customer, amount: float, currency: str
    ) -> dict[str, Any]:
        """
        Initialize a payment and return the provider initialization response.
        For Stripe, this could be a Checkout session URL.
        For M-Pesa, this could be the STK Push response.
        """
        pass

    @abstractmethod
    async def process_webhook(
        self, payload: dict[str, Any], signature: str | None = None
    ) -> Transaction:
        """
        Process an incoming webhook/callback from the provider.
        Should return the updated Transaction object.
        """
        pass

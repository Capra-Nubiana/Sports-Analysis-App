import uuid
from typing import Any

from src.core.payments.base_gateway import PaymentGateway
from src.core.payments.models import Customer, Transaction, TransactionStatus


class StripeService(PaymentGateway):
    """
    Stripe payment integration.
    This is a mock implementation that simulates Stripe API calls for the MVP.
    """

    async def initialize_payment(
        self, customer: Customer, amount: float, currency: str
    ) -> dict[str, Any]:
        transaction_id = str(uuid.uuid4())
        # In a real app we would call stripe.checkout.Session.create()
        checkout_url = f"https://checkout.stripe.com/pay/{transaction_id}"

        return {
            "provider": "stripe",
            "transaction_id": transaction_id,
            "checkout_url": checkout_url,
            "status": "pending_checkout"
        }

    async def process_webhook(
        self, payload: dict[str, Any], signature: str | None = None
    ) -> Transaction:
        # Mock webhook processing
        event_type = payload.get("type")
        tx_id = payload.get("data", {}).get("object", {}).get("id", "unknown")

        status = TransactionStatus.PENDING
        if event_type == "checkout.session.completed":
            status = TransactionStatus.SUCCESS
        elif event_type == "checkout.session.expired":
            status = TransactionStatus.FAILED

        return Transaction(
            transaction_id=tx_id,
            customer_id=payload.get("data", {}).get(
                "object", {}
            ).get("client_reference_id", "unknown"),
            amount=payload.get("data", {}).get("object", {}).get("amount_total", 0) / 100,
            currency=payload.get("data", {}).get("object", {}).get("currency", "usd"),
            status=status,
            provider="stripe",
            provider_reference=payload.get("id"),
        )

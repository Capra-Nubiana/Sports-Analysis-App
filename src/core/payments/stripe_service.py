"""
Stripe payment integration using the official Stripe Python SDK.

Replaces the mock implementation with real Stripe Checkout session creation
and webhook signature verification.

Copyright (c) 2026 Philip Kwimba. All rights reserved.
Licensed under AGPLv3 (see LICENSE).
"""

import json
import os
import uuid
from typing import Any

import stripe

from src.core.payments.base_gateway import PaymentGateway
from src.core.payments.models import Customer, Transaction, TransactionStatus

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


class StripeService(PaymentGateway):
    """Real Stripe payment integration via Checkout Sessions."""

    async def initialize_payment(
        self, customer: Customer, amount: float, currency: str
    ) -> dict[str, Any]:
        """Create a Stripe Checkout Session for one-time or subscription payment."""
        transaction_id = str(uuid.uuid4())

        line_items: list[dict[str, Any]] = [
            {
                "price_data": {
                    "currency": currency,
                    "unit_amount": int(amount * 100),
                    "product_data": {"name": "Sports Analysis Credits"},
                },
                "quantity": 1,
            }
        ]

        session_kwargs: dict[str, Any] = {
            "payment_method_types": ["card"],
            "line_items": line_items,
            "mode": "payment",
            "client_reference_id": customer.customer_id,
            "metadata": {"transaction_id": transaction_id},
            "success_url": os.getenv(
                "STRIPE_SUCCESS_URL", "https://example.com/success"
            ),
            "cancel_url": os.getenv(
                "STRIPE_CANCEL_URL", "https://example.com/cancel"
            ),
        }

        if customer.stripe_customer_id:
            session_kwargs["customer"] = customer.stripe_customer_id
        elif customer.email:
            session_kwargs["customer_email"] = customer.email

        checkout = stripe.checkout.Session.create(**session_kwargs)

        return {
            "provider": "stripe",
            "transaction_id": transaction_id,
            "checkout_url": checkout.url,
            "checkout_session_id": checkout.id,
            "status": "pending_checkout",
        }

    async def process_webhook(
        self, payload: dict[str, Any], signature: str | None = None
    ) -> Transaction:
        """Verify webhook signature and process the event."""
        if signature and STRIPE_WEBHOOK_SECRET:
            try:
                event = stripe.Webhook.construct_event(
                    json.dumps(payload), signature, STRIPE_WEBHOOK_SECRET
                )
            except (ValueError, stripe.error.SignatureVerificationError):
                raise ValueError("Invalid webhook signature") from None
        else:
            event = payload  # type: ignore[assignment]

        event_data: dict[str, Any] = event  # type: ignore[assignment]
        event_type = event_data.get("type", "")
        session_data = event.get("data", {}).get("object", {})

        status = TransactionStatus.PENDING
        if event_type == "checkout.session.completed":
            status = TransactionStatus.SUCCESS
        elif event_type == "checkout.session.expired":
            status = TransactionStatus.FAILED
        elif event_type == "charge.refunded":
            status = TransactionStatus.FAILED

        amount_total = session_data.get("amount_total", 0)
        currency_val = session_data.get("currency", "usd")

        return Transaction(
            transaction_id=str(uuid.uuid4()),
            customer_id=str(session_data.get("client_reference_id", "unknown")),
            amount=amount_total / 100,
            currency=currency_val,
            status=status,
            provider="stripe",
            provider_reference=event.get("id"),
        )

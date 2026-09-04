"""
Tests for payment services (Stripe + M-Pesa).

Copyright (c) 2026 Philip Kwimba. All rights reserved.
Licensed under AGPLv3 (see LICENSE).
"""

import asyncio

import pytest

from src.core.payments.models import Customer, SubscriptionTier


class TestStripeService:
    def test_service_instantiates(self):
        from src.core.payments.stripe_service import StripeService
        svc = StripeService()
        assert svc is not None

    def test_stripe_no_api_key_raises(self):
        from src.core.payments.stripe_service import StripeService
        svc = StripeService()
        customer = Customer(
            customer_id="test-123",
            email="test@example.com",
            tier=SubscriptionTier.FREE,
        )
        with pytest.raises(Exception, match=".*"):
            asyncio.run(svc.initialize_payment(customer, 100.0, "usd"))


class TestMPesaService:
    def test_service_instantiates(self):
        from src.core.payments.mpesa_service import MPesaService
        svc = MPesaService()
        assert svc is not None

    def test_mpesa_rejects_non_kes(self):
        from src.core.payments.mpesa_service import MPesaService
        svc = MPesaService()
        customer = Customer(
            customer_id="test-123",
            email="test@example.com",
            mpesa_phone_number="254700000000",
            tier=SubscriptionTier.FREE,
        )
        with pytest.raises(ValueError, match="KES"):
            asyncio.run(svc.initialize_payment(customer, 100.0, "USD"))

    def test_mpesa_requires_phone(self):
        from src.core.payments.mpesa_service import MPesaService
        svc = MPesaService()
        customer = Customer(
            customer_id="test-123",
            email="test@example.com",
            mpesa_phone_number=None,
            tier=SubscriptionTier.FREE,
        )
        with pytest.raises(ValueError, match="phone"):
            asyncio.run(svc.initialize_payment(customer, 100.0, "KES"))

    def test_mpesa_webhook_callback_processing(self):
        from src.core.payments.mpesa_service import MPesaService
        svc = MPesaService()
        callback_payload = {
            "Body": {
                "stkCallback": {
                    "ResultCode": 0,
                    "MerchantRequestID": "MRQ-123",
                    "CheckoutRequestID": "CHK-456",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": 500.0},
                        ]
                    },
                }
            }
        }
        tx = asyncio.run(svc.process_webhook(callback_payload))
        assert tx.status.value == "success"
        assert tx.provider == "mpesa"
        assert tx.amount == 500.0
        assert tx.provider_reference == "CHK-456"

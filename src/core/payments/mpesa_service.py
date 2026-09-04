"""
Safaricom M-Pesa STK Push payment integration via the Daraja API.

Replaces the mock implementation with real API calls.

Copyright (c) 2026 Philip Kwimba. All rights reserved.
Licensed under AGPLv3 (see LICENSE).
"""

import base64
import os
import time
import uuid
from typing import Any

import requests

from src.core.payments.base_gateway import PaymentGateway
from src.core.payments.models import Customer, Transaction, TransactionStatus

MPESA_BASE_URL = "https://sandbox.safaricom.co.ke"
STK_PUSH_URL = f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
ACCESS_TOKEN_URL = f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"

CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY", "")
CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "")
SHORTCODE = os.getenv("MPESA_SHORTCODE", "")
PASSKEY = os.getenv("MPESA_PASSKEY", "")
CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "https://example.com/api/v1/payments/mpesa/callback")


class MPesaService(PaymentGateway):
    """M-Pesa STK Push payment integration."""

    def _get_access_token(self) -> str | None:
        """Fetch an OAuth access token from Safaricom."""
        if not CONSUMER_KEY or not CONSUMER_SECRET:
            return None
        try:
            resp = requests.get(
                ACCESS_TOKEN_URL,
                auth=(CONSUMER_KEY, CONSUMER_SECRET),
                timeout=10,
            )
            resp.raise_for_status()
            token: str | None = resp.json().get("access_token")
            return token
        except Exception:
            return None

    def _generate_password(self) -> str:
        """Generate M-Pesa password for STK Push."""
        timestamp = time.strftime("%Y%m%d%H%M%S")
        password = f"{SHORTCODE}{PASSKEY}{timestamp}"
        return base64.b64encode(password.encode()).decode()

    async def initialize_payment(
        self, customer: Customer, amount: float, currency: str
    ) -> dict[str, Any]:
        """Initiate an M-Pesa STK Push payment."""
        if currency != "KES":
            raise ValueError("M-Pesa only supports KES currency")
        if not customer.mpesa_phone_number:
            raise ValueError("Customer must have an M-Pesa phone number")

        access_token = self._get_access_token()
        if not access_token:
            raise RuntimeError("Failed to obtain M-Pesa access token")

        timestamp = time.strftime("%Y%m%d%H%M%S")
        password = self._generate_password()
        transaction_id = str(uuid.uuid4())

        payload = {
            "BusinessShortCode": SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": customer.mpesa_phone_number,
            "PartyB": SHORTCODE,
            "PhoneNumber": customer.mpesa_phone_number,
            "CallBackURL": CALLBACK_URL,
            "AccountReference": f"sports-analysis-{transaction_id[:8]}",
            "TransactionDesc": "Sports Analysis App payment",
        }

        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.post(
            STK_PUSH_URL, json=payload, headers=headers, timeout=30  # type: ignore[arg-type]
        )
        result = resp.json()

        if resp.status_code != 200:
            raise RuntimeError(f"M-Pesa API error: {result.get('errorMessage', 'Unknown')}")

        return {
            "provider": "mpesa",
            "transaction_id": transaction_id,
            "merchant_request_id": result.get("MerchantRequestID"),
            "checkout_request_id": result.get("CheckoutRequestID"),
            "customer_message": result.get("customer_message", "Request accepted"),
            "status": "pending_stk_push",
        }

    async def process_webhook(
        self, payload: dict[str, Any], signature: str | None = None
    ) -> Transaction:
        """Process an M-Pesa STK Push callback."""
        callback = payload.get("Body", {}).get("stkCallback", {})
        result_code = callback.get("ResultCode")
        merchant_request_id = callback.get("MerchantRequestID")
        checkout_request_id = callback.get("CheckoutRequestID")

        status = TransactionStatus.SUCCESS if result_code == 0 else TransactionStatus.FAILED

        # Extract amount from callback metadata
        amount = 0.0
        metadata_items = callback.get("CallbackMetadata", {}).get("Item", [])
        for item in metadata_items:
            if item.get("Name") == "Amount":
                amount = item.get("Value", 0.0)

        return Transaction(
            transaction_id=merchant_request_id or str(uuid.uuid4()),
            customer_id="unknown_from_callback",
            amount=amount,
            currency="KES",
            status=status,
            provider="mpesa",
            provider_reference=checkout_request_id,
            metadata=callback,
        )

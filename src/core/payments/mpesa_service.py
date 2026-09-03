import uuid
from typing import Any

from src.core.payments.base_gateway import PaymentGateway
from src.core.payments.models import Customer, Transaction, TransactionStatus


class MPesaService(PaymentGateway):
    """
    Safaricom M-Pesa STK Push payment integration.
    This is a mock implementation that simulates Daraja API calls for the MVP.
    """

    async def initialize_payment(
        self, customer: Customer, amount: float, currency: str = "KES"
    ) -> dict[str, Any]:
        if currency != "KES":
            raise ValueError("M-Pesa only supports KES currency")

        if not customer.mpesa_phone_number:
            raise ValueError("Customer must have an M-Pesa phone number configured")

        transaction_id = str(uuid.uuid4())
        # In a real app, generate password, timestamp, and call Daraja API STK Push endpoint.

        return {
            "provider": "mpesa",
            "transaction_id": transaction_id,
            "merchant_request_id": f"MRQ_{transaction_id}",
            "checkout_request_id": f"CHK_{transaction_id}",
            "customer_message": "Success. Request accepted for processing"
        }

    async def process_webhook(
        self, payload: dict[str, Any], signature: str | None = None
    ) -> Transaction:
        # Mock M-Pesa callback processing
        stk_callback = payload.get("Body", {}).get("stkCallback", {})
        result_code = stk_callback.get("ResultCode")
        merchant_request_id = stk_callback.get("MerchantRequestID")

        status = TransactionStatus.SUCCESS if result_code == 0 else TransactionStatus.FAILED

        return Transaction(
            transaction_id=merchant_request_id,  # Typically we'd look this up in the DB
            customer_id="unknown_from_callback", # Looked up via MerchantRequestID
            amount=0.0, # We'd extract this from CallbackMetadata if successful
            currency="KES",
            status=status,
            provider="mpesa",
            provider_reference=stk_callback.get("CheckoutRequestID"),
            metadata=stk_callback
        )

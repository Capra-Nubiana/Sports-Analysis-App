"""
Payment API routes — Stripe checkout, M-Pesa STK Push, webhooks.

Copyright (c) 2026 Philip Kwimba. All rights reserved.
Licensed under AGPLv3 (see LICENSE).
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.api.dependencies.auth import get_current_user
from src.core.payments.models import Customer, Transaction
from src.core.payments.mpesa_service import MPesaService
from src.core.payments.stripe_service import StripeService

router = APIRouter(prefix="/payments", tags=["payments"])

_stripe = StripeService()
_mpesa = MPesaService()


@router.post("/stripe/checkout")
async def stripe_checkout(
    request: Request,
    amount: float,
    currency: str = "usd",
) -> dict[str, Any]:
    """Create a Stripe Checkout Session."""
    claims = await get_current_user(request)
    customer = Customer(
        customer_id=claims["sub"],
        email="user@example.com",
        role=claims["role"],
        tier=claims["tier"],
    )
    try:
        result = await _stripe.initialize_payment(customer, amount, currency)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request) -> dict[str, Any]:
    """Handle Stripe webhook events (no auth required)."""
    payload = await request.json()
    signature = request.headers.get("stripe-signature", "")
    try:
        tx = await _stripe.process_webhook(payload, signature)
        return {"status": "processed", "transaction_id": tx.transaction_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/mpesa/stk-push")
async def mpesa_stk_push(
    request: Request,
    amount: float,
    phone_number: str,
) -> dict[str, Any]:
    """Initiate an M-Pesa STK Push payment."""
    claims = await get_current_user(request)
    customer = Customer(
        customer_id=claims["sub"],
        email="user@example.com",
        role=claims["role"],
        tier=claims["tier"],
        mpesa_phone_number=phone_number,
    )
    try:
        result = await _mpesa.initialize_payment(customer, amount, "KES")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.post("/mpesa/callback")
async def mpesa_callback(request: Request) -> dict[str, Any]:
    """Handle M-Pesa STK Push callback (no auth required)."""
    payload = await request.json()
    try:
        tx = await _mpesa.process_webhook(payload)
        return {"status": "processed", "transaction_id": tx.transaction_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

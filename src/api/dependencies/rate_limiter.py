import os

from fastapi import Depends, HTTPException, Request, status

from src.core.payments.models import Customer, Role, SubscriptionTier

_ADMIN_DEFAULTS = "ikambili34@gmail.com,ikambili34@live.com"
ADMIN_IDENTIFIERS = os.getenv("ADMIN_IDENTIFIERS", _ADMIN_DEFAULTS).split(",")

TIER_LIMITS = {
    SubscriptionTier.FREE: 10,
    SubscriptionTier.BASIC: 50,
    SubscriptionTier.PRO: float('inf')
}


async def get_current_customer(request: Request) -> Customer:
    """Mock dependency that retrieves the current customer making the request."""
    customer_id = request.headers.get("X-Customer-ID")
    if not customer_id:
        # Default to a mock test customer for MVP if none provided
        customer_id = "test_customer"

    app_state = request.app.state.store

    # Auto-provision a free customer for testing purposes
    if customer_id not in app_state.customers:
        email = f"{customer_id}@example.com"

        # Check if the customer ID or email matches an admin identifier
        is_admin = customer_id in ADMIN_IDENTIFIERS or email in ADMIN_IDENTIFIERS
        role = Role.ADMIN if is_admin else Role.USER
        tier = SubscriptionTier.PRO if is_admin else SubscriptionTier.FREE

        app_state.customers[customer_id] = Customer(
            customer_id=customer_id,
            email=email,
            tier=tier,
            role=role
        )

    return app_state.customers[customer_id]  # type: ignore[no-any-return]

async def check_rate_limit(
    request: Request, customer: Customer = Depends(get_current_customer)  # noqa: B008
) -> Customer:
    """Dependency that checks if the customer has exceeded their subscription limit."""

    if customer.role == Role.ADMIN:
        return customer

    limit = TIER_LIMITS.get(customer.tier, 10)

    if customer.matches_processed >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Subscription limit reached for tier {customer.tier.value}."
        )

    return customer

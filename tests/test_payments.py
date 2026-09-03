from fastapi.testclient import TestClient

from src.api.main import app
from src.core.payments.models import Customer, SubscriptionTier

client = TestClient(app)

def test_rate_limiter_free_tier():
    # Clear customers
    app.state.store.customers.clear()

    # Initialize a mock free customer
    customer = Customer(
        customer_id="test_free",
        email="test_free@example.com",
        tier=SubscriptionTier.FREE,
        matches_processed=10
    )
    app.state.store.customers["test_free"] = customer

    # Payload for a new match
    match_payload = {
        "sport_type": "football",
        "start_time": "2026-09-03T10:00:00",
        "teams": {0: "Team A", 1: "Team B", 2: "Referee"},
    }

    # Try creating match (should fail with 429 because limit=10)
    response = client.post(
        "/api/v1/matches/",
        json=match_payload,
        headers={"X-Customer-ID": "test_free"},
    )
    assert response.status_code == 429
    assert "Subscription limit reached" in response.json()["detail"]


def test_rate_limiter_free_tier_under_limit():
    app.state.store.customers.clear()

    customer = Customer(
        customer_id="test_free2",
        email="test_free2@example.com",
        tier=SubscriptionTier.FREE,
        matches_processed=5
    )
    app.state.store.customers["test_free2"] = customer

    match_payload = {
        "sport_type": "football",
        "start_time": "2026-09-03T10:00:00",
    }

    response = client.post(
        "/api/v1/matches/",
        json=match_payload,
        headers={"X-Customer-ID": "test_free2"},
    )
    assert response.status_code == 200
    assert app.state.store.customers["test_free2"].matches_processed == 6


def test_rate_limiter_pro_tier():
    app.state.store.customers.clear()

    customer = Customer(
        customer_id="test_pro",
        email="test_pro@example.com",
        tier=SubscriptionTier.PRO,
        matches_processed=100
    )
    app.state.store.customers["test_pro"] = customer

    match_payload = {
        "sport_type": "football",
        "start_time": "2026-09-03T10:00:00",
    }

    response = client.post(
        "/api/v1/matches/",
        json=match_payload,
        headers={"X-Customer-ID": "test_pro"},
    )
    assert response.status_code == 200
    assert app.state.store.customers["test_pro"].matches_processed == 101

def test_admin_bypass():
    app.state.store.customers.clear()

    match_payload = {
        "sport_type": "football",
        "start_time": "2026-09-03T10:00:00",
    }

    # Try creating match with admin email (default in rate_limiter.py)
    response = client.post(
        "/api/v1/matches/",
        json=match_payload,
        headers={"X-Customer-ID": "ikambili34@gmail.com"},
    )
    assert response.status_code == 200
    customer = app.state.store.customers["ikambili34@gmail.com"]
    assert customer.role == "admin"
    assert customer.tier == "pro"

if __name__ == "__main__":
    print("Running tests...")
    test_rate_limiter_free_tier()
    test_rate_limiter_free_tier_under_limit()
    test_rate_limiter_pro_tier()
    test_admin_bypass()
    print("All tests passed!")


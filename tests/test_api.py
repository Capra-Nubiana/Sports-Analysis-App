"""
Tests for API REST endpoints (Phase 3).
"""

from fastapi.testclient import TestClient

from src.api.main import app


def test_api_health():
    client = TestClient(app)
    resp = client.get("/players/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_list_matches_empty():
    client = TestClient(app)
    resp = client.get("/matches/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_nonexistent_match():
    client = TestClient(app)
    resp = client.get("/matches/nonexistent")
    assert resp.status_code == 404


def test_add_event_no_match():
    client = TestClient(app)
    resp = client.post(
        "/events/",
        json={
            "event_type": "goal",
            "timestamp": 10.0,
            "frame_id": 300,
            "confidence": 0.9,
            "players_involved": [1],
            "metadata": {},
        },
    )
    assert resp.status_code == 400


def test_create_match():
    client = TestClient(app)
    resp = client.post(
        "/matches/",
        json={
            "sport_type": "football",
            "start_time": "2026-01-01T00:00:00Z",
            "players": {},
            "events": [],
        },
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "created"


def test_list_highlights():
    client = TestClient(app)
    resp = client.get("/highlights/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_event_endpoints_after_match():
    client = TestClient(app)
    client.post(
        "/matches/",
        json={
            "sport_type": "football",
            "start_time": "2026-01-01T00:00:00Z",
            "players": {},
            "events": [],
        },
    )
    resp = client.post(
        "/events/",
        json={
            "event_type": "goal",
            "timestamp": 45.0,
            "frame_id": 1350,
            "confidence": 0.95,
            "players_involved": [1, 2],
            "metadata": {"scoring_team": 0},
        },
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "added"

    resp = client.get("/events/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

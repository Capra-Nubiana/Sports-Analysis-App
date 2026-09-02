"""
Tests for API REST endpoints (Phase 3).
"""

from fastapi.testclient import TestClient

from src.api.main import app

API = "/api/v1"


def test_api_health():
    client = TestClient(app)
    resp = client.get(f"{API}/players/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_list_matches_empty():
    client = TestClient(app)
    resp = client.get(f"{API}/matches/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_nonexistent_match():
    client = TestClient(app)
    resp = client.get(f"{API}/matches/nonexistent")
    assert resp.status_code == 404


def test_add_event_no_match():
    client = TestClient(app)
    resp = client.post(
        f"{API}/events/",
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
        f"{API}/matches/",
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
    resp = client.get(f"{API}/highlights/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_event_endpoints_after_match():
    client = TestClient(app)
    client.post(
        f"{API}/matches/",
        json={
            "sport_type": "football",
            "start_time": "2026-01-01T00:00:00Z",
            "players": {},
            "events": [],
        },
    )
    resp = client.post(
        f"{API}/events/",
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

    resp = client.get(f"{API}/events/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_video_upload_and_analyze():
    client = TestClient(app)

    # 1. Upload video
    # We simulate a file upload with multipart/form-data
    file_content = b"fake video content"
    files = {"file": ("test_vid.mp4", file_content, "video/mp4")}
    resp = client.post(f"{API}/videos/upload", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["filename"] == "test_vid.mp4"
    assert data["size_bytes"] == len(file_content)
    video_id = data["id"]

    # 2. List videos
    resp = client.get(f"{API}/videos/")
    assert resp.status_code == 200
    listed = resp.json()
    assert len(listed) >= 1
    assert any(v["id"] == video_id for v in listed)

    # 3. Analyze video
    resp = client.post(f"{API}/videos/{video_id}/analyze?sport=rugby")
    assert resp.status_code == 200
    analyze_data = resp.json()
    assert analyze_data["status"] == "queued"
    assert "job_id" in analyze_data

    # 4. Get background job status
    resp = client.get(f"{API}/videos/{video_id}/status")
    assert resp.status_code == 200
    status_data = resp.json()
    assert status_data["video_id"] == video_id

    # Not testing the actual pipeline background execution here since
    # that would block/take time and require a real video.

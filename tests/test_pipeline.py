"""
Person 1 owns this file.

Tests for the AIRAVAT AI Agent.
"""

from fastapi.testclient import TestClient

from services.ai_agent import app

client = TestClient(app)


def _sample_state():
    return {
        "timestamp": "2026-08-22T14:00:00Z",
        "battery_pct": 68.4,
        "wind_ms": 11.2,
        "obstacle_distance_m": 21.5,
        "mission_progress_pct": 46.0,
        "position": {
            "lat": 12.9716,
            "lon": 77.5946,
            "alt": 42.0,
        },
    }


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "airavat-ai-agent"


def test_state_returns_airavat_decision():
    response = client.post("/state", json=_sample_state())

    assert response.status_code == 200

    data = response.json()

    assert data["mode"] == "AIRAVAT"
    assert data["status"] == "LIVE"
    assert len(data["world_model_predictions"]) == 5

    assert data["selected_action"] in [
        "Continue",
        "Reroute",
        "Hold",
        "Return Early",
        "Reprioritize Waypoint",
    ]


def test_event_endpoint():
    response = client.post(
        "/event",
        json={"type": "WIND"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "event_accepted"
    assert data["event"] == "WIND"


def test_mode_endpoint():
    response = client.post(
        "/mode",
        json={"mode": "BASELINE"},
    )

    assert response.status_code == 200
    assert response.json()["mode"] == "BASELINE"

    response = client.post("/state", json=_sample_state())
    assert response.status_code == 200
    assert response.json()["mode"] == "BASELINE"

    response = client.post(
        "/mode",
        json={"mode": "AIRAVAT"},
    )

    assert response.status_code == 200
    assert response.json()["mode"] == "AIRAVAT"

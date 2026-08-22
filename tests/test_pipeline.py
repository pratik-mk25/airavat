"""
tests/test_pipeline.py
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
        "position": {"lat": 12.9716, "lon": 77.5946, "alt": 42.0},
    }


def test_health():
    assert client.get("/health").status_code == 200


def test_airavat_decision():
    res = client.post("/state", json=_sample_state()).json()
    assert res["mode"] == "AIRAVAT"
    assert len(res["world_model_predictions"]) == 5
    assert "metrics" in res  # Verify metrics are present


def test_events_and_modes():
    assert client.post("/event", json={"type": "WIND"}).status_code == 200
    client.post("/mode", json={"mode": "BASELINE"})
    base_res = client.post("/state", json=_sample_state()).json()
    assert base_res["mode"] == "BASELINE"
    assert base_res["selected_action"] == "Continue"

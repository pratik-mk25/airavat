"""
Person 1 owns this file.

AIRAVAT AI Agent

Responsibilities:
- Receive simulation state from SIM Agent
- Apply scenario event modifiers
- Run world model
- Select best action
- Serve live payload to GCS
- Support Baseline / AIRAVAT mode
- Support scenario event injection

Person 2 and Person 3 depend on the endpoints and payload shape.
"""

import sys
import os
from pathlib import Path
from typing import Literal, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from shared.contracts import LivePayload, SimState
from shared.world_model import evaluate_all_actions


app = FastAPI(title="AIRAVAT AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ⚠️ DO NOT EDIT: EVENT AND MODE MODELS
# Person 3 sends these exact payloads.
# ============================================================

class EventIn(BaseModel):
    type: Literal[
        "WIND",
        "OBSTACLE",
        "LOW_BATTERY",
        "RESET",
    ]


class ModeIn(BaseModel):
    mode: Literal[
        "BASELINE",
        "AIRAVAT",
    ]


# ============================================================
# ⚠️ DO NOT EDIT: GLOBAL RUNTIME STATE
# ============================================================

latest_payload: Optional[LivePayload] = None
runtime_mode = "AIRAVAT"

event_modifier = {
    "wind_ms": 0.0,
    "obstacle_distance_m": 0.0,
    "battery_pct": 0.0,
    "ttl": 0,
}


# ============================================================
# 🎨 EDITABLE: LOGGING
# Person 1 can enable logging for replay and technical proof.
# ============================================================

ENABLE_LOGGING = os.getenv("ENABLE_LOGGING", "false").lower() == "true"
LOG_DIR = Path("data")
LOG_FILE = LOG_DIR / "live_payloads.jsonl"


def _log_payload(payload: LivePayload) -> None:
    if not ENABLE_LOGGING:
        return

    try:
        LOG_DIR.mkdir(exist_ok=True)

        with open(LOG_FILE, "a", encoding="utf-8") as file:
            file.write(payload.model_dump_json() + "\n")

    except Exception:
        pass


# ============================================================
# ⚠️ DO NOT EDIT: HEALTH ENDPOINT
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "airavat-ai-agent",
        "mode": runtime_mode,
    }


# ============================================================
# ⚠️ DO NOT EDIT: LIVE ENDPOINT
# Person 2 and Person 3 fetch this endpoint.
# ============================================================

@app.get("/live")
def live():
    if latest_payload is None:
        return {
            "status": "WAITING",
            "message": "No simulation state received yet",
        }

    return latest_payload


# ============================================================
# ⚠️ DO NOT EDIT: STATE ENDPOINT
# SIM Agent posts telemetry here.
# ============================================================

@app.post("/state")
def receive_state(state: SimState):
    global latest_payload
    global event_modifier

    sim_state = state.model_dump()

    # --------------------------------------------------------
    # ⚠️ DO NOT EDIT: EVENT MODIFIER APPLICATION
    # This is what makes GCS buttons affect the live mission.
    # --------------------------------------------------------

    if event_modifier["ttl"] > 0:
        sim_state["wind_ms"] = max(
            0,
            sim_state["wind_ms"] + event_modifier["wind_ms"],
        )

        sim_state["obstacle_distance_m"] = max(
            3,
            sim_state["obstacle_distance_m"] + event_modifier["obstacle_distance_m"],
        )

        sim_state["battery_pct"] = max(
            3,
            sim_state["battery_pct"] + event_modifier["battery_pct"],
        )

        event_modifier["ttl"] -= 1

    safe_state = SimState(**sim_state)

    # --------------------------------------------------------
    # ⚠️ DO NOT EDIT: BASELINE MODE
    # Baseline proves the project works without world model.
    # --------------------------------------------------------

    if runtime_mode == "BASELINE":
        payload = LivePayload(
            timestamp=safe_state.timestamp,
            mode="BASELINE",
            status="LIVE",
            state=safe_state,
            world_model_predictions=[],
            selected_action="Continue",
            reason="Baseline mode: fixed mission plan, no world model adaptation.",
        )

        latest_payload = payload
        _log_payload(payload)
        return payload

    # --------------------------------------------------------
    # ⚠️ DO NOT EDIT: AIRAVAT MODE
    # World model evaluates all actions and selects best.
    # --------------------------------------------------------

    predictions = evaluate_all_actions(safe_state.model_dump())
    best = predictions[0]

    reason = (
        f"{best['action']} selected. "
        f"Predicted battery: {best['predicted_battery_pct']}%, "
        f"risk: {best['risk_level']}, "
        f"ETA: {best['eta_seconds']}s."
    )

    payload = LivePayload(
        timestamp=safe_state.timestamp,
        mode="AIRAVAT",
        status="LIVE",
        state=safe_state,
        world_model_predictions=predictions,
        selected_action=best["action"],
        reason=reason,
    )

    latest_payload = payload
    _log_payload(payload)
    return payload


# ============================================================
# ⚠️ DO NOT EDIT: EVENT ENDPOINT
# Person 3 buttons call this endpoint.
# ============================================================

@app.post("/event")
def trigger_event(event: EventIn):
    global event_modifier

    # --------------------------------------------------------
    # 🎨 EDITABLE: EVENT STRENGTH AND DURATION
    # Person 1 can tune these for a better live demo.
    # Do not change the event type names.
    # --------------------------------------------------------

    if event.type == "WIND":
        event_modifier = {
            "wind_ms": 8.0,
            "obstacle_distance_m": 0.0,
            "battery_pct": 0.0,
            "ttl": 20,
        }

    elif event.type == "OBSTACLE":
        event_modifier = {
            "wind_ms": 0.0,
            "obstacle_distance_m": -25.0,
            "battery_pct": 0.0,
            "ttl": 20,
        }

    elif event.type == "LOW_BATTERY":
        event_modifier = {
            "wind_ms": 0.0,
            "obstacle_distance_m": 0.0,
            "battery_pct": -25.0,
            "ttl": 20,
        }

    elif event.type == "RESET":
        event_modifier = {
            "wind_ms": 0.0,
            "obstacle_distance_m": 0.0,
            "battery_pct": 0.0,
            "ttl": 0,
        }

    return {
        "status": "event_accepted",
        "event": event.type,
        "modifier": event_modifier,
    }


# ============================================================
# ⚠️ DO NOT EDIT: MODE ENDPOINT
# Person 3 toggle button calls this endpoint.
# ============================================================

@app.post("/mode")
def set_mode(mode_input: ModeIn):
    global runtime_mode

    runtime_mode = mode_input.mode

    return {
        "status": "mode_updated",
        "mode": runtime_mode,
    }


# ============================================================
# Optional helper endpoint for debugging.
# Safe to keep.
# ============================================================

@app.get("/mode")
def get_mode():
    return {
        "mode": runtime_mode,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

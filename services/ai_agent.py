import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import Optional, Literal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.contracts import LivePayload, SimState, EventIn, ModeIn
from shared.world_model import evaluate_all_actions

app = FastAPI(title="AIRAVAT AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

latest_payload: Optional[LivePayload] = None

# Global runtime state
runtime_mode = "AIRAVAT"

event_modifier = {
    "wind_ms": 0.0,
    "obstacle_distance_m": 0.0,
    "battery_pct": 0.0,
    "ttl": 0,
}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "airavat-ai-agent",
        "runtime_mode": runtime_mode,
        "event_modifier": event_modifier,
    }


@app.post("/event")
def trigger_event(event: EventIn):
    global event_modifier

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


@app.post("/mode")
def set_mode(mode_input: ModeIn):
    global runtime_mode
    runtime_mode = mode_input.mode

    return {
        "status": "mode_updated",
        "mode": runtime_mode,
    }


@app.post("/state")
def receive_state(state: SimState):
    global latest_payload
    global event_modifier

    sim_state = state.model_dump()

    if event_modifier["ttl"] > 0:
        sim_state["wind_ms"] = max(
            0,
            sim_state["wind_ms"] + event_modifier["wind_ms"]
        )

        sim_state["obstacle_distance_m"] = max(
            3,
            sim_state["obstacle_distance_m"] + event_modifier["obstacle_distance_m"]
        )

        sim_state["battery_pct"] = max(
            3,
            sim_state["battery_pct"] + event_modifier["battery_pct"]
        )

        event_modifier["ttl"] -= 1

    safe_state = SimState(**sim_state)

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
        return payload

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
    return payload


@app.get("/live")
def live():
    if latest_payload is None:
        return {
            "status": "WAITING",
            "message": "No simulation state received yet",
        }

    return latest_payload


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

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
    global latest_payload, event_modifier, runtime_mode

    state_dict = state.model_dump()

    # Apply event modifiers if TTL is active (> 0)
    if event_modifier["ttl"] > 0:
        state_dict["wind_ms"] += event_modifier["wind_ms"]
        state_dict["obstacle_distance_m"] = max(0.0, state_dict["obstacle_distance_m"] + event_modifier["obstacle_distance_m"])
        state_dict["battery_pct"] = max(0.0, state_dict["battery_pct"] + event_modifier["battery_pct"])
        event_modifier["ttl"] -= 1

    updated_state = SimState(**state_dict)

    predictions = evaluate_all_actions(state_dict)
    best = predictions[0]

    if runtime_mode == "BASELINE":
        selected_action = "Continue"
        reason = (
            f"BASELINE (Fixed Plan Active): Blindly continuing mission. "
            f"Risk: {best['risk_level']}. AIRAVAT AI would choose '{best['action']}'."
        )
    else:
        selected_action = best["action"]
        reason = (
            f"AIRAVAT AI Active: {best['action']} selected. "
            f"Predicted battery: {best['predicted_battery_pct']}%, "
            f"risk: {best['risk_level']}, "
            f"ETA: {best['eta_seconds']}s."
        )

    payload = LivePayload(
        timestamp=updated_state.timestamp,
        mode=runtime_mode,
        status="LIVE",
        state=updated_state,
        world_model_predictions=predictions,
        selected_action=selected_action,
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

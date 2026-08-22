import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.contracts import LivePayload, SimState, ModeRequest, EventRequest
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
current_mode: str = "AIRAVAT"
active_event: Optional[EventRequest] = None


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "airavat-ai-agent",
        "mode": current_mode,
        "active_event": active_event.event_type if active_event else None
    }


@app.post("/mode")
def set_mode(req: ModeRequest):
    global current_mode
    current_mode = req.mode
    return {"status": "ok", "mode": current_mode}


@app.post("/event")
def trigger_event(req: EventRequest):
    global active_event
    if req.event_type == "RESET":
        active_event = None
    else:
        active_event = req
    return {
        "status": "ok",
        "event_received": req.event_type,
        "description": req.description
    }


@app.post("/state")
def receive_state(state: SimState):
    global latest_payload, active_event

    state_dict = state.model_dump()

    # Apply interactive event overrides if injected from GCS
    if active_event:
        if active_event.event_type == "INJECT_WIND":
            state_dict["wind_ms"] = active_event.value if active_event.value > 0 else 16.5
        elif active_event.event_type == "INJECT_OBSTACLE":
            state_dict["obstacle_distance_m"] = active_event.value if active_event.value > 0 else 4.5
        elif active_event.event_type == "LOW_BATTERY":
            state_dict["battery_pct"] = active_event.value if active_event.value > 0 else 18.0

    # Re-construct updated SimState
    updated_state = SimState(**state_dict)

    predictions = evaluate_all_actions(state_dict)
    best = predictions[0]

    if current_mode == "BASELINE":
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
        mode=current_mode,
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

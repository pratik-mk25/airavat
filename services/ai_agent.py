import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

latest_payload: Optional[LivePayload] = None


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "airavat-ai-agent",
    }


@app.post("/state")
def receive_state(state: SimState):
    global latest_payload

    predictions = evaluate_all_actions(state.model_dump())
    best = predictions[0]

    reason = (
        f"{best['action']} selected. "
        f"Predicted battery: {best['predicted_battery_pct']}%, "
        f"risk: {best['risk_level']}, "
        f"ETA: {best['eta_seconds']}s."
    )

    payload = LivePayload(
        timestamp=state.timestamp,
        mode="AIRAVAT",
        status="LIVE",
        state=state,
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

"""
services/ai_agent.py
PERSON 1 OWNS THIS FILE.
"""
import base64
import os
import sys
import threading
import time
import requests
from collections import deque
from pathlib import Path
from typing import Literal, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.contracts import LivePayload, SimState
from shared.world_model import evaluate_all_actions

load_dotenv()

app = FastAPI(title="AIRAVAT AI Agent")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- GLOBAL STATE ---
latest_payload: Optional[LivePayload] = None
runtime_mode = "AIRAVAT"
event_modifier = {"wind_ms": 0.0, "obstacle_distance_m": 0.0, "battery_pct": 0.0, "ttl": 0}

# --- METRICS TRACKER ---
start_time = time.time()
metrics_tracker = {
    "danger_events": 0,
    "min_obstacle_distance": 999.0,
    "current_battery": 100.0,
    "mission_time_seconds": 0,
    "total_decisions": 0
}

# --- DECISION HISTORY (last 50) ---
decision_history = deque(maxlen=50)

# --- REACTOR VISUAL CACHE ---
reactor_cache = {"url": None, "prompt": "", "last_action": ""}


# --- PYDANTIC MODELS FOR ENDPOINTS ---
class EventIn(BaseModel):
    type: Literal["WIND", "OBSTACLE", "LOW_BATTERY", "RESET"]


class ModeIn(BaseModel):
    mode: Literal["BASELINE", "AIRAVAT"]


# ==========================================
# 🚀 REACTOR.INC BACKGROUND WORKER & FALLBACK
# ==========================================
def get_reactor_prompt(action: str, state: dict) -> str:
    wind = state.get("wind_ms", 0)
    base_prompts = {
        "Continue": "FPV drone camera view flying straight ahead, clear path, sunny day, cinematic 4k",
        "Reroute": "FPV drone camera view banking sharply to avoid a concrete obstacle, dynamic motion, cinematic",
        "Hold": "FPV drone camera view hovering in place, scanning environment, stabilized gimbal",
        "Return Early": "FPV drone camera view turning 180 degrees to return home, safe descent",
        "Reprioritize Waypoint": "FPV drone camera view adjusting trajectory toward a new target marker, urban landscape"
    }
    prompt = base_prompts.get(action, base_prompts["Continue"])
    if wind > 12:
        prompt += ", heavy wind distortion, turbulent flight, camera shake"
    return prompt


def _generate_fallback_hud_svg(action: str, state: dict, prompt: str) -> str:
    action_colors = {
        "Continue": "#10B981",
        "Reroute": "#F59E0B",
        "Hold": "#3B82F6",
        "Return Early": "#EF4444",
        "Reprioritize Waypoint": "#8B5CF6"
    }
    color = action_colors.get(action, "#10B981")
    battery = state.get("battery_pct", 100)
    wind = state.get("wind_ms", 0)
    obstacle = state.get("obstacle_distance_m", 100)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="512" height="320" viewBox="0 0 512 320" style="background:#0F172A; font-family:sans-serif;">
      <line x1="0" y1="160" x2="512" y2="160" stroke="#334155" stroke-width="2"/>
      <rect x="0" y="160" width="512" height="160" fill="#1E293B" opacity="0.6"/>
      <circle cx="256" cy="160" r="80" stroke="{color}" stroke-width="2" fill="none" opacity="0.4"/>
      <line x1="216" y1="160" x2="296" y2="160" stroke="{color}" stroke-width="3"/>
      <line x1="256" y1="120" x2="256" y2="200" stroke="{color}" stroke-width="3"/>
      {"<rect x='226' y='110' width='60' height='70' fill='#EF4444' opacity='0.3' stroke='#EF4444' stroke-width='2'/><text x='256' y='100' fill='#EF4444' font-size='12' font-weight='bold' text-anchor='middle'>OBSTACLE: " + f"{obstacle:.1f}m</text>" if obstacle < 20 else ""}
      <rect x="15" y="15" width="482" height="40" rx="6" fill="#020617" opacity="0.85" stroke="#334155"/>
      <text x="30" y="40" fill="#F8FAFC" font-size="14" font-weight="bold">REACTOR WORLD MODEL VISION</text>
      <text x="480" y="40" fill="{color}" font-size="14" font-weight="bold" text-anchor="end">{action.upper()}</text>
      <rect x="15" y="265" width="482" height="40" rx="6" fill="#020617" opacity="0.85" stroke="#334155"/>
      <text x="30" y="290" fill="#94A3B8" font-size="12">BATTERY: <tspan fill='#F8FAFC' font-weight='bold'>{battery:.1f}%</tspan></text>
      <text x="180" y="290" fill="#94A3B8" font-size="12">WIND: <tspan fill='#F8FAFC' font-weight='bold'>{wind:.1f}m/s</tspan></text>
      <text x="320" y="290" fill="#94A3B8" font-size="12">OBSTACLE: <tspan fill='#F8FAFC' font-weight='bold'>{obstacle:.1f}m</tspan></text>
      <text x="256" y="245" fill="#E2E8F0" font-size="11" text-anchor="middle" font-style="italic">"{prompt[:65]}..."</text>
    </svg>"""

    b64_svg = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64_svg}"


def reactor_worker():
    """Background thread to fetch Reactor visuals without blocking telemetry."""
    print("Reactor worker thread started.")
    while True:
        time.sleep(2)  # Check every 2 seconds
        if latest_payload and latest_payload.mode == "AIRAVAT":
            current_action = latest_payload.selected_action
            state_dict = latest_payload.state.model_dump()
            
            # Update prompt
            prompt = get_reactor_prompt(current_action, state_dict)
            reactor_cache["prompt"] = prompt

            # Only fetch new visual if action changed or URL is empty
            if current_action != reactor_cache["last_action"] or not reactor_cache["url"]:
                reactor_cache["last_action"] = current_action
                
                # Call Reactor API
                api_key = os.getenv("REACTOR_API_KEY")
                api_url = os.getenv("REACTOR_API_URL", "https://api.reactor.inc/v1/generate")
                model = os.getenv("REACTOR_MODEL", "helios")
                
                fetched_url = None
                if api_key and api_key != "your_reactor_hackathon_key_here":
                    try:
                        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                        payload = {"model": model, "prompt": prompt, "width": 512, "height": 512}
                        res = requests.post(api_url, json=payload, headers=headers, timeout=5)
                        if res.status_code == 200:
                            data = res.json()
                            # Flexible extraction across different Reactor API response structures
                            fetched_url = (
                                data.get("image_url")
                                or data.get("url")
                                or data.get("b64_json")
                                or (data.get("output", {}).get("url") if isinstance(data.get("output"), dict) else None)
                                or (data.get("images", [{}])[0].get("url") if isinstance(data.get("images"), list) and data.get("images") else None)
                                or (data.get("data", [{}])[0].get("url") if isinstance(data.get("data"), list) and data.get("data") else None)
                            )
                    except Exception as e:
                        print(f"Reactor API error: {e}")
                
                # Fallback generator if API key is unconfigured or call fails
                if not fetched_url:
                    fetched_url = _generate_fallback_hud_svg(current_action, state_dict, prompt)

                reactor_cache["url"] = fetched_url


# Start the background thread
threading.Thread(target=reactor_worker, daemon=True).start()


# ==========================================
# ⚠️ ENDPOINTS
# ==========================================
@app.get("/health")
def health():
    return {"status": "ok", "service": "airavat-ai-agent", "mode": runtime_mode}


@app.get("/live")
def live():
    if latest_payload is None:
        return {"status": "WAITING", "message": "No simulation state received yet"}
    
    # Inject Reactor cache into the payload before sending to GCS
    payload_dict = latest_payload.model_dump()
    payload_dict["reactor_visual_url"] = reactor_cache["url"]
    payload_dict["reactor_prompt"] = reactor_cache["prompt"]
    return payload_dict


@app.post("/state")
def receive_state(state: SimState):
    global latest_payload, event_modifier, metrics_tracker

    sim_state = state.model_dump()

    # Apply Event Modifiers (from GCS buttons)
    if event_modifier["ttl"] > 0:
        sim_state["wind_ms"] = max(0.0, sim_state["wind_ms"] + event_modifier["wind_ms"])
        sim_state["obstacle_distance_m"] = max(3.0, sim_state["obstacle_distance_m"] + event_modifier["obstacle_distance_m"])
        sim_state["battery_pct"] = max(3.0, sim_state["battery_pct"] + event_modifier["battery_pct"])
        event_modifier["ttl"] -= 1

    safe_state = SimState(**sim_state)

    # Update Metrics
    metrics_tracker["mission_time_seconds"] = int(time.time() - start_time)
    metrics_tracker["current_battery"] = safe_state.battery_pct
    if safe_state.obstacle_distance_m < metrics_tracker["min_obstacle_distance"]:
        metrics_tracker["min_obstacle_distance"] = safe_state.obstacle_distance_m

    if runtime_mode == "BASELINE":
        payload = LivePayload(
            timestamp=safe_state.timestamp, mode="BASELINE", status="LIVE", state=safe_state,
            world_model_predictions=[], selected_action="Continue",
            reason="Baseline mode: fixed mission plan.", metrics=metrics_tracker
        )
        latest_payload = payload
        return payload

    # AIRAVAT MODE
    predictions = evaluate_all_actions(safe_state.model_dump())
    best = predictions[0]
    
    if best["risk_level"] in ["HIGH", "CRITICAL"] or safe_state.battery_pct < 15:
        metrics_tracker["danger_events"] += 1

    metrics_tracker["total_decisions"] += 1

    # Confidence = score gap between #1 and #2 action (large gap = high confidence)
    confidence = round(best["score"] - predictions[1]["score"], 2) if len(predictions) >= 2 else 99.0

    reason = f"{best['action']} selected (confidence: {confidence}). Predicted battery: {best['predicted_battery_pct']}%, risk: {best['risk_level']}, ETA: {best['eta_seconds']}s."

    payload = LivePayload(
        timestamp=safe_state.timestamp, mode="AIRAVAT", status="LIVE", state=safe_state,
        world_model_predictions=predictions, selected_action=best["action"],
        reason=reason, metrics={**metrics_tracker, "confidence": confidence}
    )
    
    # Store in history
    decision_history.append({
        "timestamp": safe_state.timestamp,
        "action": best["action"],
        "confidence": confidence,
        "battery_pct": safe_state.battery_pct,
        "risk_level": best["risk_level"],
    })

    latest_payload = payload
    return payload


@app.post("/event")
def trigger_event(event: EventIn):
    global event_modifier
    if event.type == "WIND":
        event_modifier = {"wind_ms": 8.0, "obstacle_distance_m": 0.0, "battery_pct": 0.0, "ttl": 20}
    elif event.type == "OBSTACLE":
        event_modifier = {"wind_ms": 0.0, "obstacle_distance_m": -25.0, "battery_pct": 0.0, "ttl": 20}
    elif event.type == "LOW_BATTERY":
        event_modifier = {"wind_ms": 0.0, "obstacle_distance_m": 0.0, "battery_pct": -25.0, "ttl": 20}
    elif event.type == "RESET":
        event_modifier = {"wind_ms": 0.0, "obstacle_distance_m": 0.0, "battery_pct": 0.0, "ttl": 0}
    return {"status": "event_accepted", "event": event.type, "modifier": event_modifier}


@app.post("/mode")
def set_mode(mode_input: ModeIn):
    global runtime_mode
    runtime_mode = mode_input.mode
    return {"status": "mode_updated", "mode": runtime_mode}


@app.get("/mode")
def get_mode():
    return {"mode": runtime_mode}


@app.get("/metrics")
def get_metrics():
    """Cumulative flight performance metrics for dashboards."""
    return {
        **metrics_tracker,
        "uptime_seconds": int(time.time() - start_time),
        "mode": runtime_mode,
        "reactor_status": "connected" if reactor_cache["url"] else "fallback",
    }


@app.get("/history")
def get_history():
    """Last 50 decisions for timeline visualization."""
    return {"decisions": list(decision_history)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

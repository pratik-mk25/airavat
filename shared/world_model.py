"""
shared/world_model.py
PERSON 1 OWNS THIS FILE.
"""
from typing import Dict, List

ACTIONS = ["Continue", "Reroute", "Hold", "Return Early", "Reprioritize Waypoint"]


def predict_action_outcome(state: Dict, action: str) -> Dict:
    battery = state.get("battery_pct", 50)
    wind = state.get("wind_ms", 0)
    obstacle = state.get("obstacle_distance_m", 100)
    progress = state.get("mission_progress_pct", 0)

    eta, risk = 240, 0

    if action == "Continue":
        drain_mult = 1.0 + wind / 20
        risk = 75 if obstacle < 20 else 30
        eta = int(max(60, 240 - progress * 1.8))
    elif action == "Reroute":
        drain_mult = 1.1 + wind / 25
        risk = 25 if obstacle < 20 else 15
        eta = int(max(60, 265 - progress * 1.8))
    elif action == "Hold":
        drain_mult = 0.6 + wind / 30
        risk = 45
        eta = int(max(60, 310 - progress * 1.8))
    elif action == "Return Early":
        drain_mult = 0.9
        risk = 10
        eta = int(max(60, 180 - progress * 0.5))
    else:  # Reprioritize
        drain_mult = 0.95
        risk = 30
        eta = int(max(60, 250 - progress * 1.8))

    predicted_battery = max(0, battery - (1.0 * drain_mult * 5))
    
    if predicted_battery < 20:
        risk += 25
    if wind > 12:
        risk += 15

    if risk > 85:
        risk_level = "CRITICAL"
    elif risk > 65:
        risk_level = "HIGH"
    elif risk > 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    score = predicted_battery - risk * 0.6 - eta * 0.05
    if battery < 25 and action == "Return Early":
        score += 40

    return {
        "action": action,
        "predicted_battery_pct": round(predicted_battery, 1),
        "risk_level": risk_level,
        "eta_seconds": eta,
        "score": round(score, 1),
    }


def evaluate_all_actions(state: Dict) -> List[Dict]:
    predictions = [predict_action_outcome(state, action) for action in ACTIONS]
    predictions.sort(key=lambda x: x["score"], reverse=True)
    return predictions

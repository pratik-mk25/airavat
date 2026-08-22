"""
Person 1 owns this file.

This is the core predictive world model.

It predicts the likely outcome of each possible UAV action:
- Continue
- Reroute
- Hold
- Return Early
- Reprioritize Waypoint

Person 3 displays the output, so the returned dictionary keys
must remain compatible with the contract.
"""

from typing import Dict, List


# ============================================================
# ⚠️ DO NOT EDIT: ACTION LIST ORDER
# These must match the shared Action contract.
# ============================================================

ACTIONS = [
    "Continue",
    "Reroute",
    "Hold",
    "Return Early",
    "Reprioritize Waypoint",
]


# ============================================================
# 🎨 EDITABLE: WORLD MODEL TUNING
# Person 1 can tune these values to make the demo better.
# Keep the behavior explainable.
# ============================================================

BASE_BATTERY_DRAIN = 1.0
LOW_BATTERY_THRESHOLD = 25
HIGH_WIND_THRESHOLD = 12
CLOSE_OBSTACLE_THRESHOLD = 20

RETURN_EARLY_LOW_BATTERY_BONUS = 40


def predict_action_outcome(state: Dict, action: str) -> Dict:
    """
    Predict the outcome of one candidate action.

    Returns:
        {
            "action": str,
            "predicted_battery_pct": float,
            "risk_level": str,
            "eta_seconds": int,
            "score": float,
        }
    """

    battery = state.get("battery_pct", 50)
    wind = state.get("wind_ms", 0)
    obstacle = state.get("obstacle_distance_m", 100)
    progress = state.get("mission_progress_pct", 0)

    eta = 240
    risk = 0

    # --------------------------------------------------------
    # 🎨 EDITABLE: ACTION PHYSICS / HEURISTICS
    # Person 1 can improve these rules.
    # --------------------------------------------------------

    if action == "Continue":
        drain_multiplier = 1.0 + wind / 20
        risk = 75 if obstacle < CLOSE_OBSTACLE_THRESHOLD else 30
        eta = int(max(60, 240 - progress * 1.8))

    elif action == "Reroute":
        drain_multiplier = 1.1 + wind / 25
        risk = 25 if obstacle < CLOSE_OBSTACLE_THRESHOLD else 15
        eta = int(max(60, 265 - progress * 1.8))

    elif action == "Hold":
        drain_multiplier = 0.6 + wind / 30
        risk = 45
        eta = int(max(60, 310 - progress * 1.8))

    elif action == "Return Early":
        drain_multiplier = 0.9
        risk = 10
        eta = int(max(60, 180 - progress * 0.5))

    else:  # Reprioritize Waypoint
        drain_multiplier = 0.95
        risk = 30
        eta = int(max(60, 250 - progress * 1.8))

    predicted_battery = battery - BASE_BATTERY_DRAIN * drain_multiplier * 5
    predicted_battery = max(predicted_battery, 0)

    # --------------------------------------------------------
    # 🎨 EDITABLE: RISK PENALTIES
    # --------------------------------------------------------

    if predicted_battery < 20:
        risk += 25

    if wind > HIGH_WIND_THRESHOLD:
        risk += 15

    if risk > 85:
        risk_level = "CRITICAL"
    elif risk > 65:
        risk_level = "HIGH"
    elif risk > 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # --------------------------------------------------------
    # 🎨 EDITABLE: ACTION SCORING
    # Higher score wins.
    # --------------------------------------------------------

    score = predicted_battery - risk * 0.6 - eta * 0.05

    if battery < LOW_BATTERY_THRESHOLD and action == "Return Early":
        score += RETURN_EARLY_LOW_BATTERY_BONUS

    return {
        "action": action,
        "predicted_battery_pct": round(predicted_battery, 1),
        "risk_level": risk_level,
        "eta_seconds": eta,
        "score": round(score, 1),
    }


def evaluate_all_actions(state: Dict) -> List[Dict]:
    """
    Evaluate all possible actions and return them sorted by score.
    """

    predictions = [predict_action_outcome(state, action) for action in ACTIONS]
    predictions.sort(key=lambda item: item["score"], reverse=True)
    return predictions

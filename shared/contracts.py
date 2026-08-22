"""
Person 1 owns this file.

This file defines the shared contract between:
- SIM Agent
- AIRAVAT AI Agent
- GCS Agent

Person 2 and Person 3 depend on these field names.
Do not remove or rename fields without informing the whole team.
"""

from typing import Dict, List, Literal

from pydantic import BaseModel, Field


# ============================================================
# ⚠️ DO NOT EDIT: ACTION CONTRACT
# Person 3 displays these actions.
# ============================================================

Action = Literal[
    "Continue",
    "Reroute",
    "Hold",
    "Return Early",
    "Reprioritize Waypoint",
]


# ============================================================
# ⚠️ DO NOT EDIT: RISK CONTRACT
# Person 3 may display risk values.
# ============================================================

RiskLevel = Literal[
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
]


# ============================================================
# ⚠️ DO NOT EDIT: POSITION CONTRACT
# Person 2 uses position.lat, position.lon, position.alt.
# ============================================================

class Position(BaseModel):
    lat: float
    lon: float
    alt: float


# ============================================================
# ⚠️ DO NOT EDIT: SIM STATE CONTRACT
# Person 3 uses battery_pct, wind_ms, obstacle_distance_m,
# and mission_progress_pct.
# ============================================================

class SimState(BaseModel):
    timestamp: str
    battery_pct: float
    wind_ms: float
    obstacle_distance_m: float
    mission_progress_pct: float
    position: Position


# ============================================================
# ⚠️ DO NOT EDIT: WORLD MODEL PREDICTION CONTRACT
# Person 3 displays these columns.
# ============================================================

class WorldModelPrediction(BaseModel):
    action: Action
    predicted_battery_pct: float
    risk_level: RiskLevel
    eta_seconds: int
    score: float


# ============================================================
# ⚠️ DO NOT EDIT: LIVE PAYLOAD CONTRACT
# This is the main payload returned by GET /live.
# ============================================================

class LivePayload(BaseModel):
    timestamp: str
    mode: str = "AIRAVAT"
    status: str = "LIVE"
    state: SimState
    world_model_predictions: List[WorldModelPrediction]
    selected_action: Action
    reason: str

    # Optional future fields.
    # These are safe additions because they default to empty.
    metrics: Dict[str, float] = Field(default_factory=dict)

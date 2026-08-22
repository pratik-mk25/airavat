from typing import List, Literal
from pydantic import BaseModel

Action = Literal[
    "Continue",
    "Reroute",
    "Hold",
    "Return Early",
    "Reprioritize Waypoint",
]

RiskLevel = Literal[
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
]


class Position(BaseModel):
    lat: float
    lon: float
    alt: float


class SimState(BaseModel):
    timestamp: str
    battery_pct: float
    wind_ms: float
    obstacle_distance_m: float
    mission_progress_pct: float
    position: Position


class WorldModelPrediction(BaseModel):
    action: Action
    predicted_battery_pct: float
    risk_level: RiskLevel
    eta_seconds: int
    score: float


class LivePayload(BaseModel):
    timestamp: str
    mode: str = "AIRAVAT"
    status: str = "LIVE"
    state: SimState
    world_model_predictions: List[WorldModelPrediction]
    selected_action: Action
    reason: str

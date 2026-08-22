"""
shared/contracts.py
PERSON 1 OWNS THIS FILE. DO NOT RENAME FIELDS.
"""
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field

Action = Literal["Continue", "Reroute", "Hold", "Return Early", "Reprioritize Waypoint"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


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
    
    # 🚀 ADDED FOR GATE 3 & REACTOR INTEGRATION
    metrics: Dict[str, float] = Field(default_factory=dict)
    reactor_visual_url: Optional[str] = None
    reactor_prompt: Optional[str] = None

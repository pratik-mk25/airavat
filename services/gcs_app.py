"""
Streamlit GCS Main Application Entry Point with 3-Column Layout:
Top: Scenario Controls
Left: render_map_panel(data)
Middle: render_telemetry_panel(data)
Right: render_world_model_panel(data) & render_reactor_visual_panel(data)
"""

import time
import math
import streamlit as st
from services.gcs_map import render_map_panel
from services.gcs_panels import (
    render_controls,
    render_telemetry_panel,
    render_world_model_panel,
    render_reactor_visual_panel,
    DEFAULT_AI_URL
)

st.set_page_config(
    page_title="AIRAVAT Ground Control Station",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("AIRAVAT Ground Control Station")

# Initialize simulated drone position state in Streamlit session
if "sim_step" not in st.session_state:
    st.session_state.sim_step = 0

st.session_state.sim_step += 1
step = st.session_state.sim_step

# Base position (Bengaluru coordinates near planned route)
base_lat = 12.9716
base_lon = 77.5946

# Orbit/path simulation calculation
radius = 0.0006
angle = step * 0.1
current_lat = base_lat + radius * math.sin(angle)
current_lon = base_lon + radius * math.cos(angle)
current_alt = 45.0 + 5.0 * math.sin(step * 0.2)

current_mode = "AIRAVAT"

# Backend telemetry payload matching the integration contract
telemetry_data = {
    "state": {
        "position": {
            "lat": current_lat,
            "lon": current_lon,
            "alt": current_alt
        },
        "velocity": {
            "speed": 12.5,
            "yaw": math.degrees(angle)
        },
        "battery_pct": max(15.0, 100.0 - (step * 0.2)),
        "wind_ms": 5.2,
        "obstacle_distance_m": 120.0,
        "mission_progress_pct": min(100.0, step * 1.5)
    },
    "selected_action": "AIRAVAT Reroute" if step % 20 < 10 else "Continue",
    "world_model_predictions": [
        {
            "action": "Continue",
            "predicted_battery_pct": 78.5,
            "risk_level": "LOW",
            "eta_seconds": 120,
            "score": 0.99
        },
        {
            "action": "AIRAVAT Reroute",
            "predicted_battery_pct": 74.0,
            "risk_level": "LOW",
            "eta_seconds": 135,
            "score": 0.96
        },
        {
            "action": "Hold",
            "predicted_battery_pct": 70.0,
            "risk_level": "MEDIUM",
            "eta_seconds": 180,
            "score": 0.82
        }
    ],
    "reason": "AIRAVAT Qwen model predicts safe flight trajectory around obstacle zone.",
    "metrics": {
        "reactor_visual": "https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=600&auto=format&fit=crop&q=60"
    },
    "mode": current_mode,
    "status": "LIVE"
}

# Top Sidebar Controls
with st.sidebar:
    st.header("⚙️ Simulation Settings")
    ai_agent_url = st.text_input("AI Agent Endpoint URL", value=DEFAULT_AI_URL)
    auto_refresh = st.checkbox("Auto Refresh Stream", value=True)
    refresh_rate = st.slider("Update Interval (s)", 0.5, 3.0, 1.0)
    
    if st.button("Reset Telemetry Trail"):
        st.session_state.actual_route = []
        st.session_state.sim_step = 0
        st.rerun()

# 1. Top Scenario Controls Panel
render_controls(ai_agent_url, current_mode)

st.markdown("---")

# 2. 3-Column Dashboard Layout (Left, Middle, Right)
left, middle, right = st.columns([1, 1, 1])

with left:
    render_map_panel(telemetry_data)

with middle:
    render_telemetry_panel(telemetry_data)

with right:
    render_world_model_panel(telemetry_data)
    render_reactor_visual_panel(telemetry_data)

# Auto refresh trigger for live simulation demo
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()

"""
Person 3 owns this file.

This file renders:
- Scenario controls
- Telemetry panel
- World model prediction panel
- Selected action panel
- Reactor visual panel

Rules:
- Do not change function names.
- Do not change API paths.
- Do not change event/mode payload keys.
- Do not change data keys being read from the live payload.
- Aesthetic improvements are allowed in marked sections.
"""

import pandas as pd
import requests
import streamlit as st
import base64


# ============================================================
# 🎨 EDITABLE: UI LABELS
# Person 3 can improve these labels for a better demo.
# ============================================================

CONTROL_TITLE = "Scenario Controls"
TELEMETRY_TITLE = "Telemetry"
WORLD_MODEL_TITLE = "World Model"

BUTTON_WIND_LABEL = "💨 Inject Wind"
BUTTON_OBSTACLE_LABEL = "🚧 Inject Obstacle"
BUTTON_LOW_BATTERY_LABEL = "🪫 Low Battery"
BUTTON_RESET_LABEL = "♻️ Reset"

BUTTON_SWITCH_TO_BASELINE_LABEL = "Switch to Baseline"
BUTTON_SWITCH_TO_AIRAVAT_LABEL = "Switch to AIRAVAT"

BASELINE_WARNING = "Baseline mode: fixed mission plan active."
BASELINE_INFO = "World model is disabled in baseline mode."

NO_PREDICTIONS_INFO = "No world model predictions available."

SELECTED_ACTION_LABEL = "Selected Action"
MISSION_PROGRESS_LABEL = "Mission Progress"

SELECTED_MARKER = "⭐"

TABLE_HEIGHT = 300


# ============================================================
# 🎨 EDITABLE: THRESHOLDS AND COLORS
# Person 3 can tune these for visual clarity.
# Keep them reasonable for the demo.
# ============================================================

BATTERY_SAFE_THRESHOLD = 50
BATTERY_WARNING_THRESHOLD = 20

WIND_SAFE_THRESHOLD = 8
WIND_WARNING_THRESHOLD = 14

OBSTACLE_SAFE_THRESHOLD = 30
OBSTACLE_WARNING_THRESHOLD = 15

COLOR_SAFE = "#00c853"
COLOR_WARNING = "#ff9800"
COLOR_DANGER = "#ff1744"
COLOR_NEUTRAL = "#9e9e9e"


# ============================================================
# ⚠️ DO NOT EDIT: API CONTRACT CONSTANTS
#
# These must match the AI Agent endpoints.
# If these change, Person 1 must change the backend too.
# ============================================================

DEFAULT_AI_URL = "http://localhost:8000"

EVENT_ENDPOINT = "/event"
MODE_ENDPOINT = "/mode"

EVENT_WIND = "WIND"
EVENT_OBSTACLE = "OBSTACLE"
EVENT_LOW_BATTERY = "LOW_BATTERY"
EVENT_RESET = "RESET"

MODE_BASELINE = "BASELINE"
MODE_AIRAVAT = "AIRAVAT"


# ============================================================
# ⚠️ DO NOT EDIT: SAFE VALUE HELPER
# Protects UI if telemetry values are missing or invalid.
# ============================================================

def _safe_float(value, default):
    try:
        return float(value)
    except Exception:
        return default


# ============================================================
# ⚠️ DO NOT EDIT: API POST HELPER
#
# This is used by all control buttons.
# The path and JSON payload structure must stay compatible
# with the AI Agent.
# ============================================================

def _post(ai_url, path, payload):
    try:
        requests.post(
            f"{ai_url}{path}",
            json=payload,
            timeout=2,
        )
    except Exception:
        st.error("Could not reach AI Agent")


# ============================================================
# 🎨 EDITABLE: COLOR HELPER STYLE
# Person 3 can improve the visual style of telemetry badges.
# Keep the function names and returned HTML safe.
# ============================================================

def _colored_text(label, value, color):
    return (
        f"<div style='margin-bottom:10px;'>"
        f"<span style='color:{color}; font-weight:700;'>{label}</span><br/>"
        f"<span style='color:{color}; font-size:18px;'>{value}</span>"
        f"</div>"
    )


def _battery_color(value):
    if value > BATTERY_SAFE_THRESHOLD:
        return COLOR_SAFE
    if value >= BATTERY_WARNING_THRESHOLD:
        return COLOR_WARNING
    return COLOR_DANGER


def _wind_color(value):
    if value < WIND_SAFE_THRESHOLD:
        return COLOR_SAFE
    if value <= WIND_WARNING_THRESHOLD:
        return COLOR_WARNING
    return COLOR_DANGER


def _obstacle_color(value):
    if value > OBSTACLE_SAFE_THRESHOLD:
        return COLOR_SAFE
    if value >= OBSTACLE_WARNING_THRESHOLD:
        return COLOR_WARNING
    return COLOR_DANGER


# ============================================================
# ⚠️ DO NOT EDIT: CONTROL PANEL FUNCTION SIGNATURE
#
# gcs_app.py calls:
#
#   render_controls(AI_URL, mode)
#
# Do not change the function name or arguments.
# ============================================================

def render_controls(ai_url, current_mode=None):
    st.subheader(CONTROL_TITLE)

    if not ai_url:
        ai_url = DEFAULT_AI_URL

    col1, col2, col3, col4, col5 = st.columns(5)

    # --------------------------------------------------------
    # ⚠️ DO NOT EDIT: EVENT PAYLOADS
    # The "type" values must match backend event types.
    # --------------------------------------------------------
    with col1:
        if st.button(BUTTON_WIND_LABEL, use_container_width=True):
            _post(ai_url, EVENT_ENDPOINT, {"type": EVENT_WIND})

    with col2:
        if st.button(BUTTON_OBSTACLE_LABEL, use_container_width=True):
            _post(ai_url, EVENT_ENDPOINT, {"type": EVENT_OBSTACLE})

    with col3:
        if st.button(BUTTON_LOW_BATTERY_LABEL, use_container_width=True):
            _post(ai_url, EVENT_ENDPOINT, {"type": EVENT_LOW_BATTERY})

    with col4:
        if st.button(BUTTON_RESET_LABEL, use_container_width=True):
            _post(ai_url, EVENT_ENDPOINT, {"type": EVENT_RESET})

    # --------------------------------------------------------
    # ⚠️ DO NOT EDIT: MODE PAYLOADS
    # The "mode" values must match backend modes.
    # --------------------------------------------------------
    with col5:
        if current_mode == MODE_AIRAVAT:
            if st.button(BUTTON_SWITCH_TO_BASELINE_LABEL, use_container_width=True):
                _post(ai_url, MODE_ENDPOINT, {"mode": MODE_BASELINE})
        else:
            if st.button(BUTTON_SWITCH_TO_AIRAVAT_LABEL, use_container_width=True):
                _post(ai_url, MODE_ENDPOINT, {"mode": MODE_AIRAVAT})


# ============================================================
# ⚠️ DO NOT EDIT: TELEMETRY PANEL FUNCTION SIGNATURE
#
# gcs_app.py calls:
#
#   render_telemetry_panel(data)
#
# Do not change the function name or argument.
# ============================================================

def render_telemetry_panel(data):
    st.subheader(TELEMETRY_TITLE)

    # --------------------------------------------------------
    # ⚠️ DO NOT EDIT: PAYLOAD PARSING
    # These keys must match the shared backend contract.
    # --------------------------------------------------------
    state = data.get("state", {})

    battery = _safe_float(state.get("battery_pct", data.get("battery")), 0)
    wind = _safe_float(state.get("wind_ms", data.get("wind_speed")), 0)
    obstacle = _safe_float(state.get("obstacle_distance_m", data.get("obstacle_distance")), 0)
    progress = _safe_float(state.get("mission_progress_pct", data.get("mission_progress")), 0)

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # 🎨 EDITABLE: TELEMETRY CARD LAYOUT
    # Person 3 can improve layout, spacing, icons, and colors.
    # Keep the values readable.
    # --------------------------------------------------------
    with col1:
        st.markdown(
            _colored_text(
                "Battery",
                f"{battery:.1f}%",
                _battery_color(battery),
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            _colored_text(
                "Obstacle Distance",
                f"{obstacle:.1f}m",
                _obstacle_color(obstacle),
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            _colored_text(
                "Wind",
                f"{wind:.1f} m/s",
                _wind_color(wind),
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            _colored_text(
                MISSION_PROGRESS_LABEL,
                f"{progress:.1f}%",
                COLOR_NEUTRAL,
            ),
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # 🎨 EDITABLE: PROGRESS BAR STYLE
    # Person 3 can replace this with a better progress UI.
    # --------------------------------------------------------
    st.progress(min(max(progress, 0), 100) / 100)


# ============================================================
# ⚠️ DO NOT EDIT: WORLD MODEL PANEL FUNCTION SIGNATURE
#
# gcs_app.py calls:
#
#   render_world_model_panel(data)
#
# Do not change the function name or argument.
# ============================================================

def render_world_model_panel(data):
    st.subheader(WORLD_MODEL_TITLE)

    # --------------------------------------------------------
    # ⚠️ DO NOT EDIT: MODE PARSING
    # The mode value must match the backend contract.
    # --------------------------------------------------------
    mode = data.get("mode", MODE_AIRAVAT)

    if mode == MODE_BASELINE:
        st.warning(BASELINE_WARNING)
        st.info(BASELINE_INFO)
        return

    # --------------------------------------------------------
    # ⚠️ DO NOT EDIT: PREDICTION PARSING
    # These keys must match the backend contract.
    # --------------------------------------------------------
    predictions = data.get("world_model_predictions", [
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
    ])

    if not predictions:
        st.info(NO_PREDICTIONS_INFO)
        return

    df = pd.DataFrame(predictions)

    # --------------------------------------------------------
    # ⚠️ DO NOT EDIT: REQUIRED WORLD MODEL COLUMNS
    # These are the expected fields from the AI Agent.
    # --------------------------------------------------------
    required_columns = [
        "action",
        "predicted_battery_pct",
        "risk_level",
        "eta_seconds",
        "score",
    ]

    for col in required_columns:
        if col not in df.columns:
            df[col] = 0 if col != "action" else "Continue"

    df = df.reindex(columns=required_columns)
    df = df.sort_values("score", ascending=False)

    selected_action = data.get("selected_action", "AIRAVAT Reroute")

    # --------------------------------------------------------
    # 🎨 EDITABLE: SELECTED ACTION MARKER
    # Person 3 can change the marker style.
    # --------------------------------------------------------
    df["selected"] = df["action"].apply(
        lambda action: SELECTED_MARKER if action == selected_action else ""
    )

    column_order = [
        "selected",
        "action",
        "predicted_battery_pct",
        "risk_level",
        "eta_seconds",
        "score",
    ]

    df = df[column_order]

    # --------------------------------------------------------
    # 🎨 EDITABLE: TABLE COLUMN LABELS
    # Person 3 can improve these labels.
    # Do not remove columns.
    # --------------------------------------------------------
    df.columns = [
        "",
        "Action",
        "Predicted Battery %",
        "Risk",
        "ETA s",
        "Score",
    ]

    # --------------------------------------------------------
    # 🎨 EDITABLE: TABLE DISPLAY
    # Person 3 can improve table height, styling, highlighting.
    # Keep it readable.
    # --------------------------------------------------------
    st.dataframe(
        df,
        use_container_width=True,
        height=TABLE_HEIGHT,
    )

    # --------------------------------------------------------
    # 🎨 EDITABLE: SELECTED ACTION DISPLAY
    # Person 3 can make this stronger and more visible.
    # --------------------------------------------------------
    st.success(f"{SELECTED_ACTION_LABEL}: {selected_action}")

    # --------------------------------------------------------
    # ⚠️ DO NOT EDIT: REASON FIELD PARSING
    # The reason comes from the AI Agent.
    # --------------------------------------------------------
    reason = data.get("reason", data.get("ai_explanation", "AIRAVAT Qwen model predicts safe flight trajectory around obstacle zone."))

    if reason:
        st.info(reason)


def render_reactor_visual_panel(data):
    st.subheader("👁️ Reactor Visual World Model")
    
    metrics = data.get("metrics", {})
    visual_url = metrics.get("reactor_visual")
    
    if not visual_url:
        st.info("Waiting for Reactor visual prediction...")
        return
        
    st.caption(f"Predicted visual outcome for action: **{data.get('selected_action', 'Continue')}**")
    
    # Handle URL or Base64
    try:
        if isinstance(visual_url, str) and visual_url.startswith("http"):
            st.image(visual_url, use_container_width=True)
        else:
            # If base64 string or bytes
            if isinstance(visual_url, str):
                if "," in visual_url:
                    visual_url = visual_url.split(",")[1]
                img_data = base64.b64decode(visual_url)
            else:
                img_data = visual_url
            st.image(img_data, use_container_width=True)
    except Exception as e:
        st.error(f"Error rendering reactor visual: {e}")

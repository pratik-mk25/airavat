import base64
import os
import time

import pandas as pd
import requests
import streamlit as st

AI_URL = os.getenv("AI_URL", "http://localhost:8000")

st.set_page_config(
    page_title="TESSERACT-X | AIRAVAT GCS",
    layout="wide",
)

st.title("TESSERACT-X | AIRAVAT GCS")
st.caption("All-Python Ground Control Station & Reactor.inc Visual World Model")

# --- SIDEBAR CONTROL PANEL ---
st.sidebar.title("🎛️ Flight Control Panel")

# Mode Selection
st.sidebar.subheader("Mode Selection")
mode_choice = st.sidebar.radio(
    "Active Control Layer",
    ["AIRAVAT", "BASELINE"],
    index=0
)

if st.sidebar.button("Set Active Mode"):
    try:
        res = requests.post(f"{AI_URL}/mode", json={"mode": mode_choice}, timeout=2)
        if res.status_code == 200:
            st.sidebar.success(f"Mode set to: {mode_choice}")
    except Exception as e:
        st.sidebar.error(f"Error setting mode: {e}")

# Interactive Fault Injection Buttons
st.sidebar.subheader("Interactive Fault Injection")

col_btn1, col_btn2 = st.sidebar.columns(2)

if col_btn1.button("🌬️ Inject Wind"):
    try:
        requests.post(f"{AI_URL}/event", json={"type": "WIND"}, timeout=2)
        st.sidebar.warning("Injected +8 m/s Wind Spike (TTL: 20 ticks)")
    except Exception as e:
        st.sidebar.error(f"Failed: {e}")

if col_btn2.button("🛑 Inject Obstacle"):
    try:
        requests.post(f"{AI_URL}/event", json={"type": "OBSTACLE"}, timeout=2)
        st.sidebar.warning("Injected -25m Obstacle Proximity (TTL: 20 ticks)")
    except Exception as e:
        st.sidebar.error(f"Failed: {e}")

if col_btn1.button("🪫 Low Battery"):
    try:
        requests.post(f"{AI_URL}/event", json={"type": "LOW_BATTERY"}, timeout=2)
        st.sidebar.warning("Injected -25% Battery Drop (TTL: 20 ticks)")
    except Exception as e:
        st.sidebar.error(f"Failed: {e}")

if col_btn2.button("♻️ Reset Env"):
    try:
        requests.post(f"{AI_URL}/event", json={"type": "RESET"}, timeout=2)
        st.sidebar.info("Environment Overrides Cleared")
    except Exception as e:
        st.sidebar.error(f"Failed: {e}")


def render_reactor_visual_panel(data: dict):
    """Renders the Reactor.inc Visual World Model FPV frame prediction."""
    st.subheader("👁️ Reactor Visual World Model")
    
    visual_url = data.get("reactor_visual_url") or data.get("metrics", {}).get("reactor_visual")
    prompt = data.get("reactor_prompt")
    
    if not visual_url:
        st.info("Waiting for Reactor visual prediction...")
        return

    if prompt:
        st.caption(f"Prompt: *\"{prompt}\"*")
    else:
        st.caption(f"Predicted FPV visual outcome for action: **{data.get('selected_action')}**")

    if visual_url.startswith("http") or visual_url.startswith("data:image"):
        st.image(visual_url, use_container_width=True)
    else:
        try:
            st.image(base64.b64decode(visual_url), use_container_width=True)
        except Exception:
            st.image(visual_url, use_container_width=True)


# --- MAIN DASHBOARD CONTENT ---
try:
    response = requests.get(f"{AI_URL}/live", timeout=2)
    data = response.json()
except Exception:
    data = None

if not data or data.get("status") == "WAITING":
    st.warning("Waiting for simulation state...")
    st.info("Make sure SIM Agent and AI Agent are running.")

elif data.get("status") == "LIVE":
    state = data["state"]

    mode_badge = "🟢 AIRAVAT AI ACTIVE" if data.get("mode") == "AIRAVAT" else "🔴 BASELINE (FIXED PLAN)"
    st.subheader(f"System Status: {mode_badge}")

    # Top Row Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Battery %", f"{state['battery_pct']:.1f}%")
    col2.metric("Wind m/s", f"{state['wind_ms']:.1f}")
    col3.metric("Obstacle m", f"{state['obstacle_distance_m']:.1f}")
    col4.metric("Mission Progress", f"{state['mission_progress_pct']:.1f}%")

    if data.get("mode") == "AIRAVAT":
        st.success(f"Selected Action: {data['selected_action']}")
        st.info(data["reason"])
    else:
        st.error(f"Selected Action: {data['selected_action']}")
        st.warning(data["reason"])

    # Two-Column Layout: Left (World Model Table & Position) | Right (Reactor Visual Panel)
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("Predictive World Model Outcomes")
        df = pd.DataFrame(data.get("world_model_predictions", []))
        if not df.empty:
            df = df.sort_values("score", ascending=False)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No predictions in Baseline Mode (Fixed Plan active).")

        st.subheader("Position Telemetry")
        position = state["position"]
        st.write(
            f"📍 **Latitude**: `{position['lat']:.6f}` | "
            f"**Longitude**: `{position['lon']:.6f}` | "
            f"**Altitude**: `{position['alt']:.1f}m`"
        )

        # Performance Metrics Summary
        metrics = data.get("metrics", {})
        if metrics:
            st.subheader("Flight Performance Metrics")
            m_col1, m_col2 = st.columns(2)
            m_col1.metric("Danger Events", metrics.get("danger_events", 0))
            m_col2.metric("Min Obstacle Dist", f"{metrics.get('min_obstacle_distance', 0):.1f}m")

    with right_col:
        render_reactor_visual_panel(data)

    with st.expander("Raw Live Payload JSON"):
        st.json(data)

else:
    st.error("Unknown payload format")

time.sleep(2)

try:
    st.rerun()
except Exception:
    st.experimental_rerun()

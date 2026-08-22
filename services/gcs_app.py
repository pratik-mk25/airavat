import os
import time

import pandas as pd
import requests
import streamlit as st

AI_URL = os.getenv("AI_URL", "http://localhost:8000")

st.set_page_config(
    page_title="TESSERACT-X GCS",
    layout="wide",
)

st.title("TESSERACT-X | AIRAVAT GCS")
st.caption("All-Python Ground Control Station & Interactive Fault Injector")

# --- SIDEBAR CONTROL PANEL ---
st.sidebar.title("🎛️ Flight Control Panel")

# Mode Toggle
st.sidebar.subheader("Mode Selection")
mode_choice = st.sidebar.radio(
    "Active Control Layer",
    ["AIRAVAT (AI Active)", "BASELINE (Fixed Mission Plan)"],
    index=0
)
target_mode = "AIRAVAT" if "AIRAVAT" in mode_choice else "BASELINE"

if st.sidebar.button("Set Active Mode"):
    try:
        res = requests.post(f"{AI_URL}/mode", json={"mode": target_mode}, timeout=2)
        if res.status_code == 200:
            st.sidebar.success(f"Mode set to: {target_mode}")
    except Exception as e:
        st.sidebar.error(f"Error setting mode: {e}")

# Interactive Fault Injection Buttons
st.sidebar.subheader("Interactive Fault Injection")

col_btn1, col_btn2 = st.sidebar.columns(2)

if col_btn1.button("🌬️ Inject Wind"):
    try:
        requests.post(f"{AI_URL}/event", json={"event_type": "INJECT_WIND", "value": 16.5, "description": "16.5 m/s Wind Spike"}, timeout=2)
        st.sidebar.warning("Injected 16.5 m/s Wind Gust")
    except Exception as e:
        st.sidebar.error(f"Failed: {e}")

if col_btn2.button("🛑 Inject Obstacle"):
    try:
        requests.post(f"{AI_URL}/event", json={"event_type": "INJECT_OBSTACLE", "value": 4.5, "description": "4.5m Obstacle Blockade"}, timeout=2)
        st.sidebar.warning("Injected 4.5m Obstacle Blockade")
    except Exception as e:
        st.sidebar.error(f"Failed: {e}")

if col_btn1.button("🪫 Low Battery"):
    try:
        requests.post(f"{AI_URL}/event", json={"event_type": "LOW_BATTERY", "value": 18.0, "description": "Critical 18% Battery Drop"}, timeout=2)
        st.sidebar.warning("Injected 18% Low Battery Drop")
    except Exception as e:
        st.sidebar.error(f"Failed: {e}")

if col_btn2.button("♻️ Reset Env"):
    try:
        requests.post(f"{AI_URL}/event", json={"event_type": "RESET", "value": 0, "description": "Reset Environmental Overrides"}, timeout=2)
        st.sidebar.info("Environment Overrides Cleared")
    except Exception as e:
        st.sidebar.error(f"Failed: {e}")

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

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Battery %",
        f"{state['battery_pct']:.1f}%",
    )

    col2.metric(
        "Wind m/s",
        f"{state['wind_ms']:.1f}",
    )

    col3.metric(
        "Obstacle m",
        f"{state['obstacle_distance_m']:.1f}",
    )

    col4.metric(
        "Mission Progress",
        f"{state['mission_progress_pct']:.1f}%",
    )

    if data.get("mode") == "AIRAVAT":
        st.success(f"Selected Action: {data['selected_action']}")
        st.info(data["reason"])
    else:
        st.error(f"Selected Action: {data['selected_action']}")
        st.warning(data["reason"])

    st.subheader("World Model Predictions")

    df = pd.DataFrame(data["world_model_predictions"])
    df = df.sort_values("score", ascending=False)

    st.dataframe(df, use_container_width=True)

    st.subheader("Position")

    position = state["position"]

    st.write(
        f"Latitude: {position['lat']:.6f}, "
        f"Longitude: {position['lon']:.6f}, "
        f"Altitude: {position['alt']:.1f}m"
    )

    with st.expander("Raw Live Payload"):
        st.json(data)

else:
    st.error("Unknown payload format")

time.sleep(2)

try:
    st.rerun()
except Exception:
    st.experimental_rerun()

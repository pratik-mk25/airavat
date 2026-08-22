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
st.caption("All-Python Ground Control Station")

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

    st.success(f"Selected Action: {data['selected_action']}")
    st.info(data["reason"])

    st.subheader("World Model Predictions")

    df = pd.DataFrame(data["world_model_predictions"])
    df = df.sort_values("score", ascending=False)

    st.dataframe(df)

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

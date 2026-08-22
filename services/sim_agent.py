"""
Person 1 owns this file.

SIM Agent

Responsibilities:
- Generate mission telemetry
- Send telemetry to AIRAVAT AI Agent

For Gate 2, use MockSim.
For later gates, Person 1 can replace generate_state()
with PX4 SITL / MAVSDK telemetry.
"""

import math
import os
import time
from datetime import datetime, timezone

import requests


# ============================================================
# 🎨 EDITABLE: SIMULATION NETWORK SETTINGS
# ============================================================

AI_URL = os.getenv("AI_URL", "http://localhost:8000")
SIM_INTERVAL_SECONDS = float(os.getenv("SIM_INTERVAL_SECONDS", "1"))


# ============================================================
# 🎨 EDITABLE: MOCK MISSION BEHAVIOR
# Person 1 can tune this to create a better demo curve.
# Keep values realistic.
# ============================================================

def generate_state(tick: int) -> dict:
    battery = max(5, 92 - tick * 0.35)

    wind = min(
        18,
        5 + 2 * math.sin(tick / 12) + tick * 0.05,
    )

    obstacle = max(
        6,
        65 - tick * 0.8,
    )

    progress = min(
        100,
        tick * 0.8,
    )

    lat = 12.9716 + 0.0002 * math.sin(tick / 10)
    lon = 77.5946 + 0.0002 * math.cos(tick / 10)
    alt = 40 + math.sin(tick / 5)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "battery_pct": battery,
        "wind_ms": wind,
        "obstacle_distance_m": obstacle,
        "mission_progress_pct": progress,
        "position": {
            "lat": lat,
            "lon": lon,
            "alt": alt,
        },
    }


# ============================================================
# ⚠️ DO NOT EDIT: POST LOOP
# This sends telemetry to the AI Agent.
# ============================================================

def main():
    tick = 0

    print(f"SIM Agent sending telemetry to {AI_URL}/state")

    while True:
        state = generate_state(tick)

        try:
            response = requests.post(
                f"{AI_URL}/state",
                json=state,
                timeout=2,
            )

            print(f"Tick {tick}: HTTP {response.status_code}")

        except Exception as error:
            print(f"SIM Agent error: {error}")

        tick += 1
        time.sleep(SIM_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()

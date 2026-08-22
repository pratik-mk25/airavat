"""
services/sim_agent.py
PERSON 1 OWNS THIS FILE.
"""
import math
import os
import time
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
AI_URL = os.getenv("AI_URL", "http://localhost:8000")


def generate_state(tick: int) -> dict:
    # Smooth, realistic degradation curves
    battery = max(5, 92 - tick * 0.35)
    wind = min(18, 5 + 2 * math.sin(tick / 12) + tick * 0.05)
    obstacle = max(6, 65 - tick * 0.8)
    progress = min(100, tick * 0.8)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "battery_pct": battery,
        "wind_ms": wind,
        "obstacle_distance_m": obstacle,
        "mission_progress_pct": progress,
        "position": {
            "lat": 12.9716 + 0.0002 * math.sin(tick / 10),
            "lon": 77.5946 + 0.0002 * math.cos(tick / 10),
            "alt": 40 + math.sin(tick / 5),
        },
    }


def main():
    tick = 0
    print(f"SIM Agent sending telemetry to {AI_URL}/state")
    while True:
        state = generate_state(tick)
        try:
            res = requests.post(f"{AI_URL}/state", json=state, timeout=2)
            print(f"Tick {tick}: HTTP {res.status_code}")
        except Exception as e:
            print(f"SIM Error: {e}")
        tick += 1
        time.sleep(1)


if __name__ == "__main__":
    main()

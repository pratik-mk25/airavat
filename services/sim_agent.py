import math
import os
import time
from datetime import datetime, timezone

import requests

AI_URL = os.getenv("AI_URL", "http://localhost:8000")


def generate_state(tick: int) -> dict:
    battery = max(5, 90 - tick * 0.4)
    wind = min(18, 5 + tick * 0.1)
    obstacle = max(6, 60 - tick * 0.7)
    progress = min(100, tick * 1.0)

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


def main():
    tick = 0

    print(f"SIM Agent sending telemetry to {AI_URL}/state")

    while True:
        state = generate_state(tick)

        try:
            response = requests.post(f"{AI_URL}/state", json=state, timeout=2)
            print(f"Tick {tick}: HTTP {response.status_code}")
        except Exception as error:
            print(f"SIM Agent error: {error}")

        tick += 1
        time.sleep(1)


if __name__ == "__main__":
    main()

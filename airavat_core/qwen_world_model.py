"""
Qwen World Model Physical AI Engine Simulator for AIRAVAT GCS.
Simulates real-world physical dynamics reasoning: cross-wind turbulence, battery thermal drain,
spatial proximity to non-cooperative obstacles, and automated action recommendations.
"""

import time
import math

class QwenWorldModel:
    def __init__(self):
        self.last_reason_time = 0
        self.history_logs = [
            f"[{time.strftime('%H:%M:%S')}] [INIT] Qwen-Physical-AI world model initialized.",
            f"[{time.strftime('%H:%M:%S')}] [PHYSICS] Aerodynamic wind vector model loaded.",
            f"[{time.strftime('%H:%M:%S')}] [BASELINE] Monitoring telemetry stream."
        ]

    def evaluate_state(self, battery, wind_speed, obstacle_dist, progress, mode, is_paused):
        """
        Evaluates physical environment telemetry and returns AI recommendation state.
        
        Actions: Continue | Reroute | Hold | Return Early | Reprioritize Waypoint
        Risk Levels: LOW | MEDIUM | HIGH | CRITICAL
        """
        if is_paused:
            return {
                "action": "Hold",
                "confidence": 99.8,
                "explanation": "Mission currently paused by operator. Holding position altitude and maintaining hovering thrust dynamics.",
                "risk_level": "LOW",
                "logs": self.history_logs
            }

        # 1. Critical Battery Evaluation (< 20%)
        if battery <= 22.0:
            action = "Return Early"
            risk_level = "CRITICAL" if battery < 15.0 else "HIGH"
            confidence = 98.5
            explanation = (
                f"CRITICAL: Battery level depleted to {battery:.1f}%. Qwen energy model predicts "
                f"insufficient reserve energy to complete remaining {100-progress:.0f}% mission path under "
                f"{wind_speed:.1f} m/s wind resistance. Initiating Return-To-Launch (RTL)."
            )
            self._add_log(f"[WARN] Battery critical ({battery:.1f}%). Triggered Return Early protocol.")

        # 2. Obstacle Proximity Evaluation (< 45m)
        elif obstacle_dist < 45.0:
            if mode == "AIRAVAT":
                action = "Reroute"
                risk_level = "MEDIUM" if obstacle_dist > 25.0 else "HIGH"
                confidence = 96.2
                explanation = (
                    f"AIRAVAT physical model detected unmapped spatial obstacle at {obstacle_dist:.1f}m distance. "
                    f"Qwen World Model calculates a 3D adaptive spline detour offsetting +28m North-East to bypass collision zone."
                )
                self._add_log(f"[REROUTE] Dynamic obstacle at {obstacle_dist:.1f}m. AIRAVAT spline reroute active.")
            else:
                action = "Hold"
                risk_level = "HIGH"
                confidence = 89.0
                explanation = (
                    f"WARNING: Obstacle detected at {obstacle_dist:.1f}m. Baseline autopilot has no active AI collision avoidance. "
                    f"Holding position to prevent crash impact."
                )
                self._add_log(f"[ALERT] Obstacle at {obstacle_dist:.1f}m in Baseline mode! Holding position.")

        # 3. High Wind Turbulence (> 9.0 m/s)
        elif wind_speed >= 9.0:
            if mode == "AIRAVAT":
                action = "Reprioritize Waypoint"
                risk_level = "MEDIUM"
                confidence = 93.4
                explanation = (
                    f"High wind shear detected at {wind_speed:.1f} m/s. AIRAVAT Qwen model re-indexes waypoint priority "
                    f"to minimize cross-wind drift and optimize battery thrust efficiency."
                )
                self._add_log(f"[WIND] High wind shear ({wind_speed:.1f} m/s). Reprioritizing waypoints.")
            else:
                action = "Continue"
                risk_level = "HIGH"
                confidence = 74.0
                explanation = (
                    f"High wind shear ({wind_speed:.1f} m/s). Baseline mode continuing on rigid path. "
                    f"Attitude drift expected."
                )

        # 4. Nominal Flight Path
        else:
            action = "Continue"
            risk_level = "LOW"
            confidence = 99.1
            explanation = (
                f"Nominal flight parameters detected. Wind vector {wind_speed:.1f} m/s within aerodynamic stability margin. "
                f"AIRAVAT Qwen world model predicts 99.1% mission success probability on current trajectory."
            )
            if len(self.history_logs) < 15 and time.time() - self.last_reason_time > 4.0:
                self._add_log(f"[NOMINAL] Telemetry nominal. Wind {wind_speed:.1f}m/s | Batt {battery:.0f}%.")
                self.last_reason_time = time.time()

        return {
            "action": action,
            "confidence": confidence,
            "explanation": explanation,
            "risk_level": risk_level,
            "logs": self.history_logs[-12:]
        }

    def _add_log(self, text):
        t_str = time.strftime('%H:%M:%S')
        log_entry = f"[{t_str}] {text}"
        if not self.history_logs or self.history_logs[-1] != log_entry:
            self.history_logs.append(log_entry)
            if len(self.history_logs) > 50:
                self.history_logs.pop(0)

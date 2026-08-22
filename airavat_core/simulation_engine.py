"""
Real-time Flight Simulation & Physics Engine for AIRAVAT GCS.
Runs continuous telemetry update loop emitting state data to the UI panels.
Conforms to standard backend telemetry schema with 'state' -> 'position' -> ('lat', 'lon', 'alt')
and 'metrics' -> 'reactor_visual' for the Reactor Visual World Model.
"""

import time
import math
import base64
from PySide6.QtCore import QThread, Signal
from airavat_core.mission_planner import MissionPlanner
from airavat_core.qwen_world_model import QwenWorldModel

class SimulationEngine(QThread):
    # Qt Signal emitting complete telemetry frame dictionary to UI
    telemetry_updated = Signal(dict)

    def __init__(self):
        super().__init__()
        self.running = True
        self.is_paused = True
        
        # State Modes
        self.status = "LIVE"          # LIVE | REPLAY
        self.mode = "AIRAVAT"        # Baseline | AIRAVAT
        
        # Mission Planner & Physics
        self.planner = MissionPlanner()
        self.qwen_ai = QwenWorldModel()
        
        # Telemetry State Variables
        self.reset_state()

    def reset_state(self):
        self.battery = 88.0
        self.wind_speed = 4.2
        self.wind_angle = 45.0
        self.obstacle_distance = 120.0
        self.speed = 12.8
        self.altitude = 45.0
        self.mission_progress = 0.0
        
        # Flight path tracking
        self.route = self.planner.get_planned_route()
        self.current_waypoint_idx = 0
        self.drone_pos = list(self.route[0])
        self.drone_yaw = 0.0
        self.obstacles = []
        
        self.time_elapsed = 0.0

    def run(self):
        """Thread loop running at 10 Hz (100ms updates)."""
        while self.running:
            if not self.is_paused:
                self.update_physics()
            
            # Evaluate Qwen Physical AI Reasoning
            ai_decision = self.qwen_ai.evaluate_state(
                battery=self.battery,
                wind_speed=self.wind_speed,
                obstacle_dist=self.obstacle_distance,
                progress=self.mission_progress,
                mode=self.mode,
                is_paused=self.is_paused
            )

            # Compute current paths
            airavat_path = self.planner.calculate_airavat_path(
                drone_pos=self.drone_pos,
                obstacles=self.obstacles,
                wind_speed=self.wind_speed,
                is_airavat_mode=(self.mode == "AIRAVAT")
            )
            
            rtl_path = self.planner.get_rtl_path(self.drone_pos)

            # Standardized State Object conforming to Backend Telemetry Contract
            state_contract = {
                "position": {
                    "lat": self.drone_pos[0],
                    "lon": self.drone_pos[1],
                    "alt": self.altitude
                },
                "velocity": {
                    "speed": self.speed,
                    "yaw": self.drone_yaw
                },
                "battery": self.battery,
                "wind": {
                    "speed": self.wind_speed,
                    "angle": self.wind_angle
                }
            }

            # Assemble full telemetry frame payload including Reactor Visual World Model metrics
            payload = {
                # Shared Backend Contract State
                "state": state_contract,
                "selected_action": ai_decision["action"],
                "metrics": {
                    "reactor_visual": "https://images.unsplash.com/photo-1508614589041-895b88991e3e?w=600&auto=format&fit=crop&q=60"
                },

                # Header telemetry
                "status": self.status,
                "mode": self.mode,
                "mission_progress": round(self.mission_progress, 1),
                "battery": round(self.battery, 1),
                "wind_speed": round(self.wind_speed, 1),
                "risk_level": ai_decision["risk_level"],
                
                # Numeric readouts & speed/alt
                "speed": round(self.speed, 1),
                "altitude": round(self.altitude, 1),
                "obstacle_distance": round(self.obstacle_distance, 1),
                
                # Map / Digital Twin payload
                "drone_pos": self.drone_pos,
                "drone_yaw": round(self.drone_yaw, 1),
                "planned_route": self.planner.get_planned_route(),
                "airavat_route": airavat_path,
                "rtl_route": rtl_path,
                "waypoints": self.planner.get_waypoints(),
                "obstacles": self.obstacles,
                "rtl_point": self.planner.rtl_point,
                "wind": {"speed": self.wind_speed, "angle": self.wind_angle},
                
                # AI Feed payload
                "ai_action": ai_decision["action"],
                "ai_confidence": ai_decision["confidence"],
                "ai_explanation": ai_decision["explanation"],
                "ai_logs": ai_decision["logs"],
                "is_paused": self.is_paused
            }
            
            self.telemetry_updated.emit(payload)
            time.sleep(0.1)

    def update_physics(self):
        """Updates simulated drone position along path with speed, wind drift & battery drain."""
        self.time_elapsed += 0.1
        
        # 1. Battery Drain dynamics
        drain_rate = 0.05 + (self.wind_speed * 0.008)
        self.battery = max(0.0, self.battery - drain_rate)

        # 2. Movement along route
        target = self.route[self.current_waypoint_idx % len(self.route)]
        curr_lat, curr_lng = self.drone_pos
        t_lat, t_lng = target
        
        d_lat = t_lat - curr_lat
        d_lng = t_lng - curr_lng
        dist = math.sqrt(d_lat**2 + d_lng**2)

        if dist < 0.0003:
            # Advance to next waypoint
            self.current_waypoint_idx = (self.current_waypoint_idx + 1) % len(self.route)
        else:
            # Calculate heading yaw angle
            self.drone_yaw = math.degrees(math.atan2(d_lng, d_lat))
            
            # Step size based on speed (converted to approx lat/lng delta)
            step = (self.speed * 0.00001)
            self.drone_pos[0] += (d_lat / dist) * step
            self.drone_pos[1] += (d_lng / dist) * step

        # 3. Mission Progress % calculation
        total_wps = len(self.route)
        self.mission_progress = min(100.0, ((self.current_waypoint_idx + (1.0 - dist/0.005)) / total_wps) * 100.0)

        # 4. Obstacle Distance calculation if obstacles present
        if self.obstacles:
            closest = min([math.sqrt((self.drone_pos[0]-o['lat'])**2 + (self.drone_pos[1]-o['lng'])**2) * 100000 for o in self.obstacles])
            self.obstacle_distance = max(5.0, closest)
        else:
            self.obstacle_distance = min(180.0, self.obstacle_distance + 0.5)

    # User Control Methods
    def toggle_start_pause(self):
        self.is_paused = not self.is_paused

    def reset_mission(self):
        self.is_paused = True
        self.reset_state()

    def inject_wind(self):
        """Spikes wind speed to simulate sudden turbulence gust."""
        self.wind_speed = min(18.0, self.wind_speed + 5.5)
        self.wind_angle = (self.wind_angle + 60.0) % 360.0

    def inject_obstacle(self):
        """Injects a dynamic obstacle directly ahead of current drone flight path."""
        curr_lat, curr_lng = self.drone_pos
        obs_lat = curr_lat + math.cos(math.radians(self.drone_yaw)) * 0.0006
        obs_lng = curr_lng + math.sin(math.radians(self.drone_yaw)) * 0.0006
        obs_id = len(self.obstacles) + 1
        self.obstacles.append({'id': obs_id, 'lat': obs_lat, 'lng': obs_lng, 'radius': 30})
        self.obstacle_distance = 38.0

    def trigger_low_battery(self):
        """Forces low battery event (drops battery to 18%)."""
        self.battery = 18.0

    def toggle_mode(self):
        """Toggles between Baseline autopilot and AIRAVAT physical AI mode."""
        self.mode = "Baseline" if self.mode == "AIRAVAT" else "AIRAVAT"

    def toggle_status(self):
        """Toggles between LIVE telemetry and REPLAY mode."""
        self.status = "REPLAY" if self.status == "LIVE" else "LIVE"

    def stop(self):
        self.running = False
        self.wait()

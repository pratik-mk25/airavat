"""
Mission Planner Module for AIRAVAT GCS
Manages waypoints, planned route (red dotted), AIRAVAT dynamic path (green line), and RTL return path.
"""

import math

class MissionPlanner:
    def __init__(self, origin_lat=37.7749, origin_lng=-122.4194):
        self.origin = (origin_lat, origin_lng)
        self.rtl_point = (origin_lat, origin_lng)
        
        # Default 5-Waypoint Mission forming a perimeter search pattern
        self.waypoints = [
            (origin_lat + 0.0015, origin_lng + 0.0010),  # WP-1
            (origin_lat + 0.0030, origin_lng + 0.0025),  # WP-2
            (origin_lat + 0.0025, origin_lng + 0.0050),  # WP-3
            (origin_lat + 0.0005, origin_lng + 0.0045),  # WP-4
            (origin_lat - 0.0005, origin_lng + 0.0020),  # WP-5
        ]
        
        # Build planned route (Origin -> WP1 -> WP2 -> WP3 -> WP4 -> WP5 -> Origin)
        self.planned_route = [self.origin] + self.waypoints + [self.origin]
        self.airavat_route = list(self.planned_route)
        
    def get_planned_route(self):
        return self.planned_route

    def get_waypoints(self):
        return self.waypoints

    def calculate_airavat_path(self, drone_pos, obstacles, wind_speed, is_airavat_mode):
        """
        Computes dynamic AIRAVAT path (green line).
        If AIRAVAT mode is enabled and obstacles/high wind are present,
        it calculates adaptive detour splines around dynamic obstacle hazards.
        """
        if not is_airavat_mode or not obstacles:
            self.airavat_route = list(self.planned_route)
            return self.airavat_route

        # Calculate detour around obstacles
        new_path = []
        for point in self.planned_route:
            p_lat, p_lng = point
            offset_lat, offset_lng = 0.0, 0.0
            
            for obs in obstacles:
                o_lat, o_lng = obs['lat'], obs['lng']
                dist = math.sqrt((p_lat - o_lat)**2 + (p_lng - o_lng)**2)
                # If path point is close to an obstacle, compute repellent vector
                if dist < 0.0015:
                    angle = math.atan2(p_lat - o_lat, p_lng - o_lng)
                    repel = 0.0012 - dist
                    offset_lat += math.sin(angle) * repel * 1.5
                    offset_lng += math.cos(angle) * repel * 1.5
            
            # Apply wind offset drift compensation if wind is high
            if wind_speed > 6.0:
                offset_lng += (wind_speed - 6.0) * 0.00005

            new_path.append([p_lat + offset_lat, p_lng + offset_lng])

        self.airavat_route = new_path
        return self.airavat_route

    def get_rtl_path(self, current_pos):
        """Generates Return-To-Launch direct path from current position back to origin."""
        return [current_pos, self.rtl_point]

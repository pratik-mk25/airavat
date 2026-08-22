"""
Person 2 owns this file.

This file renders the Mission Map panel.

Rules:
- Do not change the function name.
- Do not change the data keys being read.
- Do not change the session_state key unless all teammates agree.
- Aesthetic improvements are allowed in marked sections.
"""

import streamlit as st


# ============================================================
# 🎨 EDITABLE: MISSION GEOGRAPHY
# Person 2 can edit these for a better-looking demo mission.
# Keep coordinates near the simulator coordinates.
# ============================================================

PLANNED_ROUTE = [
    (12.9716, 77.5946),
    (12.9718, 77.5948),
    (12.9720, 77.5950),
    (12.9722, 77.5952),
    (12.9716, 77.5946),
]

OBSTACLES = [
    {
        "name": "Obstacle A",
        "lat": 12.9720,
        "lon": 77.5950,
        "radius": 25,
    },
    {
        "name": "Obstacle B",
        "lat": 12.9722,
        "lon": 77.5951,
        "radius": 18,
    },
]

RETURN_HOME = (12.9716, 77.5946)


# ============================================================
# 🎨 EDITABLE: VISUAL THEME
# Person 2 can change these freely.
# ============================================================

MAP_TITLE = "Mission Map"

MAP_TILES = "CartoDB dark_matter"
# Other options:
# "CartoDB positron"
# "OpenStreetMap"

MAP_ZOOM = 15
MAP_HEIGHT = 430

PLANNED_ROUTE_COLOR = "red"
PLANNED_ROUTE_WEIGHT = 3
PLANNED_ROUTE_DASH = "6"

ACTUAL_ROUTE_COLOR = "green"
ACTUAL_ROUTE_WEIGHT = 3

OBSTACLE_COLOR = "orange"
OBSTACLE_FILL_OPACITY = 0.25

DRONE_ICON_COLOR = "blue"
DRONE_ICON = "plane"

HOME_ICON_COLOR = "gray"
HOME_ICON = "home"

SHOW_LEGEND = True
LEGEND_TEXT = (
    "🔴 Planned route  |  "
    "🟢 Actual route  |  "
    "🟠 Obstacles  |  "
    "🔵 Drone  |  "
    "⚪ Return home"
)


# ============================================================
# ⚠️ DO NOT EDIT: SAFE VALUE HELPER
# This protects the map if telemetry is missing or invalid.
# ============================================================

def _safe_float(value, default):
    try:
        return float(value)
    except Exception:
        return default


# ============================================================
# ⚠️ DO NOT EDIT: INTEGRATION CONTRACT
#
# This function name and input format must stay the same.
# gcs_app.py calls:
#
#   render_map_panel(data)
#
# The data dictionary comes from the AI Agent /live endpoint.
# ============================================================

def render_map_panel(data):
    st.subheader(MAP_TITLE)

    # --------------------------------------------------------
    # ⚠️ DO NOT EDIT: PAYLOAD PARSING
    # These keys must match the shared backend contract.
    # --------------------------------------------------------
    state = data.get("state", {})
    position = state.get("position", {})

    lat = _safe_float(position.get("lat"), 12.9716)
    lon = _safe_float(position.get("lon"), 77.5946)
    alt = _safe_float(position.get("alt"), 0.0)

    # --------------------------------------------------------
    # ⚠️ DO NOT EDIT: FALLBACK IMPORT HANDLING
    # If folium is not installed or map fails, show simple data.
    # --------------------------------------------------------
    try:
        import folium
        from streamlit_folium import st_folium
    except Exception as error:
        st.warning("Map library not available. Showing simple position view.")
        st.write(
            f"Latitude: {lat:.6f}  \n"
            f"Longitude: {lon:.6f}  \n"
            f"Altitude: {alt:.1f}m"
        )
        st.error(f"Map error: {error}")
        return

    # --------------------------------------------------------
    # ⚠️ DO NOT EDIT: ACTUAL ROUTE SESSION STORAGE
    #
    # Other parts of the app may depend on this key name.
    # Do not rename "actual_route" unless the whole team agrees.
    # --------------------------------------------------------
    if "actual_route" not in st.session_state:
        st.session_state.actual_route = []

    new_point = (lat, lon)

    if (
        not st.session_state.actual_route
        or st.session_state.actual_route[-1] != new_point
    ):
        st.session_state.actual_route.append(new_point)

    # Keep trail size reasonable
    if len(st.session_state.actual_route) > 500:
        st.session_state.actual_route = st.session_state.actual_route[-500:]

    # --------------------------------------------------------
    # 🎨 EDITABLE: MAP OBJECT
    # Person 2 can change map location, zoom, tiles, etc.
    # --------------------------------------------------------
    mission_map = folium.Map(
        location=[lat, lon],
        zoom_start=MAP_ZOOM,
        tiles=MAP_TILES,
    )

    # --------------------------------------------------------
    # 🎨 EDITABLE: PLANNED ROUTE STYLE
    # Person 2 can change colors, thickness, dash style.
    # --------------------------------------------------------
    folium.PolyLine(
        PLANNED_ROUTE,
        color=PLANNED_ROUTE_COLOR,
        weight=PLANNED_ROUTE_WEIGHT,
        dash_array=PLANNED_ROUTE_DASH,
        tooltip="Planned Route",
    ).add_to(mission_map)

    # --------------------------------------------------------
    # 🎨 EDITABLE: ACTUAL ROUTE STYLE
    # Person 2 can change colors and thickness.
    # --------------------------------------------------------
    folium.PolyLine(
        st.session_state.actual_route,
        color=ACTUAL_ROUTE_COLOR,
        weight=ACTUAL_ROUTE_WEIGHT,
        tooltip="Actual Route",
    ).add_to(mission_map)

    # --------------------------------------------------------
    # 🎨 EDITABLE: OBSTACLE STYLE
    # Person 2 can change obstacle colors, opacity, labels.
    # Do not remove obstacles completely unless demo requires it.
    # --------------------------------------------------------
    for obstacle in OBSTACLES:
        folium.Circle(
            location=[obstacle["lat"], obstacle["lon"]],
            radius=obstacle["radius"],
            color=OBSTACLE_COLOR,
            fill=True,
            fill_opacity=OBSTACLE_FILL_OPACITY,
            tooltip=obstacle["name"],
        ).add_to(mission_map)

    # --------------------------------------------------------
    # 🎨 EDITABLE: RETURN HOME MARKER
    # Person 2 can change icon/color or remove if too cluttered.
    # --------------------------------------------------------
    if RETURN_HOME:
        folium.Marker(
            location=[RETURN_HOME[0], RETURN_HOME[1]],
            tooltip="Return Home",
            icon=folium.Icon(
                color=HOME_ICON_COLOR,
                icon=HOME_ICON,
                prefix="fa",
            ),
        ).add_to(mission_map)

    # --------------------------------------------------------
    # 🎨 EDITABLE: DRONE MARKER
    # Person 2 can improve the drone marker.
    # Keep it clearly visible.
    # --------------------------------------------------------
    folium.Marker(
        location=[lat, lon],
        tooltip="Drone",
        icon=folium.Icon(
            color=DRONE_ICON_COLOR,
            icon=DRONE_ICON,
            prefix="fa",
        ),
    ).add_to(mission_map)

    # --------------------------------------------------------
    # 🎨 EDITABLE: MAP RENDER SETTINGS
    # Person 2 can adjust height and layout.
    # --------------------------------------------------------
    st_folium(
        mission_map,
        use_container_width=True,
        height=MAP_HEIGHT,
        key="mission_map",
    )

    # --------------------------------------------------------
    # 🎨 EDITABLE: LEGEND
    # Person 2 can improve this legend.
    # --------------------------------------------------------
    if SHOW_LEGEND:
        st.caption(LEGEND_TEXT)

    # --------------------------------------------------------
    # 🎨 EDITABLE: POSITION TEXT STYLE
    # Person 2 can make this nicer.
    # Keep the values readable.
    # --------------------------------------------------------
    st.write(
        f"Latitude: {lat:.6f}  \n"
        f"Longitude: {lon:.6f}  \n"
        f"Altitude: {alt:.1f}m"
    )

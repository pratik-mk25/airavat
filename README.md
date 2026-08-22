# AIRAVAT — Autonomous UAV Decision Platform & Ground Control Station (GCS)

A simulation-based platform, AI decision engine, and interactive Ground Control Station (GCS) for intelligent UAV mission management under dynamic physical conditions (battery, wind, obstacles, progress).

## Team & Contributors
- **Pratik** ([@pratik-mk25](https://github.com/pratik-mk25))
- **Darksider326** ([@Darksider326](https://github.com/Darksider326))
- **Shishir Deshmukh** ([@Shishir-Deshmukh966](https://github.com/Shishir-Deshmukh966))

---

## 📚 Table of Contents
1. [Core Capabilities](#core-capabilities)
2. [UI Architecture & Panel Breakdown](#ui-architecture--panel-breakdown)
3. [AIRAVAT Core Physics Engine](#airavat-core-physics-engine)
4. [Running Desktop Application (PySide6)](#running-desktop-application-pyside6)
5. [Running Web Dashboard (Streamlit)](#running-web-dashboard-streamlit)
6. [Project Directory Layout](#project-directory-layout)

---

## Core Capabilities
- **5-Action World Model**: Evaluates `Continue`, `Reroute`, `Hold`, `Return Early`, `Reprioritize Waypoint` in real-time.
- **Fault Injection Engine**: Real-time simulation of wind gusts, obstacle blockades, and battery drops.
- **Ground Control Station (GCS)**: PySide6 desktop tactical interface and Streamlit web dashboard.
- **Baseline vs AIRAVAT Mode**: Live comparative analysis against fixed mission plans.

---

## UI Architecture & Panel Breakdown

The user interface is divided into 5 primary regions:

### Top Header Bar (`ui/header_widget.py`)
- **Title**: `AIRAVAT | GROUND CONTROL STATION`
- **Status Badge**: `LIVE` (Green) or `REPLAY` (Orange)
- **Mode Badge**: `MODE: AIRAVAT` (Cyan) or `BASELINE` (Gray)
- **Risk Level Badge**: `RISK: LOW` (Green), `MEDIUM`, `HIGH`, `CRITICAL`

### Box 1 — Live Camera Feed (`ui/camera_panel.py`)
- HD FPV camera viewport with clean optical stream.
- **Top Cardinal Compass Tape**: Live cardinal directions (`N`, `NE`, `E`, `SE`, `S`, `SW`, `W`, `NW`) and heading tick angles.
- **Zoom Controls**: Top-right corner `ZOOM: [ − ] 1.0x [ + ]` interactive controls.

### Box 2 — Mission Map View (`ui/map_panel.py` & `assets/map_template.html`)
- Leaflet.js with CartoDB Dark Matter tactical map layer embedded via `QWebEngineView`.
- **Planned Route (Red Dotted Line)**, **AIRAVAT Route (Green Line)**, **Return-To-Launch RTL (Cyan Vector)**.
- **Inner Tactical Corner Aperture Brackets (`┌ ┐ └ ┘`)** matching camera viewport.
- **Outside Wind Speed Readout**: `💨 WIND: 4.2 m/s`.

### Box 3 — AI Decision Feed (`ui/ai_feed_panel.py`)
- **Recommended Action Card**: Displays `RECOMMENDED ACTION: CONTINUE`, `HOLD`, `AIRAVAT REROUTE`, or `RETURN EARLY`.
- **Confidence Score & Qwen World-Model Reasoning**: Physics explanation narrative and risk level chip.
- **Compact Live Log Stream**: Low-profile scrollable timeline recording real-time prediction events.

### Lower Panel — Telemetry Metrics & Sparkline Charts (`ui/telemetry_panel.py`)
- **Inline Readouts**: `SPEED: 12.8 m/s`, `ALTITUDE: 45.0 m`, `BATTERY: 78%`, `WIND SPEED: 8.0 m/s`, `OBSTACLE DIST: 120.0 m`, `PROGRESS: 42%`.
- **3 Live Line Charts**: Real-time 60 FPS animated line curves for **Battery Discharge (%)**, **Wind Speed (m/s)**, and **Altitude (m)**.

### Bottom Panel — Interactive Controls (`ui/control_panel.py`)
- Mission controls: `Start Mission / Pause`, `Reset`, `Inject Wind`, `Inject Obstacle`, `Low Battery Event`, and `Toggle Mode`.

---

## Running Desktop Application (PySide6)

### On Ubuntu Linux
```bash
cd D/team
chmod +x launch_ubuntu.sh
./launch_ubuntu.sh
```

### On Windows
```cmd
cd D:\team
python main.py
```

---

## Running Web Dashboard (Streamlit)

```bash
cd D:\team
streamlit run services/gcs_app.py
```

---

## Project Directory Layout

```
D:\team\
├── main.py                     # Desktop PySide6 application entry point
├── requirements.txt            # Python dependencies (PySide6, Streamlit, Folium)
├── launch_ubuntu.sh            # Shell execution script for Ubuntu Linux
├── README.md                   # Complete architectural guide
├── airavat_core/               # Core Engine & Physical AI Simulator
│   ├── simulation_engine.py    # 10Hz physics loop, telemetry signal emitter
│   ├── qwen_world_model.py     # Qwen Physical AI decision model
│   └── mission_planner.py      # Waypoints & dynamic spline route planner
├── services/                   # Streamlit Web Services & Panels
│   ├── gcs_app.py              # Streamlit GCS application (3-column layout)
│   ├── gcs_map.py              # Mission Map panel renderer (Person 2)
│   └── gcs_panels.py          # Telemetry, Qwen World Model, & Reactor Visual panels (Person 3)
└── ui/                         # PySide6 Desktop Tactical Panels
    ├── main_window.py          # Master layout orchestrator
    ├── header_widget.py        # Top bar status, mode, and risk badge
    ├── camera_panel.py         # Live Camera Viewport (ZOOM: [-] 1.0x [+]) & Top Compass (N,E,S,W)
    ├── map_panel.py            # Mission Map View with inner corner brackets
    ├── telemetry_panel.py      # Telemetry cards & 3 live line charts (Batt, Wind, Altitude)
    └── ai_feed_panel.py        # Qwen Physical AI feed & compact log stream
```

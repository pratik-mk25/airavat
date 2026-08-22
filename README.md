# AIRAVAT — Autonomous UAV Decision Platform

A simulation-based platform and AI decision engine for intelligent UAV mission management under dynamic conditions (battery, wind, obstacles, progress).

## Core Capabilities
- **5-Action World Model**: Evaluates `Continue`, `Reroute`, `Hold`, `Return Early`, `Reprioritize Waypoint` in real-time.
- **Fault Injection Engine**: Real-time simulation of wind gusts, obstacle blockades, and battery drops.
- **Ground Control Station (GCS)**: Streamlit interactive telemetry dashboard and control panel.
- **Baseline vs AIRAVAT Mode**: Live comparative analysis against fixed mission plans.

## Team & Contributors
- **Pratik** ([@pratik-mk25](https://github.com/pratik-mk25))
- **Darksider326** ([@Darksider326](https://github.com/Darksider326))
- **Shishir Deshmukh** ([@Shishir-Deshmukh966](https://github.com/Shishir-Deshmukh966))

## Quick Start

```bash
# 1. Install dependencies
uv venv && source .venv/bin/activate
uv pip install fastapi "uvicorn[standard]" requests pydantic streamlit pandas pytest httpx scikit-learn matplotlib

# 2. Run AI Agent Server (Port 8000)
python3 services/ai_agent.py

# 3. Run Telemetry Simulator Agent
python3 services/sim_agent.py

# 4. Launch Ground Control Station (Port 8501)
streamlit run services/gcs_app.py
```

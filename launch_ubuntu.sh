#!/usr/bin/env bash
# Launch script for AIRAVAT Ground Control Station (GCS) on Ubuntu / Linux

echo "=================================================================="
echo "  AIRAVAT Ground Control Station (GCS)"
echo "=================================================================="

# Check if python3 is available
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] python3 could not be found. Please install Python 3 on Ubuntu:"
    echo "  sudo apt update && sudo apt install -y python3 python3-pip python3-venv"
    exit 1
fi

# Ensure virtual environment exists
if [ ! -d "venv" ]; then
    echo "[INFO] Creating Python virtual environment (venv)..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "[INFO] Installing PySide6 and Streamlit dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Launch application
echo "[INFO] Launching AIRAVAT Ground Control Station Interface..."
python3 main.py

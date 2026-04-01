#!/bin/bash
# EmoTrack - Local Mac Testing Script
# Run this to test EmoTrack as a desktop-like app on macOS
#
# Usage: ./run_mac_local.sh
#
# This will:
# 1. Set up a Python virtual environment (if needed)
# 2. Install dependencies
# 3. Generate the ONNX model (if needed)
# 4. Launch EmoTrack in standalone mode

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "==============================="
echo " EmoTrack - Local Mac Setup"
echo "==============================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 is required. Install via: brew install python3"
    exit 1
fi

# Create venv if needed
if [ ! -d "venv" ]; then
    echo "[1/4] Creating virtual environment..."
    python3 -m venv venv
else
    echo "[1/4] Virtual environment exists."
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "[2/4] Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements-local.txt -q

# Generate ONNX model if needed
if [ ! -f "models/emotion_model.onnx" ]; then
    echo "[3/4] Generating emotion detection model..."
    pip install torch -q  # Needed for model creation
    python models/create_model.py
else
    echo "[3/4] Emotion model already exists."
fi

# Launch the app
echo "[4/4] Launching EmoTrack..."
echo ""
echo "==============================="
echo " EmoTrack is starting!"
echo " Open http://localhost:8501"
echo " Press Ctrl+C to stop"
echo "==============================="
echo ""

streamlit run EmoTrack.py \
    --server.port 8501 \
    --server.address localhost \
    --server.headless false \
    --browser.gatherUsageStats false

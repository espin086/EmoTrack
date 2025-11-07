#!/bin/bash

# EmoTrack Frontend Startup Script
# This script starts the Streamlit frontend locally

echo "🎨 Starting EmoTrack Frontend..."

# Set environment variables
export BACKEND_URL="http://localhost:8000"

# Navigate to frontend directory
cd frontend

# Start the Streamlit frontend
echo "Starting frontend on http://localhost:8501"
streamlit run app.py --server.port 8501 --server.address localhost


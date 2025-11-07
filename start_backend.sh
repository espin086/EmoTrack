#!/bin/bash

# EmoTrack Backend Startup Script
# This script starts the FastAPI backend locally

echo "🚀 Starting EmoTrack Backend..."

# Set environment variables
export DB_PATH="./data/emotions.db"

# Create data directory if it doesn't exist
mkdir -p ./data

# Check if AWS credentials are set
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "⚠️  Warning: AWS credentials not found in environment variables"
    echo "Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_DEFAULT_REGION"
    echo ""
    echo "You can set them by running:"
    echo "  export AWS_ACCESS_KEY_ID=your_access_key"
    echo "  export AWS_SECRET_ACCESS_KEY=your_secret_key"
    echo "  export AWS_DEFAULT_REGION=us-east-1"
    echo ""
    echo "Or AWS CLI will use credentials from ~/.aws/credentials"
    echo ""
fi

# Navigate to backend directory
cd backend

# Start the FastAPI backend
echo "Starting backend on http://localhost:8000"
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload


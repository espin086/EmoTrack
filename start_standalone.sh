#!/bin/bash

# EmoTrack Standalone Startup Script
# This script starts the standalone version (simpler, single process)

echo "🎭 Starting EmoTrack Standalone..."

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

# Start the Streamlit app
echo "Starting EmoTrack on http://localhost:8501"
streamlit run EmoTrack.py --server.port 8501 --server.address localhost


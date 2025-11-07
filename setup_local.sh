#!/bin/bash

# EmoTrack Local Setup Script
# This script sets up the local development environment

echo "🔧 Setting up EmoTrack for local development..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
echo "✓ Found Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements-local.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "Then you can start EmoTrack using one of these options:"
echo ""
echo "Option 1 - Standalone (simplest):"
echo "  ./start_standalone.sh"
echo ""
echo "Option 2 - Full stack (backend + frontend):"
echo "  Terminal 1: ./start_backend.sh"
echo "  Terminal 2: ./start_frontend.sh"
echo ""
echo "Note: Make sure AWS credentials are configured!"
echo "  Run 'aws configure' or set environment variables"
echo ""


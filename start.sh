#!/bin/bash

# Script to run the Bank Statement Consolidation Web App
# Run from project root: ./start.sh

echo "=========================================="
echo "🚀 Starting Bank Statement Consolidation Web App"
echo "=========================================="

# Get the directory where this script is located (project root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/web"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads
mkdir -p outputs

# Run the Flask app
echo ""
echo "🌐 Starting Flask server..."
echo "📍 The app will automatically find an available port (usually 5001)"
echo "📍 Check the output above for the exact URL to open in your browser"
echo "📍 Open http://localhost:5001 in your browser"
echo "=========================================="
echo ""

python3 app.py

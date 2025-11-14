#!/bin/bash

# Script to run the Bank Statement Consolidation Web App

echo "=========================================="
echo "🚀 Starting Bank Statement Consolidation Web App"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

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

# Also ensure parent directory dependencies are available
echo "📥 Installing HDFC dependencies..."
cd ../HDFC
if [ -d "venv" ] || [ -d "../finance_env" ]; then
    # Use existing venv if available
    echo "✅ Using existing HDFC environment"
else
    echo "⚠️  Note: HDFC processing requires dependencies in finance_env"
fi

cd ../AXIS
if [ -d "axis_env" ]; then
    echo "✅ Using existing AXIS environment"
else
    echo "⚠️  Note: AXIS processing requires dependencies in axis_env"
fi

cd "$SCRIPT_DIR"

# Create necessary directories
mkdir -p uploads
mkdir -p outputs

# Run the Flask app
echo ""
echo "🌐 Starting Flask server..."
echo "📍 The app will automatically find an available port (usually 5001)"
echo "📍 Check the output above for the exact URL to open in your browser"
echo "=========================================="
echo ""

python3 app.py


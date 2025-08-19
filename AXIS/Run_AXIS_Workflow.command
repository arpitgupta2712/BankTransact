#!/bin/bash

# AXIS Bank Complete Workflow Runner
# Double-click this file to run the entire workflow

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting AXIS Bank Complete Workflow..."
echo "Directory: $SCRIPT_DIR"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3 and try again."
    echo ""
    echo "Press Enter to exit..."
    read
    exit 1
fi

# Run the workflow script
echo "📋 Running complete workflow..."
python3 run_complete_workflow.py

# Check exit code and provide appropriate message
exit_code=$?
echo ""
if [ $exit_code -eq 0 ]; then
    echo "🏁 Workflow completed successfully!"
    echo "📁 Check your desktop for the organized output files."
else
    echo "❌ Workflow failed with exit code: $exit_code"
    echo "Please check the error messages above."
fi

echo "✅ Terminal will close automatically in 3 seconds..."
sleep 3

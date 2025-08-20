#!/bin/bash

# BankTransactApp - Build and Run Script
# This script builds the SwiftUI macOS app and opens it automatically

set -e  # Exit on any error

echo "🏦 BankTransactApp - Build and Run"
echo "=================================="

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Error: Xcode is not installed or not in PATH"
    echo "   Please install Xcode from the App Store"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "   Please install Python 3 from python.org"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Navigate to the app directory
APP_DIR="BankTransactApp"
if [ ! -d "$APP_DIR" ]; then
    echo "❌ Error: $APP_DIR directory not found"
    echo "   Make sure you're running this script from the BankTransact root directory"
    exit 1
fi

cd "$APP_DIR"

echo "🔨 Building BankTransactApp..."
echo "   This may take a few moments..."

# Build the app
if xcodebuild -project BankTransactApp.xcodeproj -scheme BankTransactApp -configuration Debug build; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    
    # Get the path to the built app
    APP_PATH="/Users/arpitgupta/Library/Developer/Xcode/DerivedData/BankTransactApp-*/Build/Products/Debug/BankTransactApp.app"
    
    # Find the actual app path (handle wildcards)
    ACTUAL_APP_PATH=$(ls -d $APP_PATH 2>/dev/null | head -1)
    
    if [ -n "$ACTUAL_APP_PATH" ] && [ -d "$ACTUAL_APP_PATH" ]; then
        echo "🚀 Opening BankTransactApp..."
        open "$ACTUAL_APP_PATH"
        echo "✅ App launched successfully!"
        echo ""
        echo "🎉 BankTransactApp is now running!"
        echo "   You can upload bank statements and process them using the Python scripts."
    else
        echo "❌ Error: Could not find the built app"
        echo "   Expected location: $APP_PATH"
        exit 1
    fi
else
    echo ""
    echo "❌ Build failed!"
    echo "   Please check the error messages above and fix any issues."
    exit 1
fi

echo ""
echo "📋 Usage:"
echo "   1. Select your bank (AXIS or HDFC)"
echo "   2. Click 'Choose Files' to upload bank statements"
echo "   3. Click 'Process Statements' to run the Python scripts"
echo "   4. View generated output files in the list"
echo ""
echo "🔄 To rebuild and run again, just run this script:"
echo "   ./scripts/build_and_run.sh"

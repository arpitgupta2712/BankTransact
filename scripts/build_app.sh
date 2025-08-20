#!/bin/bash

# Bank Transaction Processor - Build Script
# This script helps build and run the SwiftUI macOS app

echo "🏦 Bank Transaction Processor - Build Script"
echo "=============================================="

# Check if we're in the right directory
if [ ! -d "BankTransactApp" ]; then
    echo "❌ Error: BankTransactApp directory not found!"
    echo "Please run this script from the BankTransact root directory."
    exit 1
fi

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Error: Xcode not found!"
    echo "Please install Xcode from the App Store."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 not found!"
    echo "Please install Python 3 from python.org or using Homebrew."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Check if the Python scripts exist
if [ ! -f "AXIS/run_complete_workflow.py" ]; then
    echo "⚠️  Warning: AXIS script not found at AXIS/run_complete_workflow.py"
fi

if [ ! -f "HDFC/consolidate_statements.py" ]; then
    echo "⚠️  Warning: HDFC script not found at HDFC/consolidate_statements.py"
fi

echo ""
echo "🚀 Building the app..."

# Try to build the app
cd BankTransactApp

if xcodebuild -project BankTransactApp.xcodeproj -scheme BankTransactApp -configuration Debug build; then
    echo "✅ Build successful!"
    echo ""
    echo "🎉 The app has been built successfully!"
    echo ""
    echo "To run the app:"
    echo "1. Open BankTransactApp.xcodeproj in Xcode"
    echo "2. Press Cmd+R to build and run"
    echo "3. Or use: open BankTransactApp.xcodeproj"
    echo ""
    echo "📱 App Features:"
    echo "- Upload bank statement files (CSV for AXIS, Excel for HDFC)"
    echo "- Process statements using existing Python scripts"
    echo "- View and analyze generated output files"
    echo "- Modern macOS interface with real-time status updates"
else
    echo "❌ Build failed!"
    echo ""
    echo "💡 Troubleshooting:"
    echo "1. Make sure Xcode is properly installed"
    echo "2. Check that all Swift files are present in BankTransactApp/"
    echo "3. Try opening the project in Xcode for more detailed error messages"
    echo "4. Ensure you have the latest Xcode version"
fi

echo ""
echo "📚 For more information, see BankTransactApp/README.md"

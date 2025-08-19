@echo off
REM AXIS Bank Complete Workflow Runner for Windows
REM Double-click this file to run the entire workflow

echo 🚀 Starting AXIS Bank Complete Workflow...
echo Directory: %CD%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python and try again.
    echo.
    pause
    exit /b 1
)

REM Run the workflow script
echo 📋 Running complete workflow...
python run_complete_workflow.py

REM Check exit code and provide appropriate message
echo.
if %errorlevel% equ 0 (
    echo 🏁 Workflow completed successfully!
    echo 📁 Check your desktop for the organized output files.
) else (
    echo ❌ Workflow failed with exit code: %errorlevel%
    echo Please check the error messages above.
)

echo ✅ Terminal will close automatically in 3 seconds...
timeout /t 3 /nobreak >nul

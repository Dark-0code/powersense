@echo off
REM PowerSense Startup Script for Windows

echo.
echo ========================================
echo   PowerSense - AI Power Analysis System
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [1/3] Checking Python version...
python --version

REM Check if requirements are installed
echo.
echo [2/3] Installing/Updating dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Try running: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Start the Flask server
echo.
echo [3/3] Starting PowerSense Backend...
echo.
echo ========================================
echo   Server starting at http://localhost:5000
echo   Press Ctrl+C to stop
echo ========================================
echo.

python app.py

pause

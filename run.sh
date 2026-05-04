#!/bin/bash

# PowerSense Startup Script for macOS/Linux

echo ""
echo "========================================"
echo "  PowerSense - AI Power Analysis System"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from python.org or use:"
    echo "  macOS: brew install python3"
    echo "  Linux: sudo apt-get install python3 python3-pip"
    exit 1
fi

echo "[1/3] Checking Python version..."
python3 --version

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not installed"
    exit 1
fi

# Install/update dependencies
echo ""
echo "[2/3] Installing/Updating dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo "Try running: pip3 install -r requirements.txt"
    exit 1
fi

# Start the Flask server
echo ""
echo "[3/3] Starting PowerSense Backend..."
echo ""
echo "========================================"
echo "   Server starting at http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo "========================================"
echo ""

python3 app.py

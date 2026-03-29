#!/bin/bash
# NexGen Hospital - Start Script (Fixed for Render + Local)

set -e

echo ""
echo " ================================================"
echo "  NexGen Hospital Management System"
echo " ================================================"
echo ""

# -------------------------------
# Check Python
# -------------------------------
if ! command -v python3 &>/dev/null; then
    echo " [ERROR] Python 3 not found!"
    exit 1
fi

echo " [OK] $(python3 --version)"

# -------------------------------
# Create virtual environment
# -------------------------------
if [ ! -d "venv" ]; then
    echo " [SETUP] Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# -------------------------------
# Install dependencies
# -------------------------------
echo " [SETUP] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# -------------------------------
# Start Server
# -------------------------------
echo ""
echo " ================================================"
echo "  Starting NexGen API Server..."
echo " ================================================"
echo ""

# Render uses PORT env variable
PORT=${PORT:-10000}

uvicorn main:app --host 0.0.0.0 --port $PORT
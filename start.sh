#!/bin/bash
# NexGen Hospital - Mac/Linux start script

set -e
cd "$(dirname "$0")"

echo ""
echo " ================================================"
echo "  NexGen Hospital Management System"
echo " ================================================"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo " [ERROR] Python 3 not found!"
    echo " Mac:   brew install python"
    echo " Linux: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi
echo " [OK] $(python3 --version)"

# Create venv
if [ ! -d "backend/venv" ]; then
    echo " [SETUP] Creating virtual environment..."
    python3 -m venv backend/venv
fi

source backend/venv/bin/activate

echo " [SETUP] Installing dependencies..."
pip install -r backend/requirements.txt -q

echo ""
echo " ================================================"
echo " Make sure Neo4j Desktop is running first!"
echo " Neo4j password must be: nexgen123"
echo ""
echo " Once started, open: http://localhost:8000"
echo " Swagger API docs:   http://localhost:8000/docs"
echo " ================================================"
echo ""

cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# NexGen Hospital Management System

Full-stack hospital portal — Python (FastAPI) + Neo4j + AI predictions.
Three roles: Admin, Doctor, Patient — each with their own portal.

## Quick Start (3 steps)

### Step 1 — Install Python
Go to https://python.org/downloads and download Python 3.11 or later.
On Windows: check "Add Python to PATH" during install.

### Step 2 — Start Neo4j
1. Download Neo4j Desktop from https://neo4j.com/download
2. Create a new project, add a Local DBMS
3. Set password to exactly: nexgen123
4. Click Start — wait for green "Active" status

### Step 3 — Run the app

Windows: double-click start.bat

Mac/Linux:
  chmod +x start.sh
  ./start.sh

Then open: http://localhost:8000

## Demo Logins

Admin   → admin / admin123
Doctor  → dr.aditi / doctor123
Patient → meera.g / patient123

## API Docs

Swagger UI: http://localhost:8000/docs

## AI Predictions (extend this!)

Edit backend/ai/predictor.py to add real ML models.
Current endpoints:
  GET  /api/ai/readmission-risk/{patient}
  GET  /api/ai/length-of-stay/{patient}
  GET  /api/ai/vitals-alert/{patient}
  POST /api/ai/suggest-diagnosis

from fastapi import APIRouter
from ai.predictor import (
    predict_disease,
    risk_score,
    predict_icu,
    predict_appointments
)

router = APIRouter(prefix="/api/ai", tags=["AI"])

# ================= DISEASE =================
@router.post("/disease")
def disease(data: dict):
    result = predict_disease(
        data["age"],
        data["bp"],
        data["sugar"],
        data["heart_rate"],
        data["spo2"]
    )
    return {"success": True, "disease": result}


# ================= RISK =================
@router.post("/risk")
def risk(data: dict):
    result = risk_score(
        data["age"],
        data["bp"],
        data["sugar"],
        data["heart_rate"],
        data["spo2"]
    )
    return {"success": True, "risk": result}


# ================= ICU =================
@router.post("/icu")
def icu(data: dict):
    result = predict_icu(
        data["age"],
        data["bp"],
        data["sugar"],
        data["heart_rate"],
        data["spo2"]
    )
    return {"success": True, "icu": result}


# ================= APPOINTMENT AI =================
@router.get("/prediction")
def prediction(month: int = 1):
    result = predict_appointments(month)
    return {"success": True, "data": result}


from fastapi import APIRouter, Depends, HTTPException
from core.security import patient_only
from core.database import db
from models.schemas import APIResponse

router = APIRouter(prefix="/api/patient", tags=["Patient"])

@router.get("/dashboard")
def dashboard(user=Depends(patient_only)):
    profile = db.run_one("MATCH (p:Patient {username:$u}) RETURN p", u=user["username"])
    appointments = db.run("""
        MATCH (a:Appointment {patient_username:$u})
        RETURN a ORDER BY a.appointment_date DESC, a.appointment_time DESC
    """, u=user["username"])
    records = db.run("""
        MATCH (r:MedicalRecord {patient_username:$u})
        RETURN r ORDER BY r.record_date DESC
    """, u=user["username"])

    return APIResponse.ok(data={
        "profile":      profile["p"] if profile else None,
        "appointments": [r["a"] for r in appointments],
        "records":      [r["r"] for r in records],
    })

@router.get("/profile")
def my_profile(user=Depends(patient_only)):
    row = db.run_one("MATCH (p:Patient {username:$u}) RETURN p", u=user["username"])
    if not row:
        raise HTTPException(404, "Profile not found")
    return APIResponse.ok(data=row["p"])

@router.get("/appointments")
def my_appointments(user=Depends(patient_only)):
    rows = db.run("""
        MATCH (a:Appointment {patient_username:$u})
        RETURN a ORDER BY a.appointment_date DESC, a.appointment_time DESC
    """, u=user["username"])
    return APIResponse.ok(data=[r["a"] for r in rows])

@router.get("/records")
def my_records(user=Depends(patient_only)):
    rows = db.run("""
        MATCH (r:MedicalRecord {patient_username:$u})
        RETURN r ORDER BY r.record_date DESC
    """, u=user["username"])
    return APIResponse.ok(data=[r["r"] for r in rows])

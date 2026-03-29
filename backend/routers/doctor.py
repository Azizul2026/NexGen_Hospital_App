from fastapi import APIRouter, Depends, HTTPException
from core.security import doctor_only, get_current_user
from core.database import db
from models.schemas import APIResponse, AppointmentUpdate, RecordCreate, DoctorUpdate
from datetime import date

router = APIRouter(prefix="/api/doctor", tags=["Doctor"])

@router.get("/profile")
def my_profile(user=Depends(doctor_only)):
    row = db.run_one("MATCH (d:Doctor {username:$u}) RETURN d", u=user["username"])
    if not row:
        raise HTTPException(404, "Doctor profile not found")
    return APIResponse.ok(data=row["d"])

@router.put("/profile")
def update_profile(body: DoctorUpdate, user=Depends(doctor_only)):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if updates:
        set_clause = ", ".join(f"d.{k} = ${k}" for k in updates)
        db.run(f"MATCH (d:Doctor {{username:$u}}) SET {set_clause}", u=user["username"], **updates)
    row = db.run_one("MATCH (d:Doctor {username:$u}) RETURN d", u=user["username"])
    return APIResponse.ok(message="Profile updated", data=row["d"])

# ── My patients ───────────────────────────────────────────
@router.get("/patients")
def my_patients(user=Depends(doctor_only)):
    rows = db.run("""
        MATCH (p:Patient {assigned_doctor_username:$u})
        WHERE p.status IN ['ADMITTED','CRITICAL','OUTPATIENT']
        RETURN p ORDER BY p.full_name
    """, u=user["username"])
    return APIResponse.ok(data=[r["p"] for r in rows])

@router.get("/patients/{username}")
def get_patient(username: str, user=Depends(doctor_only)):
    row = db.run_one("MATCH (p:Patient {username:$u}) RETURN p", u=username)
    if not row:
        raise HTTPException(404, "Patient not found")
    p = row["p"]
    # Doctors can only see their own patients
    if user["role"] == "DOCTOR" and p.get("assigned_doctor_username") != user["username"]:
        raise HTTPException(403, "This patient is not assigned to you")
    return APIResponse.ok(data=p)

# ── Appointments ──────────────────────────────────────────
@router.get("/appointments")
def my_appointments(user=Depends(doctor_only)):
    rows = db.run("""
        MATCH (a:Appointment {doctor_username:$u})
        RETURN a ORDER BY a.appointment_date DESC, a.appointment_time
    """, u=user["username"])
    return APIResponse.ok(data=[r["a"] for r in rows])

@router.get("/appointments/today")
def today_appointments(user=Depends(doctor_only)):
    today = str(date.today())
    rows = db.run("""
        MATCH (a:Appointment {doctor_username:$u, appointment_date:$d})
        RETURN a ORDER BY a.appointment_time
    """, u=user["username"], d=today)
    return APIResponse.ok(data=[r["a"] for r in rows])

@router.patch("/appointments/{appt_id}/complete")
def complete_appointment(appt_id: str, body: AppointmentUpdate, user=Depends(doctor_only)):
    db.run("""
        MATCH (a:Appointment {appointment_id:$aid})
        SET a.status='COMPLETED',
            a.notes=$notes,
            a.prescription=$rx
    """, aid=appt_id, notes=body.notes or "", rx=body.prescription or "")
    row = db.run_one("MATCH (a:Appointment {appointment_id:$aid}) RETURN a", aid=appt_id)
    return APIResponse.ok(message="Appointment completed", data=row["a"])

@router.patch("/appointments/{appt_id}/cancel")
def cancel_appointment(appt_id: str, user=Depends(doctor_only)):
    db.run("MATCH (a:Appointment {appointment_id:$aid}) SET a.status='CANCELLED'", aid=appt_id)
    row = db.run_one("MATCH (a:Appointment {appointment_id:$aid}) RETURN a", aid=appt_id)
    return APIResponse.ok(message="Appointment cancelled", data=row["a"])

# ── Medical Records ───────────────────────────────────────
@router.get("/records/{patient_username}")
def get_patient_records(patient_username: str, user=Depends(doctor_only)):
    rows = db.run("""
        MATCH (r:MedicalRecord {patient_username:$pu, doctor_username:$du})
        RETURN r ORDER BY r.record_date DESC
    """, pu=patient_username, du=user["username"])
    return APIResponse.ok(data=[r["r"] for r in rows])

@router.post("/records")
def create_record(body: RecordCreate, user=Depends(doctor_only)):
    today = str(date.today())
    doc = db.run_one("MATCH (d:Doctor {username:$u}) RETURN d.full_name AS n", u=user["username"])
    doc_name = doc["n"] if doc else user["username"]
    rid = f"REC-{int(date.today().strftime('%Y%m%d%H%M%S')[-8:])}"

    db.run("""
        CREATE (r:MedicalRecord {
            record_id:$rid,
            patient_username:$pu,
            doctor_username:$du, doctor_name:$dn,
            record_date:$rd, visit_type:$vt,
            chief_complaint:$cc, diagnosis:$diag,
            symptoms:$sym, examination:$exam,
            prescription:$rx, lab_tests:$lt,
            lab_results:$lr, vitals:$vitals,
            next_visit_date:$nvd, notes:$notes,
            created_at:$today
        })
    """,
        rid=rid, pu=body.patient_username,
        du=user["username"], dn=doc_name,
        rd=body.record_date or today,
        vt=body.visit_type or "OPD",
        cc=body.chief_complaint or "", diag=body.diagnosis or "",
        sym=body.symptoms or "", exam=body.examination or "",
        rx=body.prescription or "", lt=body.lab_tests or "",
        lr=body.lab_results or "", vitals=body.vitals or "{}",
        nvd=body.next_visit_date or "", notes=body.notes or "",
        today=today
    )
    row = db.run_one("MATCH (r:MedicalRecord {record_id:$rid}) RETURN r", rid=rid)
    return APIResponse.ok(message="Record created", data=row["r"])

@router.delete("/records/{record_id}")
def delete_record(record_id: str, user=Depends(doctor_only)):
    db.run("MATCH (r:MedicalRecord {record_id:$rid}) DELETE r", rid=record_id)
    return APIResponse.ok(message="Record deleted")

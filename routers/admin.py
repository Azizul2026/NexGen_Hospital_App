from fastapi import APIRouter, Depends, HTTPException
from core.security import admin_only, hash_password
from core.database import db
from models.schemas import (
    APIResponse, PatientCreate, PatientUpdate,
    DoctorCreate, DoctorUpdate,
    AppointmentCreate, AppointmentUpdate
)
from datetime import date
import uuid

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# ── Dashboard ─────────────────────────────────────────────
@router.get("/dashboard")
def dashboard(user=Depends(admin_only)):
    total_patients  = db.run_one("MATCH (p:Patient) RETURN count(p) AS c")["c"]
    active_patients = db.run_one("MATCH (p:Patient) WHERE p.status IN ['ADMITTED','CRITICAL'] RETURN count(p) AS c")["c"]
    total_doctors   = db.run_one("MATCH (d:Doctor {active:true}) RETURN count(d) AS c")["c"]
    upcoming_appts  = db.run_one("MATCH (a:Appointment {status:'SCHEDULED'}) RETURN count(a) AS c")["c"]
    recent_patients = db.run("MATCH (p:Patient) WHERE p.status IN ['ADMITTED','CRITICAL'] RETURN p ORDER BY p.created_at DESC LIMIT 5")
    upcoming_list   = db.run("MATCH (a:Appointment {status:'SCHEDULED'}) RETURN a ORDER BY a.appointment_date, a.appointment_time LIMIT 10")

    return APIResponse.ok(data={
        "total_patients":    total_patients,
        "active_patients":   active_patients,
        "total_doctors":     total_doctors,
        "upcoming_appointments": upcoming_appts,
        "recent_patients":   [r["p"] for r in recent_patients],
        "upcoming_list":     [r["a"] for r in upcoming_list],
    })

# ── Patients ──────────────────────────────────────────────
@router.get("/patients")
def get_all_patients(user=Depends(admin_only)):
    rows = db.run("MATCH (p:Patient) RETURN p ORDER BY p.created_at DESC")
    return APIResponse.ok(data=[r["p"] for r in rows])

@router.get("/patients/search")
def search_patients(q: str, user=Depends(admin_only)):
    rows = db.run("""
        MATCH (p:Patient)
        WHERE toLower(p.full_name) CONTAINS toLower($q)
           OR p.patient_id CONTAINS $q
           OR p.username CONTAINS $q
        RETURN p LIMIT 30
    """, q=q)
    return APIResponse.ok(data=[r["p"] for r in rows])

@router.get("/patients/{username}")
def get_patient(username: str, user=Depends(admin_only)):
    row = db.run_one("MATCH (p:Patient {username:$u}) RETURN p", u=username)
    if not row:
        raise HTTPException(404, "Patient not found")
    return APIResponse.ok(data=row["p"])

@router.post("/patients")
def admit_patient(body: PatientCreate, user=Depends(admin_only)):
    if db.run_one("MATCH (u:User {username:$u}) RETURN u", u=body.username):
        raise HTTPException(400, f"Username '{body.username}' already taken")

    today = str(date.today())
    pid = f"P-{int(date.today().strftime('%Y%m%d%H%M%S')[-6:])}"

    db.run("""
        CREATE (u:User {
            username:$uname, password:$pw, email:$email,
            role:'PATIENT', active:true, created_at:$today
        })
        CREATE (p:Patient {
            patient_id:$pid, username:$uname,
            full_name:$name, gender:$gender,
            date_of_birth:$dob, blood_group:$blood,
            phone:$phone, email:$email, address:$addr,
            emergency_contact:$emerg,
            insurance_provider:$ins, insurance_number:$ins_num,
            ward:$ward, bed_number:$bed,
            admission_date:$adm, diagnosis:$diag,
            status:$status,
            assigned_doctor_username:$doc,
            notes:$notes, created_at:$today
        })
    """,
        uname=body.username, pw=hash_password(body.password),
        email=body.email or "", pid=pid,
        name=body.full_name, gender=body.gender or "",
        dob=body.date_of_birth or "", blood=body.blood_group or "",
        phone=body.phone, addr=body.address or "",
        emerg=body.emergency_contact or "",
        ins=body.insurance_provider or "", ins_num=body.insurance_number or "",
        ward=body.ward or "", bed=body.bed_number or "",
        adm=body.admission_date or today,
        diag=body.diagnosis or "", status=body.status or "ADMITTED",
        doc=body.assigned_doctor_username or "",
        notes=body.notes or "", today=today
    )

    new_patient = db.run_one("MATCH (p:Patient {username:$u}) RETURN p", u=body.username)
    return APIResponse.ok(message="Patient admitted successfully", data=new_patient["p"])

@router.put("/patients/{username}")
def update_patient(username: str, body: PatientUpdate, user=Depends(admin_only)):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(400, "No fields to update")
    set_clause = ", ".join(f"p.{k} = ${k}" for k in updates)
    db.run(f"MATCH (p:Patient {{username:$u}}) SET {set_clause}", u=username, **updates)
    row = db.run_one("MATCH (p:Patient {username:$u}) RETURN p", u=username)
    return APIResponse.ok(message="Patient updated", data=row["p"] if row else None)

@router.patch("/patients/{username}/assign-doctor")
def assign_doctor(username: str, doctor_username: str, user=Depends(admin_only)):
    db.run("MATCH (p:Patient {username:$u}) SET p.assigned_doctor_username=$doc", u=username, doc=doctor_username)
    row = db.run_one("MATCH (p:Patient {username:$u}) RETURN p", u=username)
    return APIResponse.ok(message="Doctor assigned", data=row["p"])

@router.patch("/patients/{username}/discharge")
def discharge_patient(username: str, user=Depends(admin_only)):
    today = str(date.today())
    db.run("MATCH (p:Patient {username:$u}) SET p.status='DISCHARGED', p.discharge_date=$d", u=username, d=today)
    row = db.run_one("MATCH (p:Patient {username:$u}) RETURN p", u=username)
    return APIResponse.ok(message="Patient discharged", data=row["p"])

# ── Doctors ───────────────────────────────────────────────
@router.get("/doctors")
def get_all_doctors(user=Depends(admin_only)):
    rows = db.run("MATCH (d:Doctor {active:true}) RETURN d ORDER BY d.full_name")
    return APIResponse.ok(data=[r["d"] for r in rows])

@router.get("/doctors/{username}")
def get_doctor(username: str, user=Depends(admin_only)):
    row = db.run_one("MATCH (d:Doctor {username:$u}) RETURN d", u=username)
    if not row:
        raise HTTPException(404, "Doctor not found")
    return APIResponse.ok(data=row["d"])

@router.post("/doctors")
def create_doctor(body: DoctorCreate, user=Depends(admin_only)):
    if db.run_one("MATCH (u:User {username:$u}) RETURN u", u=body.username):
        raise HTTPException(400, f"Username '{body.username}' already taken")
    today = str(date.today())
    db.run("""
        CREATE (u:User {
            username:$uname, password:$pw, email:$email,
            role:'DOCTOR', active:true, created_at:$today
        })
        CREATE (d:Doctor {
            username:$uname, full_name:$name,
            specialization:$spec, department:$dept,
            qualification:$qual, license_number:$lic,
            phone:$phone, email:$email,
            available_days:$days,
            consultation_fee:$fee, years_of_experience:$exp,
            active:true, created_at:$today
        })
    """,
        uname=body.username, pw=hash_password(body.password),
        email=body.email or "", name=body.full_name,
        spec=body.specialization, dept=body.department,
        qual=body.qualification or "", lic=body.license_number or "",
        phone=body.phone or "", days=body.available_days or "MON,TUE,WED,THU,FRI",
        fee=body.consultation_fee or 0.0, exp=body.years_of_experience or 0,
        today=today
    )
    row = db.run_one("MATCH (d:Doctor {username:$u}) RETURN d", u=body.username)
    return APIResponse.ok(message="Doctor created", data=row["d"])

@router.put("/doctors/{username}")
def update_doctor(username: str, body: DoctorUpdate, user=Depends(admin_only)):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(400, "No fields to update")
    set_clause = ", ".join(f"d.{k} = ${k}" for k in updates)
    db.run(f"MATCH (d:Doctor {{username:$u}}) SET {set_clause}", u=username, **updates)
    row = db.run_one("MATCH (d:Doctor {username:$u}) RETURN d", u=username)
    return APIResponse.ok(message="Doctor updated", data=row["d"])

@router.delete("/doctors/{username}")
def deactivate_doctor(username: str, user=Depends(admin_only)):
    db.run("MATCH (d:Doctor {username:$u}) SET d.active=false", u=username)
    db.run("MATCH (u:User {username:$u}) SET u.active=false", u=username)
    return APIResponse.ok(message="Doctor deactivated")

# ── Appointments ──────────────────────────────────────────
@router.get("/appointments")
def get_appointments(user=Depends(admin_only)):
    rows = db.run("MATCH (a:Appointment) RETURN a ORDER BY a.appointment_date DESC, a.appointment_time")
    return APIResponse.ok(data=[r["a"] for r in rows])

@router.get("/appointments/date/{appt_date}")
def get_by_date(appt_date: str, user=Depends(admin_only)):
    rows = db.run("MATCH (a:Appointment {appointment_date:$d}) RETURN a ORDER BY a.appointment_time", d=appt_date)
    return APIResponse.ok(data=[r["a"] for r in rows])

@router.post("/appointments")
def create_appointment(body: AppointmentCreate, current_user=Depends(admin_only)):
    today = str(date.today())
    aid = f"APT-{int(date.today().strftime('%Y%m%d%H%M%S')[-8:])}"
    db.run("""
        CREATE (a:Appointment {
            appointment_id:$aid,
            patient_username:$pu, patient_name:$pn,
            doctor_username:$du, doctor_name:$dn,
            department:$dept,
            appointment_date:$adate, appointment_time:$atime,
            type:$typ, status:'SCHEDULED',
            reason:$reason, notes:$notes,
            created_by:$cb, created_at:$today
        })
    """,
        aid=aid, pu=body.patient_username, pn=body.patient_name,
        du=body.doctor_username, dn=body.doctor_name,
        dept=body.department, adate=body.appointment_date,
        atime=body.appointment_time, typ=body.type or "NEW_CONSULTATION",
        reason=body.reason or "", notes=body.notes or "",
        cb=current_user["username"], today=today
    )
    row = db.run_one("MATCH (a:Appointment {appointment_id:$aid}) RETURN a", aid=aid)
    return APIResponse.ok(message="Appointment created", data=row["a"])

@router.put("/appointments/{appt_id}")
def update_appointment(appt_id: str, body: AppointmentUpdate, user=Depends(admin_only)):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(400, "Nothing to update")
    set_clause = ", ".join(f"a.{k} = ${k}" for k in updates)
    db.run(f"MATCH (a:Appointment {{appointment_id:$aid}}) SET {set_clause}", aid=appt_id, **updates)
    row = db.run_one("MATCH (a:Appointment {appointment_id:$aid}) RETURN a", aid=appt_id)
    return APIResponse.ok(message="Appointment updated", data=row["a"])

@router.delete("/appointments/{appt_id}")
def delete_appointment(appt_id: str, user=Depends(admin_only)):
    db.run("MATCH (a:Appointment {appointment_id:$aid}) DELETE a", aid=appt_id)
    return APIResponse.ok(message="Appointment deleted")

# ── Medical Records ───────────────────────────────────────
@router.get("/records/patient/{username}")
def get_patient_records(username: str, user=Depends(admin_only)):
    rows = db.run("MATCH (r:MedicalRecord {patient_username:$u}) RETURN r ORDER BY r.record_date DESC", u=username)
    return APIResponse.ok(data=[r["r"] for r in rows])

@router.get("/records")
def get_all_records(user=Depends(admin_only)):
    rows = db.run("MATCH (r:MedicalRecord) RETURN r ORDER BY r.record_date DESC")
    return APIResponse.ok(data=[r["r"] for r in rows])

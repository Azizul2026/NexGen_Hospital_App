from fastapi import APIRouter, Depends, HTTPException
from core.security import admin_only, hash_password
from core.database import db
from models.schemas import (
    APIResponse, PatientCreate, DoctorCreate,
    AppointmentCreate, UserCreate
)
from datetime import date

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# =========================================================
# 🔥 CREATE USER (FIXED WITH SCHEMA)
# =========================================================
@router.post("/create-user")
def create_user(body: UserCreate, user=Depends(admin_only)):

    # check existing
    if db.run_one("MATCH (u:User {username:$u}) RETURN u", u=body.username):
        raise HTTPException(400, "Username already exists")

    db.run("""
    CREATE (u:User {
        username:$username,
        password:$password,
        role:$role,
        active:true,
        created_at:$today
    })
    """,
    username=body.username,
    password=hash_password(body.password),
    role=body.role.upper(),
    today=str(date.today())
    )

    return APIResponse.ok(message=f"{body.role} created successfully")


# =========================================================
# 📊 DASHBOARD
# =========================================================
@router.get("/dashboard")
def dashboard(user=Depends(admin_only)):

    total_patients = db.run_one("MATCH (p:Patient) RETURN count(p) AS c")["c"]
    total_doctors = db.run_one("MATCH (d:Doctor {active:true}) RETURN count(d) AS c")["c"]

    return APIResponse.ok(data={
        "total_patients": total_patients,
        "total_doctors": total_doctors
    })


# =========================================================
# 🧑 PATIENTS
# =========================================================
@router.get("/patients")
def get_all_patients(user=Depends(admin_only)):
    rows = db.run("MATCH (p:Patient) RETURN p ORDER BY p.created_at DESC")
    return APIResponse.ok(data=[r["p"] for r in rows])


@router.post("/patients")
def admit_patient(body: PatientCreate, user=Depends(admin_only)):

    if db.run_one("MATCH (u:User {username:$u}) RETURN u", u=body.username):
        raise HTTPException(400, "Username already exists")

    today = str(date.today())

    db.run("""
    CREATE (u:User {
        username:$username,
        password:$password,
        role:'PATIENT',
        active:true,
        created_at:$today
    })
    CREATE (p:Patient {
        username:$username,
        full_name:$name,
        phone:$phone,
        status:'ADMITTED',
        created_at:$today
    })
    """,
    username=body.username,
    password=hash_password(body.password),
    name=body.full_name,
    phone=body.phone,
    today=today
    )

    return APIResponse.ok(message="Patient created successfully")


# =========================================================
# 👨‍⚕️ DOCTORS
# =========================================================
@router.get("/doctors")
def get_all_doctors(user=Depends(admin_only)):
    rows = db.run("MATCH (d:Doctor {active:true}) RETURN d")
    return APIResponse.ok(data=[r["d"] for r in rows])


@router.post("/doctors")
def create_doctor(body: DoctorCreate, user=Depends(admin_only)):

    if db.run_one("MATCH (u:User {username:$u}) RETURN u", u=body.username):
        raise HTTPException(400, "Username already exists")

    today = str(date.today())

    db.run("""
    CREATE (u:User {
        username:$username,
        password:$password,
        role:'DOCTOR',
        active:true,
        created_at:$today
    })
    CREATE (d:Doctor {
        username:$username,
        full_name:$name,
        specialization:$spec,
        active:true,
        created_at:$today
    })
    """,
    username=body.username,
    password=hash_password(body.password),
    name=body.full_name,
    spec=body.specialization,
    today=today
    )

    return APIResponse.ok(message="Doctor created successfully")


# =========================================================
# 📅 APPOINTMENTS
# =========================================================
@router.get("/appointments")
def get_appointments(user=Depends(admin_only)):
    rows = db.run("MATCH (a:Appointment) RETURN a")
    return APIResponse.ok(data=[r["a"] for r in rows])


@router.post("/appointments")
def create_appointment(body: AppointmentCreate, user=Depends(admin_only)):

    today = str(date.today())

    db.run("""
    CREATE (a:Appointment {
        patient_username:$pu,
        doctor_username:$du,
        appointment_date:$date,
        appointment_time:$time,
        status:'SCHEDULED',
        created_at:$today
    })
    """,
    pu=body.patient_username,
    du=body.doctor_username,
    date=body.appointment_date,
    time=body.appointment_time,
    today=today
    )

    return APIResponse.ok(message="Appointment created successfully")


# =========================================================
# 🗑 DELETE USER (FIXED SAFE DELETE)
# =========================================================
@router.delete("/user/{username}")
def delete_user(username: str, user=Depends(admin_only)):

    db.run("MATCH (u:User {username:$u}) DETACH DELETE u", u=username)

    return APIResponse.ok(message="User deleted successfully")


# =========================================================
# ✏️ UPDATE USER (SAFE)
# =========================================================
@router.put("/user/{username}")
def update_user(username: str, data: dict, user=Depends(admin_only)):

    updates = {k: v for k, v in data.items() if v is not None}

    if not updates:
        raise HTTPException(400, "No data provided")

    # 🔥 hash password if updated
    if "password" in updates:
        updates["password"] = hash_password(updates["password"])

    set_clause = ", ".join([f"u.{k} = ${k}" for k in updates])

    db.run(f"""
    MATCH (u:User {{username:$username}})
    SET {set_clause}
    """, username=username, **updates)

    return APIResponse.ok(message="User updated successfully")

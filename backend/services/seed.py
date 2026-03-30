from core.database import db
from core.security import hash_password
from datetime import date
import logging

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# 🚀 MAIN SEED FUNCTION
# ─────────────────────────────────────────────
def seed_all():
    """Create demo data if DB is empty"""

existing = db.run_one("MATCH (u:User) RETURN u LIMIT 1")
    if existing:
        logger.info("📦 Seed data already exists — skipping")
        return

    logger.info("🌱 Seeding database...")

    _seed_admin()
    _seed_doctors()
    _seed_patients()
    _seed_appointments()
    _seed_records()

    logger.info("✅ Demo data loaded!")
    logger.info("🔑 LOGIN CREDENTIALS:")
    logger.info(" Admin   → admin / admin123")
    logger.info(" Doctor  → dr.aditi / doctor123")
    logger.info(" Patient → meera.g / patient123")


# ─────────────────────────────────────────────
# 👑 ADMIN
# ─────────────────────────────────────────────
def _seed_admin():
    today = str(date.today())

    db.run("""
    CREATE (u:User {
        username: 'admin',
        password: $pw,
        email: 'admin@nexgen.com',
        role: 'ADMIN',
        active: true,
        created_at: $today
    })
    """, pw=hash_password("admin123"), today=today)


# ─────────────────────────────────────────────
# 👨‍⚕️ DOCTORS
# ─────────────────────────────────────────────
DOCTORS = [
    ("dr.aditi", "Dr. Aditi Roy", "Cardiology", 1200, 12),
    ("dr.karan", "Dr. Karan Mehta", "Orthopaedics", 1000, 9),
    ("dr.rohan", "Dr. Rohan Bose", "Neurology", 1500, 15),
    ("dr.lata", "Dr. Lata Rao", "Paediatrics", 800, 8),
    ("dr.priya", "Dr. Priya Nair", "General Medicine", 600, 6),
]


def _seed_doctors():
    today = str(date.today())

    for uname, name, dept, fee, exp in DOCTORS:
        db.run("""
        CREATE (u:User {
            username: $uname,
            password: $pw,
            email: $email,
            role: 'DOCTOR',
            active: true,
            created_at: $today
        })

        CREATE (d:Doctor {
            username: $uname,
            full_name: $name,
            specialization: $dept,
            department: $dept,
            consultation_fee: $fee,
            years_of_experience: $exp,
            active: true,
            created_at: $today
        })
        """,
        uname=uname,
        pw=hash_password("doctor123"),
        email=f"{uname}@nexgen.com",
        name=name,
        dept=dept,
        fee=fee,
        exp=exp,
        today=today
        )


# ─────────────────────────────────────────────
# 🧑‍ بیمار PATIENTS
# ─────────────────────────────────────────────
PATIENTS = [
    ("meera.g", "Meera Gupta", "F", "dr.aditi", "ADMITTED"),
    ("rahul.k", "Rahul Khanna", "M", "dr.rohan", "CRITICAL"),
    ("suresh.p", "Suresh Patel", "M", "dr.karan", "ADMITTED"),
    ("anjali.d", "Anjali Das", "F", "dr.rohan", "ADMITTED"),
]


def _seed_patients():
    today = str(date.today())

    for i, (uname, name, gender, doctor, status) in enumerate(PATIENTS):
        pid = f"P-{1001 + i}"

        db.run("""
        CREATE (u:User {
            username: $uname,
            password: $pw,
            email: $email,
            role: 'PATIENT',
            active: true,
            created_at: $today
        })

        CREATE (p:Patient {
            patient_id: $pid,
            username: $uname,
            full_name: $name,
            gender: $gender,
            phone: '+91 9000000000',
            diagnosis: 'General Checkup',
            assigned_doctor_username: $doc,
            status: $status,
            admission_date: $today,
            created_at: $today
        })
        """,
        uname=uname,
        pw=hash_password("patient123"),
        email=f"{uname}@mail.com",
        pid=pid,
        name=name,
        gender=gender,
        doc=doctor,
        status=status,
        today=today
        )


# ─────────────────────────────────────────────
# 📅 APPOINTMENTS
# ─────────────────────────────────────────────
def _seed_appointments():
    today = str(date.today())

    db.run("""
    CREATE (a:Appointment {
        appointment_id: 'APT-1001',
        patient_username: 'meera.g',
        patient_name: 'Meera Gupta',
        doctor_username: 'dr.aditi',
        doctor_name: 'Dr. Aditi Roy',
        department: 'Cardiology',
        appointment_date: $today,
        appointment_time: '09:30',
        status: 'SCHEDULED',
        created_by: 'admin',
        created_at: $today
    })
    """, today=today)


# ─────────────────────────────────────────────
# 📋 MEDICAL RECORDS
# ─────────────────────────────────────────────
def _seed_records():
    today = str(date.today())

    db.run("""
    CREATE (r:MedicalRecord {
        record_id: 'REC-1001',
        patient_username: 'meera.g',
        doctor_username: 'dr.aditi',
        diagnosis: 'Stable Angina',
        prescription: 'Aspirin',
        record_date: $today,
        created_at: $today
    })
    """, today=today)

from core.database import db
from core.security import hash_password
from datetime import date
import logging

logger = logging.getLogger(__name__)

def seed_all():
    """Create demo data if the database is empty."""
    existing = db.run_one("MATCH (u:User {username:'admin'}) RETURN u")
    if existing:
        logger.info("📦 Seed data already exists — skipping")
        return

    logger.info("🌱 Seeding demo data...")
    _seed_admin()
    _seed_doctors()
    _seed_patients()
    _seed_appointments()
    _seed_records()
    logger.info("✅ Demo data loaded!")
    logger.info("   Admin    → admin / admin123")
    logger.info("   Doctor   → dr.aditi / doctor123")
    logger.info("   Patient  → meera.g / patient123")

# ── Admin ────────────────────────────────────────────────
def _seed_admin():
    db.run("""
        CREATE (u:User {
            username: 'admin',
            password: $pw,
            email: 'admin@nexgen.hospital',
            role: 'ADMIN',
            active: true,
            created_at: $today
        })
    """, pw=hash_password("admin123"), today=str(date.today()))

# ── Doctors ───────────────────────────────────────────────
DOCTORS = [
    ("dr.aditi",  "Dr. Aditi Roy",    "Cardiology",       "MD, DM Cardiology",   "REGN-001", "+91 98000 11001", 1200.0, 12),
    ("dr.karan",  "Dr. Karan Mehta",  "Orthopaedics",     "MS Orthopaedics",     "REGN-002", "+91 98000 11002", 1000.0,  9),
    ("dr.rohan",  "Dr. Rohan Bose",   "Neurology",        "MD, DM Neurology",    "REGN-003", "+91 98000 11003", 1500.0, 15),
    ("dr.lata",   "Dr. Lata Rao",     "Paediatrics",      "MD Paediatrics",      "REGN-004", "+91 98000 11004",  800.0,  8),
    ("dr.priya",  "Dr. Priya Nair",   "General Medicine", "MBBS, MD",            "REGN-005", "+91 98000 11005",  600.0,  6),
    ("dr.arjun",  "Dr. Arjun Verma",  "Oncology",         "MD, DM Oncology",     "REGN-006", "+91 98000 11006", 2000.0, 18),
]

def _seed_doctors():
    for (uname, name, spec, qual, lic, phone, fee, exp) in DOCTORS:
        db.run("""
            CREATE (u:User {
                username: $uname, password: $pw,
                email: $email, role: 'DOCTOR', active: true, created_at: $today
            })
            CREATE (d:Doctor {
                username: $uname, full_name: $name,
                specialization: $spec, department: $spec,
                qualification: $qual, license_number: $lic,
                phone: $phone, email: $email,
                available_days: 'MON,TUE,WED,THU,FRI',
                consultation_fee: $fee, years_of_experience: $exp,
                active: true, created_at: $today
            })
        """,
        uname=uname, pw=hash_password("doctor123"),
        email=f"{uname}@nexgen.hospital", name=name,
        spec=spec, qual=qual, lic=lic, phone=phone,
        fee=fee, exp=exp, today=str(date.today()))

# ── Patients ──────────────────────────────────────────────
PATIENTS = [
    ("meera.g",  "Meera Gupta",   "F", "1972-03-14", "A+",  "+91 99000 11001", "Ward A", "03", "Angina Pectoris",  "dr.aditi", "ADMITTED"),
    ("rahul.k",  "Rahul Khanna",  "M", "1990-07-22", "O+",  "+91 99000 11002", "ICU",    "01", "Polytrauma",       "dr.rohan", "CRITICAL"),
    ("suresh.p", "Suresh Patel",  "M", "1963-11-05", "B+",  "+91 99000 11003", "Ward B", "11", "Hip Replacement",  "dr.karan", "ADMITTED"),
    ("anjali.d", "Anjali Das",    "F", "1979-05-19", "AB+", "+91 99000 11004", "Ward A", "09", "Migraine",         "dr.rohan", "ADMITTED"),
    ("kavya.p",  "Kavya Pillai",  "F", "2017-04-12", "A-",  "+91 99000 11006", "Ward D", "02", "Pneumonia",        "dr.lata",  "ADMITTED"),
    ("ravi.s",   "Ravi Sharma",   "M", "1984-09-30", "O-",  "+91 99000 11005", "—",      "—",  "Hypertension",     "dr.priya", "DISCHARGED"),
]

def _seed_patients():
    for i, (uname, name, gender, dob, blood, phone, ward, bed, diag, doc, status) in enumerate(PATIENTS):
        pid = f"P-{1001 + i}"
        db.run("""
            CREATE (u:User {
                username: $uname, password: $pw,
                email: $email, role: 'PATIENT', active: true, created_at: $today
            })
            CREATE (p:Patient {
                patient_id: $pid, username: $uname,
                full_name: $name, gender: $gender,
                date_of_birth: $dob, blood_group: $blood,
                phone: $phone, email: $email,
                ward: $ward, bed_number: $bed,
                diagnosis: $diag,
                assigned_doctor_username: $doc,
                status: $status,
                insurance_provider: 'Star Health',
                admission_date: $today,
                created_at: $today
            })
        """,
        uname=uname, pw=hash_password("patient123"),
        email=f"{uname}@email.com", pid=pid,
        name=name, gender=gender, dob=dob, blood=blood,
        phone=phone, ward=ward, bed=bed, diag=diag,
        doc=doc, status=status, today=str(date.today()))

# ── Appointments ──────────────────────────────────────────
def _seed_appointments():
    today = str(date.today())
    appts = [
        ("APT-1001","meera.g","Meera Gupta","dr.aditi","Dr. Aditi Roy","Cardiology","09:30","NEW_CONSULTATION","SCHEDULED","Chest pain review"),
        ("APT-1002","suresh.p","Suresh Patel","dr.karan","Dr. Karan Mehta","Orthopaedics","10:15","FOLLOW_UP","SCHEDULED","Post-surgery review"),
        ("APT-1003","anjali.d","Anjali Das","dr.rohan","Dr. Rohan Bose","Neurology","11:00","NEW_CONSULTATION","SCHEDULED","Severe headache"),
        ("APT-1004","kavya.p","Kavya Pillai","dr.lata","Dr. Lata Rao","Paediatrics","14:00","FOLLOW_UP","SCHEDULED","Fever follow-up"),
        ("APT-1005","ravi.s","Ravi Sharma","dr.priya","Dr. Priya Nair","General Medicine","08:00","FOLLOW_UP","COMPLETED","BP check"),
    ]
    for (aid, pu, pn, du, dn, dept, time, typ, status, reason) in appts:
        db.run("""
            CREATE (a:Appointment {
                appointment_id: $aid,
                patient_username: $pu, patient_name: $pn,
                doctor_username: $du, doctor_name: $dn,
                department: $dept,
                appointment_date: $today,
                appointment_time: $time,
                type: $typ, status: $status,
                reason: $reason,
                created_by: 'admin', created_at: $today
            })
        """, aid=aid, pu=pu, pn=pn, du=du, dn=dn,
             dept=dept, today=today, time=time,
             typ=typ, status=status, reason=reason)

# ── Medical Records ───────────────────────────────────────
def _seed_records():
    today = str(date.today())
    db.run("""
        CREATE (r:MedicalRecord {
            record_id: 'REC-1001',
            patient_username: 'meera.g',
            doctor_username: 'dr.aditi',
            doctor_name: 'Dr. Aditi Roy',
            record_date: $today,
            visit_type: 'OPD',
            chief_complaint: 'Chest pain, shortness of breath',
            diagnosis: 'Stable Angina Pectoris',
            symptoms: 'Chest tightness on exertion, mild dyspnoea',
            examination: 'BP 138/88, HR 82/min, clear lung fields',
            prescription: 'Tab. Aspirin 75mg OD, Tab. Atenolol 25mg OD',
            lab_tests: 'ECG, Lipid Profile, CBC, Troponin I',
            lab_results: 'ECG: ST depression V4-V6. Troponin: Negative.',
            vitals: '{"bp":"138/88","pulse":82,"temp":"98.4F","weight":"72kg","spo2":"97%"}',
            next_visit_date: $today,
            notes: 'Advised stress test. Low fat diet.',
            created_at: $today
        })
    """, today=today)

    db.run("""
        CREATE (r:MedicalRecord {
            record_id: 'REC-1002',
            patient_username: 'anjali.d',
            doctor_username: 'dr.rohan',
            doctor_name: 'Dr. Rohan Bose',
            record_date: $today,
            visit_type: 'OPD',
            chief_complaint: 'Severe headache, nausea, photophobia',
            diagnosis: 'Migraine without aura',
            symptoms: 'Throbbing unilateral headache, nausea, photophobia',
            examination: 'Neurological exam: normal. No focal deficits.',
            prescription: 'Tab. Sumatriptan 50mg SOS, Tab. Metoclopramide 10mg TDS',
            lab_tests: 'MRI Brain',
            lab_results: 'Pending',
            vitals: '{"bp":"118/76","pulse":74,"temp":"98.6F","weight":"58kg","spo2":"99%"}',
            next_visit_date: $today,
            notes: 'Maintain migraine diary. Avoid triggers.',
            created_at: $today
        })
    """, today=today)

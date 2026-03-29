from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any
from datetime import date, datetime

# ── Generic response wrapper ──────────────────────────────
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

    @classmethod
    def ok(cls, data=None, message="Success"):
        return cls(success=True, message=message, data=data)

    @classmethod
    def error(cls, message="Error"):
        return cls(success=False, message=message, data=None)

# ── Auth ──────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    token: str
    username: str
    role: str
    full_name: str

# ── User ──────────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    role: str  # PATIENT | DOCTOR | ADMIN

# ── Patient ───────────────────────────────────────────────
class PatientCreate(BaseModel):
    # Login credentials
    username: str
    password: str
    # Personal
    full_name: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    # Medical
    insurance_provider: Optional[str] = None
    insurance_number: Optional[str] = None
    ward: Optional[str] = None
    bed_number: Optional[str] = None
    admission_date: Optional[str] = None
    diagnosis: Optional[str] = None
    status: Optional[str] = "ADMITTED"
    assigned_doctor_username: Optional[str] = None
    notes: Optional[str] = None

class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    ward: Optional[str] = None
    bed_number: Optional[str] = None
    diagnosis: Optional[str] = None
    status: Optional[str] = None
    assigned_doctor_username: Optional[str] = None
    discharge_date: Optional[str] = None
    notes: Optional[str] = None

# ── Doctor ────────────────────────────────────────────────
class DoctorCreate(BaseModel):
    username: str
    password: str
    full_name: str
    specialization: str
    department: str
    qualification: Optional[str] = None
    license_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    available_days: Optional[str] = "MON,TUE,WED,THU,FRI"
    consultation_fee: Optional[float] = None
    years_of_experience: Optional[int] = None

class DoctorUpdate(BaseModel):
    full_name: Optional[str] = None
    specialization: Optional[str] = None
    department: Optional[str] = None
    qualification: Optional[str] = None
    phone: Optional[str] = None
    available_days: Optional[str] = None
    consultation_fee: Optional[float] = None

# ── Appointment ───────────────────────────────────────────
class AppointmentCreate(BaseModel):
    patient_username: str
    patient_name: str
    doctor_username: str
    doctor_name: str
    department: str
    appointment_date: str   # YYYY-MM-DD
    appointment_time: str   # HH:MM
    type: Optional[str] = "NEW_CONSULTATION"
    reason: Optional[str] = None
    notes: Optional[str] = None

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    doctor_username: Optional[str] = None
    doctor_name: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    prescription: Optional[str] = None

# ── Medical Record ────────────────────────────────────────
class RecordCreate(BaseModel):
    patient_username: str
    record_date: Optional[str] = None
    visit_type: Optional[str] = "OPD"
    chief_complaint: Optional[str] = None
    diagnosis: Optional[str] = None
    symptoms: Optional[str] = None
    examination: Optional[str] = None
    prescription: Optional[str] = None
    lab_tests: Optional[str] = None
    lab_results: Optional[str] = None
    vitals: Optional[str] = None   # JSON string: {"bp":"120/80","pulse":72,...}
    next_visit_date: Optional[str] = None
    notes: Optional[str] = None

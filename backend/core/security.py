from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# ================= CONFIG =================
SECRET_KEY = "supersecretkey"  # ⚠️ change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


# ================= PASSWORD =================
def hash_password(password: str):
    """
    Hash password safely (bcrypt limit fix applied)
    """
    if not password:
        raise ValueError("Password cannot be empty")

    return pwd_context.hash(password[:72])  # 🔥 FIX


def verify_password(password: str, hashed: str):
    """
    Verify password safely (no crash)
    """
    try:
        return pwd_context.verify(password[:72], hashed)
    except Exception:
        return False  # 🔥 prevents 500 crash


# ================= JWT CREATE =================
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "type": "access"
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ================= VERIFY TOKEN =================
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


# ================= CURRENT USER =================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )

    return payload


# ================= ROLE GUARDS =================
def admin_only(user=Depends(get_current_user)):
    if user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


def doctor_only(user=Depends(get_current_user)):
    if user.get("role") != "DOCTOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor access required"
        )
    return user


def patient_only(user=Depends(get_current_user)):
    if user.get("role") != "PATIENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient access required"
        )
    return user

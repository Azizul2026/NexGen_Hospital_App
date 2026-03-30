from fastapi import APIRouter, HTTPException
from core.security import create_access_token, create_refresh_token, verify_token, verify_password
from core.database import db
from passlib.context import CryptContext

router = APIRouter(prefix="/api/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔐 SAFE PASSWORD (bcrypt limit fix)
def safe_pwd(p: str):
    return (p or "")[:72]


# ================= LOGIN =================
@router.post("/login")
def login(data: dict):
    username = data.get("username")
    password = data.get("password")

    # ❌ VALIDATION
    if not verify_password(password, user["password"]):
        raise HTTPException(401, "Invalid username or password")

    # 🔍 FIND USER
    row = db.run_one("MATCH (u:User {username:$u}) RETURN u", u=username)

    if not row:
        raise HTTPException(401, "Invalid username or password")

    user = row["u"]

    # 🔐 VERIFY PASSWORD (FIXED)
    try:
        if not pwd_context.verify(safe_pwd(password), user["password"]):
            raise HTTPException(401, "Invalid username or password")
    except Exception:
        raise HTTPException(401, "Invalid username or password")

    # 🔑 CREATE TOKENS
    payload = {
        "username": user["username"],
        "role": user["role"]
    }

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    # ✅ RESPONSE (MATCHES FRONTEND)
    return {
        "success": True,
        "data": {
            "token": access_token,
            "refresh_token": refresh_token,
            "username": user["username"],
            "role": user["role"],
            "fullName": user.get("full_name", user["username"])
        }
    }


# ================= REFRESH =================
@router.post("/refresh")
def refresh(data: dict):
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        raise HTTPException(400, "Missing refresh token")

    payload = verify_token(refresh_token)

    if not payload:
        raise HTTPException(401, "Invalid refresh token")

    new_access = create_access_token(payload)

    return {
        "success": True,
        "data": {
            "token": new_access
        }
    }

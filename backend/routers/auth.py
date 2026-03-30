from fastapi import APIRouter, HTTPException
from core.security import create_access_token, create_refresh_token
from core.database import db
from passlib.context import CryptContext

router = APIRouter(prefix="/api/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ================= LOGIN =================
@router.post("/login")
def login(data: dict):

    username = data.get("username")
    password = data.get("password")

    # 🔍 FIND USER
    user = db.run_one("MATCH (u:User {username:$u}) RETURN u", u=username)

    if not user:
        raise HTTPException(401, "Invalid username or password")

    user = user["u"]

    # 🔐 VERIFY PASSWORD
    if not pwd_context.verify(password, user["password"]):
        raise HTTPException(401, "Invalid username or password")

    # 🔑 CREATE TOKENS
    payload = {
        "username": user["username"],
        "role": user["role"]
    }

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    # ✅ RETURN FORMAT (VERY IMPORTANT)
    return {
        "success": True,
        "data": {
            "token": access_token,
            "refresh_token": refresh_token,
            "username": user["username"],
            "role": user["role"],
            "fullName": user.get("full_name", "")
        }
    }


# ================= REFRESH =================
@router.post("/refresh")
def refresh(data: dict):
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        raise HTTPException(400, "Missing refresh token")

    from core.security import verify_token
    payload = verify_token(refresh_token)

    if not payload:
        raise HTTPException(401, "Invalid refresh token")

    new_access = create_access_token(payload)

    return {
        "access_token": new_access
    }

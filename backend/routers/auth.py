from fastapi import APIRouter, HTTPException
from core.database import db
from core.security import (
    create_access_token,
    create_refresh_token,
    verify_password
)

router = APIRouter(prefix="/api/auth", tags=["Auth"])


# ================= LOGIN =================
@router.post("/login")
def login(data: dict):
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        raise HTTPException(400, "Username & password required")

    # 🔍 find user
    user = db.run_one("MATCH (u:User {username:$u}) RETURN u", u=username)

    if not user:
        raise HTTPException(401, "Invalid username")

    user = user["u"]

    # 🔐 check password
    if not verify_password(password, user["password"]):
        raise HTTPException(401, "Invalid password")

    payload = {
        "username": user["username"],
        "role": user["role"]
    }

    return {
        "success": True,
        "data": {
            "token": create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
            "username": user["username"],
            "role": user["role"]
        }
    }


# ================= REFRESH =================
@router.post("/refresh")
def refresh(data: dict):
    token = data.get("refresh_token")

    payload = verify_password(token)  # ❗ fix if needed based on your impl

    if not payload:
        raise HTTPException(401, "Invalid refresh token")

    return {
        "access_token": create_access_token(payload)
    }

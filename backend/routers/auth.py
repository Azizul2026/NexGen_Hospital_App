from fastapi import APIRouter
from core.security import create_access_token, create_refresh_token, verify_token

router = APIRouter(prefix="/api/auth")

@router.post("/login")
def login(data: dict):
    user = {"username": data["username"], "role": "admin"}

    return {
        "access_token": create_access_token(user),
        "refresh_token": create_refresh_token(user),
        "role": user["role"]
    }


@router.post("/refresh")
def refresh(data: dict):
    payload = verify_token(data["refresh_token"])

    if not payload:
        return {"success": False}

    new_access = create_access_token(payload)

    return {"access_token": new_access}
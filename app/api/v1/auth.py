from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import os
from datetime import timedelta

from app.db.session import get_db
from app.models.admin import Admin
from app.services.auth import verify_password

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

# -------------------------------------------------
# ROUTER
# -------------------------------------------------
router = APIRouter(tags=["Auth"])

# -------------------------------------------------
# TOKEN CREATION (SINGLE SOURCE)
# -------------------------------------------------
def create_access_token(data: dict):
    payload = data.copy()
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# -------------------------------------------------
# LOGIN
# -------------------------------------------------
@router.post("/auth/login")
def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    admin = db.query(Admin).filter(Admin.username == username).first()

    if not admin or not verify_password(password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": admin.username,
        "role": "admin"
    })

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
    )

    return {"message": "Login successful"}

# -------------------------------------------------
# LOGOUT
# -------------------------------------------------
@router.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}

# -------------------------------------------------
# AUTH DEPENDENCY
# -------------------------------------------------
def require_admin(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return payload

# -------------------------------------------------
# WHO AM I
# -------------------------------------------------
@router.get("/auth/me")
def me(payload: dict = Depends(require_admin)):
    return {
        "username": payload.get("sub"),
        "role": payload.get("role"),
    }
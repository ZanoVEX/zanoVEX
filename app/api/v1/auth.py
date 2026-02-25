from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.session import get_db
from app.models.admin import Admin
from app.services.auth import verify_password, create_access_token

# ======================
# CONFIG
# ======================
SECRET_KEY = "CHANGE_ME"  # on Render this comes from env
ALGORITHM = "HS256"

router = APIRouter(tags=["Auth"])


# =====================================================
# LOGIN (ADMIN) — FIXED FOR HTML FORMS
# =====================================================
@router.post("/auth/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    admin = db.query(Admin).filter(Admin.username == username).first()

    if not admin or not verify_password(password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        data={"sub": admin.username, "role": "admin"}
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


# =====================================================
# AUTH GUARD (ADMIN ONLY)
# =====================================================
def require_admin(request: Request):
    auth = request.headers.get("Authorization")

    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return payload


# =====================================================
# WHO AM I (ADMIN)
# =====================================================
@router.get("/auth/me")
def me(payload: dict = Depends(require_admin)):
    return {
        "username": payload.get("sub"),
        "role": payload.get("role"),
    }

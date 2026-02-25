from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.admin import Admin  # adjust if your model name differs
from app.services.auth import verify_password, create_access_token
from jose import jwt, JWTError
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from app.services.auth import require_admin

SECRET_KEY = "CHANGE_ME"
ALGORITHM = "HS256"

router = APIRouter(tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


# =====================================================
# LOGIN (ADMIN)
# =====================================================
@router.post("/auth/login")
def login(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.username == username).first()

    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        data={"sub": admin.username, "role": "admin"}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# =====================================================
# WHO AM I (ADMIN)
# =====================================================
@router.get("/auth/me")
def me(
    payload: dict = Depends(require_admin),
):
    return {
        "username": payload.get("sub"),
        "role": payload.get("role"),
    }
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

    # attach admin info to request
    request.state.admin = payload

    return payload

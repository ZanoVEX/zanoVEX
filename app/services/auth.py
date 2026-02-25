from fastapi import HTTPException, Request, Depends
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# ===============================
# CONFIG
# ===============================
SECRET_KEY = "CHANGE_THIS_SECRET_KEY"
ALGORITHM = "HS256"

security = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ===============================
# PASSWORD UTILS
# ===============================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ===============================
# TOKEN UTILS
# ===============================
def create_access_token(data: dict) -> str:
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# ===============================
# AUTH GUARD
# ===============================
def require_admin(
 credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None
):
    # Allow Swagger/OpenAPI pages without auth
    if request and request.url.path in ["/openapi.json", "/docs", "/docs/oauth2-redirect"]:
        return

    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    request.state.admin = payload
    return payload
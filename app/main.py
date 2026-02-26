from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import os

from app.api.v1 import emails, domains, auth
from app.db.session import SessionLocal
from app.models.admin import Admin
from app.services.auth import hash_password, require_admin

# -------------------------------------------------
# APP INIT
# -------------------------------------------------
app = FastAPI(
    title="Zanovex Email Provisioning API",
    version="0.2.0",
    docs_url="/docs",
    redoc_url=None
)

# -------------------------------------------------
# STATIC & TEMPLATES
# -------------------------------------------------
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# -------------------------------------------------
# CORS
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# STARTUP — AUTO CREATE ADMIN (RENDER SAFE)
# -------------------------------------------------
@app.on_event("startup")
def create_default_admin():
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin123")

    db = SessionLocal()

    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin:
        admin = Admin(
            username=username,
            password_hash=hash_password(password)
        )
        db.add(admin)
        db.commit()
        print("✅ Default admin created")

    db.close()

# -------------------------------------------------
# UI ROUTES
# -------------------------------------------------
@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard")
def dashboard_page(
    request: Request,
    _: dict = Depends(require_admin),
):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# -------------------------------------------------
# API ROUTERS
# -------------------------------------------------
app.include_router(emails.router, prefix="/api/v1", tags=["Emails"])
app.include_router(domains.router, prefix="/api/v1", tags=["Domains"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
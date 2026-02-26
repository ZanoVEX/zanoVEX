from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from app.api.v1 import emails, domains, auth
from app.api.v1.auth import require_admin
from app.db.session import SessionLocal
from app.models.admin import Admin
from app.services.auth import hash_password

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
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# STARTUP — AUTO CREATE ADMIN
# -------------------------------------------------
@app.on_event("startup")
def create_default_admin():
    db = SessionLocal()

    admin = db.query(Admin).filter(Admin.username == "admin").first()
    if not admin:
        admin = Admin(
            username="admin",
            password_hash=hash_password("admin123")
        )
        db.add(admin)
        db.commit()

    db.close()

# -------------------------------------------------
# HTML ROUTES
# -------------------------------------------------
@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

@app.get("/dashboard")
def dashboard_page(
    request: Request,
    _: dict = Depends(require_admin),
):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )

# -------------------------------------------------
# API ROUTERS
# -------------------------------------------------
app.include_router(emails.router, prefix="/api/v1")
app.include_router(domains.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
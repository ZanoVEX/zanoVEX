from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pathlib import Path
from app.api.v1.auth import router as auth_router
from app.api.v1.emails import router as email_router
from app.api.v1.domains import router as domain_router
from app.db.init_db import init_db
from app.api.v1 import emails, domains, auth
app = FastAPI(
    title="Zanovex Email Provisioning API",
    version="0.2.0",
    docs_url="/docs",
    redoc_url=None
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates") 

@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard")
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# -------------------------------------------------
# CORS CONFIGURATION (DEV)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# STARTUP
# -------------------------------------------------
@app.on_event("startup")
def startup():
    init_db()

# -------------------------------------------------
# DASHBOARD FILE PATH
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

# -------------------------------------------------
# DASHBOARD ROUTES  ✅ STEP 3 (THIS IS WHAT YOU ASKED)
# -------------------------------------------------
@app.get("/")
def serve_client_dashboard():
    return FileResponse(BASE_DIR / "dashboard" / "index.html")


@app.get("/dashboard/emails")
def serve_admin_emails():
    return FileResponse(BASE_DIR / "dashboard" / "emails.html")


@app.get("/dashboard/domains")
def serve_admin_domains():
    return FileResponse(BASE_DIR / "dashboard" / "domains.html")

@app.get("/")
def root():
    return {"status": "Zanovex API running"}
# -------------------------------------------------
# API ROUTERS
# -------------------------------------------------
app.include_router(emails.router, prefix="/api/v1", tags=["Emails"])
app.include_router(domains.router, prefix="/api/v1", tags=["Domains"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])

for route in app.routes:
    print(route.path)

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.email_account import EmailAccount
from app.models.domain import Domain
from app.services.dns import dns_ready
from app.services.auth import require_admin

router = APIRouter(tags=["Emails"])


# =========================
# LIST EMAILS (ADMIN)
# =========================
@router.get("/emails")
def list_emails(
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    emails = db.query(EmailAccount).all()

    return [
        {
            "email": e.address,
            "domain": e.domain,
            "status": e.status,
        }
        for e in emails
    ]


# =========================
# CREATE EMAIL
# =========================
@router.post("/emails/create")
def create_email(
    domain: str,
    local_part: str,
    db: Session = Depends(get_db),
):
    if "@" in local_part:
        raise HTTPException(status_code=400, detail="Invalid email name")

    email_address = f"{local_part}@{domain}"

    existing = db.query(EmailAccount).filter(
        EmailAccount.address == email_address
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    # get or create domain
    db_domain = db.query(Domain).filter(Domain.name == domain).first()
    if not db_domain:
        db_domain = Domain(
            name=domain,
            verified=False,
            provider="namecheap",
        )
        db.add(db_domain)
        db.commit()
        db.refresh(db_domain)

    # DNS check
    if not dns_ready(domain):
        email = EmailAccount(
            address=email_address,
            domain=domain,
            status="pending",
        )
        db.add(email)
        db.commit()
        db.refresh(email)

        return {
            "email": email.address,
            "status": email.status,
            "message": "DNS not fully ready. Email pending.",
        }

    # DNS ready → mark domain verified
    if not db_domain.verified:
        db_domain.verified = True
        db.commit()

    email = EmailAccount(
        address=email_address,
        domain=domain,
        status="awaiting_provider_setup",
    )
    db.add(email)
    db.commit()
    db.refresh(email)

    return {
        "email": email.address,
        "status": email.status,
        "message": "Email request created.",
    }


# =========================
# GET EMAIL STATUS
# =========================
@router.get("/emails/status")
def get_email_status(
    email: str,
    db: Session = Depends(get_db),
):
    record = db.query(EmailAccount).filter(
        EmailAccount.address == email
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Email not found")

    return {
        "email": record.address,
        "status": record.status,
    }


# =========================
# ACTIVATE EMAIL (ADMIN)
# =========================
@router.post("/emails/activate")
def activate_email(
    email: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    record = db.query(EmailAccount).filter(
        EmailAccount.address == email
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Email not found")

    if record.status == "active":
        return {
            "email": record.address,
            "status": record.status,
            "message": "Email already active",
        }

    record.status = "active"
    db.commit()
    db.refresh(record)

    return {
        "email": record.address,
        "status": record.status,
        "message": "Email activated successfully",
    }


# =========================
# DEACTIVATE EMAIL (ADMIN)
# =========================
@router.post("/emails/deactivate")
def deactivate_email(
    email: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    record = db.query(EmailAccount).filter(
        EmailAccount.address == email
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Email not found")

    record.status = "disabled"
    db.commit()
    db.refresh(record)

    return {
        "email": record.address,
        "status": record.status,
        "message": "Email disabled",
    }
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.domain import Domain
from app.services.auth import require_admin

router = APIRouter(tags=["Domains"])


# =========================
# LIST DOMAINS (ADMIN)
# =========================
@router.get("/domains")
def list_domains(
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    domains = db.query(Domain).all()

    return [
        {
            "name": d.name,
            "verified": d.verified,
            "provider": d.provider,
        }
        for d in domains
    ]


# =========================
# GET SINGLE DOMAIN
# =========================
@router.get("/domains/{domain_name}")
def get_domain(
    domain_name: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    domain = db.query(Domain).filter(Domain.name == domain_name).first()

    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    return {
        "name": domain.name,
        "verified": domain.verified,
        "provider": domain.provider,
    }


# =========================
# UPDATE DOMAIN PROVIDER
# =========================
@router.patch("/domains/{domain_name}")
def update_domain(
    domain_name: str,
    provider: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    domain = db.query(Domain).filter(Domain.name == domain_name).first()

    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    domain.provider = provider
    db.commit()
    db.refresh(domain)

    return {
        "message": "Domain updated",
        "name": domain.name,
        "provider": domain.provider,
        "verified": domain.verified,
    }
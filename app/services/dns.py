import os
import dns.resolver


# -------------------------------------------------
# MX CHECK
# -------------------------------------------------
def check_mx(domain: str) -> bool:
    try:
        answers = dns.resolver.resolve(domain, "MX")
        return len(answers) > 0
    except Exception:
        return False


# -------------------------------------------------
# SPF CHECK
# -------------------------------------------------
def check_spf(domain: str) -> bool:
    try:
        answers = dns.resolver.resolve(domain, "TXT")
        for rdata in answers:
            record = "".join([txt.decode() for txt in rdata.strings])
            if record.lower().startswith("v=spf1"):
                return True
        return False
    except Exception:
        return False


# -------------------------------------------------
# DKIM CHECK (OPTIONAL / PROVIDER-MANAGED)
# -------------------------------------------------
def check_dkim(domain: str) -> bool:
    """
    DKIM selectors vary by provider.
    This function is kept for future strict mode.
    It is NOT required for MVP readiness.
    """
    selectors = [
        "default",
        "selector1",
        "selector2",
        "zoho",
        "google",
        "mail"
    ]

    for selector in selectors:
        dkim_domain = f"{selector}._domainkey.{domain}"
        try:
            answers = dns.resolver.resolve(dkim_domain, "TXT")
            for rdata in answers:
                record = "".join([txt.decode() for txt in rdata.strings])
                if "v=DKIM1" in record:
                    return True
        except Exception:
            continue

    return False


# -------------------------------------------------
# DNS READINESS GATE (MAIN FUNCTION)
# -------------------------------------------------
def dns_ready(domain: str) -> bool:
    """
    DNS readiness logic.

    DEV MODE:
    - If DNS_FORCE_READY=true → always return True

    PROD / MVP MODE:
    - MX must exist
    - SPF must exist
    - DKIM is provider-managed (NOT blocking)
    """

    # 🔴 DEVELOPMENT OVERRIDE (SAFE & INTENTIONAL)
    if os.getenv("DNS_FORCE_READY", "").lower() == "true":
        return True

    # 🟢 REAL MVP LOGIC
    return (
        check_mx(domain)
        and check_spf(domain)
        # DKIM intentionally NOT required here
    )
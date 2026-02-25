import os

ADMIN_COOKIE_NAME = "zanovex_admin"
ADMIN_SESSION_SECONDS = 60 * 60 * 4  # 4 hours


def is_production() -> bool:
    return os.getenv("ENV") == "production"
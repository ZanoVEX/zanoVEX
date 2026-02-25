from app.db.base import Base
from app.db.session import engine

# IMPORT ALL MODELS HERE ⬇⬇⬇
from app.models.admin import Admin
from app.models.domain import Domain
from app.models.email_account import EmailAccount

def init_db():
    Base.metadata.create_all(bind=engine)
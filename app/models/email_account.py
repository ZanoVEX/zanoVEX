from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.session import Base

class EmailAccount(Base):
    __tablename__ = "email_accounts"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, index=True, nullable=False)
    domain = Column(String, nullable=False)
    status = Column(String, default="pending")
from sqlalchemy import Column, Integer, String, Boolean
from app.db.session import Base


class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    verified = Column(Boolean, default=False)

    provider = Column(String, default="namecheap", nullable=False)
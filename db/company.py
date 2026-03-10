from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    # Una empresa tiene muchas sucursales
    branches = relationship("Branch", back_populates="company_rel", cascade="all, delete-orphan")
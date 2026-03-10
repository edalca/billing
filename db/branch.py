from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Branch(Base):
    """
    Represents a specific business location (Branch) belonging to a Company.
    Each branch manages its own stock and generates its own invoices.
    """
    __tablename__ = "branches"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    
    # Foreign Key to Company
    company_id = Column(Integer, ForeignKey("companies.id"))

    # Relationships
    # Many-to-one: Many branches belong to one company
    company_rel = relationship("Company", back_populates="branches")

    # One-to-many: One branch has many stock entries
    stocks = relationship("Stock", back_populates="branch_rel", cascade="all, delete-orphan")
    
    # One-to-many: One branch has many invoices
    invoices = relationship("Invoice", back_populates="branch_rel", cascade="all, delete-orphan")
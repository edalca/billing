from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Stock(Base):
    """
    Represents the inventory items (stock) for a specific branch and period.
    """
    __tablename__ = "stock"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    qty = Column(Integer)
    price = Column(Float)
    tax = Column(Integer)  # 0 or 15
    month = Column(Integer)
    year = Column(Integer)
    
    # Foreign Key
    branch_id = Column(Integer, ForeignKey("branches.id"))
    
    # Relationship with Branch
    # Changed 'stock_items' to 'stocks' to match the property name in db/branch.py
    branch_rel = relationship("Branch", back_populates="stocks")
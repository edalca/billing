from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_no = Column(String, unique=True, index=True)
    
    # Customer Name
    customer_name = Column(String, default="Consumidor Final") 
    
    # Invoice Date
    date = Column(Date) 
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Calculated Totals
    exempt_total = Column(Float, default=0.0)
    taxed15_total = Column(Float, default=0.0)
    isv15_total = Column(Float, default=0.0)
    grand_total = Column(Float, default=0.0)

    # Relationship with Branch
    branch_id = Column(Integer, ForeignKey("branches.id"))
    branch_rel = relationship("Branch", back_populates="invoices")

    # Relationship with Invoice Items (Cascade delete)
    items = relationship("InvoiceItem", back_populates="invoice_rel", cascade="all, delete-orphan")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float)
    tax_pct = Column(Integer) # Tax percentage (e.g., 0 or 15)

    # Relationship with parent Invoice
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    invoice_rel = relationship("Invoice", back_populates="items")
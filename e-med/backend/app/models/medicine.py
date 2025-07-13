from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    medicines = relationship("Medicine", back_populates="category")

class Medicine(Base):
    __tablename__ = "medicines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    generic_name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    manufacturer = Column(String, nullable=True)
    dosage_form = Column(String, nullable=True)
    strength = Column(String, nullable=True)
    prescription_required = Column(Boolean, default=False)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    min_stock_level = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    category = relationship("Category", back_populates="medicines")
    alternatives = relationship("MedicineAlternative", foreign_keys="[MedicineAlternative.medicine_id]", back_populates="medicine")

class MedicineAlternative(Base):
    __tablename__ = "medicine_alternatives"
    
    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id"))
    alternative_medicine_id = Column(Integer, ForeignKey("medicines.id"))
    reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    medicine = relationship("Medicine", foreign_keys=[medicine_id], back_populates="alternatives")
    alternative_medicine = relationship("Medicine", foreign_keys=[alternative_medicine_id]) 
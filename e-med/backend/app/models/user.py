from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    PHARMACY_ADMIN = "pharmacy_admin"
    DELIVERY_PARTNER = "delivery_partner"
    SYSTEM_ADMIN = "system_admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Customer specific fields
    address = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=True)
    medical_info = Column(String, nullable=True)  # JSON string for medical history
    
    # Delivery partner specific fields
    vehicle_number = Column(String, nullable=True)
    current_location = Column(String, nullable=True)  # JSON string for lat/lng
    is_available = Column(Boolean, default=True)
    
    # Pharmacy admin specific fields
    pharmacy_name = Column(String, nullable=True)
    pharmacy_address = Column(String, nullable=True)
    license_number = Column(String, nullable=True) 
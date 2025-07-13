from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PrescriptionStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"

# Base Prescription Schema
class PrescriptionBase(BaseModel):
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    prescription_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    verification_notes: Optional[str] = None

# Create Prescription Schema
class PrescriptionCreate(PrescriptionBase):
    file_url: str = Field(..., description="Cloudinary URL of the prescription image")
    file_name: Optional[str] = None
    file_size: Optional[int] = None

# Update Prescription Schema
class PrescriptionUpdate(BaseModel):
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    prescription_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    verification_notes: Optional[str] = None
    status: Optional[PrescriptionStatus] = None

# Prescription Response Schema
class Prescription(PrescriptionBase):
    id: int
    user_id: int
    verified_by: Optional[int] = None
    file_url: str
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    status: PrescriptionStatus
    extracted_medicines: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Prescription Verification Schema
class PrescriptionVerification(BaseModel):
    status: PrescriptionStatus
    verification_notes: Optional[str] = None
    extracted_medicines: Optional[str] = None

# Prescription Search Schema
class PrescriptionSearch(BaseModel):
    status: Optional[PrescriptionStatus] = None
    user_id: Optional[int] = None
    limit: int = 20
    offset: int = 0 
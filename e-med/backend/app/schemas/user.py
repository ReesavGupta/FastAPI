from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

# Base User Schema
class UserBase(BaseModel):
    email: EmailStr
    phone: str
    full_name: str
    role: UserRole = UserRole.CUSTOMER

# Create User Schema
class UserCreate(UserBase):
    password: str
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_info: Optional[str] = None
    pharmacy_name: Optional[str] = None
    pharmacy_address: Optional[str] = None
    license_number: Optional[str] = None
    vehicle_number: Optional[str] = None

# Update User Schema
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_info: Optional[str] = None
    pharmacy_name: Optional[str] = None
    pharmacy_address: Optional[str] = None
    license_number: Optional[str] = None
    vehicle_number: Optional[str] = None
    current_location: Optional[str] = None
    is_available: Optional[bool] = None

# User Response Schema
class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_info: Optional[str] = None
    pharmacy_name: Optional[str] = None
    pharmacy_address: Optional[str] = None
    license_number: Optional[str] = None
    vehicle_number: Optional[str] = None
    current_location: Optional[str] = None
    is_available: Optional[bool] = None

    class Config:
        from_attributes = True

# Login Schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str

# Token Data Schema
class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[UserRole] = None 
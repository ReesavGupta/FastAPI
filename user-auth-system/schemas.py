from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_.-]+$')
    email: EmailStr
    password: constr(min_length=8)

    @validator('username')
    def username_strip_and_sanitize(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Username cannot be empty or whitespace.')
        return v

    @validator('password')
    def password_strength(cls, v):
        import re
        if not re.match(r'^(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$', v):
            raise ValueError('Password must be at least 8 characters and contain a special character.')
        return v

class UserLogin(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=8)

    @validator('username')
    def username_strip(cls, v):
        return v.strip()

    @validator('password')
    def password_strip(cls, v):
        return v.strip()

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str 
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User as UserModel, UserRole
from app.schemas.user import User as UserSchema
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

# Helper function to check if user is admin

def get_admin_user(current_user = Depends(get_current_user)):
    if current_user.role not in [UserRole.PHARMACY_ADMIN, UserRole.SYSTEM_ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

@router.get("/", response_model=List[UserSchema])
async def get_users(
    role: Optional[str] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    query = db.query(UserModel)
    if role:
        query = query.filter(UserModel.role == role)
    if is_active is not None:
        query = query.filter(UserModel.is_active == is_active)
    users = query.all()
    return users

@router.get("/{user_id}", response_model=UserSchema)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Only return public fields (handled by schema)
    return user 
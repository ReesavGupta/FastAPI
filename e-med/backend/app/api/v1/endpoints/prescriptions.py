from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User, UserRole
from app.models.prescription import Prescription, PrescriptionStatus
from app.schemas.prescription import (
    PrescriptionCreate, PrescriptionUpdate, Prescription as PrescriptionSchema,
    PrescriptionVerification, PrescriptionSearch
)
from app.services.cloudinary_service import cloudinary_service
import uuid
from datetime import datetime

router = APIRouter()

# Helper function to check if user is admin
def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.PHARMACY_ADMIN, UserRole.SYSTEM_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Prescription CRUD Operations
@router.post("/", response_model=PrescriptionSchema)
async def create_prescription(
    prescription_data: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a new prescription"""
    # Create prescription
    db_prescription = Prescription(
        user_id=current_user.id,
        **prescription_data.dict()
    )
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return PrescriptionSchema.model_validate(db_prescription)

@router.get("/", response_model=List[PrescriptionSchema])
async def get_prescriptions(
    status: Optional[PrescriptionStatus] = Query(None, description="Filter by status"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get prescriptions with optional filtering"""
    query = db.query(Prescription)
    
    # Apply filters based on user role
    if current_user.role in [UserRole.CUSTOMER]:
        # Customers can only see their own prescriptions
        query = query.filter(Prescription.user_id == current_user.id)
    elif user_id:
        # Admins can filter by user_id
        query = query.filter(Prescription.user_id == user_id)
    
    # Apply status filter
    if status:
        query = query.filter(Prescription.status == status)
    
    # Apply pagination
    prescriptions = query.offset(offset).limit(limit).all()
    return [PrescriptionSchema.model_validate(p) for p in prescriptions]

@router.get("/{prescription_id}", response_model=PrescriptionSchema)
async def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific prescription by ID"""
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    # Check access permissions
    if current_user.role == UserRole.CUSTOMER and prescription.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return PrescriptionSchema.model_validate(prescription)

@router.put("/{prescription_id}", response_model=PrescriptionSchema)
async def update_prescription(
    prescription_id: int,
    prescription_data: PrescriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a prescription (Admin only)"""
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    # Update prescription fields
    update_data = prescription_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prescription, field, value)
    
    db.commit()
    db.refresh(prescription)
    return PrescriptionSchema.model_validate(prescription)

@router.delete("/{prescription_id}")
async def delete_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a prescription (Owner or Admin only)"""
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.CUSTOMER and prescription.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db.delete(prescription)
    db.commit()
    
    return {"message": "Prescription deleted successfully"}

# Prescription Verification (Admin only)
@router.post("/{prescription_id}/verify", response_model=PrescriptionSchema)
async def verify_prescription(
    prescription_id: int,
    verification_data: PrescriptionVerification,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Verify a prescription (Admin only)"""
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    # Update verification details
    prescription.status = verification_data.status
    prescription.verification_notes = verification_data.verification_notes
    prescription.extracted_medicines = verification_data.extracted_medicines
    prescription.verified_by = current_user.id
    prescription.verified_at = datetime.utcnow()
    
    db.commit()
    db.refresh(prescription)
    return PrescriptionSchema.model_validate(prescription)

# Get user's prescriptions
@router.get("/user/me", response_model=List[PrescriptionSchema])
async def get_my_prescriptions(
    status: Optional[PrescriptionStatus] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's prescriptions"""
    query = db.query(Prescription).filter(Prescription.user_id == current_user.id)
    
    # Apply status filter
    if status:
        query = query.filter(Prescription.status == status)
    
    # Apply pagination
    prescriptions = query.offset(offset).limit(limit).all()
    return [PrescriptionSchema.model_validate(p) for p in prescriptions]

# Get pending prescriptions (Admin only)
@router.get("/admin/pending", response_model=List[PrescriptionSchema])
async def get_pending_prescriptions(
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all pending prescriptions (Admin only)"""
    prescriptions = db.query(Prescription).filter(
        Prescription.status == PrescriptionStatus.PENDING
    ).offset(offset).limit(limit).all()
    
    return [PrescriptionSchema.model_validate(p) for p in prescriptions]

# File Upload Endpoint
@router.post("/upload", response_model=PrescriptionSchema)
async def upload_prescription_file(
    file: UploadFile = File(..., description="Prescription image file"),
    doctor_name: Optional[str] = None,
    hospital_name: Optional[str] = None,
    prescription_date: Optional[datetime] = None,
    expiry_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload prescription file and create prescription record"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Check file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: JPEG, PNG, GIF, PDF"
        )
    
    # Check file size (max 10MB)
    file_size = 0
    file_content = b""
    for chunk in file.file:
        file_content += chunk
        file_size += len(chunk)
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size: 10MB"
            )
    
    try:
        # Upload to Cloudinary
        upload_result = await cloudinary_service.upload_prescription(
            file_content, file.filename, current_user.id
        )
        
        # Create prescription record
        prescription_data = PrescriptionCreate(
            file_url=upload_result["url"],
            file_name=file.filename,
            file_size=upload_result["file_size"],
            doctor_name=doctor_name,
            hospital_name=hospital_name,
            prescription_date=prescription_date,
            expiry_date=expiry_date
        )
        
        db_prescription = Prescription(
            user_id=current_user.id,
            **prescription_data.dict()
        )
        db.add(db_prescription)
        db.commit()
        db.refresh(db_prescription)
        
        return PrescriptionSchema.model_validate(db_prescription)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload prescription: {str(e)}"
        ) 
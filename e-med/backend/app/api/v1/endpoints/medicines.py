from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User, UserRole
from app.models.medicine import Medicine, Category, MedicineAlternative
from app.schemas.medicine import (
    MedicineCreate, MedicineUpdate, Medicine as MedicineSchema, MedicineSearch,
    CategoryCreate, CategoryUpdate, Category as CategorySchema,
    MedicineAlternativeCreate, MedicineAlternative as MedicineAlternativeSchema, StockUpdate
)

router = APIRouter()

# Helper function to check if user is admin
def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.PHARMACY_ADMIN, UserRole.SYSTEM_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Medicine CRUD Operations
@router.post("/", response_model=MedicineSchema)
async def create_medicine(
    medicine_data: MedicineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new medicine (Admin only)"""
    # Check if category exists if provided
    if medicine_data.category_id:
        category = db.query(Category).filter(Category.id == medicine_data.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    
    db_medicine = Medicine(**medicine_data.dict())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return MedicineSchema.model_validate(db_medicine)

@router.get("/", response_model=List[MedicineSchema])
async def get_medicines(
    search: Optional[str] = Query(None, description="Search term for medicine name or generic name"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    prescription_required: Optional[bool] = Query(None, description="Filter by prescription requirement"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    db: Session = Depends(get_db)
):
    """Get all medicines with optional filtering"""
    query = db.query(Medicine)
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Medicine.name.like(search_term)) |
            (Medicine.generic_name.like(search_term)) |
            (Medicine.description.like(search_term))
        )
    
    # Apply category filter
    if category_id:
        query = query.filter(Medicine.category_id == category_id)
    
    # Apply price filters
    if min_price is not None:
        query = query.filter(Medicine.price >= min_price)
    if max_price is not None:
        query = query.filter(Medicine.price <= max_price)
    
    # Apply prescription filter
    if prescription_required is not None:
        query = query.filter(Medicine.prescription_required == prescription_required)
    
    # Apply stock filter
    if in_stock is not None:
        if in_stock:
            query = query.filter(Medicine.stock_quantity > 0)
        else:
            query = query.filter(Medicine.stock_quantity == 0)
    
    # Apply pagination
    medicines = query.offset(offset).limit(limit).all()
    return [MedicineSchema.model_validate(m) for m in medicines]

@router.get("/{medicine_id}", response_model=MedicineSchema)
async def get_medicine(
    medicine_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific medicine by ID"""
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found"
        )
    
    return MedicineSchema.model_validate(medicine)

@router.put("/{medicine_id}", response_model=MedicineSchema)
async def update_medicine(
    medicine_id: int,
    medicine_data: MedicineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update a medicine (Admin only)"""
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found"
        )
    
    # Check if category exists if provided
    if medicine_data.category_id:
        category = db.query(Category).filter(Category.id == medicine_data.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    
    # Update medicine fields
    update_data = medicine_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(medicine, field, value)
    
    db.commit()
    db.refresh(medicine)
    return MedicineSchema.model_validate(medicine)

@router.delete("/{medicine_id}")
async def delete_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete a medicine (Admin only) - Soft delete"""
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found"
        )
    
    # Soft delete
    medicine.is_active = False
    db.commit()
    
    return {"message": "Medicine deleted successfully"}

@router.patch("/{medicine_id}/stock", response_model=MedicineSchema)
async def update_stock(
    medicine_id: int,
    stock_data: StockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update medicine stock (Admin only)"""
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found"
        )
    
    # Update stock based on operation
    if stock_data.operation == "add":
        medicine.stock_quantity += stock_data.quantity
    elif stock_data.operation == "subtract":
        if medicine.stock_quantity < stock_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock to subtract"
            )
        medicine.stock_quantity -= stock_data.quantity
    elif stock_data.operation == "set":
        medicine.stock_quantity = stock_data.quantity
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid operation. Use 'add', 'subtract', or 'set'"
        )
    
    # Ensure stock doesn't go negative
    if medicine.stock_quantity < 0:
        medicine.stock_quantity = 0
    
    db.commit()
    db.refresh(medicine)
    return MedicineSchema.model_validate(medicine)

@router.get("/{medicine_id}/alternatives", response_model=List[MedicineSchema])
async def get_medicine_alternatives(
    medicine_id: int,
    db: Session = Depends(get_db)
):
    """Get alternative medicines for a specific medicine"""
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found"
        )
    
    # Get alternatives through the MedicineAlternative model
    alternatives = db.query(Medicine).join(
        MedicineAlternative, Medicine.id == MedicineAlternative.alternative_medicine_id
    ).filter(
        MedicineAlternative.medicine_id == medicine_id
    ).all()
    
    return [MedicineSchema.model_validate(m) for m in alternatives]

# Category CRUD Operations
@router.post("/categories/", response_model=CategorySchema)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new category (Admin only)"""
    # Check if category name already exists
    existing_category = db.query(Category).filter(Category.name == category_data.name).first()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    db_category = Category(**category_data.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return CategorySchema.model_validate(db_category)

@router.get("/categories/", response_model=List[CategorySchema])
async def get_categories(
    db: Session = Depends(get_db)
):
    """Get all categories"""
    categories = db.query(Category).all()
    return [CategorySchema.model_validate(cat) for cat in categories]

@router.get("/categories/{category_id}", response_model=CategorySchema)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific category by ID"""
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return CategorySchema.model_validate(category)

@router.put("/categories/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update a category (Admin only)"""
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Update category fields
    update_data = category_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    return CategorySchema.model_validate(category)

@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete a category (Admin only) - Soft delete"""
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check if category has medicines
    medicines_count = db.query(Medicine).filter(Medicine.category_id == category_id).count()
    if medicines_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category with {medicines_count} medicines. Move medicines to another category first."
        )
    
    # Soft delete
    category.is_active = False
    db.commit()
    
    return {"message": "Category deleted successfully"} 
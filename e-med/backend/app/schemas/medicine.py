from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class Category(CategoryBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Medicine Schemas
class MedicineBase(BaseModel):
    name: str
    generic_name: Optional[str] = None
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    prescription_required: bool = False
    price: float
    stock_quantity: int = 0
    min_stock_level: int = 10
    category_id: Optional[int] = None

class MedicineCreate(MedicineBase):
    pass

class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    generic_name: Optional[str] = None
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    prescription_required: Optional[bool] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    min_stock_level: Optional[int] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None

class Medicine(MedicineBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[Category] = None

    class Config:
        from_attributes = True

# Medicine Alternative Schema
class MedicineAlternativeBase(BaseModel):
    alternative_medicine_id: int
    reason: Optional[str] = None

class MedicineAlternativeCreate(MedicineAlternativeBase):
    pass

class MedicineAlternative(MedicineAlternativeBase):
    id: int
    medicine_id: int
    created_at: datetime
    alternative_medicine: Medicine

    class Config:
        from_attributes = True

# Search and Filter Schemas
class MedicineSearch(BaseModel):
    search_term: Optional[str] = None
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    prescription_required: Optional[bool] = None
    in_stock: Optional[bool] = None
    limit: int = 20
    offset: int = 0

# Stock Update Schema
class StockUpdate(BaseModel):
    quantity: int
    operation: str  # "add", "subtract", "set" 
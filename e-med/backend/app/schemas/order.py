from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"

class OrderType(str, Enum):
    NORMAL = "normal"
    EMERGENCY = "emergency"
    PRESCRIPTION = "prescription"

# Order Item Schemas
class OrderItemBase(BaseModel):
    medicine_id: int
    quantity: int = Field(..., gt=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    unit_price: float
    total_price: float
    medicine_name: Optional[str] = None

    class Config:
        from_attributes = True

# Order Schemas
class OrderBase(BaseModel):
    delivery_address: str
    delivery_instructions: Optional[str] = None
    is_emergency: bool = False
    emergency_reason: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]
    prescription_ids: Optional[List[int]] = None

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    delivery_address: Optional[str] = None
    delivery_instructions: Optional[str] = None
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None

class Order(OrderBase):
    id: int
    order_number: str
    user_id: int
    delivery_partner_id: Optional[int] = None
    status: OrderStatus
    order_type: OrderType
    
    # Pricing
    subtotal: float
    delivery_fee: float
    emergency_fee: float
    total_amount: float
    
    # Delivery details
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relationships
    items: List[OrderItem] = []
    
    class Config:
        from_attributes = True

# Order Search Schema
class OrderSearch(BaseModel):
    status: Optional[OrderStatus] = None
    order_type: Optional[OrderType] = None
    user_id: Optional[int] = None
    is_emergency: Optional[bool] = None
    limit: int = 20
    offset: int = 0

# Cart Schemas
class CartItemBase(BaseModel):
    medicine_id: int
    quantity: int = Field(..., gt=0)

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)

class CartItem(CartItemBase):
    id: int
    user_id: int
    medicine_name: Optional[str] = None
    medicine_price: Optional[float] = None
    total_price: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Order Status Update Schema
class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    notes: Optional[str] = None 
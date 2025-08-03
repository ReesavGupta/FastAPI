from enum import Enum
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, computed_field, model_validator
import re


class FoodCategory(str, Enum):
    APPETIZER = "appetizer"
    MAIN_COURSE = "main_course"
    DESSERT = "dessert"
    BEVERAGE = "beverage"
    SALAD = "salad"


class FoodItem(BaseModel):
    id: Optional[int] = Field(None, description="Auto-generated unique identifier")
    name: str = Field(..., min_length=3, max_length=100, description="Name of the food item")
    description: str = Field(..., min_length=10, max_length=500, description="Description of the food item")
    category: FoodCategory = Field(..., description="Category of the food item")
    price: Decimal = Field(..., gt=0, decimal_places=2, description="Price of the food item")
    is_available: bool = Field(True, description="Whether the item is available")
    preparation_time: int = Field(..., ge=1, le=120, description="Preparation time in minutes")
    ingredients: List[str] = Field(..., min_length=1, description="List of ingredients")
    calories: Optional[int] = Field(None, gt=0, description="Calories per serving")
    is_vegetarian: bool = Field(False, description="Whether the item is vegetarian")
    is_spicy: bool = Field(False, description="Whether the item is spicy")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('Name should only contain letters and spaces')
        return v

    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v < Decimal('1.00') or v > Decimal('100.00'):
            raise ValueError('Price should be between $1.00 and $100.00')
        return v

    @model_validator(mode='after')
    def validate_model(self):
        # Validate spicy constraint for desserts and beverages
        if self.is_spicy and self.category in [FoodCategory.DESSERT, FoodCategory.BEVERAGE]:
            raise ValueError('Desserts and beverages cannot be marked as spicy')

        # Validate vegetarian calorie constraint
        if self.calories is not None and self.is_vegetarian and self.calories >= 800:
            raise ValueError('Vegetarian items should have calories < 800')

        # Validate beverage preparation time
        if self.category == FoodCategory.BEVERAGE and self.preparation_time > 10:
            raise ValueError('Preparation time for beverages should be ≤ 10 minutes')

        return self

    @computed_field
    @property
    def price_category(self) -> str:
        if self.price < Decimal('10.00'):
            return "Budget"
        elif self.price <= Decimal('25.00'):
            return "Mid-range"
        else:
            return "Premium"

    @computed_field
    @property
    def dietary_info(self) -> List[str]:
        info = []
        if self.is_vegetarian:
            info.append("Vegetarian")
        if self.is_spicy:
            info.append("Spicy")
        return info

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


# Order Management Models

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    READY = "ready"
    DELIVERED = "delivered"


class OrderItem(BaseModel):
    """Simple nested model for items in order"""
    menu_item_id: int = Field(..., gt=0, description="ID of the menu item")
    menu_item_name: str = Field(..., min_length=1, max_length=100, description="Name of the menu item for easy access")
    quantity: int = Field(..., gt=0, le=10, description="Quantity of the item")
    unit_price: Decimal = Field(..., gt=0, max_digits=6, decimal_places=2, description="Price per unit")

    @computed_field
    @property
    def item_total(self) -> Decimal:
        """Calculate total price for this order item"""
        return self.quantity * self.unit_price

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class Customer(BaseModel):
    """Simple nested customer model"""
    name: str = Field(..., min_length=2, max_length=50, description="Customer name")
    phone: str = Field(..., pattern=r'^\d{10}$', description="10-digit phone number")

    @field_validator('name')
    @classmethod
    def validate_customer_name(cls, v):
        if not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('Customer name should only contain letters and spaces')
        return v


class Order(BaseModel):
    """Main order model with nested customer and order items"""
    id: Optional[int] = Field(None, description="Auto-generated unique identifier")
    customer: Customer = Field(..., description="Customer information")
    items: List[OrderItem] = Field(..., min_length=1, description="List of ordered items")
    status: OrderStatus = Field(OrderStatus.PENDING, description="Current order status")
    order_date: datetime = Field(default_factory=datetime.now, description="When the order was placed")
    special_instructions: Optional[str] = Field(None, max_length=500, description="Special instructions for the order")

    @computed_field
    @property
    def subtotal(self) -> Decimal:
        """Calculate subtotal of all items"""
        return sum(item.item_total for item in self.items)

    @computed_field
    @property
    def total_items(self) -> int:
        """Calculate total number of items"""
        return sum(item.quantity for item in self.items)

    @computed_field
    @property
    def estimated_prep_time(self) -> int:
        """Estimate total preparation time (max of all items)"""
        # This would need menu item data in a real implementation
        # For now, return a simple estimate based on number of items
        return max(15, self.total_items * 5)

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


# Response Models

class FoodItemResponse(BaseModel):
    """Response model for food items"""
    id: int
    name: str
    description: str
    category: FoodCategory
    price: Decimal
    is_available: bool
    preparation_time: int
    ingredients: List[str]
    calories: Optional[int]
    is_vegetarian: bool
    is_spicy: bool
    price_category: str
    dietary_info: List[str]

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class OrderResponse(BaseModel):
    """Response model for detailed order information"""
    id: int
    customer: Customer
    items: List[OrderItem]
    status: OrderStatus
    order_date: datetime
    special_instructions: Optional[str]
    subtotal: Decimal
    total_items: int
    estimated_prep_time: int

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class OrderSummaryResponse(BaseModel):
    """Response model for order listings"""
    id: int
    customer_name: str
    customer_phone: str
    status: OrderStatus
    order_date: datetime
    subtotal: Decimal
    total_items: int

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class OrderStatusUpdate(BaseModel):
    """Model for updating order status"""
    status: OrderStatus = Field(..., description="New order status")


class ErrorResponse(BaseModel):
    """Response model for error messages"""
    detail: str
    error_type: Optional[str] = None

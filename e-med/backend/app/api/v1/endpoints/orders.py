from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User, UserRole
from app.models.order import Order, OrderItem, OrderPrescription, OrderStatus, OrderType
from app.models.medicine import Medicine
from app.models.prescription import Prescription
from app.schemas.order import (
    OrderCreate, OrderUpdate, Order as OrderSchema, OrderItem as OrderItemSchema,
    OrderSearch, OrderStatusUpdate, CartItemCreate, CartItemUpdate, CartItem as CartItemSchema
)
from app.services.notification_service import notification_service
import uuid
from datetime import datetime, timedelta

router = APIRouter()

# Helper function to check if user is admin
def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.PHARMACY_ADMIN, UserRole.SYSTEM_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Helper function to generate order number
def generate_order_number():
    return f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

# Helper function to calculate delivery fee
def calculate_delivery_fee(is_emergency: bool = False):
    base_fee = 50.0  # Base delivery fee
    emergency_multiplier = 2.0 if is_emergency else 1.0
    return base_fee * emergency_multiplier

# Order CRUD Operations
@router.post("/", response_model=OrderSchema)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new order"""
    # Validate items
    if not order_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item"
        )
    
    # Calculate order details
    subtotal = 0.0
    order_items = []
    
    for item_data in order_data.items:
        medicine = db.query(Medicine).filter(Medicine.id == item_data.medicine_id).first()
        if not medicine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medicine with ID {item_data.medicine_id} not found"
            )
        
        if medicine.stock_quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {medicine.name}. Available: {medicine.stock_quantity}"
            )
        
        item_total = medicine.price * item_data.quantity
        subtotal += item_total
        
        order_items.append({
            "medicine_id": item_data.medicine_id,
            "quantity": item_data.quantity,
            "unit_price": medicine.price,
            "total_price": item_total
        })
    
    # Calculate fees
    delivery_fee = calculate_delivery_fee(order_data.is_emergency)
    emergency_fee = 100.0 if order_data.is_emergency else 0.0
    total_amount = subtotal + delivery_fee + emergency_fee
    
    # Determine order type
    order_type = OrderType.PRESCRIPTION if order_data.prescription_ids else (
        OrderType.EMERGENCY if order_data.is_emergency else OrderType.NORMAL
    )
    
    # Create order
    db_order = Order(
        order_number=generate_order_number(),
        user_id=current_user.id,
        status=OrderStatus.PENDING,
        order_type=order_type,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        emergency_fee=emergency_fee,
        total_amount=total_amount,
        delivery_address=order_data.delivery_address,
        delivery_instructions=order_data.delivery_instructions,
        is_emergency=order_data.is_emergency,
        emergency_reason=order_data.emergency_reason,
        estimated_delivery_time=datetime.utcnow() + timedelta(minutes=30 if order_data.is_emergency else 60)
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Create order items
    for item_data in order_items:
        db_item = OrderItem(
            order_id=db_order.id,
            **item_data
        )
        db.add(db_item)
        
        # Update stock
        medicine = db.query(Medicine).filter(Medicine.id == item_data["medicine_id"]).first()
        medicine.stock_quantity -= item_data["quantity"]
    
    # Link prescriptions if provided
    if order_data.prescription_ids:
        for prescription_id in order_data.prescription_ids:
            prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
            if prescription and prescription.user_id == current_user.id:
                db_prescription_link = OrderPrescription(
                    order_id=db_order.id,
                    prescription_id=prescription_id
                )
                db.add(db_prescription_link)
    
    db.commit()
    db.refresh(db_order)
    return OrderSchema.model_validate(db_order)

@router.get("/", response_model=List[OrderSchema])
async def get_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by status"),
    order_type: Optional[OrderType] = Query(None, description="Filter by order type"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    is_emergency: Optional[bool] = Query(None, description="Filter by emergency orders"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get orders with optional filtering"""
    query = db.query(Order)
    
    # Apply filters based on user role
    if current_user.role == UserRole.CUSTOMER:
        # Customers can only see their own orders
        query = query.filter(Order.user_id == current_user.id)
    elif user_id:
        # Admins can filter by user_id
        query = query.filter(Order.user_id == user_id)
    
    # Apply other filters
    if status:
        query = query.filter(Order.status == status)
    if order_type:
        query = query.filter(Order.order_type == order_type)
    if is_emergency is not None:
        query = query.filter(Order.is_emergency == is_emergency)
    
    # Apply pagination
    orders = query.offset(offset).limit(limit).all()
    return [OrderSchema.model_validate(o) for o in orders]

@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific order by ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check access permissions
    if current_user.role == UserRole.CUSTOMER and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return OrderSchema.model_validate(order)

@router.put("/{order_id}", response_model=OrderSchema)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update an order (Admin only)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update order fields
    update_data = order_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    return OrderSchema.model_validate(order)

@router.delete("/{order_id}")
async def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel an order (Owner or Admin only)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.CUSTOMER and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if order can be cancelled
    if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be cancelled in current status"
        )
    
    # Cancel order
    order.status = OrderStatus.CANCELLED
    
    # Restore stock
    for item in order.items:
        medicine = db.query(Medicine).filter(Medicine.id == item.medicine_id).first()
        if medicine:
            medicine.stock_quantity += item.quantity
    
    db.commit()
    
    return {"message": "Order cancelled successfully"}

# Order Status Management
@router.patch("/{order_id}/status", response_model=OrderSchema)
async def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update order status (Admin only)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update status
    order.status = status_data.status
    
    # Set delivery time if delivered
    if status_data.status == OrderStatus.DELIVERED:
        order.actual_delivery_time = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    # Send real-time notification
    try:
        await notification_service.send_order_status_update(
            user_id=order.user_id,
            order_id=order_id,
            status=status_data.status.value,
            details={
                "notes": status_data.notes,
                "updated_by": current_user.full_name
            }
        )
    except Exception as e:
        # Log error but don't fail the request
        print(f"Failed to send notification: {e}")
    
    return OrderSchema.model_validate(order)

# Get user's orders
@router.get("/user/me", response_model=List[OrderSchema])
async def get_my_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's orders"""
    query = db.query(Order).filter(Order.user_id == current_user.id)
    
    # Apply status filter
    if status:
        query = query.filter(Order.status == status)
    
    # Apply pagination
    orders = query.offset(offset).limit(limit).all()
    return [OrderSchema.model_validate(o) for o in orders]

# Get pending orders (Admin only)
@router.get("/admin/pending", response_model=List[OrderSchema])
async def get_pending_orders(
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all pending orders (Admin only)"""
    orders = db.query(Order).filter(
        Order.status == OrderStatus.PENDING
    ).offset(offset).limit(limit).all()
    
    return [OrderSchema.model_validate(o) for o in orders] 
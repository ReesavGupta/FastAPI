from fastapi import FastAPI, HTTPException, status, Query, Path
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
from decimal import Decimal
from pydantic import ValidationError
from models import (
    FoodItem, FoodCategory, Order, OrderStatus, OrderItem, Customer,
    FoodItemResponse, OrderResponse, OrderSummaryResponse, OrderStatusUpdate, ErrorResponse
)

app = FastAPI(
    title="Restaurant Ordering System",
    description="API for managing restaurant menu and orders with nested models",
    version="2.0.0"
)

# In-memory databases
menu_db: Dict[int, FoodItem] = {}
orders_db: Dict[int, Order] = {}

# Auto-incrementing IDs
next_menu_id = 1
next_order_id = 1


def get_next_menu_id() -> int:
    global next_menu_id
    current_id = next_menu_id
    next_menu_id += 1
    return current_id


def get_next_order_id() -> int:
    global next_order_id
    current_id = next_order_id
    next_order_id += 1
    return current_id


# Custom exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc), "error_type": "ValidationError"}
    )


@app.get("/", summary="Welcome endpoint")
async def root():
    return {"message": "Welcome to Restaurant Ordering System with Nested Models"}


@app.get("/menu", response_model=List[FoodItem], summary="Get all menu items")
async def get_all_menu_items():
    """Get all menu items from the restaurant menu."""
    return list(menu_db.values())


@app.get("/menu/{item_id}", response_model=FoodItem, summary="Get specific menu item")
async def get_menu_item(item_id: int):
    """Get a specific menu item by its ID."""
    if item_id not in menu_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item with ID {item_id} not found"
        )
    return menu_db[item_id]


@app.post("/menu", response_model=FoodItem, status_code=status.HTTP_201_CREATED, summary="Add new menu item")
async def add_menu_item(food_item: FoodItem):
    """Add a new menu item to the restaurant menu (staff only)."""
    # Generate new ID
    new_id = get_next_menu_id()
    food_item.id = new_id

    # Store in database
    menu_db[new_id] = food_item

    return food_item


@app.put("/menu/{item_id}", response_model=FoodItem, summary="Update existing menu item")
async def update_menu_item(item_id: int, food_item: FoodItem):
    """Update an existing menu item."""
    if item_id not in menu_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item with ID {item_id} not found"
        )
    
    # Keep the original ID
    food_item.id = item_id
    menu_db[item_id] = food_item
    
    return food_item


@app.delete("/menu/{item_id}", summary="Remove menu item")
async def delete_menu_item(item_id: int):
    """Remove a menu item from the restaurant menu."""
    if item_id not in menu_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item with ID {item_id} not found"
        )
    
    deleted_item = menu_db.pop(item_id)
    return {"message": f"Menu item '{deleted_item.name}' has been removed from the menu"}


@app.get("/menu/category/{category}", response_model=List[FoodItem], summary="Get items by category")
async def get_items_by_category(category: FoodCategory):
    """Get all menu items belonging to a specific category."""
    items = [item for item in menu_db.values() if item.category == category]
    return items


# ORDER MANAGEMENT ENDPOINTS

@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, summary="Create new order")
async def create_order(order: Order):
    """Create a new customer order with nested items and customer info."""
    try:
        # Validate that all menu items exist and are available
        for item in order.items:
            if item.menu_item_id not in menu_db:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu item with ID {item.menu_item_id} not found"
                )

            menu_item = menu_db[item.menu_item_id]
            if not menu_item.is_available:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Menu item '{menu_item.name}' is not available"
                )

            # Ensure the item name and price match the menu
            if item.menu_item_name != menu_item.name:
                item.menu_item_name = menu_item.name
            if item.unit_price != menu_item.price:
                item.unit_price = menu_item.price

        # Generate new order ID
        new_id = get_next_order_id()
        order.id = new_id

        # Store in database
        orders_db[new_id] = order

        return order

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )


@app.get("/orders", response_model=List[OrderSummaryResponse], summary="Get all orders")
async def get_all_orders(
    status_filter: Optional[OrderStatus] = Query(None, description="Filter orders by status")
):
    """Get all orders with optional status filtering."""
    orders = list(orders_db.values())

    if status_filter:
        orders = [order for order in orders if order.status == status_filter]

    # Convert to summary response
    order_summaries = []
    for order in orders:
        summary = OrderSummaryResponse(
            id=order.id,
            customer_name=order.customer.name,
            customer_phone=order.customer.phone,
            status=order.status,
            order_date=order.order_date,
            subtotal=order.subtotal,
            total_items=order.total_items
        )
        order_summaries.append(summary)

    return order_summaries


@app.get("/orders/{order_id}", response_model=OrderResponse, summary="Get specific order details")
async def get_order(order_id: int = Path(..., gt=0, description="Order ID")):
    """Get detailed information about a specific order."""
    if order_id not in orders_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )

    return orders_db[order_id]


@app.put("/orders/{order_id}/status", response_model=OrderResponse, summary="Update order status")
async def update_order_status(
    order_id: int = Path(..., gt=0, description="Order ID"),
    status_update: OrderStatusUpdate = ...
):
    """Update the status of an existing order."""
    if order_id not in orders_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )

    order = orders_db[order_id]

    # Validate status transition (simple validation)
    current_status = order.status
    new_status = status_update.status

    # Define valid status transitions
    valid_transitions = {
        OrderStatus.PENDING: [OrderStatus.CONFIRMED],
        OrderStatus.CONFIRMED: [OrderStatus.READY],
        OrderStatus.READY: [OrderStatus.DELIVERED],
        OrderStatus.DELIVERED: []  # Final state
    }

    if new_status not in valid_transitions.get(current_status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {current_status} to {new_status}"
        )

    # Update the status
    order.status = new_status
    orders_db[order_id] = order

    return order


# Health check endpoint
@app.get("/health", summary="Health check")
async def health_check():
    return {
        "status": "healthy",
        "total_menu_items": len(menu_db),
        "total_orders": len(orders_db)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

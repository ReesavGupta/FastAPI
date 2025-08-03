# Restaurant Ordering System with Nested Models

A comprehensive FastAPI-based restaurant ordering system demonstrating nested Pydantic models and relationships.

## Features

### Menu Management
- **Complete CRUD Operations**: Create, Read, Update, Delete menu items
- **Advanced Validation**: Custom Pydantic validators for business rules
- **Category Management**: Filter items by food categories
- **Computed Properties**: Automatic price categorization and dietary information

### Order Management (NEW!)
- **Nested Models**: Customer and OrderItem models embedded in Order
- **Order Creation**: Create orders with customer info and multiple items
- **Status Tracking**: Track orders through pending → confirmed → ready → delivered
- **Business Logic**: Validate menu item availability and pricing
- **Computed Totals**: Automatic calculation of subtotals and item counts

### Technical Features
- **Comprehensive Error Handling**: Detailed validation messages
- **Response Models**: Separate models for different API scenarios
- **Nested Validation**: Validation cascades through nested structures
- **JSON Serialization**: Automatic handling of nested model serialization

## Project Structure

```
restaurant/
├── main.py              # FastAPI application with menu and order endpoints
├── models.py            # Pydantic models including nested Order models
├── test_data.py         # Sample menu data and validation tests
├── order_test_data.py   # Sample order data and nested model tests
├── api_test.py          # Comprehensive API testing script
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

1. Navigate to the restaurant directory:
```bash
cd restaurant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the FastAPI server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Menu Management
- `GET /menu` - Get all menu items
- `GET /menu/{item_id}` - Get specific menu item
- `POST /menu` - Add new menu item (staff only)
- `PUT /menu/{item_id}` - Update existing menu item
- `DELETE /menu/{item_id}` - Remove menu item from menu
- `GET /menu/category/{category}` - Get items by category

### Order Management (NEW!)
- `POST /orders` - Create new order with nested customer and items
- `GET /orders` - Get all orders (with optional status filtering)
- `GET /orders/{order_id}` - Get specific order details
- `PUT /orders/{order_id}/status` - Update order status

### Utility Endpoints
- `GET /` - Welcome message
- `GET /health` - Health check with menu and order counts

## Food Categories

- `appetizer` - Appetizers and starters
- `main_course` - Main dishes
- `dessert` - Desserts and sweets
- `beverage` - Drinks and beverages
- `salad` - Salads and fresh items

## Validation Rules

### Name Validation
- 3-100 characters
- Only letters and spaces allowed
- No numbers or special characters

### Price Validation
- Must be between $1.00 and $100.00
- Maximum 2 decimal places

### Category-Specific Rules
- Desserts and beverages cannot be spicy
- Beverages must have preparation time ≤ 10 minutes

### Dietary Restrictions
- Vegetarian items with calories must have < 800 calories
- At least 1 ingredient required

## Testing

Run the validation tests:
```bash
python test_data.py
```

This will test both valid data creation and various invalid scenarios.

## Sample Usage

### Adding a Menu Item
```bash
curl -X POST "http://localhost:8000/menu" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Margherita Pizza",
       "description": "Classic pizza with tomato sauce, mozzarella cheese, and fresh basil",
       "category": "main_course",
       "price": 15.99,
       "preparation_time": 20,
       "ingredients": ["pizza dough", "tomato sauce", "mozzarella", "basil", "olive oil"],
       "calories": 650,
       "is_vegetarian": true,
       "is_spicy": false
     }'
```

### Getting All Menu Items
```bash
curl -X GET "http://localhost:8000/menu"
```

### Getting Items by Category
```bash
curl -X GET "http://localhost:8000/menu/category/appetizer"
```

## Computed Properties

Each food item automatically includes:
- **Price Category**: "Budget" (<$10), "Mid-range" ($10-25), "Premium" (>$25)
- **Dietary Info**: Array of dietary flags like ["Vegetarian", "Spicy"]

## Error Handling

The API provides detailed error messages for validation failures, including:
- Field-specific validation errors
- Business rule violations
- Missing required fields
- Invalid data types

# Expense Tracker API & Web UI

This is a FastAPI application for expense tracking, featuring SQLite database integration, robust API endpoints, and a user-friendly web UI.

## Features
- **API Endpoints:**
  - `GET /expenses` — Fetch all expenses (supports date range filtering)
  - `POST /expenses` — Create a new expense
  - `PUT /expenses/{expense_id}` — Update an existing expense
  - `DELETE /expenses/{expense_id}` — Delete an expense
  - `GET /expenses/category/{category}` — Filter expenses by category
  - `GET /expenses/total` — Get total expenses and breakdown by category
- **Database:**
  - Uses SQLite with SQLAlchemy ORM
  - Tables are created automatically on startup
  - Sample data is added for testing
  - Proper session management for all database operations
- **Web UI:**
  - Form to add new expenses (with amount validation)
  - Expenses displayed in a table with formatted dates and currency
  - Filter expenses by category using a dropdown
  - Shows total spending and category breakdown
  - Delete button for each expense

## Advanced Requirements
- **Data Validation:**
  - Amount must be positive
  - Category must be from a predefined list
- **Query Parameters:**
  - Date range filtering supported via `?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- **CRUD Operations:**
  - All database operations use proper error handling and status codes (200, 201, 204, 404)
- **Response Formatting:**
  - Currency amounts are formatted properly in the UI

## Getting Started

### Prerequisites
- Python 3.7+
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### Running the Application
1. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
2. Open your browser and go to [http://localhost:8000/](http://localhost:8000/) to access the web UI.
3. API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

## API Details

### Expense Object
```json
{
  "id": 1,
  "amount": 25.50,
  "category": "Food",
  "description": "Lunch",
  "date": "2025-07-10"
}
```

### Endpoints
- **GET /expenses**
  - Returns a list of all expenses. Supports optional date range filtering.
- **POST /expenses**
  - Creates a new expense. Requires JSON body with `amount`, `category`, `description`, and `date` (optional).
  - Returns the created expense with status code 201.
- **PUT /expenses/{expense_id}**
  - Updates an existing expense. Returns the updated expense or 404 if not found.
- **DELETE /expenses/{expense_id}**
  - Deletes an expense by ID. Returns 204 on success or 404 if not found.
- **GET /expenses/category/{category}**
  - Returns expenses filtered by category.
- **GET /expenses/total**
  - Returns total spending and breakdown by category.

## Error Handling
- Returns 404 for invalid expense IDs or categories.
- Returns appropriate status codes for each operation (200, 201, 204, 404).

## Notes
- Sample data is added automatically on first run.
- All data is stored in `expenses.db` (SQLite).
- The UI is a simple HTML page served from the `static/` directory.

---

**Track your expenses easily and efficiently!** 
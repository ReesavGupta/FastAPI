# Task Management API & Web UI

This is a simple FastAPI application for basic task management, featuring in-memory storage and a minimal web UI.

## Features
- **API Endpoints:**
  - `GET /tasks` — Fetch all tasks
  - `POST /tasks` — Create a new task
  - `PUT /tasks/{task_id}` — Update an existing task
  - `DELETE /tasks/{task_id}` — Delete a task
- **In-Memory Storage:**
  - Tasks are stored in a Python list (no database required)
  - Task IDs are generated using a counter or the `len()` function
- **Web UI:**
  - Displays all tasks in a list
  - Form to create new tasks
  - Buttons to mark tasks as complete/incomplete
  - Delete buttons for each task

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

### Task Object
```json
{
  "id": 1,
  "title": "Sample Task",
  "completed": false
}
```

### Endpoints
- **GET /tasks**
  - Returns a list of all tasks.
- **POST /tasks**
  - Creates a new task. Requires a JSON body with a `title` field.
  - Returns the created task with status code 201.
- **PUT /tasks/{task_id}**
  - Updates an existing task (title and/or completed status).
  - Returns the updated task or 404 if not found.
- **DELETE /tasks/{task_id}**
  - Deletes a task by ID. Returns 204 on success or 404 if not found.

## Error Handling
- Returns 404 for invalid task IDs.
- Returns appropriate status codes for each operation (200, 201, 204, 404).

## Notes
- All data is lost when the server restarts (in-memory storage).
- The UI is a simple HTML page served from the `static/` directory.

---

**Enjoy managing your tasks!** 
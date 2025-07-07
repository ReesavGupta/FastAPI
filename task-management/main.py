from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os

app = FastAPI()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for tasks
class Task(BaseModel):
    id: int
    title: str
    completed: bool = False

tasks: List[Task] = []

# Helper to find task by id
def get_task(task_id: int) -> Optional[Task]:
    for task in tasks:
        if task.id == task_id:
            return task
    return None

@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return tasks

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: Task):
    if get_task(task.id):
        raise HTTPException(status_code=400, detail="Task ID already exists.")
    tasks.append(task)
    return task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated: Task):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    task.title = updated.title
    task.completed = updated.completed
    return task

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    global tasks
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    tasks = [t for t in tasks if t.id != task_id]
    return

# Serve static files (UI)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    with open(os.path.join(static_dir, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 
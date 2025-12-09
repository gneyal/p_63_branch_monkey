"""Task API endpoints."""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: int = 0


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None


# In-memory storage for demo
tasks_db = []
next_id = 1


@router.get("/")
async def list_tasks():
    """Get all tasks."""
    return {"tasks": tasks_db}


@router.post("/")
async def create_task(task: TaskCreate):
    """Create a new task."""
    global next_id
    new_task = {
        "id": next_id,
        "title": task.title,
        "description": task.description,
        "status": "todo",
        "priority": task.priority,
    }
    tasks_db.append(new_task)
    next_id += 1
    return new_task


@router.put("/{task_id}")
async def update_task(task_id: int, task: TaskUpdate):
    """Update a task."""
    for t in tasks_db:
        if t["id"] == task_id:
            if task.title is not None:
                t["title"] = task.title
            if task.description is not None:
                t["description"] = task.description
            if task.status is not None:
                t["status"] = task.status
            if task.priority is not None:
                t["priority"] = task.priority
            return t
    raise HTTPException(status_code=404, detail="Task not found")


@router.delete("/{task_id}")
async def delete_task(task_id: int):
    """Delete a task."""
    global tasks_db
    tasks_db = [t for t in tasks_db if t["id"] != task_id]
    return {"success": True}

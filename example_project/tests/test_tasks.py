"""Tests for task API."""
import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_list_tasks_empty():
    """Test listing tasks when empty."""
    response = client.get("/api/tasks/")
    assert response.status_code == 200
    assert response.json()["tasks"] == []


def test_create_task():
    """Test creating a new task."""
    task_data = {"title": "Test Task", "description": "A test task"}
    response = client.post("/api/tasks/", json=task_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"


def test_update_task():
    """Test updating a task."""
    # Create a task first
    task_data = {"title": "Original Title"}
    create_response = client.post("/api/tasks/", json=task_data)
    task_id = create_response.json()["id"]

    # Update the task
    update_data = {"title": "Updated Title", "status": "in_progress"}
    response = client.put(f"/api/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["status"] == "in_progress"


def test_delete_task():
    """Test deleting a task."""
    # Create a task first
    task_data = {"title": "Task to Delete"}
    create_response = client.post("/api/tasks/", json=task_data)
    task_id = create_response.json()["id"]

    # Delete the task
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True

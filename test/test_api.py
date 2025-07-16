# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.models.task_model import Task

client = TestClient(app)

def test_create_task():
    response = client.post("/api/tasks", json={
        "function_name": "test_func",
        "args": {"x": 1},
        "priority": 1
    })
    assert response.status_code == 200
    task = response.json()
    assert task["function_name"] == "test_func"
    assert task["priority"] == 1
    assert task["status"] == "pending"

def test_get_task():
    # 先创建任务
    response = client.post("/api/tasks", json={
        "function_name": "test_func",
        "args": {"x": 1},
        "priority": 1
    })
    task_id = response.json()["id"]
    
    # 查询任务
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id

def test_get_task_not_found():
    response = client.get("/api/tasks/invalid_id")
    assert response.status_code == 404
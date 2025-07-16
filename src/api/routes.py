# src/api/routes.py
from fastapi import APIRouter, HTTPException
from src.models.task_model import Task, TaskStatus
from src.scheduler.mlqf import MLFQScheduler
from pydantic import BaseModel
from typing import List

router = APIRouter()
scheduler = MLFQScheduler()

class TaskCreate(BaseModel):
    function_name: str
    args: dict
    priority: int = 1

@router.post("/tasks", response_model=Task)
async def create_task(task_data: TaskCreate):
    """
    创建新任务并添加到调度器。
    """
    if task_data.priority not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="优先级必须为1、2或3")
    task = Task(function_name=task_data.function_name, args=task_data.args, priority=task_data.priority)
    await scheduler.add_task(task)
    return task

@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """
    查询指定任务的状态。
    """
    try:
        return scheduler.get_task_status(task_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/tasks", response_model=List[Task])
async def list_tasks():
    """
    获取所有任务列表。
    """
    tasks = []
    for priority in scheduler.queues:
        tasks.extend(scheduler.queues[priority])
    tasks.extend(scheduler.running_tasks.values())
    return tasks

@router.delete("/tasks/{task_id}")
async def cancel_task(task_id: str):
    """
    取消指定任务。
    """
    try:
        for priority in scheduler.queues:
            for task in list(scheduler.queues[priority]):
                if task.id == task_id and task.status == TaskStatus.PENDING:
                    scheduler.queues[priority].remove(task)
                    return {"message": f"Task {task_id} cancelled"}
        raise ValueError(f"Task {task_id} not found or not cancellable")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
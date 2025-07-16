import pytest
from src.scheduler.mlqf import MLFQScheduler
from src.models.task_model import Task

@pytest.mark.asyncio
async def test_scheduler_add_task():
    scheduler = MLFQScheduler()
    task = Task(function_name="test_func", args={"x": 1}, priority=1)
    scheduler.add_task(task)
    assert len(scheduler.queues[1]) == 1
    assert scheduler.queues[1][0].id == task.id
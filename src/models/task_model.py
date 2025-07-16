from pydantic import BaseModel
from enum import Enum
from datetime import datetime
import uuid

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Task(BaseModel):
    id: str = str(uuid.uuid4())
    function_name: str
    args: dict
    priority: int = 1  # 1最高，3最低
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = datetime.utcnow()
    result: dict = {}
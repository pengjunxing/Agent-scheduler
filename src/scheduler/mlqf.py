# src/scheduler/mlqf.py
from collections import deque
import asyncio
from src.models.task_model import Task, TaskStatus
from src.utils.logger import setup_logger
from src.utils.config import load_config
from src.scheduler.task import process_task

logger = setup_logger()
config = load_config()

class MLFQScheduler:
    def __init__(self):
        self.queues = {1: deque(), 2: deque(), 3: deque()}  # 优先级队列
        self.time_slice = {1: 0.5, 2: 1.0, 3: 2.0}  # 时间片（秒）
        self.running_tasks = {}  # 正在运行的任务
        self.max_concurrent = config["SCHEDULER_MAX_CONCURRENT"]
        self.lock = asyncio.Lock()

    async def add_task(self, task: Task):
        """
        添加任务到对应优先级队列。
        """
        async with self.lock:
            self.queues[task.priority].append(task)
            logger.info(f"Task {task.id} added to queue {task.priority}")

    async def run(self):
        """
        调度器主循环，处理任务并实现抢占式调度。
        """
        while True:
            async with self.lock:
                if len(self.running_tasks) >= self.max_concurrent:
                    await asyncio.sleep(0.1)
                    continue
                
                for priority in sorted(self.queues.keys()):
                    queue = self.queues[priority]
                    if queue:
                        task = queue.popleft()
                        task.status = TaskStatus.RUNNING
                        self.running_tasks[task.id] = task
                        logger.info(f"Running task {task.id} with priority {priority}")
                        
                        # 异步执行任务
                        asyncio.create_task(self._execute_task(task, priority))
                        break  # 处理一个任务后检查更高优先级
            await asyncio.sleep(0.1)

    async def _execute_task(self, task: Task, priority: int):
        """
        执行任务并处理抢占逻辑。
        """
        try:
            await asyncio.wait_for(
                process_task(task),
                timeout=self.time_slice[priority]
            )
        except asyncio.TimeoutError:
            logger.warning(f"Task {task.id} timed out, requeueing")
            async with self.lock:
                task.status = TaskStatus.PENDING
                if priority < 3:  # 降低优先级
                    task.priority += 1
                self.queues[task.priority].append(task)
        except Exception as e:
            logger.error(f"Task {task.id} failed: {str(e)}")
            task.status = TaskStatus.FAILED
            task.result = {"error": str(e)}
        finally:
            async with self.lock:
                self.running_tasks.pop(task.id, None)

    def get_task_status(self, task_id: str) -> Task:
        """
        查询任务状态。
        """
        for priority in self.queues:
            for task in self.queues[priority]:
                if task.id == task_id:
                    return task
        if task_id in self.running_tasks:
            return self.running_tasks[task_id]
        raise ValueError(f"Task {task_id} not found")
# src/scheduler/task.py
from src.models.task_model import Task, TaskStatus
from src.tools.openai_tools import execute_tool
from src.utils.logger import setup_logger

logger = setup_logger()

async def process_task(task: Task) -> None:
    """
    处理单个任务，调用工具并更新任务状态。
    """
    try:
        logger.info(f"Processing task {task.id} with function {task.function_name}")
        result = await execute_tool(task.function_name, task.args)
        task.result = result
        task.status = TaskStatus.COMPLETED
        logger.info(f"Task {task.id} completed with result: {result}")
    except Exception as e:
        task.status = TaskStatus.FAILED
        task.result = {"error": str(e)}
        logger.error(f"Task {task.id} failed: {str(e)}")
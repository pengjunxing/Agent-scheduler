from fastapi import FastAPI
from src.api.routes import router
from src.scheduler.mlqf import MLFQScheduler
from src.utils.logger import setup_logger
import asyncio

app = FastAPI(title="LLM Agent Scheduler")
logger = setup_logger()

# 初始化调度器
scheduler = MLFQScheduler()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting scheduler...")
    asyncio.create_task(scheduler.run())  # 启动调度器

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
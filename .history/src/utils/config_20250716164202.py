# src/utils/config.py
import os
from dotenv import load_dotenv
from pathlib import Path

def load_config():
    """
    加载配置文件和环境变量。
    返回包含所有配置的字典。
    """
    # 加载 .env 文件
    env_path = Path(__file__).resolve().parent.parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    
    config = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        "SCHEDULER_MAX_CONCURRENT": int(os.getenv("SCHEDULER_MAX_CONCURRENT", 10))
    }
    
    # 验证必要配置
    if not config["OPENAI_API_KEY"]:
        raise ValueError("OPENAI_API_KEY 未在 .env 文件中配置")
    
    return config
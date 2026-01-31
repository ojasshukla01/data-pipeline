"""
Logging utility for the pipeline
"""
import os
import sys
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# Configure loguru
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/pipeline.log")

# Create logs directory if it doesn't exist
Path(LOG_FILE_PATH).parent.mkdir(parents=True, exist_ok=True)

# Remove default handler
logger.remove()

# Add console handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=LOG_LEVEL,
    colorize=True
)

# Add file handler
logger.add(
    LOG_FILE_PATH,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
    level=LOG_LEVEL,
    rotation="10 MB",
    retention="7 days",
    compression="zip"
)

def get_logger(name: str = __name__):
    """Get a logger instance"""
    return logger.bind(name=name)

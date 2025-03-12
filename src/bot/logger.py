import os
import sys
from loguru import logger

# Define logs directory inside data folder
LOGS_DIR = os.path.join('src', 'data', 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Configure logger
def setup_logger():
    """Configure the logger with appropriate settings"""
    log_file = os.path.join(LOGS_DIR, "bot_{time}.log")
    
    # Remove default handler
    logger.remove()
    
    # Add console handler with INFO level
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Add file handler with rotation settings
    logger.add(
        log_file,
        rotation="10 MB",
        compression="zip",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        retention=10
    )
    
    return logger
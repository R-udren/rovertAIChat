import sys
from pathlib import Path

from loguru import logger

# Configure Loguru
LOG_LEVEL = "DEBUG"
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

# Remove default logger
logger.remove()

# Add console logger
logger.add(
    sys.stderr,
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    colorize=True,
)

# Add file logger - create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

logger.add(
    logs_dir / "app.log",
    rotation="10 MB",
    retention="1 week",
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    compression="zip",
)

# Export logger to be used across the application
app_logger = logger

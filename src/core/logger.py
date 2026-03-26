import logging
from logging.handlers import RotatingFileHandler
import os

from src.core.settings import settings

log_level_str = getattr(settings, "LOG_LEVEL", "INFO")
log_level = getattr(logging, log_level_str.upper() if isinstance(log_level_str, str) else "INFO", logging.INFO)

# Create logs directory with fallback
log_dir = getattr(settings, "SYS_LOG_PATH", "./logs")
try:
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
except Exception:
    log_dir = "./logs"
    os.makedirs(log_dir, exist_ok=True)

# Define format
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# Setup StreamHandler (Console)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

handlers = [stream_handler]
try:
    file_handler = RotatingFileHandler(
        filename=f"{log_dir}/app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    handlers.append(file_handler)
except Exception:
    pass

logging.basicConfig(
    level=log_level,
    handlers=handlers,
    force=True
)

logger = logging.getLogger("app")


def setup_log(name: str):
    global logger
    logger = logging.getLogger(name)
    return logger


def setup_app_level_logger(name: str) -> logging.Logger:
    """Compatible helper for existing modules across the codebase."""
    return logging.getLogger(name)


__all__ = ["logger", "setup_log", "setup_app_level_logger", "handlers", "formatter"]

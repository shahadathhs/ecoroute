"""
Logging Configuration Module
"""
import sys
from pathlib import Path
from loguru import logger as _logger

from app.core.config import settings


def setup_logger() -> None:
    """Configure application logger with loguru."""
    # Remove default handler
    _logger.remove()

    # Console handler
    _logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
        backtrace=True,
        diagnose=settings.debug,
    )

    # File handler
    log_path = Path(settings.log_file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    _logger.add(
        settings.log_file_path,
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        compression="zip",
        backtrace=True,
        diagnose=settings.debug,
        enqueue=True,  # Async logging
    )

    # Intercept standard logging
    import logging

    class InterceptHandler(logging.Handler):
        """Intercept standard logging messages."""

        def emit(self, record: logging.LogRecord) -> None:
            """Emit log record."""
            try:
                level = _logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            _logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)


# Initialize logger
logger = _logger

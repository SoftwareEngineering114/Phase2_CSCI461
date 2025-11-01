"""
Logging configuration respecting $LOG_FILE and $LOG_LEVEL environment variables.
"""
from __future__ import annotations

import logging
import os
from typing import List


def configure_logging() -> None:
    """
    Configure logging based on environment variables.
    
    Environment variables:
        LOG_FILE: Path to log file. If not set, logs to stderr.
        LOG_LEVEL: Logging verbosity level
            0 = CRITICAL (silent)
            1 = INFO
            2+ = DEBUG
    """
    log_file = os.environ.get("LOG_FILE")
    level = int(os.environ.get("LOG_LEVEL", "0"))
    
    # Map level to logging constant
    if level >= 2:
        log_level = logging.DEBUG
    elif level == 1:
        log_level = logging.INFO
    else:
        log_level = logging.CRITICAL
    
    # Setup handlers
    handlers: List[logging.Handler] = []
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    else:
        handlers.append(logging.StreamHandler())
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format="%(asctime)s %(levelname)s %(message)s"
    )


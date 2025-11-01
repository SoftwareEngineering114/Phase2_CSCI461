"""
Logging configuration respecting $LOG_FILE and $LOG_LEVEL environment variables.
"""
from __future__ import annotations

import logging
import os
from typing import Dict


# Cache for loggers to prevent duplicate handlers
_loggers: Dict[str, logging.Logger] = {}


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger for the given name.
    
    Reads environment variables:
    - LOG_FILE: Path to log file (default: ./registry.log if LOG_LEVEL > 0)
    - LOG_LEVEL: Logging verbosity level
        0 = No logging (NullHandler)
        1 = INFO
        2 = DEBUG
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
        
    Note:
        Repeated calls with the same name return the cached logger
        to prevent duplicate handlers.
    """
    # Return cached logger if it exists
    if name in _loggers:
        return _loggers[name]
    
    # Read environment variables
    log_file = os.environ.get("LOG_FILE")
    log_level_int = int(os.environ.get("LOG_LEVEL", "0"))
    
    # Create logger
    logger = logging.getLogger(name)
    logger.handlers.clear()  # Clear any existing handlers
    logger.propagate = False  # Don't propagate to root logger
    
    if log_level_int == 0:
        # No logging - use NullHandler
        logger.addHandler(logging.NullHandler())
        logger.setLevel(logging.CRITICAL + 1)  # Effectively disable
    else:
        # Map log level
        if log_level_int >= 2:
            level = logging.DEBUG
        else:  # log_level_int == 1
            level = logging.INFO
        
        logger.setLevel(level)
        
        # Determine log file path
        if log_file:
            # Use specified log file
            log_path = log_file
            # Create directory if it doesn't exist
            log_dir = os.path.dirname(log_path)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
        else:
            # Default to ./registry.log
            log_path = "./registry.log"
        
        # Create file handler
        handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
        handler.setLevel(level)
        
        # Create formatter with timestamp + level + message
        formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
    
    # Cache the logger
    _loggers[name] = logger
    
    return logger


def configure_logging() -> None:
    """
    Configure logging based on environment variables.
    
    Environment variables:
        LOG_FILE: Path to log file. If not set, logs to ./registry.log (if enabled)
        LOG_LEVEL: Logging verbosity level
            0 = No logging (silent)
            1 = INFO
            2+ = DEBUG
            
    Note:
        This is a legacy function for backward compatibility.
        Prefer using get_logger(__name__) directly.
    """
    # Just create a root logger
    get_logger("registry")

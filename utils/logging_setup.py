"""
Logging configuration utilities for MedClarify application.
"""

import os
import logging
from datetime import datetime
from typing import Optional

def setup_logger(name: str, level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up and configure a logger with file and console handlers.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_default_log_path() -> str:
    """
    Get default log file path based on current date.
    
    Returns:
        Log file path string
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return os.path.join(log_dir, f"medclarify_{current_date}.log")
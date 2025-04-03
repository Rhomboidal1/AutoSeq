# log_service.py - Logging utilities
import logging as py_logging  # Rename the import to avoid confusion
import os
from datetime import datetime
import sys
import logging as py_logging

# Add the project's root directory to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))  # Go up two levels
sys.path.append(project_root)

def setup_logger(name, log_dir="logs", level=py_logging.INFO):  # Use py_logging here
    """
    Set up a logger with file and console handlers
    
    Args:
        name: Logger name (typically module name)
        log_dir: Directory to store log files
        level: Logging level
        
    Returns:
        Configured logger
    """
    # Create logger
    logger = py_logging.getLogger(name)  # Use py_logging here
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
        
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create file handler with timestamp
    log_file = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = py_logging.FileHandler(log_file)  # Use py_logging here
    file_handler.setLevel(level)
    
    # Create console handler
    console_handler = py_logging.StreamHandler()  # Use py_logging here
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = py_logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Use py_logging here
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

class LoggingService:
    """Service for standardized logging across the application"""
    
    def __init__(self, module_name, log_dir="logs"):
        """Initialize logging service for a module"""
        self.logger = setup_logger(module_name, log_dir)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message)

    def close(self):
        """Close all handlers to release file locks"""
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)
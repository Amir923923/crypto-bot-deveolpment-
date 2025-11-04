"""
Logging configuration for the crypto trading bot.
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional


class BotLogger:
    """Custom logger for the trading bot."""
    
    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        """Initialize logger with specified level and output."""
        # Remove default handler
        logger.remove()
        
        # Add console handler with colors
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level=log_level,
            colorize=True
        )
        
        # Add file handler if specified
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.add(
                log_file,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
                level=log_level,
                rotation="10 MB",  # Rotate log file when it reaches 10MB
                retention="1 week",  # Keep logs for 1 week
                compression="zip"  # Compress rotated logs
            )
        
        self.logger = logger
    
    def get_logger(self):
        """Get the logger instance."""
        return self.logger


# Global logger instance
_logger_instance = None


def setup_logger(log_level: str = "INFO", log_file: Optional[str] = None):
    """Setup global logger instance."""
    global _logger_instance
    _logger_instance = BotLogger(log_level, log_file)
    return _logger_instance.get_logger()


def get_logger():
    """Get or create global logger instance."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = BotLogger()
    return _logger_instance.get_logger()

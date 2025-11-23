"""Logging configuration for all services."""
import logging
from pathlib import Path


def setup_logger(
    name: str = None,
    level: int = logging.INFO,
    log_file: str = None,
    log_dir: str = "logs"
):
    """
    Set up logging configuration.
    
    Args:
        name: Logger name (None for root logger)
        level: Logging level (default: INFO)
        log_file: Log file name (default: None, uses name if provided)
        log_dir: Directory for log files (default: 'logs')
    """
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        full_log_path = log_path / (log_file or f"{name or 'app'}.log")
    else:
        full_log_path = None
    
    # Set up logging configuration
    handlers = [logging.StreamHandler()]
    
    if full_log_path:
        file_handler = logging.FileHandler(full_log_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        )
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=handlers
    )
    
    logger = logging.getLogger(name)
    logger.info(f"Logger initialized: {name or 'root'}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)

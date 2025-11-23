"""Logging configuration for all services."""
import logging
from pathlib import Path
from rich.logging import RichHandler
from rich.console import Console


def setup_logger(
    name: str = None,
    level: int = logging.INFO,
    log_file: str = None,
    log_dir: str = "logs",
    use_rich: bool = True
):
    """
    Set up logging configuration with rich formatting.
    
    Args:
        name: Logger name (None for root logger)
        level: Logging level (default: INFO)
        log_file: Log file name (default: None, uses name if provided)
        log_dir: Directory for log files (default: 'logs')
        use_rich: Use rich formatting for console output (default: True)
    """
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        full_log_path = log_path / (log_file or f"{name or 'app'}.log")
    else:
        full_log_path = None
    
    # Set up logging handlers
    handlers = []
    
    # Console handler with rich formatting
    if use_rich:
        console_handler = RichHandler(
            console=Console(stderr=True),
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            show_time=True,
            show_level=True,
            show_path=False
        )
        console_handler.setLevel(level)
        handlers.append(console_handler)
    else:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        )
        handlers.append(console_handler)
    
    # File handler (no rich formatting for files)
    if full_log_path:
        file_handler = logging.FileHandler(full_log_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        )
        handlers.append(file_handler)
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(message)s',  # Rich handler formats its own
        datefmt='[%X]',
        handlers=handlers
    )
    
    logger = logging.getLogger(name)
    logger.info(f"Logger initialized: {name or 'root'}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)

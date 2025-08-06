#!/usr/bin/env python3
"""
ProcOS Centralized Logging Configuration

Provides consistent logging setup across all ProcOS services with both console and file output.
Logs are organized in the logs/ directory structure.

Author: ProcOS Development Team
License: MIT
"""

import logging
import os
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


def setup_logging(
    service_name: str,
    log_category: str = "services",
    console_level: str = None,
    file_level: str = None
) -> logging.Logger:
    """
    Setup logging for a ProcOS service with both console and file output.
    
    Args:
        service_name: Name of the service (e.g., "ai_worker", "generic_worker", "kernel")
        log_category: Category for organizing logs ("services", "workers", "kernel", "tests")
        console_level: Console log level (defaults to LOG_LEVEL env var or INFO)
        file_level: File log level (defaults to DEBUG for comprehensive file logs)
    
    Returns:
        Configured logger instance
    """
    
    # Determine log levels
    if console_level is None:
        console_level = os.getenv('LOG_LEVEL', 'INFO')
    if file_level is None:
        file_level = os.getenv('FILE_LOG_LEVEL', 'DEBUG')
    
    # Create logs directory structure
    logs_dir = Path("logs") / log_category
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Define log file path
    log_file = logs_dir / f"{service_name}.log"
    
    # Setup console for rich output
    console = Console()
    
    # Create logger
    logger = logging.getLogger(f"procos.{service_name}")
    logger.setLevel(logging.DEBUG)  # Set to lowest level, handlers will filter
    
    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler with Rich formatting
    console_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        show_path=False,
        show_time=True
    )
    console_handler.setLevel(getattr(logging, console_level.upper()))
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    
    # File handler with detailed formatting
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(getattr(logging, file_level.upper()))
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Prevent propagation to root logger to avoid duplicates
    logger.propagate = False
    
    logger.info(f"📝 Logging initialized for {service_name}")
    logger.debug(f"Log file: {log_file}")
    
    return logger


def get_test_logger(test_name: str) -> logging.Logger:
    """Get a logger for test scripts."""
    return setup_logging(test_name, "tests")


def get_service_logger(service_name: str) -> logging.Logger:
    """Get a logger for service components."""
    return setup_logging(service_name, "services")


def get_worker_logger(worker_name: str) -> logging.Logger:
    """Get a logger for worker processes."""
    return setup_logging(worker_name, "workers")


def get_kernel_logger(component_name: str = "kernel") -> logging.Logger:
    """Get a logger for kernel components."""
    return setup_logging(component_name, "kernel")


# Convenience function for backward compatibility
def setup_rich_logging(service_name: str, log_category: str = "services") -> logging.Logger:
    """Backward compatibility wrapper."""
    return setup_logging(service_name, log_category)
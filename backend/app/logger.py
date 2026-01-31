import structlog
import logging
import sys
import os

def configure_logger():
    # Configure standard logging to output to both stdout and a file
    handlers = [logging.StreamHandler(sys.stdout)]
    
    # Add File Handler
    log_file = "backend_logs.json"
    file_handler = logging.FileHandler(log_file)
    handlers.append(file_handler)

    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
        handlers=handlers
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()

logger = configure_logger()

import structlog
import logging
import sys
import os

# Custom processor to format error logs as incidents
def format_incident(logger, method_name, event_dict):
    if method_name in ("error", "critical"):
        event_dict["type"] = "incident"
        event_dict["service"] = "incident-backend"
        
        # Rename event -> incident_type
        if "event" in event_dict:
            event_dict["incident_type"] = event_dict.pop("event")
            
        # Rename level -> severity
        if "level" in event_dict:
            event_dict["severity"] = event_dict.pop("level")
            
    return event_dict

def configure_logger():
    # Configure standard logging to output to stdout
    handlers = [logging.StreamHandler(sys.stdout)]


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
            format_incident,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()

logger = configure_logger()

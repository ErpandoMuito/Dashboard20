import logging
import sys
from pythonjsonlogger import jsonlogger
from .config import settings

def setup_logging():
    """Configura logging estruturado"""
    log_level = getattr(logging, settings.log_level.upper())
    
    # Remove handlers existentes
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    
    # Configura handler
    handler = logging.StreamHandler(sys.stdout)
    
    if settings.log_format == "json":
        # JSON format para produção
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        # Formato simples para desenvolvimento
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    handler.setFormatter(formatter)
    
    # Configura root logger
    root.setLevel(log_level)
    root.addHandler(handler)
    
    # Silencia logs verbosos
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
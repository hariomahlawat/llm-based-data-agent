import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import settings

LOG_FILE = Path(__file__).resolve().parents[2] / "logs" / "app.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

_logger = None

def get_logger(name: str = "data_agent"):
    global _logger
    if _logger is None:
        _logger = logging.getLogger(name)
        _logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
        handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        handler.setFormatter(fmt)
        _logger.addHandler(handler)
    return _logger



import traceback
from functools import wraps
from typing import Callable, Any, Tuple
from .logger import get_logger

logger = get_logger()

def safe_ui(fn: Callable[..., Any]) -> Callable[..., Tuple[bool, Any, str]]:
    """
    Decorator for UI-callable functions.
    Returns: (ok, result, tb_text)
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            res = fn(*args, **kwargs)
            return True, res, ""
        except Exception as e:  # broad, but we log + show friendly msg
            tb = traceback.format_exc()
            logger.error("Error in %s: %s\n%s", fn.__name__, e, tb)
            return False, None, tb
    return wrapper


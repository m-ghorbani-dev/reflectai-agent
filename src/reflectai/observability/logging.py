"""Application logger setup without logging prompt contents by default."""
import logging
import os

def get_logger(name: str = "reflectai") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(os.getenv("REFLECTAI_LOG_LEVEL", "INFO").upper())
    logger.propagate = False
    return logger

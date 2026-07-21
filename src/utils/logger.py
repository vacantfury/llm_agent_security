"""Minimal local logging helper — stdlib-only (no colorlog dependency).

Local replacement for the sibling repo's `src.utils.logger`; the import path is
identical, so every `from src.utils.logger import get_logger` in the copied encoder
package resolves here with no per-file edits.
"""

import logging

DEFAULT_LOGGER_NAME = "llm_agent_security"


def get_logger(name: str = DEFAULT_LOGGER_NAME, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("[%(levelname)s] %(asctime)s %(name)s - %(message)s", "%H:%M:%S")
        )
        logger.addHandler(handler)
    return logger

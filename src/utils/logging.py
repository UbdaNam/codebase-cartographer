"""Structured logging helpers for Stage 0."""

from __future__ import annotations

import json
import logging
from pathlib import Path


def create_logger(log_path: Path, run_id: str) -> logging.Logger:
    """Create a logger that writes JSON lines to the run log."""

    logger = logging.getLogger(f"cartography.{run_id}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def log_event(logger: logging.Logger, **payload: object) -> None:
    """Write a single structured event."""

    logger.info(json.dumps(payload, sort_keys=True, default=str))

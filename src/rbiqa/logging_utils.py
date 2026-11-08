"""Logging setup shared by the CLI and later pipeline stages."""

from __future__ import annotations

import logging
import os

from rich.logging import RichHandler


def setup_logging(level: str | None = None) -> None:
    resolved = (level or os.getenv("RBIQA_LOG_LEVEL") or "INFO").upper()
    logging.basicConfig(
        level=resolved,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
        force=True,
    )
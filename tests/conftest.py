"""Pytest session setup for sandbox-friendly temp handling."""

from __future__ import annotations

import os
import shutil
import tempfile
from uuid import uuid4
from pathlib import Path

import pytest


def _configure_repo_local_temp() -> None:
    temp_root = Path(__file__).resolve().parent.parent / ".test-tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    temp_path = str(temp_root)
    os.environ["TMP"] = temp_path
    os.environ["TEMP"] = temp_path
    os.environ["TMPDIR"] = temp_path
    tempfile.tempdir = temp_path


_configure_repo_local_temp()


@pytest.fixture
def tmp_path() -> Path:
    path = Path(tempfile.gettempdir()) / f"case-{uuid4().hex[:8]}"
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)

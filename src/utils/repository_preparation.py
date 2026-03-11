"""Repository input resolution and preparation helpers for Stage 3."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlparse

from src.config import AppSettings
from src.models.repository_input import (
    PreparedRepository,
    PreparationStatus,
    RepositoryInput,
    RepositoryReuseMode,
)


def prepare_repository(repository_target: str | Path, settings: AppSettings) -> PreparedRepository:
    """Resolve a local path or Git URL into a prepared local repository root."""

    repo_input = RepositoryInput.from_raw(repository_target)
    artifact_root = settings.resolved_artifact_dir()
    repos_root = artifact_root / settings.repos_dir_name
    repos_root.mkdir(parents=True, exist_ok=True)

    if repo_input.input_kind.value == "local_path":
        local_path = Path(repo_input.raw_input).resolve()
        if not local_path.is_dir():
            raise ValueError(f"local repository path is not a directory: {local_path}")
        return PreparedRepository(
            repository_input=repo_input,
            local_repo_path=str(local_path),
            preparation_status=PreparationStatus.READY,
            reuse_mode=RepositoryReuseMode.DIRECT,
        )

    clone_dir = repos_root / repo_input.canonical_identity.replace(":", "-")
    if clone_dir.exists() and (clone_dir / ".git").exists():
        return PreparedRepository(
            repository_input=repo_input,
            local_repo_path=str(clone_dir.resolve()),
            preparation_status=PreparationStatus.READY,
            reuse_mode=RepositoryReuseMode.REUSED_CLONE,
            source_url=repo_input.raw_input,
        )

    if clone_dir.exists():
        shutil.rmtree(clone_dir, ignore_errors=True)

    _run_git_clone(repo_input.raw_input, clone_dir)
    return PreparedRepository(
        repository_input=repo_input,
        local_repo_path=str(clone_dir.resolve()),
        preparation_status=PreparationStatus.READY,
        reuse_mode=RepositoryReuseMode.FRESH_CLONE,
        source_url=repo_input.raw_input,
    )


def _run_git_clone(source_url: str, clone_dir: Path) -> None:
    parsed = urlparse(source_url)
    if parsed.scheme == "file":
        source_path = Path(unquote(parsed.path.lstrip("/"))).resolve()
        shutil.copytree(source_path, clone_dir)
        return

    git_binary = shutil.which("git")
    if git_binary is None:
        raise RuntimeError("git is required for Git URL repository preparation")

    command = [git_binary, "clone", "--depth", "1", source_url, str(clone_dir)]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        stderr = result.stderr.strip() or "unknown git clone error"
        raise RuntimeError(f"repository clone failed: {stderr}")

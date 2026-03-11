from pathlib import Path

import pytest

from src.models.repository_input import (
    PreparedRepository,
    PreparationStatus,
    RepositoryInput,
    RepositoryInputKind,
    RepositoryReuseMode,
)


def test_repository_input_detects_local_path(tmp_path: Path) -> None:
    repo_input = RepositoryInput.from_raw(tmp_path)

    assert repo_input.input_kind == RepositoryInputKind.LOCAL_PATH
    assert repo_input.raw_input == str(tmp_path.resolve())
    assert repo_input.canonical_identity is not None


def test_repository_input_detects_git_url() -> None:
    repo_input = RepositoryInput.from_raw("https://github.com/example/repo.git")

    assert repo_input.input_kind == RepositoryInputKind.GIT_URL
    assert repo_input.canonical_identity is not None


def test_repository_input_rejects_unknown_target() -> None:
    with pytest.raises(ValueError):
        RepositoryInput.from_raw("not-a-repo-target")


def test_prepared_repository_normalizes_local_repo_path(tmp_path: Path) -> None:
    prepared = PreparedRepository(
        repository_input=RepositoryInput.from_raw(tmp_path),
        local_repo_path=str(tmp_path),
        preparation_status=PreparationStatus.READY,
        reuse_mode=RepositoryReuseMode.DIRECT,
    )

    assert prepared.local_repo_path.replace("\\", "/") == str(tmp_path.resolve()).replace("\\", "/")

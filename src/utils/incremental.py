"""Incremental baseline discovery and reuse heuristics."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import subprocess

from src.models.archivist import IncrementalBaseline
from src.models.run_metadata import RunStatus, RunSummary


@dataclass(slots=True)
class IncrementalPlan:
    """Reuse/regeneration decision surface for the current run."""

    current_commit: str | None
    previous_run_id: str | None = None
    previous_commit: str | None = None
    changed_files: list[str] = field(default_factory=list)
    reuse_inventory: bool = False
    reuse_structural: bool = False
    reuse_surveyor: bool = False
    reuse_hydrologist: bool = False
    reuse_semanticist: bool = False
    reuse_archivist: bool = False
    warning_codes: list[str] = field(default_factory=list)


def git_head_commit(repo_root: Path) -> str | None:
    """Return the current HEAD commit when available."""

    return _git(repo_root, "rev-parse", "HEAD")


def changed_files_since(repo_root: Path, previous_commit: str | None, current_commit: str | None) -> list[str]:
    """Return changed files between two commits or an empty list when unavailable."""

    if not previous_commit or not current_commit or previous_commit == current_commit:
        return []
    output = _git(repo_root, "diff", "--name-only", previous_commit, current_commit)
    if output is None:
        return []
    return sorted(path.replace("\\", "/") for path in output.splitlines() if path.strip())


def load_latest_successful_summary(runs_dir: Path) -> tuple[RunSummary | None, Path | None]:
    """Load the latest completed or partial run summary from the runs directory."""

    candidates: list[tuple[float, Path]] = []
    for run_dir in runs_dir.iterdir() if runs_dir.exists() else []:
        if not run_dir.is_dir():
            continue
        summary_path = run_dir / "run_summary.json"
        if not summary_path.exists():
            continue
        candidates.append((summary_path.stat().st_mtime, summary_path))
    for _, summary_path in sorted(candidates, key=lambda item: item[0], reverse=True):
        summary = RunSummary.model_validate_json(summary_path.read_text(encoding="utf-8"))
        if summary.status in {RunStatus.COMPLETED, RunStatus.PARTIAL}:
            return summary, summary_path.parent
    return None, None


def load_incremental_baseline(path: Path) -> IncrementalBaseline | None:
    """Load a persisted incremental baseline when present."""

    if not path.exists():
        return None
    return IncrementalBaseline.model_validate_json(path.read_text(encoding="utf-8"))


def write_incremental_baseline(path: Path, baseline: IncrementalBaseline) -> None:
    """Persist the incremental baseline deterministically."""

    path.write_text(json.dumps(baseline.model_dump(mode="json"), indent=2, sort_keys=True), encoding="utf-8")


def plan_incremental_refresh(repo_root: Path, runs_dir: Path) -> IncrementalPlan:
    """Compute a bounded reuse plan based on the latest successful run."""

    current_commit = git_head_commit(repo_root)
    latest_summary, latest_run_dir = load_latest_successful_summary(runs_dir)
    if latest_summary is None or latest_run_dir is None:
        return IncrementalPlan(current_commit=current_commit)

    baseline = load_incremental_baseline(latest_run_dir / "incremental_baseline.json")
    previous_commit = baseline.commit_hash if baseline else None
    changed = changed_files_since(repo_root, previous_commit, current_commit)
    plan = IncrementalPlan(
        current_commit=current_commit,
        previous_run_id=latest_summary.run_id,
        previous_commit=previous_commit,
        changed_files=changed,
    )
    if previous_commit and current_commit and previous_commit == current_commit:
        plan.reuse_inventory = True
        plan.reuse_structural = True
        plan.reuse_surveyor = True
        plan.reuse_hydrologist = True
        plan.reuse_semanticist = True
        plan.reuse_archivist = True
        return plan

    docs_only = changed and all(path.lower().endswith((".md", ".rst", ".txt")) for path in changed)
    data_only = changed and all(path.lower().endswith((".sql", ".yaml", ".yml")) for path in changed)

    if docs_only:
        plan.reuse_inventory = True
        plan.reuse_structural = True
        plan.reuse_surveyor = True
        plan.reuse_hydrologist = True
        plan.warning_codes.append("incremental_docs_only_refresh")
    elif data_only:
        plan.reuse_inventory = True
        plan.reuse_structural = True
        plan.reuse_surveyor = True
        plan.warning_codes.append("incremental_data_only_refresh")
    return plan


def _git(repo_root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()

import json
from pathlib import Path

from src.config import AppSettings
from src.models.run_metadata import RunStatus, RunSummary
from src.utils.artifacts import create_run_context, finalize_run, initialize_artifact_dirs


def test_artifact_directories_are_created(tmp_path: Path) -> None:
    settings = AppSettings(repo_root=tmp_path, artifact_dir=".cartography")

    directories = initialize_artifact_dirs(settings)

    assert directories["root"].exists()
    assert directories["runs"].exists()
    assert directories["cache"].exists()
    assert directories["logs"].exists()


def test_run_metadata_and_summary_are_written(tmp_path: Path) -> None:
    settings = AppSettings(repo_root=tmp_path, artifact_dir=".cartography")
    context, run_dir = create_run_context(settings, branch="test-branch")
    summary = RunSummary(
        run_id=context.run_id,
        status=RunStatus.COMPLETED,
        message="done",
        manifest_path=str(run_dir / "manifest.json"),
    )

    finalize_run(context, run_dir, summary)

    metadata = json.loads((run_dir / "run_metadata.json").read_text(encoding="utf-8"))
    output_summary = json.loads((run_dir / "run_summary.json").read_text(encoding="utf-8"))

    assert metadata["branch"] == "test-branch"
    assert output_summary["status"] == "completed"

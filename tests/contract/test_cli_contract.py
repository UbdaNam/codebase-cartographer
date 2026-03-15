from pathlib import Path

from typer.testing import CliRunner

from src.cli import app

runner = CliRunner()


def test_query_returns_structured_partial_response_without_runs(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["query", "What is this repository?"],
        env={
            "CARTOGRAPHY_REPO_ROOT": str(tmp_path),
            "CARTOGRAPHY_ARTIFACT_DIR": ".cartography",
            "CARTOGRAPHY_SEMANTIC_PROVIDER_ENABLED": "false",
        },
    )

    assert result.exit_code == 0
    assert '"partial_result_flags"' in result.stdout
    assert '"navigator_run_not_found"' in result.stdout


def test_analyze_returns_json_summary(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('hello')", encoding="utf-8")

    result = runner.invoke(app, ["analyze", "--repo", str(tmp_path)])

    assert result.exit_code == 0
    assert '"status": "completed"' in result.stdout
    assert '"module_graph_path"' in result.stdout
    assert '"codebase_md_path"' in result.stdout

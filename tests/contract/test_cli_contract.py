from pathlib import Path

from typer.testing import CliRunner

from src.cli import app

runner = CliRunner()


def test_query_is_a_stage2_stub() -> None:
    result = runner.invoke(app, ["query", "What is this repository?"])

    assert result.exit_code == 0
    assert "not implemented in Stage 2" in result.stdout


def test_analyze_returns_json_summary(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("print('hello')", encoding="utf-8")

    result = runner.invoke(app, ["analyze", "--repo", str(tmp_path)])

    assert result.exit_code == 0
    assert '"status": "completed"' in result.stdout

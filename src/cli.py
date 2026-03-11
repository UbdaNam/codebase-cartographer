"""Typer CLI for Stage 0."""

from __future__ import annotations

from pathlib import Path

import typer

from src.config import AppSettings
from src.orchestrator import Stage0Orchestrator

app = typer.Typer(help="Brownfield Cartographer Stage 0 CLI.")


@app.command()
def analyze(repo: Path = typer.Option(Path("."), "--repo", exists=True, file_okay=False)) -> None:
    """Initialize a Stage 0 analysis run."""

    settings = AppSettings(repo_root=repo.resolve())
    orchestrator = Stage0Orchestrator(settings)
    summary = orchestrator.analyze(repo)
    typer.echo(summary.model_dump_json(indent=2))


@app.command()
def query(question: str) -> None:
    """Return the Stage 0 query stub response."""

    settings = AppSettings()
    orchestrator = Stage0Orchestrator(settings)
    typer.echo(orchestrator.query(question))


if __name__ == "__main__":
    app()

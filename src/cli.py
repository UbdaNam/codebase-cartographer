"""Typer CLI for Brownfield Cartographer inventory and query flows."""

from __future__ import annotations

from pathlib import Path

import typer

from src.config import AppSettings
from src.orchestrator import CartographyOrchestrator

app = typer.Typer(help="Brownfield Cartographer CLI.")


@app.command()
def analyze(repo: Path = typer.Option(Path("."), "--repo", exists=True, file_okay=False)) -> None:
    """Initialize a Stage 2 repository inventory run."""

    settings = AppSettings(repo_root=repo.resolve())
    orchestrator = CartographyOrchestrator(settings)
    summary = orchestrator.analyze(repo)
    typer.echo(summary.model_dump_json(indent=2))


@app.command()
def query(question: str) -> None:
    """Return the Stage 2 query stub response."""

    settings = AppSettings()
    orchestrator = CartographyOrchestrator(settings)
    typer.echo(orchestrator.query(question))


if __name__ == "__main__":
    app()

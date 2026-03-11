"""Typer CLI for Brownfield Cartographer analyze and query flows."""

from __future__ import annotations

import typer

from src.config import AppSettings
from src.orchestrator import CartographyOrchestrator

app = typer.Typer(help="Brownfield Cartographer CLI.")


@app.command()
def analyze(repo: str = typer.Option(".", "--repo")) -> None:
    """Initialize a Stage 3 repository preparation and structural analysis run."""

    settings = AppSettings()
    orchestrator = CartographyOrchestrator(settings)
    summary = orchestrator.analyze(repo)
    typer.echo(summary.model_dump_json(indent=2))


@app.command()
def query(question: str) -> None:
    """Return the Stage 3 query stub response."""

    settings = AppSettings()
    orchestrator = CartographyOrchestrator(settings)
    typer.echo(orchestrator.query(question))


if __name__ == "__main__":
    app()

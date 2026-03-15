"""Typer CLI for Brownfield Cartographer analyze and query flows."""

from __future__ import annotations

import typer

from src.config import AppSettings
from src.orchestrator import CartographyOrchestrator

app = typer.Typer(help='Brownfield Cartographer CLI.')


@app.command()
def analyze(repo: str = typer.Option('.', '--repo')) -> None:
    """Run the full pipeline through Archivist."""

    settings = AppSettings()
    orchestrator = CartographyOrchestrator(settings)
    summary = orchestrator.analyze(repo)
    typer.echo(summary.model_dump_json(indent=2))


@app.command()
def query(
    question: str,
    query_type: str | None = typer.Option(None, "--query-type"),
    target_identifier: str | None = typer.Option(None, "--target"),
    direction: str | None = typer.Option(None, "--direction"),
    include_inference: bool = typer.Option(True, "--include-inference/--no-include-inference"),
    max_results: int = typer.Option(5, "--max-results"),
    run_id: str | None = typer.Option(None, "--run-id"),
) -> None:
    """Run a Navigator query against persisted artifacts, with LLM planning when enabled."""

    settings = AppSettings()
    orchestrator = CartographyOrchestrator(settings)
    typer.echo(
        orchestrator.query(
            question,
            query_type=query_type,
            target_identifier=target_identifier,
            direction=direction,
            include_inference=include_inference,
            max_results=max_results,
            run_id=run_id,
        )
    )


if __name__ == '__main__':
    app()

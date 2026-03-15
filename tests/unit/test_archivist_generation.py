from pathlib import Path

from src.agents.archivist import ArchivistAgent
from src.config import AppSettings
from src.models.artifacts import SerializationMetadata
from src.models.graph import GraphPayload, SurveySummaryPayload
from src.models.semantic import DayOneAnswersPayload, DocumentationDriftPayload, DomainMapPayload, ModuleSemanticsPayload


def _fixture_run_dir() -> Path:
    runs_root = Path("tests/fixtures/semanticist_repo/.cartography/runs")
    for run_dir in sorted(runs_root.iterdir()):
        if (run_dir / "module_semantics.json").exists() and (run_dir / "day_one_answers.json").exists():
            return run_dir
    raise AssertionError("semanticist fixture run not found")


def test_generate_codebase_md_contains_required_sections() -> None:
    run_dir = _fixture_run_dir()
    agent = ArchivistAgent(AppSettings(repo_root=Path("tests/fixtures/semanticist_repo").resolve(), semantic_provider_enabled=False))

    document = agent.generate_codebase_document(
        metadata=SerializationMetadata(run_id="run-001", artifact_dir=".cartography"),
        repo_root=Path("tests/fixtures/semanticist_repo").resolve(),
        module_graph=GraphPayload.model_validate_json((run_dir / "module_graph.json").read_text(encoding="utf-8")),
        survey_summary=SurveySummaryPayload.model_validate_json((run_dir / "survey_summary.json").read_text(encoding="utf-8")),
        lineage_graph=GraphPayload.model_validate_json((run_dir / "lineage_graph.json").read_text(encoding="utf-8")),
        module_semantics=ModuleSemanticsPayload.model_validate_json((run_dir / "module_semantics.json").read_text(encoding="utf-8")),
        documentation_drift=DocumentationDriftPayload.model_validate_json((run_dir / "documentation_drift.json").read_text(encoding="utf-8")),
        domain_map=DomainMapPayload.model_validate_json((run_dir / "domain_map.json").read_text(encoding="utf-8")),
    )
    markdown = agent.generate_CODEBASE_md(document)

    assert "## Architecture Overview" in markdown
    assert "## Critical Path" in markdown
    assert "## Data Sources & Sinks" in markdown
    assert "## Known Debt" in markdown
    assert "## Recent Change Velocity" in markdown
    assert "## Module Purpose Index" in markdown


def test_onboarding_brief_preserves_evidence_labels() -> None:
    run_dir = _fixture_run_dir()
    agent = ArchivistAgent(AppSettings(repo_root=Path("tests/fixtures/semanticist_repo").resolve(), semantic_provider_enabled=False))
    day_one_answers = DayOneAnswersPayload.model_validate_json((run_dir / "day_one_answers.json").read_text(encoding="utf-8"))

    brief = agent.generate_onboarding_brief(
        metadata=SerializationMetadata(run_id="run-001", artifact_dir=".cartography"),
        analysis_root=str(Path("tests/fixtures/semanticist_repo").resolve()),
        day_one_answers=day_one_answers,
    )
    markdown = agent.render_onboarding_brief(brief)

    assert "Observed facts:" in markdown
    assert "Inferred conclusions:" in markdown
    assert "Evidence citations:" in markdown
    assert len(brief.sections) == 5

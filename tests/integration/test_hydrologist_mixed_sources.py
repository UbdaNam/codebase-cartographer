from pathlib import Path

from src.agents.hydrologist import HydrologistAgent
from src.agents.surveyor import SurveyorAgent
from src.analyzers.repository_manifest import build_repository_manifest
from src.analyzers.tree_sitter_analyzer import TreeSitterAnalyzer
from src.config import AppSettings
from src.models.repository_input import PreparedRepository, PreparationStatus, RepositoryInput, RepositoryInputKind, RepositoryReuseMode


def _prepared_repo(path: Path) -> PreparedRepository:
    return PreparedRepository(repository_input=RepositoryInput(raw_input=str(path), input_kind=RepositoryInputKind.LOCAL_PATH), local_repo_path=str(path), preparation_status=PreparationStatus.READY, reuse_mode=RepositoryReuseMode.DIRECT)


def test_hydrologist_mixed_sources_include_sql_python_and_yaml_signals() -> None:
    repo_root = Path('tests/fixtures/hydrologist_python_repo').resolve()
    settings = AppSettings(repo_root=repo_root)
    manifest = build_repository_manifest(settings)
    prepared = _prepared_repo(repo_root)
    structural_index, _ = TreeSitterAnalyzer().analyze_manifest(prepared, manifest, run_id='run-mixed', artifact_dir='.cartography')
    module_graph, _ = SurveyorAgent(settings).analyze(prepared, manifest, structural_index, run_id='run-mixed', artifact_dir='.cartography')
    lineage_graph, lineage_summary = HydrologistAgent(settings).analyze(prepared, manifest, structural_index, module_graph, run_id='run-mixed', artifact_dir='.cartography')

    names = {node.canonical_name for node in lineage_graph.nodes}
    assert 'raw.orders' in names
    assert 'analytics.orders_enriched' in names
    assert 'data.input.orders.csv' in names
    assert lineage_summary.sql_signal_count > 0
    assert lineage_summary.python_signal_count > 0
    assert lineage_summary.yaml_signal_count > 0

from pathlib import Path

from src.agents.hydrologist import HydrologistAgent
from src.agents.surveyor import SurveyorAgent
from src.analyzers.repository_manifest import build_repository_manifest
from src.analyzers.tree_sitter_analyzer import TreeSitterAnalyzer
from src.config import AppSettings
from src.models.repository_input import PreparedRepository, PreparationStatus, RepositoryInput, RepositoryInputKind, RepositoryReuseMode


def _prepared_repo(path: Path) -> PreparedRepository:
    return PreparedRepository(repository_input=RepositoryInput(raw_input=str(path), input_kind=RepositoryInputKind.LOCAL_PATH), local_repo_path=str(path), preparation_status=PreparationStatus.READY, reuse_mode=RepositoryReuseMode.DIRECT)


def test_hydrologist_partial_pipeline_emits_warnings() -> None:
    repo_root = Path('tests/fixtures/hydrologist_partial_repo').resolve()
    settings = AppSettings(repo_root=repo_root)
    manifest = build_repository_manifest(settings)
    prepared = _prepared_repo(repo_root)
    structural_index, _ = TreeSitterAnalyzer().analyze_manifest(prepared, manifest, run_id='run-partial', artifact_dir='.cartography')
    module_graph, _ = SurveyorAgent(settings).analyze(prepared, manifest, structural_index, run_id='run-partial', artifact_dir='.cartography')
    lineage_graph, lineage_summary = HydrologistAgent(settings).analyze(prepared, manifest, structural_index, module_graph, run_id='run-partial', artifact_dir='.cartography')

    assert lineage_summary.partial_result_flags
    assert lineage_summary.warnings
    assert lineage_graph.graph_metadata['partial_result_flags']

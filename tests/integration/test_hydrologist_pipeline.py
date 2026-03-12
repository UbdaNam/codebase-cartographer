from pathlib import Path

from src.agents.hydrologist import HydrologistAgent
from src.agents.surveyor import SurveyorAgent
from src.analyzers.repository_manifest import build_repository_manifest
from src.analyzers.tree_sitter_analyzer import TreeSitterAnalyzer
from src.config import AppSettings
from src.models.repository_input import PreparedRepository, PreparationStatus, RepositoryInput, RepositoryInputKind, RepositoryReuseMode


def _prepared_repo(path: Path) -> PreparedRepository:
    return PreparedRepository(repository_input=RepositoryInput(raw_input=str(path), input_kind=RepositoryInputKind.LOCAL_PATH), local_repo_path=str(path), preparation_status=PreparationStatus.READY, reuse_mode=RepositoryReuseMode.DIRECT)


def test_hydrologist_generates_deterministic_lineage_graph_from_fixture() -> None:
    repo_root = Path('tests/fixtures/hydrologist_sql_repo').resolve()
    settings = AppSettings(repo_root=repo_root)
    manifest = build_repository_manifest(settings)
    prepared = _prepared_repo(repo_root)
    structural_index, _ = TreeSitterAnalyzer().analyze_manifest(prepared, manifest, run_id='run-1', artifact_dir='.cartography')
    module_graph, _ = SurveyorAgent(settings).analyze(prepared, manifest, structural_index, run_id='run-1', artifact_dir='.cartography')
    lineage_graph_one, lineage_summary_one = HydrologistAgent(settings).analyze(prepared, manifest, structural_index, module_graph, run_id='run-1', artifact_dir='.cartography')
    lineage_graph_two, lineage_summary_two = HydrologistAgent(settings).analyze(prepared, manifest, structural_index, module_graph, run_id='run-2', artifact_dir='.cartography')

    assert [node['canonical_name'] for node in lineage_graph_one.model_dump(mode='json')['nodes']] == [node['canonical_name'] for node in lineage_graph_two.model_dump(mode='json')['nodes']]
    assert [edge['edge_id'] for edge in lineage_graph_one.model_dump(mode='json')['edges']] == [edge['edge_id'] for edge in lineage_graph_two.model_dump(mode='json')['edges']]
    assert lineage_summary_one.dataset_count >= 2
    assert lineage_summary_one.edge_count == lineage_summary_two.edge_count

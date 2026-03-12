from src.models.graph import GraphPayload, LineageSummaryPayload


def test_lineage_summary_payload_serializes_deterministically() -> None:
    payload = LineageSummaryPayload(run_id='run-123', analysis_root='repo', dataset_count=1, transformation_count=1, edge_count=2, sql_signal_count=1, python_signal_count=0, yaml_signal_count=0, warnings=['b', 'a'], partial_result_flags=['y', 'x'], stats={'b': 2, 'a': 1})
    dumped = payload.model_dump(mode='json')
    assert dumped['warnings'] == ['a', 'b']
    assert dumped['partial_result_flags'] == ['x', 'y']
    assert dumped['stats'] == {'a': 1, 'b': 2}


def test_graph_payload_supports_lineage_nodes_and_edges() -> None:
    payload = GraphPayload(run_id='run-1')
    dumped = payload.model_dump(mode='json')
    assert dumped['nodes'] == []
    assert dumped['edges'] == []

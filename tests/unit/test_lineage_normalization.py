from src.graph.lineage import normalize_dataset_identifier
from src.utils.ids import build_dataset_id, build_transformation_id


def test_normalize_dataset_identifier_collapses_common_variants() -> None:
    assert normalize_dataset_identifier('Analytics.Orders') == 'analytics.orders'
    assert normalize_dataset_identifier('`analytics`.`orders`') == 'analytics.orders'
    assert normalize_dataset_identifier('analytics/orders') == 'analytics.orders'


def test_lineage_ids_are_stable() -> None:
    assert build_dataset_id('analytics.orders') == build_dataset_id('analytics.orders')
    assert build_transformation_id('jobs/pipeline.py', 'jobs.pipeline') == build_transformation_id('jobs/pipeline.py', 'jobs.pipeline')

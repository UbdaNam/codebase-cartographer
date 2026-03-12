from src.agents.hydrologist import HydrologistAgent
from src.config import AppSettings


def test_extract_yaml_pipeline_references() -> None:
    agent = HydrologistAgent(AppSettings())
    content = """
    sources: [raw.orders, raw.customers]
    target: analytics.orders_enriched
    """
    signals, warnings, partial = agent._extract_yaml_signals('pipelines/orders.yaml', content, None)
    roles = {(signal.dataset_name, signal.role) for signal in signals}

    assert ('raw.orders', 'input') in roles
    assert ('raw.customers', 'input') in roles
    assert ('analytics.orders_enriched', 'output') in roles
    assert partial is False
    assert not warnings

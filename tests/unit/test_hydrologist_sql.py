from src.agents.hydrologist import HydrologistAgent
from src.config import AppSettings


def test_extract_sql_lineage_handles_cte_and_output() -> None:
    agent = HydrologistAgent(AppSettings())
    sql = """
    create table analytics.orders_enriched as
    with base as (
      select * from raw.orders
    )
    select * from base join raw.customers on base.customer_id = raw.customers.id
    """
    signals, warnings, partial = agent._extract_sql_signals('models/orders.sql', sql, None)
    names = sorted({signal.dataset_name for signal in signals})
    roles = {(signal.dataset_name, signal.role) for signal in signals}

    assert 'raw.orders' in names
    assert 'raw.customers' in names
    assert ('analytics.orders_enriched', 'output') in roles
    assert partial is False
    assert not warnings

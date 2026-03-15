from src.agents.hydrologist import HydrologistAgent
from src.config import AppSettings


PYTHON_SAMPLE = """
import pandas as pd

df = pd.read_csv('data/input/orders.csv')
df.to_csv('data/output/orders_clean.csv')
report = spark.read.table('warehouse.sales')
engine.execute("INSERT INTO mart.sales SELECT * FROM warehouse.sales")
"""


def test_detect_python_ingestion_and_sql_patterns() -> None:
    agent = HydrologistAgent(AppSettings())
    signals, warnings, partial = agent._extract_python_signals('jobs/pipeline.py', PYTHON_SAMPLE, None)
    roles = {(signal.dataset_name, signal.role) for signal in signals}

    assert ('data/input/orders.csv', 'input') in roles
    assert ('data/output/orders_clean.csv', 'output') in roles
    assert ('warehouse.sales', 'input') in roles
    assert ('mart.sales', 'output') in roles
    assert partial is False
    assert not warnings


def test_python_helper_sql_name_does_not_trigger_embedded_sql_parsing() -> None:
    agent = HydrologistAgent(AppSettings())
    content = '''
def cleanup() -> None:
    """Drop tables and views from a schema."""
    grant_sql("Drop tables and views from a schema.")
'''

    signals, warnings, partial = agent._extract_python_signals('jobs/helpers.py', content, None)

    assert signals == []
    assert warnings == []
    assert partial is False

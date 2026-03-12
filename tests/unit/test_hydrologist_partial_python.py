from src.agents.hydrologist import HydrologistAgent
from src.config import AppSettings


def test_dynamic_python_sql_is_marked_partial() -> None:
    agent = HydrologistAgent(AppSettings())
    content = 'query = f"SELECT * FROM {table_name}"\nengine.execute(query)\n'
    signals, warnings, partial = agent._extract_python_signals('jobs/dynamic.py', content, None)
    assert partial is True
    assert warnings
    assert signals == []

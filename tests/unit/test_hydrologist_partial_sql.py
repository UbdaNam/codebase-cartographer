from src.agents.hydrologist import HydrologistAgent
from src.config import AppSettings


def test_malformed_sql_returns_partial_warning() -> None:
    agent = HydrologistAgent(AppSettings())
    signals, warnings, partial = agent._extract_sql_signals('broken.sql', 'select from', None)
    assert partial is True
    assert warnings
    assert isinstance(signals, list)

from src.agents.hydrologist import HydrologistAgent
from src.config import AppSettings


def test_malformed_sql_returns_partial_warning() -> None:
    agent = HydrologistAgent(AppSettings())
    signals, warnings, partial = agent._extract_sql_signals('broken.sql', 'select from', None)
    assert partial is True
    assert warnings
    assert isinstance(signals, list)


def test_command_only_sql_does_not_emit_malformed_warning(capsys) -> None:
    agent = HydrologistAgent(AppSettings())
    sql = "LOAD httpfs; CALL load_aws_credentials()"

    signals, warnings, partial = agent._extract_sql_signals('setup.sql', sql, None)
    captured = capsys.readouterr()

    assert signals == []
    assert warnings == []
    assert partial is False
    assert captured.err == ""


def test_command_prefixed_sql_keeps_lineage_and_stays_quiet(capsys) -> None:
    agent = HydrologistAgent(AppSettings())
    sql = """
    LOAD iceberg;
    CALL load_aws_credentials();
    CREATE TABLE analytics.orders AS
    SELECT * FROM raw.orders
    """

    signals, warnings, partial = agent._extract_sql_signals('models/orders.sql', sql, None)
    roles = {(signal.dataset_name, signal.role) for signal in signals}
    captured = capsys.readouterr()

    assert ('analytics.orders', 'output') in roles
    assert ('raw.orders', 'input') in roles
    assert warnings == []
    assert partial is False
    assert captured.err == ""

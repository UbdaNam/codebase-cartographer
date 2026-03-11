from src.utils.ids import stable_id


def test_stable_id_is_deterministic_for_same_parts() -> None:
    first = stable_id("file", "src/cli.py")
    second = stable_id("file", "src/cli.py")

    assert first == second
    assert first.startswith("file:")

from src.models.enums import SupportStatus
from src.models.manifest import ManifestRecord
from src.utils.language_router import LanguageRouter


def _record(path: str, language: str, support_status: SupportStatus, parse_eligible: bool = True) -> ManifestRecord:
    return ManifestRecord(
        relative_path=path,
        size_bytes=10,
        modified_time="2026-03-11T00:00:00Z",
        language=language,
        support_status=support_status,
        is_parse_eligible=parse_eligible,
        classification_source="test",
    )


def test_language_router_marks_supported_languages_as_deep_parse_eligible() -> None:
    route = LanguageRouter().route_manifest_record(_record("src/app.py", "python", SupportStatus.SUPPORTED))

    assert route.normalized_language == "python"
    assert route.parser_language == "python"
    assert route.deep_parse_eligible is True


def test_language_router_marks_partial_languages_as_non_deep_parse() -> None:
    route = LanguageRouter().route_manifest_record(_record("notes.ipynb", "notebook", SupportStatus.PARTIAL))

    assert route.support_status == SupportStatus.PARTIAL
    assert route.deep_parse_eligible is False
    assert route.notes


def test_language_router_marks_unknown_languages_as_non_deep_parse() -> None:
    route = LanguageRouter().route_manifest_record(_record("docs/readme.txt", "unknown", SupportStatus.UNSUPPORTED, False))

    assert route.deep_parse_eligible is False
    assert "no structural route defined" in route.notes

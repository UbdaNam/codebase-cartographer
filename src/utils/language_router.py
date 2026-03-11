"""Centralized language routing for structural analysis."""

from __future__ import annotations

from functools import lru_cache

from tree_sitter import Parser
from tree_sitter_language_pack import get_parser

from src.models.manifest import ManifestRecord
from src.models.structural import LanguageRoute
from src.models.enums import SupportStatus


ROUTE_TABLE = {
    "python": {"parser_language": "python", "deep_parse_eligible": True},
    "sql": {"parser_language": "sql", "deep_parse_eligible": True},
    "yaml": {"parser_language": "yaml", "deep_parse_eligible": True},
    "javascript": {"parser_language": "javascript", "deep_parse_eligible": True},
    "typescript": {"parser_language": "typescript", "deep_parse_eligible": True},
    "json": {"parser_language": None, "deep_parse_eligible": False, "note": "configuration file recognized but not structurally parsed in Stage 3"},
    "notebook": {"parser_language": None, "deep_parse_eligible": False, "note": "notebook parsing remains partial in Stage 3"},
    "shell": {"parser_language": None, "deep_parse_eligible": False, "note": "shell parsing remains partial in Stage 3"},
}


class LanguageRouter:
    """Route manifest records to parser-capable structural languages."""

    def route_manifest_record(self, record: ManifestRecord) -> LanguageRoute:
        entry = ROUTE_TABLE.get(record.language)
        if entry is None:
            return LanguageRoute(
                normalized_language=record.language,
                parser_language=None,
                support_status=record.support_status,
                deep_parse_eligible=False,
                notes=["no structural route defined"],
            )

        notes: list[str] = []
        if note := entry.get("note"):
            notes.append(note)
        notes.extend(record.notes)
        return LanguageRoute(
            normalized_language=record.language,
            parser_language=entry["parser_language"],
            support_status=record.support_status,
            deep_parse_eligible=bool(record.is_parse_eligible and entry["deep_parse_eligible"]),
            notes=notes,
        )

    @lru_cache(maxsize=None)
    def get_parser(self, parser_language: str) -> Parser:
        return get_parser(parser_language)

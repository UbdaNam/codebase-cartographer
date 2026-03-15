"""Append-only trace logging for Archivist and Navigator."""

from __future__ import annotations

import json
from pathlib import Path

from src.models.trace import TraceEvent
from src.utils.ids import canonicalize_json_value


class TraceWriter:
    """Write structured trace events to JSON Lines files."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: TraceEvent) -> TraceEvent:
        payload = canonicalize_json_value(event.model_dump(mode="json"))
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True))
            handle.write("\n")
        return event


def read_trace_events(path: Path) -> list[TraceEvent]:
    """Load a trace log when it exists."""

    if not path.exists():
        return []
    events: list[TraceEvent] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        events.append(TraceEvent.model_validate_json(stripped))
    return events

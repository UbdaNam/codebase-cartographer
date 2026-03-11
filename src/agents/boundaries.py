"""Future agent boundary declarations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentBoundary:
    name: str
    responsibility: str
    status: str = "placeholder"


DEFAULT_AGENT_BOUNDARIES = [
    AgentBoundary("Surveyor", "Repository discovery and coarse structure"),
    AgentBoundary("Hydrologist", "Data flow and lineage boundary"),
    AgentBoundary("Semanticist", "Semantic structure and meaning boundary"),
    AgentBoundary("Archivist", "Artifact persistence and retrieval boundary"),
    AgentBoundary("Navigator", "Future query interface boundary"),
]

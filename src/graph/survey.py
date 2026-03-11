"""Surveyor graph construction, velocity, and heuristic helpers."""

from __future__ import annotations

import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import networkx as nx
from networkx.algorithms.link_analysis.pagerank_alg import _pagerank_python

from src.models.enums import AnalysisMethod, ConfidenceBand, EdgeKind, SupportStatus
from src.models.evidence import EvidenceRecord
from src.models.graph import (
    DeadCodeCandidate,
    GraphEdge,
    ModuleNode,
    SurveyCycle,
    SurveyHub,
    VelocityRecord,
)
from src.models.structural import StructuralFileResult, StructuralRecord, StructuralSymbolKind
from src.utils.ids import build_module_dependency_key, normalize_relative_path

GRAPH_LANGUAGES = {"python", "javascript", "typescript"}

PYTHON_IMPORT_RE = re.compile(r"^(?:from\s+([A-Za-z0-9_\.]+)\s+import|import\s+([A-Za-z0-9_\. ,]+))")
JS_IMPORT_RE = re.compile(r"""(?:import|export)\s+(?:.+?\s+from\s+)?['"]([^'"]+)['"]""")
JS_REQUIRE_RE = re.compile(r"""require\(\s*['"]([^'"]+)['"]\s*\)""")


@dataclass(frozen=True)
class UnresolvedImport:
    source_path: str
    target: str
    reason: str


def relative_path_to_module_name(relative_path: str) -> str:
    """Convert a repo-relative source path to a stable dotted module name."""

    normalized = normalize_relative_path(relative_path)
    pure = PurePosixPath(normalized)
    stem = pure.with_suffix("").as_posix()
    if stem.endswith("/__init__"):
        stem = stem[: -len("/__init__")]
    return stem.replace("/", ".")


def build_module_node(file_result: StructuralFileResult) -> ModuleNode:
    """Create a Surveyor module node from one structural file result."""

    symbols = [record for record in file_result.records if record.symbol_kind != StructuralSymbolKind.IMPORT]
    function_records = [
        record for record in file_result.records if record.symbol_kind in {StructuralSymbolKind.FUNCTION, StructuralSymbolKind.METHOD}
    ]
    class_records = [record for record in file_result.records if record.symbol_kind == StructuralSymbolKind.CLASS]
    public_symbols = [
        record
        for record in symbols
        if record.symbol_name and not record.symbol_name.startswith("_") and record.symbol_kind != StructuralSymbolKind.MODULE
    ]
    return ModuleNode(
        relative_path=file_result.file_path,
        module_name=relative_path_to_module_name(file_result.file_path),
        language_or_dialect=file_result.language,
        support_status=file_result.support_status,
        confidence=ConfidenceBand.MEDIUM if file_result.is_partial else ConfidenceBand.HIGH,
        evidence=[ev for record in file_result.records for ev in record.evidence],
        import_targets=[],
        public_symbol_count=len(public_symbols),
        class_count=len(class_records),
        function_count=len(function_records),
        warnings=list(file_result.warnings),
    )


def extract_import_targets(repo_root: Path, file_result: StructuralFileResult) -> list[str]:
    """Extract raw import targets using structural evidence line ranges."""

    if file_result.language not in GRAPH_LANGUAGES:
        return []
    path = repo_root / file_result.file_path
    if not path.exists():
        return []
    source_lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    targets: list[str] = []
    seen: set[str] = set()
    for record in file_result.records:
        if record.symbol_kind != StructuralSymbolKind.IMPORT:
            continue
        snippet = _record_snippet(record, source_lines)
        for target in _parse_import_targets(file_result.language, snippet):
            key = build_module_dependency_key(file_result.file_result_id or file_result.file_path, target)
            if key not in seen:
                seen.add(key)
                targets.append(target)
    return targets


def build_import_edges(
    repo_root: Path,
    module_nodes: list[ModuleNode],
    file_results: list[StructuralFileResult],
) -> tuple[list[GraphEdge], list[UnresolvedImport], dict[str, list[str]]]:
    """Create deterministic import edges and unresolved-import summaries."""

    by_path = {node.relative_path: node for node in module_nodes}
    by_module_name = {node.module_name: node for node in module_nodes}
    file_lookup = {result.file_path: result for result in file_results}
    edges: list[GraphEdge] = []
    unresolved: list[UnresolvedImport] = []
    import_targets_by_path: dict[str, list[str]] = {}

    for node in module_nodes:
        file_result = file_lookup.get(node.relative_path)
        if file_result is None:
            continue
        raw_targets = extract_import_targets(repo_root, file_result)
        import_targets_by_path[node.relative_path] = raw_targets
        for raw_target in raw_targets:
            resolved = resolve_internal_target(raw_target, node.relative_path, by_path, by_module_name)
            if resolved is None:
                unresolved.append(
                    UnresolvedImport(source_path=node.relative_path, target=raw_target, reason="unresolved_or_external")
                )
                continue
            edges.append(
                GraphEdge(
                    source_node_id=node.node_id,
                    target_node_id=resolved.node_id,
                    kind=EdgeKind.IMPORTS,
                    analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                    confidence=ConfidenceBand.MEDIUM,
                    evidence=_first_import_evidence(file_result.records),
                    metadata={"target_display": raw_target},
                    support_status=SupportStatus.SUPPORTED,
                )
            )
    deduped = {edge.edge_id: edge for edge in edges}
    ordered_edges = sorted(deduped.values(), key=lambda edge: edge.edge_id or "")
    return ordered_edges, sorted(unresolved, key=lambda item: (item.source_path, item.target)), import_targets_by_path


def build_import_graph(module_nodes: list[ModuleNode], edges: list[GraphEdge]) -> nx.DiGraph:
    """Build a directed import graph for Surveyor analytics."""

    graph = nx.DiGraph()
    for node in sorted(module_nodes, key=lambda item: item.node_id or ""):
        graph.add_node(node.node_id, relative_path=node.relative_path, module_name=node.module_name)
    for edge in sorted(edges, key=lambda item: item.edge_id or ""):
        graph.add_edge(edge.source_node_id, edge.target_node_id, edge_id=edge.edge_id)
    return graph


def compute_pagerank(graph: nx.DiGraph, module_nodes: dict[str, ModuleNode]) -> list[SurveyHub]:
    """Compute deterministic PageRank scores for architectural hubs."""

    if graph.number_of_nodes() == 0:
        return []
    try:
        scores = nx.pagerank(graph)
    except ModuleNotFoundError:
        scores = _pagerank_python(graph)
    hubs = [
        SurveyHub(module_id=node_id, relative_path=module_nodes[node_id].relative_path, score=round(score, 8))
        for node_id, score in scores.items()
        if node_id in module_nodes
    ]
    return sorted(hubs, key=lambda item: (-item.score, item.relative_path, item.module_id))


def compute_strongly_connected_components(graph: nx.DiGraph, module_nodes: dict[str, ModuleNode]) -> list[SurveyCycle]:
    """Compute deterministic circular-dependency groups."""

    cycles: list[SurveyCycle] = []
    for component in nx.strongly_connected_components(graph):
        if len(component) < 2:
            continue
        ordered_ids = sorted(component)
        paths = sorted(module_nodes[node_id].relative_path for node_id in ordered_ids if node_id in module_nodes)
        cycles.append(SurveyCycle(module_ids=ordered_ids, relative_paths=paths))
    return sorted(cycles, key=lambda item: tuple(item.relative_paths))


def extract_git_velocity(repo_root: Path, days: int = 30) -> tuple[dict[str, int], list[str]]:
    """Return recent per-file change counts from git history."""

    command = [
        "git",
        "-C",
        str(repo_root),
        "log",
        f"--since={days} days ago",
        "--name-only",
        "--pretty=format:",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {}, [f"git_velocity_unavailable:{type(exc).__name__}"]
    if result.returncode != 0:
        return {}, [f"git_velocity_unavailable:returncode_{result.returncode}"]

    counter: Counter[str] = Counter()
    for line in result.stdout.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        try:
            normalized = normalize_relative_path(cleaned)
        except ValueError:
            continue
        counter[normalized] += 1
    return dict(counter), []


def compute_high_velocity_core(
    velocity_by_path: dict[str, int],
    *,
    lookback_days: int,
    change_share_threshold: float = 0.8,
    module_id_by_path: dict[str, str] | None = None,
) -> list[VelocityRecord]:
    """Select a deterministic Pareto-style high-velocity core."""

    if not velocity_by_path:
        return []
    total_changes = sum(velocity_by_path.values())
    cumulative = 0
    core: list[VelocityRecord] = []
    for relative_path, count in sorted(velocity_by_path.items(), key=lambda item: (-item[1], item[0])):
        cumulative += count
        module_id = module_id_by_path.get(relative_path, relative_path) if module_id_by_path else relative_path
        core.append(
            VelocityRecord(
                module_id=module_id,
                relative_path=relative_path,
                lookback_days=lookback_days,
                change_count=count,
                is_high_velocity_core=True,
            )
        )
        if cumulative / max(total_changes, 1) >= change_share_threshold:
            break
    return core


def detect_dead_code_candidates(
    module_nodes: dict[str, ModuleNode],
    graph: nx.DiGraph,
    velocity_by_path: dict[str, int],
) -> list[DeadCodeCandidate]:
    """Produce conservative heuristic dead-code signals."""

    candidates: list[DeadCodeCandidate] = []
    for node_id, node in sorted(module_nodes.items(), key=lambda item: item[1].relative_path):
        if node.relative_path.endswith("__init__.py"):
            continue
        reasons: list[str] = []
        if graph.in_degree(node_id) == 0:
            reasons.append("no_inbound_imports")
        if graph.out_degree(node_id) == 0:
            reasons.append("isolated_module")
        if node.public_symbol_count == 0 and (node.function_count > 0 or node.class_count > 0):
            reasons.append("no_public_symbols")
        if velocity_by_path.get(node.relative_path, 0) == 0:
            reasons.append("low_recent_change_activity")
        if len(reasons) < 2:
            continue
        candidates.append(
            DeadCodeCandidate(
                module_id=node_id,
                relative_path=node.relative_path,
                reason_codes=reasons,
                confidence=ConfidenceBand.MEDIUM if len(reasons) >= 3 else ConfidenceBand.LOW,
                evidence=node.evidence[:2],
            )
        )
    return candidates


def resolve_internal_target(
    raw_target: str,
    source_relative_path: str,
    by_path: dict[str, ModuleNode],
    by_module_name: dict[str, ModuleNode],
) -> ModuleNode | None:
    """Resolve a raw import target to an internal module node when possible."""

    if raw_target in by_module_name:
        return by_module_name[raw_target]
    normalized_target = raw_target.replace("/", ".")
    if normalized_target in by_module_name:
        return by_module_name[normalized_target]

    source_path = PurePosixPath(source_relative_path)
    candidate_paths: list[str] = []
    if raw_target.startswith("."):
        dot_count = len(raw_target) - len(raw_target.lstrip("."))
        suffix = raw_target[dot_count:]
        base = source_path.parent
        for _ in range(max(dot_count - 1, 0)):
            base = base.parent
        suffix_path = PurePosixPath(*[part for part in suffix.replace(".", "/").split("/") if part])
        candidate_base = (base / suffix_path).as_posix()
        candidate_paths.extend(_candidate_module_paths(candidate_base))
    else:
        candidate_paths.extend(_candidate_module_paths(raw_target.replace(".", "/")))

    for candidate in candidate_paths:
        normalized = normalize_relative_path(candidate)
        if normalized in by_path:
            return by_path[normalized]
        dotted = relative_path_to_module_name(normalized)
        if dotted in by_module_name:
            return by_module_name[dotted]
    return None


def _candidate_module_paths(base: str) -> list[str]:
    stripped = base.strip("/")
    if not stripped:
        return []
    candidates: list[str] = []
    for suffix in (".py", ".js", ".ts", ".tsx", ".mjs", ".cjs"):
        candidates.append(f"{stripped}{suffix}")
    for suffix in ("/__init__.py", "/index.js", "/index.ts"):
        candidates.append(f"{stripped}{suffix}")
    return candidates


def _record_snippet(record: StructuralRecord, source_lines: list[str]) -> str:
    if record.evidence:
        evidence = record.evidence[0]
        if evidence.line_start is not None and evidence.line_end is not None:
            start = max(evidence.line_start - 1, 0)
            end = min(evidence.line_end, len(source_lines))
            return "\n".join(source_lines[start:end])
    return ""


def _parse_import_targets(language: str, snippet: str) -> list[str]:
    targets: list[str] = []
    for line in snippet.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if language == "python":
            match = PYTHON_IMPORT_RE.match(stripped)
            if not match:
                continue
            from_target, import_target = match.groups()
            if from_target:
                imported_names = stripped.split("import", maxsplit=1)[-1]
                names = [part.strip() for part in imported_names.split(",") if part.strip()]
                if names:
                    targets.extend(f"{from_target}.{name}" for name in names)
                else:
                    targets.append(from_target)
                continue
            if import_target:
                targets.extend(part.strip() for part in import_target.split(",") if part.strip())
        else:
            for regex in (JS_IMPORT_RE, JS_REQUIRE_RE):
                for match in regex.finditer(stripped):
                    targets.append(match.group(1))
    return targets


def _first_import_evidence(records: list[StructuralRecord]) -> list[EvidenceRecord]:
    for record in records:
        if record.symbol_kind == StructuralSymbolKind.IMPORT:
            return record.evidence[:1]
    return []

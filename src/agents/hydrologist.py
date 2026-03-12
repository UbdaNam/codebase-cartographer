"""Hydrologist agent for deterministic lineage extraction."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re

from src.config import AppSettings
from src.graph.lineage import (
    LineageSignal,
    build_dataset_node,
    build_lineage_edges,
    build_lineage_graph,
    build_transformation_node,
    line_number_for_offset,
    normalize_dataset_identifier,
)
from src.models.enums import AnalysisMethod, ConfidenceBand
from src.models.graph import GraphPayload, LineageSummaryPayload, ModuleNode
from src.models.manifest import RepositoryManifest
from src.models.repository_input import PreparedRepository
from src.models.structural import StructuralIndexPayload

try:
    import sqlglot
    from sqlglot import exp
except Exception:  # pragma: no cover
    sqlglot = None
    exp = None

SQL_HINT_RE = re.compile(r"(?is)\b(select|with|insert\s+into|create\s+table)\b")
PY_STRING_RE = re.compile(r"(?P<quote>\"\"\"|'''|\"|')(?P<body>.*?)(?P=quote)", re.DOTALL)
READ_FILE_RE = re.compile(r"(?P<func>read_csv|read_parquet|read_json)\(\s*[ruf]*['\"](?P<dataset>[^'\"]+)['\"]", re.IGNORECASE)
WRITE_FILE_RE = re.compile(r"(?P<var>\w+)\.(?P<func>to_csv|to_parquet|to_json)\(\s*[ruf]*['\"](?P<dataset>[^'\"]+)['\"]", re.IGNORECASE)
READ_TABLE_RE = re.compile(r"(?P<prefix>spark\.read|spark)\.(?:table|load)\(\s*[ruf]*['\"](?P<dataset>[^'\"]+)['\"]", re.IGNORECASE)
WRITE_TABLE_RE = re.compile(r"(?P<prefix>write|spark\.write)\.(?:saveAsTable|insertInto|save)\(\s*[ruf]*['\"](?P<dataset>[^'\"]+)['\"]", re.IGNORECASE)
SQL_EXEC_RE = re.compile(r"(?:read_sql|execute|sql)\(\s*[ruf]*(?P<quote>\"\"\"|'''|\"|')(?P<body>.*?)(?P=quote)", re.IGNORECASE | re.DOTALL)
YAML_KEY_RE = re.compile(r"^(?P<key>source|sources|input|inputs|upstream|dataset|table|model|target|targets|output|outputs|destination):\s*(?P<value>.+)?$", re.IGNORECASE)
DYNAMIC_SQL_RE = re.compile(r"\{.+?\}|%\(.+?\)s|\+\s*\w+")
SQL_TABLE_FALLBACK_RE = re.compile(r"(?i)\b(?:from|join|into|table)\s+([A-Za-z_][A-Za-z0-9_$.]*)")
EXECUTE_VARIABLE_RE = re.compile(r"(?:execute|read_sql|sql)\((?P<var>\w+)\)", re.IGNORECASE)
SQL_ASSIGNMENT_RE = re.compile(r"(?P<var>\w+)\s*=\s*[furbFURB]*(?P<quote>\"\"\"|'''|\"|')(?P<body>.*?)(?P=quote)", re.DOTALL)


class HydrologistAgent:
    SUPPORTED_LINEAGE_LANGUAGES = {"sql", "python", "yaml"}

    def __init__(self, settings: AppSettings):
        self.settings = settings

    def analyze(
        self,
        prepared_repository: PreparedRepository,
        manifest: RepositoryManifest,
        structural_index: StructuralIndexPayload,
        module_graph: GraphPayload,
        *,
        run_id: str,
        artifact_dir: str,
    ) -> tuple[GraphPayload, LineageSummaryPayload]:
        del structural_index
        repo_root = Path(prepared_repository.local_repo_path)
        module_nodes = {
            node.relative_path: node
            for node in module_graph.nodes
            if isinstance(node, ModuleNode)
        }
        warnings: list[str] = []
        partial_flags: list[str] = []
        signals: list[LineageSignal] = []
        source_counts = {"sql": 0, "python": 0, "yaml": 0}

        for record in manifest.records:
            if record.skip_reason is not None or not record.is_parse_eligible:
                continue
            if record.language not in self.SUPPORTED_LINEAGE_LANGUAGES:
                continue
            file_path = repo_root / record.relative_path
            if not file_path.exists():
                continue
            content = file_path.read_text(encoding="utf-8", errors="replace")
            module_node = module_nodes.get(record.relative_path)
            if record.language == "sql":
                extracted, item_warnings, partial = self._extract_sql_signals(record.relative_path, content, module_node)
            elif record.language == "python":
                extracted, item_warnings, partial = self._extract_python_signals(record.relative_path, content, module_node)
            else:
                extracted, item_warnings, partial = self._extract_yaml_signals(record.relative_path, content, module_node)
            signals.extend(extracted)
            warnings.extend(item_warnings)
            source_counts[record.language] += len(extracted)
            if partial:
                partial_flags.append(f"{record.language}_partial")

        dataset_buckets: dict[str, list[LineageSignal]] = defaultdict(list)
        transformation_buckets: dict[tuple[str, str], list[LineageSignal]] = defaultdict(list)
        for signal in signals:
            dataset_buckets[normalize_dataset_identifier(signal.dataset_name)].append(signal)
            transformation_name = signal.transformation_name or signal.file_path
            transformation_buckets[(signal.file_path, transformation_name)].append(signal)

        dataset_nodes = [build_dataset_node(bucket[0].dataset_name, bucket) for _, bucket in sorted(dataset_buckets.items())]
        transformation_nodes = [
            build_transformation_node(file_path, transformation_name, bucket, module_or_file_id=bucket[0].module_or_file_id)
            for (file_path, transformation_name), bucket in sorted(transformation_buckets.items())
        ]
        edges = build_lineage_edges({node.node_id: node for node in dataset_nodes}, {node.node_id: node for node in transformation_nodes}, signals)
        graph = build_lineage_graph(dataset_nodes, transformation_nodes, edges)

        lineage_graph = GraphPayload(
            run_id=run_id,
            graph_metadata={
                "analysis_root": prepared_repository.local_repo_path,
                "artifact_dir": artifact_dir.replace("\\", "/"),
                "dataset_count": len(dataset_nodes),
                "transformation_count": len(transformation_nodes),
                "edge_count": len(edges),
                "warnings": sorted(dict.fromkeys(warnings)),
                "partial_result_flags": sorted(dict.fromkeys(partial_flags)),
                "source_counts": source_counts,
            },
            nodes=dataset_nodes + transformation_nodes,
            edges=edges,
        )
        lineage_summary = LineageSummaryPayload(
            run_id=run_id,
            analysis_root=prepared_repository.local_repo_path,
            dataset_count=len(dataset_nodes),
            transformation_count=len(transformation_nodes),
            edge_count=len(edges),
            sql_signal_count=source_counts["sql"],
            python_signal_count=source_counts["python"],
            yaml_signal_count=source_counts["yaml"],
            warnings=warnings,
            partial_result_flags=partial_flags,
            stats={
                "dataset_count": len(dataset_nodes),
                "transformation_count": len(transformation_nodes),
                "edge_count": len(edges),
                "graph_node_count": graph.number_of_nodes(),
                "graph_edge_count": graph.number_of_edges(),
                "sql_signal_count": source_counts["sql"],
                "python_signal_count": source_counts["python"],
                "yaml_signal_count": source_counts["yaml"],
            },
        )
        return lineage_graph, lineage_summary

    def _extract_sql_signals(self, file_path: str, sql_text: str, module_node: ModuleNode | None) -> tuple[list[LineageSignal], list[str], bool]:
        transformation_name = f"sql::{normalize_dataset_identifier(file_path)}"
        warnings: list[str] = []
        try:
            signals = self._parse_sql_to_signals(file_path, sql_text, transformation_name, module_node)
        except Exception:
            fallback = self._fallback_sql_signals(file_path, sql_text, transformation_name, module_node)
            partial = not fallback or any(signal.is_partial for signal in fallback)
            if partial:
                warnings.append(f"malformed_sql:{file_path}")
            return fallback, warnings, partial
        if not signals:
            fallback = self._fallback_sql_signals(file_path, sql_text, transformation_name, module_node)
            partial = not fallback or any(signal.is_partial for signal in fallback)
            if partial:
                warnings.append(f"malformed_sql:{file_path}")
            return fallback, warnings, partial
        partial = any(signal.is_partial for signal in signals)
        return signals, warnings, partial

    def _extract_python_signals(self, file_path: str, content: str, module_node: ModuleNode | None) -> tuple[list[LineageSignal], list[str], bool]:
        signals: list[LineageSignal] = []
        warnings: list[str] = []
        partial = False
        transformation_name = module_node.module_name if module_node else file_path.replace("\\", "/")
        module_id = module_node.node_id if module_node else file_path.replace("\\", "/")

        for match in READ_FILE_RE.finditer(content):
            signals.append(self._build_signal("python_api", file_path, match.group("dataset"), "input", "python", line_number_for_offset(content, match.start()), transformation_name, module_id))
        for match in WRITE_FILE_RE.finditer(content):
            signals.append(self._build_signal("python_api", file_path, match.group("dataset"), "output", "python", line_number_for_offset(content, match.start()), transformation_name, module_id))
        for match in READ_TABLE_RE.finditer(content):
            signals.append(self._build_signal("python_api", file_path, match.group("dataset"), "input", "python", line_number_for_offset(content, match.start()), transformation_name, module_id))
        for match in WRITE_TABLE_RE.finditer(content):
            signals.append(self._build_signal("python_api", file_path, match.group("dataset"), "output", "python", line_number_for_offset(content, match.start()), transformation_name, module_id))

        assigned_sql: dict[str, tuple[str, int]] = {}
        for match in SQL_ASSIGNMENT_RE.finditer(content):
            body = match.group("body")
            if SQL_HINT_RE.search(body):
                assigned_sql[match.group("var")] = (body, match.start())

        for match in SQL_EXEC_RE.finditer(content):
            sql_body = match.group("body")
            if DYNAMIC_SQL_RE.search(sql_body):
                warnings.append(f"dynamic_python_sql:{file_path}:{line_number_for_offset(content, match.start())}")
                partial = True
                continue
            extracted, sql_warnings, sql_partial = self._extract_sql_signals(file_path, sql_body, module_node)
            signals.extend(self._reframe_embedded_sql(content, match.start(), match.end(), extracted, transformation_name, module_id))
            warnings.extend(sql_warnings)
            partial = partial or sql_partial

        for match in EXECUTE_VARIABLE_RE.finditer(content):
            variable_name = match.group("var")
            if variable_name not in assigned_sql:
                continue
            sql_body, assignment_offset = assigned_sql[variable_name]
            if DYNAMIC_SQL_RE.search(sql_body):
                warnings.append(f"dynamic_python_sql:{file_path}:{line_number_for_offset(content, assignment_offset)}")
                partial = True
                continue
            extracted, sql_warnings, sql_partial = self._extract_sql_signals(file_path, sql_body, module_node)
            signals.extend(self._reframe_embedded_sql(content, assignment_offset, match.end(), extracted, transformation_name, module_id))
            warnings.extend(sql_warnings)
            partial = partial or sql_partial

        for match in PY_STRING_RE.finditer(content):
            body = match.group("body")
            if not SQL_HINT_RE.search(body):
                continue
            extracted, sql_warnings, sql_partial = self._extract_sql_signals(file_path, body, module_node)
            signals.extend(self._reframe_embedded_sql(content, match.start(), match.end(), extracted, transformation_name, module_id))
            warnings.extend(sql_warnings)
            partial = partial or sql_partial
        return signals, warnings, partial

    def _extract_yaml_signals(self, file_path: str, content: str, module_node: ModuleNode | None) -> tuple[list[LineageSignal], list[str], bool]:
        transformation_name = f"yaml::{normalize_dataset_identifier(file_path)}"
        module_id = module_node.node_id if module_node else file_path.replace("\\", "/")
        signals: list[LineageSignal] = []
        warnings: list[str] = []
        partial = False
        for line_no, line in enumerate(content.splitlines(), start=1):
            match = YAML_KEY_RE.match(line.strip())
            if not match:
                continue
            key = match.group("key").lower()
            value = (match.group("value") or "").strip()
            datasets = self._parse_yaml_dataset_values(value)
            role = "input" if key in {"source", "sources", "input", "inputs", "upstream", "dataset", "table", "model"} else "output"
            if not datasets:
                partial = True
                warnings.append(f"weak_yaml_reference:{file_path}:{line_no}")
                continue
            for dataset in datasets:
                confidence = ConfidenceBand.MEDIUM if key in {"source", "sources", "input", "inputs", "target", "targets", "output", "outputs", "destination"} else ConfidenceBand.LOW
                signals.append(
                    LineageSignal(
                        source_kind="yaml_config",
                        file_path=file_path,
                        dataset_name=dataset,
                        role=role,
                        language="yaml",
                        line_start=line_no,
                        line_end=line_no,
                        transformation_name=transformation_name,
                        module_or_file_id=module_id,
                        analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                        confidence=confidence,
                        is_partial=confidence == ConfidenceBand.LOW,
                        warnings=tuple(["weak_yaml_reference"] if confidence == ConfidenceBand.LOW else []),
                    )
                )
                partial = partial or confidence == ConfidenceBand.LOW
        return signals, warnings, partial

    def _parse_sql_to_signals(self, file_path: str, sql_text: str, transformation_name: str, module_node: ModuleNode | None) -> list[LineageSignal]:
        module_id = module_node.node_id if module_node else file_path.replace("\\", "/")
        if sqlglot is None or exp is None:
            return self._fallback_sql_signals(file_path, sql_text, transformation_name, module_node)
        statements = sqlglot.parse(sql_text)
        signals: list[LineageSignal] = []
        for statement in statements:
            produced: list[str] = []
            if isinstance(statement, exp.Create) and statement.this is not None:
                produced.append(statement.this.sql())
            if isinstance(statement, exp.Insert) and statement.this is not None:
                produced.append(statement.this.sql())
            for table in statement.find_all(exp.Table):
                dataset_name = table.sql(dialect="")
                if dataset_name in produced:
                    continue
                signals.append(LineageSignal(source_kind="sql", file_path=file_path, dataset_name=dataset_name, role="input", language="sql", transformation_name=transformation_name, module_or_file_id=module_id, analysis_method=AnalysisMethod.STATIC_ANALYSIS, confidence=ConfidenceBand.HIGH))
            for dataset_name in produced:
                signals.append(LineageSignal(source_kind="sql", file_path=file_path, dataset_name=dataset_name, role="output", language="sql", transformation_name=transformation_name, module_or_file_id=module_id, analysis_method=AnalysisMethod.STATIC_ANALYSIS, confidence=ConfidenceBand.HIGH))
        return signals

    def _fallback_sql_signals(self, file_path: str, sql_text: str, transformation_name: str, module_node: ModuleNode | None) -> list[LineageSignal]:
        module_id = module_node.node_id if module_node else file_path.replace("\\", "/")
        signals: list[LineageSignal] = []
        outputs = re.findall(r"(?i)\b(?:insert\s+into|create\s+table)\s+([A-Za-z_][A-Za-z0-9_$.]*)", sql_text)
        for match in SQL_TABLE_FALLBACK_RE.finditer(sql_text):
            dataset = match.group(1)
            if dataset in outputs:
                continue
            signals.append(LineageSignal(source_kind="sql", file_path=file_path, dataset_name=dataset, role="input", language="sql", transformation_name=transformation_name, module_or_file_id=module_id, analysis_method=AnalysisMethod.STATIC_ANALYSIS, confidence=ConfidenceBand.HIGH))
        for dataset in outputs:
            signals.append(LineageSignal(source_kind="sql", file_path=file_path, dataset_name=dataset, role="output", language="sql", transformation_name=transformation_name, module_or_file_id=module_id, analysis_method=AnalysisMethod.STATIC_ANALYSIS, confidence=ConfidenceBand.HIGH))
        return signals

    def _parse_yaml_dataset_values(self, value: str) -> list[str]:
        if not value:
            return []
        stripped = value.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            stripped = stripped[1:-1]
        return [item.strip().strip("\"'") for item in stripped.split(",") if item.strip()]

    def _reframe_embedded_sql(
        self,
        content: str,
        start: int,
        end: int,
        extracted: list[LineageSignal],
        transformation_name: str,
        module_id: str,
    ) -> list[LineageSignal]:
        reframed: list[LineageSignal] = []
        for signal in extracted:
            reframed.append(
                LineageSignal(
                    source_kind="embedded_sql",
                    file_path=signal.file_path,
                    dataset_name=signal.dataset_name,
                    role=signal.role,
                    language="python",
                    line_start=line_number_for_offset(content, start),
                    line_end=line_number_for_offset(content, end),
                    transformation_name=transformation_name,
                    module_or_file_id=module_id,
                    analysis_method=signal.analysis_method,
                    confidence=signal.confidence,
                    is_partial=signal.is_partial,
                    warnings=signal.warnings,
                )
            )
        return reframed

    def _build_signal(self, source_kind: str, file_path: str, dataset_name: str, role: str, language: str, line_no: int, transformation_name: str, module_or_file_id: str, partial: bool = False) -> LineageSignal:
        return LineageSignal(
            source_kind=source_kind,
            file_path=file_path,
            dataset_name=dataset_name,
            role=role,
            language=language,
            line_start=line_no,
            line_end=line_no,
            transformation_name=transformation_name,
            module_or_file_id=module_or_file_id,
            analysis_method=AnalysisMethod.STATIC_ANALYSIS if not partial else AnalysisMethod.HEURISTIC,
            confidence=ConfidenceBand.LOW if partial else ConfidenceBand.HIGH,
            is_partial=partial,
            warnings=tuple(["partial_lineage_signal"] if partial else []),
        )

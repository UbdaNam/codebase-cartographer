"""Tree-sitter-backed structural analyzer for Stage 3."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from src.models.artifacts import SerializationMetadata
from src.models.enums import AnalysisMethod, ConfidenceBand, SupportStatus
from src.models.evidence import EvidenceRecord
from src.models.manifest import ManifestRecord, RepositoryManifest
from src.models.repository_input import PreparedRepository
from src.models.structural import (
    AstIndexEntry,
    AstIndexPayload,
    ParseStatus,
    StructuralFileResult,
    StructuralIndexPayload,
    StructuralRecord,
    StructuralSummary,
    StructuralSymbolKind,
)
from src.utils.ids import canonicalize_json_value
from src.utils.language_router import LanguageRouter


class TreeSitterAnalyzer:
    """Analyze manifest-eligible files into deterministic structural artifacts."""

    def __init__(self, router: LanguageRouter | None = None):
        self.router = router or LanguageRouter()

    def analyze_manifest(
        self,
        prepared_repository: PreparedRepository,
        manifest: RepositoryManifest,
        *,
        run_id: str,
        artifact_dir: str,
    ) -> tuple[StructuralIndexPayload, AstIndexPayload]:
        file_results: list[StructuralFileResult] = []
        ast_entries: list[AstIndexEntry] = []

        repo_root = Path(prepared_repository.local_repo_path)
        for record in manifest.records:
            if record.skip_reason is not None:
                file_results.append(
                    StructuralFileResult(
                        manifest_file_id=record.file_id or record.relative_path,
                        file_path=record.relative_path,
                        language=record.language,
                        support_status=record.support_status,
                        parse_status=ParseStatus.SKIPPED,
                        warnings=[f"manifest_skip:{record.skip_reason.value}"],
                    )
                )
                continue

            route = self.router.route_manifest_record(record)
            if not route.deep_parse_eligible or route.parser_language is None:
                parse_status = ParseStatus.PARTIAL if route.support_status == SupportStatus.PARTIAL else ParseStatus.UNSUPPORTED
                file_results.append(
                    StructuralFileResult(
                        manifest_file_id=record.file_id or record.relative_path,
                        file_path=record.relative_path,
                        language=route.normalized_language,
                        support_status=route.support_status,
                        parse_status=parse_status,
                        is_partial=parse_status == ParseStatus.PARTIAL,
                        warnings=route.notes,
                    )
                )
                continue

            path = repo_root / record.relative_path
            source_bytes = path.read_bytes()
            parser = self.router.get_parser(route.parser_language)
            tree = parser.parse(source_bytes)
            root = tree.root_node
            warnings: list[str] = list(route.notes)
            if root.has_error:
                warnings.append("tree_sitter_parse_has_error")

            records = self._extract_records(
                route.normalized_language,
                record.relative_path,
                source_bytes,
                root,
            )
            parse_status = ParseStatus.PARSED
            is_partial = False
            if root.has_error:
                parse_status = ParseStatus.PARTIAL
                is_partial = True

            file_results.append(
                StructuralFileResult(
                    manifest_file_id=record.file_id or record.relative_path,
                    file_path=record.relative_path,
                    language=route.normalized_language,
                    support_status=route.support_status,
                    parse_status=parse_status,
                    is_partial=is_partial,
                    records=records,
                    warnings=warnings,
                    root_node_type=root.type,
                    node_count=self._count_nodes(root),
                )
            )
            ast_entries.append(
                AstIndexEntry(
                    manifest_file_id=record.file_id or record.relative_path,
                    file_path=record.relative_path,
                    language=route.normalized_language,
                    root_node_type=root.type,
                    node_count=self._count_nodes(root),
                    has_error=root.has_error,
                )
            )

        summary = self._build_summary(file_results)
        metadata = SerializationMetadata(run_id=run_id, artifact_dir=artifact_dir)
        structural_payload = StructuralIndexPayload(
            metadata=metadata,
            prepared_repository=prepared_repository,
            file_results=file_results,
            summary=summary,
        )
        ast_payload = AstIndexPayload(
            metadata=metadata,
            prepared_repository=prepared_repository,
            entries=ast_entries,
        )
        return structural_payload, ast_payload

    def _extract_records(self, language: str, file_path: str, source_bytes: bytes, root) -> list[StructuralRecord]:
        if language == "python":
            return self._extract_python(file_path, source_bytes, root)
        if language in {"javascript", "typescript"}:
            return self._extract_javascript_family(language, file_path, source_bytes, root)
        if language == "sql":
            return self._extract_sql(file_path, source_bytes, root)
        if language == "yaml":
            return self._extract_yaml(file_path, source_bytes, root)
        return []

    def _extract_python(self, file_path: str, source_bytes: bytes, root) -> list[StructuralRecord]:
        records = [self._module_record(file_path, "python", root)]
        for child in root.children:
            if child.type in {"import_statement", "import_from_statement"}:
                records.append(self._make_record(file_path, "python", StructuralSymbolKind.IMPORT, source_bytes, child))
            if child.type == "class_definition":
                records.append(self._make_record(file_path, "python", StructuralSymbolKind.CLASS, source_bytes, child, symbol_name=self._first_named_identifier(child, source_bytes)))
                for nested in self._descendants(child, {"function_definition"}):
                    records.append(
                        self._make_record(
                            file_path,
                            "python",
                            StructuralSymbolKind.METHOD,
                            source_bytes,
                            nested,
                            symbol_name=self._first_named_identifier(nested, source_bytes),
                            container_name=self._first_named_identifier(child, source_bytes),
                            signature=self._first_child_text(nested, "parameters", source_bytes),
                        )
                    )
            if child.type == "function_definition":
                records.append(
                    self._make_record(
                        file_path,
                        "python",
                        StructuralSymbolKind.FUNCTION,
                        source_bytes,
                        child,
                        symbol_name=self._first_named_identifier(child, source_bytes),
                        signature=self._first_child_text(child, "parameters", source_bytes),
                    )
                )
        return records

    def _extract_javascript_family(self, language: str, file_path: str, source_bytes: bytes, root) -> list[StructuralRecord]:
        records = [self._module_record(file_path, language, root)]
        for child in root.children:
            if child.type == "import_statement":
                records.append(self._make_record(file_path, language, StructuralSymbolKind.IMPORT, source_bytes, child))
            for declaration in self._unwrap_export(child):
                if declaration.type == "class_declaration":
                    class_name = self._first_named_identifier(declaration, source_bytes)
                    records.append(
                        self._make_record(
                            file_path,
                            language,
                            StructuralSymbolKind.CLASS,
                            source_bytes,
                            declaration,
                            symbol_name=class_name,
                        )
                    )
                    for method in self._descendants(declaration, {"method_definition"}):
                        method_name = self._first_named_identifier(method, source_bytes)
                        records.append(
                            self._make_record(
                                file_path,
                                language,
                                StructuralSymbolKind.METHOD,
                                source_bytes,
                                method,
                                symbol_name=method_name,
                                container_name=class_name,
                                signature=self._first_child_text(method, "formal_parameters", source_bytes),
                            )
                        )
                if declaration.type == "function_declaration":
                    records.append(
                        self._make_record(
                            file_path,
                            language,
                            StructuralSymbolKind.FUNCTION,
                            source_bytes,
                            declaration,
                            symbol_name=self._first_named_identifier(declaration, source_bytes),
                            signature=self._first_child_text(declaration, "formal_parameters", source_bytes),
                        )
                    )
        return records

    def _extract_sql(self, file_path: str, source_bytes: bytes, root) -> list[StructuralRecord]:
        records = [self._module_record(file_path, "sql", root)]
        for child in root.children:
            if child.type == "statement":
                symbol_name = None
                for descendant in self._descendants(child, {"relation", "object_reference"}):
                    symbol_name = self._node_text(descendant, source_bytes)
                    break
                records.append(
                    self._make_record(
                        file_path,
                        "sql",
                        StructuralSymbolKind.STATEMENT,
                        source_bytes,
                        child,
                        symbol_name=symbol_name,
                    )
                )
        return records

    def _extract_yaml(self, file_path: str, source_bytes: bytes, root) -> list[StructuralRecord]:
        records = [self._module_record(file_path, "yaml", root)]
        for pair in self._descendants(root, {"block_mapping_pair"}):
            key_name = None
            for child in pair.children:
                if child.type == "flow_node":
                    key_name = self._node_text(child, source_bytes)
                    break
            records.append(
                self._make_record(
                    file_path,
                    "yaml",
                    StructuralSymbolKind.MAPPING,
                    source_bytes,
                    pair,
                    symbol_name=key_name,
                )
            )
        return records

    def _module_record(self, file_path: str, language: str, root) -> StructuralRecord:
        return StructuralRecord(
            file_path=file_path,
            language=language,
            symbol_kind=StructuralSymbolKind.MODULE,
            symbol_name=Path(file_path).stem,
            confidence=ConfidenceBand.HIGH,
            evidence=[
                EvidenceRecord(
                    source_path=file_path,
                    line_start=1,
                    line_end=max(root.end_point.row + 1, 1),
                    language=language,
                    analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                    confidence=ConfidenceBand.HIGH,
                    content_redacted=True,
                )
            ],
        )

    def _make_record(
        self,
        file_path: str,
        language: str,
        symbol_kind: StructuralSymbolKind,
        source_bytes: bytes,
        node,
        *,
        symbol_name: str | None = None,
        container_name: str | None = None,
        signature: str | None = None,
    ) -> StructuralRecord:
        return StructuralRecord(
            file_path=file_path,
            language=language,
            symbol_kind=symbol_kind,
            symbol_name=symbol_name,
            container_name=container_name,
            signature=signature,
            evidence=[
                EvidenceRecord(
                    source_path=file_path,
                    line_start=node.start_point.row + 1,
                    line_end=node.end_point.row + 1,
                    language=language,
                    analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                    confidence=ConfidenceBand.MEDIUM,
                    symbol_name=symbol_name,
                    content_redacted=True,
                )
            ],
        )

    def _unwrap_export(self, node) -> list:
        if node.type != "export_statement":
            return [node]
        return [child for child in node.children if child.type not in {"export", ";"}]

    def _first_named_identifier(self, node, source_bytes: bytes) -> str | None:
        preferred = {"identifier", "type_identifier", "property_identifier", "object_reference", "import_specifier"}
        for descendant in self._descendants(node, preferred):
            text = self._node_text(descendant, source_bytes)
            if text:
                return text
        return None

    def _first_child_text(self, node, child_type: str, source_bytes: bytes) -> str | None:
        for child in node.children:
            if child.type == child_type:
                return self._node_text(child, source_bytes)
        return None

    def _node_text(self, node, source_bytes: bytes) -> str:
        return source_bytes[node.start_byte:node.end_byte].decode("utf-8", errors="replace").strip()

    def _descendants(self, node, types: set[str]) -> Iterable:
        stack = list(reversed(node.children))
        while stack:
            current = stack.pop()
            if current.type in types:
                yield current
            if current.children:
                stack.extend(reversed(current.children))

    def _count_nodes(self, node) -> int:
        total = 1
        for child in node.children:
            total += self._count_nodes(child)
        return total

    def _build_summary(self, file_results: list[StructuralFileResult]) -> StructuralSummary:
        summary = StructuralSummary(total_files=len(file_results))
        for result in file_results:
            summary.record_count += len(result.records)
            if result.parse_status == ParseStatus.PARSED:
                summary.parsed_files += 1
            elif result.parse_status == ParseStatus.PARTIAL:
                summary.partial_files += 1
            elif result.parse_status == ParseStatus.SKIPPED:
                summary.skipped_files += 1
            elif result.parse_status == ParseStatus.FAILED:
                summary.failed_files += 1
            elif result.parse_status == ParseStatus.UNSUPPORTED:
                summary.unsupported_files += 1
        return summary

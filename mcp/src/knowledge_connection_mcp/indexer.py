"""Read-only parsers that turn knowledge cards and Python files into a graph."""

from __future__ import annotations

import ast
import hashlib
import re
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .models import Edge, GraphSnapshot, IndexReport, Node, ServiceError


ALLOWED_SUFFIXES = {".md", ".yaml", ".yml", ".py"}
IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".knowledge-connection",
    "build",
    "dist",
}
MAX_FILE_BYTES = 1_000_000
MAX_SKIP_REPORT = 50


@dataclass(frozen=True)
class PendingCall:
    source_id: str
    callee: str


@dataclass(frozen=True)
class PendingImport:
    source_id: str
    module_name: str


class GraphBuilder:
    """Build a fresh graph without mutating a previously served snapshot."""

    def __init__(self, root: Path, *, include_code: bool, include_knowledge: bool) -> None:
        self.root = root.resolve()
        self.include_code = include_code
        self.include_knowledge = include_knowledge
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []
        self.skipped: list[dict[str, str]] = []
        self.files_indexed = 0
        self.files_skipped = 0
        self.pending_calls: list[PendingCall] = []
        self.pending_imports: list[PendingImport] = []
        self._source_nodes_by_domain: dict[str, list[str]] = defaultdict(list)

    def build(
        self,
        max_files: int,
        paths: list[Path] | None = None,
        seed_nodes: dict[str, Node] | None = None,
        seed_edges: tuple[Edge, ...] | None = None,
        total_files: int | None = None,
    ) -> GraphSnapshot:
        if not self.root.exists() or not self.root.is_dir():
            raise ServiceError("invalid_root", "The requested root is not a readable directory.")
        if not 1 <= max_files <= 5_000:
            raise ServiceError("invalid_input", "max_files must be between 1 and 5000.")

        started = time.perf_counter()
        if seed_nodes:
            self.nodes.update(seed_nodes)
            for node in seed_nodes.values():
                if node.kind == "source":
                    self._source_nodes_by_domain[str(node.attributes.get("domain", ""))].append(node.id)
        if seed_edges:
            self.edges.extend(seed_edges)
        accepted_files = len(paths) if paths is not None else 0
        candidates = paths if paths is not None else self._candidate_files()
        for path in candidates:
            if paths is None:
                accepted_files += 1
            if accepted_files > max_files:
                raise ServiceError(
                    "resource_limit",
                    "The repository exceeds the configured max_files limit.",
                    max_files=max_files,
                )
            self._parse_file(path)

        self._connect_citations()
        self._connect_python_imports_and_calls()
        self._connect_shared_terms()

        content_fingerprint = hashlib.sha256(
            "\n".join(sorted(self.nodes)).encode("utf-8")
        ).hexdigest()[:12]
        snapshot_id = f"snapshot-{int(time.time() * 1000)}-{content_fingerprint}"
        languages: list[str] = []
        if any(node.kind in {"module", "class", "function", "method"} for node in self.nodes.values()):
            languages.append("python")
        if any(node.kind in {"knowledge", "scenario", "source"} for node in self.nodes.values()):
            languages.append("markdown-yaml")
        report = IndexReport(
            snapshot_id=snapshot_id,
            root_name=self.root.name,
            files_indexed=total_files if total_files is not None else self.files_indexed,
            files_skipped=self.files_skipped,
            nodes=len(self.nodes),
            edges=len(self.edges),
            duration_ms=round((time.perf_counter() - started) * 1000),
            languages=languages,
            skipped=self.skipped,
        )
        return GraphSnapshot(snapshot_id=snapshot_id, nodes=dict(self.nodes), edges=tuple(self.edges), report=report)

    def candidate_files(self) -> list[Path]:
        """Return only files accepted by the same root and extension policy as indexing."""

        return list(self._candidate_files())

    def _candidate_files(self) -> Iterable[Path]:
        for path in sorted(self.root.rglob("*")):
            if any(part in IGNORED_DIRECTORIES for part in path.relative_to(self.root).parts):
                continue
            if path.is_symlink() or not path.is_file() or path.suffix.lower() not in ALLOWED_SUFFIXES:
                continue
            try:
                resolved = path.resolve(strict=True)
            except OSError:
                self._skip(path, "unresolvable_path")
                continue
            if not _is_relative_to(resolved, self.root):
                self._skip(path, "path_outside_root")
                continue
            relative = path.relative_to(self.root)
            is_knowledge_file = len(relative.parts) > 1 and relative.parts[0] == "knowledge"
            if path.suffix.lower() == ".py" and self.include_code:
                yield path
            elif path.suffix.lower() == ".md" and self.include_knowledge and is_knowledge_file:
                yield path
            elif path.name in {"sources.yaml", "sources.yml"} and self.include_knowledge and is_knowledge_file:
                yield path

    def _parse_file(self, path: Path) -> None:
        try:
            size = path.stat().st_size
        except OSError:
            self._skip(path, "stat_failed")
            return
        if size > MAX_FILE_BYTES:
            self._skip(path, f"file_too_large:{MAX_FILE_BYTES}")
            return
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            self._skip(path, "read_failed")
            return
        relative = path.relative_to(self.root).as_posix()
        try:
            if path.suffix.lower() == ".py":
                self._parse_python(relative, text)
            elif path.suffix.lower() == ".md":
                self._parse_markdown(relative, text)
            else:
                self._parse_sources(relative, text)
        except (SyntaxError, UnicodeError, ValueError) as exc:
            self._skip(path, f"parse_error:{type(exc).__name__}")
            return
        self.files_indexed += 1

    def _parse_markdown(self, relative: str, text: str) -> None:
        lines = text.splitlines()
        headings: list[tuple[int, int, str]] = []
        for index, line in enumerate(lines, start=1):
            match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
            if match:
                headings.append((index, len(match.group(1)), match.group(2)))

        domain = _knowledge_domain(relative)
        document_title = next((title for _, level, title in headings if level == 1), Path(relative).stem)
        for position, (line_start, level, title) in enumerate(headings):
            if level < 2:
                continue
            line_end = len(lines)
            for next_line, next_level, _ in headings[position + 1 :]:
                if next_level <= level:
                    line_end = next_line - 1
                    break
            content = "\n".join(lines[line_start - 1 : line_end]).strip()
            lowered_title = title.casefold()
            is_scenario = relative.endswith("scenarios.md") or lowered_title.startswith("sc-")
            kind = "scenario" if is_scenario else "knowledge"
            references = re.findall(r"\[(\d+)\]", content)
            attributes = {
                "domain": domain,
                "document_title": document_title,
                "references": references,
                "has_risks": bool(re.search(r"风险|risk", content, re.IGNORECASE)),
                "has_validation": bool(re.search(r"验证|通过条件|validation", content, re.IGNORECASE)),
                "heading_level": level,
            }
            self._add_node(kind, title, relative, line_start, line_end, content, attributes)

    def _parse_sources(self, relative: str, text: str) -> None:
        lines = text.splitlines()
        domain = _knowledge_domain(relative)
        records: list[tuple[int, int, dict[str, str]]] = []
        current: dict[str, str] | None = None
        start_line = 0
        for line_number, line in enumerate(lines, start=1):
            item_match = re.match(r"^\s*-\s+([A-Za-z_][\w-]*)\s*:\s*(.*?)\s*$", line)
            field_match = re.match(r"^\s{2,}([A-Za-z_][\w-]*)\s*:\s*(.*?)\s*$", line)
            if item_match:
                if current is not None:
                    records.append((start_line, line_number - 1, current))
                start_line = line_number
                current = {item_match.group(1): _clean_scalar(item_match.group(2))}
            elif field_match and current is not None:
                current[field_match.group(1)] = _clean_scalar(field_match.group(2))
        if current is not None:
            records.append((start_line, len(lines), current))

        for line_start, line_end, record in records:
            if not record.get("source_id"):
                continue
            source_id = record["source_id"]
            title = record.get("title") or source_id
            content = "\n".join(f"{key}: {value}" for key, value in record.items())
            attributes = {"domain": domain, **record}
            node = self._add_node("source", title, relative, line_start, line_end, content, attributes)
            self._source_nodes_by_domain[domain].append(node.id)

    def _parse_python(self, relative: str, text: str) -> None:
        tree = ast.parse(text, filename=relative)
        lines = text.splitlines()
        module_name = _module_name(relative)
        module = self._add_node(
            "module",
            module_name,
            relative,
            1,
            max(1, len(lines)),
            text,
            {"module_name": module_name, "imports": [], "qualified_name": module_name},
        )
        extractor = _PythonSymbolExtractor(self, relative, lines, module)
        extractor.visit(tree)

    def _add_node(
        self,
        kind: str,
        title: str,
        path: str,
        line_start: int,
        line_end: int,
        content: str,
        attributes: dict[str, object],
    ) -> Node:
        node_id = _node_id(kind, path, line_start, line_end, title)
        node = Node(
            id=node_id,
            kind=kind,
            title=title,
            path=path,
            line_start=line_start,
            line_end=line_end,
            content=content,
            attributes=attributes,
        )
        self.nodes[node_id] = node
        return node

    def _add_edge(self, source: str, target: str, relation_type: str, reason: str) -> None:
        if source == target or source not in self.nodes or target not in self.nodes:
            return
        candidate = Edge(source=source, target=target, type=relation_type, reason=reason)
        if candidate not in self.edges:
            self.edges.append(candidate)

    def _connect_citations(self) -> None:
        for node in list(self.nodes.values()):
            if node.kind not in {"knowledge", "scenario"}:
                continue
            domain = str(node.attributes.get("domain", ""))
            sources = self._source_nodes_by_domain.get(domain, [])
            for reference in node.attributes.get("references", []):
                try:
                    source = sources[int(str(reference)) - 1]
                except (IndexError, ValueError):
                    continue
                self._add_edge(node.id, source, "cites", f"Markdown reference [{reference}] maps to the domain source list")

    def _connect_python_imports_and_calls(self) -> None:
        module_index = {
            str(node.attributes.get("module_name")): node.id
            for node in self.nodes.values()
            if node.kind == "module"
        }
        symbols_by_qualified: dict[str, str] = {}
        symbols_by_short_name: dict[str, list[str]] = defaultdict(list)
        for node in self.nodes.values():
            if node.kind in {"class", "function", "method"}:
                qualified = str(node.attributes.get("qualified_name", ""))
                name = str(node.attributes.get("symbol_name", ""))
                if qualified:
                    symbols_by_qualified[qualified] = node.id
                if name:
                    symbols_by_short_name[name].append(node.id)

        for pending in self.pending_imports:
            target = module_index.get(pending.module_name)
            if target:
                self._add_edge(pending.source_id, target, "imports", f"Static import of {pending.module_name}")
        for pending in self.pending_calls:
            target = symbols_by_qualified.get(pending.callee)
            if target is None:
                short_name = pending.callee.rsplit(".", 1)[-1]
                candidates = symbols_by_short_name.get(short_name, [])
                if len(candidates) == 1:
                    target = candidates[0]
            if target:
                self._add_edge(pending.source_id, target, "calls", f"Static call expression {pending.callee}")

    def _connect_shared_terms(self) -> None:
        eligible = [
            node
            for node in self.nodes.values()
            if node.kind in {"knowledge", "scenario", "class", "function", "method"}
        ]
        term_to_nodes: dict[str, list[str]] = defaultdict(list)
        for node in eligible:
            for term in _terms(f"{node.title}\n{node.content[:2000]}"):
                term_to_nodes[term].append(node.id)

        pairs: dict[tuple[str, str], set[str]] = defaultdict(set)
        for term, node_ids in term_to_nodes.items():
            unique_ids = sorted(set(node_ids))
            if len(unique_ids) < 2 or len(unique_ids) > 10:
                continue
            for index, source in enumerate(unique_ids):
                for target in unique_ids[index + 1 :]:
                    pairs[(source, target)].add(term)
        for (source, target), terms in sorted(pairs.items()):
            source_node = self.nodes[source]
            target_node = self.nodes[target]
            if source_node.path == target_node.path:
                continue
            selected = ", ".join(sorted(terms)[:3])
            self._add_edge(source, target, "shares_terms", f"Shared terms: {selected}")

    def _skip(self, path: Path, reason: str) -> None:
        self.files_skipped += 1
        if len(self.skipped) < MAX_SKIP_REPORT:
            try:
                relative = path.relative_to(self.root).as_posix()
            except ValueError:
                relative = "<outside-root>"
            self.skipped.append({"path": relative, "reason": reason})


class _PythonSymbolExtractor(ast.NodeVisitor):
    """Collect definitions and direct call/import relations from one module."""

    def __init__(self, builder: GraphBuilder, relative: str, lines: list[str], module: Node) -> None:
        self.builder = builder
        self.relative = relative
        self.lines = lines
        self.module = module
        self.parent_stack: list[Node] = [module]
        self.qualified_stack: list[str] = [str(module.attributes["module_name"])]
        self.call_owner: list[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.builder.pending_imports.append(PendingImport(self.module.id, alias.name))
            self.module.attributes["imports"].append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module and node.level == 0:
            self.builder.pending_imports.append(PendingImport(self.module.id, node.module))
            self.module.attributes["imports"].append(node.module)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        symbol = self._create_symbol("class", node.name, node)
        self._visit_with_symbol(node, symbol)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def visit_Call(self, node: ast.Call) -> None:
        if self.call_owner:
            callee = _call_name(node.func)
            if callee:
                self.builder.pending_calls.append(PendingCall(self.call_owner[-1], callee))
        self.generic_visit(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        kind = "method" if self.parent_stack[-1].kind == "class" else "function"
        symbol = self._create_symbol(kind, node.name, node)
        self._visit_with_symbol(node, symbol)

    def _create_symbol(self, kind: str, name: str, node: ast.AST) -> Node:
        qualified = ".".join([*self.qualified_stack, name])
        line_start = getattr(node, "lineno", 1)
        line_end = getattr(node, "end_lineno", line_start)
        signature = ""
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            try:
                signature = ast.unparse(node.args)
            except ValueError:
                signature = "..."
        display = f"{qualified}({signature})" if signature else qualified
        content = _line_slice(self.lines, line_start, line_end)
        attributes: dict[str, object] = {
            "qualified_name": qualified,
            "symbol_name": name,
            "parent_id": self.parent_stack[-1].id,
            "decorators": [_decorator_name(item) for item in getattr(node, "decorator_list", [])],
        }
        if signature:
            attributes["signature"] = signature
        docstring = ast.get_docstring(node)
        if docstring:
            attributes["docstring"] = docstring
        symbol = self.builder._add_node(kind, display, self.relative, line_start, line_end, content, attributes)
        self.builder._add_edge(self.parent_stack[-1].id, symbol.id, "contains", "Lexical containment in Python AST")
        return symbol

    def _visit_with_symbol(self, ast_node: ast.AST, symbol: Node) -> None:
        self.parent_stack.append(symbol)
        self.qualified_stack.append(str(symbol.attributes["symbol_name"]))
        if symbol.kind in {"function", "method"}:
            self.call_owner.append(symbol.id)
        self.generic_visit(ast_node)
        if symbol.kind in {"function", "method"}:
            self.call_owner.pop()
        self.qualified_stack.pop()
        self.parent_stack.pop()


def _node_id(kind: str, path: str, line_start: int, line_end: int, title: str) -> str:
    raw = f"{kind}\0{path}\0{line_start}\0{line_end}\0{title.casefold()}"
    return f"{kind}:{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"


def _knowledge_domain(relative: str) -> str:
    parts = Path(relative).parts
    return parts[1] if len(parts) > 2 and parts[0] == "knowledge" else "general"


def _module_name(relative: str) -> str:
    path = Path(relative)
    parts = list(path.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts) or "__root__"


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _clean_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _line_slice(lines: list[str], line_start: int, line_end: int) -> str:
    return "\n".join(lines[max(0, line_start - 1) : max(line_start, line_end)])


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def _decorator_name(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except ValueError:
        return "<unparseable>"


def _terms(text: str) -> set[str]:
    terms: set[str] = set()
    for value in re.findall(r"[A-Za-z][A-Za-z0-9_+.-]{1,}|[\u4e00-\u9fff]{2,12}", text):
        normalized = value.casefold().strip("._-")
        if len(normalized) >= 2 and normalized not in {"the", "and", "for", "with", "this", "that", "通过", "需要", "可以"}:
            terms.add(normalized)
    return terms

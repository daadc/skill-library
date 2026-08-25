"""Core data types for the read-only knowledge graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


@dataclass(frozen=True)
class Node:
    """A source-located, queryable unit of knowledge or code structure."""

    id: str
    kind: str
    title: str
    path: str
    line_start: int
    line_end: int
    content: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)

    def summary(self, score: int | None = None, snippet_limit: int = 360) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "kind": self.kind,
            "title": self.title,
            "path": self.path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "attributes": self.attributes,
        }
        if score is not None:
            result["score"] = score
        if self.content:
            result["snippet"] = truncate(self.content, snippet_limit)
        return result

    def detail(self, content_limit: int = 8_000) -> dict[str, Any]:
        result = self.summary()
        result["content"] = truncate(self.content, content_limit)
        result["content_truncated"] = len(self.content) > content_limit
        return result


@dataclass(frozen=True)
class Edge:
    """A typed, explainable relation between two nodes."""

    source: str
    target: str
    type: str
    reason: str

    def to_dict(self, direction: str = "outbound") -> dict[str, str]:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "reason": self.reason,
            "direction": direction,
        }


@dataclass(frozen=True)
class IndexReport:
    """Operationally useful, but non-sensitive, details of a build."""

    snapshot_id: str
    root_name: str
    files_indexed: int
    files_skipped: int
    nodes: int
    edges: int
    duration_ms: int
    languages: list[str]
    skipped: list[dict[str, str]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "root_name": self.root_name,
            "files_indexed": self.files_indexed,
            "files_skipped": self.files_skipped,
            "nodes": self.nodes,
            "edges": self.edges,
            "duration_ms": self.duration_ms,
            "languages": self.languages,
            "skipped": self.skipped,
        }


@dataclass(frozen=True)
class GraphSnapshot:
    """An immutable graph assembled from one successful index operation."""

    snapshot_id: str
    nodes: dict[str, Node]
    edges: tuple[Edge, ...]
    report: IndexReport

    def __post_init__(self) -> None:
        adjacency: dict[str, list[tuple[Edge, str]]] = {node_id: [] for node_id in self.nodes}
        for edge in self.edges:
            if edge.source in adjacency and edge.target in self.nodes:
                adjacency[edge.source].append((edge, "outbound"))
                adjacency[edge.target].append((edge, "inbound"))
        object.__setattr__(self, "_adjacency", adjacency)

    def related(self, node_id: str) -> list[tuple[Edge, str]]:
        return list(self._adjacency.get(node_id, []))

    def matching_nodes(self, node_ids: Iterable[str]) -> list[Node]:
        return [self.nodes[node_id] for node_id in node_ids if node_id in self.nodes]


class ServiceError(ValueError):
    """A stable, safe error returned by MCP tools for expected failures."""

    def __init__(self, code: str, message: str, **details: Any) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details:
            result["details"] = self.details
        return result


def truncate(text: str, limit: int) -> str:
    """Return a human-readable truncation while preserving a bounded output size."""

    if limit < 1:
        return ""
    if len(text) <= limit:
        return text
    if limit <= 16:
        return text[:limit]
    return f"{text[: limit - 16].rstrip()} … [truncated]"

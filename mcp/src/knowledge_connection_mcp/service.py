"""Service layer for bounded local indexing, persistence, and knowledge queries."""

from __future__ import annotations

import re
import threading
from collections import deque
from pathlib import Path
from typing import Any

from .indexer import GraphBuilder, _is_relative_to
from .models import GraphSnapshot, ServiceError, truncate
from .storage import LocalSnapshotStore, build_manifest

MAX_LIMIT = 50
MAX_DEPTH = 3
MAX_CONTEXT_CHARS = 20_000


class KnowledgeConnectionService:
    """Owns one allowed root and its latest complete, read-only graph snapshot."""

    def __init__(self, allowed_root: Path) -> None:
        self.allowed_root = allowed_root.resolve()
        self._snapshot: GraphSnapshot | None = None
        self._store: LocalSnapshotStore | None = None
        self._lock = threading.RLock()

    def index_repository(
        self,
        root: str | None = None,
        include_code: bool = True,
        include_knowledge: bool = True,
        max_files: int = 5_000,
        force: bool = False,
    ) -> dict[str, Any]:
        """Load a matching local snapshot or explicitly build and persist a new one."""

        if not include_code and not include_knowledge:
            raise ServiceError("invalid_input", "At least one of include_code or include_knowledge must be true.")
        target_root = self._resolve_root(root)
        settings = {
            "include_code": include_code,
            "include_knowledge": include_knowledge,
            "max_files": max_files,
        }
        builder = GraphBuilder(target_root, include_code=include_code, include_knowledge=include_knowledge)
        paths = builder.candidate_files()
        if len(paths) > max_files:
            raise ServiceError(
                "resource_limit",
                "The repository exceeds the configured max_files limit.",
                max_files=max_files,
            )
        manifest = build_manifest(target_root, paths)
        store = LocalSnapshotStore(target_root)
        if not force and store.has_matching_manifest(manifest, settings):
            cached = store.load_snapshot()
            if cached is not None:
                with self._lock:
                    self._snapshot = cached
                    self._store = store
                return {**cached.report.to_dict(), "index_mode": "cached", "changed_files": 0}

        previous_snapshot = store.load_snapshot()
        previous_manifest = store.manifest() if previous_snapshot is not None else {}
        changed_paths = _changed_paths(previous_manifest, manifest)
        changed_files = len(changed_paths) if previous_snapshot is not None else len(manifest)
        incremental = previous_snapshot is not None and _can_incrementally_rebuild(changed_paths)
        if incremental:
            current_paths = {path.relative_to(target_root).as_posix(): path for path in paths}
            seeded_nodes = {
                node_id: node
                for node_id, node in previous_snapshot.nodes.items()
                if node.path not in changed_paths
            }
            seeded_ids = set(seeded_nodes)
            seeded_edges = tuple(
                edge
                for edge in previous_snapshot.edges
                if edge.source in seeded_ids and edge.target in seeded_ids
            )
            candidate = builder.build(
                max_files=max_files,
                paths=[current_paths[path] for path in changed_paths if path in current_paths],
                seed_nodes=seeded_nodes,
                seed_edges=seeded_edges,
                total_files=len(paths),
            )
        else:
            candidate = builder.build(max_files=max_files)
        store.save_snapshot(candidate, manifest, settings)
        with self._lock:
            self._snapshot = candidate
            self._store = store
        return {
            **candidate.report.to_dict(),
            "index_mode": "full" if previous_snapshot is None else ("incremental" if incremental else "refreshed"),
            "changed_files": changed_files,
        }

    def refresh_repository(
        self,
        root: str | None = None,
        include_code: bool = True,
        include_knowledge: bool = True,
        max_files: int = 5_000,
    ) -> dict[str, Any]:
        """Force a fresh graph build while retaining the last successful in-memory snapshot on failure."""

        return self.index_repository(
            root=root,
            include_code=include_code,
            include_knowledge=include_knowledge,
            max_files=max_files,
            force=True,
        )

    def index_status(self, root: str | None = None) -> dict[str, Any]:
        target_root = self._resolve_root(root)
        store = LocalSnapshotStore(target_root)
        status = store.status()
        with self._lock:
            if self._snapshot is not None and self._store and self._store.root == target_root:
                status["active_snapshot_id"] = self._snapshot.snapshot_id
            else:
                status["active_snapshot_id"] = None
        return status

    def search_knowledge(
        self,
        query: str,
        kinds: list[str] | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        snapshot = self._require_snapshot()
        query = _validate_query(query)
        limit = _bounded(limit, "limit", 1, MAX_LIMIT)
        accepted_kinds = {"knowledge", "scenario", "source", "module", "class", "function", "method"}
        if kinds is not None:
            unknown = sorted(set(kinds).difference(accepted_kinds))
            if unknown:
                raise ServiceError("invalid_input", "kinds contains unsupported node kinds.", unsupported=unknown)
            wanted = set(kinds)
        else:
            wanted = accepted_kinds

        fts_bonus: dict[str, int] = {}
        if self._store is not None:
            for rank, node_id in enumerate(self._store.fts_node_ids(query, limit=MAX_LIMIT)):
                fts_bonus[node_id] = max(1, 30 - rank)

        scored: list[tuple[int, str, str]] = []
        for node in snapshot.nodes.values():
            if node.kind not in wanted:
                continue
            score = _score_node(query, node.kind, node.title, node.content, node.attributes) + fts_bonus.get(node.id, 0)
            if score:
                scored.append((score, node.title.casefold(), node.id))
        scored.sort(key=lambda item: (-item[0], item[1], item[2]))
        matches = [snapshot.nodes[node_id].summary(score=score) for score, _, node_id in scored[:limit]]
        return {
            "snapshot_id": snapshot.snapshot_id,
            "query": query,
            "matches": matches,
            "total_candidates": len(scored),
            "ranking": "field-weighted + optional local FTS5 bonus",
        }

    def get_node(self, node_id: str, include_content: bool = True) -> dict[str, Any]:
        snapshot = self._require_snapshot()
        node = snapshot.nodes.get(node_id)
        if node is None:
            raise ServiceError("not_found", "The requested node does not exist in the current snapshot.", node_id=node_id)
        detail = node.detail() if include_content else node.summary()
        relationships = [edge.to_dict(direction) for edge, direction in snapshot.related(node_id)[:MAX_LIMIT]]
        return {"snapshot_id": snapshot.snapshot_id, "node": detail, "relationships": relationships}

    def explore_connections(
        self,
        node_id: str,
        relation_types: list[str] | None = None,
        depth: int = 1,
        limit: int = 25,
    ) -> dict[str, Any]:
        snapshot = self._require_snapshot()
        if node_id not in snapshot.nodes:
            raise ServiceError("not_found", "The requested node does not exist in the current snapshot.", node_id=node_id)
        depth = _bounded(depth, "depth", 1, MAX_DEPTH)
        limit = _bounded(limit, "limit", 1, MAX_LIMIT)
        valid_relations = {"contains", "cites", "imports", "calls", "shares_terms"}
        if relation_types is not None:
            unsupported = sorted(set(relation_types).difference(valid_relations))
            if unsupported:
                raise ServiceError("invalid_input", "relation_types contains unsupported relations.", unsupported=unsupported)
            allowed = set(relation_types)
        else:
            allowed = valid_relations

        queue: deque[tuple[str, int]] = deque([(node_id, 0)])
        visited = {node_id}
        connections: list[dict[str, Any]] = []
        truncated = False
        while queue:
            current, current_depth = queue.popleft()
            if current_depth >= depth:
                continue
            for edge, direction in snapshot.related(current):
                if edge.type not in allowed:
                    continue
                neighbor_id = edge.target if direction == "outbound" else edge.source
                if neighbor_id in visited:
                    continue
                visited.add(neighbor_id)
                neighbor = snapshot.nodes[neighbor_id]
                connections.append(
                    {
                        "node": neighbor.summary(),
                        "relationship": edge.to_dict(direction),
                        "distance": current_depth + 1,
                    }
                )
                if len(connections) >= limit:
                    truncated = bool(queue) or any(snapshot.related(neighbor_id))
                    break
                queue.append((neighbor_id, current_depth + 1))
            if len(connections) >= limit:
                break
        return {
            "snapshot_id": snapshot.snapshot_id,
            "seed": snapshot.nodes[node_id].summary(),
            "connections": connections,
            "truncated": truncated,
        }

    def build_context_pack(
        self,
        query: str,
        max_chars: int = 8_000,
        include_code: bool = True,
    ) -> dict[str, Any]:
        snapshot = self._require_snapshot()
        query = _validate_query(query)
        max_chars = _bounded(max_chars, "max_chars", 200, MAX_CONTEXT_CHARS)
        kinds = None if include_code else ["knowledge", "scenario", "source"]
        search = self.search_knowledge(query=query, kinds=kinds, limit=MAX_LIMIT)
        if not search["matches"]:
            return {
                "snapshot_id": snapshot.snapshot_id,
                "query": query,
                "context": "No indexed nodes matched the query.",
                "node_ids": [],
                "citations": [],
                "truncated": False,
            }

        pieces: list[str] = []
        node_ids: list[str] = []
        citations: list[dict[str, Any]] = []
        used = 0
        truncated = False
        for match in search["matches"]:
            node = snapshot.nodes[match["id"]]
            header = f"## {node.title}\nLocation: {node.path}:{node.line_start}-{node.line_end}\n"
            remaining = max_chars - used - len(header) - 2
            if remaining <= 0:
                truncated = True
                break
            body = truncate(node.content.strip(), remaining)
            piece = f"{header}{body}\n"
            pieces.append(piece)
            used += len(piece)
            node_ids.append(node.id)
            citations.append(_citation(node))
            if len(body) < len(node.content.strip()):
                truncated = True
                break
            for edge, direction in snapshot.related(node.id):
                if edge.type != "cites":
                    continue
                source_id = edge.target if direction == "outbound" else edge.source
                source = snapshot.nodes.get(source_id)
                if source and source.id not in node_ids:
                    citation = _citation(source)
                    if citation not in citations:
                        citations.append(citation)

        return {
            "snapshot_id": snapshot.snapshot_id,
            "query": query,
            "context": "\n".join(pieces).strip(),
            "node_ids": node_ids,
            "citations": citations,
            "truncated": truncated or len(node_ids) < min(len(search["matches"]), MAX_LIMIT),
        }

    def _resolve_root(self, root: str | None) -> Path:
        if root is None or not root.strip():
            candidate = self.allowed_root
        else:
            requested = Path(root).expanduser()
            candidate = requested.resolve() if requested.is_absolute() else (self.allowed_root / requested).resolve()
        if not _is_relative_to(candidate, self.allowed_root):
            raise ServiceError("invalid_root", "The requested root is outside this server's allowed root.")
        if not candidate.exists() or not candidate.is_dir():
            raise ServiceError("invalid_root", "The requested root is not a readable directory.")
        return candidate

    def _require_snapshot(self) -> GraphSnapshot:
        with self._lock:
            if self._snapshot is None:
                raise ServiceError("not_indexed", "No repository has been indexed in this server session.")
            return self._snapshot


def _changed_paths(previous: dict[str, str], current: dict[str, str]) -> set[str]:
    all_paths = set(previous).union(current)
    return {path for path in all_paths if previous.get(path) != current.get(path)}


def _can_incrementally_rebuild(changed_paths: set[str]) -> bool:
    """Only Markdown section changes are safely composable without re-evaluating code imports/calls."""

    return bool(changed_paths) and all(path.endswith(".md") for path in changed_paths)


def _validate_query(query: str) -> str:
    if not isinstance(query, str) or not query.strip():
        raise ServiceError("invalid_input", "query must contain non-whitespace text.")
    if len(query) > 500:
        raise ServiceError("invalid_input", "query must not exceed 500 characters.")
    return query.strip()


def _bounded(value: int, field: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ServiceError("invalid_input", f"{field} must be an integer between {minimum} and {maximum}.")
    return value


def _score_node(
    query: str,
    kind: str,
    title: str,
    content: str,
    attributes: dict[str, Any],
) -> int:
    query_folded = query.casefold()
    title_folded = title.casefold()
    content_folded = content.casefold()
    attribute_text = " ".join(str(value) for value in attributes.values()).casefold()
    document_title = str(attributes.get("document_title", "")).casefold()
    score = 0
    if query_folded in title_folded:
        score += 100
    if query_folded in content_folded:
        score += 35
    if query_folded in attribute_text:
        score += 20
    if document_title and query_folded in document_title:
        score += 60
    for term in _search_terms(query):
        if term in title_folded:
            score += 18
        elif term in content_folded:
            score += 6
        elif term in document_title:
            score += 12
        elif term in attribute_text:
            score += 4
    if score:
        score += {"knowledge": 55, "scenario": 45, "source": 25}.get(kind, 0)
    return score


def _search_terms(value: str) -> set[str]:
    terms = set(re.findall(r"[A-Za-z][A-Za-z0-9_+.-]*", value.casefold()))
    for sequence in re.findall(r"[\u4e00-\u9fff]+", value):
        if len(sequence) == 1:
            terms.add(sequence)
            continue
        terms.add(sequence)
        terms.update(sequence[index : index + 2] for index in range(len(sequence) - 1))
    return {term for term in terms if term}


def _citation(node: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "node_id": node.id,
        "title": node.title,
        "path": node.path,
        "line_start": node.line_start,
        "line_end": node.line_end,
    }
    url = node.attributes.get("url")
    if url:
        result["url"] = url
    return result

"""Local, rebuildable SQLite storage for read-only graph snapshots."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import Edge, GraphSnapshot, IndexReport, Node, ServiceError

STATE_DIRECTORY = ".knowledge-connection"
DATABASE_NAME = "graph.sqlite3"
SCHEMA_VERSION = "1"


class LocalSnapshotStore:
    """Persists only derived local state under a repository-owned state directory."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.state_directory = self.root / STATE_DIRECTORY
        self.database_path = self.state_directory / DATABASE_NAME

    def load_snapshot(self) -> GraphSnapshot | None:
        if not self.database_path.exists():
            return None
        with self._connect() as connection:
            metadata = _metadata(connection)
            if metadata.get("schema_version") != SCHEMA_VERSION or "report" not in metadata:
                return None
            try:
                report_data = json.loads(metadata["report"])
                nodes = {
                    row[0]: Node(
                        id=row[0],
                        kind=row[1],
                        title=row[2],
                        path=row[3],
                        line_start=row[4],
                        line_end=row[5],
                        content=row[6],
                        attributes=json.loads(row[7]),
                    )
                    for row in connection.execute(
                        "SELECT id, kind, title, path, line_start, line_end, content, attributes_json FROM nodes"
                    )
                }
                edges = tuple(
                    Edge(source=row[0], target=row[1], type=row[2], reason=row[3])
                    for row in connection.execute("SELECT source, target, type, reason FROM edges")
                )
                report = IndexReport(
                    snapshot_id=str(report_data["snapshot_id"]),
                    root_name=str(report_data["root_name"]),
                    files_indexed=int(report_data["files_indexed"]),
                    files_skipped=int(report_data["files_skipped"]),
                    nodes=int(report_data["nodes"]),
                    edges=int(report_data["edges"]),
                    duration_ms=int(report_data["duration_ms"]),
                    languages=list(report_data["languages"]),
                    skipped=list(report_data["skipped"]),
                )
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                return None
        return GraphSnapshot(snapshot_id=report.snapshot_id, nodes=nodes, edges=edges, report=report)

    def save_snapshot(self, snapshot: GraphSnapshot, manifest: dict[str, str], settings: dict[str, Any]) -> None:
        self.state_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        with self._connect() as connection:
            self._initialize(connection)
            connection.execute("BEGIN IMMEDIATE")
            try:
                connection.execute("DELETE FROM nodes")
                connection.execute("DELETE FROM edges")
                connection.execute("DELETE FROM files")
                connection.execute("DELETE FROM nodes_fts")
                connection.executemany(
                    "INSERT INTO nodes(id, kind, title, path, line_start, line_end, content, attributes_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        (
                            node.id,
                            node.kind,
                            node.title,
                            node.path,
                            node.line_start,
                            node.line_end,
                            node.content,
                            json.dumps(node.attributes, ensure_ascii=False, sort_keys=True),
                        )
                        for node in snapshot.nodes.values()
                    ],
                )
                connection.executemany(
                    "INSERT INTO nodes_fts(node_id, title, content) VALUES (?, ?, ?)",
                    [(node.id, node.title, node.content) for node in snapshot.nodes.values()],
                )
                connection.executemany(
                    "INSERT INTO edges(source, target, type, reason) VALUES (?, ?, ?, ?)",
                    [(edge.source, edge.target, edge.type, edge.reason) for edge in snapshot.edges],
                )
                connection.executemany(
                    "INSERT INTO files(path, digest) VALUES (?, ?)", sorted(manifest.items()),
                )
                _put_metadata(connection, "schema_version", SCHEMA_VERSION)
                _put_metadata(connection, "report", json.dumps(snapshot.report.to_dict(), ensure_ascii=False, sort_keys=True))
                _put_metadata(connection, "settings", json.dumps(settings, ensure_ascii=False, sort_keys=True))
                connection.commit()
            except Exception:
                connection.rollback()
                raise

    def has_matching_manifest(self, manifest: dict[str, str], settings: dict[str, Any]) -> bool:
        if not self.database_path.exists():
            return False
        with self._connect() as connection:
            metadata = _metadata(connection)
            if metadata.get("schema_version") != SCHEMA_VERSION:
                return False
            try:
                stored_settings = json.loads(metadata.get("settings", "{}"))
            except json.JSONDecodeError:
                return False
            if stored_settings != settings:
                return False
            stored_manifest = dict(connection.execute("SELECT path, digest FROM files"))
        return stored_manifest == manifest

    def manifest(self) -> dict[str, str]:
        if not self.database_path.exists():
            return {}
        with self._connect() as connection:
            return {str(row[0]): str(row[1]) for row in connection.execute("SELECT path, digest FROM files")}

    def status(self) -> dict[str, Any]:
        if not self.database_path.exists():
            return {"persistent": False, "state_directory": str(self.state_directory), "snapshot_id": None}
        with self._connect() as connection:
            metadata = _metadata(connection)
            report = json.loads(metadata["report"]) if "report" in metadata else {}
            files = int(connection.execute("SELECT COUNT(*) FROM files").fetchone()[0])
            nodes = int(connection.execute("SELECT COUNT(*) FROM nodes").fetchone()[0])
            edges = int(connection.execute("SELECT COUNT(*) FROM edges").fetchone()[0])
        return {
            "persistent": True,
            "state_directory": str(self.state_directory),
            "snapshot_id": report.get("snapshot_id"),
            "files": files,
            "nodes": nodes,
            "edges": edges,
        }

    def fts_node_ids(self, query: str, limit: int) -> list[str]:
        """Return FTS-ranked IDs for ASCII-style terms; invalid syntax returns no bonus."""

        terms = [term for term in query.split() if term.isascii() and term.replace("_", "").isalnum()]
        if not terms or not self.database_path.exists():
            return []
        match_expression = " OR ".join(f'"{term}"' for term in terms[:8])
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    "SELECT node_id FROM nodes_fts WHERE nodes_fts MATCH ? ORDER BY bm25(nodes_fts) LIMIT ?",
                    (match_expression, limit),
                ).fetchall()
        except sqlite3.Error:
            return []
        return [str(row[0]) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self, connection: sqlite3.Connection) -> None:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS metadata (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS files (
              path TEXT PRIMARY KEY,
              digest TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS nodes (
              id TEXT PRIMARY KEY,
              kind TEXT NOT NULL,
              title TEXT NOT NULL,
              path TEXT NOT NULL,
              line_start INTEGER NOT NULL,
              line_end INTEGER NOT NULL,
              content TEXT NOT NULL,
              attributes_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS edges (
              source TEXT NOT NULL,
              target TEXT NOT NULL,
              type TEXT NOT NULL,
              reason TEXT NOT NULL,
              PRIMARY KEY (source, target, type, reason)
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS nodes_fts USING fts5(
              node_id UNINDEXED,
              title,
              content,
              tokenize = 'unicode61'
            );
            """
        )


def build_manifest(root: Path, paths: list[Path]) -> dict[str, str]:
    """Hash only caller-approved regular files; the digest is never executed or trusted as code."""

    manifest: dict[str, str] = {}
    for path in paths:
        try:
            relative = path.relative_to(root).as_posix()
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as error:
            raise ServiceError("parse_error", "Unable to fingerprint an indexed file.", path=str(path)) from error
        manifest[relative] = digest
    return manifest


def _metadata(connection: sqlite3.Connection) -> dict[str, str]:
    return {str(row[0]): str(row[1]) for row in connection.execute("SELECT key, value FROM metadata")}


def _put_metadata(connection: sqlite3.Connection, key: str, value: str) -> None:
    connection.execute(
        "INSERT INTO metadata(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )

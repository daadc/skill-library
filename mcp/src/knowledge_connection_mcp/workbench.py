"""Loopback-only local workbench for inspecting a read-only knowledge graph."""

from __future__ import annotations

import json
import mimetypes
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .models import ServiceError
from .service import KnowledgeConnectionService

WEB_ROOT = Path(__file__).with_name("web")
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
MAX_REQUEST_PATH = 4_096


class KnowledgeWorkbenchServer(ThreadingHTTPServer):
    """A local-only HTTP server carrying one bounded service instance."""

    daemon_threads = True

    def __init__(self, address: tuple[str, int], service: KnowledgeConnectionService) -> None:
        super().__init__(address, KnowledgeWorkbenchHandler)
        self.service = service
        self.state_lock = threading.RLock()


class KnowledgeWorkbenchHandler(BaseHTTPRequestHandler):
    """Serve fixed static assets and a deliberately small same-origin API surface."""

    server: KnowledgeWorkbenchServer

    def do_GET(self) -> None:  # noqa: N802
        if len(self.path) > MAX_REQUEST_PATH:
            self._error(ServiceError("invalid_input", "Request path exceeds the local workbench limit."))
            return
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/status":
                self._json(self.server.service.index_status())
            elif parsed.path == "/api/search":
                query = _single_query_value(parsed.query, "q")
                limit = _int_query_value(parsed.query, "limit", 10)
                self._json(self.server.service.search_knowledge(query=query, limit=limit))
            elif parsed.path == "/api/node":
                node_id = _single_query_value(parsed.query, "id")
                self._json(self.server.service.get_node(node_id=node_id))
            elif parsed.path == "/api/connections":
                node_id = _single_query_value(parsed.query, "id")
                depth = _int_query_value(parsed.query, "depth", 1)
                self._json(self.server.service.explore_connections(node_id=node_id, depth=depth))
            elif parsed.path == "/api/context":
                query = _single_query_value(parsed.query, "q")
                max_chars = _int_query_value(parsed.query, "max_chars", 4_000)
                self._json(self.server.service.build_context_pack(query=query, max_chars=max_chars))
            else:
                self._static(parsed.path)
        except ServiceError as error:
            self._error(error)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/api/refresh":
            self._send_json(HTTPStatus.NOT_FOUND, {"code": "not_found", "message": "Unknown workbench endpoint."})
            return
        if self.headers.get("Content-Length", "0") not in {"", "0"}:
            self._error(ServiceError("invalid_input", "The refresh endpoint does not accept a request body."))
            return
        try:
            with self.server.state_lock:
                self._json(self.server.service.refresh_repository())
        except ServiceError as error:
            self._error(error)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        """Avoid recording search text or source content in normal HTTP logs."""

    def _static(self, request_path: str) -> None:
        filename = "index.html" if request_path in {"", "/"} else request_path.removeprefix("/")
        if filename not in {"index.html", "app.js", "styles.css"}:
            self._send_json(HTTPStatus.NOT_FOUND, {"code": "not_found", "message": "Unknown workbench asset."})
            return
        content_path = WEB_ROOT / filename
        try:
            content = content_path.read_bytes()
        except OSError:
            self._send_json(HTTPStatus.NOT_FOUND, {"code": "not_found", "message": "Workbench asset unavailable."})
            return
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def _json(self, payload: dict[str, Any]) -> None:
        self._send_json(HTTPStatus.OK, payload)

    def _error(self, error: ServiceError) -> None:
        status = HTTPStatus.NOT_FOUND if error.code == "not_found" else HTTPStatus.BAD_REQUEST
        self._send_json(status, error.to_dict())

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)


def create_workbench_server(root: Path, host: str = "127.0.0.1", port: int = 8765) -> KnowledgeWorkbenchServer:
    """Create a local server; non-loopback host values are rejected before binding."""

    if host not in LOOPBACK_HOSTS:
        raise ServiceError("invalid_input", "Workbench may bind only to a loopback host.")
    if not 0 <= port <= 65_535:
        raise ServiceError("invalid_input", "port must be between 0 and 65535.")
    service = KnowledgeConnectionService(root.resolve())
    service.index_repository()
    return KnowledgeWorkbenchServer((host, port), service)


def run_workbench(root: Path, host: str = "127.0.0.1", port: int = 8765) -> None:
    server = create_workbench_server(root=root, host=host, port=port)
    active_host, active_port = server.server_address[:2]
    print(f"Knowledge workbench listening on http://{active_host}:{active_port}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def _single_query_value(query: str, name: str) -> str:
    values = parse_qs(query, keep_blank_values=True).get(name, [])
    if len(values) != 1:
        raise ServiceError("invalid_input", f"{name} must be supplied exactly once.")
    return values[0]


def _int_query_value(query: str, name: str, default: int) -> int:
    values = parse_qs(query, keep_blank_values=True).get(name, [])
    if not values:
        return default
    if len(values) != 1:
        raise ServiceError("invalid_input", f"{name} must be supplied at most once.")
    try:
        return int(values[0])
    except ValueError as error:
        raise ServiceError("invalid_input", f"{name} must be an integer.") from error

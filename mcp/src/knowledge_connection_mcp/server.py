"""stdio MCP entry point for the knowledge connection service."""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from .models import ServiceError
from .service import KnowledgeConnectionService

LOGGER = logging.getLogger(__name__)


def create_server(allowed_root: Path) -> FastMCP:
    """Create a server bound to a single local root with only read-only tools."""

    service = KnowledgeConnectionService(allowed_root=allowed_root)
    server = FastMCP(
        name="Knowledge Connection MCP",
        instructions=(
            "Use index_repository before querying. All tools are local and read-only; "
            "answers include source locations so you can inspect evidence before reasoning."
        ),
    )

    @server.tool(
        name="index_repository",
        description=(
            "Build or reload a local persistent, read-only graph for the allowed repository root. "
            "Parses knowledge Markdown/YAML and Python AST; does not write source files, execute code, or fetch data."
        ),
        structured_output=True,
    )
    def index_repository(
        root: str | None = None,
        include_code: bool = True,
        include_knowledge: bool = True,
        max_files: int = 5_000,
    ) -> dict[str, Any]:
        return _run_tool(
            "index_repository",
            service.index_repository,
            root=root,
            include_code=include_code,
            include_knowledge=include_knowledge,
            max_files=max_files,
        )

    @server.tool(
        name="index_status",
        description="Show whether a local persistent graph snapshot exists and whether it is active in this session.",
        structured_output=True,
    )
    def index_status(root: str | None = None) -> dict[str, Any]:
        return _run_tool("index_status", service.index_status, root=root)

    @server.tool(
        name="refresh_repository",
        description=(
            "Explicitly rebuild the local persistent graph after source changes. "
            "This writes only derived state under .knowledge-connection, never indexed source files."
        ),
        structured_output=True,
    )
    def refresh_repository(
        root: str | None = None,
        include_code: bool = True,
        include_knowledge: bool = True,
        max_files: int = 5_000,
    ) -> dict[str, Any]:
        return _run_tool(
            "refresh_repository",
            service.refresh_repository,
            root=root,
            include_code=include_code,
            include_knowledge=include_knowledge,
            max_files=max_files,
        )

    @server.tool(
        name="search_knowledge",
        description=(
            "Search indexed knowledge cards, sources, scenarios, and Python symbols. "
            "Returns ranked, source-located summaries only from the current snapshot."
        ),
        structured_output=True,
    )
    def search_knowledge(
        query: str,
        kinds: list[str] | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        return _run_tool("search_knowledge", service.search_knowledge, query=query, kinds=kinds, limit=limit)

    @server.tool(
        name="get_node",
        description="Retrieve one indexed node with its full bounded content and direct, explained relationships.",
        structured_output=True,
    )
    def get_node(node_id: str, include_content: bool = True) -> dict[str, Any]:
        return _run_tool("get_node", service.get_node, node_id=node_id, include_content=include_content)

    @server.tool(
        name="explore_connections",
        description=(
            "Explore typed graph connections from a knowledge or code node. "
            "Relations are limited to lexical containment, citations, imports, direct calls, and shared terms."
        ),
        structured_output=True,
    )
    def explore_connections(
        node_id: str,
        relation_types: list[str] | None = None,
        depth: int = 1,
        limit: int = 25,
    ) -> dict[str, Any]:
        return _run_tool(
            "explore_connections",
            service.explore_connections,
            node_id=node_id,
            relation_types=relation_types,
            depth=depth,
            limit=limit,
        )

    @server.tool(
        name="build_context_pack",
        description=(
            "Create a bounded, evidence-oriented context pack for an AI task. "
            "Keeps source locations, relevant knowledge, code symbols, risks, validation text, and citations."
        ),
        structured_output=True,
    )
    def build_context_pack(
        query: str,
        max_chars: int = 8_000,
        include_code: bool = True,
    ) -> dict[str, Any]:
        return _run_tool(
            "build_context_pack",
            service.build_context_pack,
            query=query,
            max_chars=max_chars,
            include_code=include_code,
        )

    return server


def _run_tool(name: str, function: Any, /, **kwargs: Any) -> dict[str, Any]:
    try:
        return function(**kwargs)
    except ServiceError as error:
        LOGGER.info("tool=%s code=%s", name, error.code)
        raise ToolError(json.dumps(error.to_dict(), ensure_ascii=False)) from error
    except Exception as error:  # pragma: no cover - defensive MCP boundary
        LOGGER.exception("tool=%s unexpected_error", name)
        payload = {"code": "internal_error", "message": "An unexpected internal error occurred."}
        raise ToolError(json.dumps(payload, ensure_ascii=False)) from error


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the local Knowledge Connection MCP server over stdio.")
    parser.add_argument(
        "--root",
        default=os.environ.get("KNOWLEDGE_MCP_ROOT"),
        help="Allowed repository root. Defaults to the current directory, or KNOWLEDGE_MCP_ROOT when set.",
    )
    args = parser.parse_args(argv)
    allowed_root = Path(args.root).expanduser() if args.root else Path.cwd()
    server = create_server(allowed_root.resolve())
    server.run(transport="stdio")


if __name__ == "__main__":
    main()

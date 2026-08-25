"""Run a real stdio MCP session against the server without modifying client configuration."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def run_smoke_test() -> None:
    mcp_root = Path(__file__).resolve().parents[1]
    repository_root = mcp_root.parent
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(mcp_root / "src")
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "knowledge_connection_mcp.server", "--root", str(repository_root)],
        cwd=str(mcp_root),
        env=environment,
    )
    async with stdio_client(parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = {tool.name for tool in tools.tools}
            expected = {
                "index_repository",
                "index_status",
                "refresh_repository",
                "search_knowledge",
                "get_node",
                "explore_connections",
                "build_context_pack",
            }
            assert names == expected, f"Unexpected MCP tool set: {sorted(names)}"

            before = await session.call_tool("index_status", {})
            assert not before.isError, before
            indexed = await session.call_tool("index_repository", {})
            assert not indexed.isError, indexed
            refreshed = await session.call_tool("refresh_repository", {})
            assert not refreshed.isError, refreshed
            searched = await session.call_tool(
                "search_knowledge",
                {"query": "需求分析", "kinds": ["knowledge"], "limit": 3},
            )
            assert not searched.isError, searched
            structured = getattr(searched, "structuredContent", None)
            assert structured and structured["matches"], structured
            print("MCP stdio smoke test passed: seven tools registered; status, index, refresh, and search returned structured output.")


if __name__ == "__main__":
    asyncio.run(run_smoke_test())

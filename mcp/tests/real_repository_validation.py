"""Index this repository and exercise representative knowledge retrieval paths."""

from __future__ import annotations

import json
from pathlib import Path

from knowledge_connection_mcp.service import KnowledgeConnectionService


def main() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    service = KnowledgeConnectionService(repository_root)
    report = service.index_repository()

    queries = ["受约束 Agent", "风险测试", "PostgreSQL", "安全交付"]
    searches: list[dict[str, object]] = []
    first_node_id: str | None = None
    for query in queries:
        result = service.search_knowledge(query=query, limit=3)
        matches = result["matches"]
        assert matches, f"Query should find repository evidence: {query}"
        assert matches[0]["kind"] in {"knowledge", "scenario", "source"}, (
            f"Knowledge-oriented query should prefer a knowledge node: {query}"
        )
        if first_node_id is None:
            first_node_id = str(matches[0]["id"])
        searches.append(
            {
                "query": query,
                "total_candidates": result["total_candidates"],
                "top_matches": [
                    {
                        "title": item["title"],
                        "kind": item["kind"],
                        "path": item["path"],
                        "line_start": item["line_start"],
                        "score": item["score"],
                    }
                    for item in matches
                ],
            }
        )

    assert first_node_id is not None, "Representative queries should return at least one node."
    node = service.get_node(first_node_id, include_content=False)
    connections = service.explore_connections(first_node_id, depth=2, limit=10)
    context = service.build_context_pack("受约束 Agent 的需求分析、架构和验证流程", max_chars=2_500)
    assert context["node_ids"], "Context pack should contain repository evidence."

    output = {
        "repository": repository_root.name,
        "index_report": report,
        "searches": searches,
        "inspected_node": {
            "id": node["node"]["id"],
            "title": node["node"]["title"],
            "direct_relationships": len(node["relationships"]),
            "neighborhood_size": len(connections["connections"]),
        },
        "context_pack": {
            "node_count": len(context["node_ids"]),
            "citation_count": len(context["citations"]),
            "characters": len(context["context"]),
            "truncated": context["truncated"],
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from knowledge_connection_mcp.models import ServiceError
from knowledge_connection_mcp.service import KnowledgeConnectionService


class KnowledgeConnectionServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "repository"
        self.root.mkdir()
        knowledge = self.root / "knowledge" / "testing"
        knowledge.mkdir(parents=True)
        (knowledge / "knowledge-cards.md").write_text(
            """# 测试工程知识卡

## KC-TEST-001：输入校验应位于信任边界

**原则。** 在 API 和命令入口验证不可信输入，避免错误传播到核心逻辑。

**风险。** 无效输入会产生不一致状态。

**验证。** 用无效请求的测试验证稳定错误码。[1]

## KC-TEST-002：失败路径也是行为

**原则。** 为超时和依赖失败建立可恢复的失败语义。
""",
            encoding="utf-8",
        )
        (knowledge / "scenarios.md").write_text(
            """# 测试场景卡

## SC-TEST-001：调用方传入无效请求

**通过条件。** 服务返回稳定错误码，并保留可追溯日志。
""",
            encoding="utf-8",
        )
        (knowledge / "sources.yaml").write_text(
            """sources:
  - source_id: src-testing-guide
    title: Testing Guide
    url: https://example.test/testing
    version_or_date: "2026-08-25"
    claim_scope: "Validation at a trust boundary."
""",
            encoding="utf-8",
        )
        (self.root / "helper.py").write_text(
            """def normalize(value: str) -> str:
    return value.strip()
""",
            encoding="utf-8",
        )
        (self.root / "application.py").write_text(
            """from helper import normalize


def validate_input(value: str) -> str:
    if not value:
        raise ValueError("input required")
    return normalize(value)
""",
            encoding="utf-8",
        )
        self.service = KnowledgeConnectionService(self.root)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _index(self) -> dict:
        return self.service.index_repository()

    def test_index_builds_knowledge_source_and_python_nodes(self) -> None:
        report = self._index()
        self.assertGreaterEqual(report["files_indexed"], 5)
        self.assertGreater(report["nodes"], 6)
        self.assertIn("python", report["languages"])
        self.assertIn("markdown-yaml", report["languages"])

    def test_search_is_ranked_and_citation_is_connected(self) -> None:
        self._index()
        response = self.service.search_knowledge("输入校验", kinds=["knowledge"])
        self.assertEqual(1, len(response["matches"]))
        node_id = response["matches"][0]["id"]
        detail = self.service.get_node(node_id)
        self.assertEqual("knowledge", detail["node"]["kind"])
        self.assertTrue(any(edge["type"] == "cites" for edge in detail["relationships"]))

    def test_document_title_is_searchable_for_each_knowledge_section(self) -> None:
        self._index()
        response = self.service.search_knowledge("测试工程知识", kinds=["knowledge"])
        self.assertTrue(response["matches"])
        self.assertEqual("knowledge", response["matches"][0]["kind"])
        self.assertEqual("测试工程知识卡", response["matches"][0]["attributes"]["document_title"])

    def test_python_ast_connects_direct_call(self) -> None:
        self._index()
        response = self.service.search_knowledge("validate_input", kinds=["function"])
        node_id = response["matches"][0]["id"]
        connections = self.service.explore_connections(node_id, relation_types=["calls"])
        self.assertEqual(1, len(connections["connections"]))
        self.assertIn("normalize", connections["connections"][0]["node"]["title"])

    def test_context_pack_obeys_budget_and_keeps_locations(self) -> None:
        self._index()
        response = self.service.build_context_pack("验证", max_chars=400, include_code=False)
        self.assertLessEqual(len(response["context"]), 400)
        self.assertTrue(response["node_ids"])
        self.assertIn("Location:", response["context"])
        self.assertTrue(response["citations"])

    def test_errors_are_stable_and_failed_build_preserves_snapshot(self) -> None:
        with self.assertRaises(ServiceError) as not_indexed:
            self.service.search_knowledge("validation")
        self.assertEqual("not_indexed", not_indexed.exception.code)

        self._index()
        with self.assertRaises(ServiceError) as over_limit:
            self.service.index_repository(max_files=1)
        self.assertEqual("resource_limit", over_limit.exception.code)
        self.assertTrue(self.service.search_knowledge("validation")["matches"])

        with self.assertRaises(ServiceError) as outside_root:
            self.service.index_repository(root="../not-allowed")
        self.assertEqual("invalid_root", outside_root.exception.code)

    def test_limits_and_unknown_nodes_are_rejected(self) -> None:
        self._index()
        with self.assertRaises(ServiceError) as invalid_limit:
            self.service.search_knowledge("validation", limit=51)
        self.assertEqual("invalid_input", invalid_limit.exception.code)
        with self.assertRaises(ServiceError) as missing:
            self.service.get_node("knowledge:missing")
        self.assertEqual("not_found", missing.exception.code)


if __name__ == "__main__":
    unittest.main()

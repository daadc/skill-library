from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from knowledge_connection_mcp.service import KnowledgeConnectionService


class PersistentIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "repository"
        knowledge = self.root / "knowledge" / "sample"
        knowledge.mkdir(parents=True)
        self.card = knowledge / "knowledge-cards.md"
        self.card.write_text(
            """# 持久化索引知识

## KC-PERSIST-001：快照必须可重建

**原则。** 将派生索引保存在可删除并重建的本地状态目录。
""",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_persists_reloads_caches_and_refreshes_changed_files(self) -> None:
        first = KnowledgeConnectionService(self.root)
        full = first.index_repository()
        self.assertEqual("full", full["index_mode"])
        self.assertTrue((self.root / ".knowledge-connection" / "graph.sqlite3").exists())
        self.assertEqual(1, first.index_status()["files"])

        second = KnowledgeConnectionService(self.root)
        cached = second.index_repository()
        self.assertEqual("cached", cached["index_mode"])
        self.assertEqual(full["snapshot_id"], cached["snapshot_id"])

        self.card.write_text(
            self.card.read_text(encoding="utf-8") + "\n**验证。** 修改文件后应触发显式刷新。\n",
            encoding="utf-8",
        )
        refreshed = second.refresh_repository()
        self.assertEqual("incremental", refreshed["index_mode"])
        self.assertEqual(1, refreshed["changed_files"])
        matches = second.search_knowledge("显式刷新", kinds=["knowledge"])
        self.assertTrue(matches["matches"])

        third = KnowledgeConnectionService(self.root)
        reloaded = third.index_repository()
        self.assertEqual("cached", reloaded["index_mode"])
        self.assertTrue(third.search_knowledge("显式刷新", kinds=["knowledge"])["matches"])


if __name__ == "__main__":
    unittest.main()

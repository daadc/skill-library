from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from knowledge_connection_mcp.models import ServiceError
from knowledge_connection_mcp.workbench import create_workbench_server


class WorkbenchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "repository"
        knowledge = self.root / "knowledge" / "sample"
        knowledge.mkdir(parents=True)
        (knowledge / "knowledge-cards.md").write_text(
            """# 工作台知识

## KC-WB-001：本地界面应显示可追溯证据

**原则。** 工作台仅显示本地索引结果。
""",
            encoding="utf-8",
        )
        self.server = create_workbench_server(self.root, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temporary_directory.cleanup()

    def test_loopback_workbench_serves_assets_and_read_only_queries(self) -> None:
        with urlopen(f"{self.base_url}/", timeout=5) as response:
            page = response.read().decode("utf-8")
        self.assertIn("Knowledge Connection", page)

        with urlopen(f"{self.base_url}/api/status", timeout=5) as response:
            status = json.loads(response.read().decode("utf-8"))
        self.assertTrue(status["persistent"])

        query = quote("可追溯证据")
        with urlopen(f"{self.base_url}/api/search?q={query}&limit=3", timeout=5) as response:
            search = json.loads(response.read().decode("utf-8"))
        self.assertEqual("knowledge", search["matches"][0]["kind"])

        with urlopen(Request(f"{self.base_url}/api/refresh", method="POST"), timeout=5) as response:
            refreshed = json.loads(response.read().decode("utf-8"))
        self.assertIn(refreshed["index_mode"], {"incremental", "refreshed"})

        with self.assertRaises(HTTPError) as unsafe_asset:
            urlopen(f"{self.base_url}/../../etc/passwd", timeout=5)
        self.assertEqual(404, unsafe_asset.exception.code)

    def test_rejects_non_loopback_binding(self) -> None:
        with self.assertRaises(ServiceError) as rejected:
            create_workbench_server(self.root, host="0.0.0.0", port=8765)
        self.assertEqual("invalid_input", rejected.exception.code)


if __name__ == "__main__":
    unittest.main()

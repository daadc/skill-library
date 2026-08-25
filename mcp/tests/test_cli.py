from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from knowledge_connection_mcp import cli


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name) / "repository"
        knowledge = self.root / "knowledge" / "sample"
        knowledge.mkdir(parents=True)
        (knowledge / "knowledge-cards.md").write_text(
            """# 输入校验知识

## KC-CLI-001：在信任边界验证输入

**原则。** 输入校验应在 API 边界完成。
""",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_search_command_emits_json_result(self) -> None:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            cli.main(["--root", str(self.root), "--json", "search", "输入校验", "--kind", "knowledge"])
        result = json.loads(stream.getvalue())
        self.assertEqual("输入校验", result["query"])
        self.assertEqual("knowledge", result["matches"][0]["kind"])

    def test_eval_command_reports_pass_rate(self) -> None:
        cases = self.root / "cases.json"
        cases.write_text(
            json.dumps(
                {
                    "cases": [
                        {
                            "id": "input-boundary",
                            "query": "输入校验",
                            "expected_path_contains": "knowledge-cards.md",
                            "accepted_kinds": ["knowledge"],
                        }
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            cli.main(["--root", str(self.root), "--json", "eval", "--cases", str(cases)])
        result = json.loads(stream.getvalue())
        self.assertEqual(1, result["passed_cases"])
        self.assertEqual(1.0, result["pass_rate"])


if __name__ == "__main__":
    unittest.main()

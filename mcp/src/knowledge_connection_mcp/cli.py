"""Human and automation-friendly command line interface for local knowledge search."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .models import ServiceError
from .service import KnowledgeConnectionService
from .workbench import run_workbench


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "workbench":
            run_workbench(_resolve_root(args.root, args.config), host=args.host, port=args.port)
            return
        result = _dispatch(args)
    except ServiceError as error:
        _emit(error.to_dict(), as_json=True, stream=sys.stderr)
        raise SystemExit(2) from error
    _emit(result, as_json=args.json)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="knowledge-connection",
        description="Index and search a local knowledge/code repository without network or write side effects.",
    )
    parser.add_argument("--root", help="Allowed repository root. Defaults to the current directory or config root.")
    parser.add_argument("--config", help="Optional JSON configuration file containing a root value.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    index = subcommands.add_parser("index", help="Build a fresh in-memory index and print its report.")
    index.add_argument("--max-files", type=int, default=5_000)
    index.add_argument("--no-code", action="store_true")
    index.add_argument("--no-knowledge", action="store_true")

    status = subcommands.add_parser("status", help="Show local persistent index status without rebuilding.")

    refresh = subcommands.add_parser("refresh", help="Explicitly rebuild the local persistent graph after source changes.")
    refresh.add_argument("--max-files", type=int, default=5_000)
    refresh.add_argument("--no-code", action="store_true")
    refresh.add_argument("--no-knowledge", action="store_true")

    search = subcommands.add_parser("search", help="Index then search knowledge and Python symbols.")
    search.add_argument("query")
    search.add_argument("--kind", action="append", dest="kinds", help="Repeatable node kind filter.")
    search.add_argument("--limit", type=int, default=10)

    node = subcommands.add_parser("node", help="Index then show one deterministic node ID.")
    node.add_argument("node_id")
    node.add_argument("--summary", action="store_true", help="Omit bounded content.")

    connections = subcommands.add_parser("connections", help="Index then explore typed graph connections.")
    connections.add_argument("node_id")
    connections.add_argument("--relation", action="append", dest="relation_types")
    connections.add_argument("--depth", type=int, default=1)
    connections.add_argument("--limit", type=int, default=25)

    context = subcommands.add_parser("context", help="Index then build a bounded evidence-oriented context pack.")
    context.add_argument("query")
    context.add_argument("--max-chars", type=int, default=8_000)
    context.add_argument("--no-code", action="store_true")

    workbench = subcommands.add_parser("workbench", help="Run the local loopback-only knowledge workbench.")
    workbench.add_argument("--host", default="127.0.0.1", choices=["127.0.0.1", "localhost", "::1"])
    workbench.add_argument("--port", type=int, default=8765)

    evaluate = subcommands.add_parser("eval", help="Run versioned offline retrieval cases against a repository.")
    evaluate.add_argument("--cases", type=Path, required=True, help="JSON evaluation cases file.")
    evaluate.add_argument("--limit", type=int, default=3)
    return parser


def _dispatch(args: argparse.Namespace) -> dict[str, Any]:
    root = _resolve_root(args.root, args.config)
    service = KnowledgeConnectionService(root)
    if args.command == "status":
        return service.index_status()
    if args.command == "index":
        return service.index_repository(
            include_code=not args.no_code,
            include_knowledge=not args.no_knowledge,
            max_files=args.max_files,
        )

    if args.command == "refresh":
        return service.refresh_repository(
            include_code=not args.no_code,
            include_knowledge=not args.no_knowledge,
            max_files=args.max_files,
        )

    service.index_repository()
    if args.command == "search":
        return service.search_knowledge(query=args.query, kinds=args.kinds, limit=args.limit)
    if args.command == "node":
        return service.get_node(node_id=args.node_id, include_content=not args.summary)
    if args.command == "connections":
        return service.explore_connections(
            node_id=args.node_id,
            relation_types=args.relation_types,
            depth=args.depth,
            limit=args.limit,
        )
    if args.command == "context":
        return service.build_context_pack(
            query=args.query,
            max_chars=args.max_chars,
            include_code=not args.no_code,
        )
    if args.command == "eval":
        return _run_evaluation(service, args.cases, args.limit)
    raise ServiceError("invalid_input", "Unsupported command.")


def _resolve_root(root_arg: str | None, config_arg: str | None) -> Path:
    config: dict[str, Any] = {}
    if config_arg:
        config_path = Path(config_arg).expanduser().resolve()
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ServiceError("invalid_input", "config must be a readable JSON file.") from error
        if not isinstance(config, dict):
            raise ServiceError("invalid_input", "config must be a JSON object.")
    configured_root = config.get("root")
    candidate = root_arg or configured_root or str(Path.cwd())
    if not isinstance(candidate, str):
        raise ServiceError("invalid_input", "config root must be a string path.")
    return Path(candidate).expanduser().resolve()


def _run_evaluation(service: KnowledgeConnectionService, cases_path: Path, limit: int) -> dict[str, Any]:
    try:
        raw_cases = json.loads(cases_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ServiceError("invalid_input", "cases must be a readable JSON file.") from error
    cases = raw_cases.get("cases") if isinstance(raw_cases, dict) else None
    if not isinstance(cases, list) or not cases:
        raise ServiceError("invalid_input", "cases must contain a non-empty cases array.")

    reports: list[dict[str, Any]] = []
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("query"), str):
            raise ServiceError("invalid_input", "Every evaluation case needs a string query.")
        expected_path = case.get("expected_path_contains")
        expected_kinds = set(case.get("accepted_kinds", []))
        result = service.search_knowledge(case["query"], limit=limit)
        matches = result["matches"]
        passed = any(
            (not expected_path or expected_path in str(match["path"]))
            and (not expected_kinds or str(match["kind"]) in expected_kinds)
            for match in matches
        )
        reports.append(
            {
                "id": case.get("id", case["query"]),
                "query": case["query"],
                "passed": passed,
                "top_match": matches[0] if matches else None,
            }
        )
    passed_count = sum(1 for report in reports if report["passed"])
    return {
        "total_cases": len(reports),
        "passed_cases": passed_count,
        "failed_cases": len(reports) - passed_count,
        "pass_rate": round(passed_count / len(reports), 4),
        "cases": reports,
    }


def _emit(payload: dict[str, Any], *, as_json: bool, stream: Any | None = None) -> None:
    stream = stream or sys.stdout
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=stream)
        return
    for key, value in payload.items():
        if isinstance(value, (dict, list)):
            rendered = json.dumps(value, ensure_ascii=False, indent=2)
            print(f"{key}:\n{rendered}", file=stream)
        else:
            print(f"{key}: {value}", file=stream)


if __name__ == "__main__":
    main()

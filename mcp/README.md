# Knowledge Connection MCP

`knowledge-connection-mcp` 是一个**本地优先、可追溯、默认只读**的知识与代码检索工具。它将项目中的 Markdown 知识卡、场景卡、`sources.yaml` 和 Python AST 转换为统一图谱，并通过 MCP、CLI 与本地知识工作台提供一致的检索接口。

> **P0、P1、P2 已实现。** 本版本包含交互式 CLI 与离线评测、SQLite 持久化和文件级 Markdown 增量刷新，以及只绑定本机回环地址的知识工作台。它不会执行源代码、联网抓取、写入被索引源文件或自动修改 MCP 客户端配置。

## 当前能力

| 能力层 | 已实现内容 | 关键边界 |
|---|---|---|
| 知识图谱 | Markdown/YAML 知识、场景、来源；Python 模块/类/函数/方法、导入和可确定的直接调用。 | Python 是首个保证支持的 AST 语言；动态派发、反射和运行时导入不推断。 |
| 检索 | 字段化确定性评分、知识节点优先、SQLite FTS5 加分、节点详情、关系探索与受预算上下文包。 | `shares_terms` 是弱词项关联，不是引用、因果或授权证据。 |
| P0 CLI | `index`、`status`、`refresh`、`search`、`node`、`connections`、`context`、`eval` 与 `workbench`。 | 所有命令只读被索引内容；刷新只写可再生成状态。 |
| P1 状态 | `.knowledge-connection/graph.sqlite3` 保存派生快照、文件指纹、关系和 FTS5 索引。 | 状态目录可删除重建，已被 `.gitignore` 忽略；不保存到远程服务。 |
| P2 工作台 | 本地搜索、节点详情、两跳关系、上下文包、索引状态和显式刷新。 | 默认且仅允许 `127.0.0.1`、`localhost` 或 `::1`；没有远程访问、认证或写入界面。 |
| MCP | `index_repository`、`index_status`、`refresh_repository`、`search_knowledge`、`get_node`、`explore_connections`、`build_context_pack`。 | MCP 工具保持窄化、参数受限和可解释。 |

## 安装与运行

项目要求 **Python 3.10+**。在 `mcp/` 目录中使用 `uv` 安装并运行本项目：

```bash
cd /Users/zhangshaowei/code/skill-library/mcp
uv run knowledge-connection --root .. index
```

首次运行会在索引根目录创建 `.knowledge-connection/graph.sqlite3`。它是派生缓存，不包含任何源文件修改；删除该目录即可让下一次索引完整重建。

### CLI 示例

```bash
# 查看本地状态；不触发重建
uv run knowledge-connection --root .. --json status

# 构建或加载匹配快照
uv run knowledge-connection --root .. --json index

# 主题、知识卡或 Python 符号检索
uv run knowledge-connection --root .. --json search "安全交付" --kind knowledge --limit 5

# 显式刷新；不会启动后台 watcher
uv run knowledge-connection --root .. --json refresh

# 用版本化离线案例评估检索回归
uv run knowledge-connection --root .. --json eval --cases evals/retrieval_cases.json

# 启动本地工作台；浏览器访问输出的回环 URL
uv run knowledge-connection --root .. workbench --port 8765
```

`--root` 与 `--config` 必须出现在子命令之前。配置文件为只包含 `root` 字段的 JSON 对象，例如：

```json
{ "root": "/Users/zhangshaowei/code/skill-library" }
```

### MCP 客户端配置示例

以下配置只供用户手动添加；本项目不会改写任何客户端配置。服务启动后先调用 `index_repository`，再调用检索工具。

```json
{
  "mcpServers": {
    "knowledge-connection": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/zhangshaowei/code/skill-library/mcp",
        "knowledge-connection-mcp",
        "--root",
        "/Users/zhangshaowei/code/skill-library"
      ]
    }
  }
}
```

## 工作台操作流程

启动 `workbench` 后，浏览器访问控制台打印的 URL。工作台先加载持久快照，并提供以下不带权限升级的操作：搜索节点、查看路径/行号/原文、浏览至多两跳关系、创建 4,000 字符的上下文包，以及显式刷新派生索引。界面将词项关联标为“弱关联”，避免把词频关系误读为证据。

工作台 API 仅接受固定端点：`/api/status`、`/api/search`、`/api/node`、`/api/connections`、`/api/context` 和 `/api/refresh`。它不会接受任意 URL、文件路径、SQL、命令或请求体。详见 [`docs/adr-0002-local-persistent-workbench.md`](docs/adr-0002-local-persistent-workbench.md)。

## 安全、隐私与索引策略

服务只处理允许根目录内的常规非符号链接 `.md`、`.yaml`、`.yml`、`.py` 文件；默认跳过 `.git`、虚拟环境、构建输出、缓存、`node_modules` 和自身状态目录。单文件最大 1 MB，默认最多 5,000 个文件。所有关系和正文都应被视为**待审阅数据**：检索命中不等于事实认证，也不等于执行授权。

持久化策略遵循以下原则：未变更文件的匹配快照直接加载；仅 Markdown 文件变化时，服务安全地保留未变更节点和边并增量重建变化文件；Python/YAML 变化或删除触发完整回退重建，以避免在导入、调用或来源引用关系上产生不完整图谱。刷新始终由用户、CLI 或 MCP 工具显式触发。

## 验证

```bash
cd mcp
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 tests/smoke_mcp.py
PYTHONPATH=src python3 -m knowledge_connection_mcp.cli --root .. --json eval --cases evals/retrieval_cases.json
```

测试覆盖 Markdown/YAML/Python AST 解析、确定性检索、来源关系、字符预算、错误边界、SQLite 重载、缓存命中、Markdown 增量刷新、CLI 输出、loopback 工作台、静态资源、MCP stdio 与当前仓库检索评测。

## 项目文档

| 文档 | 用途 |
|---|---|
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | P0-P2 实施状态及下一阶段治理方向。 |
| [`docs/adr-0001-local-knowledge-graph.md`](docs/adr-0001-local-knowledge-graph.md) | 初始知识图谱与解析器决策。 |
| [`docs/adr-0002-local-persistent-workbench.md`](docs/adr-0002-local-persistent-workbench.md) | 持久化、刷新、工作台与安全边界。 |
| [`docs/interaction-contract.md`](docs/interaction-contract.md) | MCP 工具输入、输出与错误契约。 |
| [`docs/current-repository-validation.md`](docs/current-repository-validation.md) | 当前 `skill-library` 仓库检索验证记录。 |
| [`docs/p0-p2-verification-report.md`](docs/p0-p2-verification-report.md) | P0-P2 CLI、持久索引、MCP、工作台和安全边界验证证据。 |
| [`docs/verification-report.md`](docs/verification-report.md) | 初始质量门禁与残余风险。 |
| [`docs/evidence-audit.yaml`](docs/evidence-audit.yaml) | 调研主张与工具权限审校。 |

## 后续范围

P3 才会评估多仓库共享、远程访问、认证、写入型知识治理、发布工程和多语言 parser adapter。它们会引入新的权限、数据和发布影响，不能由当前本地只读服务自动开启。

[1]: https://py.sdk.modelcontextprotocol.io/
[2]: https://modelcontextprotocol.io/specification/2026-07-28/server/tools

# Knowledge Connection MCP

`knowledge-connection-mcp` 是一个**本地、只读**的 MCP 服务。它将本项目的 Markdown 知识卡、场景卡和 `sources.yaml` 解析成可追溯知识节点，同时用 Python 标准库 AST 提取模块、类、函数、方法、导入和可静态确定的直接调用。AI 因而可以先检索小型结构化结果，再沿“引用、场景、代码关系、术语关联”展开上下文，而不必无差别读取大量文件。

> 首版实现有意保持边界：它不执行代码、不联网、不写入被索引仓库、不启动后台守护进程；代码 AST 仅保证 Python。它并非 `codebase-memory-mcp` 的复刻，也不承诺其多语言或性能结果。

## 能力与关系边界

| 输入来源 | 提取节点 | 可解释关系 | 明确不推断 |
|---|---|---|---|
| `knowledge/**/*.md` | `knowledge`、`scenario` | `cites`、`shares_terms` | 引用之外的因果或事实关系 |
| `knowledge/**/sources.yaml` | `source` | 被知识卡 `cites` | 任意 YAML 的执行语义 |
| `**/*.py` | `module`、`class`、`function`、`method` | `contains`、`imports`、可唯一解析的 `calls` | 反射、动态导入、运行时派发、类型关系 |

`shares_terms` 仅表示规范化文本词项重合，其结果会附带关联词说明，不能被当成引用、依赖或因果结论。

## 安装与本地运行

服务要求 **Python 3.10+** 与 [官方 MCP Python SDK][1]。当前项目包含 `pyproject.toml`，可由 `uv` 管理依赖。以下命令把根目录限定为整个 `skill-library` 仓库：

```bash
cd /Users/zhangshaowei/code/skill-library/mcp
uv run knowledge-connection-mcp --root /Users/zhangshaowei/code/skill-library
```

该进程通过标准输入/输出传输 MCP 协议。请不要把运行日志或普通文本写入 stdout；实现将异常日志写至 stderr，以避免破坏协议流。

## MCP 客户端配置样例

将下列示例中的绝对路径替换为你的实际路径，并在 MCP 客户端中添加为 stdio 服务。此示例只供手动配置；本实现不会自动修改任何客户端设置。

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

也可以通过 `KNOWLEDGE_MCP_ROOT` 环境变量设定允许根目录。传入的 `index_repository.root` 只能是该允许根目录本身或其子目录；任何父目录跳转或根目录外的路径都会被拒绝。

## 工具契约

| 工具 | 何时调用 | 输出要点 |
|---|---|---|
| `index_repository` | 会话开始、或源文件改变后。 | 新快照 ID、文件/节点/边计数、支持格式、跳过原因与耗时。 |
| `search_knowledge` | 以主题、风险、验证、来源、符号或代码术语寻找入口。 | 有评分的节点摘要、相对路径、行号和匹配片段。 |
| `get_node` | 需要阅读一个结果的完整受限内容，或查看其直接关系。 | 节点详情与带理由的出入边。 |
| `explore_connections` | 需要连接知识原则、场景、来源与代码实现线索。 | 有方向、类型、距离和理由的受限邻域。 |
| `build_context_pack` | 准备让 AI 回答、评审或编码的紧凑证据包。 | 受字符预算限制的正文、节点 ID 和定位/来源列表。 |

所有列表 `limit` 最大为 50；邻域 `depth` 最大为 3；上下文包 `max_chars` 最大为 20,000。查询工具需要已经成功运行 `index_repository`；索引失败会保留最近一次成功的内存快照。

## 推荐 Agent 调用流程

```text
1. index_repository()
2. search_knowledge(query="主题或符号")
3. get_node(node_id) 或 explore_connections(node_id)
4. build_context_pack(query="要解决的问题")
5. AI 根据返回的路径、行号、来源 URL 与条件进行推理；不把 shares_terms 当作事实证明。
```

例如，用户询问“输入校验的工程原则以及代码中可能的实现入口”时，先以 `输入校验` 搜索知识节点，再扩展其 `cites` 和 `shares_terms`，最后以 `validate_input` 或同义术语搜索 Python 符号，并用上下文包把原则、风险、验证和实现定位一起交给 AI。

## 验证

在 `mcp/` 目录运行：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

测试覆盖知识卡/来源/场景解析、Python AST 调用关系、确定性检索、上下文字符预算、未索引状态、资源上限、根目录隔离、未知节点和参数限制。完整产品与接口决策记录见 [`docs/`](docs/)。

## 安全与隐私

该服务只读取允许根目录中后缀为 `.md`、`.yaml`、`.yml`、`.py` 的常规非符号链接文件，并跳过 `.git`、虚拟环境、构建目录、缓存和 `node_modules`。单文件最大 1 MB，默认最多索引 5,000 个文件。工具不会读取根目录之外的内容、写入索引文件、执行代码或发起网络请求。

所有工具调用都应在用户可察觉、可拒绝的 MCP 客户端环境中进行；这是 MCP 工具规范推荐的安全交互方式。[2]

## 项目文档

| 文档 | 作用 |
|---|---|
| [`docs/research-notes.md`](docs/research-notes.md) | 外部调研、证据、假设和范围。 |
| [`docs/routing-record.yaml`](docs/routing-record.yaml) | 使用当前团队技能进行需求、架构、实现和验证的路由记录。 |
| [`docs/product-brief.md`](docs/product-brief.md) | 目标、非目标、验收标准和验证计划。 |
| [`docs/adr-0001-local-knowledge-graph.md`](docs/adr-0001-local-knowledge-graph.md) | 图谱与解析器选型的 ADR。 |
| [`docs/interaction-contract.md`](docs/interaction-contract.md) | 五个 MCP 工具的输入、输出、错误与安全契约。 |
| [`docs/verification-report.md`](docs/verification-report.md) | 自动化测试、stdio smoke test 与残余风险记录。 |
| [`docs/evidence-audit.yaml`](docs/evidence-audit.yaml) | 调研主张、版本范围与权限边界的独立审校记录。 |

[1]: https://py.sdk.modelcontextprotocol.io/
[2]: https://modelcontextprotocol.io/specification/2026-07-28/server/tools

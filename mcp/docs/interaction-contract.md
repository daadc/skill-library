# 交互契约：知识连通 MCP 工具集

| 字段 | 内容 |
|---|---|
| 类型 | `MCP query`（五个只读工具） |
| Owner | 本地 `knowledge-connection-mcp` 服务 |
| 消费者 | 兼容 MCP 的 AI 客户端及其编程 Agent |
| 状态 | `active`（首版） |
| 规范链接 | MCP Tools 规范与工具参数 JSON Schema。[1] |
| 兼容性策略 | 加法优先：已发布参数只新增可选字段；错误码、节点 ID 与关系类型在同一主版本稳定。 |
| 关联 ADR / 测试 | `adr-0001-local-knowledge-graph.md`；`tests/` |

## 1. 用户/业务任务

AI 首先由 `index_repository` 建立调用者明确指定的本地快照，然后使用检索、详情、邻域和上下文工具完成证据导向的技术问答或代码理解。工具没有认证或租户概念，因为服务按本地 stdio 会话运行；安全边界由允许的根目录、只读解析器、文件类型白名单和资源上限共同实现。客户端和用户可在调用前看到工具的说明和参数；服务不提供任何写入或执行类工具。[1]

## 2. 输入与输出

所有成功结果均为 JSON 对象。节点摘要有统一形状：`id`、`kind`、`title`、`path`、`line_start`、`line_end`、`score?`、`snippet?`、`attributes`。路径永远为相对于索引根的 POSIX 相对路径；原始绝对路径不在常规查询结果中回显。所有 `limit` 参数的默认值为 10，最大为 50；`depth` 默认 1，最大 3；`max_chars` 默认 8,000，最大 20,000。

| 工具 | 输入 schema 摘要 | 成功输出 | 规则 |
|---|---|---|---|
| `index_repository` | `{root?: string, include_code?: boolean=true, include_knowledge?: boolean=true, max_files?: integer=5000}` | `{snapshot_id, root_name, files_indexed, files_skipped, nodes, edges, duration_ms, languages, skipped}` | `root` 缺省时取服务启动时配置的默认根；成功后原子替换当前快照。 |
| `search_knowledge` | `{query: string, kinds?: string[], limit?: integer}` | `{snapshot_id, query, matches: NodeSummary[], total_candidates}` | 查询须包含非空词项；排序按确定性评分、标题和 ID 作为稳定并列规则。 |
| `get_node` | `{node_id: string, include_content?: boolean=true}` | `{node: NodeDetail, relationships: Relationship[]}` | 仅返回当前快照的节点，正文按最大字符数裁剪并标记。 |
| `explore_connections` | `{node_id: string, relation_types?: string[], depth?: integer=1, limit?: integer=25}` | `{seed, connections: Connection[], truncated: boolean}` | 从种子节点执行有界 breadth-first 展开，不隐式查询文件系统。 |
| `build_context_pack` | `{query: string, max_chars?: integer=8000, include_code?: boolean=true}` | `{query, context, node_ids, citations, truncated}` | 在总字符预算内按相关性打包知识、风险、验证、来源与代码符号；保留定位。 |

### 2.1 节点与关系 JSON 示例

```json
{
  "id": "knowledge:ab12cd34ef56",
  "kind": "knowledge",
  "title": "KC-PD-001：需求不是功能列表，而是待验证的机会",
  "path": "knowledge/product-discovery/knowledge-cards.md",
  "line_start": 3,
  "line_end": 23,
  "attributes": {
    "domain": "product-discovery",
    "references": ["1"],
    "has_risks": true,
    "has_validation": false
  }
}
```

```json
{
  "source": "knowledge:ab12cd34ef56",
  "target": "source:09bcde123456",
  "type": "cites",
  "reason": "Markdown 引用 [1] 与同领域 sources.yaml 的第 1 项匹配"
}
```

## 3. 规则与状态机

```text
EMPTY --index_repository(success)--> READY
READY --index_repository(success)--> READY（新快照原子替换）
READY --index_repository(failure)--> READY（保留旧快照）
EMPTY --任意查询--> ERROR(not_indexed)
READY --查询--> READY（无副作用）
```

索引器必须先对根目录进行 `resolve()`，然后仅遍历该路径的非符号链接常规文件。只处理 `.md`、`.yaml`、`.yml` 和 `.py`，并跳过默认忽略目录（`.git`、虚拟环境、`node_modules`、构建/缓存目录）及超限文件。Markdown 节点由二级与更深层标题切分；在 `scenarios.md` 中识别 `SC-` 标题为 `scenario`，在其他知识 Markdown 中将 `KC-` 标题或知识卡文件内二级标题识别为 `knowledge`。来源节点只从键值标量构成的 `sources.yaml` 条目提取，未知 YAML 构造不执行也不解释。

Python 关系只保证可由单个模块静态确定的导入、定义和简单名字调用。无法在同一快照中唯一解析的调用不创建 `calls` 边；服务不会猜测运行时派发、反射、动态导入或类型关系。跨域“融会”关系来自规范化词项交集，标记为 `shares_terms`，其 `reason` 必须显式说明关联词，不能被视为引用或因果关系。

## 4. 幂等与并发

工具均无写入副作用。以相同输入、相同文件内容再次调用 `index_repository` 会创建逻辑等价的新快照；`snapshot_id` 可改变，因为它携带构建时间，不作为内容哈希承诺。服务以互斥锁保护快照替换；查询在取得快照引用后对该不可变对象执行，因而不会观察到半构建状态。stdio 会话默认串行，当前实现不承诺多进程共享或跨会话缓存。

## 5. 失败与异步语义

所有索引和查询均同步完成，不启动后台任务。服务应把预期失败转换为稳定、机器可读的 `code` 和人类可读的 `message`；对外部工具调用按 MCP 错误结果语义返回，不能打印额外内容到 stdout。[1]

| 情况 | 稳定码 | 是否可重试 | 消费者动作 | 观测 |
|---|---|---:|---|---|
| 未建立快照 | `not_indexed` | 是 | 调用 `index_repository`。 | 工具日志包含工具名。 |
| 根目录无效/越界 | `invalid_root` | 否，除非提供允许根。 | 修正根路径；不尝试父目录绕过。 | 索引结果/错误不泄露未授权路径内容。 |
| 输入不合法 | `invalid_input` | 否 | 修正字段、范围或空查询。 | 返回字段名和限制。 |
| 节点不存在 | `not_found` | 可在重新索引后重试 | 从搜索结果获取当前节点 ID。 | 返回当前 snapshot 标识。 |
| 超过资源上限 | `resource_limit` | 是 | 缩小根目录、降低 `max_files` 或收紧查询。 | 返回触发的限制和已跳过计数。 |
| 解析失败 | `parse_error` | 视文件修正情况 | 查询剩余可用节点或修正源文件后重新索引。 | 报告相对路径和安全化错误摘要。 |
| 未处理内部错误 | `internal_error` | 视情况 | 保留 correlation ID 并向维护者报告。 | stderr 结构化日志，stdout 保持 MCP 协议。 |

## 6. 兼容、弃用与安全

当前版本不持久化快照，因此升级或重启后需要重建索引。将来增加 parser、节点属性或关系类型时，只能增加字段/类型；不能改变既有 ID 生成算法而不提升主版本。服务不采集遥测、不传输代码内容、不读取根目录外文件。日志只记录相对路径、计数和错误类别，默认不记录知识卡正文或源码。单文件大小、文件数、输出字符数与邻域深度均有上限；符号链接、设备文件、管道和不允许的扩展名被忽略。

## 7. 验证与批准

契约测试必须覆盖所有五个工具的成功和稳定错误码、排序稳定性、输出字段、输入边界、超限截断、快照原子替换、路径安全、无写入副作用、Markdown/YAML 结构和 Python AST 关系。MCP stdio smoke test 必须验证客户端可完成初始化、`tools/list`、`index_repository` 与 `search_knowledge`。未来引入持久化、多语言解析、网络或任何写工具时，必须新建 ADR、更新该契约，并取得相应的人类批准。

## 参考文献

[1]: https://modelcontextprotocol.io/specification/2026-07-28/server/tools

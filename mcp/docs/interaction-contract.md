# 交互契约：知识连通 MCP 工具集

| 字段 | 内容 |
|---|---|
| 类型 | `MCP query + local-derived-state refresh`（七个窄化工具） |
| Owner | 本地 `knowledge-connection-mcp` 服务 |
| 消费者 | 兼容 MCP 的 AI 客户端及其编程 Agent |
| 状态 | `active`（R2） |
| 规范链接 | MCP Tools 规范与工具参数 JSON Schema。[1] |
| 兼容性策略 | 加法优先；已发布参数只新增可选字段；错误码、节点 ID 与关系类型在同一主版本稳定。 |
| 关联 ADR / 测试 | ADR-0001、ADR-0002；`tests/`、`evals/` |

## 1. 用户任务与权限边界

AI 或开发者先使用 `index_repository` 加载或构建调用者明确指定的本地快照，再使用检索、详情、邻域和上下文工具完成证据导向的技术问答或代码理解。`index_status` 用于观察派生状态；`refresh_repository` 是唯一会写入的工具，但它**只**在允许根目录中的 `.knowledge-connection/` 写入可删除重建的 SQLite 派生状态，绝不写入被索引源文件。

工具没有认证或租户概念，因为服务按本地 stdio 会话运行。安全边界由允许根目录、常规非符号链接文件、扩展名白名单、资源上限、参数校验与本地状态目录共同实现。工具不提供任意路径、URL、SQL、shell、代码执行或网络访问。[1]

## 2. 输入与输出

所有成功结果均为 JSON 对象。节点摘要有统一形状：`id`、`kind`、`title`、`path`、`line_start`、`line_end`、`score?`、`snippet?`、`attributes`。路径永远为相对于索引根的 POSIX 路径。`limit` 最大为 50，`depth` 最大为 3，`max_chars` 最大为 20,000；超出范围返回 `invalid_input`。

| 工具 | 输入 schema 摘要 | 成功输出 | 规则 |
|---|---|---|---|
| `index_repository` | `{root?, include_code?=true, include_knowledge?=true, max_files?=5000}` | 索引报告加 `{index_mode, changed_files}` | 匹配文件指纹时加载持久快照；否则构建并原子持久化新快照。 |
| `index_status` | `{root?}` | `{persistent, state_directory, snapshot_id, files, nodes, edges, active_snapshot_id}` | 不构建、不扫描源文件；只报告本地派生状态。 |
| `refresh_repository` | 与 `index_repository` 相同 | 索引报告加 `{index_mode, changed_files}` | 显式强制刷新；只写 `.knowledge-connection/`，失败时保留会话内旧快照。 |
| `search_knowledge` | `{query, kinds?, limit?=10}` | `{snapshot_id, query, matches, total_candidates, ranking}` | 使用字段权重及可选 SQLite FTS5 加分；排序有稳定并列规则。 |
| `get_node` | `{node_id, include_content?=true}` | `{snapshot_id, node, relationships}` | 仅返回当前快照节点。 |
| `explore_connections` | `{node_id, relation_types?, depth?=1, limit?=25}` | `{snapshot_id, seed, connections, truncated}` | 有界 breadth-first 展开，不隐式读取文件。 |
| `build_context_pack` | `{query, max_chars?=8000, include_code?=true}` | `{snapshot_id, query, context, node_ids, citations, truncated}` | 在字符预算内保留证据定位。 |

## 3. 状态机、持久化与增量策略

```text
EMPTY --index_repository(cache hit)--> READY
EMPTY --index_repository(build)--> READY + local derived state
READY --refresh_repository(success)--> READY + atomically replaced derived state
READY --index/refresh(failure)--> READY (preserve last in-memory snapshot)
EMPTY --query--> ERROR(not_indexed)
READY --query/status--> READY (query has no source write side effect)
```

SQLite 只保存节点、边、文件内容指纹、构建报告、设置与 FTS5 索引。它不连接网络，状态目录可删除重建。未变更的同一设置命中缓存；只变更 Markdown 文件时，系统保留未变更节点/边并增量重建变化文件；Python、YAML 或删除变化回退为全量重建，以避免导入、调用或来源关系残留。

索引器仅处理允许根内的 `.md`、`.yaml`、`.yml`、`.py` 常规文件，跳过符号链接、虚拟环境、构建/缓存输出、`node_modules` 和自身状态目录。Python 关系只保证单模块静态可确定的导入、定义和简单名称调用；动态派发、反射和运行时导入不猜测。`shares_terms` 是弱词项关联，不能被视为引用、因果或授权。

## 4. 失败、幂等与观测

| 情况 | 稳定码 | 消费者动作 |
|---|---|---|
| 尚无会话快照 | `not_indexed` | 调用 `index_repository`。 |
| 根目录无效/越界 | `invalid_root` | 提供允许根内部的路径；不尝试父目录绕过。 |
| 输入、端口或范围不合法 | `invalid_input` | 修正字段。 |
| 节点不存在 | `not_found` | 从当前搜索结果重新获取 ID。 |
| 文件数超限 | `resource_limit` | 缩小根目录或降低范围。 |
| 解析/指纹异常 | `parse_error` | 修正源文件后显式刷新；旧会话快照保持可查询。 |
| 未处理内部错误 | `internal_error` | 保持 stdout 协议洁净并向维护者报告。 |

相同文件内容和设置的 `index_repository` 幂等地加载逻辑等价快照；`refresh_repository` 是明确请求的新构建，快照 ID 可因构建时间变化。服务以互斥锁保护会话快照替换。日志不记录正文；MCP stdout 只保留协议数据。[1]

## 5. 验证与批准

契约测试覆盖七个工具、稳定错误码、排序、输入边界、SQLite 重载、缓存命中、Markdown 增量刷新、路径安全、MCP stdio 和回环工作台 API。版本化离线评测在 `evals/retrieval_cases.json` 中维护。任何远程访问、认证、写入型知识治理、任意执行、多用户共享、网络出口或新解析器必须更新 ADR、契约、评测与人工审批。

## 参考文献

[1]: https://modelcontextprotocol.io/specification/2026-07-28/server/tools

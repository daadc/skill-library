# P0-P2 升级验证报告

| 字段 | 结果 |
|---|---|
| 验证日期 | 2026-08-25 |
| 验证范围 | P0 CLI 与离线评测、P1 SQLite 持久索引/增量刷新/FTS5、P2 loopback 工作台与受限 API。 |
| 目标仓库 | 当前 `skill-library`；索引运行通过 `--root ..` 从 `mcp/` 启动。 |
| 结论 | 通过。所有自动化、协议、CLI、离线评测、工作台 API 与安全边界检查均通过。 |

## 执行证据

| 验证项 | 命令或方法 | 结果 |
|---|---|---|
| Python 编译 | `python3 -m compileall -q src tests` | 通过。 |
| 单元/集成测试 | `python3 -m unittest discover -s tests -v` | 12/12 通过。 |
| MCP stdio | `python3 tests/smoke_mcp.py` | 通过；客户端发现 7 个工具，并成功调用状态、索引、刷新和检索。 |
| CLI 离线评测 | `knowledge-connection --root .. --json eval --cases evals/retrieval_cases.json` | 4/4 通过，`pass_rate=1.0`。 |
| 当前仓库 CLI | `status`、`index`、`search`、`refresh` | 通过；一次当前运行索引 72 个文件、405 个节点和 4,891 条关系。此数字会随工作树变化而变化，非性能承诺。 |
| 持久化行为 | 临时仓库内第一次全量构建、第二个服务实例缓存重载、Markdown 修改后的增量刷新、第三个服务实例再次重载。 | 通过；派生状态可删除重建。 |
| 工作台 API | 临时回环服务器；静态首页、状态、搜索、刷新与非法静态路径。 | 通过；非法路径返回 404。 |
| 网络与执行边界 | 代码审查搜索 `subprocess`、`os.system`、`shell=True`、HTTP 客户端、非 loopback bind。 | 未发现执行器、外部 HTTP 客户端或非 loopback 绑定；唯一 HTTP 文本为本地监听 URL。 |

## 覆盖内容

测试文件 `test_service.py`、`test_cli.py`、`test_persistence.py` 和 `test_workbench.py` 共同覆盖 Markdown/YAML/Python AST 提取、来源边、稳定错误、上下文预算、CLI JSON、评测通过率、SQLite 状态、缓存命中、Markdown 增量刷新、loopback 拒绝规则、固定静态资源和只读查询 API。`smoke_mcp.py` 覆盖 MCP 客户端初始化和工具调用。

## 已知限制与不误报声明

当前持久化快照服务于单个本地根目录；SQLite 不表示多人共享图数据库。Markdown 文件变化可以文件级增量重建；Python/YAML/删除变化为避免不完整关系会安全回退到全量重建。FTS5 只作为本地排序加分，不是向量检索或语言模型重排。工作台不提供认证、远程访问、编辑、审批或发布功能。

这些限制符合 ADR-0002 的本地只读范围；它们不是已解决的 P3 能力。任何上述范围扩展必须重新进行架构、安全和发布审查。

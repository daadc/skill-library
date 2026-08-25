# Verification Report：知识连通 MCP（R1 本地实现）

| 字段 | 内容 |
|---|---|
| 验证日期 | 2026-08-25 |
| 状态 | `ready-with-conditions` |
| 验证环境 | macOS；Python 3.10.8；已安装 `mcp` 1.28.1；本地工作树。 |
| 被测范围 | `mcp/src/knowledge_connection_mcp/` 与 MCP stdio 会话。 |
| 外部副作用 | 无。未修改被索引知识文件、未配置客户端、未发布或部署。 |

## 执行证据

```text
PYTHONPATH=src python3 -m compileall -q src tests
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 tests/smoke_mcp.py
```

编译检查通过。单元测试共 **6/6** 通过。stdio smoke test 成功完成 MCP 初始化、`tools/list`、`index_repository` 和 `search_knowledge`；服务准确暴露五个只读工具，并返回结构化查询输出。

## 风险驱动测试矩阵

| 风险 | 影响 | 主要验证 | 结果 |
|---|---|---|---|
| 知识卡结构丢失或来源不可追溯 | 高 | 解析知识卡、场景卡、`sources.yaml`，并断言 `cites` 边与定位字段。 | 通过。 |
| Python 实现线索不能关联 | 中 | 解析模块/函数，断言唯一静态调用产生 `calls` 边。 | 通过。 |
| 输出过大导致 AI 上下文失控 | 中 | 对 `build_context_pack(max_chars=400)` 断言字符上限与定位保留。 | 通过。 |
| 未建立索引、未知节点或错误参数产生不稳定失败 | 中 | 断言 `not_indexed`、`not_found`、`invalid_input` 和 `resource_limit`。 | 通过。 |
| 根目录外读取或失败索引破坏可用快照 | 高 | 拒绝 `../not-allowed`；在资源超限后验证前一快照仍可查询。 | 通过。 |
| MCP 工具未正确注册或协议输出无效 | 高 | 真实 stdio 客户端列工具并调用索引、搜索。 | 通过。 |

## 残余风险与条件

| 残余风险 | 原因 | 缓解与复审触发 |
|---|---|---|
| 多语言代码覆盖不足 | 首版只解析 Python AST。 | 实际任务反复涉及其他语言时，以新 ADR 评估 Tree-sitter parser adapter。 |
| 术语关联可能带来弱相关结果 | `shares_terms` 基于受控词项重叠，而非语义证明。 | 所有关系附理由；Agent 应读取原节点并以 `cites`/定位为证据。若召回噪声高，加入词典或可选向量召回评估。 |
| Markdown/YAML 解析为当前卡片格式优化 | 不支持完整 YAML 语法或任意 Markdown 语义。 | 对新格式先添加夹具和测试；不把 YAML 当成可执行配置。 |
| 索引为进程内快照 | 重启后需重新索引，且没有增量持久化。 | 仅在用户提供真实规模/速度需求后评估持久化、文件哈希和增量更新。 |
| 尚未验证所有 MCP 客户端 | 本轮只验证官方 Python SDK 客户端与 stdio。 | 用户在目标客户端手动添加示例配置后运行 `index_repository` 进行验收；配置修改需用户执行/确认。 |

## 质量结论

当前实现达到 **R1 本地可运行与可验证** 标准：关键成功路径、错误路径、根目录隔离、输出预算和真实 MCP 协议路径均有自动化证据。它尚不适合被表述为多语言或生产级大规模索引服务；任何持久化、网络、写工具、客户端自动配置或发布行为必须走新的范围评审和人工审批。

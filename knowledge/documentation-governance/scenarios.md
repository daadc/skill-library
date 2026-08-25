# 开发文档治理场景卡

## SC-DOC-001：新增异步批量导入功能

**输入。** 前端上传 CSV，后端创建导入任务，Kafka worker 处理，用户查看进度/错误并可重试。

**必须同步维护。** Opportunity/验收与未知项；交互契约（状态、幂等、权限、错误、进度、SSE/轮询）；OpenAPI/schema；ADR（仅当技术/拓扑决定显著）；数据迁移/保留；Kafka 事件/重放/DLQ；Runbook（积压、失败、恢复）；发布契约和用户 how-to/reference。

**通过条件。** PR 中能链接每项文档或给出无影响理由；CI 能校验 schema/链接/模板 metadata；非作者能按文档完成任务、处理失败并知道何时升级；发布后观察业务完成率、错误和积压并将反馈写回文档。

## SC-DOC-002：数据库迁移和 API 兼容变更

**输入。** 订单状态字段要拆为状态机；旧 API 客户端依赖旧字段；有历史数据和外部集成。

**必须同步维护。** ADR/迁移 charter、OpenAPI 弃用和混合版本行为、事件 schema、对账规则、回退/不可逆点、Runbook、release contract、消费者迁移指引。

**通过条件。** 新旧 source of truth、dual-read/write 范围、对账和删除条件清晰；不能以“migration 成功”替代正确性；无消费者确认、兼容测试、发布/回滚记录则不得进入 R2/R3 发布准备。

## SC-DOC-003：生产告警的 Runbook 是否真实可用

**输入。** Kafka consumer lag 突增，可能影响订单履约。

**演练。** 非 Runbook 作者根据文档判断影响/升级级别，建立事件状态文档，分配指挥/操作/沟通，执行受控诊断，记录每步证据，选择缓解/回滚，完成明确交接和复盘。

**通过条件。** 没有未授权自由操作；关键上下文、权限、dashboard、停止条件、回退和升级路径可找到；演练发现的问题更新到 Runbook、告警、架构/韧性卡或 backlog。

## SC-DOC-004：文档陈旧性审计

**输入。** 某服务升级 Go 版本、修改 OpenAPI、调整 Redis 缓存策略，并发生一次支持工单。

**通过条件。** 自动/人工检查能定位受影响的参考、ADR、契约、Runbook 和 how-to；owner 在 review deadline 前选择 verified/update/supersede/retire；所有变更保留历史和关联证据，不能通过删除旧文档抹掉决策理由。

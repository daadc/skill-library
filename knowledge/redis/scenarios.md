# Redis 场景卡

## SC-RDS-001：缓存雪崩与数据库回源

**输入。** 某批热点 key 同时过期，Redis 命中率下降，PostgreSQL 连接池耗尽，API P99 恶化。

**责任路由。** `platform-sre-engineer` 稳定流量与采集证据；`data-engineer` 评估 Redis 驱逐/内存和数据库回源；`backend-runtime-engineer` 审查 TTL、并发重建、请求合并和降级；`quality-engineer` 建立压测回归。

**通过条件。** 明确权威源与可接受陈旧度；证明保护机制不会制造陈旧数据或热点锁；验证 Redis 不可用、热点突发、回源超时和逐步恢复。

## SC-RDS-002：重要 Redis 数据的恢复演练

**输入。** 服务使用 Redis 存储短期会话与可恢复任务状态，要求验证 RPO/RTO。

**通过条件。** 指明 RDB/AOF/组合方案、fsync 语义、跨机备份、恢复步骤、数据校验、恢复耗时和失败处理。仅有文件副本不视为通过；必须在隔离环境恢复并核验关键数据。

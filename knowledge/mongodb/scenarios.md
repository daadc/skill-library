# MongoDB 场景卡

## SC-MDB-001：主节点故障与读语义

**输入。** 复制集 primary 不可用，业务需要决定是否把部分读请求切向 secondary。

**责任路由。** `data-engineer` 明确 read preference、read concern、write concern、复制延迟与故障窗口；`backend-runtime-engineer` 审查驱动重试与连接池；`platform-sre-engineer` 观察选举、lag、网络与容量；`quality-engineer` 验证用户语义。

**通过条件。** 明确哪些界面/接口可容忍陈旧读取，哪些必须 primary 读取；验证故障转移、重试、可能回滚和恢复后的数据正确性；禁止把“secondary 可读”描述为无条件安全。

## SC-MDB-002：分片前评审

**输入。** Collection 体量和写入增长，团队提出分片以解决性能问题。

**通过条件。** 先提供查询/写入/大小/索引/热点证据；给出候选分片键、目标查询、数据分布、balancer/备份/恢复影响；对比模型、索引、归档和单副本集优化。参见 KC-MDB-003 与共享场景 SC-DATA-001。

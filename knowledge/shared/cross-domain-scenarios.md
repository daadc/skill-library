# 跨领域协作场景

以下场景用于将知识卡转化为团队可评测的工程判断。它们不是可直接执行的生产变更脚本；所有生产操作仍需人工批准。

## SC-PLAT-001：多租户订单导入平台

**背景。** B2B 管理后台需要接受 10 万行 CSV 导入。外部请求经 Nginx 到 Kubernetes 服务；任务写入 Kafka；worker 解析后写 MongoDB；状态和短期幂等键保存在 Redis；最终业务数据同步到 PostgreSQL。

| 阶段 | 主责任角色 | 协作角色 | 必交付物 |
|---|---|---|---|
| 需求与风险 | 产品 | 架构、质量 | 用户目标、最大文件、SLO、错误恢复、验收条件 |
| 架构 | 架构 | 后端、数据、SRE | 数据所有权、异步边界、ADR、失败/重放/回滚策略 |
| 边缘与集群 | SRE | 后端、前端 | Nginx 代理/限流策略、Kubernetes 资源与发布契约 |
| 流与存储 | 数据 | 后端、SRE | Kafka topic 契约、Mongo 模型、Redis 一致性/TTL、PostgreSQL 写入契约 |
| 验证 | 质量 | 全体 | 大文件、重复投递、worker 宕机、Kafka 回放、Redis 失效、数据库失败和发布回滚测试 |

**关键验收。** 必须证明同一导入不会产生重复业务写入；错误行可定位且可重试；Kafka 回放不会绕过权限或破坏一致性；Nginx 保护不能误伤有效租户；Kubernetes 发布失败能够停止扩大影响。

## SC-PLAT-002：Kafka 消费延迟与 Redis 缓存故障并发发生

**背景。** 消费延迟持续上升，同时 Redis 驱逐率升高，worker 开始回源 MongoDB，Nginx 上游 P99 增加。

**预期协作。**

1. `platform-sre-engineer` 建立时间线、影响面、变更记录与系统级指标，先控制扩大影响。
2. `data-engineer` 区分 Redis 内存/驱逐、Mongo 查询/复制延迟、Kafka 分区/消费组滞后的因果与相关性。
3. `backend-runtime-engineer` 检查消费批量、并发、回源保护、超时、重试与幂等，不得把无限重试当修复。
4. `tech-lead-architect` 判断是否存在缓存与消息耦合的结构性问题，并提出可逆修复路径。
5. `quality-engineer` 把真实失效机制转化为负载与故障回归场景。

**不可接受结论。** 只重启 Pod；未看分区键/消费并发就加 worker；未看缓存键/TTL/数据源就扩 Redis；把 consumer lag 当作唯一根因。

## SC-PLAT-003：Kubernetes 升级与 Nginx 配置变更

**背景。** 同一窗口内计划升级 Kubernetes minor 版本，并更改 Nginx upstream/限流配置。

**强制门禁。**

- 拆分为可独立验证的变更，避免在没有明确必要性时叠加风险。
- K8s 变更必须提交版本兼容清单、Webhook/CNI/CSI/Ingress 检查、etcd/恢复证据、节点 drain 策略和每批停机条件。
- Nginx 变更必须先 dry-run 或预生产回放，明确真实客户端来源链、限流 key、上游超时/重试与回滚配置。
- 任何一个变更出现 SLO 恶化均应停止下一批；回滚需同时考虑镜像、清单、配置和数据/协议兼容性。

## SC-DATA-001：MongoDB 分片与 Kafka 事件契约演进

**背景。** 某 collection 增长过快，团队希望同时引入 MongoDB 分片和 Kafka 新事件字段。

**验证问题。** 分片键是否分散写入并支持主要查询？新字段是否向旧消费者兼容？回放历史事件时字段缺失和默认值如何处理？分片、索引与消费者重放会否导致热点或数据泄漏？是否建立了迁移、备份、恢复和回滚演练？

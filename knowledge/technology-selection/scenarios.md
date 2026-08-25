# 技术选型场景卡

## SC-SEL-001：Go B2B 订单服务的 Web 与数据访问选择

**输入。** 团队 5 人，需要在 3 个月交付多租户订单、库存预占和运营后台；PostgreSQL；日均 100 万请求，峰值写入 200 rps；已有 Go 经验但无复杂 Web 框架长期维护经验。

**评审任务。** 比较 `net/http` + router、团队熟悉的 Web 框架、以及是否需要 BFF；比较 GORM、`database/sql`/显式 SQL 在管理 CRUD、库存预占与运营报表上的组合。禁止只写“Gin/Fiber/GORM 更快/更流行”作为理由。

**通过条件。**

1. 给出两周 POC：一个订单 command、一个游标查询、一个库存条件更新、一个管理列表；包含 tracing、deadline、错误、迁移和 contract tests。
2. 输出真实 SQL、执行计划、连接池上限、事务/冲突处理和压测结论。
3. 合同使用 OpenAPI，状态机包含 `accepted/processing/succeeded/failed`，命令有 idempotency key。
4. 最终 ADR 记录团队维护成本、依赖升级、出口方案及 6 个月复审触发。

## SC-SEL-002：异步导入与前端进度体验

**输入。** 用户上传 10 万行 CSV；系统需校验、导入、展示行级错误并允许重试；导入由 Kafka worker 执行。

**通过条件。** 入口返回 task ID 和状态契约，不让 HTTP 长连接承担处理；明确轮询/SSE 选择、进度准确度、终态、错误文件授权、重复上传、取消、worker 重启、消息重复/乱序、事件/数据版本和前端回退策略。质量团队在前后端混合版本、网络断开、API 失败与重新进入页面后验证体验。

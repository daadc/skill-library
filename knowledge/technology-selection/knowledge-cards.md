# 技术选型与前后端契约知识卡

## KC-SEL-001：框架选型不是排行榜，而是可逆性与风险决策

**问题。** 如何在 Go Web、ORM、API 风格和前端交互方案之间做选择？

**原则。** 先比较真实用例的生产语义：团队熟悉度、可观测性、安全、错误处理、取消/超时、测试、迁移、维护者活跃度、依赖风险、性能/容量和未来替换成本。选择应记录在 ADR 中，包含不选项、POC 任务、成功门槛和退出策略；不要凭 benchmarks、下载量或“行业流行”替代上下文。

```yaml
selection_record:
  decision: ""
  workload_and_slo: ""
  team_constraints: []
  mandatory_capabilities: []
  options:
    - name: ""
      evidence_from_poc_or_docs: []
      benefits: []
      costs_and_risks: []
      exit_or_replacement_path: ""
  decision_and_review_trigger: ""
```

---

## KC-SEL-002：Go Web 层的选择与不可谈判项

**基线。** `net/http` 提供 HTTP client/server、handler、request context、`Server.Shutdown`、请求大小控制等标准能力；客户端和 transport 可被多个 goroutine 并发安全复用，适合作为任何 Go Web 框架兼容性的判断基线。[1]

| 方案 | 适用条件 | 风险与补偿 |
|---|---|---|
| `net/http` + router/middleware | 需要少依赖、长期可维护、团队了解 HTTP 细节、服务边界清楚 | 需要自己统一绑定/验证/错误/日志/tracing；用内部 starter/中间件减少复制 |
| 成熟 Web 框架 | 快速交付，需路由/绑定/验证/中间件约定，团队已具备维护经验 | 验证对标准 `http.Handler`、context、错误、测试、observability、依赖升级和退出路径的支持 |
| BFF / 前端专用 API | 多端体验差异大、页面需要聚合多个后端、减少客户端编排 | 不让 BFF 成为隐藏领域核心；保持 domain API 归属，控制聚合超时/缓存/权限 |

**任何方案必须实现。** 显式 server read/write/idle 超时、最大 body、全链路 context/deadline、优雅关闭、认证/授权、输入验证、稳定错误格式、日志/metrics/traces、rate limit、健康检查和依赖保护。框架只是承载这些策略的容器。

---

## KC-SEL-003：GORM、SQL 与 Repository/Port 的边界

**原则。** GORM 对常规 CRUD、关联、transaction、context、批处理、迁移、日志和扩展有成熟能力；标准 `database/sql` 提供事务、连接池、context 取消及更直接的 SQL 控制。[2] [3]

| 工作负载 | 合理起点 | 审查重点 |
|---|---|---|
| 管理后台与常规业务 CRUD | GORM，可通过 repository/adapter 封装 | 模型与 DTO/领域对象不要混用；审 SQL、Preload/N+1、事务和索引 |
| 核心读模型、复杂搜索/报表 | 显式 SQL 或受控查询工具 | 执行计划、统计信息、分页、锁、超时、连接池、性能回归 |
| 高并发写入/库存/账务 | 显式事务 + 条件更新/版本控制；必要时专用 SQL | 幂等、隔离级别、死锁/重试、唯一约束、审计与对账 |
| 多存储/读写分离 | application port + 外部 adapter；数据归属明确 | 避免 ORM 模型跨 context；一致性、故障、回滚、测试 double |

**禁止结论。** “使用 ORM 所以不用懂 SQL/索引/事务”“`AutoMigrate` 所以生产迁移安全”“Repository 必须给每张表一套接口”。GORM 的实际 SQL、迁移兼容、锁/事务、批量操作和连接池都要被观测与测试。

---

## KC-SEL-004：前后端交互策略

| 需求 | 默认策略 | 必须额外声明 |
|---|---|---|
| 正常读写 | REST/HTTP + OpenAPI，资源或用例导向 | 权限、验证、错误码、幂等、分页/排序、缓存和弃用 |
| 需要一次加载多个领域数据 | BFF 或后端聚合 endpoint，明确 deadline 和部分结果语义 | 聚合 owner、缓存、失败/降级、N+1 调用与观测 |
| 长时间处理 | `202 Accepted` + task resource；前端轮询、SSE 或 webhook 订阅 | 状态机、进度、取消、终态、幂等、过期与权限 |
| 实时状态推送 | SSE/WebSocket（必要时） | 断线重连、事件 ID、顺序范围、补偿查询、权限、背压 |
| 领域异步集成 | 事件总线，对外用稳定事件 schema | 事件不是 UI DTO；版本、key、交付、去重、重放、DLQ、数据修复 |

OpenAPI 是 HTTP 接口的可版本化机器可读描述，可驱动文档、代码生成与测试；前端和后端还应共同维护用例状态机、错误体验和渐进兼容规则。[4]

---

## KC-SEL-005：前端状态与 API 边界

**原则。** 将服务端事实、缓存/异步状态、表单临时状态和纯 UI 状态分开。前端不能假设一次 mutation 后读取模型已完全一致；后端不能要求前端重建内部领域状态。

| 状态 | Owner | 例子 | 协作要点 |
|---|---|---|---|
| 领域事实 | 后端 context | 订单状态、库存预占、权限 | 通过 query/事件暴露稳定语义与版本 |
| 请求/缓存状态 | 客户端数据层 | loading、stale、retry、optimistic update | 明确新鲜度、失效、冲突、重复提交和错误恢复 |
| 表单状态 | 前端 | 未提交输入、草稿、局部校验 | 提交时映射到 command；不要直接复用后端实体 |
| UI 状态 | 前端 | modal、tab、展开项 | 不进入 API/领域模型 |

**乐观更新边界。** 只有命令可幂等、冲突可显示/恢复、失败可回退、权限与服务端规则最终裁定时，才使用乐观 UI；库存、支付、权限和长任务默认采用明确的处理中状态。

## References

[1]: https://pkg.go.dev/net/http
[2]: https://gorm.io/docs/index.html
[3]: https://go.dev/doc/database/
[4]: https://spec.openapis.org/oas/v3.2.0.html

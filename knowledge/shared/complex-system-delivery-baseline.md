# 复杂系统交付基线

> **目的。** 本基线用来决定“是否值得做、如何设计、怎样安全交付与如何持续演进”。它不是项目计划模板；每一步都必须产出可审查证据，并按风险允许删减。没有用户调研、领域边界、接口/数据契约、质量证据或运行反馈的“设计完成”，一律视为未完成。

## 1. 端到端交付链

| 阶段 | 主责任 | 关键问题 | 强制产物 | 退出门禁 |
|---|---|---|---|---|
| 发现与调研 | 产品、设计、工程 | 哪个用户/场景/结果值得解决？现有证据与未知是什么？ | Opportunity brief、研究计划、假设台账、成功指标/反指标 | 至少有行为、访谈、工单或业务数据中的一种直接/间接证据；所有假设有验证方式 |
| 领域建模 | 产品、架构、领域专家 | 统一语言、核心/支撑/通用子域、上下文、规则和例外是什么？ | 术语表、事件/命令流、Context Map、领域风险 | 不按数据库表或技术层划领域；数据所有权与外部边界明确 |
| 方案决策 | 架构、后端、数据、平台、前端 | 哪种架构/框架/数据模型最小且可演进？ | ADR、选型矩阵、接口/事件/数据契约、威胁/失败模型 | 选项至少包含保持简单的替代方案；明确迁移、回退、SLO、成本和未知项 |
| 切片交付 | 实现角色、质量 | 最小可验证价值切片是什么？ | 垂直切片计划、可构建产物、变更说明 | 能在隔离环境通过关键功能和失败路径验证 |
| 发布准备 | 质量、SRE、数据、韧性 | 会怎样失败、如何发现、何时停止、如何回退？ | 发布契约、测试矩阵、Runbook、仪表盘/告警、回滚/修复方案 | 高风险变更完成演练；数据/权限/账务有人工批准 |
| 渐进上线 | SRE、产品、实施角色 | 金丝雀的样本、观察窗与决策阈值是什么？ | 灰度计划、实时指标、停止条件 | 业务与技术信号同时达标；异常可止损 |
| 学习与演进 | 全团队 | 假设是否成立？遗留/债务/体验问题如何进入下一轮？ | 上线复核、复盘、行动项、知识卡更新 | 行动项有 owner、优先级、期限和验证证据 |

## 2. 需求调研协议

**任何功能在写 PRD 前先建立“证据—假设—实验”表。** 产品、设计和工程共同负责：产品验证价值与商业约束，设计验证可用性，工程验证可行性、成本、隐私/安全与运行风险。调研不等于“问用户想要什么”；应结合观察、日志、工单、访谈、原型和对照实验，区分用户陈述与真实行为。[1] [2]

```yaml
opportunity:
  target_user_and_context: ""
  job_or_problem: ""
  current_workaround_and_cost: ""
  evidence:
    - kind: "行为数据 | 访谈 | 观察 | 工单 | 市场 | 原型测试"
      finding: ""
      limitations: ""
  hypotheses:
    - statement: ""
      risk: "value | usability | feasibility | viability | security | reliability"
      validation_method: ""
      pass_fail_signal: ""
  success_metrics: []
  guardrail_metrics: []
  non_goals: []
```

**研究选择。** 方向未知时优先生成性研究（现场观察、访谈、日志/工单分析、概念测试）；交互设计阶段使用形成性研究（原型可用性测试、卡片分类、树测试）；上线后使用评估性研究（任务成功率、漏斗、A/B、反馈）。定性研究解释“为何/如何修”，定量研究量化“多少/多大”；不将二者互相替代。[2]

## 3. 架构风格与模式决策树

> 先选**问题边界**，后选框架。DDD、MVC、六边形、CQRS、事件驱动、微服务都是工具箱中的不同层次，不能互斥地当作唯一“架构”。

| 选择 | 适用信号 | 最小实践 | 不适用/风险 |
|---|---|---|---|
| MVC / Handler-Application-View | 以同步 Web/CRUD 交互为主，业务规则相对简单 | Controller/Handler 只处理 HTTP；应用服务编排用例；View/DTO 不泄漏持久化模型 | 将业务规则堆进 Controller，或把 MVC 误当完整领域/部署架构 |
| 分层架构 | 边界稳定、团队小、中等复杂度 | 表现层→应用层→领域/业务层→基础设施；依赖方向受控 | 数据访问模型直接穿透到 UI/业务；复杂领域被贫血模型吞没 |
| 模块化单体 | 团队/系统仍小或领域尚在探索，但需要隔离变化 | 按业务模块分包；模块 API、数据所有权和依赖规则由 CI 检查 | 为“未来微服务”预先引入网络调用、分布式事务和独立部署成本 |
| DDD（战略） | 复杂规则、术语歧义、多业务角色、长期演进 | 子域分类、统一语言、bounded context、Context Map；核心域投入更多设计 | 简单 CRUD 或通用子域过度建模；把实体/聚合当作机械目录规范 |
| 六边形 / Ports & Adapters | 核心规则复杂、外部依赖多、需高可测试性或逐步替换 | 领域/应用定义 port；HTTP、DB、Kafka、第三方 API 为 adapter；依赖向内 | 只有单一简单 DB CRUD 时增加过多接口和文件层次 |
| 事件驱动 | 工作可异步、需削峰/解耦/审计/回放，接受最终一致 | 明确命令与事实事件、schema、key、顺序、去重、retry/DLQ、可观测性 | 把同步查询硬改异步；没有幂等、回放和数据修复能力 |
| CQRS | 读写模型/扩缩/安全/性能差异明显且可承担双模型成本 | 先分离命令与查询接口；只有读模型收益可证明时再物理分离 | 用它逃避数据建模，或未处理投影延迟/一致性/重建 |
| 微服务 | 有清晰业务能力边界、独立发布/扩缩/SLO/团队所有权的已测需求 | 从模块化单体抽取一个垂直能力；先建契约、观测、发布、数据归属和迁移切片 | 按技术层拆分、共享数据库、同步调用链过深、平台能力不足 |
| Cell / 分片隔离 | 多租户/区域爆炸半径或合规/容量隔离收益大 | 稳定路由键、cell 级 SLO/容量/发布/演练、明确控制面 | 小团队为“高可用标签”复制基础设施而无验证收益 |

**DDD 与 MVC 的关系。** MVC/Handler 是用户交互边界的组织方式；DDD 是复杂领域的建模和边界方法；六边形是依赖方向方法；模块化单体/微服务/cell 是运行与部署拓扑选择。一个系统可在模块化单体中对核心域使用 DDD 和 ports/adapters，在入口层使用 HTTP handler/MVC 风格；不应要求所有子域同等复杂。

## 4. 服务、数据和前后端契约

每个同步 API、异步事件和 UI 状态必须有**版本化契约**。OpenAPI 可描述 HTTP 表面并生成文档、客户端/服务端骨架和测试，但还应在契约旁写明业务语义、权限、幂等、分页、错误、并发、异步进度、兼容与弃用策略。[3]

```yaml
interaction_contract:
  use_case: "提交订单"
  actor_and_permission: ""
  command_or_query: ""
  request_and_response_schema: "OpenAPI/JSON Schema reference"
  state_machine: "pending -> accepted -> processing -> succeeded|failed"
  validation_and_domain_rules: []
  idempotency: "key scope, retention, duplicate result semantics"
  concurrency: "version/ETag/optimistic lock or serialized command key"
  errors: "stable code, retryability, user message, correlation id"
  async_behavior: "poll/webhook/SSE/event; progress/terminal states"
  pagination_filter_sort: "stable sort, cursor/version semantics"
  compatibility_and_deprecation: "additive first, feature flag/canary, expiry"
  observability: "trace/correlation ID, product events, SLI"
```

## 5. Go Web 与 GORM 选型协议

**Go HTTP 层。** 默认从 `net/http` 与一个明确维护的 router/middleware 组合开始。需要更快搭建成熟路由、绑定、验证、请求日志或统一中间件时，再选择团队已熟悉、可审计、可观测、与标准 `http.Handler` 兼容的 Web 框架。无论框架如何，必须显式配置 server/client 超时、最大请求体、context 取消、优雅关闭、错误映射、身份鉴别、限流与 tracing；框架不会自动提供这些生产语义。[4]

**GORM/SQL 数据层。**

| 场景 | 优先选择 | 必须保留的检查 |
|---|---|---|
| 快速开发、常规 CRUD、关联模型、团队熟悉 GORM | GORM，可用 Generics API / context / logger / transaction | 审查生成 SQL、N+1、Preload、事务边界、索引和连接池；迁移不等于生产变更计划 |
| 查询是核心竞争力、复杂报表/窗口函数、批量更新、极致性能 | 显式 SQL / `database/sql` 或受控查询工具 | SQL 版本化、参数化、执行计划、锁/事务、取消、连接池、回归/负载测试 |
| Schema 迭代、类型安全、代码生成有明显收益 | 评估 `ent` 或其他生成工具，但用一个真实垂直切片 POC 比较 | 迁移文件、领域模型与持久化模型分离、构建/审查成本 |
| 多数据库/多读写路径 | 显式 repository/port 与具体 adapter；不要让 ORM 类型跨边界 | 一致性、路由、事务语义、故障与回退 |

GORM 不是禁止或默认选择；它是提升部分开发效率的库。数据所有权、显式事务、迁移、索引、观察真实 SQL、执行计划和高风险路径压测属于团队不可外包的职责。[5] [6]

## 6. 复杂系统质量证据

| 风险 | 最小证据 | 高风险补强 |
|---|---|---|
| 需求/体验 | 可验证假设、原型/用户/行为证据、验收标准 | 分群研究、可用性基准、灰度实验和护栏指标 |
| 领域规则 | 单元/属性/示例测试、统一语言映射 | 模型审查、规则覆盖、边界/异常场景和领域专家验收 |
| API/前后端 | OpenAPI/Schema、contract tests、mixed-version test | 消费者驱动契约、弃用演练、跨端 E2E、权限/错误体验测试 |
| 数据 | 迁移演练、备份恢复、数据不变量/对账 | 影子读/双写对账、CDC 延迟/恢复、锁/性能/容量压测 |
| 并发/依赖 | deadline、幂等、资源上限、超时/重试/降级测试 | 故障注入、过载、恢复积压、部分失败、租户隔离测试 |
| 发布/运行 | 不可变产物、灰度、仪表盘、停机/回滚 | 演练、game day、cell/区域故障、回放和人工接管 |

## 7. 重构控制协议

重构分为**内部整理**（不改变外部行为）与**现代化/迁移**（可能改变边界、数据或运行拓扑）。两者都从可观察基线开始；后者必须使用增量切片而非“大爆炸重写”。

```yaml
refactoring_charter:
  business_outcome_and_baseline: ""
  behavior_to_preserve_and_behavior_to_retire: []
  seams_and_smallest_migration_slice: []
  legacy_new_coexistence: "facade/ACL/shadow/dual-read or dual-write"
  source_of_truth_per_phase: ""
  data_reconciliation_and_invariants: []
  compatibility_and_routing: ""
  observability_and_success_thresholds: []
  rollback_window_and_point_of_no_return: ""
  deletion_criteria_for_legacy: []
  organization_and_ownership_changes: []
```

## References

[1]: https://www.svpg.com/discovery-problem-vs-solution/
[2]: https://www.nngroup.com/articles/which-ux-research-methods/
[3]: https://spec.openapis.org/oas/v3.2.0.html
[4]: https://pkg.go.dev/net/http
[5]: https://go.dev/doc/database/
[6]: https://gorm.io/docs/index.html

# 端到端复杂系统团队演练：多租户采购与履约平台

> **性质。** 这是用于检验团队方法的假设性场景，不是假装已经完成的用户调研或生产方案。所有业务规模、指标和用户发现均标记为 `unknown`，必须由真实调研、流量数据、领域专家和压测补齐后才能实施。

## 1. 假设任务与风险画像

企业客户需要创建采购申请、审批、下单、库存预占、履约跟踪、对账和报表。系统面向多租户，需要 Web 管理端与 API 集成；可能接入外部支付、ERP、物流和身份系统。系统包含订单、库存、审批、结算和审计等复杂规则，适合作为 DDD/契约/韧性/重构方法的演练，但不应据此直接选择微服务或具体框架。

| 维度 | 已知/未知 | 需要的证据 |
|---|---|---|
| 用户与任务 | unknown | 采购、审批、运营、财务、集成方的任务观察/访谈；现有流程、工单、日志 |
| 价值 | unknown | 周期、错误、人工处理、订单失败、合规与客户留存的基线 |
| 容量与 SLO | unknown | 峰值读写、批量任务、可用性/延迟、RPO/RTO、租户热点与成本 |
| 规则与一致性 | 部分可推断，尚未证实 | 领域专家确认的审批、额度、预占、取消、结算、审计不变量 |
| 外部依赖 | likely | ERP/支付/物流的 SLA、限额、幂等、回调、故障与合规契约 |

## 2. 发现与需求验证

**产品、设计、工程共同完成。** 先把“做采购平台”拆成可验证机会，例如“审批人不知道哪些申请阻塞履约”“运营无法可靠发现库存预占失败”。每个机会创建 evidence/assumption/experiment 表，不允许以功能清单替代调研。

| 风险 | 最小研究 | 可交付证据 |
|---|---|---|
| 价值 | 任务访谈 + 工单/日志分析 | 当前耗时、错误、影响用户、替代方案、机会优先级 |
| 可用性 | 任务原型/可用性测试 | 成功率、错误、理解偏差、恢复体验和信息架构反馈 |
| 可行性 | 跨角色技术 spike | 核心规则、数据/集成、容量、SLO、隐私与成本的 POC 结果 |
| 可行商业/组织性 | 权限、审计、合同、支持流程审查 | 合规约束、批准者、运维/支持 owner 与不可接受风险 |

**第一个交付切片。** 只选择“提交采购申请 → 规则校验 → 审批任务 → 明确进度查询”的小闭环；不在首期同时做 ERP 双向同步、实时库存、自动支付、复杂推荐和全量 BI。

## 3. 领域模型与上下文地图

先建立统一语言并允许不同上下文不同模型。下表是待验证的假设 Context Map。

| Bounded Context | 核心职责/规则 | 权威写入数据 | 上下游契约 |
|---|---|---|---|
| Procurement Request | 申请草稿、提交、金额/类别校验、申请状态 | request、line、version | 对 Approval 发 `RequestSubmitted`；查询给 Web/BFF |
| Approval | 审批流、委派、SLA、拒绝/撤回 | approval decision、policy snapshot | 消费申请事件；发 `RequestApproved/Rejected` |
| Order | 下单、取消、履约状态机、客户可见状态 | order、order-line、idempotency record | 消费批准结果；命令库存/外部 ERP；发事实事件 |
| Inventory Allocation | 可售、预占、释放、回补 | allocation、inventory version | 接收预占/释放命令；返回明确结果，不共享订单表 |
| Settlement/Audit | 对账、不可篡改审计、财务导出 | ledger/audit entries | 只订阅已承诺事实；不反向改变订单核心规则 |
| Identity/Tenant | 身份、租户、角色、配额 | identity mapping、tenant policy | 提供权限/租户边界；是通用/外部能力 |

**不变量示例（待领域确认）。** 已批准申请才能创建订单；同一业务请求不会生成两笔订单；库存预占不能低于可售规则；审批决策应保留当时规则版本；租户之间不能读写或推断彼此数据。

## 4. 推荐的初始拓扑：模块化单体 + 明确边界

在团队/领域仍在学习阶段，默认采用 **Go 模块化单体**：一个部署单元，按 bounded context 分模块；HTTP handler/MVC 在入口层，application service 编排用例，核心规则在领域模块，PostgreSQL/Redis/Kafka/ERP 通过 adapter 访问。模块依赖和数据所有权由 CI/代码审查约束；只在订单、库存或集成已证明有独立部署/扩缩/SLO/所有权价值时抽取垂直能力。

```text
React/Vue Web
   │ OpenAPI client + task/status UX
   ▼
HTTP / BFF edge (auth, rate limits, request deadline, error mapping)
   ▼
Go modular application
   ├── procurement-request context
   ├── approval context
   ├── order context
   ├── inventory-allocation context
   └── adapter layer
        ├── PostgreSQL (context-owned schemas/tables)
        ├── Redis (explicit cache/lock policy; not source of truth)
        ├── Kafka (outbox-published facts; idempotent consumers)
        └── ERP/payment/logistics ACL adapters
```

| 架构选择 | 当前结论 | 重新评估触发条件 |
|---|---|---|
| MVC/Handler | 仅用于 HTTP/UI 边界，负责 DTO、鉴权、错误映射和调用应用用例 | 无 |
| DDD | 核心审批/订单/库存规则使用，建立统一语言、context 和不变量 | 规则被证实简单时降低建模复杂度 |
| Ports & Adapters | 外部 ERP/支付/消息/DB 边界使用，保护领域不受 SDK/schema 侵蚀 | 单一简单依赖时可保持轻量 |
| 模块化单体 | 初始拓扑 | 独立发布/扩缩/SLO/owner 的收益及平台能力已被量化证明 |
| 微服务/CQRS/Cell | 暂不默认采用 | 指定 context 的负载、读写差异、隔离或组织边界有数据支持 |

## 5. API、异步与前端交互契约

### 示例：提交采购申请

```yaml
command: POST /v1/procurement-requests
actor: requester with tenant-scoped permission
idempotency: Idempotency-Key scoped to tenant + user + request body hash
request: {items: [], costCenter: "", justification: ""}
success: 202 Accepted + requestId + state=SUBMITTED
conflict: 409 with stable code and current version/state
validation: 422 with field/domain errors and correlationId
async: status endpoint with cursor/history; optional SSE after evidence of user need
state_machine: DRAFT -> SUBMITTED -> PENDING_APPROVAL -> APPROVED|REJECTED|CANCELLED
observability: trace/correlation ID, tenant-safe product event, latency/error/duplicate metrics
compatibility: additive schema changes first; deprecation window and mixed-version contract tests
```

前端将表单草稿、请求缓存、领域状态和纯 UI 状态分离。提交后显示 `accepted/processing/succeeded/failed`，而非乐观假设订单/审批即时完成；网络重连后可以按 request ID 恢复状态。权限、空态、部分失败、重复提交、冲突、取消和延迟反馈是验收的一部分。

## 6. Go、GORM 和数据实施选择

**HTTP。** 以 `net/http` 兼容的 router/middleware 为基线。启动时显式设置 server/client deadline、最大请求体、优雅关闭、认证、rate limit、trace 和健康检查；所有出站 I/O 继承 context/deadline。

**数据。** PostgreSQL 是采购/审批/订单/预占的权威事务存储（假设，需容量/合规确认）；每个 context 有写入所有权。管理 CRUD 可以使用 GORM，但核心预占、对账和复杂报表必须以实际 SQL、事务隔离、唯一约束、条件更新、索引/执行计划、连接池和压测为评审对象。不要让 GORM model 直接作为 API 或事件模型。

**异步一致性。** 订单上下文的本地事务写入 outbox；可靠发布者投递到 Kafka；消费者按 event ID/业务版本幂等。跨 context 的订单—库存—履约采用显式 workflow/Saga，写明状态、超时、补偿/人工处理和对账，而非分布式大事务。

## 7. 韧性、容量和安全

| 问题 | 设计门禁 |
|---|---|
| 端到端延迟 | 为 Web→BFF→模块→外部依赖分配 deadline；取消向下传播；不以客户端默认超时替代预算 |
| 重试/副作用 | 仅一层有限重试，退避+抖动；写入/支付/ERP 操作有 idempotency key 和查询/对账路径 |
| 依赖故障 | 每依赖独立连接池/并发/队列；用熔断+降级，但不对审批、余额、权限等关键事实静默返回陈旧数据 |
| 租户洪峰 | 租户配额、优先级/队列、稳定观测维度；验证不会饿死其他租户 |
| Kafka 积压 | 有界并发、lag/age 告警、DLQ/replay、重复/乱序/暂停恢复测试 |
| 安全/隐私 | tenant scope 在每一读写和事件/日志路径验证；审计不可被普通业务接口绕过；密钥/PII 不入日志 |

## 8. 质量工程与发布证据

| 层次 | 关键验证 |
|---|---|
| 领域单元测试 | 审批、订单、预占的状态机/不变量、策略规则、时间边界 |
| API/契约测试 | OpenAPI、错误码、权限、分页、idempotency、混合客户端版本 |
| 数据/迁移测试 | 迁移前后兼容、约束、回填、对账、恢复、真实 SQL 与执行计划 |
| 集成测试 | ERP/支付/物流 adapter、Kafka outbox/重复/乱序、Redis 失效 |
| 韧性/性能 | deadline、超时、重试、连接/队列饱和、熔断恢复、租户隔离、p95/p99/成本 |
| E2E/体验 | 申请、审批、失败恢复、任务重进、可访问性和支持人员排障路径 |
| 发布 | 不可变产物、配置审查、feature flag、金丝雀、业务+技术停机条件、回滚/修复 runbook |

**质量判定。** “代码合并”不是通过；每个切片必须同时通过业务验收、领域/契约、数据、失败路径、可观测性和运行/回退证据。对核心路径设置上线后 review：假设是否成立、错误/等待/放弃是否改善、是否出现新债务或不公平影响。

## 9. 遗留系统重构路径

如已有单体/ERP 深度耦合，使用 Strangler + ACL：先从查询或低风险新功能切片开始，由 façade 路由；用 ACL 翻译遗留模型；对数据做 Expand–Migrate–Validate–Contract；在新旧共存中影子/对账/金丝雀，明确每阶段 source of truth 和回退窗口。只有旧路径无调用、数据不变量验证、观察期和人工审批完成后才删除。

## 10. 角色交接评分卡

| 角色 | 必须交付 | 拒绝通过的条件 |
|---|---|---|
| 产品发现 | 证据/假设/研究计划、用户任务、指标/护栏、非目标 | 没有调研证据却声称用户需要某功能 |
| 架构 | Context Map、ADR、契约、简单方案比较、演进/回退 | 以技术潮流替代业务/容量/SLO证据 |
| 后端/数据 | 垂直切片、SQL/事务、错误/幂等、迁移与性能证据 | ORM/框架抽象替代真实 SQL/资源/失败分析 |
| 前端设计 | 状态模型、错误/恢复/权限/可访问性、合同消费 | 仅交 happy path 或假定同步成功 |
| 平台/韧性 | deadline、资源上限、SLO、告警、故障/恢复演练 | 未知依赖限制、无 stop/rollback 条件 |
| 质量 | 风险矩阵、契约/迁移/韧性/回归证据、残余风险 | 测试数量替代风险覆盖或没有恢复验证 |
| 证据审校 | 来源、版本、私有材料权属、假设边界 | 将 Distilly 或二手摘要当权威事实 |

## 11. 演练通过标准

1. `unknown` 没有被伪装成调研结论、容量或 SLO。
2. 能从用户任务追溯到领域规则、API/事件、数据 owner、测试、指标和 runbook。
3. 每个跨系统副作用有幂等、超时、资源上限、失败/恢复和对账方案。
4. 每项模式/框架选择都有更简单替代方案、适用条件、POC 或运行证据、退出路径。
5. 任一模块/服务/数据迁移都能指出最小切片、回退窗口与不可逆点。
6. 所有高风险生产动作仍需人类 owner 的明确批准。

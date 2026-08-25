# 领域驱动设计与架构风格知识卡

## KC-DDD-001：DDD 的触发条件与停止条件

**问题。** 何时需要 DDD，而不是直接按页面、表或 CRUD 组织？

**使用信号。** 业务规则复杂且不断变化；同一个词在销售、运营、财务或技术侧含义不同；核心竞争力来自规则/决策而不是通用能力；跨团队改动常因模型歧义而返工。DDD 是围绕领域模型、统一语言和可演进边界的方法，尤其适合复杂、混乱逻辑的长期组织；它不要求所有模块都使用复杂战术模式。[1] [2]

| 子域类型 | 处理策略 | 例子 |
|---|---|---|
| 核心子域 | 投入领域专家、模型、测试和专属能力 | 定价、风控、排产、撮合、核心调度 |
| 支撑子域 | 清晰实现与可维护性优先 | 订单后台、运营流程、特定企业集成 |
| 通用子域 | 优先成熟服务/组件或简单实现 | 身份认证、通知、日志、一般报表 |

**停止条件。** 若功能是单一且稳定的 CRUD、没有复杂规则/术语歧义、可用通用 SaaS/库解决，则不要为其强建聚合、领域事件和复杂端口层。将设计能力留给核心子域。

---

## KC-DDD-002：从调研到 Context Map，而不是从表结构到服务名

**问题。** 领域边界如何得出？

**流程。**

1. 以用户场景和业务目标收集命令、事件、规则、角色、例外、外部系统和指标。
2. 建立统一语言表；发现同词不同义（如“客户”“订单”“库存”“结算”）时，保留差异而不是强行统一。
3. 把强内聚规则分成 bounded contexts，并写明上游/下游、数据归属、同步 API/异步事件、翻译层和团队 owner。
4. 先在模块化单体内强制边界；当独立部署/扩缩/SLO/所有权收益被证据证明后再抽取服务。
5. 将 Context Map 作为 ADR 输入；每次业务变化、团队变化或跨域痛点出现时重新评估。

Microsoft 的领域分析建议先理解功能需求，再定义 bounded contexts、应用战术模式、最后识别微服务；边界不应由技术层或组织图自动决定。[3]

```yaml
context_map_entry:
  context: "Order Management"
  purpose_and_core_rules: []
  ubiquitous_language: []
  owner: ""
  authoritative_data: []
  upstream_downstream_relations: []
  integration: "sync API | published event | ACL | no integration"
  invariants: []
  slo_and_failure_semantics: ""
  version_and_deprecation: ""
```

---

## KC-DDD-003：聚合、事务边界与一致性规则

**问题。** 如何避免“每张表一个 Aggregate”或“整个订单加一把大锁”？

**原则。** Aggregate 是为了维护一组必须同时成立的不变量而选择的一致性边界，不是 ORM 关联图或数据库表的同义词。命令应通过聚合根执行；跨聚合/跨 context 的一致性通常需要显式工作流、幂等事件、补偿或人工处理，而不是伪装成全局 ACID 事务。

| 判断问题 | 设计含义 |
|---|---|
| 哪些状态若部分更新会违反业务规则？ | 放在同一事务/聚合内，保持边界小 |
| 哪些行为可接受最终一致？ | 用事件、状态机、对账与补偿；写明用户可见状态 |
| 同一资源会并发修改吗？ | 采用乐观版本、条件更新、命令序列化或短事务；测试冲突路径 |
| 规则跨多个 context 吗？ | 由 application workflow/Saga 编排，保留每一方数据归属 |

**验证。** 对每条核心不变量写示例测试和并发/重复命令测试；对最终一致工作流写状态机、超时、重试、对账和人工兜底。

---

## KC-DDD-004：MVC、分层、六边形与 DDD 如何组合？

**结论。** 它们解决不同问题，通常应组合而不是二选一。

| 层次 | 解决什么 | 常见实现 |
|---|---|---|
| 交互/表现 | HTTP/UI 输入输出、认证、序列化、错误体验 | MVC controller、Go handler、React/Vue view model |
| 应用层 | 用例编排、事务边界、权限、调用 domain port | command/query handler、application service |
| 领域层 | 业务规则、状态机、实体/值对象、策略、不变量 | domain model；核心子域优先 |
| 基础设施层 | DB、消息、缓存、第三方服务、文件系统 | repository、client、event publisher adapter |
| 运行拓扑 | 模块化单体/服务/cell、部署、伸缩、SLO | 根据独立演进收益选择 |

六边形架构要求领域/应用核心定义需要的 port，由外部 adapter 实现，帮助基础设施变化不反向侵蚀核心逻辑；MVC 则应停留在入口/视图边界。简单 CRUD 可以保持轻量分层；复杂核心域才需要更严格的 DDD/ports-and-adapters。[4]

---

## KC-DDD-005：前后端交互的领域契约

**问题。** 为什么仅有 DTO 和一个接口文档仍会产生反复联调？

**原则。** 前端不是数据库浏览器；后端也不应暴露内部实体。以用户任务/用例定义 command 和 query，并为异步、并发、错误、权限和状态变迁建立契约。

| 交互类型 | 契约必须声明 | 典型错误 |
|---|---|---|
| 查询 | 筛选、稳定排序、游标、权限、缓存/新鲜度、空态 | offset 分页在易变列表中重复/漏项；返回内部 ORM 对象 |
| 命令 | 输入规则、幂等键、并发版本、成功/重复/冲突语义 | 成功与“已处理过”无法区分；盲覆盖更新 |
| 长任务 | 接受状态、任务 ID、进度、轮询/SSE/webhook、终态、取消 | HTTP 同步等待到超时；前端猜测任务是否成功 |
| 事件 | 事件版本、key、顺序范围、交付语义、幂等、重放/DLQ | 把 DTO 当事件；消费者依赖未承诺的内部字段 |
| 错误 | 稳定错误码、可重试性、用户文案、关联 ID | 前端解析英文错误；把 500 当作业务校验 |

OpenAPI 是 HTTP 交互表面的机器可读描述，应该受版本控制并用于文档、生成与契约测试；状态机和业务语义则必须补充到同一用例文档。[5]

## References

[1]: https://martinfowler.com/bliki/DomainDrivenDesign.html
[2]: https://martinfowler.com/bliki/BoundedContext.html
[3]: https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis
[4]: https://docs.aws.amazon.com/prescriptive-guidance/latest/hexagonal-architectures/overview.html
[5]: https://spec.openapis.org/oas/v3.2.0.html

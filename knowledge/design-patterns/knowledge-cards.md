# 设计模式选择知识卡

> **模式是命名过的取舍，不是目录或类图模板。** 先写出变化源、约束、失败模式和验证，再选择最小模式。若只有一个稳定实现，直接代码通常优于预置抽象。

## KC-PAT-001：模式选择的四个层次

| 层次 | 典型模式 | 要解决的问题 | 不能解决的问题 |
|---|---|---|---|
| 代码/对象 | Strategy、State、Adapter、Facade、Decorator、Factory、Command | 算法变化、状态/协议差异、第三方适配、横切增强、对象构建 | 跨服务一致性、容量、组织所有权 |
| 模块/领域 | DDD context、Ports & Adapters、Repository、ACL | 业务边界、依赖方向、外部模型侵蚀、可测试替换 | 自动消除复杂业务或分布式失败 |
| 交互/数据 | BFF、Gateway Aggregation、CQRS、Saga、Outbox、Cache-Aside | 客户端聚合、读写差异、跨服务事务、可靠发布、缓存 | 不明确的领域模型或缺失幂等 |
| 分布式/运行 | Retry、Circuit Breaker、Bulkhead、Rate Limit、Queue、Cell、Strangler | 临时失败、级联、隔离、削峰、迁移与爆炸半径 | 错误业务语义、无限资源、无观察/恢复能力 |

云/分布式模式应从具体约束选择并接受其 trade-off；一个工作负载常需组合多个模式，例如 retry + circuit breaker、queue + competing consumers、saga + compensating transaction。[1]

---

## KC-PAT-002：常见代码级模式的选择表

| 模式 | 触发信号 | 简化实现（Go 优先） | 不适用/反模式 |
|---|---|---|---|
| Strategy | 同一目标有多种可替换算法/政策，分支持续增长 | 定义小行为接口或函数类型；调用方按显式 policy 选择 | 只有一两个稳定分支仍硬拆十个类型 |
| State | 行为由有限且有迁移规则的状态决定 | 显式状态机 + 转移表/guard；状态持久化和版本可见 | 用状态模式替代简单布尔/枚举，或隐藏状态迁移 |
| Adapter / ACL | 外部/遗留协议、模型、错误语义不兼容 | 在边界翻译 request/response/event；新模型不泄漏旧字段 | 把 adapter 变为无 owner 的万能转换层 |
| Facade | 客户端需要稳定、简化入口但后端复杂 | 明确聚合/路由边界、超时/权限/错误和淘汰计划 | Facade 吞进核心业务，成为瓶颈或永久上帝服务 |
| Decorator / Middleware | 认证、日志、限流、trace、缓存等横切行为可组合 | 标准 `http.Handler` 或小函数包装；顺序/错误/资源语义可测 | 在业务核心散落不可见副作用 |
| Factory | 构造依赖随环境/配置/类型不同，且有验证/生命周期管理 | 组合根集中 wiring；显式返回依赖和 error | 到处用全局 singleton/service locator 隐藏依赖 |
| Command | 操作需排队、审计、延迟执行、重试或远程处理 | 命令 ID、payload、幂等、状态机、handler | 把普通同步 getter 强行命令化 |
| Observer / Pub-Sub | 一个领域事实有多个异步独立反应者 | 发布稳定事实事件，消费者幂等/可重放 | 用事件隐藏关键同步错误；事件直接承载内部 DTO |

Strategy 的本意是将可替换算法隔离并通过共同接口使用，使新增/替换算法不修改调用上下文；若算法少且稳定，额外类型/接口会过度复杂。[2]

---

## KC-PAT-003：模式组合示例

### 异步订单导入

```text
HTTP Command
  → Idempotency Key + Command record
  → Queue-Based Load Leveling
  → Competing Consumers (bounded concurrency)
  → State machine + progress query/SSE
  → Retry with jitter (one layer only)
  → Circuit Breaker/Bulkhead around external dependency
  → DLQ + replay + reconciliation
```

每一层需要明确 owner 和观测：命令状态、队列积压/年龄、worker 并发、重试、熔断状态、失败原因、对账差异与用户体验。不要把所有问题归结为“Kafka 会保证”。

### 遗留系统现代化

```text
Client
  → Facade / Gateway Routing
  → ACL (legacy ⇄ new context)
  → Strangler slice
  → Expand–Migrate–Validate–Contract
  → retire legacy path
```

Facade 负责路由而非领域决策；ACL 保护新语言/模型；迁移必须有数据权威源、对账、回退窗口和删除标准。

---

## KC-PAT-004：Go 中的模式实现守则

1. **偏向组合与小行为接口。** Go 的接口由使用者侧定义；只在多实现/测试替身/边界适配的实际需求出现时抽象。
2. **组合根负责注入。** 在 `main`/bootstrap 组装 DB、HTTP client、Kafka、repository、service 和 handler；避免全局可变单例。
3. **context 只传递请求范围信息与取消。** 不把任意依赖藏进 context；所有 I/O path 应尊重取消/deadline。
4. **错误是契约。** 内部错误可包装；对外映射稳定错误码/可重试性/关联 ID，不暴露基础设施细节。
5. **先测行为再抽象。** 对重构前未知行为写 characterization test；对策略/状态/adapter 写契约测试；对中间件写顺序、短路和资源释放测试。

Effective Go 仍可作为清晰包/接口/命名和错误处理的基础参考，但它明确说明并未覆盖后来加入的泛型、模块和新库；不能把它当作当前生态全部权威。[3]

## References

[1]: https://learn.microsoft.com/en-us/azure/architecture/patterns/
[2]: https://refactoring.guru/design-patterns/strategy
[3]: https://go.dev/doc/effective_go

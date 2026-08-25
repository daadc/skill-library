# 重构与系统演进知识卡

## KC-REF-001：区分代码重构、架构重构与业务现代化

| 类型 | 外部行为 | 主要目标 | 最小安全网 |
|---|---|---|---|
| 代码重构 | 预期不变 | 可读性、重复、局部复杂度、测试性 | 单元/特征测试、静态检查、小 PR、行为对比 |
| 模块重构 | API 可保持或渐进演进 | 边界、依赖方向、所有权、构建/测试速度 | 模块契约、依赖规则、集成测试、可回退合并 |
| 数据/架构迁移 | 可能存在短暂双轨与兼容窗口 | 数据归属、部署拓扑、容量、可演进性 | 迁移 ADR、影子/对账、灰度、回滚和 point of no return |
| 业务现代化 | 保留、改变或淘汰部分行为 | 新业务结果而非技术换代本身 | 需求证据、行为清单、废弃规则、客户/运营迁移和指标 |

**原则。** 不要把“重构”当作无法量化的技术愿望。开始前建立业务/技术基线，例如发布 lead time、事故、错误率、维护工时、测试时间、变化失败率、用户任务成功率或成本；把重构投资与可验证的结果关联。[1]

---

## KC-REF-002：Strangler Fig 的最小迁移切片

**问题。** 如何避免大爆炸重写失败？

**流程。** 先明确现代化结果和需要放弃的遗留行为，再找一个能由 façade、API、队列、表边界或业务流程切开的 seam。新旧系统在一段时间内共存，流量/功能按小切片迁移；每一步都可观测、可对账、可回退。Fowler 指出渐进替换可让投资、收益和学习逐步可见；Microsoft 将 façade 的增量路由、ACL 和数据阶段作为模式的一部分。[1] [2]

```yaml
migration_slice:
  outcome_and_baseline: ""
  capability_and_seam: ""
  client_routing: "facade/feature flag/gateway/versioned API"
  legacy_new_roles: ""
  source_of_truth_by_phase: ""
  compatibility_and_acl: ""
  data_sync_or_backfill: ""
  invariants_and_reconciliation: []
  shadow_or_canary_validation: []
  rollback_window: ""
  point_of_no_return: ""
  legacy_deletion_criteria: []
```

**反模式。** 在不了解遗留行为时宣布全面重写；先建新平台再找用例；无限期双写且没有对账；把 façade 变成永久核心瓶颈；在数据/依赖未清理前宣称迁移完成。

---

## KC-REF-003：数据迁移的 Expand–Migrate–Contract

**问题。** 如何让 schema/数据从旧到新安全过渡？

| 阶段 | 做什么 | 不能做什么 |
|---|---|---|
| Expand | 添加向后兼容 schema/接口、可选字段、影子读或新表 | 立即删除旧列/字段或强制全部客户端同日升级 |
| Migrate | 回填、CDC/同步、双读/有限双写（只在有 owner/对账时）、逐批切读写 | 不测延迟/冲突/失败恢复，不定义 source of truth |
| Validate | 对账不变量、抽样、业务指标、混合版本和恢复演练 | 只看迁移任务“成功”而忽略业务正确性 |
| Contract | 切换单一权威源、观察窗口后删除旧路径 | 在回滚窗口/审计要求未满足时删除旧对象 |

**安全门。** 记录每阶段的权威写入源、读取路径、数据版本、校验方法、回滚可行性和不可逆点。数据库 DDL、回填、CDC、缓存和事件消费者必须共同参与评审；数据迁移不是单纯 ORM migration 文件。

---

## KC-REF-004：遗留模型与新模型之间使用 ACL

**问题。** 为什么把遗留 API/DB schema 直接暴露给新模块，会让新系统继承旧设计？

**原则。** Anti-Corruption Layer 是翻译/适配边界：新 context 只看到自己的语言和模型；ACL 将遗留请求、字段、错误、状态和事件转换为新模型。它增加过渡代码，但防止旧语义扩散，并允许逐步移除。[2] [3]

| ACL 需要转换 | 示例 |
|---|---|
| 数据含义 | `customer_status=2` → 新模型的明确状态与证据 |
| 命令/流程 | 旧系统同步“下单” → 新系统 `OrderRequested` 状态机 |
| 错误 | 遗留 200 + 文本错误 → 稳定错误码、可重试性、关联 ID |
| 事件 | 旧表 CDC → 领域事实事件，加入版本、幂等与去重 |
| 权限 | 遗留角色枚举 → 新 context 的权限策略 |

**删除标准。** 当没有客户端/内部调用、没有回填/对账依赖、所有数据不变量有验证证据、观察期已过且回滚窗口决议完成时，才移除 ACL/旧路径。

---

## KC-REF-005：重构质量保证

**规则。** 重构不是“测试通过即可”。质量证据需覆盖外部行为、数据一致性、性能/容量、失败恢复、部署/回滚、观测与组织 ownership。

| 风险 | 检查方法 |
|---|---|
| 未知遗留行为 | characterization/feature tests、日志/流量分析、领域专家/客服/运营访谈 |
| 兼容性 | consumer contract、mixed-version、旧客户端/旧事件回放、弃用通知 |
| 数据错误 | 不变量、行数/金额/状态对账、抽样、影子读、可审计差异处理 |
| 性能退化 | 基线对比、压测、p95/p99、连接/队列/缓存/成本监测 |
| 故障恢复 | 依赖故障、重复/乱序、暂停/重启、积压清理、回滚/恢复演练 |
| 组织回归 | owner、runbook、值班、仪表盘、知识卡与复审日期 |

## References

[1]: https://martinfowler.com/bliki/StranglerFigApplication.html
[2]: https://learn.microsoft.com/en-us/azure/architecture/patterns/strangler-fig
[3]: https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis

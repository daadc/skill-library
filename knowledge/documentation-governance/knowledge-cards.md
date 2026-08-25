# 开发文档维护知识卡

## KC-DOC-001：把文档变成开发变更的一部分

**问题。** 为什么“上线前补文档”通常导致错误、过期或无人维护？

**原则。** 让文档随代码、配置、API 规范、测试与发布流程一起计划和审查。对外行为、重要选择、运行操作和迁移风险的变化，应在同一 issue/变更集中评估并更新相应文档；文档本身进入版本控制、预览和 CI 检查。GitLab 将功能文档纳入开发 Definition of Done，并对每次内容变更运行检查；这种流程的价值是可审查、可追溯和减少版本漂移，而不是 Markdown 本身。[1]

| 变更 | 默认需更新的文档 |
|---|---|
| 新用户功能 | Opportunity/验收、用户流程、错误/恢复、分析事件、how-to/release note |
| API / event | OpenAPI/schema、示例、错误/权限、兼容/弃用、consumer contract |
| 数据/存储 | migration charter、模型/owner、对账、备份/恢复、runbook |
| 服务/基础设施 | ADR（显著时）、配置参考、SLO/告警、runbook、发布/回退 |
| 重构 | 行为基线、ADR、ACL/迁移切片、退役标准、架构解释 |
| 事故/支持反馈 | 事件状态/复盘、runbook、FAQ/how-to、监控和行动项 |

**验证。** 在 PR 模板/CI 中要求作者声明“影响的文档/无影响理由”；由 owner 或消费者审查链接、预览与可执行性。

---

## KC-DOC-002：ADR 是决策历史，不是架构散文

**触发条件。** 当决定影响结构、关键质量属性或难以逆转的选择，并且存在两个以上合理方案、无既定标准或后续读者需要理解为何如此时，创建 ADR。[2] [3]

**最小结构。** 状态、日期、owner、问题/约束、备选项、决定、理由、后果、置信度、关联代码/规范/指标、复审触发和 supersession 链接。

| ADR 状态 | 含义 | 维护动作 |
|---|---|---|
| `proposed` | 等待评审/证据 | 补齐选项、风险、验证和 owner |
| `accepted` | 当前有效决定 | 不回写历史；按触发器复审 |
| `superseded` | 已被新决定替代 | 链接新 ADR，保留历史和原后果 |
| `deprecated` | 仍可理解但不应复用 | 指向替代/迁移说明 |

**反模式。** 把每个实现细节写 ADR；只有结论没有为什么；在旧 ADR 里静默改写历史；让 ADR 成为过期教程而非清晰决定。[3]

---

## KC-DOC-003：API / 事件文档是可验证契约

OpenAPI 描述 HTTP API 的可发现、可理解表面，并可用于文档、代码生成和测试；它应与服务版本控制、schema 校验和 breaking-change 检查一起维护。[4]

**OpenAPI/Schema 之外仍必须记录。** 用户任务/领域语义、权限、状态机、幂等/并发、稳定错误码与可重试性、分页/排序/缓存、异步进度、交付/顺序/重放、兼容/弃用策略、SLO 与 owner。

**验收。** 每个契约有 producer 和 consumer owner；规范校验、兼容 diff、consumer contract/混合版本测试通过；弃用有通知、迁移路径、观测和删除门槛。

---

## KC-DOC-004：Runbook 与事件文档必须可在压力下使用

**Runbook 结构。** 适用范围/告警，影响与升级条件，权限/安全警告，诊断步骤，每步预期/验证，安全缓解，禁止动作，回滚/恢复，沟通/交接，证据采集，相关 dashboard/配置/代码，owner 与演练日期。

**事件状态文档。** 记录当前影响、指挥/操作/沟通/计划角色、时间线、假设、已尝试动作、结果、风险、待办、客户沟通和明确交接。Google SRE 将职责分离、操作变更集中、实时状态文档和清晰交接作为防止事件响应自由发挥的关键机制。[5]

**验证。** 每季度或架构/告警变化后在非生产环境演练；随机让非作者按 runbook 完成受控任务；记录失败步骤并更新。

---

## KC-DOC-005：按读者任务组织文档，避免“万能页面”

| 类别 | 读者需要 | 写作规则 | 示例 |
|---|---|---|---|
| Tutorial | 学习技能 | 安全、循序、可完成的练习 | 首次创建 Go 服务 |
| How-to | 完成工作 | 目标导向、前置条件和验证明确 | 如何回滚 Kafka consumer 配置 |
| Reference | 查准确信息 | 完整、中立、可检索、结构反映系统 | API 字段、配置项、CLI 参数 |
| Explanation | 理解为何 | 提供背景、约束、关联与观点边界 | 为什么库存使用乐观锁与幂等 |

Diátaxis 的价值在于帮助作者和读者识别内容意图；它是信息架构工具，不强制所有项目采用同一种目录或文风。[6]

---

## KC-DOC-006：陈旧性不是一次审阅能解决的

**规则。** 每项重要文档有 `owner`、`status`、`last_verified` 和 `review_trigger`。文档被代码/契约/配置/告警/上游版本/事故/支持反馈改变时，自动创建或提示 review；到期 owner 必须选择 `verified`、`updated`、`superseded` 或 `retired`，不能静默过期。

| 失效信号 | 推荐处理 |
|---|---|
| 代码/规范变更 | PR/CI 检查链接文档或要求显式无影响说明 |
| 事故/失败发布 | 复盘行动项审计相关 runbook/ADR/release contract |
| 用户/支持反复失败 | 用错误路径补 how-to、FAQ 或参考；验证阅读后任务成功 |
| 上游版本/安全变更 | 标为待验证，更新来源卡和运行前提 |
| owner 离岗 | 在交接前转移文档 owner 和 review 责任 |

## References

[1]: https://about.gitlab.com/blog/five-fast-facts-about-docs-as-code-at-gitlab/
[2]: https://docs.cloud.google.com/architecture/architecture-decision-records
[3]: https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record
[4]: https://spec.openapis.org/oas/v3.2.0.html
[5]: https://sre.google/sre-book/managing-incidents/
[6]: https://diataxis.fr/start-here/

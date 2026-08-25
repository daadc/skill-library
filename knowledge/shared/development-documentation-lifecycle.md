# 开发文档生命周期与质量门禁

> **原则。** 文档是可执行决策、接口、操作和学习的证据，不是交付末尾补写的说明。以代码、配置、API 规范、测试、仪表盘和运行记录为准的事实应尽可能从源头生成或校验；解释“为何”的内容必须有 owner、状态、版本、审查日期和变更触发器。

## 1. 文档对象与唯一事实来源

| 文档对象 | 解决的问题 | 主要 Owner | 真值来源 | 强制维护触发器 |
|---|---|---|---|---|
| Opportunity Brief / PRD | 用户问题、证据、目标、非目标与验收是什么？ | 产品 | 调研记录、行为/工单数据、批准决策 | 问题、用户、指标、范围或约束改变 |
| ADR | 为什么做出重要且难逆转的技术决策？ | 架构 owner | 版本化 Markdown；关联设计/代码/指标 | 关键架构/数据/安全/平台/选型决定或被推翻 |
| Context Map / 数据契约 | 谁拥有什么业务含义与权威数据？ | 架构、领域 owner | 图/Markdown + schema | 新 context、数据 owner、集成边界或一致性变化 |
| OpenAPI / event schema | 客户端/服务如何正确交互？ | API/event owner | 版本控制的规范与兼容性测试 | 输入输出、错误、权限、异步/弃用或版本变化 |
| 数据迁移计划 | 如何安全改变 schema/数据并验证/回退？ | 数据 owner | 迁移代码 + migration charter | DDL、回填、双写、CDC、分片、删除或恢复行为变化 |
| Runbook / Playbook | 当告警、故障或例行操作发生时如何安全行动？ | 服务/SRE owner | 可访问、演练过的操作文档 | 告警、架构、依赖、权限、发布或恢复路径变化 |
| 发布契约 | 谁在何时以何条件发布、停止、回退和复核？ | Release owner | CI/CD 配置 + release record | 服务、依赖、风险等级、SLO、回滚或灰度策略变化 |
| Postmortem / 学习记录 | 发生了什么、系统如何改进、谁跟进？ | Incident commander / owner | 事件状态文档 + 复盘 | P1/P2 或团队定义的学习阈值事件 |
| Reference / How-to / Tutorial / Explanation | 用户需要事实、操作、学习还是背景？ | 对应组件 owner | 文档站/仓库，按分类维护 | 公共行为、配置、用法、概念或常见任务变化 |

**规则。** 每项文档必须有：`owner`、`status`、`last_verified`、`review_trigger`、`links_to_evidence`。只要无法回答“谁负责、何时失效、由什么事实校验”，该文档就不是可维护资产。

## 2. 文档即代码工作流

Docs-as-code 意味着把文档与代码一样计划、变更、审查、预览、自动检查和发布；它不等于强行把所有协作文档都写成 Markdown。ADR、API 规范、runbook、迁移计划、架构图源文件和用户可见参考文档通常应进入与工作负载关联的版本控制；探索访谈原始记录或事故实时状态可在协作空间，但需要链接到版本化决策/学习记录。[1] [2]

```text
Issue / Opportunity / Incident
        │  变更影响评估（需要哪些文档？）
        ▼
Docs + Code + Spec + Tests 同一变更集
        │  作者自检、文档预览、链接/格式/schema/lint
        ▼
领域 + 消费者 + 运行/质量评审
        │  风险门禁、版本/弃用、发布/回滚文档
        ▼
Merge / Release / Publish
        │  使用数据、支持工单、事故/复盘、上游版本变化
        ▼
复审、更新、Supersede 或 Retire
```

## 3. 文档完成定义（Definition of Done）

| 变更类型 | 合并前最低文档证据 | 发布前最低文档证据 |
|---|---|---|
| 用户功能 | Opportunity/验收标准、用户流程、错误/恢复体验、分析事件 | 支持/操作说明、发布说明、已知限制和观测链接 |
| API / 事件 | 版本化 OpenAPI/schema、权限、错误、幂等、兼容/弃用、consumer review | contract test、文档发布、客户端迁移/回退说明 |
| 数据迁移 | migration charter、权威源、对账、回滚/不可逆点 | 备份/恢复、演练记录、监控、停止条件、清理/退役计划 |
| 运行/基础设施 | ADR（若显著）、配置说明、SLO/告警、容量/故障假设 | Runbook、dashboard、灰度/回滚、owner/on-call 交接 |
| 架构/框架选型 | ADR、备选方案、POC/证据、影响的 Context/API/data | 迁移与复审日期、培训/支持材料、废弃计划 |
| 重构 | 行为基线、切片、兼容/ACL、对账、回退窗口 | 切换记录、旧路径删除标准、事后性能/错误复核 |

## 4. 文档内容质量门禁

### 4.1 通用门禁

1. **可定位。** 标题、目的、受众、owner、状态、最后验证日期、关联服务/代码/工单可快速找到。
2. **可行动。** 操作文档包含前置条件、步骤、验证、失败/回退与升级路径；不得只写名词解释。
3. **可验证。** 事实链接到代码、规范、测试、指标、配置或权威来源；观点和未知项清晰标注。
4. **可演进。** ADR append-only；变化以新记录 supersede 旧记录；API/事件与迁移有兼容/弃用历史。
5. **可访问与安全。** 不含密钥、PII 或不当内部细节；读者权限、紧急访问与离线/替代位置适当。
6. **与读者匹配。** 使用 tutorial/how-to/reference/explanation 分类，避免把操作、参考和背景混在同一页面。[3]

### 4.2 自动与人工检查

| 检查 | 自动化优先 | 人工审查重点 |
|---|---|---|
| 链接、格式、拼写、术语 | CI lint、link checker、Markdown/schema 校验 | 读者是否能理解/完成任务、术语是否与领域一致 |
| API / event | OpenAPI/JSON Schema validation、breaking-change diff、contract tests | 业务语义、权限、错误、弃用、消费者迁移 |
| ADR | metadata 完整性、链接有效性、状态关系 | 是否真是重大决定、选项/理由/后果/置信度是否充分 |
| Runbook | 模板/owner/告警链接检查 | 步骤是否在安全环境演练、恢复/升级路径是否真实有效 |
| 发布/迁移 | 版本、变更集、CI、回滚字段检查 | 业务/数据正确性、停止条件、人类批准与不可逆点 |

## 5. ADR 维护协议

ADR 只记录影响系统结构、关键质量属性或难以逆转的决策；不将它写成泛化设计教程。每条记录保持短小、明确、事实化，包括问题/上下文、需求和约束、备选项、决定、理由、权衡、置信度、状态、后果、关联证据、owner 与复审触发。已接受 ADR 不回写改历史；新的决策以 `Supersedes`/`Superseded by` 链接保留演进历史。[4] [5]

```yaml
adr_metadata:
  id: ADR-0001
  title: ""
  status: proposed | accepted | superseded | deprecated
  date: ""
  owners: []
  decision_confidence: high | medium | low
  decision_drivers: []
  related_code_specs_and_metrics: []
  supersedes: []
  superseded_by: []
  review_trigger: ""
```

## 6. Runbook 与事件活文档协议

Runbook 要服务于真实操作，而非展示系统知识。它至少声明：适用告警/症状、影响/优先级判定、角色/权限、风险提示、诊断/缓解步骤、每步验证、禁止动作、升级/沟通、回滚/恢复、证据采集和事后更新。高风险步骤需要人工批准或双人复核。事件期间维护一个可协作的**事件状态文档**：当前影响、指挥/操作/沟通/计划角色、时间线、已尝试操作、待办、决策、客户沟通和交接；它应在事后保留并链接到复盘。[6]

## 7. 文档陈旧性管理

| 陈旧信号 | 系统动作 |
|---|---|
| API schema / IaC / 配置 / 代码变更 | CI 检查关联文档/规范是否同变更；缺失则阻止或要求豁免 |
| 上游版本或安全公告 | 建立 review issue；版本敏感卡/Runbook 标记为待验证 |
| 告警、事故、失败发布 | 检查 runbook/ADR/release 文档；复盘行动项包含文档更新 |
| 支持工单/开发者反馈 | 将读者失败场景转为 how-to、FAQ 或 reference 修订 |
| 定期复审到期 | owner 选择 verified、update、supersede 或 retire；不能静默过期 |

## References

[1]: https://about.gitlab.com/blog/five-fast-facts-about-docs-as-code-at-gitlab/
[2]: https://developers.google.com/style
[3]: https://diataxis.fr/start-here/
[4]: https://docs.cloud.google.com/architecture/architecture-decision-records
[5]: https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record
[6]: https://sre.google/sre-book/managing-incidents/

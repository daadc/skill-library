# 用户需求分析与产品发现知识卡

## KC-PD-001：需求不是功能列表，而是待验证的机会

**问题。** “用户想要导出/审批/看板”能否直接变成开发需求？

**原则。** 功能请求是线索而不是已验证需求。团队应确认用户、语境、目标、当前做法、痛点成本、替代方案、成功信号与约束；产品、设计和工程共同验证价值、可用性、可行性和商业/组织可行性。[1]

```yaml
opportunity_brief:
  target_user_segment_and_context: ""
  job_to_be_done_or_problem: ""
  current_workaround_and_cost: ""
  evidence_and_limitations: []
  desired_outcome: ""
  success_and_guardrail_metrics: []
  constraints: ["privacy", "security", "regulation", "deadline", "cost"]
  assumptions_to_test: []
  alternatives_including_do_nothing: []
  non_goals: []
```

**反模式。** 只有老板意见/竞品截图；把“做一个页面”当作用户结果；只研究问题不验证方案；只由产品写需求而不让工程早期判断可行性/运行风险。

---

## KC-PD-002：调研方法按问题和阶段选择

| 阶段/问题 | 合适方法 | 不应得出的结论 |
|---|---|---|
| 方向/机会未知 | 现场观察、任务访谈、日志/工单分析、日记研究、概念测试 | 单次问卷足以证明高价值需求 |
| 交互/信息架构 | 原型可用性测试、卡片分类、树测试、设计参与 | 用户说“喜欢”即可上线 |
| 规模/优先级 | 漏斗/行为分析、问卷、A/B 或分组实验 | 相关性必然等于方案因果效果 |
| 上线后效果 | 任务成功、完成时间、错误、留存、反馈、支持工单 | 单个北极星指标改善代表无负面影响 |

NN/g 将研究按行为/态度、定性/定量和使用语境区分：行为观察常有助于理解真实使用；定性常回答为何/怎么改，定量常回答多少/多大。探索、形成和评估阶段应使用不同的证据组合。[2]

---

## KC-PD-003：把调研结论转成可开发、可验收的用例

**流程。**

1. 将已验证目标拆成用户任务和结果，而非 UI 部件。
2. 与设计共同定义主路径、失败路径、空态、权限、可访问性、文案和恢复体验。
3. 与工程共同定义数据、状态机、领域规则、SLO、依赖、风险、成本和不可逆点。
4. 用场景化验收标准和可观测指标表达完成，而不是“接口已提供”。
5. 明确哪些是假设，安排原型/POC/灰度来验证；失败时允许删减/改向。

```yaml
acceptance_contract:
  user_task: ""
  preconditions_and_permissions: []
  happy_path: []
  edge_and_failure_paths: []
  outcome_and_guardrail_metrics: []
  accessibility_and_localization: []
  data_retention_and_privacy: []
  operational_expectations: []
  analytics_events_and_definitions: []
```

## References

[1]: https://www.svpg.com/discovery-problem-vs-solution/
[2]: https://www.nngroup.com/articles/which-ux-research-methods/

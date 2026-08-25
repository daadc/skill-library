# 开发文档模板

这些模板是受约束研发框架的最小产物，不要求每个任务全部填写。编排器根据任务阶段、风险等级和文档生命周期选择；涉及 R2/R3 风险的任务必须由人类 owner 审查和批准。

| 模板 | 使用时机 | Owner | 关联知识 |
|---|---|---|---|
| `adr.md` | 结构、质量属性或难逆决定 | 架构 owner | `knowledge/documentation-governance/`、`domain-driven-design/` |
| `interaction-contract.md` | HTTP/API、事件、BFF、异步任务、前后端状态变化 | API/event owner | `technology-selection/`、`domain-driven-design/` |
| `migration-charter.md` | Schema、回填、双写、CDC、数据归属或遗留替换 | 数据/架构 owner | `refactoring-evolution/` |
| `runbook.md` | 告警、例行运维、故障/恢复、安全操作 | 服务/SRE owner | `documentation-governance/`、`resilience-engineering/` |
| `release-contract.md` | 上线、灰度、停止、回滚、观察和复核 | release owner | `development-lifecycle/` |
| `routing-record.yaml` | 每次动态 Agent/Skill 编排 | 编排 owner | `constrained-agentic-development-framework.md` |

模板中的 `unknown` 是合法值；不得为了通过模板而虚构调研、容量、测试或批准结果。

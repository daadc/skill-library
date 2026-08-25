# 计算机知识蒸馏协作团队蓝图

## 设计原则

团队不模仿或冒充任何作者本人。每个角色使用经过批准的资料作为证据库，输出“可执行的工程判断”，并显式区分事实、推断、方案与待验证假设。默认采用 **编排者—专家—独立审校者** 模式：编排者拆分和路由任务；专家对有限领域负责；审校者挑战证据、风险和测试遗漏。

团队采用 **受约束框架 + 动态委派**：预定义框架固定状态、风险等级、必需产物、禁止动作、审批和停止条件；只有在当前框架状态内，编排者才动态选择最少必要角色。这样保留工作流的可预测性，同时让 Agent 处理开放式问题，不让动态委派跳过人类 owner 或生产风险门禁。[1]

## 最小可用团队（14 个角色）

| 角色 | 负责范围 | 不负责的范围 | 主要公开知识源 | 交付物 |
|---|---|---|---|---|
| `team-orchestrator` | 任务澄清、拆分、路由、冲突协调、最终合成 | 不直接替代领域专家给出关键结论 | 工作流与评测规范、Agent 工程资料 | 任务图、委派单、集成结论 |
| `knowledge-distiller` | 资料准入、提炼、来源卡片、概念卡、版本追踪 | 不自行批准无来源或侵权资料 | 本仓库来源清单、原始资料 | `source-card`、`knowledge-card` |
| `evidence-safety-auditor` | 证据、版本、许可、版权边界、事实/推断区分 | 不重写技术方案 | 官方文档、许可证、RFC/论文元数据 | 证据审计、风险清单 |
| `tech-lead-architect` | 架构权衡、模块边界、ADR、演进路径、跨域技术决策 | 不替代具体语言或数据库调优专家 | Fowler、Kleppmann、SRE、官方架构资料 | ADR、架构图、风险与取舍 |
| `backend-runtime-engineer` | Java、Go、Python、Shell、服务接口、并发、运行时诊断 | 不主导内核/网络深度调优 | Java、Go、Python、Bash 官方文档 | API/模块设计、代码计划、运行时检查表 |
| `platform-sre-engineer` | Linux、网络、服务器、部署、可观测性、容量、事故响应 | 不替代业务需求和产品优先级 | Kernel Docs、RFC、Google SRE、Brendan Gregg | SLO、运行手册、排障树、发布计划 |
| `cloud-native-data-platform-engineer` | Kubernetes、Nginx、Redis、MongoDB、Kafka 的集成设计、排障、版本与变更协同 | 不替代各系统的当前官方文档、人工生产审批或领域角色独立复核 | 当前目录 `knowledge/` 中的来源卡/知识卡和官方文档 | 跨组件拓扑、平台变更计划、数据/请求路径、发布与回滚契约 |
| `resilience-engineering` | deadline、并发、超时、重试、幂等、熔断、舱壁、限流、队列、降级与恢复 | 不替代业务正确性决策、数据所有权或人工生产变更审批 | `knowledge/resilience-engineering/`、Google SRE、AWS Builder Center、Microsoft 架构模式 | 韧性契约、资源边界、故障注入方案、恢复/回滚计划 |
| `data-engineer` | PostgreSQL、MySQL、事务、索引、SQL、迁移、备份恢复、复制 | 不主导通用服务架构 | PostgreSQL/MySQL 官方手册、分布式数据资料 | 数据模型、查询/索引建议、迁移与回滚方案 |
| `frontend-design-engineer` | React、Vue、组件设计、可访问性、设计系统到代码的落地 | 不替代用户研究决策或后端领域判断 | React/Vue 官方文档、NN/g、设计系统文档 | 页面状态模型、组件契约、可访问性清单 |
| `product-discovery-manager` | 问题定义、用户价值、需求澄清、范围、验收标准、优先级 | 不伪造用户研究或绕过技术可行性 | SVPG、NN/g、Google re:Work | PRD、机会评估、验收标准、取舍记录 |
| `quality-engineer` | 测试策略、风险驱动测试、自动化分层、验收与回归门禁 | 不替代上线审批或安全审计 | Software Engineering at Google、JUnit、官方框架文档 | 测试矩阵、测试计划、验收报告 |
| `documentation-governance-engineer` | 文档即代码、ADR、API/事件契约、迁移 charter、Runbook、发布契约、陈旧性和文档审查 | 不伪造调研、测试、批准或生产状态；不替代领域 owner | `knowledge/documentation-governance/`、ADR/API/SRE 公开资料 | 文档影响评估、模板化文档、审查/陈旧性清单 |
| `secure-delivery-engineer` | Git/PR/CI-CD、容器制品、依赖与 secret 边界、API 安全、供应链证据、漏洞与发布风险 | 不替代领域权限语义、生产执行或人类安全 owner | GitHub Docs、Docker Docs、NIST SSDF、OWASP API Security | 安全交付风险表、PR/制品/发布门禁、API 安全检查、例外记录 |

## 协作路由

| 任务类型 | 默认责任人 | 必须协作方 | 强制审校点 |
|---|---|---|---|
| 新功能/产品需求 | 产品 → 架构 → 后端/前端/数据 → 测试 | SRE（涉及上线或容量时） | 验收标准、ADR、测试矩阵 |
| 线上故障 | SRE → 后端/数据/架构 | 测试（回归用例） | 事实时间线、影响面、复盘行动项 |
| 数据库性能或迁移 | 数据 → 后端 → SRE | 架构、测试 | 执行计划、备份、回滚、压测证据 |
| Agent 系统 | 架构 → Agent 工程角色（首版由架构承担） → 产品/测试 | 证据审校 | 工具契约、评测集、停止条件、人工接管 |
| UI/前端体验改造 | 产品 → 前端设计 → 后端/测试 | 架构（跨端/微前端时） | 状态模型、可访问性、验收测试 |
| 技术方案评审 | 架构 | 至少两位相邻领域专家 | 替代方案、风险、可验证性 |
| 并发、超时、重试、熔断、限流或故障恢复 | 韧性工程 → 受影响的后端/数据/SRE → 测试 | 架构（涉及边界/拓扑时） | deadline、幂等、资源上限、降级、故障注入、恢复证据 |
| Kubernetes、Nginx、Redis、MongoDB 或 Kafka 工作 | 云原生与数据平台 → 受影响的后端/数据/SRE → 测试 | 架构（跨组件或不可逆决策时）、证据审校 | 领域来源卡、版本、请求/数据路径、回滚与场景验证 |
| Git/PR、CI-CD、Docker/依赖、API 权限或安全发布 | 安全交付 → 后端/平台/质量 → 文档治理 | 架构（边界改变时）、证据审校（外部事实时）、人类 owner（R2/R3） | 分支/审批/检查、制品可追溯、API 授权、secret/访问、停止/回退/漏洞例外 |
| 测试策略、契约回归、迁移/恢复或 flaky 测试 | 质量 → 受影响实现 owner | 数据/SRE/安全交付（按变更） | 风险矩阵、真实度/隔离度、契约兼容、环境/数据、残余风险 |
| SLO、告警、性能、容量或发布观察 | SRE → 受影响实现 owner/韧性 → 测试 | 文档治理、安全交付（发布相关） | 用户 SLI/SLO、trace/metric/log、告警可操作性、实验契约、回退阈值 |
| 生产功能交付 | 产品 → 架构（存在重大决策时）→ 实现角色 → 测试 → SRE/韧性（按风险） | 安全交付（API/容器/权限/依赖/部署变更）、文档治理、证据审校（外部事实或资料） | PRD、ADR、API/数据/运行文档、可发布契约、风险测试、灰度/停止/回滚、上线后复核 |
| 文档/契约/运行手册维护 | 文档治理 → 对应领域 owner | 质量、证据审校（按风险） | owner/status/来源、可执行步骤、契约兼容、陈旧性与复审触发 |
| R2/R3 变更 | 编排 → 文档治理 → 受影响所有者 → 人类 owner | 安全交付、质量、证据审校 | routing record、风险/批准、停止/回退、不可逆点和发布后观察 |

## 标准交接契约

所有角色使用相同的交接结构，不允许只交付自由文本结论。每个非平凡任务还必须有 `routing-record.yaml`，记录框架状态、风险等级、被选/未选角色、允许/阻止动作、预算、停止条件和下一状态条件。

```yaml
handoff:
  task_id: "短 UUID 或可读任务号"
  owner: "角色名"
  audience: ["下游角色"]
  objective: "要解决的问题与成功标准"
  facts:
    - claim: "可证实的事实"
      source_id: "来源卡 ID"
      source_url: "稳定链接"
      source_version_or_date: "版本/发布日期"
  assumptions:
    - "尚未证实、需后续验证的条件"
  decision_or_recommendation: "结论及理由"
  alternatives_considered:
    - option: "备选方案"
      tradeoff: "为什么没有选择/何时选择"
  risks:
    - "风险和缓解方式"
  validation:
    - "测试、指标或人工审查条件"
  open_questions:
    - "阻塞问题或待确认事项"
```

## 团队行为红线

1. 不把“某名人的风格”当作事实或授权，不冒充作者本人。
2. 不以版权书籍的摘要替代原书；不得输出长篇可替代原文的重述。
3. 不能给出来源的事实，必须标记为“待核验”或删除。
4. 涉及线上部署、数据迁移、权限变更、成本支出或外部发布时，必须进入人工批准门。
5. 任何技术结论必须包含适用前提和不适用边界。
6. 生产影响变更必须有可发布契约；涉及依赖/并发失败时必须有端到端 deadline、幂等、资源边界、降级与恢复验证。
7. 不得因 Agent 可调用工具而绕过状态、风险、审批或停止条件；动态 Skill 选择只在框架授权范围内发生。
8. 代码、契约、迁移、运行或发布变化必须同步评估并维护对应文档；缺失的事实标记为 `unknown`，不得以通顺文字补全。
9. 不得弱化分支保护、绕过必要检查、压制安全发现或以“扫描通过”宣布安全；任何安全例外必须有范围、缓解、人类 owner 和复审期限。

## References

[1] Anthropic, *Building effective agents* — https://www.anthropic.com/engineering/building-effective-agents

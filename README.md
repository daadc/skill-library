# Computer Knowledge Distillation Team

这是一个面向计算机、软件工程、产品、设计和管理知识的**可审计协作 Skill 团队**。它将权威公开资料和用户合法拥有的私有资料，转换为带来源、版本、适用前提、取舍、验证方法和审校记录的知识卡；它不用于复制名人或重建受版权保护书籍。

## 已部署的团队

**14 个 Skill** 同步到 Hermes 用户目录：

```text
~/.hermes/skills/computer-team/
```

| Skill | 职责 |
|---|---|
| `/computer-team-orchestrator` | 任务拆解、受约束角色路由、冲突协调和最终合成 |
| `/technical-knowledge-distiller` | 把许可资料蒸馏为来源卡和知识卡 |
| `/evidence-safety-auditor` | 来源、版本、版权、风险和事实边界审校 |
| `/tech-lead-architect` | 架构权衡、ADR、系统演进和跨域评审 |
| `/backend-runtime-engineer` | Java、Go、Python、Shell、API、并发与服务实现 |
| `/platform-sre-engineer` | Linux、网络、SRE、可观测性、性能和事故响应 |
| `/cloud-native-data-platform-engineer` | Kubernetes、Nginx、Redis、MongoDB、Kafka 及跨组件平台工程 |
| `/resilience-engineering` | 并发预算、超时、重试、熔断、舱壁、限流、降级、级联故障与恢复设计 |
| `/data-engineer` | PostgreSQL、MySQL、SQL、迁移、索引和恢复 |
| `/frontend-design-engineer` | React、Vue、组件、UI 状态、可访问性与设计系统 |
| `/product-discovery-manager` | 问题发现、需求、范围、优先级和验收标准 |
| `/quality-engineer` | 风险测试、回归、发布门禁和 Agent 评测 |
| `/documentation-governance-engineer` | Docs-as-Code、ADR/API/迁移/Runbook/发布契约与陈旧性治理 |
| `/secure-delivery-engineer` | Git/PR/CI-CD、容器制品、API 安全、供应链证据与安全发布审查 |

建议新开 Hermes 会话后，从：

```text
/computer-team-orchestrator
```

开始描述任务。编排 Skill 会在风险等级、停止条件和人类 owner 约束内，只路由最少必要的专家，并要求使用结构化交接。

## 核心文件

| 文件 | 用途 |
|---|---|
| `SOURCE_CANDIDATES.md` | 已核验的权威公开资料、书籍候选、链接与使用边界 |
| `TEAM_BLUEPRINT.md` | 14 个角色的责任边界、协作路由和交接契约 |
| `ROADMAP_COVERAGE_GAP_ANALYSIS.md` | roadmap.sh 作为能力地图时的合规边界、覆盖差距与补全优先级 |
| `knowledge/` | 当前目录下所有已蒸馏的领域知识、来源卡、知识卡与场景卡 |
| `DISTILLATION_WORKFLOW.md` | 资料准入、来源卡、知识卡、场景卡、评测卡和质量门禁 |
| `TEAM_TEST_PLAN.md` | 功能、迁移、事故和版权边界的测试场景 |
| `skills/*/SKILL.md` | 可独立安装或迭代的 Team Skill 源码 |

## 第一轮 P0 补全：安全交付、测试、可观测性与性能

本轮不把 roadmap.sh 当作内容资料库。其站点只作为高层能力导航；根据其条款，不复制、抓取、存储、再分发其具体材料，也不把该材料用于模型训练或批量蒸馏。[1] 新知识均由独立核验的官方/标准/原始资料写成原创、可验证的知识卡。

| 已补齐领域 | 目录 | 核心决策能力 | 默认协作路由 |
|---|---|---|---|
| 安全交付 | `knowledge/secure-delivery/` | 受保护分支、PR/CI、CODEOWNER、容器制品、SSDF、API 授权与发布证据 | 安全交付 → 后端/平台/质量/文档治理 → 人类 owner（按风险） |
| 测试工程 | `knowledge/testing-engineering/` | 风险测试、真实度/隔离度、API/event 契约、迁移与回归选择 | 质量 → 后端/数据/前端/平台 → 文档治理（按变更） |
| 可观测性与性能 | `knowledge/observability-performance/` | OTel 信号、SLI/SLO、告警、性能实验、容量与发布观察 | SRE → 实现 owner/质量/韧性 → 文档治理（按风险） |

每个包均含 `sources.yaml`、`knowledge-cards.md` 和 `scenarios.md`，将前提、风险、验证和多角色协作场景与来源关联。它们补的是高优先级能力缺口，**并不表示已完成 roadmap.sh 的全部路径**。

## 后续优先级

| 优先级 | 下一批能力 | 采取方式 |
|---|---|---|
| P1 | Terraform/IaC、实际云平台、PostgreSQL/MySQL 深化、System Design 与网络 | 先确认语言、云厂商和项目约束，再从官方资料建立窄主题知识包 |
| P2 | 具体前端构建/发布、移动端、特定消息/数据栈的扩展 | 仅在真实需求出现且现有领域包无法覆盖时补充 |

## 第一次使用：先蒸馏一个窄主题

不要从“整本书”或“整个领域”开始。选一个有明确决策边界的问题，例如：

```text
使用 /technical-knowledge-distiller，基于 PostgreSQL 官方文档，
蒸馏“为多租户订单查询新增索引前需要收集和验证哪些证据”。
请创建来源卡和知识卡；标明版本、适用条件、候选方案、风险和验证步骤。
```

然后交给：

```text
/evidence-safety-auditor 审查这张知识卡的来源、版本、版权和未证实推断。
```

对于 API 改动和容器发布，追加 `/secure-delivery-engineer`；对于风险测试和发布观察，追加 `/quality-engineer` 与 `/platform-sre-engineer`。所有 R2/R3 变更仍必须有明确人类 owner 批准。

## 资料准入原则

- **可直接使用**：官方文档、RFC、开放论文、明确开放许可的原作者文章。
- **可私有蒸馏**：你合法拥有的书籍、课程、公司文档。不得推送公开仓库或生成可替代原文的长篇内容。
- **不能使用**：盗版扫描件、付费墙绕过、无出处转载、无法确认版本的材料。
- **不做作者分身**：将名人的公开观点写为有出处的工程原则；不得命令 Skill 冒充在世作者。

所有新蒸馏知识统一写入当前项目的 `knowledge/` 目录，不写入 Hermes 安装目录；Hermes 只保存可执行的 Skill 定义。

## References

[1]: https://roadmap.sh/terms

# 知识库

此目录是本项目所有**已蒸馏知识**的唯一落点。每个领域以来源卡和知识卡组织，而不是保存无法审计的长摘要。所有内容均应能回答：来源是什么、适用于什么版本和场景、有哪些前提和风险、如何验证。

## 目录结构

| 目录 | 内容 | 当前负责角色 |
|---|---|---|
| `shared/` | 通用证据格式、跨领域决策模式、场景与评测模板 | `technical-knowledge-distiller`、`evidence-safety-auditor` |
| `kubernetes/` | 集群、工作负载、发布、安全、版本升级 | `platform-sre-engineer`、`tech-lead-architect` |
| `nginx/` | 反向代理、负载均衡、缓存、限流、TLS 与流量治理 | `platform-sre-engineer`、`backend-runtime-engineer` |
| `redis/` | 缓存、持久化、复制、哨兵、集群、容量与恢复 | `data-engineer`、`platform-sre-engineer` |
| `mongodb/` | 文档建模、索引、事务、复制集、分片、备份恢复 | `data-engineer`、`backend-runtime-engineer` |
| `kafka/` | 主题/分区、生产消费、消费组、投递语义、保留、复制与演进 | `backend-runtime-engineer`、`data-engineer`、`platform-sre-engineer` |
| `development-lifecycle/` | 需求到运行复盘的交付流程、评审、测试、发布与工程效能 | `computer-team-orchestrator`、`quality-engineer` |
| `resilience-engineering/` | deadline、超时、重试、熔断、舱壁、限流、队列、降级与恢复 | `resilience-engineering`、`platform-sre-engineer` |
| `architecture-patterns/` | 模块化单体、服务演进、cell 隔离与成熟架构案例 | `tech-lead-architect` |
| `product-discovery/` | 调研、机会假设、用户任务、验收、体验与实验 | `product-discovery-manager`、`frontend-design-engineer` |
| `domain-driven-design/` | DDD、统一语言、子域、bounded context、契约与架构风格组合 | `tech-lead-architect`、`backend-runtime-engineer` |
| `technology-selection/` | Go Web、GORM/SQL、API/BFF、前后端状态与选型 ADR | `backend-runtime-engineer`、`data-engineer`、`frontend-design-engineer` |
| `design-patterns/` | 代码/模块/分布式模式的触发条件、组合与反模式 | `tech-lead-architect`、`backend-runtime-engineer` |
| `refactoring-evolution/` | 代码/模块/数据重构、Strangler、ACL、迁移与遗留退役 | `tech-lead-architect`、`quality-engineer`、`data-engineer` |
| `documentation-governance/` | 文档即代码、ADR、API/事件契约、迁移、Runbook、发布、陈旧性和文档审查 | `documentation-governance-engineer`、各领域 owner |
| `secure-delivery/` | Git/PR、分支保护、CI/CD、容器制品、SSDF、API 安全与发布证据 | `secure-delivery-engineer`、`backend-runtime-engineer`、`platform-sre-engineer`、`quality-engineer` |
| `testing-engineering/` | 风险测试、真实度/隔离度、契约、迁移/恢复、回归选择与质量证据 | `quality-engineer`、受影响实现 owner |
| `observability-performance/` | OTel 遥测、SLI/SLO、告警、性能实验、容量与发布观察 | `platform-sre-engineer`、`resilience-engineering`、`quality-engineer` |

每个领域至少包含：

```text
sources.yaml         # 版本化来源卡
knowledge-cards.md   # 问题驱动的知识卡
scenarios.md         # 协作/评测场景
```

## 发布规则

> **知识卡不是教材摘要，也不是作者人格模型。** 它是为真实工程决策服务的原创、可验证的操作性说明。

1. 只把 A/B 类公开资料，或用户合法拥有且仅在本地私用的 C 类材料加入来源卡。对 C 类材料先按根目录 `DISTILLY_INTEGRATION.md` 使用 `/distilly` 建立私有候选知识，再经来源和领域审校后写入本目录。
2. 对 Kubernetes、数据库、消息系统、框架、API、安全、制品和可观测性相关规则，必须标明软件版本或文档访问日期。
3. 所有配置建议必须附带适用前提、失败模式和至少一种验证方法；不要把默认值当成生产推荐值。
4. 涉及生产变更、数据迁移、权限、成本、集群升级或外部发布的建议，必须通过人工批准门。
5. 非平凡任务必须遵循 `shared/constrained-agentic-development-framework.md`：先标记框架状态、风险等级、人类 owner、路由记录与停止条件，再由 Agent 动态选择最少必要的 Skill。
6. 对 API、Git/CI/CD、容器、依赖和基础设施变更，必须联合查阅 `secure-delivery/`、`testing-engineering/` 与 `observability-performance/` 的相关卡，并维护交互契约、发布契约、Runbook 和回退证据。
7. 官方文档升版、事故复盘、性能评测失败、安全公告或供应链事件出现时，应修订而不是静默覆盖旧卡。

## 使用顺序

1. 对公开资料，先调用 `/technical-knowledge-distiller` 创建或更新来源卡与知识卡；对合法私有书籍、ADR、复盘或评审记录，先用 `/distilly` 再进入技术蒸馏与审校。
2. 让对应领域 Skill 审查实施前提和技术细节。涉及 API、CI/CD、容器或安全发布时，加入 `/secure-delivery-engineer`。
3. 调用 `/evidence-safety-auditor` 核验来源、版本、版权与未证实假设。
4. 对开发/运行文档使用 `/documentation-governance-engineer`，并按 `../templates/development-docs/` 选择 ADR、交互契约、迁移、Runbook、发布或路由记录模板。
5. 用领域 `scenarios.md` 中的场景进行团队演练，由 `/quality-engineer` 检查测试风险与证据，由 `/platform-sre-engineer` 复核发布观察与事故可操作性。

根目录中的 `DISTILLATION_WORKFLOW.md`、`TEAM_BLUEPRINT.md` 与 `SOURCE_CANDIDATES.md` 仍是全局规范和候选资料索引；本目录保存领域级的实际蒸馏成果。

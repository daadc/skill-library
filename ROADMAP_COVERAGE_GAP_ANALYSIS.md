# roadmap.sh 能力地图覆盖缺口分析

> **使用边界。** roadmap.sh 仅作为主题导航。其网站条款限制复制、存储、抓取或将内容用于 AI 训练，因此本分析只记录高层主题名称与链接，不复制其路线图节点或文本。任何新增知识必须从官方文档、标准、原作者资料或合法用户自有资料独立核验。[1] [2]

## 现有覆盖

当前 `knowledge/` 已有 15 个领域包，强项集中于复杂系统交付：需求/产品发现、DDD、架构/模式、Go/GORM/API、韧性、研发生命周期、文档治理、重构，以及 Kubernetes、Nginx、Redis、MongoDB、Kafka。团队已有 13 个专业 Skill，能够处理后端、数据、SRE、平台、前端、产品、质量、证据与文档治理。

这与 roadmap.sh 的 Backend、Go、React/Vue、Linux、Kubernetes、Redis、MongoDB、AI Agents、Product Manager、Engineering Manager、Software Architect、QA、Technical Writer 等主题有实质交集。[1]

## 高优先级缺口

| 优先级 | roadmap.sh 对应主题 | 当前状态 | 为什么优先 | 首轮蒸馏目标 |
|---|---|---|---|---|
| P0 | Git and GitHub、Code Review | 无独立知识包 | 所有协作、变更可追溯、分支/PR/回滚和 AI 变更审计的基础 | Git 工作流、变更集、PR 审查、CODEOWNERS、分支保护、AI 变更门禁 |
| P0 | DevOps、Docker、CI/CD | 仅有研发生命周期的抽象规则 | Kubernetes 前必须掌握镜像、构建、测试、制品、部署与供应链基础 | Container 基线、不可变制品、CI/CD gate、环境/配置、SBOM/签名概念 |
| P0 | DevSecOps、API Security、Cyber Security | 仅分散提及权限/安全 | 当前 API、K8s、Agent 和自动化体系缺少结构化威胁建模与安全验收 | 威胁建模、身份/授权、输入/API 安全、秘密、依赖/供应链、日志/审计 |
| P0 | QA、Automated Regression Testing | 有质量角色但无独立知识包 | 复杂系统质量不能仅靠测试策略描述，需要可执行分层和变更风险证据 | 测试金字塔/测试奖杯、契约/集成/E2E、回归选择、测试数据、质量信号 |
| P0 | Observability、Backend Performance | 在 SRE/韧性中零散出现 | 没有可观测性就无法验证 AI、发布、重构和容量结论 | logs/metrics/traces、SLI/SLO、告警、profiling、性能实验与容量证据 |
| P1 | Terraform、AWS、Cloudflare | 无独立知识包 | 需要先确定云与 IaC 是否是实际部署目标；避免泛化云厂商知识 | IaC state/plan/review、policy、drift；在选定云后补充服务实践 |
| P1 | System Design、Network Engineer | 有架构/韧性但无完整入门/面试式能力包 | 可以由现有知识组合，但仍缺容量估算、缓存/队列/分片/网络基础的系统化索引 | 设计评审卡、估算、网络/协议、容量、权衡和故障模型 |
| P1 | SQL、PostgreSQL DBA、Elasticsearch | 数据角色存在但 Postgres/MySQL 仅在描述中 | 要支撑实际数据设计、性能和恢复，需单独建立来源和场景 | SQL、事务/锁/索引/执行计划、备份恢复、检索系统选型 |
| P2 | Java、Python、Shell、TypeScript、Node.js | Skill 描述覆盖，但缺各语言知识包 | 应按照团队实际技术栈和项目触发；当前不宜平均铺开 | 语言版本、并发/工具链、测试、打包、性能与安全 |
| P2 | Data Structures & Algorithms、LeetCode | 无独立包 | 对工程面试和基础训练有价值，但不是复杂产品交付首要短板 | 基础算法/复杂度/工程适用边界与练习体系 |
| P2 | MLOps、AI Red Teaming、Product Design、Design System | Agent/前端/产品有初步能力 | 需要在出现模型部署、设计系统或红队需求时按项目深化 | 模型评测/发布/监控、Agent 安全、设计 tokens/组件治理 |

## 首轮补全顺序

1. **Secure Delivery Foundation**：Git/代码审查、Docker/CI-CD、供应链与 API/应用安全。
2. **Quality and Observability**：测试工程、测试数据/回归、logs/metrics/traces、性能/容量与发布观察。
3. **Infrastructure as Code and Data Operations**：在实际目标云与代码仓库确定后，补 Terraform/云/IaC 和 PostgreSQL/MySQL 深度运维。

这一顺序与当前体系的价值链一致：先让每个变更可追溯、可审查、可构建、可安全发布；再让结果可验证、可观察；最后根据真实部署平台深化工具链。不要以“知识库主题数量”替代工程能力。

## 不建议立即照搬的主题

不应在未确认项目语言/云厂商/产品需要前，完整复制 roadmap.sh 的 90 多条路径。例如 AWS、Cloudflare、Android、iOS、WordPress、Blockchain、游戏、Power BI 或每种语言框架，只应在真实项目需求出现后以官方资料建立领域包。

## References

[1]: [roadmap.sh — Developer Roadmaps](https://roadmap.sh/)
[2]: [roadmap.sh — Terms of Use](https://roadmap.sh/terms)

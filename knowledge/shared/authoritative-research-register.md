# 权威研究资料登记：研发流程与韧性工程

本文件保存本轮检索已核验的外部来源、版本信息和可支持的结论范围。后续知识卡必须链接到此处或领域级 `sources.yaml`，不能把作者/机构声望当成没有出处的事实。

| ID | 来源 | 访问日期/版本 | 可支撑的知识范围 |
|---|---|---|---|
| `src-google-code-review` | Google Engineering Practices, [Code Review Introduction](https://google.github.io/eng-practices/review/) | 2026-08-25 | 代码审查维度：设计、功能、复杂度、测试、命名、文档；选择合适评审者 |
| `src-google-code-health` | Google Engineering Practices, [The Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html) | 2026-08-25 | 评审以持续改进整体代码健康为目标，平衡前进速度与质量，不追求无关紧要的完美 |
| `src-google-release-engineering` | Google SRE, [Release Engineering](https://sre.google/sre-book/release-engineering/) | 2026-08-25 | 可重复/自动化发布、密封构建、持续测试、版本/配置管理、金丝雀与回滚、发布审计 |
| `src-dora-metrics-2026` | DORA, [Software Delivery Performance Metrics](https://dora.dev/guides/dora-metrics/) | 2026-01-05 页面更新；2026-08-25 访问 | 五项交付指标、以应用/服务为单位持续改进、避免指标竞赛和跨上下文比较 |
| `src-google-cascading-failures` | Google SRE, [Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/) | 2026-08-25 | 过载、资源耗尽、队列管理、负载丢弃、优雅降级、重试放大、容量规划与故障演练 |
| `src-aws-timeout-retry-jitter-2026` | AWS Builder Center, [Timeouts, retries, and backoff with jitter](https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter) | 2026-06-15 页面更新；2026-08-25 访问 | 远程调用超时、幂等重试、封顶指数退避、抖动、单层重试、令牌桶限重试与流量放大风险 |
| `src-ms-circuit-breaker-2025` | Microsoft Azure Architecture Center, [Circuit Breaker pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker) | 2025-03-21 页面日期；2026-08-25 访问 | Closed/Open/Half-Open 状态、快速失败、恢复探测、异常分类、观测与手动干预 |
| `src-ms-bulkhead-2026` | Microsoft Azure Architecture Center, [Bulkhead pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead) | 2026-03-19 页面更新；2026-08-25 访问 | 连接池/线程池/队列/实例/租户隔离、故障遏制、QoS 与资源隔舱权衡 |

## 关键事实摘录（原创转述）

Google 工程实践把代码审查视为保持代码健康的正常开发工作流，并要求检查设计、功能、复杂度、测试和文档等维度。Google SRE 将发布工程定义为从源代码、构建、测试、打包到部署的一体化、可重复过程；其核心是自动化、版本化、审计和按风险选择发布策略。DORA 当前将交付表现分为吞吐和不稳定性两组，共五项指标，并强调按单个应用/服务在时间维度上改进，而非把指标用于团队间竞赛。[1] [2] [3] [4]

Google SRE 将过载视为级联故障的常见触发因素，建议用容量测试、早拒绝、负载丢弃、优雅降级和小队列来保护系统。AWS 指出超时、重试、退避和抖动必须一起设计：带副作用调用只有具备幂等语义时才可安全重试，多层独立重试会以乘数放大下游负载。Microsoft 的熔断与舱壁模式分别用于快速阻止可能持续失败的调用和隔离依赖资源，二者均需要明确定义阈值、恢复、观测和不适用场景。[5] [6] [7] [8]

## References

[1]: https://google.github.io/eng-practices/review/
[2]: https://google.github.io/eng-practices/review/reviewer/standard.html
[3]: https://sre.google/sre-book/release-engineering/
[4]: https://dora.dev/guides/dora-metrics/
[5]: https://sre.google/sre-book/addressing-cascading-failures/
[6]: https://builder.aws.com/content/3EumjoZascWd1oZiEgL8ORlv3qE/timeouts-retries-and-backoff-with-jitter
[7]: https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker
[8]: https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead

## 成熟架构案例登记

| ID | 来源 | 访问日期/版本 | 可迁移模式与边界 |
|---|---|---|---|
| `src-shopify-modular-monolith-2019` | Shopify Engineering, [Deconstructing the Monolith](https://shopify.engineering/deconstructing-monolith-designing-software-maximizes-developer-productivity) | 2019-02-21 发布；2026-08-25 访问 | 保留单一部署单元但用业务域边界、公共接口、数据归属和自动化违规检测降低耦合；不把微服务当作默认解法 |
| `src-aws-cell-architecture-2023` | AWS Well-Architected, [Reducing the Scope of Impact with Cell-Based Architecture](https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/reducing-scope-of-impact-with-cell-based-architecture.html) | 2023-09-20 发布；2026-08-25 访问 | 以单元隔离有限范围的客户/租户/工作负载故障，换取可预测性和可测性；适用于高韧性场景而非所有小型系统 |
| `src-netflix-video-microservices-2024` | Netflix TechBlog, [Rebuilding Netflix Video Processing Pipeline with Microservices](https://netflixtechblog.com/rebuilding-netflix-video-processing-pipeline-with-microservices-4e5e6310e359) | 2024-01-10 发布；2026-08-25 访问 | 当既有系统的耦合、共同发布和长发布周期已被业务/测量证据证实为瓶颈时，以清晰业务功能边界、专用编排与渐进迁移拆分服务 |

Shopify 的案例说明：模块化单体是“单一应用内严格执行领域边界”的演进选项。其重点不是目录重命名，而是按真实业务概念组织、为组件定义公共接口和数据所有权，并通过工具在 CI 中识别跨边界违规。AWS 的单元化架构把隔离边界下沉到工作负载层，以缩小故障域、提高可预测性和可测试性；它应由实际的关键性、规模、租户隔离和运维能力驱动。Netflix 的案例显示，微服务拆分应由既有架构的具体限制驱动，例如共同部署、耦合和过长发布周期，并以业务功能边界和渐进流量切换来控制迁移风险。[9] [10] [11]

[9]: https://shopify.engineering/deconstructing-monolith-designing-software-maximizes-developer-productivity
[10]: https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/reducing-scope-of-impact-with-cell-based-architecture.html
[11]: https://netflixtechblog.com/rebuilding-netflix-video-processing-pipeline-with-microservices-4e5e6310e359

## 复杂系统建模与演进资料登记

| ID | 来源 | 访问日期/版本 | 可支撑的知识范围 |
|---|---|---|---|
| `src-fowler-bounded-context-2014` | Martin Fowler, [Bounded Context](https://martinfowler.com/bliki/BoundedContext.html) | 2014-01-15 发布；2026-08-25 访问 | 大型领域中的多模型、统一语言、显式上下文关系和 context map |
| `src-fowler-ddd-2020` | Martin Fowler, [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html) | 2020-04-22 发布；2026-08-25 访问 | 复杂领域、统一语言、实体/值对象/服务/聚合及战略设计；概念不绑定特定语言 |
| `src-ms-domain-analysis-2026` | Microsoft Azure Architecture Center, [Use domain analysis to model microservices](https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis) | 2026-02-25 页面更新；2026-08-25 访问 | 从业务能力到子域、bounded context、上下文映射、服务边界和 Anti-Corruption Layer 的迭代过程 |
| `src-aws-hexagonal-overview` | AWS Prescriptive Guidance, [Hexagonal architectures overview](https://docs.aws.amazon.com/prescriptive-guidance/latest/hexagonal-architectures/overview.html) | 2026-08-25 访问 | 领域优先、ports/adapters、依赖倒置、与分层架构的取舍及可测试性 |

DDD 不是“上 Entity/VO/Aggregate 类名”的框架。它首先要求开发者和领域专家共同形成可演进的统一语言，并把复杂领域拆成明确关系的 bounded contexts；同一词语可以在不同上下文有不同但内部一致的模型。服务或模块边界应以业务能力、高内聚、低耦合和可独立演进为依据，而非按 controller/service/repository 等技术横层切割。[12] [13] [14]

六边形（ports-and-adapters）架构把领域/应用核心与 HTTP、数据库、消息、第三方 API 等外部细节隔离，接口由核心定义，外部实现端口。它适用于复杂规则、依赖可替换、需高测试性或逐步重构的系统；简单 CRUD 不应为形式而过度分层。[15]

[12]: https://martinfowler.com/bliki/BoundedContext.html
[13]: https://martinfowler.com/bliki/DomainDrivenDesign.html
[14]: https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis
[15]: https://docs.aws.amazon.com/prescriptive-guidance/latest/hexagonal-architectures/overview.html

## 重构与需求调研资料登记

| ID | 来源 | 访问日期/版本 | 可支撑的知识范围 |
|---|---|---|---|
| `src-fowler-strangler-fig-2024` | Martin Fowler, [Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html) | 2024-08-22 发布；2026-08-25 访问 | 明确现代化目标、寻找可替换 seam、小步交付与组织改进；避免一次性重写 |
| `src-ms-strangler-fig-2026` | Microsoft Azure Architecture Center, [Strangler Fig pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/strangler-fig) | 2026-06-02 页面更新；2026-08-25 访问 | façade 路由、旧新系统共存、增量切流、ACL、数据迁移/验证/最终退役边界 |
| `src-svpg-discovery-2020` | SVPG, [Discovery — Problem vs. Solution](https://www.svpg.com/discovery-problem-vs-solution/) | 2020-09-04 发布；2026-08-25 访问 | 需求发现中产品、设计和工程共同验证价值、可用性、可行性和商业可行性 |
| `src-nng-ux-methods-2026` | Nielsen Norman Group, [When to Use Which User-Experience Research Methods](https://www.nngroup.com/articles/which-ux-research-methods/) | 2026-07-15 审核；2026-08-25 访问 | 调研方法按行为/态度、定性/定量和使用语境选择；探索、形成、评估阶段的证据策略 |

重构不能从“更换技术栈”开始。先明确业务结果、可量化痛点和需要保留/废弃的行为；识别可切分 seam，以 façade/适配器、增量路由、数据一致性验证和可回退切换让新旧共存。过渡架构有临时成本，但通常可把风险和收益分段可见化；只有在旧功能已验证迁移且最终依赖被移除后，才应删除遗留对象。[16] [17]

用户需求不能只由产品角色“收集”后扔给工程实现。SVPG 主张产品、设计和工程共同形成价值、可用性、可行性和商业可行性判断；NN/g 指出研究方法应匹配问题类型和阶段，行为观察更适合理解实际使用，定性回答“为什么/怎样改”，定量回答“多少/多大”，探索/形成/评估阶段的研究目标不同。[18] [19]

[16]: https://martinfowler.com/bliki/StranglerFigApplication.html
[17]: https://learn.microsoft.com/en-us/azure/architecture/patterns/strangler-fig
[18]: https://www.svpg.com/discovery-problem-vs-solution/
[19]: https://www.nngroup.com/articles/which-ux-research-methods/

## Go Web、数据访问与前后端契约资料登记

| ID | 来源 | 访问日期/版本 | 可支撑的知识范围 |
|---|---|---|---|
| `src-go-net-http-1-27` | Go standard library, [net/http](https://pkg.go.dev/net/http) | Go 1.27.0 页面；2026-08-25 访问 | 标准 HTTP client/server、并发安全的 client/transport 复用、明确 Server 超时、context、优雅关闭、HTTP/2 |
| `src-go-database-access` | Go, [Accessing relational databases](https://go.dev/doc/database/) | 2026-08-25 访问 | `database/sql`、事务、context 取消、连接池、ORM/NoSQL 选择的官方概览 |
| `src-gorm-guides-2026` | GORM, [Guides](https://gorm.io/docs/index.html) | 2026-08-04 页面更新；2026-08-25 访问 | 关联、预加载、事务、context、批处理、SQL Builder、约束、迁移、Generics API、日志与插件 |
| `src-openapi-3-2-2025` | OpenAPI Initiative, [OpenAPI Specification v3.2.0](https://spec.openapis.org/oas/v3.2.0.html) | 2025-09-19 发布；2026-08-25 访问 | 语言无关 HTTP API 描述、客户端/服务端生成、文档、测试、版本与弃用语义 |

Go 的 `net/http` 是稳定、功能完整的标准库 HTTP 基线，适合需要少依赖、可控中间件和团队理解其上下文/超时/优雅关闭行为的服务；其 Client/Transport 可被多个 goroutine 并发安全复用，生产服务仍应显式定义 Server 超时、请求大小、context 取消、错误映射和观测。框架的选择应由路由/绑定/验证/中间件/生态速度、团队熟悉度和可观测性需求决定，而非性能口碑。[20]

Go 的 `database/sql` 提供连接池、事务和 context 取消的低层基线。GORM 在需要快速 CRUD、关联、预加载、事务、迁移和约定优先开发时有效，但复杂查询、批量操作、性能关键路径和跨数据库迁移必须审查实际 SQL、索引、事务边界和执行计划；ORM 不替代数据模型和迁移治理。[21] [22]

OpenAPI 是 HTTP API 的语言无关描述，适合作为前后端之间可版本化、可生成、可测试的契约。它不能替代产品语义、权限、幂等、异步事件、SLO 和用户体验的协作说明；这些必须补充到交互契约中。[23]

[20]: https://pkg.go.dev/net/http
[21]: https://go.dev/doc/database/
[22]: https://gorm.io/docs/index.html
[23]: https://spec.openapis.org/oas/v3.2.0.html

## 开发文档维护与决策记录资料登记

| ID | 来源 | 访问日期/版本 | 可支撑的知识范围 |
|---|---|---|---|
| `src-google-dev-doc-style-2026` | Google, [Developer Documentation Style Guide](https://developers.google.com/style) | 2026-04-27 更新；2026-08-25 访问 | 面向技术读者的清晰一致文档、项目级规范优先与一致性原则 |
| `src-google-cloud-adr-2024` | Google Cloud, [Architecture decision records overview](https://docs.cloud.google.com/architecture/architecture-decision-records) | 2024-08-16 审核；2026-08-25 访问 | ADR 的适用场景、内容、靠近代码/可访问存储、历史价值与演进 |
| `src-ms-adr-2026` | Microsoft Azure Well-Architected, [Maintain an ADR](https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record) | 2026-04-13 更新；2026-08-25 访问 | ADR 的 append-only 历史、状态、备选项、上下文/理由/后果和共享文档仓库 |
| `src-openapi-3-2-2025` | OpenAPI Initiative, [OpenAPI Specification v3.2.0](https://spec.openapis.org/oas/v3.2.0.html) | 2025-09-19 发布；2026-08-25 访问 | 机器可读 HTTP API 描述、文档/代码生成/测试、版本与弃用语义 |

开发文档应优先满足项目读者的清晰与一致，而不是机械遵循外部写作规则。项目级术语、模板、责任人、版本和引用标准应优先，外部风格指南作为补充。[24]

ADR 只记录影响结构、关键质量属性或难以逆转的决策；它应包含问题/上下文、备选项、决定、理由、权衡、状态和后果。将 ADR 与工作负载文档和版本控制放在可访问位置；已接受 ADR 应 append-only，变更决策以新记录 supersede 并链接旧记录，以保存演进历史。[25] [26]

OpenAPI 定义了语言无关的 HTTP 接口描述，能够支持文档、客户端/服务端生成和测试。API 文档应和 API 代码/契约一起被版本控制与验证，并处理弃用/兼容性；OpenAPI 之外的业务状态、错误恢复、权限、幂等、异步语义和 SLO 仍须另行维护。[27]

[24]: https://developers.google.com/style
[25]: https://docs.cloud.google.com/architecture/architecture-decision-records
[26]: https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record
[27]: https://spec.openapis.org/oas/v3.2.0.html

## Docs-as-Code、运行文档与文档分类资料登记

| ID | 来源 | 访问日期/版本 | 可支撑的知识范围 |
|---|---|---|---|
| `src-gitlab-docs-as-code-2022` | GitLab, [Five fast facts about docs as code](https://about.gitlab.com/blog/five-fast-facts-about-docs-as-code-at-gitlab/) | 2022-10-12 发布；2026-08-25 访问 | 文档与代码同仓、计划/评审/预览/CI 检查/发布、文档纳入 Definition of Done |
| `src-google-sre-managing-incidents` | Google SRE, [Managing Incidents](https://sre.google/sre-book/managing-incidents/) | 2026-08-25 访问 | 事件状态文档、明确角色、实时交接、预先演练和保留记录供复盘 |
| `src-diataxis-start-here` | Daniele Procida, [Diátaxis](https://diataxis.fr/start-here/) | 2026-08-25 访问 | Tutorial、How-to、Reference、Explanation 四类文档的不同用户需求与维护边界 |

Docs-as-code 的关键不是 Markdown 本身，而是让文档进入与代码相同的计划、版本控制、评审、预览、检查和发布链路。GitLab 的实践将功能文档纳入开发 Definition of Done，并在提交/合并请求中运行链接、拼写/语法等检查。[28]

运行文档要在事件发生前定义角色、命令/沟通通道、实时状态记录和明确交接；事故中非协调的“自由操作”会恶化局势。活文档可以凌乱但必须可用，重要状态放在顶部，并保留给复盘和改进。[29]

文档维护需区分用户目标：tutorial 用于学习、how-to 解决现实任务、reference 提供准确技术事实、explanation 提供背景和理由。将四类内容混在一个页面会导致读者难以执行或难以理解；分类是维护信息架构的工具而不是格式教条。[30]

[28]: https://about.gitlab.com/blog/five-fast-facts-about-docs-as-code-at-gitlab/
[29]: https://sre.google/sre-book/managing-incidents/
[30]: https://diataxis.fr/start-here/

## roadmap.sh 能力地图与使用边界登记

| ID | 来源 | 访问日期/版本 | 可支撑的用途 | 不可支撑的用途 |
|---|---|---|---|---|
| `src-roadmap-sh-directory-2026` | [roadmap.sh Developer Roadmaps](https://roadmap.sh/) / [roadmap directory](https://roadmap.sh/roadmaps) | 2026-08-25 访问 | 角色与技能主题的能力地图、学习路径和缺口识别 | 技术事实真值、生产配置、对其内容的复制/改写性蒸馏 |
| `src-roadmap-sh-terms-2025` | [roadmap.sh Terms of Use](https://roadmap.sh/terms) | 2025-03-27 更新；2026-08-25 访问 | 内容使用与自动化访问边界 | 不授权复制、存储、传播或使用内容训练 AI |
| `src-developer-roadmap-github-2026` | [nilbuild/developer-roadmap](https://github.com/nilbuild/developer-roadmap) | 2026-08-25 访问 | 开源仓库的路径目录、公开贡献结构和许可入口定位 | 未核对仓库许可前复制具体路线图/节点内容 |

roadmap.sh 将自己定位为社区创建的开发者学习路径、指南和资源目录，覆盖角色型、技能型、最佳实践和项目练习等主题。[31] [32] 因此本项目只将其作为**覆盖盘点与学习顺序的导航索引**，不将其作为生产技术结论的唯一或优先真值来源。

其网站条款声明网站内容仅可用于个人、非商业使用，并禁止通过手工或自动化流程监视、复制或抓取材料（包括用于训练 AI）。因此不得复制、缓存或批量蒸馏网站路线图内容；应只保存本次人工核对出的高层主题名称和链接，并为任何纳入知识库的技术结论回到官方文档、标准、原作者材料或合法用户自有资料进行独立核验。[33]

[31]: https://roadmap.sh/
[32]: https://roadmap.sh/roadmaps
[33]: https://roadmap.sh/terms

## 安全交付基础资料登记

| ID | 来源 | 访问日期/版本 | 可支撑的知识范围 |
|---|---|---|---|
| `src-github-protected-branches-2026` | GitHub Docs, [About protected branches](https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches) | 2026-08-25 访问 | PR 审查、状态检查、CODEOWNERS、最新提交审查、分支推送/删除/绕过约束、merge queue |
| `src-docker-build-best-practices-2026` | Docker Docs, [Building best practices](https://docs.docker.com/build/building/best-practices/) | 2026-08-25 访问 | 多阶段构建、最小/可信基础镜像、`.dockerignore`、不可变镜像、构建测试、镜像 digest/更新权衡 |
| `src-owasp-api-security-2023` | OWASP, [API Security Top 10](https://owasp.org/API-Security/) | 2023 版；2026-08-25 访问 | API 对象/函数/属性授权、认证、资源消耗、业务流、SSRF、配置、库存、上游 API 消费风险 |
| `src-nist-ssdf-1-1-2026` | NIST, [Secure Software Development Framework](https://csrc.nist.gov/projects/ssdf) | SP 800-218 v1.1；页面 2026-04-13 更新；2026-08-25 访问 | 组织准备、软件保护、安全软件生产、漏洞响应；风险化和可定制的 DevSecOps 改进框架 |

GitHub 的保护分支允许以 PR 审批、状态检查、会话解决、签名、线性历史、merge queue、部署成功、推送/删除限制等设置约束关键分支。具体启用项应按仓库风险和吞吐量选择，而不是将所有开关一律设为必需；重要的是将“谁能合并、何种证据通过、最新 diff 是否被独立审查”固化为可审计规则。[34]

Docker 建议使用多阶段构建，选择可信且尽量小的基础镜像，使用 `.dockerignore` 控制上下文，尽量产生可替换的短生命周期容器，并在 CI 中构建和测试镜像。固定 image digest 增强可再现性和审计，但需要配合受控更新机制以避免错过安全修复。[35]

OWASP API Security Top 10 是威胁/审查清单，不是自动通过的合规证明。API 契约的权限、对象/属性/功能级授权、认证、资源限制、敏感业务流、SSRF、配置、库存和上游依赖消费应映射到可测试的需求和运行信号。[36]

NIST SSDF 将安全实践组织为 PO、PS、PW、RV 四组，并强调按风险、成本、可行性、适用性与可自动化程度定制，而不是把框架当作机械清单。它也将安全需求、风险与设计决定、组件溯源和漏洞响应纳入软件生命周期。[37]

[34]: https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches
[35]: https://docs.docker.com/build/building/best-practices/
[36]: https://owasp.org/API-Security/
[37]: https://csrc.nist.gov/projects/ssdf

## 测试工程与可观测性资料登记

| ID | 来源 | 访问日期/版本 | 可支撑的知识范围 |
|---|---|---|---|
| `src-swe-book-larger-testing` | Software Engineering at Google, [Larger Testing](https://abseil.io/resources/swe-book/html/ch14.html) | 2026-08-25 访问 | 小/大测试的范围与取舍、fidelity/hermeticity、配置/负载/真实依赖缺口、测试所有权与组合爆炸 |
| `src-opentelemetry-signals-2026` | OpenTelemetry, [Signals](https://opentelemetry.io/docs/concepts/signals/) | 2026-03-10 更新；2026-08-25 访问 | traces、metrics、logs、baggage 与 profiles 的遥测语义 |
| `src-google-sre-slo` | Google SRE, [Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) | 2026-08-25 访问 | SLI/SLO/SLA、错误预算、用户结果驱动目标、延迟分位数和服务类型差异 |
| `src-google-sre-monitoring` | Google SRE, [Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) | 2026-08-25 访问 | black-box/white-box、golden signals、低噪可行动告警、简单可理解的监控系统 |

小测试提供快速、可靠、可扩展的局部反馈；更大测试用于覆盖配置、真实依赖、负载、未预期输入与涌现行为，但其成本、脆弱性、所有权和组合复杂度更高。应根据风险使用“最小足够测试”，并维护契约/配置/真实集成的覆盖，而不是只追求端到端测试数量。[38]

OpenTelemetry 的通用遥测信号包括 traces（请求路径）、metrics（运行时测量）、logs（事件记录）和 baggage（跨信号上下文）；profiles 记录代码级资源使用。信号应该服务于用户/业务/运行问题，不能只因技术可采集而无限制增加。[39]

SLI 是经定义的服务质量度量，SLO 是对应目标，SLA 是带有明确后果的协议。目标应从用户真正关心的结果倒推，定义测量范围和有效条件，以尽量少的指标覆盖行为；错误预算可将可靠性状态纳入发布与改进的权衡。[40]

Google SRE 将延迟、流量、错误和饱和度视为用户服务系统的四个基础监控信号；对人类 pager，规则应简单、低噪、可行动并对应真实/迫近的用户影响。black-box 更接近用户症状，white-box 用于内部原因与提前信号，两者不可互相替代。[41]

[38]: https://abseil.io/resources/swe-book/html/ch14.html
[39]: https://opentelemetry.io/docs/concepts/signals/
[40]: https://sre.google/sre-book/service-level-objectives/
[41]: https://sre.google/sre-book/monitoring-distributed-systems/

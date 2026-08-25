# 权威资料与书籍候选清单

> 采集原则：将公开网页、标准、开放获取论文和明确开放许可的资料作为可直接引用的证据源；对受版权保护书籍，仅将公开目录、作者公开文章或用户自有的合法副本用于私有摘要，不建立可替代原书的复述库。

| 领域 | 作者/机构与资料 | 可用范围 | 蒸馏目标 |
|---|---|---|---|
| 软件架构 | Martin Fowler，《Software Architecture Guide》与相关架构文章 | 公开网页；按页面条款引用与转述 | 演进式架构、架构决策、微服务边界、遗留系统迁移 |
| 数据与分布式系统 | Martin Kleppmann，个人网站文章、公开论文和演讲；《Designing Data-Intensive Applications》为付费书 | 网站内容采用 CC BY 3.0（页面另有标注除外）；书籍只限用户自有副本私用 | 一致性、复制、流处理、CRDT、数据系统权衡 |
| SRE / 安全可靠性 | Google SRE Books：*Site Reliability Engineering*、*The SRE Workbook*、*Building Secure & Reliable Systems* | 官方在线阅读 | SLO、错误预算、容量、变更、事故处理、安全与可靠性结合 |
| 可观测性与性能 | OpenTelemetry 官方概念文档；Google SRE 的 SLO 与分布式系统监控章节 | 官方公开资料；版本/访问日期须记录 | traces、metrics、logs、profiles、SLI/SLO、可操作告警、性能/容量实验 |
| 软件工程与测试 | *Software Engineering at Google* 在线章节；Google Testing Blog；JUnit 用户指南；OpenAPI Specification | 在线公开；具体页面按其许可/条款引用 | 测试分层、测试大小、真实度/隔离度、契约、回归与可维护性 |
| 安全交付 / DevSecOps | GitHub 分支保护文档、Docker 构建最佳实践、NIST SSDF、OWASP API Security Top 10 | 官方/标准/社区安全基线；实施前复核当前版本 | Git/PR 门禁、CI/CD、容器制品、供应链证据、风险化安全开发、API 授权与资源边界 |
| Java | Oracle JDK 文档、Java SE 规范、dev.java 教程；Joshua Bloch《Effective Java》为付费书 | 官方参考与教程公开；付费书仅限合法自有副本 | Java 语言、JVM、并发、GC、模块、安全、诊断 |
| Go | Go 项目官方文档、语言规范、Effective Go、官方演讲 | 官方公开文档 | 并发、内存模型、模块、数据库访问、性能与竞态检测 |
| Python | Python 官方文档、PEP、Guido van Rossum 的公开文章 | PSF 文档许可；按页面许可引用 | 语言语义、标准库、打包、类型、并发与工程规范 |
| Shell | GNU Bash Reference Manual；POSIX Shell and Utilities（规范链接待补） | GNU 官方公开手册；按许可与引用边界使用 | Shell 解析、引用、扩展、退出码、管道、安全脚本 |
| Linux 内核/服务器 | Linux Kernel Documentation、Linux man-pages、Brendan Gregg 的 Linux 性能资料 | 内核官方文档；Gregg 页面图示 CC BY-SA，文章按页面条款 | 内核接口、网络、追踪、perf、eBPF、USE Method、故障定位 |
| 网络 | IETF RFC（优先 TCP/HTTP/TLS/DNS 等现行 RFC）、Linux 网络文档 | RFC 公开发布；需保留 RFC 编号/版本 | 协议状态机、超时与重试、可观测性、网络故障排查 |
| PostgreSQL | PostgreSQL 官方当前与历史文档 | 官方在线与 PDF 手册 | SQL、事务、索引、MVCC、查询优化、备份恢复、复制 |
| MySQL | MySQL 官方 Reference Manual 和高可用/复制指南 | Oracle 官方在线文档 | InnoDB、事务、索引、执行计划、复制、高可用、运维 |
| React | React 官方文档 | 官方公开文档 | 组件、状态、数据流、可访问性、性能、测试接口 |
| Vue | Vue 3 官方 Guide | 官方公开文档 | 响应式、组件、Composition API、SFC、工程结构 |
| UI / 设计系统 | Nielsen Norman Group 的 UX 和设计系统文章；Material Design / Carbon 等官方系统（待第二轮核验） | 公开文章；遵守页面条款 | 用户研究、可用性、信息架构、可访问性、设计系统协作 |
| 产品 | Marty Cagan / SVPG 公开文章；《Inspired》《Empowered》为付费书 | SVPG 公开文章；书籍仅限合法自有副本 | 产品发现、价值/可用性/可行性、产品团队协作、路线图 |
| 管理 | Google re:Work；*The Manager’s Path*、*High Output Management*、*Accelerate* 等付费书仅作合法私有补充 | re:Work 公开；书籍按授权 | 目标、反馈、团队设计、招聘、绩效、工程效能 |
| AI Agent 工程 | Anthropic《Building Effective Agents》、Lilian Weng《LLM Powered Autonomous Agents》、标准/框架官方文档 | 公开文章；对工具版本和实作需二次核验 | 工作流与 Agent 边界、路由、编排、评测、工具接口、记忆、可靠性 |
| Kubernetes | Kubernetes 官方架构、工作负载、版本偏差策略；Brendan Burns、Joe Beda、Kelsey Hightower 等《Kubernetes: Up and Running》为付费书 | 官方文档公开；书籍仅限合法自有副本 | 集群架构、工作负载、发布、升级、服务网络、资源和安全边界 |
| Nginx | nginx.org 官方模块/负载均衡文档、F5 NGINX 官方管理指南 | 官方公开文档；区分 OSS 与 Plus 功能 | 反向代理、上游、缓存、TLS、限流、流量治理、故障排查 |
| Redis | Redis 官方持久化、复制、Sentinel、Cluster 和安全文档；Josiah L. Carlson《Redis in Action》为付费书 | 官方文档公开；书籍仅限合法自有副本 | 缓存一致性、RDB/AOF、复制、故障转移、恢复与容量 |
| MongoDB | MongoDB Manual 的复制、分片、事务、索引和安全文档；《MongoDB: The Definitive Guide》为付费书 | 官方文档公开；书籍仅限合法自有副本 | 文档建模、复制集、读写关注点、分片、迁移与恢复 |
| Kafka | Apache Kafka 官方文档和设计/运维章节；Gwen Shapira、Todd Palino、Rajini Sivaram《Kafka: The Definitive Guide》为付费书 | Apache 文档采用 Apache License 2.0；书籍仅限合法自有副本 | 事件契约、主题分区、生产消费、投递语义、保留、复制与回放 |

## 建议优先蒸馏的开放资料包

1. **Google SRE Books**：作为可靠性、运维、事故响应和安全设计的主线资料。
2. **Software Engineering at Google**：作为开发流程、代码审查、测试策略与可维护性的主线资料。
3. **Martin Fowler 的 Architecture Guide**：作为架构/演进/交付协作的主线资料。
4. **Linux Kernel Docs + Brendan Gregg**：作为 Linux、服务器、性能排障的主线资料。
5. **PostgreSQL / MySQL 官方文档**：作为数据库实现与运维的主线资料。
6. **Go、Python、Java、React、Vue 的官方文档**：作为语言与框架真值源；每月复核版本。
7. **Anthropic、Lilian Weng 的 Agent 文章**：作为 Agent 系统设计的基线，再以当前框架官方文档补齐版本差异。
8. **SVPG + NN/g + Google re:Work**：作为产品、体验、团队协作的实践资料。
9. **GitHub、Docker、NIST、OWASP、OpenTelemetry、Google SRE 与 OpenAPI 资料**：作为安全交付、测试工程、可观测性与性能的 P0 基线；领域级成果存入 `knowledge/secure-delivery/`、`knowledge/testing-engineering/` 与 `knowledge/observability-performance/`。
10. **Kubernetes、Nginx、Redis、MongoDB、Kafka 官方资料**：作为云原生与数据平台的首批可直接蒸馏资料包；领域级来源卡和知识卡已存入 `knowledge/`。

## 参考链接

1. Martin Fowler Architecture Guide — https://martinfowler.com/architecture/
2. Martin Kleppmann — https://martin.kleppmann.com/
3. Google SRE Books — https://sre.google/books/
4. Software Engineering at Google — https://abseil.io/resources/swe-book/html/
5. Linux Kernel Documentation — https://docs.kernel.org/
6. Brendan Gregg Linux Performance — https://www.brendangregg.com/linuxperf.html
7. PostgreSQL Documentation — https://www.postgresql.org/docs/
8. MySQL Documentation — https://dev.mysql.com/doc/
9. Go Documentation — https://go.dev/doc/
10. Go Specification — https://go.dev/ref/spec
11. Python Documentation — https://docs.python.org/3/
12. Guido van Rossum — https://gvanrossum.github.io/
13. Java Documentation — https://docs.oracle.com/en/java/javase/26/
14. Learn Java — https://dev.java/learn/
15. GNU Bash Manual — https://www.gnu.org/software/bash/manual/bash.html
16. React Documentation — https://react.dev/learn
17. Vue Guide — https://vuejs.org/guide/introduction.html
18. JUnit User Guide — https://docs.junit.org/current/user-guide/
19. Anthropic, Building Effective Agents — https://www.anthropic.com/engineering/building-effective-agents
20. Lilian Weng, LLM Powered Autonomous Agents — https://lilianweng.github.io/posts/2023-06-23-agent/
21. Nielsen Norman Group, Design Systems 101 — https://www.nngroup.com/articles/design-systems-101/
22. SVPG Product Management Articles — https://www.svpg.com/insights/product-management-articles/
23. Google re:Work — https://rework.withgoogle.com/
24. Kubernetes Documentation — https://kubernetes.io/docs/home/
25. Kubernetes Version Skew Policy — https://kubernetes.io/releases/version-skew-policy/
26. Nginx Documentation — https://nginx.org/en/docs/
27. F5 NGINX Security Controls — https://docs.nginx.com/nginx/admin-guide/security-controls/controlling-access-proxied-http/
28. Redis Documentation — https://redis.io/docs/latest/
29. MongoDB Manual — https://www.mongodb.com/docs/manual/
30. Apache Kafka Documentation — https://kafka.apache.org/documentation/
31. GitHub Docs, About protected branches — https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches
32. Docker Docs, Building best practices — https://docs.docker.com/build/building/best-practices/
33. NIST Secure Software Development Framework — https://csrc.nist.gov/projects/ssdf
34. OWASP API Security — https://owasp.org/API-Security/
35. OpenTelemetry, Signals — https://opentelemetry.io/docs/concepts/signals/
36. Google SRE, Service Level Objectives — https://sre.google/sre-book/service-level-objectives/
37. Google SRE, Monitoring Distributed Systems — https://sre.google/sre-book/monitoring-distributed-systems/
38. OpenAPI Specification — https://spec.openapis.org/oas/v3.2.0.html

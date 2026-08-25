# roadmap.sh 能力地图：P0 补全交付报告

**完成日期：** 2026-08-25  
**范围：** 以 roadmap.sh 作为高层能力导航，独立核验并补充安全交付、测试工程、可观测性与性能能力。

## 合规边界

roadmap.sh 只用于识别高层能力缺口，不作为知识内容来源。本轮没有复制、抓取、保存或蒸馏其正文，也没有将其材料用于训练。三个新领域包均基于独立核验的 GitHub、Docker、NIST、OWASP、OpenTelemetry、Google SRE、Software Engineering at Google 和 OpenAPI 原始/官方资料写成原创卡片。[1]

## 本轮成果

| 能力包 | 交付内容 | 支持的关键决策 |
|---|---|---|
| `knowledge/secure-delivery/` | 来源卡、4 张知识卡、3 个协作场景 | 受保护分支和 PR、CI/CD、容器制品、供应链追溯、SSDF、API 授权、安全发布与漏洞例外 |
| `knowledge/testing-engineering/` | 来源卡、5 张知识卡、3 个协作场景 | 风险化分层测试、真实度与隔离度、契约、迁移/恢复、回归选择、flaky 测试与质量证据 |
| `knowledge/observability-performance/` | 来源卡、5 张知识卡、3 个协作场景 | OTel 信号、用户 SLI/SLO、可操作告警、性能实验、容量与发布后观察 |

每个领域均包含 `sources.yaml`、`knowledge-cards.md` 与 `scenarios.md`。场景覆盖了带 API 改动和容器发布的 Go 服务、事件/队列一致性、生产告警与发布回归、容量压测和回退证据。

## 团队与路由更新

| 更新 | 结果 |
|---|---|
| 新增角色 | `secure-delivery-engineer`，专门审查 Git/PR、CI/CD、容器、API 安全、供应链和安全敏感发布；不取代权限领域 owner 或人类安全 owner |
| 团队规模 | 项目与 Hermes 运行时目录均为 **14 个 Skill** |
| 编排规则 | `computer-team-orchestrator` 新增安全交付、测试工程与 SLO/性能固定路由，并规定 R2/R3 安全变更进入人类 owner 门禁 |
| 角色协作 | `quality-engineer` 接入契约、CI/制品和发布观察规则；`platform-sre-engineer` 接入 OTel、告警、性能实验和安全发布证据 |
| 项目索引 | 已更新根 `README.md`、`knowledge/README.md`、`TEAM_BLUEPRINT.md` 和 `SOURCE_CANDIDATES.md` |

## 验证记录

| 项目 | 结果 |
|---|---|
| 新知识包结构 | 3 个领域包各含 3 个非空必需文件 |
| 来源治理 | 每个 `sources.yaml` 均含 `source_id`、版本/访问日期和 `review_due` |
| 内容边界 | 新知识包中未出现 roadmap.sh 内容引用 |
| Skill 校验 | `secure-delivery-engineer`、`computer-team-orchestrator`、`quality-engineer`、`platform-sre-engineer` 均通过 `quick_validate.py` |
| Hermes 发现 | 14 个 `SKILL.md` 被发现，新增安全交付角色已同步 |

## 后续优先级

本轮**不宣称完成所有 roadmap.sh 路径**。下一批建议按实际项目语言、云厂商和交付约束收敛后再蒸馏：首先是 Terraform/IaC、具体云平台和 PostgreSQL/MySQL 深化；随后是 System Design 与网络。不要在没有真实技术栈或部署约束时一次性铺开所有云产品和工具。

## References

[1]: https://roadmap.sh/terms

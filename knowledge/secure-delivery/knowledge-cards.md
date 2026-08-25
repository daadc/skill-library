# 安全交付知识卡

## KC-SD-001：把关键分支当作受控变更入口

**问题。** AI 和多人协作提高提交速度后，如何确保进入主干的变更可追溯、可复审、可验证而不把小团队拖入过度流程？

**规则。** 对关键分支启用与风险匹配的保护：通过 PR 合并、要求状态检查、解决审查讨论、由 code owner 审核高风险路径、必要时要求最新 diff 的独立批准、限制推送/删除和绕过。对高吞吐主干可考虑 merge queue，在最新基线组合上重新执行必要检查。[1]

| 风险 | 合并最小门禁 | 额外门禁 |
|---|---|---|
| 文档/低风险局部逻辑 | 通过 CI、至少一个独立 review | 变更影响的文档更新 |
| API/共享模块/配置 | CI、受影响 owner review、契约/兼容性测试 | 最新 diff 再批准或 stale approval 失效 |
| 身份/权限、迁移、IaC、部署 | CI、CODEOWNER、质量与安全 review | 人类 owner、发布契约、停止/回退与观察 |

**不应机械开启。** 保护规则不等于质量；重复或不可信 status check、只看形式的 review、无法紧急恢复的过度限制都可能制造假安全。每项规则必须有 owner、目的和定期复审。

---

## KC-SD-002：容器制品必须可重建、最小化且可追溯

Docker 的多阶段构建可将构建/测试环境与运行环境分离；可信且尽量小的基础镜像、`.dockerignore`、不安装无关依赖、短生命周期容器和 CI 中构建/测试，有助于降低最终镜像复杂度和攻击面。[2]

**制品契约。** 每次候选发布至少记录源码 commit、Dockerfile/lockfile、基础镜像 digest/标签、构建参数、测试/扫描结果、生成时间、制品 digest、签名/证明（若采用）、部署环境和回退版本。

**digest 的权衡。** Pin 到 digest 可获得可重现性和审计轨迹；但它不会自动吸收上游安全更新，需要受控的检查与升级 PR。不要把“使用 latest”或“固定不更新”当作安全策略。[2]

**验证。** 在干净环境可从记录重建或定位相同制品；运行用户/端口/挂载/secret/最小权限被检查；镜像与部署配置与 release contract 对齐。

---

## KC-SD-003：API 安全是领域授权和资源边界的可测试契约

OWASP API Security Top 10 将对象、属性和功能级授权，认证，资源消耗，敏感业务流，SSRF，安全配置，API 库存与上游 API 消费等列为常见风险类别。[3]

| API 契约层 | 必须回答的问题 | 典型验证 |
|---|---|---|
| 身份与租户 | 调用者是谁？可访问哪个 tenant/组织？ | 认证缺失/过期/跨租户测试 |
| 对象/属性 | 谁可读/写哪一个对象和字段？ | IDOR/BOLA、过度暴露/批量赋值测试 |
| 功能与业务流 | 谁能执行何种动作、频率和顺序？ | BFLA、配额/限流、重复/跳步/并发测试 |
| 输入与外部调用 | 哪些 URL/命令/模板/文件被处理？ | SSRF、解析、allow-list、出站网络测试 |
| 演进与库存 | 哪些版本、端点、消费者仍在使用？ | schema diff、弃用/扫描、日志和入口盘点 |

**边界。** 身份认证不能替代对象/属性/功能授权；HTTP 2xx 不能证明业务操作安全；限流不能替代对资源、队列、成本和依赖的 end-to-end 预算。

---

## KC-SD-004：DevSecOps 采用风险化证据，不采用“安全清单幻觉”

NIST SSDF 将实践组织为 Prepare the Organization、Protect the Software、Produce Well-Secured Software 与 Respond to Vulnerabilities，并明确建议按风险、成本、可行性、适用性和自动化能力定制，而非照抄为单一检查表。[4]

**在本团队中的映射。**

| SSDF 方向 | 交付证据 |
|---|---|
| Prepare | 安全/隐私需求、威胁模型、owner/培训、最小权限开发环境 |
| Protect | 仓库/分支/secret/制品/组件溯源与访问控制 |
| Produce | 安全设计、代码/依赖/配置检查、API/权限测试、修复证据 |
| Respond | 漏洞接收/分级/修复/发布、客户影响、复盘和防复发更新 |

**AI 特别规则。** AI 只能建议安全变更、生成测试/文档和在隔离环境验证；它不能把扫描“绿色”宣布为无风险，不能在无人工 owner 批准下修改生产权限、secret、网络、依赖或部署。

## References

[1]: https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches
[2]: https://docs.docker.com/build/building/best-practices/
[3]: https://owasp.org/API-Security/
[4]: https://csrc.nist.gov/projects/ssdf

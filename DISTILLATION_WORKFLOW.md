# 技术知识蒸馏、审校与演进流程

## 关键决策

**不要把 Distilly 用于“复制名人”。** Distilly 适合将可授权的个人或团队工作经验沉淀为 source-grounded Profile；本项目对书籍、标准和公开技术资料采用“证据卡—知识卡—场景卡—评测卡”流程。这样可以保留出处、避免错误人格化、降低版权风险，并让多个角色围绕可验证产物协作。

## 资料分级与准入

| 级别 | 资料类型 | 可否直接纳入知识库 | 使用规则 |
|---|---|---:|---|
| A | RFC、标准、官方文档、明确开放许可的原作者文章/论文 | 可以 | 保存元数据、链接、版本和必要短引述；产出原创的规则与示例 |
| B | 作者官网文章、演讲、博客、公开目录 | 可以，但需人工确认访问/使用条款 | 仅提炼有明确出处的原则；不依据二手摘要构成事实 |
| C | 用户合法拥有的付费书、课程、企业内部文档 | 仅限本地私有蒸馏 | 不推送公开仓库；不输出可替代原书的长篇复述；保留来源/页码或章节索引 |
| D | 盗版扫描件、无来源转载、付费墙绕过、无法定位作者版本的材料 | 不可以 | 拒绝入库，并寻找原始公开来源 |

## 标准产物

### 1. 来源卡 `source-card`

```yaml
source_id: "src-YYYY-topic-slug"
title: "标题"
author_or_organization: "作者/机构"
url: "https://..."
source_kind: "official-doc | RFC | author-article | open-paper | user-owned-book"
access_class: "A | B | C"
license_or_terms: "已知许可或需遵守的访问条款"
version_or_date: "版本/发布日期/访问日期"
domains: ["database", "architecture"]
claim_scope: "该资料能够支持什么、不支持什么"
review_due: "YYYY-MM-DD"
```

### 2. 知识卡 `knowledge-card`

知识卡只承载**可操作、可审计、不可替代原书**的内容。每卡以一个问题为中心，而不是按章节堆砌笔记。

```yaml
knowledge_id: "kc-postgres-index-selectivity"
question: "何时需要为查询新增或调整索引？"
principle: "一到三句原创表述"
evidence:
  - source_id: "src-postgresql-current-docs"
    locator: "章节、标题或锚点"
    support: "该来源支撑的事实"
preconditions:
  - "数据规模、负载模式、版本等"
procedure:
  - "可执行的检查步骤"
tradeoffs:
  - option: "备选方案"
    benefit: "收益"
    cost_or_risk: "代价/风险"
validation:
  - "EXPLAIN/指标/测试等"
non_goals:
  - "明确不解决的问题"
last_verified: "YYYY-MM-DD"
```

### 3. 场景卡 `scenario-card`

用于让团队在真实任务中调用知识，并使测试可重复。

```yaml
scenario_id: "sc-db-slow-query-001"
context: "业务与技术背景"
request: "用户问题"
constraints: ["不可停机", "PostgreSQL 18"]
expected_roles: ["data-engineer", "platform-sre-engineer", "quality-engineer"]
required_artifacts: ["诊断假设", "执行计划", "回滚方案", "验证指标"]
forbidden_shortcuts: ["不得仅凭索引名称猜测", "不得忽略备份"]
```

### 4. 评测卡 `evaluation-card`

```yaml
evaluation_id: "eval-db-slow-query-001"
criteria:
  evidence_traceability: "每条关键事实能映射到来源卡"
  technical_correctness: "结论与版本和前提一致"
  risk_coverage: "包含回滚、数据安全和性能风险"
  collaboration_quality: "角色交接完整，无未声明假设"
  copyright_safety: "无长篇受版权材料复述"
pass_threshold: "关键项全部通过；非关键项至少 80%"
```

## 蒸馏流水线

1. **登记与准入**：创建来源卡，确认 URL、作者/机构、版本、访问类别和允许的使用边界。D 类资料立即拒绝。
2. **问题驱动阅读**：由知识蒸馏角色提出待回答的问题；不要把整本书或整站页面不加选择地塞给模型。
3. **原子化提取**：以“主张—证据定位—适用条件—反例/边界”提取。事实不等于建议；建议不等于结论。
4. **知识卡编写**：用原创语言写成可执行规则、检查步骤、取舍与验证方法。每卡最多解决一个核心问题。
5. **交叉审校**：证据审校角色检查来源和版权；相邻领域专家检查技术前提，例如数据库建议由 SRE 或后端共同审查。
6. **场景验证**：用至少一个正例、一个反例或边界例测试；输出必须解释“为什么不建议另一种做法”。
7. **发布与版本化**：通过后登记到目录，记录版本、来源复核日期和依赖的知识卡。官方文档或框架升版时重新验证。
8. **淘汰与修订**：若来源失效、版本过期、场景评测失败或发现错误，标记 `deprecated`，不要静默覆盖历史结论。

## 质量门禁

| 门禁 | 必过条件 | 失败后的处理 |
|---|---|---|
| 来源门 | 有一手链接、作者/机构、版本、访问类别 | 退回资料检索 |
| 版权门 | 没有未授权全文复制、无替代性长摘要 | 删除或改为抽象原则 |
| 技术门 | 前提、边界、替代方案和验证方法齐全 | 退回领域专家 |
| 协作门 | 交接契约完整，开放问题显式标识 | 退回角色所有者 |
| 场景门 | 至少覆盖一个成功场景和一个失败/边界场景 | 补充评测卡 |
| 发布门 | 有版本、复核日期、来源链接和责任角色 | 不得进入共享目录 |

## 本地私有书籍的安全蒸馏方式

用户上传合法拥有的书籍时，先创建 C 类来源卡，再按“每章一个问题集”处理。允许输出概念图、决策树、反例、原创代码或伪代码、引用位置和行动清单；禁止按章节连续复述、导出大量逐字摘录、生成可恢复原书结构的完整笔记，或将内容提交到公开仓库。

## 与 Agent 团队的关系

- `knowledge-distiller` 只生成来源卡/知识卡，不能绕过审校自行发布。
- `team-orchestrator` 只引用通过发布门的知识卡；对于时效性强的框架、云服务或安全信息，必须再查当前官方文档。
- `evidence-safety-auditor` 有权阻止任何不符合准入规则的材料进入共享知识库。
- `quality-engineer` 维护场景卡与评测卡，并向所有角色反馈失败样例。

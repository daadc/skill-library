# Computer Knowledge Skill Library

一个面向 **AI Agent、软件团队与技术学习者** 的可审计知识与技能库。仓库将工程方法、产品发现、架构、质量、安全交付和运行治理组织为可复用的 **Skill 定义**、带来源的 **知识卡**、可执行的 **协作流程**，并提供一个本地优先的 **MCP（Model Context Protocol）知识检索服务**，让 Agent 可以在代码与知识资产之间进行有定位、可追溯的检索。[1]

> 目标不是输出脱离语境的“最佳实践清单”，而是让人或 Agent 能够回答：**基于哪些来源和前提做决策、涉及哪些风险、如何验证，以及下一步应由谁负责。**

| 你可以在这里获得什么 | 当前内容 |
|---|---|
| 可复用的 Agent Skills | 14 个聚焦不同工程职责的 `SKILL.md` 定义，可按宿主环境的安装方式使用。 |
| 结构化技术知识 | 19 个知识领域，包含来源卡、知识卡、场景和跨领域协作资料。 |
| 协作与治理框架 | 任务路由、ADR、验收、文档治理、风险测试和证据审校的可追溯模板。 |
| 本地 MCP 检索 | Python AST、Markdown/YAML 知识图谱、CLI、持久化快照和本地知识工作台。 |

## 适用场景

这个仓库适合希望把“知识、流程与 Agent 行为”连接起来的个人和团队。典型用途包括：将一个模糊工程需求拆解为可验证的任务；为架构评审建立带来源和反例的决策上下文；将团队内部允许使用的资料蒸馏为紧凑知识卡；让 AI 在理解 Python 代码时同时检索相关的技术原则、风险和验证方式；为发布、迁移、权限或性能改动建立明确的人类 owner 与停止条件。

它不试图替代 IDE、生产观测平台、通用向量数据库或完整知识管理 SaaS。MCP 服务默认只读、仅本地运行，不执行被索引代码、不自动联网抓取、不修改源文件，也不会修改任何 MCP 客户端配置。

## 快速开始

### 1. 获取仓库并浏览一个 Skill

```bash
git clone https://github.com/daadc/skill-library.git
cd skill-library

# 从团队编排入口开始了解角色路由和交接约束
cat skills/computer-team-orchestrator/SKILL.md
```

Skill 的源文件全部在 [`skills/`](skills/) 下。请选择与你的 Agent 宿主兼容的安装/加载方式；不依赖某一个特定平台。若你本地使用 **Hermes**，可将需要的 Skill 目录复制或同步至 Hermes 识别的技能目录，例如 `~/.hermes/skills/computer-team/`。Hermes 只是一个可选集成示例，不是使用本仓库的前提，也不构成本仓库的唯一运行环境。

### 2. 从一个窄问题开始使用知识库

不要一次性要求 Agent “掌握整个领域”。先选择一个有明确决策边界的问题，并指定来源、适用条件、风险和验收方式。例如：

```text
使用 technical-knowledge-distiller，基于 PostgreSQL 官方文档，
蒸馏“为多租户订单查询新增索引前需要收集和验证哪些证据”。
请生成来源卡和知识卡，标明版本、适用条件、候选方案、风险和验证步骤。
```

然后由 `evidence-safety-auditor` 审查来源质量、版本、版权边界和未经证实的推断；对于涉及发布、权限或数据迁移的变更，再加入相应的安全、质量、平台或数据角色。

### 3. 启动 MCP 知识检索服务

[`mcp/`](mcp/) 将知识卡、场景、`sources.yaml` 与 Python AST 转换为本地图谱。它要求 **Python 3.10+**；以下示例使用 `uv`：

```bash
cd mcp

# 首次构建，后续相同工作树会加载本地快照
uv run knowledge-connection --root .. index

# 搜索知识、场景和代码符号
uv run knowledge-connection --root .. --json search "安全交付" --kind knowledge --limit 5

# 使用版本化离线案例检查检索回归
uv run knowledge-connection --root .. --json eval --cases evals/retrieval_cases.json

# 启动仅绑定本机回环地址的知识工作台
uv run knowledge-connection --root .. workbench --port 8765
```

首次索引会在目标根目录创建可删除重建的 `.knowledge-connection/graph.sqlite3`。该目录仅保存派生状态，已被 Git 忽略；服务不会修改被索引代码或知识文件。

## MCP：为 Agent 提供可追溯检索

MCP 是本仓库连接 Agent 与知识资产的主要集成面。服务通过 stdio 公开结构化工具，结果始终携带相对路径、行号、节点类型和关系理由；调用者应将检索结果视为**待审阅证据**，而不是自动执行授权。[1]

| MCP 工具 | 用途 |
|---|---|
| `index_repository` | 构建或加载允许根目录的本地持久图谱。 |
| `index_status` | 查看本地派生快照是否存在及其统计信息。 |
| `refresh_repository` | 显式刷新图谱；仅写入 `.knowledge-connection/` 派生状态。 |
| `search_knowledge` | 搜索知识卡、场景、来源与 Python 符号。 |
| `get_node` | 返回节点正文、相对定位和直接关系。 |
| `explore_connections` | 在深度和数量上限内浏览局部关系。 |
| `build_context_pack` | 在字符预算内生成保留定位和引用的 Agent 上下文包。 |

你可以在自己的 MCP 客户端中手动添加如下配置。请将路径替换为本机仓库绝对路径；本项目不会自动写入客户端配置。

```json
{
  "mcpServers": {
    "knowledge-connection": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/skill-library/mcp",
        "knowledge-connection-mcp",
        "--root",
        "/absolute/path/to/skill-library"
      ]
    }
  }
}
```

MCP 还附带可脚本化的 CLI：`index`、`status`、`refresh`、`search`、`node`、`connections`、`context`、`eval` 与 `workbench`。完整工具契约、边界和验证证据见 [`mcp/README.md`](mcp/README.md)、[`mcp/docs/interaction-contract.md`](mcp/docs/interaction-contract.md) 和 [`mcp/docs/p0-p2-verification-report.md`](mcp/docs/p0-p2-verification-report.md)。

## Skill 团队

Skill 是带职责边界、输入证据、交接产物和质量要求的 Markdown 定义。`computer-team-orchestrator` 负责在风险等级、停止条件和明确人类 owner 的约束内，选择最少必要角色并合成结果；它不替代授权、审批或最终责任人。

| Skill | 主要职责 |
|---|---|
| [`computer-team-orchestrator`](skills/computer-team-orchestrator/SKILL.md) | 任务拆解、角色路由、冲突协调与最终合成。 |
| [`technical-knowledge-distiller`](skills/technical-knowledge-distiller/SKILL.md) | 将许可资料蒸馏为来源卡、知识卡和场景。 |
| [`evidence-safety-auditor`](skills/evidence-safety-auditor/SKILL.md) | 审校来源、版本、版权、风险与事实边界。 |
| [`tech-lead-architect`](skills/tech-lead-architect/SKILL.md) | 架构权衡、ADR、系统演进与跨域评审。 |
| [`backend-runtime-engineer`](skills/backend-runtime-engineer/SKILL.md) | 后端运行时、API、并发、服务实现和调试。 |
| [`platform-sre-engineer`](skills/platform-sre-engineer/SKILL.md) | Linux、网络、SRE、可观测性、性能与事故响应。 |
| [`cloud-native-data-platform-engineer`](skills/cloud-native-data-platform-engineer/SKILL.md) | Kubernetes、Nginx、Redis、MongoDB、Kafka 与平台工程。 |
| [`resilience-engineering`](skills/resilience-engineering/SKILL.md) | 超时、重试、熔断、限流、降级与恢复设计。 |
| [`data-engineer`](skills/data-engineer/SKILL.md) | PostgreSQL、MySQL、SQL、迁移、索引与恢复。 |
| [`frontend-design-engineer`](skills/frontend-design-engineer/SKILL.md) | 前端组件、状态、可访问性与设计系统。 |
| [`product-discovery-manager`](skills/product-discovery-manager/SKILL.md) | 问题发现、需求、范围、优先级与验收。 |
| [`quality-engineer`](skills/quality-engineer/SKILL.md) | 风险测试、回归、发布门禁与 Agent 评测。 |
| [`documentation-governance-engineer`](skills/documentation-governance-engineer/SKILL.md) | Docs-as-Code、ADR、Runbook、发布契约与陈旧性治理。 |
| [`secure-delivery-engineer`](skills/secure-delivery-engineer/SKILL.md) | Git/PR/CI-CD、制品、API 安全、供应链证据与安全发布审查。 |

## 知识库导航

每个知识包通常由 `sources.yaml`、`knowledge-cards.md` 和 `scenarios.md` 组成；它们将原则与来源、假设、风险、验证和跨角色协作场景关联起来。知识卡是工程决策的压缩材料，并不替代原始资料或领域专家审阅。

| 主题 | 目录与示例内容 |
|---|---|
| 产品、架构与演进 | [`knowledge/product-discovery/`](knowledge/product-discovery/)、[`knowledge/architecture-patterns/`](knowledge/architecture-patterns/)、[`knowledge/domain-driven-design/`](knowledge/domain-driven-design/)、[`knowledge/refactoring-evolution/`](knowledge/refactoring-evolution/)、[`knowledge/technology-selection/`](knowledge/technology-selection/) |
| 工程质量与治理 | [`knowledge/development-lifecycle/`](knowledge/development-lifecycle/)、[`knowledge/testing-engineering/`](knowledge/testing-engineering/)、[`knowledge/documentation-governance/`](knowledge/documentation-governance/)、[`knowledge/secure-delivery/`](knowledge/secure-delivery/) |
| 运行与韧性 | [`knowledge/observability-performance/`](knowledge/observability-performance/)、[`knowledge/resilience-engineering/`](knowledge/resilience-engineering/) |
| 云原生与数据平台 | [`knowledge/kubernetes/`](knowledge/kubernetes/)、[`knowledge/nginx/`](knowledge/nginx/)、[`knowledge/kafka/`](knowledge/kafka/)、[`knowledge/redis/`](knowledge/redis/)、[`knowledge/mongodb/`](knowledge/mongodb/) |
| 跨域框架 | [`knowledge/shared/`](knowledge/shared/) 中的受约束 Agent 开发、复杂系统交付、协作场景和研究登记。 |

## 项目结构

```text
skill-library/
├── skills/                 # 可复用 Skill 定义
├── knowledge/              # 来源卡、知识卡、场景与共享框架
├── templates/              # ADR、交互契约等可复用文档模板
├── mcp/                    # 本地 Knowledge Connection MCP、CLI、工作台与测试
├── DISTILLATION_WORKFLOW.md
├── TEAM_BLUEPRINT.md
├── TEAM_TEST_PLAN.md
├── SOURCE_CANDIDATES.md
└── ROADMAP_COVERAGE_GAP_ANALYSIS.md
```

## 知识准入、版权与安全边界

| 资料类型 | 处理方式 |
|---|---|
| 官方文档、RFC、开放论文、明确开放许可的原作者文章 | 可作为公开知识蒸馏的候选来源，但仍须记录版本、适用范围和引用。 |
| 合法拥有的书籍、课程或内部文档 | 可在私有环境内做受限蒸馏；不得推送受保护原文或可替代原文的长篇复述。 |
| 盗版扫描件、绕过付费墙内容、无出处转载或无法确认版本的材料 | 不应纳入知识库或作为训练/蒸馏来源。 |
| 人或 Agent 生成的推断 | 必须标明为推断，并与已验证来源、约束和验证方法区分。 |

对高影响操作，例如生产发布、权限调整、批量修改、外部发送或数据迁移，Agent 的检索结论只能用于准备建议、预演和审阅；具体执行仍需遵循项目自己的授权、审批、审计与回退流程。

## 验证与演进

MCP 当前已经覆盖 Python AST、Markdown/YAML 知识、SQLite 本地快照、Markdown 文件级增量刷新、CLI、stdio 协议和仅回环地址的工作台。测试命令和验证记录位于 [`mcp/README.md`](mcp/README.md) 与 [`mcp/docs/p0-p2-verification-report.md`](mcp/docs/p0-p2-verification-report.md)。

后续是否加入多语言解析、语义检索、远程访问、认证、协作写入或团队治理，将以真实使用证据为前提，并先更新 ADR、权限模型、评测和发布门禁；不会由当前本地只读服务自动开启。参见 [`mcp/docs/ROADMAP.md`](mcp/docs/ROADMAP.md)。

## 贡献与使用说明

欢迎通过 Issue 或 Pull Request 提交可复现的缺口、错误来源、改进建议、测试用例或新的窄主题知识包。提交知识内容时，请保留来源、版本、适用条件、风险、验证方式和版权边界；提交 Skill 时，请说明职责边界、输入、输出、停止条件和评测方式。

仓库当前**未包含许可证文件**。在复制、再发布或用于生产环境前，请先与维护者确认适用的使用许可和责任边界。

## 参考资料

[1]: https://modelcontextprotocol.io/

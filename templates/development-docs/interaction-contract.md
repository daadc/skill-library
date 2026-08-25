# 交互契约：<用例/命令/查询/事件名称>

| 字段 | 内容 |
|---|---|
| 类型 | `HTTP command \| HTTP query \| async task \| domain event \| integration event \| BFF aggregation` |
| Owner | `<服务/context/团队>` |
| 消费者 | `<前端、服务、集成方>` |
| 状态 | `draft \| active \| deprecated \| retired` |
| 规范链接 | `<OpenAPI / AsyncAPI / JSON Schema / protobuf>` |
| 兼容性策略 | `<additive first、版本、弃用窗口>` |
| 关联 ADR / 测试 | `<链接>` |

## 1. 用户/业务任务

描述 actor、权限、触发场景、目标和不可完成时的用户体验。

## 2. 输入与输出

引用版本化 schema；说明默认值、字段含义、单位、时间、分页/排序/筛选、敏感字段和示例。

## 3. 规则与状态机

```text
<合法状态与迁移；每个状态的 owner 和用户可见语义>
```

列出校验、领域不变量、权限与租户边界。

## 4. 幂等与并发

- Idempotency key / 去重范围与保存期：
- 重复请求/重复事件的结果：
- 版本/ETag/条件更新/命令串行化：
- 冲突响应与用户/消费者恢复方式：

## 5. 失败与异步语义

| 情况 | 稳定码/事件 | 是否可重试 | 用户/消费者动作 | 观测 |
|---|---|---:|---|---|
| 校验失败 |  | 否 |  |  |
| 权限拒绝 |  | 否 |  |  |
| 并发冲突 |  | 视情况 |  |  |
| 临时依赖失败 |  | 视情况 |  |  |
| 部分完成/长任务 |  |  |  |  |

说明 deadline、取消、任务进度/轮询/SSE/webhook、事件 key/顺序/交付/重放/DLQ 和过期/取消。

## 6. 兼容、弃用与安全

说明 mixed-version 行为、feature flag、migration/rollback、弃用通知与删除条件；列出认证、授权、速率/配额、审计、PII/日志要求。

## 7. 验证与批准

列出 producer/consumer contract tests、schema validation、错误/并发/E2E/性能/安全测试；记录消费者、质量、产品/设计和人类 owner 审查结果。

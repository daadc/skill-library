# Kubernetes 知识卡

## KC-K8S-001：何时选择 Deployment，何时需要有状态工作负载方案？

**问题。** 新服务准备部署到 Kubernetes，如何避免把所有 Pod 都当作可互换的无状态副本？

**原则。** `Deployment` 管理通常不维护状态、Pod 可互换的应用工作负载；在开始部署前，必须先明确数据持久化、实例身份、稳定网络名、启动/终止顺序与故障恢复是否属于业务契约。[1]

| 检查项 | 使用 Deployment 的信号 | 需要进一步设计的信号 |
|---|---|---|
| 实例身份 | 任一副本可处理任一请求 | 实例身份、固定排序或稳定网络地址有语义 |
| 状态 | 状态在外部数据库/对象存储，或可安全重建 | 本地状态必须保留、复制或有一致性要求 |
| 扩缩容 | 可水平扩缩，副本无差别 | 需要分区、主从、成员发现或顺序维护 |
| 发布 | 可用新副本逐步替代旧副本 | 协议/数据格式需要有序升级和跨版本兼容 |

**实施步骤。** 先由 `tech-lead-architect` 定义状态与数据所有权；再由 `data-engineer` 与 `platform-sre-engineer` 分别确认持久化、备份恢复、容量、可用区和故障域。只有在上述契约明确后，才编写工作负载清单。

**风险与边界。** 不要根据镜像名称或“数据库能跑在容器中”来选择控制器。Kubernetes 控制面会驱动声明状态，但它不会替代数据库复制、备份恢复和业务一致性设计。[1]

**验证。** 使用包含单 Pod 丢失、节点不可用、扩容、滚动升级和回滚的演练；分别验证数据完整性、服务可用性与恢复时间。

---

## KC-K8S-002：如何做可回滚的 Deployment 发布？

**问题。** 如何避免把 `kubectl apply` 误当成完整的发布策略？

**原则。** Deployment 会根据 Pod 模板变化创建新的 ReplicaSet，并按策略逐步调整新旧副本；只有 `.spec.template` 的变化会触发新的 rollout revision。发布安全性取决于探针、资源、就绪条件、流量策略和回滚验证，而不是仅依赖控制器默认值。[2]

**最低发布契约。**

```yaml
release_contract:
  image: "不可变标签或可审计摘要"
  readiness: "就绪代表可接受真实流量，而非仅进程存活"
  liveness: "仅在重启能够改善的失败场景使用"
  startup: "慢启动服务应避免被过早判死"
  resources: "requests/limits 基于测量或明确假设"
  strategy: "maxSurge/maxUnavailable 与可用性、容量相匹配"
  observability: "版本、错误、延迟、饱和、就绪副本和发布事件可观测"
  rollback: "回滚触发条件、所有者、数据/协议兼容性检查"
```

**决策步骤。** 先确认前后版本是否能同时处理消息、数据库模式和外部 API；再根据 SLO、容量余量和初始化时长设置发布策略；用预发布环境或小范围流量验证，再逐步扩大。

**常见错误。** 选择器不可变，且重叠选择器可能造成控制器冲突；把“Pod Running”当作可接流量；发布期间忽略终止中 Pod 的额外资源占用；在不兼容数据库迁移之后期待镜像回滚解决问题。[2]

**验证。** 人为注入新版本启动失败、依赖超时和错误率上升，确认 rollout 暂停/回滚、告警、日志和业务指标都能识别异常。

---

## KC-K8S-003：如何规划 Kubernetes 小版本升级？

**问题。** 集群升级时，哪些组件顺序和版本兼容性必须先审查？

**原则。** Kubernetes 项目维护最近三个 minor release 分支；`kubelet` 和 `kube-proxy` 不得比 `kube-apiserver` 更新，允许的 minor skew 有边界。具体托管服务、CNI、CSI、Ingress、Admission Webhook 和运维工具可能施加更严格限制。[3]

**升级前检查。**

1. 记录集群、控制面、节点、`kubectl`、CNI/CSI/Ingress、Operator、Webhook 和关键工作负载的实际版本。
2. 读取目标版本的弃用、API 变更、安全和存储/网络兼容说明。
3. 检查 Admission Webhook 是否能处理新 API 版本和字段；清点已弃用 API 与 CRD。
4. 验证 etcd/控制面备份与恢复、节点 drain 策略、PodDisruptionBudget、容量余量和回滚/应急路径。
5. 先升级控制面，再按受支持的顺序滚动升级节点组件；不要跳过 minor 版本。[3]

**验证。** 在可复现的预生产环境走完整升级与故障回退演练；生产执行时分批 drain 节点、观察控制面与工作负载 SLO，并在每批设置停机判断点。

## References

[1]: https://kubernetes.io/docs/concepts/architecture/
[2]: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
[3]: https://kubernetes.io/releases/version-skew-policy/

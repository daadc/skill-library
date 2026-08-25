# Kubernetes 场景卡

## SC-K8S-001：发布后新版本 CrashLoopBackOff

**输入。** 某 Deployment 发布后，新 ReplicaSet 的 Pod 无法就绪，旧副本仍在提供流量；服务需要在 15 分钟内恢复 SLO。

**责任路由。** `platform-sre-engineer` 先确认影响、暂停扩大和保留证据；`backend-runtime-engineer` 检查镜像、配置、依赖、启动与探针；`tech-lead-architect` 判断协议/数据兼容性；`quality-engineer` 将根因变成回归测试。

**必须证据。** Deployment/ReplicaSet/Pod 事件、日志、资源/节点状态、就绪与存活探针、变更差异、业务 SLI、回滚兼容性。

**通过条件。** 恢复路径是可逆的；旧版本与数据/API 状态兼容；修复覆盖“为何未能就绪”，而非仅增加重试。

## SC-K8S-002：Kubernetes minor 升级前审查

**输入。** 计划从当前支持版本升级一个 minor，集群有 Ingress、Webhook、CSI、状态服务和多个 namespace。

**通过条件。** 输出版本/依赖矩阵、弃用 API 清单、备份恢复证据、节点 drain/PDB 策略、分批计划、停机阈值、回退与人工批准点。参见 `knowledge-cards.md` 的 KC-K8S-003 和共享场景 SC-PLAT-003。

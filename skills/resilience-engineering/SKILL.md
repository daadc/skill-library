---
name: resilience-engineering
description: Design and review concurrency control and distributed-system resilience. Use for request deadlines, timeouts, cancellation, retries, backoff and jitter, idempotency, circuit breakers, bulkheads, rate limiting, queues, load shedding, graceful degradation, cascading failures, capacity tests, and recovery design.
---

# Resilience Engineering

Use this Skill to make a failure-aware design, not to bolt generic retry or circuit-breaker libraries onto an unknown request path. Read `knowledge/resilience-engineering/knowledge-cards.md` and the relevant component cards before making recommendations.

## Required Inputs

Collect or mark as `unknown`:

- User-facing SLO/deadline, priority class, and acceptable degraded behavior.
- End-to-end request/data path, including gateways, queues, workers, caches, databases, and external dependencies.
- Actual timeout, retry, idempotency, pool, queue, rate-limit, and circuit-breaker settings at every layer.
- Failure evidence: latency percentiles, error classes, in-flight requests, queue depth/age, pool saturation, CPU/memory/GC, connection and dependency metrics.
- Dependency ownership, side effects, data consistency/RPO/RTO, and recovery capabilities.

## Workflow

1. **Map the path and budgets.** Start at the user deadline; allocate time for gateway, queueing, service work, downstream work, retry and safety margin. Require cancellation propagation.
2. **Classify the operation.** State whether it is read-only, idempotent write, non-idempotent side effect, asynchronous work, or control-plane operation. Identify deduplication/compensation rules.
3. **Choose protection in order.** Prefer small bounded concurrency/queues, admission control, backpressure, priority, and per-dependency/tenant isolation before retries. Use retry only for plausible transient failures. Use circuit breaking when continued calls are likely to fail and a defined fallback exists.
4. **Design recovery.** Specify load shedding/degraded behavior, message replay/DLQ rules, circuit half-open probes, manual controls, data repair, and user-visible state.
5. **Design observability and tests.** Add dependency-scoped metrics, state transitions, traces, saturation signals and business correctness checks. Fault-inject latency, failure, partial success, recovery and load spikes.
6. **Review the release.** Require owner, thresholds, stop conditions, rollback, runbook, alerting and human approval for production changes.

## Decision Rules

| Concern | Rule |
|---|---|
| Timeout | Derive from an end-to-end budget; do not use a universal client default. Include connection/DNS/TLS semantics and upstream cancellation. |
| Retry | Retry one selected layer, a limited number of times, with capped exponential backoff and jitter. Require idempotency or a stable idempotency key for side effects. |
| Circuit breaker | Scope by operation/dependency/partition; design Closed/Open/Half-Open transitions, limited probes, observability, fallback and manual override. Do not use it to hide business exceptions. |
| Bulkhead | Isolate thread pools, connections, queues, instances or tenants when a failing dependency could consume shared resources. Size and test each partition. |
| Queue | Bound it. Queue age and depth are first-class signals. A queue is not capacity; reject or defer work before long queues consume resources and deadlines. |
| Rate limit | Key it by a meaningful resource owner (tenant/user/API key), prioritize critical paths, and test shared-NAT/proxy behavior. |
| Degradation | Declare correctness and UX implications; never silently return stale/partial data for money, authorization, inventory or compliance decisions. |

## Failure Review Questions

- Can retries at more than one layer multiply load? What is the upper bound?
- Does a timeout mean the side effect did not occur? If unknown, how does the caller query/deduplicate safely?
- What resource becomes exhausted first under overload, and what happens then?
- Which dependency, tenant, queue or region can consume another path's resources?
- How do you distinguish transient errors, permanent errors, overload signals and cancellation?
- What is the recovery sequence after the dependency returns? Can it absorb backlog and reconnect storms?

## Required Handoff

```yaml
resilience_handoff:
  request_or_data_path: []
  slo_and_deadline_budget: {}
  operation_semantics: ""
  resource_bounds: {concurrency: "", queue: "", pools: "", rate_limits: ""}
  timeout_retry_and_idempotency: {}
  circuit_and_fallback: {}
  degradation_contract: {}
  observability: []
  fault_injection_plan: []
  rollout_and_recovery: {}
  unknowns_and_approvals: []
```

## Safety Boundary

Do not change production timeout, retry, rate-limit, circuit-breaker, queue, Kubernetes resource, autoscaling, database, cache, or Kafka settings without explicit human approval. Recommendations must identify the expected benefit, failure mode, measurable stop condition, rollback and data-correctness impact.

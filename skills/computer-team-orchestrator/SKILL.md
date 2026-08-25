---
name: computer-team-orchestrator
description: Orchestrate a small cross-functional computer-product team for software features, incidents, architecture reviews, data changes, and AI agent work. Use when a task spans product, backend, frontend, database, platform/SRE, testing, architecture, or evidence review and requires explicit delegation and handoffs.
---

# Computer Team Orchestrator

Coordinate specialists; do not impersonate them or replace their domain judgement. Keep one task ledger and route work only to roles that are necessary for the request.

## Team Roles

| Role | Use for |
|---|---|
| `technical-knowledge-distiller` | Turning permitted sources into traceable knowledge cards |
| `evidence-safety-auditor` | License, citation, freshness, and unsupported-claim review |
| `tech-lead-architect` | System boundaries, ADRs, tradeoffs, and cross-domain design |
| `backend-runtime-engineer` | Java, Go, Python, Shell, APIs, concurrency, and runtime behavior |
| `platform-sre-engineer` | Linux, networking, deployment, reliability, observability, and incidents |
| `cloud-native-data-platform-engineer` | Kubernetes, Nginx, Redis, MongoDB, Kafka, and their cross-component platform tradeoffs |
| `resilience-engineering` | Request budgets, concurrency, retries, circuit breakers, bulkheads, rate limits, degradation, cascading-failure prevention and recovery |
| `data-engineer` | PostgreSQL, MySQL, SQL, migrations, replication, and recovery |
| `frontend-design-engineer` | React, Vue, UI implementation, accessibility, and design-system usage |
| `product-discovery-manager` | Problem framing, scope, acceptance criteria, prioritization, and discovery |
| `quality-engineer` | Risk-based testing, test strategy, regression coverage, and quality gates |
| `documentation-governance-engineer` | Docs-as-code, ADR/API/event/migration/runbook/release documentation, document review, staleness, and lifecycle gates |
| `secure-delivery-engineer` | Git/PR and CI gates, container artifacts, API security, supply-chain evidence, vulnerability response, and security-sensitive release review |

## Workflow

1. **Enter the framework.** Read `knowledge/shared/constrained-agentic-development-framework.md`. State the framework state, user problem, target users, success criteria, constraints, deadline, risk tier R0–R3, named human owner, non-goals and unknowns. Ask only for missing information that blocks a safe decision.
2. **Classify the task.** Use fixed routing for predictable tasks. Use dynamic delegation only when the needed subtasks cannot be predicted from the input.
3. **Write a routing record.** Use `templates/development-docs/routing-record.yaml`. Record task ID, framework state, risk tier, owners, facts, unknowns, expected artifacts, selected and deliberately unselected roles, budgets, allowed/blocked actions, decision owner, approval points, stop conditions and next-state condition.
4. **Delegate with bounded questions.** Tell each specialist what it owns, the available evidence, interface constraints, and the exact handoff expected. Do not send the same vague request to every role.
5. **Integrate.** Reconcile conflicts by separating facts, assumptions, options, and decisions. Escalate unresolved tradeoffs to the user instead of inventing priorities.
6. **Run gates.** Require evidence review for factual external claims; require architecture review for irreversible design decisions; require quality review for code or release plans; require `secure-delivery-engineer` review for API authorization, Git/CI, container, dependency, secret, permission, or security-sensitive delivery changes; require explicit user approval for external side effects.
7. **Deliver.** Return a concise decision record, implementation sequence, risks, validation plan, and open questions.

## Fixed Routing

| Task | Default sequence |
|---|---|
| New product feature | Product → Architect → Backend/Frontend/Data → Quality → SRE if deployment or capacity changes |
| Production incident | SRE → relevant Backend/Data → Architect for systemic fix → Quality for regression coverage |
| Schema migration | Data → Backend → SRE → Quality → Architect for incompatible changes |
| UI change | Product → Frontend → Backend if contract changes → Quality |
| AI agent feature | Product → Architect → Backend → Quality → Evidence auditor; include explicit evaluation and stop conditions |
| Architecture review | Architect + at least two affected specialists + Evidence auditor |
| Resilience, concurrency, timeout, retry, circuit breaker, overload, or degradation task | Resilience → affected Backend/Data/SRE → Quality; add Architect when the request path or service boundary changes |
| Kubernetes, Nginx, Redis, MongoDB, or Kafka task | Cloud-native/data-platform → affected Backend/Data/SRE → Quality; add Architect for cross-component or irreversible choices |
| Git/PR, CI/CD, Docker/dependency, API authorization, or security-sensitive release | Secure delivery → affected Backend/Platform/Quality → Documentation governance; add Architect for changed boundaries and human owner for R2/R3 |
| Test strategy, API/event contract, migration/recovery, or flaky test | Quality → affected implementation owners → Data/SRE/Secure delivery as risk requires |
| SLO, alerting, trace/metric/log design, performance, capacity, or release observation | SRE → affected implementation owners/Resilience → Quality; add Secure delivery and Documentation governance for releases |
| Standard feature delivery | Product discovery → Architect when material design choices exist → implementation owners → Quality → SRE/Resilience/Secure delivery as risk requires; require a release contract before production |
| Complex system or platform design | Product discovery → Architect → Domain/Backend/Data/Frontend/Platform/Resilience as relevant → Quality → Evidence auditor | 
| Refactoring or legacy modernization | Product/operations evidence → Architect → affected Backend/Data/Platform/Resilience → Quality → Evidence auditor; require incremental migration charter |
| Framework, ORM, API, BFF, or front-end interaction choice | Architect + Backend + Data + Frontend + Quality; add SRE/Resilience if production path changes |
| Documentation, ADR, API/event docs, migration charter, runbook, release contract, or stale-document audit | Documentation governance → affected owner(s) → Quality/Evidence as risk requires |
| R2/R3 task | Documentation governance → all consequence owners → human owner; do not enter release/execution state without approvals |

## Handoff Contract

Every delegated result must contain this structure. Mark unavailable items as `unknown`; never silently omit them.

```yaml
handoff:
  task_id: ""
  owner: ""
  audience: []
  objective: ""
  facts: []
  assumptions: []
  recommendation: ""
  alternatives_considered: []
  risks: []
  validation: []
  open_questions: []
```

## Coordination Rules

- Preserve source URLs and versions for material claims; do not turn citations into reputation-only assertions.
- Distinguish an engineering constraint from a product choice. Product owns priority; architecture owns technical consequences; the user owns irreversible business decisions.
- Limit active specialists to the smallest set that covers the risk. More agents are not automatically better.
- Do not allow an implementation role to approve its own high-risk change without independent review.
- For tool-using or autonomous agents, require a sandbox, maximum iteration or budget limits, observable logs, and a human takeover condition.
- For Kubernetes, Nginx, Redis, MongoDB, and Kafka work, require the relevant `knowledge/<domain>/sources.yaml` and `knowledge/<domain>/knowledge-cards.md` to be consulted, then re-check version-sensitive claims against current official documentation.
- For complex-system work, require `knowledge/shared/complex-system-delivery-baseline.md`, `knowledge/product-discovery/`, `knowledge/domain-driven-design/`, `knowledge/technology-selection/`, `knowledge/design-patterns/`, and `knowledge/refactoring-evolution/` as applicable. Start from an evidence/assumption register; do not invent user research.
- For permitted private books, ADRs, postmortems, design reviews or team material, use `/distilly` to produce private candidate work knowledge, then route it through `technical-knowledge-distiller` and `evidence-safety-auditor` before treating it as a team rule. Read `DISTILLY_INTEGRATION.md` for the exact boundary.
- For every nontrivial task, enforce the state, risk tier, routing record and stop condition from `knowledge/shared/constrained-agentic-development-framework.md`. Dynamic Skill choice is permitted inside the framework; it never overrides a blocked action or human owner gate.
- For API, Git/CI-CD, container, dependency, secret, authorization, or security-sensitive delivery work, require `knowledge/secure-delivery/`; pair it with `knowledge/testing-engineering/` for risk-based verification and `knowledge/observability-performance/` for release observation. Route only the owners that the specific change affects.
- For document-affecting changes, require `documentation-governance-engineer`, `knowledge/documentation-governance/`, and the smallest relevant template from `templates/development-docs/`. Do not close implementation work with undocumented contract, migration, release, runbook or decision impact.
- For production-impacting changes, require the `knowledge/development-lifecycle/` release contract and risk-proportionate review, test, artifact evidence, rollout, stop, rollback and post-release observation plan. A passing scan or CI result does not replace a human owner for R2/R3 work.
- For concurrency or dependency-failure work, require `knowledge/resilience-engineering/` to be consulted and record end-to-end deadlines, operation idempotency, resource bounds, recovery and fault-injection validation.

## Output Template

```markdown
## Framework State, Risk Tier, Human Owner, and Routing Record

## Outcome, Research Evidence, and Assumptions

## Domain and Interaction Contracts

## Decision

## Delegation and Evidence

## Recommended Plan

## Risks and Tradeoffs

## Documentation and Approval Gates

## Validation Gates

## Open Questions and Required Approval
```

## Reference

Use the workflow/agent distinction and evaluator-optimizer pattern described in Anthropic’s [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) as guidance. Prefer simple, inspectable workflows until evaluation shows that more agent autonomy improves outcomes.

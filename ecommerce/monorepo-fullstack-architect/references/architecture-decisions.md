# Architecture decisions: monolith, modular monolith, microservices

## Contents
1. Choosing the style
2. Modular monolith blueprint
3. Microservices blueprint
4. Extraction triggers and how to extract safely
5. Data ownership rules
6. ADR template

## 1. Choosing the style

Start from constraints, not fashion. Score the project against these signals.

| Signal | Points toward |
|---|---|
| One team (under about 8 engineers), domain still being discovered | Modular monolith |
| Needs to ship fast with low operational overhead | Modular monolith |
| One component has a very different load profile (media processing, search, realtime fan-out) | Extract that component |
| Multiple teams that need independent release cadence | Services along team lines |
| A failure in one capability must not take down others (payments adapters, notifications) | Extract with fault isolation |
| A part needs a different runtime for a real reason (Go for a hot path, Python for ML) | Extract that part |
| Compliance requires isolating a data set or region | Extract with its own store |
| User explicitly requests microservices | Build microservices, record risks in an ADR |

Rules of thumb:

- A modular monolith is the default. It keeps transactions local, deploys simply, and debugs easily, while module boundaries preserve the option to split later.
- Do not split to look scalable. Network calls replace function calls, and every call now needs timeouts, retries, idempotency, tracing, and versioning.
- Do not build a "distributed monolith": services that must deploy together, share a database, or call each other synchronously in long chains. That is the worst of both worlds.
- Hybrid is normal: a modular monolith core plus a handful of extracted services.

## 2. Modular monolith blueprint

One deployable (or one per runtime), many modules with hard boundaries.

```text
apps/
  api/                    # single backend process: composition root only
    src/modules/
      catalog/            # each module owns its tables, logic, and public API
        public/           # the ONLY surface other modules may import
        internal/         # private: domain, repositories, handlers
      orders/
      payments/
      identity/
    src/platform/         # cross-cutting: config, logging, db, cache, event bus
```

Boundary rules (enforce with lint or module-boundary tooling, not by trust):

- A module imports another module only through its `public/` API (functions or events), never its internals or tables.
- Each module owns its schema (separate Postgres schema or table prefix). No cross-module joins; compose in code or via a read model.
- Cross-module side effects go through an in-process event bus backed by a transactional outbox, so later extraction to a real broker changes the transport and nothing else.
- Each module has its own tests and could be lifted out with its tables and public interface intact.

Scaling a modular monolith: run N identical replicas behind a load balancer, keep processes stateless, put sessions and caches in Redis or signed tokens, run background workers as a separate process type from the same codebase.

## 3. Microservices blueprint

```text
services/
  identity/   catalog/   orders/   payments/   notifications/
  each: own repo folder, own database, own Dockerfile, own CI job, own OpenAPI + event schemas
apps/
  gateway/    # API gateway or BFF: auth, rate limit, routing, response shaping
  web/  admin/  mobile/
packages/
  contracts/  # shared schemas: OpenAPI, event schemas, generated clients
  observability/  auth-client/  config/  ui/
```

Requirements for every service:

- Own its data. No other service reads or writes its database.
- Versioned API and event contracts with compatibility checks in CI.
- Health (`/healthz` liveness, `/readyz` readiness), metrics, traces, structured logs with correlation IDs.
- Timeouts, bounded retries, and circuit breakers on every outbound call; deadlines propagated across hops.
- Idempotent handlers for both requests and events.
- A runbook entry and an owner.

Communication guidance:

- Synchronous (HTTP or gRPC) for queries that need an immediate answer and for commands where the caller must know the result. Keep chains short, ideally one hop deep.
- Asynchronous events for propagation, projections, notifications, and anything that tolerates delay. Use the outbox to publish and an inbox or dedup table to consume.
- A gateway or BFF shapes data for each client, so clients do not make five calls to render one screen.
- Cross-service workflows use sagas with compensations (see `consistency-and-availability.md`), not distributed transactions.

## 4. Extraction triggers and how to extract safely

Extract a module into a service when at least one is true and measured:

- Its scaling profile differs enough that sharing a process wastes money or causes contention.
- Its deploy cadence or team ownership conflicts with the rest.
- Its failures need isolation from the core path.
- It needs a different runtime or data store for a proven reason.

Safe extraction sequence (strangler pattern):

1. Confirm the module already has a clean `public/` API and owns its tables.
2. Put an interface in front of calls to it; keep the in-process implementation.
3. Stand up the service with the same API; mirror data via outbox events or a one-time migration plus change capture.
4. Route a small percentage of traffic to the service; compare results.
5. Cut over, keep rollback ready, then remove the old code and tables after a soak period.

## 5. Data ownership rules

- One authoritative writer per entity. Others hold references (IDs) and derived copies.
- Never share a database between services. Sharing a database server with separate schemas and credentials is acceptable for cost reasons if nothing crosses the boundary.
- Derived stores (search indexes, caches, read models, analytics) can always be rebuilt from the source of truth plus events. Write and test the rebuild path.
- Reference data copied across boundaries carries a version or timestamp so staleness is visible.
- Store money as integer minor units with a currency code; store timestamps in UTC with timezone handled at the edge.

## 6. ADR template

Save as `docs/adr/NNNN-short-title.md`.

```markdown
# NNNN. Title

Status: proposed | accepted | superseded by NNNN
Date: YYYY-MM-DD

## Context
What forces are at play: requirements, constraints, scale assumptions, team.

## Decision
What we chose, in one or two sentences.

## Alternatives considered
Option A: why not. Option B: why not.

## Consequences
Good, bad, and what we now have to do (operational load, migration path, risks).

## Revisit when
The measurable condition that would make us change this decision.
```

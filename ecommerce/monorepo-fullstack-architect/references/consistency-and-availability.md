# Consistency and availability

## Contents
1. Decide consistency per operation
2. Transactions and constraints
3. Concurrency control
4. Idempotency
5. Transactional outbox and inbox
6. Sagas for multi-step workflows
7. Replicas, read-your-writes, and staleness
8. Distributed locks and coordination
9. Availability: SLOs, redundancy, degradation, recovery
10. Time, ordering, and IDs
11. Background jobs

## 1. Decide consistency per operation

Write a table in `docs/architecture.md`, one row per write path and per important read.

| Operation | Consistency | Mechanism |
|---|---|---|
| Place order, take payment, reserve stock, redeem coupon | Strong | Single-store transaction, conditional update, unique constraints |
| Change password, permissions, account status | Strong, then revoke sessions | Transaction plus session or token invalidation |
| Profile edits | Strong writes, version check | Optimistic concurrency |
| Product listing, feed, search results | Eventual (seconds) | Projection from events |
| Counters (views, likes) | Eventual | Buffered increments, periodic flush |
| Analytics | Eventual (minutes) | Event pipeline |

Principle: pay for strong consistency only where wrong data costs money, trust, or safety. Everywhere else prefer availability and speed, and make staleness bounded and visible.

## 2. Transactions and constraints

- Express invariants in the database, not only in code: primary and unique keys, foreign keys, `CHECK` constraints, exclusion constraints (for example no overlapping bookings). Constraints still hold when a bug slips past code review.
- Keep transactions short. No network calls to external services inside a transaction.
- Choose isolation deliberately. `READ COMMITTED` is the usual default; use `REPEATABLE READ` or `SERIALIZABLE` with retry for invariants spanning multiple rows, and always retry on serialization failures with a bound.
- Use conditional updates for counters and stock so the check and the change are one atomic statement:

```sql
UPDATE inventory
SET available = available - $2
WHERE sku_id = $1 AND available >= $2
RETURNING available;   -- zero rows means insufficient stock
```

- For multi-row operations acquire locks in a deterministic order to avoid deadlocks; use `SELECT ... FOR UPDATE SKIP LOCKED` for work queues.
- Use exact types for money (integer minor units or `numeric`), never floating point.

## 3. Concurrency control

- **Optimistic concurrency**: each mutable row has a `version` (or `updated_at` used carefully). The update includes `WHERE id = $1 AND version = $2`; zero rows updated means a conflict. Expose it through `ETag` and `If-Match`, returning `412` or `409` so the client can refetch and let the user resolve or retry.
- **Pessimistic locks** (`FOR UPDATE`) for short, high-contention critical sections where retries would thrash.
- **Hot rows** (flash-sale stock, popular coupon): shard the counter across several rows and sum them, use a reservation queue or admission control, or serialize through a single worker per key. Autoscaling does not fix row contention.
- **Uniqueness**: rely on unique indexes plus handling the violation, not on check-then-insert.

## 4. Idempotency

Every operation reachable by retry (client retry, queue redelivery, webhook redelivery, user double-click) must produce the same final state as a single execution.

- **API commands**: `Idempotency-Key` header, stored with request hash and response. Scope keys per user and operation. Same key with a different body is an error.
- **Natural idempotency**: prefer `PUT` semantics and set-state operations ("set status to shipped") over increments ("add one").
- **Event consumers**: record processed event IDs in an inbox table inside the same transaction as the side effect; skip duplicates.
- **Webhooks**: verify signature and timestamp, dedupe by provider event ID, tolerate out-of-order delivery by checking current state before applying.
- **Client side**: generate the idempotency key (or the entity ID) before the first attempt and reuse it on every retry of the same user intent. Disable the submit control while pending.
- **External calls**: pass the provider's idempotency key; store provider request IDs for reconciliation.

## 5. Transactional outbox and inbox

Problem: updating the database and publishing an event are two writes; a crash between them loses or invents events.

Solution:

1. In the same database transaction as the state change, insert the event into an `outbox` table.
2. A relay (poller with `SKIP LOCKED`, or change data capture such as Debezium) publishes outbox rows to the broker and marks them sent. Delivery is at-least-once.
3. Consumers dedupe with an `inbox` table (processed event ID plus the side effect in one transaction) so processing is effectively once.

Event rules: stable event ID, type, schema version, timestamp, producer, aggregate ID and version, correlation and causation IDs, minimal payload without secrets. Partition by aggregate ID when per-entity ordering matters. Consumers tolerate duplicates and out-of-order events (compare aggregate versions). Provide dead-letter queues, replay, and a reconciliation job for anything that must not drift.

## 6. Sagas for multi-step workflows

Distributed transactions across services are not available; model workflows as sagas.

- **Orchestration** (a coordinator holds the state machine) for workflows with many steps or important visibility, such as checkout. **Choreography** (services react to events) for simple, loosely coupled flows.
- Each step is idempotent and has a compensating action where a rollback is needed (release reservation, void authorization, refund). Compensation is a new forward action, not an undo of history.
- Persist saga state durably with explicit states and transitions; add timeouts for every waiting state and a sweeper that resolves stuck sagas.
- Uncertain outcomes (payment provider timed out) are reconciled by querying the provider before retrying or releasing resources.
- Never infer failure from a client timeout alone.

Example checkout state machines kept independent: order (`PENDING`, `CONFIRMED`, `CANCELLED`), payment (`CREATED`, `AUTHORIZED`, `CAPTURED`, `FAILED`, `REFUNDED`), reservation (`HELD`, `COMMITTED`, `RELEASED`, `EXPIRED`).

## 7. Replicas, read-your-writes, and staleness

Read replicas improve capacity and availability but lag.

- Send reads that must see the latest data (right after a write, order or payment status, permission checks) to the primary.
- To provide read-your-writes after a write: pin that user's reads to the primary for a short window, or return a version or log position in the write response and have reads wait for or require a replica at least that fresh, or have the client keep the written value in its cache (optimistic state) until the read model catches up.
- Monotonic reads: avoid a user flipping between a fresh and a stale replica; use sticky routing for a session where it matters.
- Eventually consistent projections (search, feeds) show a "pending" or fresh-local state for the user's own changes so the UI does not appear to lose them.
- Monitor replication lag and projection lag; alert and degrade (route to primary, hide the stale feature) beyond thresholds.

## 8. Distributed locks and coordination

- Prefer constraints, conditional updates, and queues over locks.
- If a lock is unavoidable (singleton scheduled job, leader election), use a lease with a TTL and fencing tokens so a paused holder cannot corrupt state after it lost the lock. A bare Redis `SET NX` lock is not safe for correctness-critical sections.
- Use database advisory locks or a coordination service (etcd, ZooKeeper, cloud-native leader election) where correctness matters.
- Make scheduled jobs safe to run twice.

## 9. Availability: SLOs, redundancy, degradation, recovery

- **Set SLOs** per user journey (for example checkout availability 99.9 percent, p95 latency under a stated target) with error budgets. Measure from the user's side.
- **Remove single points of failure**: multiple replicas across availability zones, managed database with automatic failover, redundant caches and brokers, health-checked load balancing.
- **Stateless services** so any replica can serve any request; keep session state in tokens or Redis.
- **Graceful degradation**: classify features as critical or optional. Optional features (recommendations, reviews summary, analytics, suggestions) have timeouts and fallbacks and never block the critical path.
- **Overload protection**: rate limits, concurrency limits, load shedding, bounded queues, circuit breakers.
- **Safe deploys**: readiness probes, graceful shutdown (stop accepting, drain in-flight requests, then exit), progressive rollout, automatic rollback, backward-compatible migrations (expand, migrate, contract).
- **Data protection**: automated backups, point-in-time recovery, periodic restore tests, defined RPO and RTO that have been exercised.
- **Multi-region** only when a concrete requirement exists; it multiplies consistency complexity.
- **Runbooks and alerts** for each failure mode you identified, with owners.

## 10. Time, ordering, and IDs

- Never rely on client clocks for ordering or conflict resolution. Use server-assigned versions, sequence numbers, or logical clocks.
- Store timestamps in UTC; convert at the edge. Keep both a business timestamp and a server receipt time where it matters.
- Use time-sortable unique IDs (UUIDv7, ULID) generated by whoever creates the entity, which also enables offline creation and idempotent retries.
- Do not use wall-clock timestamps as sync cursors; use monotonic sequence numbers or opaque cursors.

## 11. Background jobs

- Use a durable queue (Postgres-backed, Redis streams with acknowledgements, SQS, Kafka) with at-least-once delivery, visibility timeouts, bounded retries with backoff, and a dead-letter queue.
- Jobs are idempotent and carry the data or IDs needed to rerun them; payloads are small and versioned.
- Separate worker pools by priority so bulk work cannot starve critical jobs.
- Schedule recurring work with leader election or a scheduler that guarantees single execution, and make the job safe if it overlaps.
- Surface job health: queue depth, age of oldest job, failure rate, DLQ size, with alerts.

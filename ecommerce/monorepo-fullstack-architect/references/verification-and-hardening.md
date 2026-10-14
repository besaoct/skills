# Verification and hardening

## Contents
1. The loophole checklist
2. Test strategy
3. Load, stress, and failure testing
4. Observability that proves it works
5. Definition of done
6. Honest reporting

## 1. The loophole checklist

Walk each item against the real design and code. For every "no" or "not sure", fix it or record the risk with an owner.

**Duplicates and retries**
- If the client sends the same state-changing request twice, is the result identical to sending it once?
- If a queue or webhook redelivers an event, is the effect applied once?
- Does a user double-click or flaky network retry produce a second order, charge, email, or reward?

**Partial failure**
- If the process crashes between "database updated" and "event published" (or "payment captured" and "order confirmed"), does the system recover without manual repair?
- Are there stuck states (pending forever) with a sweeper, timeout, and alert?
- When an external provider times out, do we reconcile before retrying or releasing resources?

**Concurrency**
- Can two concurrent requests both pass a check and both write (oversell, double redeem, double spend, overbooking)?
- Are invariants enforced by constraints or atomic statements, not by check-then-write in code?
- Is there a hot row or hot key that serializes the whole system under load?

**Staleness and caching**
- Can any cache serve stale data to a decision that should be strong (price at checkout, stock, permission, balance)?
- Can one user ever receive another user's cached response?
- What happens on a cold cache, a cache outage, and a stampede on one expiring key?
- After a write, does the user see their own change (read-your-writes), including through replicas and projections?

**Authorization and trust**
- Is authorization checked server-side on every endpoint and every object (including IDs in the URL and body, bulk endpoints, exports, and sync pushes)?
- Does the server recompute price, discounts, totals, and permissions rather than trusting the client?
- Are tenant boundaries enforced in queries, caches, search, and events?
- Are secrets absent from the repo, logs, client bundles, and error messages?

**Time and ordering**
- Do any decisions depend on client clocks or on wall-clock ordering across machines?
- Are events consumed correctly when duplicated or out of order?
- Are time zones and daylight saving handled at the edges, with UTC stored?

**Client and server agreement**
- Can a deployed old client talk to the new server (and the reverse during rollout) without breaking?
- Does the client handle unknown fields, unknown enum values, and every documented error code?
- Are responses validated where a wrong shape would cause harm?

**Overload and dependencies**
- Does every outbound call have a timeout, bounded retries with jitter, and a circuit breaker?
- Are queues, pools, and request sizes bounded?
- Do optional features fail soft?
- What happens if the database, cache, queue, or search is down, slow, or returning errors?

**Data lifecycle**
- Are migrations backward compatible with the previous release running simultaneously?
- Can every derived store (cache, index, read model) be rebuilt, and has the rebuild been tested?
- Do backups restore, and has a restore been rehearsed?
- Are retention, deletion, and privacy requirements implemented, including in logs, caches, and device storage?

**Offline and sync (if applicable)**
- Is every mutation idempotent by `mutationId`?
- Are conflicts detected by version, not timestamps, with a defined resolution per entity?
- Are there protections against poison mutations, expired cursors, and device schema migrations?

**UX integrity**
- Does every failure above have a user-visible, understandable state with a recovery action?
- Is user input preserved across errors, expired sessions, and reloads?
- Is it always clear whether an action is pending, saved, synced, or failed?

## 2. Test strategy

Match the test to the risk.

| Level | What it proves | Examples |
|---|---|---|
| Unit | Domain rules, state machines, pricing math, conflict resolvers | Illegal state transitions rejected; rounding rules |
| Integration | Real database and cache behavior | Constraints hold; transactions roll back; cache invalidation after commit; outbox publishes |
| Contract | Client and server agree | Responses validate against OpenAPI; breaking-change diff; event schema compatibility |
| Concurrency | No races | N parallel purchases of the last unit yield exactly one success; coupon limit holds |
| Idempotency and replay | Safe retries | Same `Idempotency-Key` twice; webhook replay; event redelivery |
| Failure injection | Resilience | Kill a dependency mid-request; add latency; drop packets (Toxiproxy, chaos tooling) |
| End to end | The user journey works | Browser test of the main flows, including an error path |
| Accessibility and visual | Usable by everyone | Automated a11y checks; keyboard path for core flows |
| Offline and sync | Convergence | Scenarios in `offline-first-and-sync.md` section 10 |
| Security | Basic abuse resistance | Authorization tests per role and per object; input fuzzing on key endpoints; dependency and secret scanning |

Use real Postgres and Redis in integration tests (Testcontainers or Compose) rather than mocks for anything involving transactions, locking, or caching semantics. Keep tests deterministic: inject clocks and random sources, avoid sleeps, seed data explicitly.

## 3. Load, stress, and failure testing

Do this with a tool such as k6, Gatling, or Locust against a production-like environment.

1. Write down workload assumptions (users, requests per second per endpoint, read and write mix, data size) and the SLOs to meet.
2. Load test to expected peak and verify latency percentiles, error rate, and saturation (CPU, connections, queue lag, cache hit ratio).
3. Stress beyond peak to find the first bottleneck and confirm the system degrades gracefully (shedding, backpressure) rather than collapsing.
4. Soak test for hours to find leaks and slow degradation.
5. Spike test for sudden bursts (campaign launch).
6. Contention test on hot keys and rows.
7. Failure test: kill a replica, fail over the database, drop the cache, slow a dependency; confirm SLOs and recovery.
8. Record results, fix the first bottleneck, and repeat. Report only numbers you measured, with the environment they were measured in.

## 4. Observability that proves it works

- Structured logs with correlation IDs across client, gateway, services, queues, and jobs.
- Metrics: request rate, errors, and duration (RED) per endpoint; saturation (USE) per resource; cache hit ratio and evictions; queue depth and age; outbox lag; replication lag; sync success and conflict rates; client-side web vitals and API error rates.
- Distributed traces through every hop, including async boundaries (propagate trace context in messages).
- Business metrics that reveal silent failures: orders created versus paid, duplicate prevented counts, stuck workflow counts, reconciliation mismatches.
- Alerts tied to SLO burn rate and to the specific failure modes in the checklist, each with a runbook.
- Health endpoints: liveness (process is up) and readiness (dependencies reachable, migrations applied).

## 5. Definition of done

A feature or system is done when all of these are true and evidenced:

- Contract defined, generated types in use, contract checks green.
- Consistency choice implemented and tested for the concurrency and retry cases that apply.
- Caching policy written down, implemented, and tested for invalidation and failure.
- Client handles loading, empty, error, stale, and success; errors map to the documented codes.
- Observability in place: logs, metrics, traces, alerts, runbook entry.
- Security checks: authorization tests, input validation, no secrets exposed.
- Lint, typecheck, unit, integration, and end-to-end tests pass from a clean checkout.
- The full stack boots locally with one command and the smoke flow passes.
- Documentation updated: architecture doc, ADRs, README commands.
- Load or failure testing completed for anything with a stated SLO, or the gap is stated openly.

## 6. Honest reporting

End every build with a short report:

- What was built and where.
- Exactly which commands were run and their outcomes (pass or fail).
- What was not verified and why (for example, no load test run, no real payment provider sandbox, no device testing).
- Known limitations and risks, with the proposed mitigation.
- The recommended next step.

Do not use words like "production-ready", "scalable to N users", "fully tested", or "no loopholes" unless the evidence in the report supports them. A precise statement of what is proven and what is assumed is more valuable to the user than confidence without proof.

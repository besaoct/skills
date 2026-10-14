---
name: monorepo-fullstack-architect
description: Senior-architect skill for building a new full-stack product (or restructuring one) as a monorepo, choosing monolith, modular monolith, or microservices from the user's requirements, and wiring backend, frontend, caching, request/response contracts, consistency, availability, and optional offline-first background sync into one fast, reliable system. Use this skill whenever the user wants to start or scaffold a project, build an app or platform with a backend and frontend, set up a monorepo, decide between monolith and microservices, design APIs, caching, sync, or offline support, or asks for something optimized, production-grade, scalable, fast, or consistent, even if they never say "architecture" or "monorepo".
---

# Monorepo Full-Stack Architect

You are acting as a senior architect who owns the whole system: repo layout, services, data, the API contract, the client's data layer, and the UX that results from all of it. The job is a product that is fast, available, and consistent, with no gaps between what the backend guarantees and what the frontend assumes.

Most real failures happen at seams: a cache that serves stale money data, a retry that double-charges, an optimistic UI that never rolls back, an offline queue that replays the same mutation twice. Spend your effort there. Choose boring, proven techniques, name the trade-off for every decision, and verify by running things.

Related skills in this collection: `production-commerce-base-and-security-concerns` covers commerce domains, payments, and security controls in depth. `production-ui-ux-and-centralized-styling` covers the visual system. Use them alongside this one when the project is a commerce product or has a UI.

## How to work

Follow these phases in order. Skip a phase only when the existing project already answers it.

### Phase 0: Inspect before deciding

If a repo already exists, read it first: package manager, workspace tool, frameworks, services, schemas, CI, conventions. Extend what is there rather than introducing a second system. A greenfield project skips this.

### Phase 1: Intake (requirements that drive the architecture)

Gather the answers below from the user's request. Ask at most a few short questions for the ones that would change the design and cannot be inferred; for everything else, state an assumption explicitly and move on. Do not stall the build on a long questionnaire.

| Question | Why it matters |
|---|---|
| What is the product, and who are the users (consumers, staff, partners)? | Domain boundaries, auth model |
| Expected scale: users, peak requests per second, data volume, growth horizon | Monolith vs services, datastore choices |
| Team size and ownership model | Services follow teams, not the reverse |
| Platforms: web, iOS/Android, desktop, public API | Client data layer, offline options |
| Connectivity of real users: reliable, flaky, often offline? | Offline-first decision |
| Which data is money, stock, identity, or legally sensitive? | Strong-consistency set |
| Real-time needs: live updates, collaboration, notifications | Transport (SSE, WebSocket, polling) |
| Compliance and data residency | Isolation, retention, regions |
| Existing stack, cloud, and skills of the team | Stack follows the team |
| Budget and time horizon | How much infrastructure is justified now |

If the user gave no numbers, assume a modest scale, say so, and design so the first version can grow without a rewrite (clean module boundaries, contract-first APIs, an outbox for events). Never invent benchmarks or claim capacity you have not measured.

### Phase 2: Decide and record

Make each decision below explicitly, then write a short Architecture Decision Record for it in `docs/adr/` (template in `references/architecture-decisions.md`). A decision without a recorded reason gets re-litigated or silently reversed.

**1. Architecture style.** Default to a modular monolith unless the requirements show a concrete reason to split. Microservices cost distributed transactions, network failure modes, and operational load, so they must earn their place.

- Monolith or modular monolith: one team or a few, one deploy unit is acceptable, domain still evolving, scale reachable with vertical plus horizontal replicas of one process.
- Microservices: independently scaling hot paths, separate team ownership, strong fault isolation needs, different runtimes for good reason, or compliance isolation.
- Hybrid is common and good: a modular monolith core plus a few extracted services for the genuinely different workloads (search, media, notifications, payments adapters).

The user's explicit choice always wins; if they ask for microservices, build them well and note any risks you see. Details and layouts: `references/architecture-decisions.md`.

**2. Consistency map.** For every write path, label it strongly consistent or eventually consistent and say why. Money, stock, uniqueness, permissions, and identity are strong by default. Feeds, counters, search, and analytics tolerate eventual. Details: `references/consistency-and-availability.md`.

**3. Offline and sync mode.** Choose one and record it:

- **Online-first**: network assumed, cache for speed only. Default for dashboards, admin tools, checkout-centric flows.
- **Offline-tolerant**: cached reads and queued low-risk writes, but critical writes (payments, stock claims) require a live connection and give a clear message otherwise.
- **Offline-first / local-first**: the local database is the working source of truth, the server syncs in the background. Choose when users lose connectivity routinely (field work, POS, low-connectivity markets, mobile-first apps), when losing a user's input is unacceptable, or when instant local response is the core experience.

Offline-first adds real complexity (conflict resolution, schema migration on devices, tombstones, resync). Do not add it by reflex, and do not skip it when the requirements call for it. Decision rubric and protocol: `references/offline-first-and-sync.md`.

**4. API style and contract.** REST with OpenAPI for most APIs, gRPC for internal calls with a measured reason, GraphQL only when client-driven query shape is a real requirement. Contract first: the schema is the source of truth, and types, validators, and clients are generated from it. Details: `references/frontend-backend-contract.md`.

**5. Data and caching.** One authoritative store per piece of data, caches are derived. Pick layers from `references/caching-and-http.md` and justify each one by the access pattern it serves.

**6. Real-time transport.** Server-to-client only: SSE. Bidirectional or high frequency: WebSocket. Otherwise polling with backoff. Always design resume and fallback.

### Phase 3: Scaffold the monorepo

Create the workspace skeleton, shared packages, standard scripts, local dev environment, and CI before feature code, so every service and app is built, tested, and run the same way. Layout, tooling, boundary enforcement, and CI: `references/monorepo-scaffold.md`.

Non-negotiables for the scaffold:

- One command each for install, dev, lint, typecheck, test, build, from the repo root.
- Enforced module boundaries (lint rule or tooling), not a convention in a README.
- A shared contracts package that both backend and frontend import.
- Local dependencies (database, cache, queue) start with a single command and have health checks.
- Config validated at startup; the process refuses to boot on invalid config.

### Phase 4: Build in vertical slices

Build one thin end-to-end slice first (for example, "list items, create an item, see it update"), prove the whole path including caching, errors, and sync, then widen. Each slice, backend to UI, includes:

1. Contract: schema, error shapes, pagination, idempotency, caching headers.
2. Service logic with the consistency choice implemented (transaction, constraint, version check, outbox event).
3. Cache policy with an invalidation story, written down.
4. Client data layer using the generated client, with loading, empty, error, and retry states.
5. Observability: structured logs with correlation IDs, metrics, traces, health endpoints.
6. Tests at the right levels (unit for rules, integration for the database and cache, contract tests at the seam, one end-to-end path).

### Phase 5: Harden against loopholes

Walk the failure checklist in `references/verification-and-hardening.md` against what you built: duplicate requests, retries, partial failure, stale reads, concurrent writers, cache stampede, replica lag, clock skew, expired sessions mid-flow, queue replays, schema drift between client and server, and oversize inputs. Fix gaps in the design rather than documenting them away.

### Phase 6: Verify by running it

"Works perfectly" is a claim that needs evidence. Before saying anything is done:

- Install from clean, build everything, run lint, typecheck, and tests.
- Boot the full stack locally and hit the health endpoints.
- Exercise the main flow end to end, including at least one failure path (dependency down, duplicate submit, offline then reconnect if the app is offline-capable).
- Report exactly what you ran and what passed. If something could not be run, say so plainly. Never write "tested" or "production-ready" for things you did not verify.

## Core engineering rules (the reasons behind the details)

- **One owner per fact.** Every piece of data has one authoritative writer. Everything else is a cache or projection that can be rebuilt. This is what keeps consistency tractable as the system grows.
- **Cache for a reason.** Each cache layer must name the read pattern it accelerates, its TTL or invalidation trigger, its stampede protection, and what happens when it is empty or down. Personalized or money-critical data is never served from a shared cache.
- **Assume the network lies.** Requests time out, arrive twice, arrive late, or succeed without the client hearing back. Every state-changing operation is idempotent or carries an idempotency key; every client call has a timeout, bounded retries with jittered backoff, and a defined user-visible outcome.
- **Contracts over conventions.** If the client and server can disagree, they eventually will. Generate types and validate at runtime at every trust boundary.
- **Fast is perceived and real.** Cut real latency (indexes, caching, payload size, fewer round trips) and perceived latency (optimistic updates, skeletons only where useful, prefetching, instant local response). Budget both.
- **Degrade, do not collapse.** Decide up front which features are optional (recommendations, analytics, search suggestions) and make them fail soft so the core flow survives their outage.
- **Measure before optimizing, and again after.** Set latency and availability targets, instrument, and compare. Avoid complexity added for an imagined load.
- **UX is part of the architecture.** Every failure mode has a user-facing state: pending, synced, failed with retry, conflict needing a choice, offline. If the backend can fail in a way the UI cannot express, the design is unfinished.
- **Security is built in.** Deny by default, validate input at runtime, check authorization server-side on every request, keep secrets out of code and logs. For commerce specifics, apply `production-commerce-base-and-security-concerns`.

## Output expectations

For a full build, deliver working code plus:

- `docs/architecture.md`: context diagram, services or modules, data ownership, consistency map, caching map, sync mode, and known risks.
- `docs/adr/`: one record per decision from Phase 2.
- A root `README` with the exact commands to install, run, test, and deploy.
- A short final report: what was built, what was verified and how, what was not verified, and the next sensible step.

For design-only requests, return the same documents without code, with assumptions and open questions listed.

## Reference index

Read the file that matches the work in front of you; you rarely need all of them at once.

- `references/architecture-decisions.md`: monolith vs modular monolith vs microservices, extraction triggers, ADR template.
- `references/monorepo-scaffold.md`: layouts, tooling, boundaries, shared packages, local dev, CI.
- `references/caching-and-http.md`: cache layers and algorithms, HTTP caching, request/response standards, retries, rate limiting.
- `references/consistency-and-availability.md`: transactions, outbox, sagas, idempotency, concurrency control, replicas, failure handling, SLOs.
- `references/offline-first-and-sync.md`: the offline decision rubric, local storage, mutation queue, sync protocol, conflicts, background sync, UX states.
- `references/frontend-backend-contract.md`: contract-first workflow, client data layer, optimistic updates, real-time, perceived performance.
- `references/verification-and-hardening.md`: loophole checklist, test strategy, load testing, definition of done.

# Frontend and backend contract, and the UX it creates

## Contents
1. Contract-first workflow
2. Runtime validation at every boundary
3. Client data layer
4. Mutations and optimistic updates
5. Error mapping and states
6. Real-time updates
7. Authentication flow between client and server
8. Perceived performance and Core Web Vitals
9. Backend-for-frontend (BFF)
10. Contract change management

## 1. Contract-first workflow

The schema is the source of truth; code follows it.

1. Design the endpoint in OpenAPI (or Protobuf for gRPC) inside `packages/contracts`: paths, request and response schemas, error shapes, pagination, caching and idempotency headers.
2. Generate artifacts from it: TypeScript types, runtime validators (for example Zod or Valibot), and a typed client (for example openapi-typescript with a fetch wrapper, orval, or a generated SDK). Generate server stubs or validators too where the framework supports it.
3. Implement the server against the generated types; it fails to compile when it drifts from the contract.
4. Implement the client against the generated client; it fails to compile when the contract changes incompatibly.
5. Contract tests in CI: the server's actual responses validate against the schema, and breaking-change detection (for example `oasdiff`) compares against the main branch.

Where the backend and frontend are both TypeScript and one team owns both, an end-to-end typed RPC layer (tRPC or similar) is acceptable for internal APIs. Keep a REST and OpenAPI surface for anything public, partner-facing, or consumed by non-TypeScript clients.

## 2. Runtime validation at every boundary

Types disappear at runtime. Validate:

- Incoming requests on the server (reject with `422` and field errors).
- Responses on the client in development and in tests, and at least at critical boundaries in production (payment results, auth tokens, sync payloads), because a drifted server or a proxy can send anything.
- Webhook, queue, and import payloads.
- Local persisted data after migration.

Share schemas between client and server through `packages/contracts` so a rule (maximum length, allowed values) lives in one place and the form validation matches the server's.

## 3. Client data layer

Use a server-state library (TanStack Query, SWR, RTK Query, Apollo) rather than hand-rolled `useEffect` fetching. Define conventions once:

- **Query keys**: structured and hierarchical (`['orders', 'list', filters]`, `['orders', 'detail', id]`) produced by key factories, so invalidation is precise.
- **Freshness**: per data type `staleTime` and `gcTime` chosen from the server's cache policy. Rarely changing reference data: long. Live status: short or push-driven. Money-critical views: always revalidate on mount.
- **Request dedupe and cancellation**: library handles dedupe; pass `AbortSignal` so navigation cancels in-flight requests.
- **Prefetching**: prefetch on hover, focus, route intent, and during idle time for the likely next screen; prefetch on the server for first paint.
- **Pagination**: infinite scroll or paged queries with cursors from the API; keep previous data visible while the next page loads.
- **Retry**: library retries with backoff for idempotent reads only; mutations retry only with idempotency keys.
- **Persistence**: persist selected queries (for example with `persistQueryClient` to IndexedDB) for offline-tolerant apps, with a cache buster tied to the app and schema version, and never persist sensitive responses without a policy.
- **Single API client module** that attaches auth, `X-Request-Id`, locale, `Idempotency-Key` for flagged calls, handles `401` refresh once, honors `Retry-After`, and normalizes errors into one error type.
- **Server rendering**: for SEO or first-paint speed, fetch on the server, hydrate the client cache from it, and avoid duplicate fetching after hydration.

Do not duplicate server state into global client stores (Redux, Zustand). Use them for true client state (UI preferences, wizard steps), and let the query cache own server data.

## 4. Mutations and optimistic updates

Pattern for user actions that should feel instant (toggle, reorder, add to cart, edit a field):

1. Generate the idempotency key or entity ID once per user intent.
2. Cancel in-flight queries for the affected keys, snapshot the previous cache value.
3. Apply the optimistic change to the cache so the UI updates immediately.
4. Send the request. On success, reconcile the cache with the server's response (it may differ: price, version, normalized text).
5. On failure, roll back to the snapshot and show a message with a retry action. On conflict (`409` or `412`), refetch and offer the user a resolution.
6. Invalidate or refresh the related queries afterwards so derived views converge.

Guidance:

- Use optimistic updates where failure is rare and recoverable. For payments, order placement, and irreversible actions, show a clear pending state and wait for the server.
- Disable the submit control and show progress while pending; this prevents double submissions at the UI, while the idempotency key protects at the server.
- Preserve user input on failure. Never clear a form because a request failed.
- Show the server-confirmed state when it matters (totals, tax, availability); show the optimistic state for low-stakes presentation.
- Keep multi-step flows resumable: persist the draft (server-side or local) so refreshes and network drops do not lose progress.

## 5. Error mapping and states

Every backend failure has a defined UI outcome. Maintain one table in the contracts package:

| Server signal | Client behavior |
|---|---|
| `401` | Try refresh once, then route to sign-in preserving the return path and unsaved input |
| `403` | Permission-denied state, no retry |
| `404` | Not-found state |
| `409` with a `code` (for example `OUT_OF_STOCK`) | Domain-specific message and recovery action |
| `412` / version conflict | Refetch, show what changed, let the user reapply |
| `422` with `errors[]` | Field-level messages next to inputs, focus the first invalid field |
| `429` | Respect `Retry-After`, show a calm "try again shortly" |
| `5xx` / network | Retry control, keep stale data visible if available, report with `traceId` |
| Offline | Offline state; queued actions where supported |

Each screen implements five states: loading, empty, error, partial or stale (with a refresh indicator), and success. Use skeletons only when the shape of content is known and loading exceeds a perceptible delay; avoid layout shifts when data arrives. Errors for users are written in plain language with a next step; the `traceId` is available for support but not the headline.

## 6. Real-time updates

- **SSE** for one-way server push (notifications, status, live counters): simple, works over HTTP/2, auto-reconnects, supports `Last-Event-ID` to resume. Prefer it when the client only listens.
- **WebSocket** for bidirectional or high-frequency interaction (chat, collaboration, live trading). Add heartbeats, backoff reconnect with jitter, auth on connect and on token refresh, and message acknowledgements where loss matters.
- **Polling** with adaptive intervals and backoff as the universal fallback; pause when the tab is hidden.
- Treat real-time messages as invalidation hints that trigger a refetch, or as small patches applied to the cache, with sequence numbers to detect gaps. On gap or reconnect, resynchronize through the normal API so the client cannot drift.
- Fan out through a broker (Redis pub/sub or streams, NATS, Kafka) so any replica can serve any connection; keep connection state out of process memory where possible, and cap connections per user.

## 7. Authentication flow between client and server

- Browser apps: short-lived access token plus rotating refresh token in `HttpOnly`, `Secure`, `SameSite` cookies, with CSRF protection for cookie-authenticated mutations. Avoid long-lived tokens in local storage.
- Mobile: tokens in Keychain or Keystore; refresh with rotation and reuse detection.
- A single refresh in flight at a time on the client (queue other requests behind it), then replay the original request once.
- Authorization is enforced on the server for every request and resource; the client hides UI for convenience only.
- Session expiry mid-flow preserves user input and returns the user to where they were.
- Logout clears caches (query cache, local databases, service worker caches that hold private data).

## 8. Perceived performance and Core Web Vitals

Targets to set and measure per route: LCP, INP, CLS, plus time to first byte and API p95.

Techniques:

- Render critical content on the server or at build time; stream where the framework supports it; defer nonessential widgets (recommendations, chat) until after first paint.
- Reserve space for images and dynamic content to avoid layout shift; serve responsive, modern image formats from a CDN.
- Split bundles by route; keep admin code out of the storefront bundle; audit third-party scripts and load them after interaction or idle.
- Prefetch the next likely route and its data; use `preconnect` for critical origins.
- Show something meaningful immediately (cached data, local data, skeleton with the right shape), then refresh quietly.
- Keep interactions under the INP budget: avoid long main-thread tasks, debounce expensive handlers, move heavy work to workers.
- Reduce chattiness: one aggregated request per screen from a BFF beats many small calls over mobile networks.
- Track real-user metrics by route, device class, and region; set budgets in CI.

## 9. Backend-for-frontend (BFF)

Add a BFF when different clients need different shapes, when one screen needs data from several services, or when you need to hide internal topology.

- It composes calls in parallel with timeouts and partial-failure tolerance (optional sections degrade, the page still renders).
- It owns response shaping and client-specific caching, not business rules (those stay in domain services).
- One BFF per client type if their needs diverge significantly; avoid a catch-all that becomes a second monolith.

## 10. Contract change management

- Additive changes (new optional fields, new endpoints) are safe within a version. Removing or changing meaning of fields is breaking.
- Expand and contract: add the new field, migrate clients, then remove the old one after the deprecation window, announced with `Deprecation` and `Sunset` headers.
- Clients tolerate unknown fields and unknown enum values (fall back gracefully) so servers can evolve.
- Mobile and installed clients live for years: define a minimum supported version, expose it through a config endpoint, and show a clear update prompt when needed.
- Feature flags gate rollout of new contract usage; flags are removed on schedule.

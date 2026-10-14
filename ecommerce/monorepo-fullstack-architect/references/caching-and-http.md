# Caching, requests, and responses

## Contents
1. Cache layers and when to use each
2. Cache algorithms and patterns
3. Invalidation strategies
4. HTTP caching headers
5. Request and response standards
6. Client-side resilience: timeouts, retries, circuit breakers
7. Rate limiting and backpressure
8. Performance levers beyond caching
9. Cache design checklist

## 1. Cache layers and when to use each

Add a layer only when it serves a measured or clearly predictable read pattern. Each layer needs an owner, a TTL or invalidation trigger, and an empty-cache story.

| Layer | Good for | Avoid for |
|---|---|---|
| Browser HTTP cache and service worker | Static assets (immutable, hashed filenames), rarely changing public data | Personalized or money-critical data |
| CDN / edge | Public pages, images, media, public API responses, static JSON | Anything per-user unless keyed safely; responses with `Set-Cookie` |
| Client data cache (TanStack Query, SWR, Apollo, RTK Query) | Avoiding refetch, deduping in-flight requests, instant navigation | Being the source of truth for server state |
| Application in-process cache (LRU) | Tiny hot lookups, config, feature flags, per-request memoization | Data that must be consistent across replicas |
| Distributed cache (Redis) | Hot reads shared across replicas, sessions, rate limit counters, computed fragments | Authority for money, stock, or uniqueness |
| Database query tuning (indexes, covering indexes, materialized views, read replicas) | The real fix for slow queries | Used instead of fixing an N+1 |
| Search index / read model | Full-text, facets, denormalized screens | Transactional decisions |

Order of effort: fix queries and indexes first, then cache at the cheapest effective layer. A cache over a slow, unbounded query hides the problem and makes invalidation harder.

## 2. Cache algorithms and patterns

**Cache-aside (lazy loading)**: default. Read cache, on miss read the database and populate the cache. Writers update the database, then invalidate or update the cache entry. Simple and safe.

**Write-through**: write to the store and the cache together. Use for small, hot, read-after-write sensitive entries. Requires handling partial failure (write order, retry, reconcile).

**Write-behind (write-back)**: acknowledge from the cache and persist asynchronously. High risk of data loss; avoid for anything that matters. Acceptable for counters and analytics with a durable queue.

**Stale-while-revalidate (SWR)**: serve a stale value immediately while refreshing in the background. Best default for UX on data that tolerates short staleness. Also use `stale-if-error` so an origin outage serves stale content rather than errors.

**Request coalescing (single-flight)**: when many requests miss the same key at once, only one hits the origin; the others wait for its result. Prevents stampedes (thundering herd).

**TTL jitter**: add random spread (for example plus or minus 10 to 20 percent) to TTLs so entries written together do not expire together.

**Probabilistic early refresh (XFetch)**: as an entry nears expiry, a small random fraction of requests refresh it early, so expiry never causes a synchronized miss on very hot keys.

**Negative caching**: cache "not found" results for a short TTL (seconds to a minute) to blunt enumeration and repeated misses. Keep it short so newly created items appear.

**Versioned keys (namespace versioning)**: embed a version in the key (`catalog:v7:product:42`). Invalidate a whole group by bumping the version; old entries age out. Avoids expensive key scans.

**Tag-based invalidation**: attach tags (for example `product:42`, `category:shoes`) to cached entries; invalidating a tag evicts all dependent entries. CDNs support surrogate keys; implement a tag index in Redis for app caches.

**Request-scoped memoization / DataLoader**: batch and dedupe lookups inside one request to kill N+1 patterns.

**Bloom filter in front of lookups**: for very large key spaces under hostile lookups, to avoid database hits on keys that cannot exist.

Cache key rules:

- Include everything that changes the response: resource ID, version, locale, currency, tenant, role or permission scope, and relevant query parameters in a canonical order.
- Never put a user's private data under a key shared by other users. When in doubt, key by user ID or do not cache at the shared layer.
- Set a maximum size and eviction policy (allkeys-lru or lfu) and monitor hit ratio, evictions, and memory.

When the cache is down: fall back to the origin with concurrency limits and timeouts so the database is protected; never let a cache outage become a database outage.

## 3. Invalidation strategies

Choose per data type and write it in the architecture doc.

| Strategy | Use when | Trade-off |
|---|---|---|
| TTL only | Staleness of N seconds is acceptable | Simple; users may see old data until expiry |
| Event-driven invalidation | Changes are published as events (outbox) and consumers evict or refresh | Precise and fast; needs reliable events and idempotent handlers |
| Write-path invalidation | The service that writes also evicts or updates the entry | Easy in a monolith; use after-commit hooks, not before commit |
| Version bump | Whole groups change together (publish a new catalog) | Cheap and safe; wastes memory briefly |
| Revalidation with ETags | Clients and CDNs check if content changed | Saves bandwidth, not round trips |

Rules:

- Invalidate after the transaction commits, not inside it, or a rollback leaves a wrong cache. Prefer outbox-driven invalidation when correctness matters.
- Delete beats update for races: updating a cache from a stale read can overwrite fresher data. Delete and let the next read repopulate, or use versioned values with compare-and-set.
- Combine TTL with event invalidation: events give freshness, TTL bounds the damage if an event is lost.

## 4. HTTP caching headers

Be explicit on every response; the default behavior of intermediaries is guesswork.

| Case | Headers |
|---|---|
| Hashed static assets | `Cache-Control: public, max-age=31536000, immutable` |
| Public, shared content that can be a bit stale | `Cache-Control: public, max-age=60, s-maxage=300, stale-while-revalidate=600, stale-if-error=86400` plus `ETag` |
| Per-user data, safe for the browser only | `Cache-Control: private, max-age=0, must-revalidate` plus `ETag` |
| Sensitive or transactional responses | `Cache-Control: no-store` |
| Responses varying by header | `Vary: Accept-Encoding, Accept-Language` (only headers that truly vary the output) |

Conditional requests: send `ETag` (strong, derived from content or version) and honor `If-None-Match` with `304 Not Modified`. For writes, support `If-Match` for optimistic concurrency (`412 Precondition Failed` on mismatch).

Never cache responses that set cookies or contain authorization-scoped data in shared caches unless the cache key includes the scope and it has been tested.

## 5. Request and response standards

Define these once in the contracts package and use them everywhere.

**Resource design**: nouns, plural collections, stable IDs (UUIDv7 or ULID, sortable by time), no internal database IDs exposed if they leak ordering or counts.

**Success envelope**: return the resource or a collection object directly. For collections use cursor pagination:

```json
{
  "items": [ ... ],
  "page": { "nextCursor": "opaque-string-or-null", "limit": 50 }
}
```

Use cursors (keyset pagination) rather than offsets for large or changing collections; cap `limit` server-side. Offer filtering and sorting through documented, allowlisted parameters only.

**Error format**: use RFC 9457 `application/problem+json`:

```json
{
  "type": "https://api.example.com/problems/out-of-stock",
  "title": "Item out of stock",
  "status": 409,
  "code": "OUT_OF_STOCK",
  "detail": "Only 2 units remain.",
  "traceId": "4bf92f35...",
  "errors": [{ "field": "quantity", "message": "Max 2" }]
}
```

Rules: stable machine-readable `code` values the client maps to UX copy; no stack traces, SQL, or internal IDs; `traceId` for support; field errors for validation (`422` or `400`).

**Status code discipline**: 200/201/204 success; 400/422 validation; 401 unauthenticated; 403 forbidden; 404 not found (also for unauthorized resources if existence is sensitive); 409 conflict; 412 precondition failed; 413 payload too large; 429 rate limited with `Retry-After`; 500 unexpected; 503 with `Retry-After` for planned unavailability or load shedding.

**Idempotency**: state-changing `POST` operations that must not run twice (orders, payments, transfers, message sends) require an `Idempotency-Key` header. The server stores key, request hash, status, and response for a retention window; a retry returns the stored response, a key reused with a different payload returns an error. `PUT` and `DELETE` are naturally idempotent if designed so.

**Partial updates**: `PATCH` with explicit semantics (JSON Merge Patch or JSON Patch) and `If-Match` versioning for resources with concurrent editors.

**Payload hygiene**: gzip or brotli compression, field selection or purpose-built endpoints instead of overfetching, request size limits, and server-side runtime validation of every input.

**Correlation**: accept or generate `X-Request-Id` (or W3C `traceparent`) at the edge, propagate it to every downstream call and log line, and return it in responses.

**Versioning**: `/v1` in the path or a header; additive changes only within a version; deprecations announced with `Deprecation` and `Sunset` headers.

## 6. Client-side resilience: timeouts, retries, circuit breakers

Apply to browsers, mobile clients, and service-to-service calls alike.

- **Timeouts everywhere.** Connect and total timeouts on every call. Choose from observed latency (for example slightly above p99), not defaults of 30 seconds or infinity.
- **Deadline propagation.** Pass the remaining time budget downstream so inner calls do not outlive the outer one.
- **Retries only when safe**: idempotent methods, or calls with an idempotency key. Retry on timeouts, connection errors, `502/503/504`, and `429` (respecting `Retry-After`). Never retry `4xx` validation errors.
- **Exponential backoff with full jitter**: `sleep = random(0, min(cap, base * 2^attempt))`. Cap attempts (typically 2 to 4) and total elapsed time.
- **Retry budget**: limit retries to a fraction of traffic (for example 10 percent) so a struggling dependency is not buried by retry storms.
- **Circuit breaker**: after repeated failures, stop calling for a cooldown, then allow a few probe requests (half-open). Return a fast fallback or a clear error instead of queueing up.
- **Bulkheads**: separate connection pools or concurrency limits per dependency so one slow dependency cannot exhaust all workers.
- **Hedged requests** (send a second request after a short delay) only for idempotent reads on latency-critical paths, with a cap.
- **Graceful fallbacks**: serve stale cache, a reduced response, or hide the optional feature; do not show a blank screen.

## 7. Rate limiting and backpressure

- Limit at the edge by IP and at the application by authenticated identity and by operation cost. Stricter limits on login, OTP, password reset, search suggestions, and expensive exports.
- Algorithms: token bucket (allows bursts, smooth average) for general APIs; sliding window counters for fairness; concurrency limits for expensive operations. Store counters in Redis with atomic operations (Lua script or `INCR` with expiry).
- Return `429` with `Retry-After` and rate limit headers; clients must honor them.
- **Load shedding**: when overloaded, reject low-priority work early (`503`) rather than letting queues grow without bound. Protect the critical path (checkout, auth) first.
- Bound every queue and worker pool; unbounded queues turn spikes into outages with long delays.

## 8. Performance levers beyond caching

- Indexes matched to real query plans (`EXPLAIN ANALYZE`), composite indexes ordered by selectivity and sort, partial indexes for hot subsets.
- Eliminate N+1 queries; batch and paginate; avoid `SELECT *` on wide rows.
- Connection pooling with a bounded budget (PgBouncer or the driver's pool).
- Move slow work off the request path: queue it, return `202 Accepted` with a status resource, and notify on completion.
- HTTP/2 or HTTP/3, keep-alive, compression, and CDN edge termination.
- Smaller payloads and fewer round trips: aggregate in a BFF, use purpose-built endpoints for heavy screens, prefetch likely next data.
- Precompute expensive aggregates into read models or materialized views, refreshed by events or on a schedule.
- Warm caches for known peaks (campaign launch) deliberately and test them.

## 9. Cache design checklist

For each cached item, the architecture doc answers:

1. What read pattern and measured cost does this cache remove?
2. What is the key, and does it include all response-varying inputs, including user scope?
3. What are the TTL and the invalidation trigger?
4. How is a stampede prevented (single-flight, jitter, early refresh)?
5. What is served on a miss, on cache failure, and on origin failure (stale-if-error)?
6. Can this ever be the authority for money, stock, uniqueness, or permissions? (Answer must be no.)
7. How will we observe it (hit ratio, latency, evictions, staleness)?

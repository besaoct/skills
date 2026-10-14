# Offline-first and background sync

## Contents
1. The decision rubric
2. Three modes and what each requires
3. Architecture of an offline-capable client
4. Sync protocol
5. Conflict resolution
6. Data lifecycle: tombstones, retention, resync, migrations
7. Background sync mechanics by platform
8. UX states
9. Security and privacy on devices
10. Testing offline behavior

## 1. The decision rubric

Choose the mode from requirements, then record it in an ADR. Count how many apply.

Signals for offline-first or local-first:

- Users routinely lose connectivity (field work, warehouses, POS, transport, rural or low-connectivity markets).
- Losing a user's input is unacceptable (forms, inspections, orders taken in the field, notes).
- Instant response from local data is central to the product feel (editors, task apps, messaging).
- Mobile or desktop apps are primary and can hold a local database.
- Users collaborate or work on their own data subset that is bounded in size.

Signals against (stay online-first or offline-tolerant):

- Authoritative shared state decides outcomes: stock claims, payments, seat or slot booking, auctions, limited coupons. Offline writes cannot be honored without conflict that the user cannot resolve.
- Data is large, global, or constantly changing so a local copy would be incomplete or stale.
- Strong security requires that data never rest on a device.
- The team cannot afford the testing and operational cost.

A common right answer is a hybrid: offline-first for personal and field data (drafts, notes, checklists, carts, wishlists, form submissions), online-required for authoritative operations (payment, final stock reservation), with clear UX for the boundary ("Order saved, will confirm when you are back online" is only valid if the business can honor or reject it later).

## 2. Three modes and what each requires

**Online-first**
- Client data cache (TanStack Query or equivalent) with sensible `staleTime`.
- Optional service worker caching of the app shell and static assets.
- Clear offline and error states. No local mutation queue.

**Offline-tolerant**
- Everything above plus persisted read cache (IndexedDB or SQLite) so previously viewed screens work offline.
- A small mutation queue for low-risk writes, replayed on reconnect with idempotency keys.
- Critical actions are disabled offline with an honest explanation.

**Offline-first / local-first**
- Local database is the working source of truth for the user's data; the UI reads and writes it directly and instantly.
- A sync engine reconciles with the server in the background.
- Conflict policy per entity, tombstones, resync, device-side migrations, and observability for sync health.

## 3. Architecture of an offline-capable client

```text
UI  <-->  Local store (queryable)  <-->  Sync engine  <-->  API (push / pull / realtime)
              |                              |
        schema + migrations         mutation queue (outbox) + cursors + status
```

Components:

- **Local store**: IndexedDB (via Dexie or a SQLite WASM build) on web; SQLite (drift, Room, GRDB, WatermelonDB) on mobile. Choose queryable storage, not key-value blobs, for relational data. Define a versioned schema with migrations.
- **Client-generated IDs**: UUIDv7 or ULID created at the moment of the user's action, so records can exist and relate to each other before the server has seen them.
- **Mutation queue (client outbox)**: every user write is recorded as a mutation with `mutationId`, entity, operation, payload (or patch), base version, timestamp, and attempt count, stored durably in the same local transaction as the local data change. The UI reflects the change immediately.
- **Sync engine**: a single component responsible for push, pull, retries, backoff, and status. Keep it separate from UI code, single-flight (one sync loop at a time), and resumable after app restart.
- **Sync state**: per collection, the last server cursor, last successful sync time, pending mutation count, and last error.
- **Status API for UI**: `idle | syncing | offline | error | conflict`, plus counts, so every screen can show truthful state.

## 4. Sync protocol

Design the protocol once, in the contracts package, and test it with a simulated flaky network.

**Push (client to server)**

- Endpoint accepts a batch of mutations in order: `[{ mutationId, entityType, entityId, op, patch, baseVersion, clientCreatedAt }]`.
- The server applies each mutation idempotently, recording processed `mutationId`s per client so a replay returns the earlier result and does nothing twice.
- The response gives a per-mutation result: `applied` (with new server version), `rejected` (with a reason code and the current server state), or `conflict` (with server state for resolution). One bad mutation does not poison the batch.
- Apply mutations through the same domain services and authorization checks as normal API calls. Sync is not a back door.

**Pull (server to client)**

- Server maintains a change feed per scope (user, tenant, or shared space): an append-only log with a monotonic sequence number, or per-row `serverVersion` assigned by the database.
- Client requests `GET /sync/changes?since=<cursor>&limit=N` and receives changes (including deletions as tombstones) plus the next cursor and a `hasMore` flag. Paginate until caught up.
- Cursors are opaque and server-issued. Never use device clocks as cursors.
- If the cursor is too old (compacted history) the server returns `410 Gone` with the instruction to do a full resync from a snapshot.

**Realtime nudges**

- SSE or WebSocket tells the client "something changed" (optionally with the new cursor); the client then pulls. Keep the push channel as a hint, not the data path, so missed messages cannot cause divergence. Pull on reconnect and on app foreground.

**Initial sync and partial sync**

- Download a snapshot of the user's relevant subset (bounded by scope, date range, or assignment) with progress UI, then switch to incremental changes. Do not sync entire large tables to every device.
- Prioritize what the user needs first (current view, recent items) and fetch the rest in the background.

**Efficiency**

- Batch, compress, and send only patches or changed fields.
- Back off on failure with jitter; pause on low battery or metered networks where policy says so; coalesce multiple edits to the same entity in the queue.
- Rate limit sync endpoints per client and cap batch sizes.

## 5. Conflict resolution

Decide per entity type, and write the rule down. Do not apply one global policy.

| Entity or field type | Recommended policy |
|---|---|
| Money, stock, balances, bookings, coupons | Server authoritative. Never merge offline. Reject with reason and let the user retry or choose another option. |
| User-owned single-writer data (personal notes, drafts) | Last write wins by server-assigned order; low conflict risk |
| Multi-field records edited by several people | Field-level merge: apply non-overlapping field changes, flag overlapping field conflicts |
| Sets and collections (tags, wishlist, members) | Set merge with add and remove semantics (observed-remove set or per-item operations) |
| Counters | Operation-based increments, applied additively on the server |
| Collaborative text or ordered lists | CRDT (Yjs, Automerge, Loro) or operational transformation |
| Status and workflow states | State-machine validation; reject illegal transitions and show the current state |

Mechanics:

- Detect conflicts with `baseVersion` (what the client's edit was based on) compared with the current server version, not with timestamps.
- Return conflicts with both the server state and the rejected change so the client can auto-resolve per policy or ask the user.
- Keep a visible conflict inbox for cases that need a human; never silently discard a user's edit.
- Deletes versus edits: define the winner (usually delete wins with tombstone, or restore on conflicting edit) per entity.
- Log resolved conflicts with enough metadata to debug and audit.

## 6. Data lifecycle: tombstones, retention, resync, migrations

- **Tombstones**: deletions sync as records (`deletedAt`, version). Keep them long enough for devices that were offline to catch up (for example 30 to 90 days) and define what happens beyond that window (full resync).
- **Compaction**: collapse old change-log history periodically; clients behind the compaction horizon get `410` and resync from a snapshot.
- **Device migrations**: local schema migrations run on app start, are tested from every supported prior version, and are resumable. If a migration fails, fall back to clearing the local store and resyncing, but never before pending mutations are safely preserved or the user is warned.
- **Server schema evolution**: changes to synced entities are additive and versioned; old clients continue to work for a defined support window; a minimum supported client version triggers a forced update screen when needed.
- **Pending mutations across versions**: mutations in the queue carry a schema version so the server can upgrade them.
- **Poison mutations**: a mutation that is permanently rejected is moved to a failed list with the reason and surfaced to the user, not retried forever, and does not block the rest of the queue (or blocks only mutations on the same entity).

## 7. Background sync mechanics by platform

| Platform | Mechanism | Caveats |
|---|---|---|
| Web | Service worker plus Workbox for asset caching; Background Sync API (`sync` event) where available; always also sync on `online` event, page visibility change, and app start | Background Sync is not universally supported (notably Safari), and periodic sync is limited; treat it as an enhancement and keep foreground triggers as the baseline |
| iOS | Background tasks (BGAppRefreshTask, BGProcessingTask), silent push, URLSession background transfers | System decides timing; do not promise real-time background sync |
| Android | WorkManager with network constraints and backoff, FCM data messages | Doze and battery policies delay work; use expedited work sparingly |
| Flutter | `workmanager` plugin plus drift/sqflite local DB, `connectivity_plus` for hints | Same OS limits apply underneath |
| Desktop | App-owned background loop with the same engine | Straightforward; respect sleep and network changes |

Always combine triggers: app start, foreground, connectivity restored, after each local write (debounced), periodic while active, and push-driven nudges. Do not rely on a single trigger. Treat `navigator.onLine` as a hint only; confirm with a real request.

## 8. UX states

Offline behavior is a design deliverable. Provide, consistently (see the UI skill for styling):

- A global, calm connectivity and sync indicator: online and synced, syncing, offline (changes saved on this device), sync failed with retry.
- Per-item state for pending writes ("Saved on device", "Waiting to sync", "Failed. Tap to retry"), with something other than color alone.
- Immediate local response to actions; no spinner for local operations.
- Disabled-with-explanation states for actions that need the server ("Payment requires a connection").
- A conflict resolution flow that shows both versions, lets the user pick or merge, and does not lose data.
- Clear first-run behavior: what is downloaded, how much, and what works offline.
- Storage and cache management: show usage, allow clearing, handle quota errors gracefully.
- Never show a success state for something the server later rejects without telling the user what happened and how to fix it.

## 9. Security and privacy on devices

- Local data is exposed if the device is lost; store only what is needed, and encrypt sensitive stores (SQLCipher, OS keystore-protected keys, WebCrypto with non-extractable keys where feasible).
- Tokens live in secure storage (Keychain, Keystore, HttpOnly cookies), not in plain local storage.
- Wipe local data on logout and on account removal; support remote revoke where required.
- Offline authentication is a design decision: define how long cached credentials remain valid and which actions are allowed with an expired session; re-authenticate before syncing sensitive mutations.
- The server remains the authority: re-validate every pushed mutation for authorization and business rules.

## 10. Testing offline behavior

Include these in the test plan; they are where offline-first systems fail:

- Create, edit, and delete offline, then reconnect: final state correct and no duplicates.
- Kill the app mid-sync and mid-write; restart; no lost or double-applied mutations.
- Same mutation sent twice (retry after lost response): applied once.
- Two devices editing the same entity offline: conflict policy produces the documented result.
- Cursor expiry and forced full resync.
- Clock skew on the device (wrong date) does not break ordering.
- Slow, lossy, and flapping networks (use network throttling or a proxy such as Toxiproxy).
- Local schema migration from every supported prior version.
- Server rejects a queued mutation (permission revoked, validation changed): user sees it and can recover.
- Storage quota exceeded.
- Logout with pending mutations: user is warned, data is handled according to policy.

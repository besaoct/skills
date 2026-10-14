---
name: production-commerce-base-and-security-concerns
description: A reusable architecture skill for designing, extending, securing, scaling, and operating production-grade commerce platforms, including customer storefronts, admin frontends, APIs, microservices, data systems, SEO, cloud infrastructure, and future domain extensions.
---

# Production Commerce Base and Security Concerns

## 1. Mission and scope

Use this skill as the foundational architecture standard for a production-grade e-commerce platform. It must guide the design and implementation of:

- Customer storefronts and mobile applications.
- Admin, operations, support, finance, warehouse, and merchandising interfaces.
- Public, private, partner, and internal APIs.
- Commerce domains and independently deployable services.
- Transactional data, caches, search indexes, event streams, and analytics.
- SEO, accessibility, performance, privacy, security, reliability, and operations.
- Future services and features added after the initial architecture is established.

The architecture must support extension without requiring a redesign of the platform's core. New domains may be added later, but they must use the same identity, authorization, API contracts, event conventions, observability, security controls, deployment policies, and data-ownership rules.

Do not produce a toy MVP architecture or defer essential correctness, security, SEO foundations, observability, recovery, and deployment safety. Build required foundations from day one. Sequence delivery by dependency and risk, not by omitting critical safeguards.

Do not add technologies merely for prestige. Every component must have a clear workload, authoritative owner, consistency model, operational plan, failure strategy, and measurable reason to exist.

## 2. Non-negotiable architecture principles

1. **Domain ownership:** Every business invariant has one authoritative owner. Other services interact through versioned APIs or domain events, never by directly mutating another service's tables.
2. **Polyglot by evidence:** Use TypeScript and Go intentionally. Select SQL and NoSQL databases according to access patterns and consistency requirements.
3. **Correctness before caching:** Caches and search indexes are derived or ephemeral unless a documented design proves otherwise. They must not silently become the authority for orders, payments, inventory, coupon usage, or financial balances.
4. **Explicit consistency:** Identify which operations require strong consistency and which can tolerate eventual consistency. Never leave this implicit.
5. **Partial failure is normal:** Assume timeouts, retries, duplicate events, delayed webhooks, unavailable providers, stale replicas, queue backlogs, and interrupted deployments.
6. **Security by default:** Threat-model customer, admin, service-to-service, payment, upload, integration, and automation flows.
7. **SEO by architecture:** Search engine crawlability, rendering, canonical URLs, indexation controls, structured data, redirects, and page performance are part of storefront architecture—not a final marketing task.
8. **Accessibility by design:** Customer and admin interfaces must support keyboard navigation, screen readers, semantic structure, focus management, and appropriate contrast.
9. **Operational readiness:** Include metrics, logs, traces, alerting, backups, restoration tests, deployment safety, capacity planning, runbooks, and disaster recovery.
10. **Scale from evidence:** Define workload assumptions and service-level objectives (SLOs). Do not claim capacity without repeatable load-test evidence.
11. **Extensibility without coupling:** Future modules must integrate through stable contracts, domain events, explicit permissions, and governed data ownership.
12. **Avoid unnecessary complexity:** Microservices are justified by domain boundaries, scaling needs, team ownership, or fault isolation—not by maximizing service count.
13. **Secure defaults:** Deny access unless explicitly authorized; validate all external input at runtime; minimize collected data; avoid secrets and sensitive data in logs.
14. **Reversible changes:** Use versioned APIs, backward-compatible events, expand-and-contract database migrations, progressive deployments, and documented rollback procedures.

## 3. Recommended reference stack

Treat this as a strong default, not a universal mandate. Verify current provider features, regional availability, service guarantees, quotas, compliance needs, and cost before finalizing.

### 3.1 Frontend and application layer

- **Customer web storefront:** Next.js + TypeScript, with server rendering or static generation chosen per route and freshness requirement.
- **Mobile:** Flutter where cross-platform mobile applications are required.
- **Admin and operations:** TypeScript web application, using Next.js or a suitable React application architecture.
- **Backend TypeScript:** Node.js with NestJS or Fastify, strict TypeScript, runtime schema validation, and generated API clients.
- **Go services:** Go for selected high-throughput, concurrency-sensitive, latency-sensitive, or operationally isolated services when workload benchmarks justify it.
- **API style:** REST + OpenAPI for external and most internal APIs. Use gRPC + Protobuf for internal calls where typed contracts, streaming, or measured efficiency provide a concrete benefit.
- **Frontend data access:** A typed API client, explicit loading/error/empty states, controlled cache invalidation, and server-side authorization for protected data.
- **Validation:** TypeScript types do not validate untrusted network payloads. Validate all API, webhook, queue, import, and integration payloads at runtime.

### 3.2 Data and messaging

- **PostgreSQL:** Transactional authority for orders, payment state, stock reservations, coupon redemptions, reward ledgers, and relational invariants.
- **Redis:** Hot-data caching, rate limiting, bounded ephemeral state, and carefully designed coordination. Do not rely on cache-only correctness for financial or stock operations.
- **Kafka:** Durable event streaming, replayable domain events, search indexing, analytics pipelines, and asynchronous integrations at appropriate throughput.
- **OpenSearch:** Full-text search, autocomplete, facets, filtering, and ranking. Treat indexes as rebuildable projections.
- **Object storage + CDN:** Product media, user uploads, invoices, exports, and static assets.
- **ClickHouse:** High-volume analytical queries and event analytics where justified.
- **MongoDB:** Add only when a defined document-oriented workload benefits from its data model and access patterns. Consider PostgreSQL JSONB first when suitable.
- **Data lake / warehouse:** Historical reporting and machine-learning workloads, isolated from transactional databases.
- **Schema registry or schema governance:** Version event schemas and enforce compatibility for durable event streams.

### 3.3 Infrastructure and operations

- Kubernetes, preferably managed, for workloads needing orchestration, isolation, and independent scaling.
- Terraform for infrastructure as code.
- GitOps with Argo CD or an equivalent deployment controller.
- Progressive delivery with Argo Rollouts or an equivalent canary/blue-green mechanism.
- Cloud secret manager and KMS for secrets and key management.
- OpenTelemetry for instrumentation; Prometheus and Grafana for metrics and dashboards; centralized structured logs; Sentry or equivalent error tracking.
- Managed PostgreSQL, Kafka, Redis, and search where guarantees, regional availability, team skills, and economics justify them.
- CDN, WAF, DDoS protection, bot defense, rate limiting, and API gateway at the edge.
- Container image scanning, signing, provenance, dependency scanning, and controlled artifact promotion.

Managed services still require configuration, capacity planning, access controls, monitoring, backup verification, and disaster recovery. Avoid multi-cloud unless a concrete business, resilience, or regulatory requirement justifies the additional complexity.

## 4. Reference architecture

```text
Customer web / Mobile / Admin / Partner APIs
                    |
       CDN + WAF + DDoS + Bot defense
                    |
       Load balancer + API gateway / BFF
                    |
        Kubernetes application platform
          |                       |
   TypeScript services       Go services
          |                       |
          +------ domain APIs ----+
                    |
   +----------------+-------------------+
   |                |                   |
PostgreSQL        Redis             OpenSearch
(transactional)  (cache/state)      (search projection)
   |
Transactional outbox
   |
Kafka / durable event stream
   |             |             |
Search index   Fulfillment   Notifications
projection     integrations  and engagement
   |
Analytics pipeline -> ClickHouse / warehouse / object storage

Cross-cutting platform:
Identity and policy | Secrets/KMS | Observability | CI/CD/GitOps
Audit logging | Backups/DR | Feature flags | Schema governance
```

This is a logical architecture, not a mandate to run every module as a separate cluster. Keep synchronous critical paths bounded; use events for propagation, analytics, notifications, and decoupled workflows.

## 5. Domain boundaries and ownership

Define one authoritative owner for each domain. Services may share a language or cluster without sharing database ownership.

| Domain/service | Owns |
|---|---|
| Identity | Authentication, identity lifecycle, sessions, authorization primitives |
| Customer | Profile, addresses, preferences, consent |
| Catalog | Product descriptions, variants, categories, attributes, publication state |
| Pricing | Base prices, price lists, currency, price versions |
| Cart | Customer selections, quantities, persistence, guest-to-user merge rules |
| Wishlist | Saved items and wishlist operations |
| Promotion | Campaign rules, coupon eligibility, stacking, usage limits, discount budgets |
| Inventory | Stock ledger, warehouse quantities, reservations, allocation, release |
| Checkout | Workflow orchestration, checkout quote, delivery selection and validation |
| Orders | Order lifecycle, immutable line-item snapshots, cancellation workflow |
| Payments | Provider integration, payment attempts, webhook verification, reconciliation |
| Shipping | Serviceability, shipping rates, shipment creation and tracking |
| Returns | Return eligibility, inspection, exchange and refund initiation |
| Referral and loyalty | Attribution, reward ledger, eligibility, redemption and reversals |
| Reviews and trust | Reviews, ratings, moderation, verified-purchase status |
| Notifications | Transactional email, SMS, push, templates and delivery status |
| Search projection | Consumes domain events and updates search index |
| Content/CMS | Editorial pages, banners, landing pages, navigation and publication schedule |
| Analytics | Event collection, transformations, metrics and reporting |
| Admin platform | Admin navigation, permissions integration, audit surfaces and operational shell |

A separate deployment or database is not automatically required for every logical service. Split where independent scaling, ownership, deployment, or fault isolation warrants it. Never let one service directly mutate another service's tables.

### Future service extension contract

Any future service must declare:

- Business purpose and domain owner.
- Data it owns and data it only reads.
- API and event contracts, including versions.
- Authentication and authorization requirements.
- Data classification, retention, deletion, and audit requirements.
- Consistency requirements and source of truth.
- Idempotency, retry, timeout, and failure behavior.
- Metrics, logs, traces, SLOs, alerts, and runbook.
- Deployment, rollback, migration, and disaster-recovery plan.
- Capacity assumptions and load-test evidence.
- Dependencies and failure impact on existing customer flows.

New services must not bypass the platform gateway, identity, policy, event governance, secrets management, observability, or CI/CD standards.

## 6. Customer storefront and frontend architecture

### 6.1 Frontend structure

Organize the frontend by business domains/features rather than creating a giant shared component directory. Keep design-system primitives separate from domain components.

Recommended layers:
- **Design system:** tokens, typography, color, spacing, breakpoints, accessible primitives.
- **Shared UI:** buttons, inputs, dialogs, tables, cards, navigation, feedback states.
- **Feature modules:** catalog, search, product detail, cart, wishlist, checkout, account, orders, reviews, promotions.
- **Data access:** typed API client, schema validation, query keys, retry rules, cache invalidation.
- **Routing and layouts:** public SEO routes, authenticated customer routes, checkout routes, and admin routes with separate layouts.
- **Error handling:** route-level error boundaries, safe fallbacks, retry UI, and non-sensitive diagnostics.
- **Feature flags:** controlled rollout for new functionality; flags must not replace authorization.

### 6.2 Frontend security

- Treat all client state as untrusted. The server determines identity, price, discounts, permissions, stock, and order state.
- Do not embed private API keys, payment secrets, signing keys, or privileged credentials in client bundles.
- Prefer secure, HttpOnly, Secure, appropriately SameSite cookies for browser sessions when suitable; apply CSRF defenses to cookie-authenticated state-changing operations.
- Prevent XSS using safe rendering, contextual output encoding, sanitization for user-authored rich text, and a restrictive Content Security Policy (CSP).
- Do not use `dangerouslySetInnerHTML` on untrusted content without a vetted sanitization strategy.
- Validate redirect destinations to prevent open redirects.
- Apply clickjacking protection using CSP `frame-ancestors` and appropriate response headers.
- Avoid storing long-lived bearer tokens or sensitive personal/payment data in localStorage.
- Do not rely on hidden buttons, client-side route guards, or role flags as authorization.
- Ensure every server action/API independently checks authentication, permission, and resource ownership.
- Avoid leaking PII or secrets in browser logs, URLs, analytics events, source maps, and error reports.
- Apply secure dependency management, lockfiles, vulnerability scanning, and controlled updates.
- Protect file uploads with size/type limits, content inspection, safe storage, malware scanning where appropriate, and non-executable delivery.
- Use safe error messages that do not expose stack traces, internal identifiers, SQL, tokens, or provider secrets.
- Ensure third-party scripts are minimized, reviewed, and constrained by CSP and consent policy.

### 6.3 Frontend performance

- Set performance budgets for JavaScript, images, fonts, route payloads, and third-party scripts.
- Optimize image formats, responsive sizes, lazy loading, and CDN caching.
- Load critical content quickly; avoid blocking initial rendering on recommendations or nonessential integrations.
- Split code by route and feature; avoid loading admin bundles into the storefront.
- Use server rendering or static generation where it improves SEO and performance; use client rendering only when interaction requires it.
- Prevent hydration errors and avoid unnecessary client-side waterfalls.
- Use stable cache keys and explicit revalidation/invalidation policies.
- Track Core Web Vitals and real-user metrics by route, device, and geography.
- Build accessible loading, empty, error, offline, and retry states.
- Avoid exposing private or personalized responses to shared CDN caches.

## 7. Admin frontend and operations console

Admin is a high-risk application because it can change prices, inventory, coupons, refunds, customer data, and permissions.

### 7.1 Admin capabilities

Provide domain modules for:
- Dashboard and operational alerts.
- Product/catalog, media, categories and attributes.
- Pricing, promotion rules, coupon issuance and campaign scheduling.
- Orders, payments, cancellations, returns and refunds.
- Inventory, warehouses, suppliers, stock movements and purchase orders.
- Customers, support, reviews and moderation.
- Shipping, carrier integrations and delivery exceptions.
- CMS pages, banners, navigation, SEO metadata and redirects.
- Analytics, finance reports and exports.
- Users, roles, permission policies, audit logs and system configuration.

### 7.2 Admin security controls

- Use a separate admin route/layout and preferably a distinct admin origin where practical.
- Enforce server-side RBAC or ABAC on every request and resource, not just navigation visibility.
- Apply least privilege and separation of duties for finance, refunds, pricing, user management, and security settings.
- Require MFA for privileged users; use step-up authentication for sensitive actions.
- Use short, controlled session lifetimes and session revocation; consider device and risk policies.
- Protect state-changing cookie-authenticated requests against CSRF.
- Require explicit confirmation and, where appropriate, dual approval for high-value refunds, mass price changes, campaign budget increases, bulk exports, and privilege escalation.
- Log who did what, to which resource, when, from which session/context, and the before/after values where safe.
- Make audit records tamper-resistant and restrict access to them.
- Redact sensitive values from logs and audit metadata.
- Apply rate limits and reauthentication for sensitive endpoints.
- Restrict bulk exports and downloads; log them and apply retention rules.
- Prevent insecure direct object references by checking tenant and resource ownership on the server.
- Protect against CSV/formula injection in exported spreadsheets.
- Treat imported CSVs, product descriptions, images, and uploaded files as untrusted.
- Use a separate approval workflow for changes that can affect many users or large financial amounts.
- Never use shared admin accounts.

### 7.3 Admin usability and reliability

- Show explicit loading, empty, validation, permission-denied, and failure states.
- Provide searchable/filterable tables with server-side pagination for large datasets.
- Support bulk operations with previews, dry runs, limits, and progress tracking.
- Use optimistic updates only when conflicts and rollback are handled correctly.
- Require reason codes for high-impact adjustments such as inventory corrections and refunds.
- Show promotion eligibility previews and estimated campaign exposure before publication.
- Provide immutable audit history and safe reversal workflows instead of destructive edits.
- Do not expose internal service credentials or unrestricted database consoles in the browser.

## 8. SEO architecture

SEO is a storefront and content-platform requirement. Admin tooling must allow authorized staff to manage SEO metadata, redirects, indexation, canonical URLs, and structured content without deploying code for every change.

### 8.1 Crawlability and rendering

- Use stable, human-readable, canonical URLs for products, categories, brands, and editorial content.
- Render essential product name, price, availability, main content, canonical link, and metadata in crawlable HTML.
- Choose static generation, server rendering, or revalidation per route and data freshness requirement.
- Do not require login, client-side interaction, or API calls that search crawlers cannot reliably execute to reveal essential public product content.
- Ensure internal links use crawlable anchor elements with meaningful destinations.
- Keep important pages reachable through category navigation, breadcrumbs, and XML sitemaps.
- Avoid orphan product pages unless there is a deliberate indexation policy.
- Provide useful 404 and 410 behavior for removed or unavailable content where appropriate.
- Avoid redirect chains and loops; maintain a tested redirect registry for URL changes.
- Keep pagination and filter URLs deliberate, consistent, and crawlable only when they provide useful search landing pages.

### 8.2 Canonical URLs and duplicate content

- Define one canonical URL per indexable product/category/content page.
- Normalize hostname, HTTPS, trailing slash, case, query parameters, and variant URL conventions.
- Use canonical tags consistently; do not point all product pages to the homepage or a broad category.
- Control duplicate URLs created by sorting, filtering, tracking parameters, session IDs, and faceted navigation.
- Keep internal links consistent with canonical URLs.
- Use redirects for permanent URL changes; use canonical signals for duplicate or near-duplicate versions when appropriate.
- Avoid indexing cart, checkout, account, internal search results, admin, API, and other private or low-value utility routes.

### 8.3 Robots, sitemaps, and indexation

- Generate XML sitemaps by content type and partition them to meet search engine limits.
- Include only canonical, indexable, successful public URLs.
- Update sitemap entries when products are published, removed, or materially changed.
- Include accurate `lastmod` values; do not change every timestamp on every deployment without a meaningful content update.
- Use robots.txt for crawl management, not as a security boundary or guaranteed deindexing mechanism.
- Use `noindex` for pages that must not appear in search results; ensure crawlers can access the page to see the directive.
- Do not block CSS/JS resources needed for rendering.
- Prevent staging, preview, internal admin, and test environments from being indexed; use access control as well as indexation controls.
- Avoid accidentally applying `noindex` or robots disallow rules to production during deployment.
- Monitor sitemap processing, crawl errors, indexed canonical URLs, and unexpected indexation changes.

### 8.4 Structured data

Implement valid, accurate structured data where applicable:
- `Product` and `Offer` for individual product pages.
- `AggregateRating` and `Review` only when displayed content qualifies and complies with search engine rules.
- `BreadcrumbList` for navigational hierarchy.
- `Organization` and `WebSite` where appropriate.
- `Article` for editorial content when relevant.
- Merchant/shipping/return information only when accurate and supported.

Structured data must match visible page content. Do not fabricate ratings, prices, availability, reviews, shipping promises, or discounts. Validate structured data in CI and after major template changes.

### 8.5 Product SEO content and merchandising

- Give each indexable product a unique title, meta description, heading, descriptive copy, image alt text, and canonical URL.
- Use stable product identifiers and consistent variant handling.
- Expose availability and price accurately and keep structured data synchronized with visible content.
- Optimize image size, format, dimensions, alt text, and image URLs.
- Avoid thin, duplicated, automatically generated pages with little user value.
- Provide unique category copy when useful, meaningful internal linking, breadcrumbs, and pagination behavior.
- Do not keyword-stuff titles, descriptions, alt text, or product content.
- Preserve SEO value during product slug changes, category reorganizations, and migrations with a redirect plan.
- Support authorized editors with metadata fields, social preview metadata, canonical overrides only where safe, indexation controls, and redirect management.
- Keep faceted navigation under an explicit crawl-budget and duplicate-content policy.

### 8.6 International and local SEO

When multiple locales or markets are supported:
- Use a consistent URL strategy for locales and regions.
- Implement correct `hreflang` relationships where applicable.
- Ensure each locale's canonical and alternate links are reciprocal and valid.
- Avoid redirecting crawlers or users solely based on IP in ways that prevent content discovery.
- Define currency, language, price, stock, tax, and delivery claims by market.
- Keep locale-specific metadata and translated content accurate.

### 8.7 SEO measurement

- Track organic landing sessions, crawl/index coverage, canonical selection, sitemap health, structured-data errors, Core Web Vitals, and conversion by landing page.
- Monitor 404 spikes, redirect chains, blocked important routes, duplicate titles, missing metadata, and accidental `noindex`.
- Include SEO checks in release testing and incident response.
- Use current official search engine documentation when requirements or structured-data rules may have changed.

## 9. E-commerce feature coverage

### Product discovery and catalog

- Product cards with image, title, base price, sale price, discount, rating, and stock indicator.
- Variants, SKU, attributes, gallery, video, specifications, SEO metadata.
- Categories, facets, filters, sorting, pagination, autocomplete, typo tolerance, synonyms, and ranking.
- Recommendations, similar products, recently viewed products, back-in-stock alerts, and price-drop alerts.
- Region-specific availability, delivery ETA, and serviceability.
- CMS landing pages, banners, campaign pages, canonical URLs, and structured data.

### Cart and wishlist

- Guest and authenticated carts.
- Guest-to-account cart merge with explicit conflict rules.
- Cross-device persistence for signed-in users.
- Quantity and variant validation, save-for-later, buy-again, and item removal.
- Server-side price and promotion revalidation.
- Cart expiry policy, stock changes, changed-price messaging, and unavailable-item handling.
- Wishlist add/remove, sharing if required, move-to-cart, and stock/price notifications.

### Checkout, orders, and payments

- Guest and authenticated checkout.
- Saved addresses, delivery methods, slots, pickup, shipping estimates, and tax calculations.
- Immutable, versioned checkout quote with itemized totals.
- Payment authorization/capture, retries, refunds, cancellations, COD where applicable, and provider reconciliation.
- Idempotent order creation and payment operations.
- Verified provider webhooks, duplicate-event handling, and delayed-event recovery.
- Order history, shipment tracking, invoices, cancellation, returns, exchanges, and partial refunds.

### Promotion, coupon, and referral engine

Support configurable:
- Percentage discounts with caps.
- Fixed-amount discounts.
- SKU-, product-, brand-, and category-specific promotions.
- Cart threshold offers.
- Buy-X-get-Y and bundle offers.
- Free shipping.
- First-order offers.
- Flash sales with start/end times.
- Payment-method offers.
- Customer-segment and personalized offers.
- Referral rewards for referrer and referred customer.
- Loyalty points, store credit, and gift cards.
- Subscription discounts if recurring purchases are in scope.

Each campaign should define eligibility predicates, exclusions, start/end time and timezone policy, global/per-customer usage limits, minimum subtotal, maximum discount, budget, eligible products/channels/segments/regions/currencies, stacking/exclusivity, deterministic priority, reservation/redemption/reversal semantics, audit history, and authorized approvers.

### Referral and loyalty

- Unique referral codes or links.
- Explicit attribution window and qualifying event.
- First-purchase and other eligibility requirements.
- Pending, available, redeemed, expired, and reversed rewards.
- Immutable reward-ledger entries.
- Self-referral and referral-farming detection.
- Reward hold/reversal rules for cancelled, refunded, or suspicious orders.
- Risk checks using legally appropriate account, device, velocity, and payment signals.
- Atomic reward redemption and idempotent reward issuance.

### Shipping, returns, and operations

- Multi-warehouse allocation, split shipments, delivery estimates, pickup, serviceability, carrier webhooks, and tracking.
- Return eligibility, exchanges, partial returns, refund-to-original-payment flows, inspection, restocking rules, and reconciliation.
- Tax jurisdiction rules, tax-inclusive/exclusive pricing, invoices, credit notes, and compliance requirements.
- Customer support tickets, FAQs, order assistance, notifications, abandoned-cart recovery, back-in-stock alerts, and transactional messaging.
- Reviews, verified-purchase labels, moderation, product trust signals, and abuse reporting.
- Accessibility, localization, multiple currencies, and consent controls where required.
- Marketplace seller onboarding, commissions, settlements, payouts, and disputes only if the business model requires them.
- B2B customer-specific price lists, purchase orders, negotiated discounts, credit limits, and approval workflows only if required.

## 10. Transactional correctness

### Money and pricing

- Store money in integer minor units or an exact decimal representation, with explicit currency. Never use binary floating point for monetary calculations.
- Keep one canonical pricing calculation path on the server.
- Persist an immutable quote with price versions, item-level discounts, order-level discounts, shipping, taxes, currency, and final amount.
- Define rounding rules explicitly.
- Define tax and discount ordering according to applicable jurisdictions and business policy.
- Snapshot SKU, product name, unit price, applied discounts, tax, shipping, and other material terms into order records. Catalog changes must not rewrite order history.

### Checkout saga

Model checkout as an explicit workflow rather than one long database transaction:

1. Create or resume a checkout session.
2. Revalidate customer, cart, current prices, promotions, tax, shipping, and serviceability.
3. Create a versioned immutable checkout quote.
4. Reserve required inventory with a unique reservation ID and expiration.
5. Create a pending order with an idempotency key.
6. Initiate a payment attempt with the provider.
7. Verify the provider result using a trusted API response or verified webhook.
8. Transition order, payment, inventory, and promotion states through explicit, idempotent operations.
9. Publish committed events using the transactional outbox.
10. Trigger fulfillment and customer notifications asynchronously.

External providers cannot participate in one PostgreSQL transaction. Use a saga-style workflow, explicit state transitions, timeouts, retries, reconciliation, and compensating actions. If payment outcome is uncertain, reconcile provider state before creating another charge or releasing resources unsafely.

### Separate state machines

Keep order, payment, inventory reservation, and fulfillment state independent.

Example order states: `PENDING_PAYMENT`, `CONFIRMED`, `CANCELLED`, `COMPLETED`.

Example payment states: `CREATED`, `PENDING`, `AUTHORIZED`, `CAPTURED`, `FAILED`, `REFUND_PENDING`, `REFUNDED`.

Example reservation states: `HELD`, `COMMITTED`, `RELEASED`, `EXPIRED`.

Example fulfillment states: `UNFULFILLED`, `PICKING`, `SHIPPED`, `DELIVERED`, `RETURNED`.

Use formal transition policies. Do not infer cancellation solely from a client timeout, and do not treat an order as paid based only on a client redirect.

### Inventory concurrency

Never implement inventory reservation as an unprotected read followed by a decrement.

Illustrative atomic conditional update for a single inventory row:

```sql
UPDATE inventory
SET available_quantity = available_quantity - $2
WHERE sku_id = $1
  AND available_quantity >= $2
RETURNING available_quantity;
```

Execute it within the appropriate transaction and pair it with a durable reservation record, unique reservation identifier, expiration/release policy, and commit behavior. For multi-SKU orders, use deterministic lock ordering, bounded transaction retries, and deadlock monitoring.

For hot SKUs and flash sales, consider admission control, partitioning strategies, reservation workers, or queue-based allocation. Redis can reduce load or coordinate ephemeral work, but a cache-only stock check must not be the final inventory authority.

### Coupon concurrency

A naive read-count-then-increment sequence can exceed campaign limits under concurrent requests. Use atomic reservations and database constraints.

Illustrative pattern only:

```sql
UPDATE coupons
SET reserved_count = reserved_count + 1
WHERE id = $1
  AND status = 'ACTIVE'
  AND reserved_count + redeemed_count < usage_limit
RETURNING id;
```

Production logic must also handle expiry, per-customer limits, reservation release, finalization, transaction isolation, and idempotent accounting. Track individual claims/redemptions with durable records and suitable unique constraints. Reserve budget as well as count for spend-capped campaigns.

### Idempotency

- Require idempotency keys for order creation and sensitive payment operations.
- Scope keys to the customer/operation or another explicit security boundary.
- Persist request identity, payload hash, operation status, and result.
- Return the original result for a legitimate retry.
- Reject reuse of a key with a conflicting payload.
- Deduplicate webhooks using stable provider event identifiers.
- Make consumers idempotent and support replay.
- Reconcile delayed or missing payment events against the provider.

## 11. Data ownership and database policy

### PostgreSQL

Use for authoritative transactional records and relational invariants. Use constraints, transactions, appropriate isolation, exact monetary types, connection pooling, query plans, and indexes based on observed workload. Use replicas for suitable reads but account for replication lag. Do not use stale replicas for decisions requiring the latest order/payment state.

### Redis

Use for caching, rate limits, hot data, and bounded ephemeral coordination. Define TTLs, cache keys, invalidation/versioning, stampede protection, memory limits, eviction behavior, and outage fallback. Do not silently make cache contents the authority for money or inventory.

### Kafka

Define topic ownership, partition keys, ordering expectations, schema compatibility, retention, consumer groups, retries, dead-letter handling, replay procedures, and lag alerts. Use the transactional outbox to avoid a database-commit/event-publish dual-write gap. Avoid using a stream for every synchronous request.

### OpenSearch

Treat it as a derived read model. Use versioned mappings, controlled reindexing, aliases for cutover, event-driven updates, idempotent consumers, and rebuild procedures. Account for eventual consistency between catalog changes and search visibility.

### MongoDB and other NoSQL

Do not add a NoSQL database merely because the team knows it. State the exact workload, data model, access patterns, consistency needs, retention, operational burden, and benchmark evidence. PostgreSQL JSONB may be sufficient for flexible attributes. ClickHouse is suited to analytical workloads, not as the transactional order database.

## 12. API, event, and integration standards

### API standards

- Publish OpenAPI specifications and generate typed clients where appropriate.
- Define consistent naming, pagination, filtering, sorting, error envelopes, correlation IDs, and request validation.
- Use explicit API versioning and a deprecation policy.
- Enforce authentication, authorization, ownership, quotas, and rate limits at the server.
- Use optimistic concurrency/version fields for mutable resources where lost updates are possible.
- Make retry behavior explicit for each operation.
- Avoid exposing internal database models as public contracts.
- Do not put secrets, payment data, or unnecessary PII in URLs.
- Apply request-size limits and timeouts.

### Event standards

- Use domain-oriented event names, stable event IDs, event version, timestamp, producer, correlation/causation identifiers, and minimal required payload.
- Avoid publishing secrets, full payment details, or unnecessary personal information.
- Define ordering requirements and partition keys per domain.
- Consumers must be idempotent and resilient to duplicates and out-of-order delivery.
- Keep schemas backward compatible or publish a new version under a documented policy.
- Support replay, dead-letter inspection, redrive, and reconciliation.
- Use the transactional outbox or an equivalent reliable publication pattern.

### Third-party integrations

- Put providers behind adapters so business domains do not depend on one vendor's response format.
- Set explicit timeouts, retry limits, circuit breakers, and fallback behavior.
- Validate webhook signatures and timestamps where supported.
- Store provider request IDs and sanitized outcomes for reconciliation.
- Protect credentials using a secret manager and rotate them.
- Review data sharing, regional processing, retention, and contractual requirements.

## 13. Security threat model and controls

Security must cover the customer storefront, admin frontend, APIs, services, databases, queues, cloud infrastructure, third-party integrations, and CI/CD supply chain.

### Identity and access control

- Prefer a well-maintained identity provider or established authentication implementation over custom cryptography.
- Use secure session lifecycle, rotation, revocation, and protection against session fixation.
- Apply MFA to admin and privileged accounts; consider step-up authentication for high-risk actions.
- Enforce RBAC/ABAC server-side and check resource ownership for every protected object.
- Apply least privilege to users, services, database roles, cloud identities, and CI/CD agents.
- Separate customer, staff, service, and machine identities.
- Rate-limit login, password reset, OTP, registration, and recovery endpoints.
- Use safe account recovery and avoid revealing whether an account exists.
- Define tenant boundaries if the platform becomes multi-tenant.

### Web and API security

- Follow current OWASP Top 10 and OWASP API Security Top 10 guidance.
- Validate and normalize input; use parameterized SQL and safe query construction.
- Prevent SQL/NoSQL injection, XSS, CSRF, SSRF, command injection, path traversal, request smuggling, and unsafe deserialization.
- Use strict CORS allowlists; CORS is not authorization.
- Set CSP, HSTS, `X-Content-Type-Options`, `Referrer-Policy`, and appropriate framing protections.
- Apply body-size, upload-size, pagination, concurrency, and request-time limits.
- Prevent mass assignment and property-level authorization flaws.
- Validate outbound URLs and restrict server-side network access to reduce SSRF.
- Use TLS for public and internal communication where supported.
- Return generic public errors; keep stack traces and internal details in protected telemetry.

### Payments and financial safety

- Do not store raw card numbers or CVV. Use provider-hosted fields/tokenization and comply with applicable PCI DSS scope.
- Verify signed webhooks and deduplicate provider events.
- Keep payment attempts, captures, refunds, and reconciliation records auditable.
- Never trust client redirects or browser-supplied payment status.
- Use idempotency for payment creation, capture, cancellation, and refund operations.
- Restrict refund permissions and apply step-up/dual approval for high-value or suspicious operations.
- Reconcile provider settlements, chargebacks, refunds, and internal ledgers.
- Keep secrets and sensitive provider payloads out of logs.

### Abuse, fraud, and promotions

- Protect coupon endpoints from enumeration and brute force.
- Detect referral farming, self-referrals, account abuse, COD abuse, payment fraud, and refund abuse.
- Use rate limits, velocity checks, device/account/payment risk signals where lawful and appropriate.
- Make rewards reversible or pending until the qualifying order reaches the defined state.
- Apply atomic redemption counts, per-user limits, and campaign budget reservations.
- Add manual review paths and explainable risk decisions.
- Do not rely on IP address alone for identity or fraud decisions.

### Data protection and privacy

- Classify data as public, internal, confidential, or restricted.
- Collect only data required for a defined purpose.
- Encrypt in transit and at rest; use managed KMS and rotate keys.
- Apply field-level protection or tokenization for especially sensitive fields where appropriate.
- Define retention, deletion, export, consent, and access request workflows for applicable privacy laws.
- Redact PII, access tokens, passwords, secrets, and payment data from logs and telemetry.
- Restrict analytics data and prevent sensitive attributes from entering tracking events.
- Review third-party SDKs, cookies, pixels, and data-sharing behavior.
- Use least-privilege access and audit sensitive data access.

### Upload and content security

- Allowlist file types, validate actual content rather than trusting extensions, limit size, and randomize storage names.
- Store uploads outside executable web roots and serve with safe content types.
- Scan or quarantine risky uploads where appropriate.
- Sanitize user-generated HTML/Markdown and moderate reviews/images according to risk.
- Prevent SVG/script execution and unsafe file preview behavior.
- Keep private documents and invoices behind authorization rather than public predictable URLs.

### Infrastructure and supply-chain security

- Use private network boundaries for databases, brokers, and internal services.
- Keep databases and administrative interfaces off the public internet unless strictly necessary.
- Use workload identity, least-privilege IAM, secret managers, and key management.
- Scan dependencies, containers, infrastructure definitions, and source code.
- Pin and review dependencies; generate an SBOM where required.
- Sign and verify release artifacts; protect CI/CD secrets and deployment permissions.
- Separate environments and credentials; never use production customer data casually in development.
- Patch base images and runtime dependencies under a documented policy.
- Enable audit logging for cloud control-plane and privileged actions.
- Test incident response, credential rotation, backup integrity, and disaster recovery.

## 14. SEO and security interaction

- `robots.txt` is not access control. Protect admin, preview, private exports, and account resources through authentication and authorization.
- `noindex` is not a confidentiality control. Never publish sensitive data and assume a crawler directive protects it.
- Keep staging and preview deployments access-controlled; do not rely only on `noindex`.
- Do not expose tokens, session IDs, email addresses, addresses, or other PII in URLs, canonical tags, sitemaps, analytics, or referrer data.
- Ensure CDN caching rules never cache personalized account, cart, checkout, admin, or sensitive API responses for shared users.
- Avoid caching responses with `Set-Cookie` or private data in public caches unless explicitly safe and tested.
- Prevent user-generated content from injecting malicious markup into indexable pages or structured data.
- Validate redirect destinations and redirect rules to prevent open redirects and SEO redirect abuse.
- Protect sitemap and metadata generation from including draft, private, deleted, or unauthorized content.
- Apply consent and privacy requirements to marketing scripts without blocking essential security controls.

## 15. Performance and high-traffic design

### Edge and read-heavy workloads

- CDN for images, media, static assets, and safely cacheable content.
- Next.js rendering/revalidation strategy aligned with SEO and freshness requirements.
- Redis/application caches for hot catalog responses where justified.
- Cursor pagination and measured database indexes.
- Search engine for full-text queries and facets.
- Precomputed campaign/category read models for major traffic peaks.
- Cache invalidation through versioning or domain events.
- Server-side validation at cart update, checkout, and order placement.

### Database scaling

- Connection pooling and bounded connection budgets.
- Query-plan review and N+1 elimination.
- Read replicas for appropriate read paths.
- Partition large tables only when measured access and maintenance patterns justify it.
- Archive old operational data with a tested retrieval policy.
- Isolate analytics from the transactional primary.
- Shard only when a single database's capacity or operational limits require it, with an explicit partition key and migration plan.

### Flash-sale protection

1. Serve cached product media and safe read models at the edge.
2. Reject abusive traffic using WAF, bot controls, and rate limits.
3. Bound concurrency on expensive operations.
4. Apply a waiting room/admission control when required.
5. Enforce stock limits through authoritative reservation logic.
6. Enforce coupon limits atomically.
7. Move notifications, analytics, and other noncritical work off the checkout critical path.
8. Monitor provider rate limits, database contention, queue lag, and user-visible error rates.

Autoscaling does not solve hot-row contention, overloaded databases, or external provider limits by itself.

## 16. Observability and reliability engineering

- Instrument traces, metrics, and structured logs with OpenTelemetry.
- Define SLOs for availability, latency, errors, and critical business outcomes.
- Track p50/p95/p99 latency, error rate, saturation, cache hit rate, DB locks, queue lag, payment success, checkout conversion, oversell incidents, coupon rejection reasons, crawl errors, and Core Web Vitals.
- Use bounded retries with exponential backoff and jitter.
- Set explicit timeouts and circuit breakers where appropriate.
- Use dead-letter queues, replay tools, reconciliation jobs, and stuck-workflow alerts.
- Test database restore, point-in-time recovery, regional recovery, and event replay.
- Define RPO and RTO and validate them with exercises.
- Make optional features degrade gracefully when search, recommendations, analytics, notifications, or personalization are unavailable.
- Keep the checkout critical path small and observable.
- Maintain incident runbooks, ownership metadata, escalation paths, and post-incident corrective actions.

## 17. CI/CD and engineering standards

- Monorepo or polyrepo is a team decision; define clear ownership, dependency boundaries, and release workflows.
- Enforce strict TypeScript, Go formatting/linting, static analysis, dependency scanning, and secret scanning.
- Unit-test domain rules and state transitions.
- Integration-test database constraints, transactions, cache behavior, and provider adapters.
- Contract-test service APIs and event schemas.
- Add concurrency tests for inventory and coupons, idempotency tests for payments, and replay tests for events.
- Run realistic load, stress, soak, accessibility, SEO, and fault-injection tests.
- Build immutable, scanned, signed container images.
- Use progressive rollout, health checks, rollback automation, and backward-compatible database migrations.
- Use expand-and-contract migrations for schema changes.
- Maintain an SBOM and artifact provenance where appropriate.
- Protect production deployment with approvals and least-privilege identities.
- Keep staging representative without casually copying sensitive production data.

### Release gates

Before production deployment, verify:
- Automated tests and contract checks pass.
- No critical/high unresolved security findings without an explicit risk acceptance process.
- Authentication, authorization, tenant isolation, and admin privilege tests pass.
- SEO checks pass for canonical URLs, robots directives, sitemaps, metadata, structured data, redirects, and indexable rendering.
- Accessibility and performance budgets pass agreed thresholds.
- Database migration and rollback/recovery paths are rehearsed.
- Observability dashboards and alerts are ready.
- Load tests meet agreed SLOs.
- Deployment rollback and incident runbooks are available.

## 18. Capacity planning and launch gates

Do not claim support for a number of users without workload assumptions and load-test evidence. Establish:
- Daily visits and peak requests/second.
- Concurrent sessions and checkout attempts.
- Catalog and variant count; search query mix.
- Hot-SKU and coupon contention during campaigns.
- Orders per second and payment-provider limits.
- Database connections, query latency, lock contention, and replica lag.
- Event throughput, consumer lag, retention, and replay time.
- CDN cache hit rate and origin traffic.
- Core Web Vitals and server rendering capacity.
- Availability SLOs, RPO, and RTO.
- Cost at baseline, peak, and degraded operating conditions.

Demonstrate:
- No overselling under defined concurrent purchase tests.
- Coupon limits and budgets remain correct under concurrency.
- Duplicate client requests and webhook replays do not duplicate orders, charges, or rewards.
- Payment timeout and late-webhook cases recover safely.
- Queues recover from downstream outages.
- Backups can be restored within defined objectives.
- Capacity tests meet agreed SLOs.
- SEO-critical pages remain crawlable and render correctly under load.
- Cache rules do not leak private or personalized responses.
- Rollback and disaster recovery procedures have been exercised.

## 19. Implementation workflow for an AI architect or coding agent

When asked to design, extend, or implement the platform:

1. Identify the requested outcome and affected domain. Do not assume the request is limited to storefront features.
2. Determine whether the work affects customer frontend, admin frontend, APIs, data, events, infrastructure, SEO, security, or operations.
3. Clarify business model: B2C, marketplace, B2B, or hybrid. Establish traffic, catalog, order, peak-sale, region, compliance, and availability requirements. If unknown, state assumptions and identify what must be measured.
4. Read the existing architecture, contracts, code conventions, deployment setup, and skill requirements before making changes.
5. Preserve established domain ownership and data boundaries. Do not create direct cross-service database writes.
6. Define APIs, events, schemas, permissions, consistency requirements, and failure behavior before implementation.
7. Specify database migrations, indexes, constraints, idempotency, and backfill/replay behavior.
8. Design customer and admin interfaces with accessibility, responsive behavior, authorization, SEO, and performance in scope.
9. Add threat-model considerations, runtime validation, auditability, privacy handling, and abuse prevention.
10. Include observability, dashboards, alerts, operational runbooks, rollback, and disaster recovery changes.
11. Write tests for happy paths, negative paths, concurrency, retries, authorization, failure injection, SEO, and accessibility as applicable.
12. Verify compatibility with existing services and events. Do not silently break APIs or consumers.
13. Include infrastructure and CI/CD changes when the new service requires them.
14. Do not promise scale, availability, SEO outcomes, or compliance without evidence.
15. Do not defer required production safeguards to a hypothetical later phase. Sequence work based on dependencies while retaining the required architecture.
16. Avoid inventing requirements, cloud quotas, benchmarks, provider guarantees, or compliance claims. Verify current official documentation when necessary.
17. For a new service, update the service inventory, architecture diagram, ownership map, API/event catalog, threat model, dashboards, alerts, and runbooks.

## 20. Expected architecture deliverables

For a full architecture request, provide:
1. Executive recommendation, business context, assumptions, and non-goals.
2. System context and component diagrams.
3. Service boundaries, ownership, dependencies, and data-flow diagrams.
4. Technology decisions with rationale, alternatives, trade-offs, and operational burden.
5. Database schemas, indexes, constraints, retention, and migration strategy.
6. API and event contracts, versioning, idempotency, and consistency model.
7. Checkout, inventory, promotions, payment, cancellation, returns, and refund workflows.
8. Customer storefront and admin frontend architecture.
9. SEO strategy: rendering, URLs, canonicals, sitemaps, structured data, redirects, and monitoring.
10. Security threat model, access policies, privacy controls, fraud controls, and audit strategy.
11. Infrastructure, CI/CD, observability, backup/restore, and disaster recovery.
12. Capacity model, load-test plan, SLOs, RPO/RTO, and launch gates.
13. Test strategy, rollout strategy, runbooks, and acceptance criteria.
14. Risks, trade-offs, dependencies, and unresolved questions.

For a focused implementation request, return the relevant subset while preserving this skill's mandatory security, correctness, SEO, operational, and domain-ownership standards.

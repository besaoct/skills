---
name: flexible-ecommerce-admin-platform
description: Build a secure, fast, responsive, configuration-driven e-commerce platform with a flexible admin CMS, per-user RBAC, dynamic storefront composition, single-vendor or multi-vendor capability, configurable integrations, SEO, and production-grade operations. Use when agents are asked to design, implement, extend, or review an e-commerce platform, its admin panel, back office, dashboard, page or section builder, navigation or theme editor, roles and permissions, or any drag-and-drop admin interface, even if the user only says "admin panel", "CMS", or "store backend".
---

# Flexible E-commerce Admin Platform

## 1. Mission

Build a production-grade e-commerce platform in which the storefront, admin console, commerce features, integrations, and visual presentation are configurable and extensible. Codex agents must implement the platform according to the user's explicit requirements, not assume every possible feature is required for every deployment.

The system must support:

- Single-vendor commerce as the default operating mode.
- Multi-vendor marketplace capabilities when explicitly requested, without forcing marketplace complexity on a single-vendor deployment.
- An admin-managed storefront CMS and visual layout builder.
- Individual admin-panel accounts, invitations, roles, and fine-grained per-user permissions.
- Create/read/update/delete (CRUD) permissions for every applicable resource and action.
- Multiple payment gateways, shipping providers, notification providers, search services, and other integrations.
- Runtime configuration managed from the admin panel wherever safe and practical.
- Fast, accessible, responsive, SEO-friendly public pages.
- Secure APIs, strong tenant/store boundaries when applicable, auditability, observability, and safe deployment practices.

Do not implement this as a fixed template with a few editable labels. Build reusable primitives, a structured content model, typed configuration, server-side authorization, and versioned storefront configuration.

## 2. How Codex agents must work

Before writing code:

1. Inspect the existing repository, package manifests, framework versions, folder structure, conventions, database schema, tests, and deployment configuration.
2. Identify the current stack and preserve it unless the user explicitly requests a change or a clear technical limitation requires one.
3. Create a concise implementation plan with dependencies, migrations, API changes, security considerations, and acceptance criteria.
4. Separate requested scope from optional future capabilities. Do not build marketplace, subscription, or multi-tenant features unless requested; keep extension points where useful.
5. Implement in small, verifiable steps. Run formatting, linting, type checking, tests, and relevant builds.
6. Do not claim a feature works unless it has been implemented and verified.
7. Never silently replace working project conventions or remove existing behavior unrelated to the task.
8. When requirements are ambiguous, prefer safe, conventional defaults and clearly record assumptions. Ask a question only when a missing decision blocks correct implementation.
9. Do not leave security-critical behavior as TODOs, mock authorization, hardcoded credentials, or frontend-only validation.
10. Finish with a summary of changes, migrations, environment variables, tests run, known limitations, and follow-up work.

## 3. Architecture principles

### 3.1 Configuration-driven, not configuration-only

Use code for stable business logic and security boundaries. Use validated, versioned configuration for choices administrators should control, such as:

- Store identity, branding, theme, typography, and logos.
- Navigation, pages, homepage sections, banners, hero media, and footer content.
- SEO metadata, favicons, social metadata, redirects, and sitemap settings.
- Enabled commerce modules and supported feature options.
- Payment and shipping provider selection and non-secret settings.
- Notification templates, tax settings, checkout rules, and store policies.
- Integration status and operational settings.
- Roles and permissions.

Do not let arbitrary configuration override authorization, payment verification, stock integrity, server-side pricing, or other security-critical invariants.

### 3.2 Keep responsibilities separate

Use clear boundaries for:

- Public storefront frontend.
- Admin frontend.
- Public storefront API/BFF where appropriate.
- Admin API and authorization.
- Commerce domain services.
- CMS and published storefront configuration.
- Integration adapters.
- Background jobs and event processing.
- Database and persistence.
- Logging, metrics, tracing, and audit events.

These boundaries may initially live in a modular monolith. Do not split into microservices merely for appearance. Keep modules cohesive and service boundaries explicit so they can be extracted later when scale and team ownership justify it.

### 3.3 One source of truth

- Store persistent admin-managed configuration in the database.
- Validate configuration on write and when loading a new published version.
- Use typed schemas and explicit migrations for configuration evolution.
- Cache public configuration safely and invalidate caches on publish.
- Avoid duplicating the same setting in code, database, and environment variables.
- Environment variables are for bootstrapping, deployment-specific infrastructure, and secrets that cannot safely be managed in the database.

### 3.4 Feature and deployment modes

Represent deployment mode explicitly, such as `single_vendor` or `multi_vendor`, and validate it server-side. Feature flags must not be used as a substitute for authorization.

For single-vendor deployments, hide irrelevant marketplace UI and routes. If multi-vendor is enabled, add seller entities, seller onboarding, seller-scoped catalogs, commissions, order splitting, payouts, seller permissions, and marketplace dispute workflows as required. Enforce seller isolation on the server.

## 4. Environment variables and admin-managed configuration

### 4.1 Keep `.env` small

Environment variables should primarily contain settings required before the application can start or securely connect to infrastructure, for example:

- Database connection and database TLS settings.
- Application runtime environment and canonical public base URL if needed for bootstrap.
- Session/token signing or encryption keys, preferably supplied by a secret manager.
- Initial bootstrap administrator mechanism, if required.
- Secret-manager connection settings.
- Infrastructure-specific ports, bind addresses, and observability exporter credentials.
- A small number of deployment-level feature switches that must be fixed before startup.

Do not place every provider option, theme value, navigation item, SEO title, banner, shipping rate, or storefront text in `.env`.

Never commit secrets to source control. Provide `.env.example` with placeholder names and no real credentials.

### 4.2 Store runtime configuration safely

Use database-backed, typed settings for normal admin-managed configuration. Group settings by domain and store scope. Every setting should define:

- Stable key and schema/version.
- Type and validation rules.
- Default value and allowed range/options.
- Whether it is public, admin-only, or secret.
- Whether it requires approval, re-authentication, or a publish action.
- Whether a change takes effect immediately or after publication.
- Audit and cache-invalidation behavior.

Store secret values encrypted using a dedicated key-management strategy or a secrets manager. The application must never return secret plaintext to the browser after saving it. Display only masked values and status such as “configured.” Support rotation and test-connection actions. Prefer external secret managers for high-value production credentials.

Do not store private API keys, payment secrets, SMTP passwords, webhook signing secrets, or encryption keys as ordinary unencrypted JSON settings.

### 4.3 Integration configuration UX

Each integration should have:

- Enable/disable control.
- Provider selection.
- Provider-specific typed form.
- Server-side validation.
- Secret fields that are write-only and masked after save.
- Test connection or test credentials action where safe.
- Sandbox/test mode distinct from production.
- Explicit active/default provider selection.
- Health status, last successful operation, and recent sanitized errors.
- Safe fallback behavior and alerting.
- Credential rotation and disablement.
- Audit logging for changes.

Provider adapters must implement a common internal contract. Avoid coupling commerce workflows directly to one vendor's SDK.

## 5. Admin identity, invitations, RBAC, and audit

### 5.1 Bootstrap model

Initially there is one root/owner administrator. This administrator can invite staff users and assign roles and permissions. Every staff member must have an individual account and unique credentials. Never share the owner's login.

The bootstrap administrator must be provisioned through a secure one-time setup flow, deployment command, or environment-backed bootstrap procedure. Do not ship a universal default password. Force secure credential setup and MFA where available.

### 5.2 Invitations

The administrator can create an invitation by entering an email address, assigning roles and/or explicit permissions, and setting an expiry. The platform sends a unique invitation link.

Invitation requirements:

- Use a cryptographically secure, high-entropy, single-use token.
- Store only a hash of the token where practical.
- Bind the token to the intended email address, store/tenant scope, and invitation.
- Expire invitations and allow the admin to revoke or resend them.
- Rate-limit invitation creation and acceptance.
- Do not reveal whether arbitrary email addresses already have accounts.
- Require the invitee to establish their own password or use the configured identity provider.
- Verify email ownership before activation.
- Revalidate role/permission assignment when the invitation is accepted.
- Audit invitation creation, changes, acceptance, expiry, and revocation.
- Never allow the invitee to elevate their own permissions.
- Avoid placing tokens in logs, analytics, referrers, or third-party resources.
- After acceptance, invalidate the invitation and all equivalent tokens.

### 5.3 RBAC model

Use roles as reusable permission bundles, with optional explicit user-specific grants only where the product requires them. The system must support assigning permissions to an individual user, but the authorization model must be understandable and auditable.

Each permission should be a stable, machine-readable identifier, such as:

- `catalog.products.read`
- `catalog.products.create`
- `catalog.products.update`
- `catalog.products.delete`
- `catalog.products.publish`
- `orders.orders.read`
- `orders.orders.update`
- `payments.refunds.create`
- `cms.pages.publish`
- `settings.integrations.update`
- `users.permissions.manage`
- `audit.logs.read`

Support, as applicable:

- CRUD permissions for every resource.
- Separate action permissions for publish, approve, refund, export, import, restore, manage permissions, and other high-risk actions.
- Resource and record scope, such as store, warehouse, seller, region, or assigned records.
- Role assignment and revocation.
- Direct user grants if required, with a visible explanation of effective permissions.
- Permission inheritance only if explicitly designed and clearly shown.
- Least privilege and deny-by-default.
- Immediate invalidation of sessions/caches when roles or permissions change.
- Audit logs for changes to roles, permissions, and user status.

A permission matrix should be generated from the registered module/resource/action catalog. Do not hardcode a separate inconsistent permission list in every page.

### 5.4 Authorization enforcement

- Enforce permissions in the backend/API on every request and every relevant record.
- Frontend route guards and hidden buttons improve UX but are not security controls.
- Check object ownership and store/tenant/seller scope, not just the action permission.
- Avoid insecure direct object references (IDOR/BOLA).
- Use centralized authorization middleware/policies plus domain-level checks for sensitive workflows.
- Require stronger permissions and, where appropriate, step-up authentication for large refunds, credential changes, role management, exports, and destructive actions.
- Never let ordinary admins assign permissions they do not possess or grant privileges beyond their delegated authority.
- Protect the final active owner/root account from accidental removal or demotion; define a documented recovery process.
- Test both permitted and denied cases for every protected endpoint.

### 5.5 Audit trail

Log security-relevant and business-sensitive actions, including actor, action, resource, timestamp, result, request/correlation ID, and meaningful before/after values when safe. Record invitation activity, login/security events, permission changes, integration settings, publish operations, exports, refunds, inventory adjustments, and destructive changes.

Audit logs must be access-controlled and tamper-resistant. Never log passwords, raw invitation tokens, access tokens, payment credentials, full card data, or unnecessary personal information.

## 6. Admin console foundation

Provide:

- Responsive admin shell and sidebar/navigation configuration.
- Dashboard widgets and operational alerts.
- Global search with permission-aware results.
- Tables with server-side pagination, sorting, filtering, and saved views.
- Bulk actions with previews, validation, and partial-failure reports.
- Forms with client and server validation.
- Clear loading, empty, success, failure, and permission-denied states.
- Confirmation for destructive or irreversible actions.
- Unsaved-change warnings.
- Accessible keyboard navigation and visible focus states.
- Toasts for transient feedback and persistent error details where needed.
- Activity history and contextual audit information.
- Preview, draft, publish, rollback, and version history for CMS/configuration.
- Permission-aware menus and actions.
- Consistent design tokens and component library.
- Searchable settings pages grouped by domain.

Do not put every setting on one giant page. Use domain-specific modules with consistent patterns.

## 7. Flexible storefront CMS and visual builder

### 7.1 Page management

Administrators can create and manage pages with:

- Title, slug, page type, content, status, and visibility.
- Draft, preview, scheduled publish, publish, unpublish, and archive.
- Page template and configurable section list.
- Locale/market variants if needed.
- Page-level SEO and social metadata.
- Version history and rollback.
- Redirect creation when changing a published slug.
- Access-controlled editing and publishing.
- Preview links that are signed, short-lived, and not indexed.
- Validation before publication.

Build a reusable page model rather than a separate hardcoded component for each page.

### 7.2 Section builder

Administrators can add, remove, duplicate, configure, reorder, and hide/show reusable sections using drag-and-drop. Each section has a schema and editor UI.

Initial section types should include:

- Hero image/banner.
- Hero video.
- Hero slider/carousel.
- Image with text.
- Text/rich-text block.
- Product grid and featured products.
- Category/collection grid.
- Promotional banner.
- Ad/promotion placement.
- Brand logos.
- Testimonials and reviews.
- Benefits/features list.
- Newsletter signup.
- Blog/article cards.
- FAQ/accordion.
- Rich media/embed with safe allowlist.
- Spacer/divider.
- Custom reusable section only through a safe, reviewed extension mechanism.

For every section, support configurable content, links, media, background, spacing, alignment, responsive visibility, typography, and relevant accessibility fields. Do not allow arbitrary unsanitized HTML or JavaScript.

### 7.3 Drag-and-drop requirements

- Keyboard-accessible alternative to dragging.
- Clear drag handles and visible insertion targets.
- Stable ordering persisted in configuration.
- Undo/redo for editor operations where feasible.
- Preview before saving/publishing.
- Autosave drafts with conflict detection.
- Warn when navigating away with unsaved edits.
- Validate required fields and referenced assets before publish.
- Prevent deleting a shared section or asset that is still referenced without warning.

### 7.4 Draft and publish lifecycle

Use a clear lifecycle: `draft -> validated -> published`, with optional scheduled publication. Public requests must read the published configuration, not an unfinished admin draft. Publishing should be atomic: either the full valid version becomes active or the previous version remains active.

Keep revision history and support rollback. Invalidate or version public caches after a successful publish. Do not expose private drafts to unauthenticated visitors.

## 8. Dynamic hero, banner, advertisement, and text controls

Admins must be able to configure:

- Hero image, video, slider, or mixed media.
- Desktop, tablet, and mobile media assets.
- Overlay, gradients, contrast treatment, and fallback image.
- Heading, subheading, body text, CTA labels and URLs.
- Text and CTA alignment and positioning.
- Background colors, image focal point, crop mode, and aspect ratio.
- Slide order, autoplay, duration, pause behavior, and transition.
- Start/end schedule and audience/placement rules where required.
- Ad/promotion placement, creative, destination, and tracking metadata.
- Visibility and responsive behavior.

### 8.1 Text placement

Provide x/y position controls with explicit units and responsive values. Prefer percentage or normalized coordinates, supplemented by safe layout presets, rather than fixed pixel offsets that break on mobile.

Support:

- Presets such as center, top-left, top-center, bottom-left, and bottom-center.
- Horizontal and vertical alignment.
- Width/max-width and safe-area padding.
- Independent desktop/tablet/mobile position settings.
- Drag-to-position in the preview plus numeric controls.
- Text/background contrast validation and preview.
- Bounds checking to prevent text from being positioned outside the visible canvas.

### 8.2 Typography controls

Allow each supported text element to configure:

- Font family from a curated Google Fonts catalog or approved uploaded/self-hosted fonts.
- Font weight, style, size, line height, letter spacing, text transform, decoration, and alignment.
- Color, opacity, text shadow, and limited safe effects.
- Responsive values for desktop/tablet/mobile.
- Fallback font stack and language support.

Do not fetch arbitrary font URLs from user input. Use an allowlisted font catalog and load only required families/weights. Prefer self-hosting approved font files or a controlled font-loading strategy for performance, privacy, and availability. Verify licensing and include appropriate fallbacks. Never let typography controls inject CSS or JavaScript.

## 9. Dynamic navigation builder

Support separate desktop and mobile navigation configurations and preview modes.

Possible navigation patterns:

- Standard horizontal header.
- Logo-left, centered navigation, right-side actions.
- Centered logo navigation.
- Compact header.
- Sticky header.
- Transparent/overlay header for hero sections.
- Mobile drawer.
- Mobile bottom navigation when appropriate.
- Mega menu and nested dropdowns.
- Announcement bar with optional dismissible state.

Admin controls should include:

- Logo, alternate logo, logo dimensions, favicon, and destination.
- Header/footer background and foreground colors.
- Navigation height, width, spacing, gaps, alignment, and positioning.
- Font family, size, weight, style, line height, and text transform.
- Icons, labels, accessible names, and active/hover/focus states.
- Menu items, order, nesting, destination, visibility, and open behavior.
- CTA buttons, account, cart, search, locale/currency selectors.
- Sticky behavior, scroll behavior, borders, shadows, and corner styles.
- Responsive breakpoints and per-device visibility.
- Drag-and-drop placement/order where meaningful.
- Preview at common viewport widths and custom viewport dimensions.

Navigation links must be validated. External links must use safe URL handling and appropriate `rel` behavior when opening a new tab. The editor must preserve keyboard navigation, focus management, accessible menu semantics, and usable touch targets.

## 10. Dynamic theme, color palettes, fonts, and design tokens

Create a token-based design system, not scattered hardcoded values.

Admin can configure:

- Named palettes and saved custom palettes.
- Primary, secondary, accent, background, surface, text, muted, border, success, warning, danger, and focus colors.
- Light and dark themes if requested.
- Button, input, card, badge, modal, and navigation styles.
- Border radius, shadows, spacing scale, container widths, and typography scale.
- Global font family and heading/body roles.
- Page/section-level overrides within controlled bounds.
- Desktop/tablet/mobile breakpoints and responsive token values.
- Preview and rollback.

Requirements:

- Generate CSS variables from validated tokens.
- Use a consistent token registry across components.
- Validate contrast and provide warnings for inaccessible combinations.
- Ensure focus indicators and states remain visible.
- Avoid allowing arbitrary CSS strings in normal settings.
- Sanitize and validate color, dimension, and typography values.
- Provide sensible defaults and fallback themes.
- Ensure theme changes do not cause major layout shifts or flash of unstyled content.
- Publish theme changes as a versioned atomic configuration.

## 11. Dynamic footer

Allow administrators to configure:

- Multiple footer columns and link groups.
- Logo and brand description.
- Navigation links and policy links.
- Social links with validated destinations.
- Newsletter signup.
- Contact details and business information.
- Payment/shipping trust marks where appropriate.
- Locale/currency controls where supported.
- Copyright text and dynamic year.
- Background, text, link, border, spacing, typography, and alignment.
- Desktop/mobile layout and collapse behavior.
- Legal links and required regional disclosures.

Footer content must remain accessible, responsive, and crawlable. Do not create empty or broken links. Protect forms against spam and abuse.

## 12. SEO, metadata, branding, and technical discoverability

Admin-manageable fields include:

- Store name, logo variants, favicon set, theme color, and social share image.
- Global title templates and meta defaults.
- Page-specific title, description, canonical URL, robots directives, and Open Graph/Twitter metadata.
- Product/category/brand/page SEO fields.
- Redirect manager with import/export and loop detection.
- XML sitemap generation and indexation controls.
- Structured data settings and validation.
- Search-engine verification tokens stored safely.
- Locale and `hreflang` settings if internationalization is enabled.
- Robots configuration with protected defaults.
- SEO audit reports for missing/duplicate metadata, broken links, redirect chains, canonical conflicts, and orphan pages.

SEO safety rules:

- Public product and category pages should be server-rendered or statically rendered where the chosen framework supports it.
- Public content and product links must be crawlable.
- Avoid indexing admin pages, preview links, internal search/filter URL combinations, cart, checkout, account, and private content.
- Prevent accidental production-wide `noindex` or blocking of required assets.
- Canonicalize duplicate URLs and define variant URL behavior.
- Generate correct Product/Offer/Breadcrumb structured data from real visible content and current price/availability. Never fabricate review or rating data.
- Use accurate `robots.txt` and sitemap entries based on published, indexable URLs.
- Preserve redirects and SEO equity when URLs change.
- Keep metadata and structured data synchronized with visible content.
- Provide graceful handling of missing/deleted content and appropriate HTTP status codes.

## 13. Responsive preview and quality checks

The admin preview must support:

- Desktop, tablet, and mobile presets.
- Custom viewport dimensions.
- Viewport orientation where useful.
- Responsive navigation behavior.
- Responsive typography, spacing, media crop, and section order/visibility.
- Preview of draft content without exposing it publicly.
- Preview of published and draft variants for comparison.
- Validation of overflow, clipped text, missing media, contrast, and broken links where feasible.
- Realistic preview of sticky headers, sliders, video fallback, and footer behavior.

Preview is a tool, not a replacement for real browser tests. Include automated visual/smoke checks at key viewport widths for critical templates.

## 14. Public storefront performance

Treat the public storefront as a high-traffic product.

- Render critical content on the server or statically when appropriate.
- Keep the JavaScript bundle small and split noncritical code.
- Use responsive image formats/sizes and explicit dimensions.
- Lazy-load below-the-fold media; do not lazy-load the primary LCP image unnecessarily.
- Use video posters, sensible bitrate/format choices, muted autoplay only where appropriate, and mobile fallback media.
- Respect reduced-motion preferences.
- Defer nonessential third-party scripts and advertising tags.
- Cache public published configuration and content with explicit versioning/invalidation.
- Use CDN and edge caching where appropriate.
- Avoid loading every font weight or the full icon library.
- Prevent layout shift with reserved media dimensions.
- Minimize expensive client-side personalization on initial render.
- Use database indexes and bounded pagination for dynamic data.
- Apply timeouts, circuit breakers, and safe fallback behavior for external services.
- Monitor Core Web Vitals, TTFB, error rate, cache hit rate, and API latency.
- Do not let admin preview/editor scripts leak into production storefront bundles.

## 15. Frontend security and content safety

- Sanitize rich text with a maintained allowlist-based sanitizer.
- Do not execute user-provided JavaScript or arbitrary HTML/CSS.
- Use a restrictive Content Security Policy (CSP), tuned to actual providers.
- Validate URLs and media sources; reject dangerous schemes such as `javascript:`.
- Prevent stored/reflected XSS in page content, product descriptions, navigation labels, metadata, and admin previews.
- Use CSRF protection for cookie-authenticated mutations.
- Configure secure, HttpOnly, SameSite cookies.
- Use appropriate CORS allowlists; never treat CORS as authorization.
- Add rate limits and abuse protection to login, invitations, forms, search, checkout, and other sensitive endpoints.
- Validate uploaded file type, size, dimensions, and content; scan where appropriate.
- Store uploads outside executable paths and use safe delivery headers.
- Do not expose internal stack traces, secrets, database identifiers, or private settings to public APIs.
- Protect preview routes with expiring authorization and `noindex`.
- Validate server-side all prices, stock, discounts, shipping rates, permissions, and payment states.
- Use safe external-link behavior and third-party script governance.
- Keep dependencies patched and scan builds for known vulnerabilities.

## 16. Core commerce modules

Implement only the modules required by the deployment, but keep a consistent extension pattern.

### Catalog

- Products, variants, SKUs, attributes, categories, brands, collections.
- Media, pricing, product status, SEO metadata, related products.
- Import/export with validation and failure reports.

### Inventory

- Stock by SKU/location.
- Available, reserved, committed, and in-transit quantities as needed.
- Stock movements, adjustments, low-stock alerts, purchase orders, transfers.
- Atomic reservations and concurrency control to prevent overselling.

### Orders

- Order search, details, status transitions, notes, cancellation.
- Partial fulfillment, shipment tracking, invoices, returns, refunds.
- Order timeline and audit history.

### Customers

- Profiles, addresses, order history, segments, consent and privacy workflows.
- Mask sensitive fields and enforce access permissions.

### Promotions

- Coupons, automatic promotions, usage limits, stacking rules, eligibility.
- Enforce usage limits atomically to prevent concurrent over-redemption.

### Payments

- Provider-neutral payment adapter contract.
- Authorize/capture/void/refund operations as supported.
- Verify provider signatures and webhook events.
- Idempotency and reconciliation for all financial mutations.
- Never trust the frontend's payment-success redirect as proof of payment.

### Shipping

- Provider-neutral rate/label/tracking adapter contract.
- Serviceability, rates, shipments, delivery status, returns.
- Verify webhook signatures and handle duplicate/out-of-order events.

### CMS and marketing

- Pages, sections, banners, media, navigation, theme, footer, SEO.
- Campaigns and ads only through approved integrations and consent-aware tracking.

### Reporting

- Sales, orders, catalog, inventory, customers, refunds, campaigns, SEO, and operational reports.
- Permission-controlled exports and scheduled reports.

## 17. Single-vendor and multi-vendor behavior

### Single-vendor default

- One merchant owns the catalog and inventory.
- Store admins manage all authorized products and orders.
- No seller onboarding, commissions, seller payouts, or seller portal unless requested.
- Keep data models extensible without making the MVP unnecessarily complex.

### Multi-vendor extension

When requested, introduce:

- Seller records, onboarding, verification, and status.
- Seller-scoped product/catalog management.
- Seller-scoped inventory and fulfillment.
- Commission and fee rules.
- Order splitting and per-seller fulfillment.
- Seller payout accounting and reconciliation.
- Seller roles and permissions.
- Marketplace disputes, moderation, and policy enforcement.
- Tenant/seller data isolation in every query and API.
- Marketplace-specific reporting and fraud monitoring.

Never simulate multi-vendor isolation using frontend filters alone. The server must scope all records and operations.

## 18. Provider-neutral integrations

Define internal interfaces/adapters for payment, shipping, tax, notifications, search, storage, analytics, and other external providers. Keep provider-specific code behind those interfaces.

Requirements:

- Multiple configured providers with one active/default provider or explicit routing policy.
- Capability detection rather than assuming all providers support identical operations.
- Validated configuration schemas per provider.
- Safe secret handling and rotation.
- Timeouts, retries with backoff, idempotency, and circuit breakers.
- Signature verification for incoming webhooks.
- Durable event handling and deduplication.
- Sanitized provider logs and correlation IDs.
- Health status and last-error diagnostics.
- Test/sandbox mode and safe provider switching.
- Reconciliation processes for financial or inventory state.
- Explicit behavior when the active provider is unavailable.

Provider changes must not corrupt in-flight payments, shipments, or existing records. Store the provider and external reference used for each transaction.

## 19. Data model and configuration schema

Use normalized relational tables for core commerce entities and relationships. Use JSON/JSONB only for versioned, validated documents such as section configuration or provider-specific non-secret settings when it is appropriate.

Typical entities include:

- `users`, `roles`, `permissions`, `user_roles`, `role_permissions`, optional `user_permission_overrides`
- `invitations`, `sessions`, `audit_logs`
- `stores`, optional `tenants`, optional `sellers`
- `products`, `product_variants`, `categories`, `brands`, `product_media`
- `inventory_items`, `stock_movements`, optional `warehouses`, `purchase_orders`
- `carts`, `orders`, `order_items`, `payments`, `refunds`, `shipments`, `returns`
- `promotions`, `coupons`, `coupon_redemptions`
- `pages`, `page_revisions`, `page_sections` or a versioned page document, `assets`, `navigation_menus`
- `theme_configurations`, `store_settings`, `integration_configurations`, `redirects`
- `webhook_events`, `background_jobs`, `outbox_events` where required

Use explicit foreign keys, unique constraints, indexes, transactions, and migration files. Avoid storing the entire commerce domain in one giant JSON document.

### Configuration versioning

Use immutable or revisioned published snapshots for storefront configuration:

- Draft revisions are editable.
- Validation occurs before publish.
- Publish switches the active revision atomically.
- Public cache keys include a revision/version.
- Rollback switches to a previous valid revision.
- Changes emit an event for cache invalidation and observability.
- Public APIs expose only approved, public-safe fields.
- Secret configuration is never included in public snapshots.

## 20. API and backend conventions

- Use consistent resource naming and API versioning.
- Validate all input with shared schemas where practical.
- Authenticate and authorize every admin mutation.
- Use explicit DTOs; never serialize database entities with sensitive fields by default.
- Apply server-side pagination, sorting allowlists, and filter validation.
- Use idempotency keys for payment/refund/order creation workflows where retries may occur.
- Use transactions for coupled state changes.
- Use optimistic concurrency or version checks for CMS editing to prevent overwriting another admin's work.
- Use rate limits and request-size limits.
- Return safe, consistent error responses with correlation IDs.
- Keep internal error details in protected logs only.
- Verify webhook signatures, timestamps, and replay protection.
- Use an outbox or equivalent reliable event-publishing pattern where consistency requires it.
- Do not allow client-submitted totals, permissions, role names, or payment status to be authoritative.

## 21. Accessibility and usability

- Aim for WCAG 2.2 AA for storefront and admin UI.
- Keyboard-operable menus, dialogs, forms, drag-and-drop alternatives, and navigation.
- Semantic HTML, accessible labels, focus handling, and screen-reader announcements.
- Adequate contrast and visible focus states.
- Touch targets appropriate for mobile.
- Reduced-motion support.
- Captions or equivalent information for meaningful video content.
- Alt text support for editorial images.
- Clear error messages and validation summaries.
- Do not communicate status by color alone.

## 22. Testing and quality gates

Required test categories, scaled to the project:

### Unit tests
- Permission evaluation and role inheritance/overrides.
- Configuration schema validation.
- Theme/token validation.
- Section schema validation and publishing rules.
- Price, tax, discount, inventory, and order state calculations.

### Integration tests
- Invitation creation, expiry, revocation, and acceptance.
- CRUD permission enforcement for every resource.
- Unauthorized and cross-scope access denial.
- Secret configuration never returned by APIs.
- Draft/publish/rollback behavior and cache invalidation.
- Provider adapter behavior and webhook signature checks.
- Database constraints, transactions, and idempotency.

### End-to-end tests
- Owner invites a user with limited permissions.
- Invited user sets up their own credentials.
- Limited user can perform allowed actions and is denied all forbidden actions.
- Admin creates a page and composes/reorders sections.
- Admin configures responsive hero text, typography, and navigation.
- Admin previews and publishes a theme/page.
- Public storefront reflects published configuration and not drafts.
- Single-vendor flows work without marketplace modules.
- Multi-vendor scope tests run when that mode is enabled.
- Checkout, payment callbacks, shipping updates, refund, and return flows are tested where implemented.

### Security tests
- IDOR/BOLA and cross-tenant access.
- XSS in rich text, metadata, labels, URLs, and previews.
- CSRF, session fixation, brute-force/rate-limit behavior.
- Privilege escalation and role assignment boundaries.
- Invitation token replay and expiry.
- Mass assignment and unsafe object binding.
- File upload validation.
- Secret leakage in logs, client bundles, API responses, and source maps.
- Dependency and container scanning.

### Performance and responsive tests
- Load-test key public endpoints and checkout flows.
- Test caching and invalidation after publish.
- Measure Core Web Vitals on critical templates.
- Test common mobile, tablet, and desktop viewport sizes.
- Verify that heavy editor dependencies do not inflate storefront bundles.

## 23. Observability, operations, and recovery

Provide:

- Structured logs with request/correlation IDs.
- Metrics for latency, throughput, error rates, queue lag, cache behavior, and provider failures.
- Distributed tracing when useful.
- Alerts for payment failures, webhook backlog, inventory inconsistencies, auth anomalies, and elevated errors.
- Health/readiness endpoints that do not disclose sensitive internals.
- Backup schedules and documented restoration tests.
- Migration and rollback procedures.
- Deployment health checks and gradual rollout where appropriate.
- Incident runbooks and ownership.
- Dead-letter queues and safe replay for failed events.
- Reconciliation jobs for payments, orders, shipments, and inventory.
- Feature flags for controlled rollout, with documented cleanup.
- No destructive admin action without authorization, audit logging, and appropriate confirmation.

## 24. Suggested implementation sequence

Adapt this sequence to the repository and user's actual requirements. Do not implement every optional module before a working release.

### Phase 0: Repository assessment and foundation
- Inspect stack and constraints.
- Define module boundaries and typed contracts.
- Set up database migrations, validation, error handling, logging, and tests.
- Establish environment/secret policy and secure bootstrap process.

### Phase 1: Admin identity and authorization
- Bootstrap owner.
- Individual admin accounts.
- Invitations and account activation.
- Roles, permission catalog, user-level grants if required.
- Server-side authorization middleware/policies.
- Audit logging and session controls.

### Phase 2: Configuration and CMS foundation
- Settings registry and schema validation.
- Assets/media library.
- Page, revision, draft, publish, and rollback lifecycle.
- Section registry and builder.
- Public configuration delivery and cache invalidation.

### Phase 3: Storefront visual controls
- Theme tokens and palettes.
- Typography and font management.
- Navigation builder for desktop/mobile.
- Hero image/video/slider and responsive text positioning.
- Homepage section ordering and page builder.
- Footer, logos, favicon, metadata, and SEO controls.
- Responsive preview and accessibility validation.

### Phase 4: Core commerce modules
- Catalog and inventory.
- Cart and checkout.
- Orders, payment abstraction, and shipping abstraction.
- Customers, refunds, returns, promotions.
- Notifications and essential reporting.

### Phase 5: Production readiness
- Security review and abuse controls.
- Performance and caching.
- Backups and recovery tests.
- Provider webhook reliability and reconciliation.
- CI/CD quality gates, monitoring, alerting, and deployment checks.

### Phase 6: Optional expansion
- Multi-vendor marketplace.
- Multi-store/tenant management.
- Subscriptions, loyalty, advanced analytics, AI assistance, and other user-requested modules.

## 25. Definition of done

A feature is complete only when all relevant conditions are met:

- It satisfies the user's requirement and follows existing project conventions.
- It has a clear data model and migration if persistence is required.
- It has server-side input validation and authorization.
- Every relevant action is covered by CRUD/action permissions.
- Sensitive operations are audited.
- Error, loading, empty, and permission-denied states are implemented.
- Responsive and accessible behavior is implemented.
- SEO and performance implications have been considered for public pages.
- Tests cover success, denial, invalid input, concurrency, and failure paths as appropriate.
- Documentation and configuration examples are updated.
- No secrets, credentials, mock security, or unsafe defaults are introduced.
- Linting, type checking, tests, and relevant builds pass.
- The final report accurately states what was tested and what remains.

## 26. Non-negotiable rules

1. Never trust the frontend to enforce permissions, prices, inventory, discounts, or payment status.
2. Never expose secrets to the browser or store them as plaintext ordinary settings.
3. Never allow arbitrary admin-provided JavaScript, unsafe HTML, or unvalidated CSS.
4. Never publish invalid or partially saved storefront configuration.
5. Never allow invitation reuse, permission self-escalation, or unbounded admin access.
6. Never couple core checkout workflows to only one payment or shipping vendor.
7. Never introduce multi-vendor complexity unless requested, but enforce server-side isolation if it is enabled.
8. Never make the public storefront depend on the admin editor being loaded or available.
9. Never trade security, accessibility, or data integrity for visual configurability.
10. Never assume a UI control is secure because it is hidden or disabled.
11. Never let a theme or content change break mobile layout without responsive validation.
12. Never claim completion without running relevant verification and reporting the result.

## 27. Expected output from a Codex agent

For each implementation task, provide:

1. A brief summary of the architecture and existing patterns discovered.
2. The implementation plan and assumptions.
3. Files and modules changed.
4. Database migrations and data/backfill implications.
5. New settings, secrets, or environment variables required.
6. Security and permission behavior.
7. Tests added and exact verification commands/results.
8. Known limitations and recommended next steps.

Prioritize correct, maintainable, secure, testable implementation over excessive abstraction. Build a flexible platform through well-defined schemas, module contracts, permission catalogs, provider adapters, and published configuration revisions—not through arbitrary runtime code execution.

## 28. Extensions: admin UX, drag-and-drop, and the admin feature catalog

Sections 1 to 27 are the contract. The reference files below add detail for the parts agents most often get wrong or leave thin. Read the one that matches the work in front of you.

- `references/admin-ux-and-responsiveness.md`: admin shell, responsive behavior from phone to wide desktop, tables, forms, feedback, keyboard and command palette, saved views, collaboration, accessibility (WCAG 2.2), performance, and UX acceptance checks.
- `references/drag-and-drop-and-builder-ux.md`: where drag and drop belongs and where it does not, library choices, the full interaction and accessibility spec, ordering persistence and conflict handling, and the builder, preview, and inspector experience.
- `references/admin-feature-catalog.md`: a menu of what a complete admin should offer, grouped by area and tiered (launch, growth, advanced), including features beyond sections 5 to 17, with permission and audit reminders.

How to use them:

1. Scope from the user's requirements first. The catalog is a menu, not a mandate; section 2 still applies (do not build marketplace, subscription, or multi-tenant features unless requested).
2. Every feature picked from the catalog registers its permissions in the catalog from section 5.3, is audited per section 5.5, and meets the definition of done in section 25.
3. Drag and drop is never the only way to do something (WCAG 2.2 criterion 2.5.7). Every drag interaction needs a keyboard and single-pointer alternative.
4. Admin screens must be usable on a phone for operational tasks (orders, fulfillment, approvals, alerts), even if the visual builder is desktop and tablet focused.
5. Related skills in this collection: `monorepo-fullstack-architect` for repo layout, caching, consistency, and offline or sync decisions; `production-commerce-base-and-security-concerns` for commerce domain and security depth; `production-ui-ux-and-centralized-styling` for the shared design tokens and component rules the admin UI must follow; `repo-cleanup-and-secrets-hardening` before anything is committed or shared.

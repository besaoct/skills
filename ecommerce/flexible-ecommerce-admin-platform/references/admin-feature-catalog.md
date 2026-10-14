# Admin feature catalog

A menu of what a complete e-commerce admin can offer, so agents do not forget important areas and do not invent half-built ones. It is not a mandate: pick from it using the user's requirements and the scoping rules in the main skill (section 2). Items already specified in sections 5 to 17 of the main skill are listed briefly so the catalog reads as a whole; items marked **(added)** go beyond those sections.

## Contents
1. How to use the tiers
2. Quality bar that applies to every feature
3. Dashboard and daily work
4. Orders and fulfillment
5. Catalog
6. Inventory and procurement
7. Customers
8. Marketing and promotions
9. Content and storefront configuration
10. Search and merchandising
11. Payments, shipping, tax, and finance
12. Staff, roles, and security
13. Audit, privacy, and compliance
14. Reports and analytics
15. Integrations and developer tools
16. Notifications and communication templates
17. Customer service and trust
18. System operations
19. Marketplace and multi-store (only if requested)
20. Per-admin personalization
21. Permissions and risk reminders for new features

## 1. How to use the tiers

- **Launch**: needed to run a store safely on day one.
- **Growth**: valuable once the store has steady orders or a team.
- **Advanced**: for scale, complex operations, or specific business models.

Build the Launch tier for the modules the user actually needs, record Growth and Advanced items as follow-ups, and say which you skipped. Never ship a menu entry that leads to an unfinished screen.

## 2. Quality bar that applies to every feature

Each feature must have: registered permissions (view, create, update, delete, and any special actions), server-side authorization and scope checks, audit entries for sensitive actions, validated input, loading and empty and error and permission-denied states, responsive and accessible behavior (see `admin-ux-and-responsiveness.md`), and tests. Lists get search, filters, sorting, saved views, bulk actions where useful, and export under a permission. Detail pages get a timeline, internal notes where relevant, and links to related records. Settings get history, and risky ones get approval or step-up authentication.

## 3. Dashboard and daily work

Launch
- Today's snapshot: sales, orders, average order value, visitors or conversion if tracked, refunds, with comparison to the previous period.
- Work queue **(added)**: orders awaiting fulfillment, payments needing review, returns to approve, low-stock items, reviews to moderate, failed webhooks or jobs.
- Alerts for integration health (payment, shipping, email), failing background jobs, and expiring credentials.
- Store setup checklist for new stores (add products, set payment, shipping, tax, policies, domain, test order) **(added)**.

Growth
- Date range and comparison pickers, drill-down from tiles into filtered lists.
- Role-aware dashboards and customizable widget layout (drag to arrange, with keyboard alternative).
- Top products, top customers, traffic sources, search terms with no results.

Advanced
- Real-time activity feed, goal tracking, forecasts, anomaly highlights.

## 4. Orders and fulfillment

Launch
- Order list with filters (status, payment status, fulfillment status, date, channel, location, tag, customer, amount), search by number, email, name, phone, and product.
- Order detail: items, totals breakdown, customer, addresses, payment details (masked), shipments, timeline, notes.
- Status transitions through a server-side state machine with permission per transition; cancel, partial and full fulfillment, tracking numbers, mark as paid for manual methods, resend confirmation.
- Refunds: full and partial, per line item, with reason codes, restock choice, and permission and threshold approvals.
- Packing slips, invoices, credit notes, and shipping labels (via shipping adapters), print and bulk print.
- Cash on delivery handling: confirmation call status, collected amount, remittance tracking **(added)**.

Growth
- Draft and manual orders (phone or counter sales) with custom items, discounts, and payment links **(added)**.
- Edit an order before fulfillment (add, remove, change quantity, change address) with recalculation and payment difference handling **(added)**.
- Returns and exchanges (RMA): request, approval, return label, inspection, restock, refund or store credit, exchange order creation.
- Holds, tags, internal assignments, and fraud or risk review queue with explainable flags **(added)**.
- Split and merge shipments, multi-location fulfillment, pick lists and batch picking, barcode scan verification **(added)**.
- Order timeline merging system events, staff actions, and customer messages.

Advanced
- Automation rules (auto-tag, auto-hold on risk score, auto-assign location) **(added)**.
- Pre-orders and backorders with allocation rules, subscription orders, B2B purchase orders and net terms.
- Delivery slot management and route or courier batching **(added)**.

## 5. Catalog

Launch
- Products with title, description (sanitized rich text), media, status, SEO fields, and URL handle.
- Variants and options, SKU, barcode (GTIN, UPC, EAN, ISBN, MPN) **(added)**, price, compare-at price, cost, weight and dimensions, tax class.
- Categories (tree, drag to reorder and re-parent), brands, tags, collections.
- Media management: multiple images and video, reorder, alt text, focal point.
- Draft, scheduled, active, archived statuses; duplicate product.
- Import and export with mapping, dry run, and error report.

Growth
- Smart collections defined by rules (tag, price range, stock, vendor) and manual collections with drag-sort **(added)**.
- Bulk edit (price, status, tags, category) in a grid with preview and undo.
- Attributes and filterable specifications, size guides, custom fields (typed metafields) with admin-defined definitions **(added)**.
- Related, cross-sell, and upsell products; bundles and kits **(added)**.
- Price lists per market or customer group, scheduled price changes, and sale schedules.
- Product templates for repetitive creation **(added)**.
- Digital products with secure delivery and download limits **(added)**.
- Product reviews and Q&A moderation (see section 17).
- Translations per locale and per-market availability.

Advanced
- Product data quality dashboard: missing images, missing descriptions, duplicate titles, missing GTIN **(added)**.
- Product feeds (Google Merchant, Meta catalog, marketplaces) with validation and error reports **(added)**.
- Personalized or made-to-order products, configurators, subscriptions and recurring billing.
- Digital asset management with versioning and rights metadata.

## 6. Inventory and procurement

Launch
- Stock per SKU and location, available versus reserved versus committed, manual adjustments with reason codes and audit.
- Low-stock thresholds and alerts, continue-selling-when-out-of-stock option, and inventory tracking toggle per product.
- Movement ledger showing every change with source (order, return, adjustment, transfer).

Growth
- Multiple locations and warehouses, stock transfers with in-transit state.
- Purchase orders, suppliers, expected delivery, receiving workflow with partial receipts **(added)**.
- Cycle counts and stock takes with barcode scanning **(added)**.
- Reorder suggestions based on sales velocity **(added)**.

Advanced
- Batch and lot tracking, expiry dates, serial numbers, bin locations, landed cost and COGS methods, inventory valuation reports **(added)**.

## 7. Customers

Launch
- Customer list and profile: contact details, addresses, order history, notes, tags, marketing consent status, with sensitive fields masked by permission.
- Block or deactivate accounts, and password reset triggers without exposing credentials.

Growth
- Segments defined by rules (spend, order count, last order date, location, tags, consent) used by marketing and pricing **(added)**.
- Customer groups with group pricing and group-specific visibility.
- Store credit, gift cards, and wallet balances with a ledger **(added)**.
- Merge duplicate customers with a preview and audit **(added)**.
- Privacy requests: export a customer's data and delete or anonymize on request with a tracked workflow **(added)**.
- Customer lifetime value, repeat purchase indicators, and last activity.

Advanced
- "View as customer" or impersonation for support, only with a dedicated permission, a visible banner, read-only mode by default, time limits, and full audit. Never expose payment methods or allow actions that spend money **(added)**.
- B2B accounts: companies, multiple buyers, credit limits, approval flows, tax exemptions.
- Loyalty program management: tiers, points rules, adjustments, and expiry.

## 8. Marketing and promotions

Launch
- Discount codes and automatic discounts: percentage (with cap), fixed amount, free shipping, minimum spend, scope by product, category, or collection, start and end time with timezone, usage limits global and per customer, with atomic enforcement.
- Announcement bar, banners, and hero management (see section 9).

Growth
- Stacking and priority rules with a preview of which discount wins; buy X get Y and bundle offers; flash sales.
- Gift cards and referral programs, first-order offers, payment-method offers.
- Abandoned cart recovery with timing, templates, and consent-aware sending **(added)**.
- Email and SMS campaigns through connected providers, using segments, with unsubscribe and consent handling **(added)**.
- UTM and attribution tracking, campaign performance reports.
- Pop-ups and exit-intent offers with frequency capping and consent awareness **(added)**.
- Tracking pixel and tag management with a consent gate and an allowlist of providers **(added)**.

Advanced
- A/B testing of sections, offers, and subject lines **(added)**.
- Affiliate and influencer program with codes, commissions, and payouts **(added)**.
- Personalized recommendations and merchandising rules, back-in-stock and price-drop alert management.
- Marketplace and social channel sales sync.

## 9. Content and storefront configuration

Covered in depth by main skill sections 7 to 12; the admin should provide:

Launch
- Pages with draft, preview, schedule, publish, rollback, revisions, SEO, and redirects.
- Section builder with drag-and-drop and keyboard alternative, hero image or video or slider, typography, text positioning, responsive controls.
- Navigation builder (desktop and mobile), footer builder, theme tokens and palettes, logos and favicon.
- Media library with folders, usage tracking, alt text, and replace-in-place that updates references **(added)**.
- Legal and policy pages (terms, privacy, shipping, returns) with versioning and required regional disclosures; cookie consent banner configuration **(added)**.
- Custom 404 page and maintenance mode or password protection for pre-launch **(added)**.

Growth
- Blog or article management with categories, authors, scheduling, and SEO **(added)**.
- Form builder (contact, wholesale inquiry, warranty) with spam protection, field validation, submissions inbox, notifications, and export **(added)**.
- Reusable global sections and saved blocks, page templates, and a template gallery.
- Translation management: per-locale content, missing-translation report, and market-specific pages.
- Content approval workflow with comments.
- Checkout customization within safe bounds: field requirements, order of steps, trust badges, custom notes, delivery instructions, and policy checkboxes **(added)**.

Advanced
- Multi-theme management with staged theme previews, per-market storefronts, and scheduled theme switches (for example seasonal).
- Structured content models (custom content types) for lookbooks, store locators, and size charts **(added)**.
- Store locator and pickup point management.

## 10. Search and merchandising

Growth **(added section)**
- Search configuration: synonyms, stop words, redirects (a query goes to a page), pinned and buried results, boosting rules by attribute.
- Facet and filter configuration: which attributes appear, order, labels, and display type.
- Search analytics: top queries, zero-result queries, click-through, with suggestions to create synonyms or content.
- Manual merchandising: drag-sort products within a collection or category, with the option to mix manual order with rule-based sorting.
- Reindex trigger, index health, and last sync status.

## 11. Payments, shipping, tax, and finance

Launch
- Payment providers: enable, mode (sandbox or live), masked secrets, test connection, default and fallback routing, webhook status, per-method settings and restrictions (currency, country, amount).
- Shipping: zones, flat rate, weight-based, price-based, free-shipping thresholds, pickup, carrier integrations with rates and labels, handling fees, package presets.
- Tax: inclusive or exclusive display, rates per region, product tax classes, tax exemptions; regional schemes (for example GST with HSN codes, or VAT) configured per the business's jurisdiction **(added)**.
- Currency and rounding rules, store timezone, units of measure.
- Invoice numbering sequences and legal invoice fields (business identifiers, addresses) **(added)**.

Growth
- Payment reconciliation: match provider settlements and fees to orders, list unreconciled items **(added)**.
- Disputes and chargebacks queue with evidence upload and deadlines **(added)**.
- Refund policies, automatic refund rules, and approval thresholds.
- Delivery slots and cutoff times, shipping rules with priority ordering (drag to reorder), carrier fallbacks, shipping insurance options.
- Multi-currency pricing with exchange rate source and manual overrides.

Advanced
- Payout and settlement reports for marketplaces, accounting exports and integrations (for example to accounting software), revenue recognition and tax filing exports **(added)**.
- Fraud rules and third-party fraud screening configuration, 3-D Secure and strong customer authentication settings.
- Subscription billing management and dunning.

## 12. Staff, roles, and security

Launch (main skill section 5)
- Owner bootstrap, invitations (expiring, single-use, revocable, resendable), individual accounts, roles, per-user grants with an effective-permissions viewer, resource and record scopes, deny by default, final-owner protection.
- Session management **(added)**: list of active sessions with device and location hints, sign out everywhere, forced sign-out on role change or deactivation.
- MFA enforcement for privileged roles, passkey support, password policy with breach-check, and secure recovery **(added)**.

Growth
- Permission matrix generated from the module catalog, role templates (Owner, Manager, Catalog editor, Fulfillment, Support, Marketing, Finance, Read-only), cloning roles, and comparing two roles.
- Maker-checker approvals for risky changes with pending-approvals inbox **(added)**.
- Access reviews: periodic report of who has what, last login, and unused accounts, with one-click deactivation **(added)**.
- Staff offboarding checklist (revoke sessions, tokens, transfer assigned work) **(added)**.
- API keys and personal access tokens with scopes, expiry, last-used time, and revocation **(added)**.
- Login history and security events (failed logins, new device, permission changes).

Advanced
- SSO via SAML or OIDC with SCIM provisioning, IP allowlists, device trust, time-boxed elevated access (break glass) with automatic expiry and alerts, separate admin origin.

## 13. Audit, privacy, and compliance

Launch
- Audit log viewer with filters (actor, action, resource, date, result), detail with safe before and after values, and export under permission; tamper-resistant storage.
- Data retention settings for logs, carts, and abandoned checkouts **(added)**.

Growth
- Consent records and cookie preferences log, marketing opt-in history **(added)**.
- Privacy request workflow (access, portability, deletion, correction) with deadlines and status **(added)**.
- Policy version history with effective dates and customer re-acceptance where required.
- PCI scope notes and checklist (card data never stored; hosted fields or redirects) **(added)**.

Advanced
- Legal holds, data residency settings, DPIA templates, and audit evidence exports for compliance reviews.

## 14. Reports and analytics

Launch
- Sales over time, orders, average order value, refunds, top products, inventory on hand, with date ranges and export under permission.

Growth
- Sales by product, category, channel, location, discount, and payment method; tax report; payout report **(added)**.
- Customer reports: new versus returning, cohorts, retention, lifetime value **(added)**.
- Inventory reports: aging, sell-through, stock-outs, valuation **(added)**.
- Marketing reports: campaign and coupon performance, attribution, abandoned cart recovery rate.
- Funnel and checkout drop-off, search analytics, and SEO audit report (main skill section 12).
- Saved reports, scheduled email delivery to roles, and shareable permission-aware links **(added)**.

Advanced
- Custom report builder with safe, allowlisted dimensions and metrics, warehouse-backed analytics, forecasts, and anomaly alerts. Keep heavy queries off the transactional database.

## 15. Integrations and developer tools

Launch (main skill sections 4.3 and 18)
- Integration settings per provider with health, last error, test connection, masked secrets, rotation, sandbox versus live.

Growth **(added)**
- Outgoing webhooks: subscribe to events, signing secret management, delivery log with status and retries, manual replay, and failure alerts.
- Incoming webhook monitor: received events, verification result, processing state, dead-letter queue and replay.
- Import and export job center with history, progress, and downloadable error reports.
- Background job monitor: queue depth, failures, retry, and cancel (permissioned).
- Feature flag viewer and controls with owners and expiry dates, never as a substitute for permissions.
- API documentation and sandbox keys if an external API is offered.

Advanced
- App or extension management with scoped permissions and review, custom fields and metaobjects through the registry, event bus visibility, and developer audit log.

## 16. Notifications and communication templates

Launch
- Transactional email templates (order confirmation, shipping, refund, password reset, invitation) with variables, live preview with sample data, test send, and plain-text fallback.
- Sender identity, reply-to, and domain authentication status (SPF, DKIM, DMARC) with guidance **(added)**.

Growth
- SMS, WhatsApp, and push templates through providers, with opt-in handling and regional rules **(added)**.
- Template versioning and locale variants; a trigger matrix showing which event sends which message to whom, with enable and disable per event **(added)**.
- Delivery log and bounce handling, suppression list management **(added)**.
- Internal notifications to staff (new order, low stock, failed payment) via email, in-app, or chat integrations, with per-user preferences.

## 17. Customer service and trust

Growth **(added section)**
- Inbox for contact form messages and, optionally, tickets with assignment, status, canned replies, and links to orders and customers.
- Review and rating moderation: approve, reject, reply, flag, verified-purchase indicator, and bulk actions; never fabricate reviews.
- Product Q&A moderation.
- Returns portal configuration: eligibility windows, reasons, label policies, and automatic approvals.
- Order tracking page configuration and proactive delay notifications.
- FAQs and help center management.

## 18. System operations

Launch
- General store settings: name, contact, address, currency, timezone, units, order and invoice numbering, default language.
- Domains and SSL status, canonical domain, redirects from alternate domains **(added)**.
- Environment banner and read-only indicator for production versus staging **(added)**.

Growth
- Backup status and last successful restore test visibility, job health, cache purge for published content, search reindex, and sitemap regeneration with status **(added)**.
- Error and incident log viewer showing sanitized errors with correlation IDs for support **(added)**.
- Changelog and release notes for the admin itself, and a "what changed recently" feed for staff.
- Data migration and import wizard from other platforms with validation and rollback **(added)**.

Advanced
- Multi-region and multi-store settings management, tenant provisioning, usage and billing metering where the platform is offered as a service.

## 19. Marketplace and multi-store (only if requested)

Follow main skill section 17. Typical admin additions when multi-vendor is enabled: seller onboarding and verification queue, seller catalog moderation, commission and fee rules, order splitting views, payout schedules and statements, dispute and policy enforcement, seller performance scorecards, seller roles and scoped permissions, and marketplace-wide fraud and quality monitoring. Multi-store adds a store switcher, per-store settings and theme, shared versus per-store catalog options, and cross-store reporting with scoped permissions.

## 20. Per-admin personalization

**(added section)**
- Profile, avatar, language, timezone, and date and number format.
- Theme (light, dark, system) and density (comfortable, compact), with the admin interface following the shared tokens.
- Saved views, favorites, pinned pages, recent items, and dashboard layout.
- Notification preferences and quiet hours.
- Keyboard shortcut settings and an option to disable single-key shortcuts.
- Security page: password, MFA and passkeys, active sessions, and personal API tokens.

## 21. Permissions and risk reminders for new features

Register permissions as `module.resource.action` in the central catalog, for example `catalog.collections.update`, `orders.draft_orders.create`, `customers.privacy_requests.manage`, `reports.exports.create`, `integrations.webhooks.replay`, `settings.api_keys.create`. Add separate action permissions rather than overloading update.

Treat these as high risk and require stronger permission, step-up authentication or approval, and audit: refunds above a threshold, bulk price or stock changes, exporting personal data, role and permission changes, creating API keys or webhooks, changing payment or shipping credentials, impersonating customers, hard deleting records, publishing site-wide changes, changing tax or currency settings, and disabling security controls such as MFA enforcement.

Each new module also needs: seed roles updated with sensible defaults, the permission matrix regenerated, tests for permitted and denied cases (including cross-scope access), and documentation of any new environment variables or secrets (kept small per main skill section 4.1).

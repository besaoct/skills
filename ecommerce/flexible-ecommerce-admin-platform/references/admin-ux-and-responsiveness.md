# Admin UX and responsiveness

## Contents
1. Principles
2. Admin shell and page anatomy
3. Responsive behavior by breakpoint
4. Tables and lists
5. Forms and editing
6. Feedback, safety, and recovery
7. Speed for power users
8. Collaboration and awareness
9. Accessibility (WCAG 2.2)
10. Performance budgets for the admin
11. UX acceptance checks

## 1. Principles

- Admins live in this tool for hours. Optimize for repeat use: fewer clicks, predictable layout, keyboard paths, and no surprises, over first-impression flair.
- One pattern per job. Every list, detail page, form, and settings page follows the same anatomy so staff learn it once.
- Show state honestly: draft or published, saved or unsaved, synced or failed, allowed or denied. Never leave the admin guessing whether an action worked.
- Safe by default, fast when sure: reversible actions get an undo, irreversible ones get a deliberate confirmation.
- The tool follows the shared design tokens and components (see `production-ui-ux-and-centralized-styling`). Admin density and theme are token variations, not a second design system.

## 2. Admin shell and page anatomy

**Shell**

- Left sidebar grouped by domain (Orders, Catalog, Customers, Marketing, Content, Analytics, Settings), driven by the registered module and permission catalog so menus show only what the user may access. Support collapsing to an icon rail, pinning favorites, and a recently visited list.
- Top bar: global search or command palette trigger, store switcher (when more than one store exists), environment banner for non-production, notifications, help, user menu (profile, theme, density, shortcuts, sign out).
- Breadcrumbs on detail and nested pages. The page title is a real heading and the document title reflects it.

**Page anatomy (list pages)**: title and primary action, then a toolbar (search, filters, saved views, column chooser, density, export), then the table, then pagination or infinite scroll with a total or an honest "more than N".

**Page anatomy (detail pages)**: header with identifier, status badges, and primary and secondary actions; main column for the editable content; side column for status, summary, tags, and related records; activity timeline and audit at the bottom or in a tab. Keep the primary action reachable (sticky header or action bar) on long pages.

**Settings**: grouped by domain, each in its own page with a left sub-navigation, searchable across all settings, each setting showing its effect (immediate, after publish, requires approval) per section 4.2 of the main skill.

**Peek panels**: opening a record from a list should offer a side panel or drawer so the user keeps list context, with a link to the full page. Preserve filters and scroll position when returning from a detail page.

## 3. Responsive behavior by breakpoint

Design for three jobs, not one layout shrunk: operating (orders, fulfillment, approvals), managing (catalog, customers, marketing), and building (visual editor). Operating must work on phones; managing should work on tablets; building targets tablets landscape and desktop and degrades gracefully.

| Width | Typical device | Shell | Content behavior |
|---|---|---|---|
| under 640 px | Phone | Top bar plus slide-over drawer navigation; optional bottom bar for the 3 to 5 most-used destinations (Orders, Products, Alerts, Search, More) | Tables become card lists with the key fields; filters open in a bottom sheet or full-screen panel; forms are single-column; primary action is a sticky bottom bar; detail side column stacks under the main column |
| 640 to 1023 px | Large phone, tablet | Collapsed icon rail or drawer | Two-column forms where fields are short; tables show priority columns with a column chooser; side panels overlay instead of pushing |
| 1024 to 1439 px | Laptop | Full sidebar (collapsible) | Full tables, split detail layout, side peek panel |
| 1440 px and up | Desktop, wide | Full sidebar | Use extra width for side-by-side panels (editor plus preview, list plus detail), not for stretching lines of text; cap form and prose width |

Techniques:

- Use container queries for components that appear in different panel widths (a table inside a side panel is narrow even on a wide screen). Use media queries for page-level shell changes.
- Use dynamic viewport units (`dvh`, `svh`) for full-height panels so mobile browser toolbars do not clip content, and respect safe-area insets (`env(safe-area-inset-*)`) on sticky bars.
- Keep the virtual keyboard from covering the focused field and the submit bar; scroll the focused input into view.
- Touch targets: at least 44 by 44 CSS pixels on touch layouts for primary controls (WCAG 2.2 requires a minimum of 24 by 24 at AA; 44 is the practical recommendation). Space destructive actions away from frequent ones.
- No hover-only functionality. Anything revealed on hover must also be reachable by focus and by tap (row actions behind a menu button, not hover icons).
- Wide tables: horizontal scroll inside the table region with a sticky first column and sticky header, not page-level horizontal scroll. Provide column prioritization so the phone card view shows the right fields.
- Dialogs on small screens become full-screen sheets with a clear close and a sticky confirm bar. Avoid nesting modals.
- Support orientation changes without losing unsaved state.
- Images and media thumbnails use fixed aspect-ratio boxes to avoid layout shift in grids.
- Test text expansion (long product names, translations, RTL) and very long unbroken strings (SKUs, URLs) so layouts truncate gracefully with a full-value tooltip or expand control.

Builder on small screens: if full visual editing is not practical under about 768 px, show a clear read-only preview plus a limited set of safe edits (text, visibility toggles, publish or unpublish, order moves via move menus) and say so, rather than shipping a broken drag canvas. Never silently disable authoring features.

Optional: an installable PWA for staff (order alerts via web push, barcode or QR scanning with the camera for fulfillment and stock counts, offline-tolerant read access to open orders). Decide through the offline rubric in `monorepo-fullstack-architect`; do not allow offline financial or stock-affecting actions without the sync design that skill describes.

## 4. Tables and lists

Every list of business records offers:

- Server-side pagination (cursor for large or changing sets), sorting on allowlisted columns, and filtering with typed filters (status, date range, amount range, tag, owner, location). Show active filters as removable chips and a clear-all control.
- Search that is fast and forgiving (partial match, identifier match, typo tolerance where the search engine supports it), with the match highlighted.
- Saved views: named combinations of filters, sort, and columns, personal or shared (shared views require a permission), with a default view per user. Provide ready-made views for common needs (Unfulfilled, Awaiting payment, Low stock, Drafts, Needs review).
- Column chooser, column reorder (drag with keyboard alternative), density toggle (comfortable and compact), and persisted preferences per user.
- Row selection with a clear selected count, select-all-on-page versus select-all-matching-filter (state which one), and a bulk action bar. Bulk actions show a preview of what will change, run as background jobs when large, report partial failures per row, and can be retried for failures only. Destructive bulk actions need stronger confirmation and permission.
- Inline editing for simple fields (price, stock, status, title) with validation, optimistic update, and per-cell error feedback. Respect field-level permissions.
- Export of the current filtered view (CSV, XLSX) under an export permission, audited, with PII masking options and a background job with a download link for large sets. Guard against CSV or formula injection.
- Row actions in a menu (accessible button) with the most frequent action also visible.
- Virtualize rows beyond a few hundred and keep scroll position on return.
- Empty states that explain why the list is empty (no records versus no matches for filters) and offer the next action (create, import, clear filters).
- Status badges use text plus icon plus color, never color alone, with a consistent semantic palette.

## 5. Forms and editing

- Group fields into labeled sections; use progressive disclosure (advanced options collapsed) so common edits are quick.
- Validate on blur and on submit with messages next to the field and a summary at the top that links to the first invalid field; preserve entered values on failure. Mirror server schemas on the client so rules cannot drift; the server stays authoritative.
- Show dirty state and warn before navigating away with unsaved changes (route change, tab close, drawer close). Offer autosave drafts for long-form content and builders, with a visible indicator ("Saved 10:42", "Saving...", "Offline, will retry").
- Optimistic concurrency: send the record version with every save. On conflict, show who changed it and what, and offer reload, compare, or overwrite (the last only with permission).
- Use the right input for the data: money inputs with currency and minor-unit handling, quantity steppers with min and max, date and time pickers with explicit timezone, searchable selects with async loading for large option sets, tag inputs, rich text with a sanitizing editor, address autocomplete where licensed, and unit-aware inputs (weight, dimensions).
- Multi-step flows (new product, new campaign, store setup) show progress, allow back navigation without losing data, save progress as a draft, and end with a review step.
- Secret fields are write-only and masked after save (main skill section 4.2); provide replace and rotate actions, never reveal.
- Duplicate, template, and "save as" shortcuts for repetitive creation (duplicate product, copy page, clone campaign).
- Field-level help and examples, character counters where limits matter (SEO titles), and previews for anything that renders publicly (search snippet, social card, email).

## 6. Feedback, safety, and recovery

- Reversible actions (archive, unpublish, move, hide, bulk tag) complete immediately with an undo toast for several seconds, instead of a confirmation dialog that trains people to click through.
- Irreversible or high-impact actions (delete, refund, cancel with side effects, publish site-wide changes, role changes, credential changes, large bulk edits) use a confirmation that states the consequence in plain words, names the target, and for the most dangerous ones requires typing the record name or a step-up authentication.
- Prefer archive and soft delete with a trash view and restore over hard delete; hard delete is a separate, permissioned, audited action.
- Toasts for transient success; persistent inline banners for errors that need action, with the correlation ID available for support.
- Background jobs (imports, exports, bulk edits, reindex) appear in a job center with progress, status, downloadable error reports, and retry.
- Show where the record stands in its lifecycle (draft, scheduled, published, archived) and who last changed it and when.
- Permission-denied states explain what permission is missing and who can grant it, without leaking existence of restricted records.
- Failure states for each loading path: retry control, keep stale data visible when possible, and never a blank panel.
- Session expiry mid-edit: keep the draft locally, prompt for re-authentication, then return to the same place with the work intact.

## 7. Speed for power users

- Command palette (Cmd or Ctrl plus K) that searches records (orders, products, customers) and actions ("Create product", "Go to Settings, Payments"), permission-aware, with recent items.
- Keyboard shortcuts for common navigation and actions (go to orders, create new, save, search, next and previous record), a cheat sheet opened with `?`, and no conflicts with browser, screen reader, or input fields. Provide a way to disable single-key shortcuts for accessibility.
- Bulk edit and spreadsheet-like grid editing for catalog and inventory work, plus import with a mapping step, a dry-run validation report, and a downloadable error file.
- Pins, favorites, and recently viewed per user. Saved filters and views.
- Print-friendly and PDF outputs for packing slips, pick lists, invoices, and labels.
- Smart defaults: remember last-used location, date range, and view per user.
- Barcode scanner input support (keyboard-wedge scanners work as typing; camera scanning on mobile) for fulfillment and stock counts.

## 8. Collaboration and awareness

- Presence and soft locks on records and pages being edited ("Priya is editing this page"), with conflict detection as the safety net; locks must expire.
- Internal notes and mentions on orders, customers, and products, separated clearly from customer-visible messages.
- Activity timeline on every major record merging system events, staff actions, and customer actions, filterable.
- Notification center for assigned items, approvals, failed jobs, low stock, and integration failures, with per-user preferences and links straight to the record.
- Approval workflows (maker-checker) for risky changes such as large refunds, price changes above a threshold, role changes, and site-wide publishes, with a pending-approvals inbox and an audit trail.
- Comments on drafts and revisions in the CMS so reviewers can leave feedback before publishing.
- Role-aware dashboards: the fulfillment lead sees orders to ship, the marketer sees campaign performance, the owner sees revenue and alerts.

## 9. Accessibility (WCAG 2.2 AA)

Follow the main skill's section 21 and pay attention to these 2.2 criteria that affect admin UIs:

- **2.5.7 Dragging Movements**: any drag-and-drop must have a single-pointer alternative (move up and down buttons, a "Move to" menu, or click to pick up and click to place) in addition to the keyboard path.
- **2.5.8 Target Size (Minimum)**: interactive targets at least 24 by 24 CSS pixels (use larger on touch).
- **2.4.11 Focus Not Obscured (Minimum)**: sticky headers, action bars, and cookie or chat widgets must not hide the focused element. Use scroll padding to offset sticky regions.
- **3.3.7 Redundant Entry**: do not make users re-enter information already provided in the same flow.
- **3.3.8 Accessible Authentication (Minimum)**: do not require cognitive tests to sign in; allow password managers and paste.
- Landmarks (`header`, `nav`, `main`, `aside`), a skip link, logical heading order, and one `h1` per page.
- Data tables use real table semantics with header cells and scope, captions or accessible names, sortable column state announced, and row selection exposed to assistive tech. Complex grids follow the ARIA grid pattern only when truly needed.
- Modals trap focus, return focus on close, close with Escape, and label themselves; toasts use polite live regions; errors move focus to the summary.
- Status communicated with text and icon, not color alone; sufficient contrast for all token pairs in light and dark themes.
- Respect `prefers-reduced-motion` and `prefers-color-scheme`; allow zoom to 200 percent and text spacing changes without loss of content.
- Test with keyboard only, a screen reader on at least one platform, and automated checks (axe) in CI.

## 10. Performance budgets for the admin

- Route-level code splitting; load the visual editor and its heavy dependencies only on builder routes, never in the storefront bundle.
- Set budgets: first meaningful render of a list under about 1.5 s on a mid-range laptop on a normal connection, interaction latency (INP) under 200 ms, and bounded JS per route.
- Debounce search inputs, cancel superseded requests, and prefetch likely next pages (hover or focus intent on a row).
- Cache reference data (statuses, locations, tax classes, permission catalog) client-side with sensible freshness; revalidate on focus.
- Use cursor pagination and indexed filters on the server; report counts approximately for huge sets instead of exact `COUNT(*)` on every request.
- Real-time updates (new orders, job progress) via SSE or WebSocket with polling fallback, applied as targeted cache updates rather than full refetches.
- Monitor real-user admin performance and errors, not only the storefront.

## 11. UX acceptance checks

Before calling an admin screen done, verify and report which of these were actually run:

1. Works with keyboard only, including any drag interaction and every dialog.
2. Usable at 360 px, 768 px, 1024 px, and 1440 px widths; no horizontal page scroll; no clipped actions.
3. Loading, empty, error, permission-denied, and partial-failure states exist and read clearly.
4. Unsaved-change warning, undo or confirmation behavior, and conflict handling work as specified.
5. A user without the permission cannot see the action and, when calling the API directly, is denied by the server.
6. Large data set check: 10,000 or more rows stay responsive (virtualization, server pagination).
7. Audit entries are created for sensitive actions and contain no secrets.
8. Screen reader pass over the main flow, and automated accessibility checks have no serious violations.
9. The same screen in dark theme and compact density still has adequate contrast and no overflow.

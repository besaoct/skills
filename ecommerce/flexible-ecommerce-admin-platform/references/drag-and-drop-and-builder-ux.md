# Drag and drop, and the visual builder experience

## Contents
1. Where drag and drop belongs, and where it does not
2. Library choices
3. Interaction specification
4. Keyboard, screen reader, and pointer alternatives
5. Persisting order safely
6. Undo, redo, and drafts
7. File drop zones and media ordering
8. Builder layout: canvas, outline, inspector
9. Responsive editing and preview
10. Text positioning on media
11. Section and block governance
12. Testing drag and drop

## 1. Where drag and drop belongs, and where it does not

Good fits (order or arrangement is the user's intent):

- Page sections, blocks within sections, and slides in a hero carousel.
- Navigation items, nested menus and mega-menu columns, footer link groups.
- Product images and gallery order, product option values, variant display order.
- Category and collection trees (reorder and re-parent), manual collection sort for merchandising.
- FAQ items, benefit lists, testimonials, brand logos, and other repeated content.
- Dashboard widget layout, table column order, saved view order, form field order in a form builder.
- Priority ordering of rules where order matters (shipping rules, promotion priority, redirect matching), with the resulting priority shown as a number.

Poor fits or needs extra care:

- State changes with side effects. Dragging an order card across a kanban column (for example to Shipped or Refunded) must not silently trigger fulfillment, emails, or refunds. If a board view exists, a drop opens a confirmation or form, calls the same server-side state machine as the normal action, enforces the same permission, and snaps back if the server refuses.
- Financial or irreversible operations (refund, delete, publish site-wide). Use explicit buttons.
- Large flat lists where the target is far away. Offer "Move to position" or "Move to top or bottom" and sorting rules instead of dragging across pages.
- Touch-first operations on small phones where precision is poor. Prefer move menus.

Rule: drag and drop is an accelerator on top of a complete non-drag path, never the only path (WCAG 2.2 criterion 2.5.7).

## 2. Library choices

Match the existing stack first. If none exists, these are reasonable defaults; check current maintenance, bundle size, and accessibility support before adopting, since this ecosystem moves.

| Stack | Options | Notes |
|---|---|---|
| React | dnd-kit; Atlassian Pragmatic drag and drop; React Aria drag and drop; hello-pangea/dnd (community fork of react-beautiful-dnd, which Atlassian no longer maintains) | dnd-kit is flexible with sensors, collision strategies, sortable presets, and keyboard support; Pragmatic is small, framework-agnostic, and strong on tree and file drop; React Aria gives well-tested accessibility behaviors |
| Vue | VueDraggable (SortableJS based), dnd-kit-vue style libraries | Verify keyboard support; add your own move menu if missing |
| Svelte | svelte-dnd-action | Add keyboard and menu alternatives where needed |
| Angular | Angular CDK drag-drop | Built in; supports sorting, transfer between lists, and handles |
| Vanilla or mixed | SortableJS, native HTML5 drag events | Native HTML5 drag has poor touch support and awkward styling; avoid as the only mechanism |
| Flutter (mobile admin) | `ReorderableListView`, packages such as `reorderable_grid_view` | Long-press to drag on touch |
| Trees | dnd-kit plus a tree utility, or a purpose-built tree component with keyboard support | Indent and outdent must work from the keyboard |

Choose by: touch plus mouse plus keyboard support, screen reader announcements, nested and cross-container support, auto-scroll, virtualization compatibility, bundle size, maintenance activity, and license. Wrap the choice in one internal component (for example `SortableList` and `SortableTree`) so the library can change without touching every screen.

## 3. Interaction specification

Define these once in the shared component and reuse them everywhere so every drag in the admin feels the same.

- **Handles**: a visible grip handle (with an accessible name like "Reorder Hero banner") on every draggable item. Whole-row dragging is acceptable on desktop only when the row has no competing interactions. Handles appear on focus as well as hover.
- **Activation**: pointer drags start after a small movement threshold (about 4 to 8 px) so clicks still work. Touch drags start after a long press (about 150 to 250 ms) or via the handle only, so scrolling is not hijacked. Set `touch-action: none` on the handle only, never on the whole list.
- **While dragging**: show a lifted preview (drag overlay) with reduced visual noise, a clear placeholder gap or insertion line at the target, and the original position still discernible. Highlight valid drop targets and mark invalid ones (for example nesting beyond the allowed depth, or a section type not allowed in that slot) with an explanatory cue.
- **Auto-scroll** near the edges of the scroll container, including inside nested panels. Cap speed and respect reduced motion preferences.
- **Dropping**: animate to place briefly (disable under reduced motion), then confirm the change with a subtle saved state. Dropping outside any valid target cancels and returns the item.
- **Cancel**: Escape cancels an in-progress drag and restores the previous order.
- **Constraints**: define allowed containers, maximum depth for trees, and maximum counts (for example 5 slides). Block drops that violate them with a visible reason rather than silently ignoring.
- **Multi-select drag** where it saves time (media, products in a manual collection), showing a count badge on the drag overlay.
- **Cross-list moves** (for example from "Available sections" to "Page layout", or between navigation columns) copy or move according to a stated rule, with the library palette items always copying.
- **Performance**: virtualize long lists with a library that supports it; avoid re-rendering the entire list on every pointer move; keep drag overlays lightweight.
- **Dirty state**: a reorder marks the document dirty and either autosaves as a draft or enables Save, consistent with the screen's pattern.

## 4. Keyboard, screen reader, and pointer alternatives

Required for every draggable list or tree:

1. **Keyboard drag**: focus the handle or item, Space or Enter to pick up, Arrow keys to move, Space or Enter to drop, Escape to cancel. Provide Home and End to jump to the first and last positions. For trees, Right and Left arrows indent and outdent where valid.
2. **Announcements**: a polite live region announces pick up, each move ("Hero banner, position 2 of 6"), drop ("Dropped at position 3 of 6"), and cancel. The default announcements of the library should be customized to use the item's label.
3. **Single-pointer, non-drag alternative**: a per-item menu with "Move up", "Move down", "Move to top", "Move to bottom", and "Move to position..." (and "Move into..." for trees), plus "Duplicate", "Hide", and "Delete" where applicable. This satisfies 2.5.7 and also serves precision-challenged and touch users.
4. **Visible focus** on handles and items that does not rely on color alone and is not covered by sticky bars (2.4.11).
5. **Reduced motion**: swap animations for instant moves.
6. **Role semantics**: lists are real lists; sortable items expose a clear instruction (for example `aria-roledescription="sortable"` and an instruction string on focus) the way the chosen library supports. Do not invent conflicting ARIA.

## 5. Persisting order safely

Pick a persistence model per list and write it down.

| Model | How | Use when |
|---|---|---|
| Ordered ID list in a document | The page or menu document stores `children: [id1, id2, ...]` and saves as part of a versioned revision | Small, bounded structures edited as a whole: page sections, navigation, footer, hero slides |
| Integer position column | `position` integers, resequenced on change in a transaction | Short lists with infrequent edits; simplest to reason about |
| Fractional index key | A sortable string key between neighbors (for example via a fractional-indexing library); a move rewrites one row | Large or frequently reordered lists (product images, collection items, tasks), or lists edited by several people. Store the key as text with a binary collation so ordering is stable (for example `COLLATE "C"` in PostgreSQL); occasionally rebalance if keys grow long |

Rules:

- The client sends intent ("move X after Y within parent P"), or the full ordered ID list for small sets, plus the current revision or version for conflict detection. Never trust the client's computed positions without validation.
- The server validates that every ID exists, belongs to the stated parent and store or seller scope, is movable by this user (permission and record scope), obeys depth and count limits, and that the list is complete when a full list is submitted. Reject duplicates and unknown IDs.
- Apply the change in one transaction, bump the version, write an audit entry for meaningful changes, and invalidate public caches only on publish (drafts do not touch published output).
- Be idempotent: resubmitting the same move produces the same state. Use a request ID for retries.
- Optimistic UI: update locally at once, send in the background, and on failure roll back with a clear message and a retry. On a version conflict, fetch the latest state, show what changed, and let the user reapply.
- For trees, prevent cycles (cannot move a node into its own descendant) on the server, and update materialized paths or closure tables atomically.
- Debounce rapid successive moves into one request when appropriate, but never lose the final order.
- For published storefront structures, the published snapshot is immutable; edits happen on the draft revision and publish is atomic (main skill section 7.4).

## 6. Undo, redo, and drafts

- Implement undo and redo with a command history for editor operations (move, add, remove, duplicate, property change, text edit). Each command knows how to apply and revert itself. Cap history length and clear it on publish or reload.
- Keyboard: Ctrl or Cmd plus Z and Shift plus Z (or Ctrl plus Y), scoped to the builder so it does not fight text inputs.
- Autosave drafts at a short interval and after meaningful operations, with a visible state ("Saved", "Saving...", "Offline, changes kept on this device", "Conflict"). Autosave writes to the draft revision only.
- Conflict detection on autosave using the revision version; if another admin saved, present a compare and merge choice (keep mine, take theirs, or per-section choice) instead of silently overwriting.
- Revision history with named versions, who changed what, diff between versions, restore, and the ability to label a revision before publishing.
- Warn when leaving with unsaved or unpublished work, and distinguish "saved as draft" from "published" everywhere.

## 7. File drop zones and media ordering

- Drop zones for images, video, and documents with a visible target, click-to-browse fallback, paste from clipboard for images, and multi-file support.
- Validate type by content (not only extension), size, dimensions, and count before upload; show per-file progress, cancel, retry, and clear error messages. Use resumable or chunked upload for large video. Upload directly to object storage with short-lived signed URLs, then register the asset on the server after validation and scanning.
- Generate responsive renditions and modern formats server-side; extract a poster frame for video; strip risky metadata (EXIF location) unless needed.
- Require alt text (or an explicit "decorative" choice) for editorial images before publish, and offer suggestions the user can edit.
- Folders or tags in the media library, usage tracking ("used in 3 pages, 12 products"), and a warning before deleting an asset still referenced (main skill section 7.3).
- After upload, allow reorder with the same sortable component, setting a primary image, and per-image focal point selection (click on the image to set the crop center) used for responsive crops.
- Drag from the media library into the builder or product gallery as a shortcut, with a click-to-insert alternative.

## 8. Builder layout: canvas, outline, inspector

A familiar three-region layout keeps the builder learnable.

- **Left: structure and library.** An outline (layers) tree of the page's sections and blocks, drag-reorderable with keyboard support, with visibility toggles, lock, rename, and duplicate. A library of addable sections and blocks with search and categories, plus saved blocks and global (shared) sections.
- **Center: canvas.** A live preview of the draft, rendered by the real storefront components inside a sandboxed iframe so what the admin sees matches production. Clicking an element selects it and opens its settings; hover shows outlines and labels; insertion points appear between sections ("Add section here"). Provide zoom and fit-to-width.
- **Right: inspector.** Typed settings for the selected item, grouped into Content, Layout, Style, Responsive, and Advanced. Show where a value is overridden for a breakpoint (a dot or badge) with a "reset to inherited" action.
- **Top bar**: page name and status, device switcher, undo and redo, preview in new tab (signed link), save state, schedule, publish, and revision history.

Implementation notes:

- Editor-to-preview communication uses `postMessage` with strict origin checks and a message schema; the preview never trusts arbitrary messages. Sandbox the iframe appropriately and keep editor scripts out of public bundles (main skill section 14).
- The preview renders from the same section registry and schemas as production, so a section type exists in one place: schema, editor form, and renderer.
- Inline text editing is useful, but writes through a sanitizing rich text model, never raw HTML.
- Selection state is addressable (URL or state) so a deep link opens a specific section.
- Provide templates for new pages, duplicate page and duplicate section, and copy and paste of sections between pages or stores with asset and reference handling.
- Show validation problems in the outline (missing alt text, missing image, broken link, low contrast, empty required field) and block publish on errors while allowing publish with warnings after review.

## 9. Responsive editing and preview

- Device switcher with presets (phone, tablet, desktop) and a custom width and height with orientation toggle. Remember the last choice.
- Settings that vary by breakpoint (media asset, crop focal point, alignment, text size, spacing, visibility, columns, section order) show an indicator when overridden and inherit from the larger size by default.
- "Hide on mobile" or "show only on desktop" toggles per section, with a preview and a warning when hiding would remove the only primary call to action on a device class.
- Section reorder on mobile only, when the product needs it, is an explicit per-breakpoint order override and not an accident of drag.
- Live checks per breakpoint: text overflow or clipping, image crop losing the subject (compare against focal point), contrast against the media behind text, minimum touch target size, missing alt text, and layout shift risks.
- Side-by-side comparison of draft and published, and of two breakpoints.
- Real browser smoke and visual tests at key widths for critical templates remain required; the preview is a tool, not a test (main skill section 13).

## 10. Text positioning on media

Extends main skill section 8.1.

- Offer layout presets (nine-point grid: top, center, bottom crossed with left, center, right) as the primary control, with an "Advanced" free-position control for fine tuning.
- Store positions as normalized coordinates (0 to 1 of the container) or percentage anchors plus an anchor point, never raw pixels, with separate values per breakpoint and sensible inheritance.
- Drag the text box in the preview with snapping to guides (center lines, thirds, safe-area margins) and arrow-key nudging (1 percent, 10 percent with Shift), plus numeric fields. Clamp inside safe-area bounds.
- Re-run contrast checks when the text, overlay, or crop changes; offer an overlay or text-shadow suggestion when contrast is insufficient.
- Because the background media crops differently per device, tie text anchors to the focal point or to the container edges, and warn when the text would sit over the subject's face or a busy region if the platform has such detection; otherwise rely on the preview and checks.

## 11. Section and block governance

- Each section type declares: schema, defaults, allowed parents and children, limits (maximum slides, maximum items), required fields, responsive fields, accessibility fields, and which roles may use it. This declaration drives the editor form, validation, and renderer.
- Permissions: separate abilities to edit draft content, edit structure (add, remove, reorder), edit styles, manage global sections, and publish (`cms.pages.update`, `cms.pages.publish`, and similar). A content editor may change copy and images without being able to restructure the layout or publish.
- Locked regions and guardrails: let owners lock sections or style properties so editors cannot break brand rules (fixed header, fixed legal footer).
- Global (shared) sections: edits propagate to every page that uses them; show usage count and require confirmation and publish permission; offer "detach to local copy".
- Approval workflow for publish on sensitive pages (home, checkout copy, policies) with reviewer comments.
- Scheduling: start and end times in the store timezone shown with the viewer's timezone, plus a calendar view of scheduled changes to catch collisions.
- Custom code is not allowed in sections. New section types are added by developers through the registry, reviewed, tested, and deployed, per the main skill's extension rule.

## 12. Testing drag and drop

Include these in the test plan and report which were actually run:

- Unit tests for the reorder and move functions (insert at start, middle, end; move across parents; cycle prevention; depth and count limits).
- Integration tests that the API rejects foreign IDs, cross-scope IDs, duplicate IDs, stale versions, and unauthorized users, and that a valid move is idempotent.
- End-to-end tests driving the real UI: pointer drag, keyboard drag, and the "Move to" menu produce identical results; Escape cancels; a failed save rolls back; two admins editing produce a conflict prompt.
- Touch testing on a real or emulated touch device: scrolling still works, long-press picks up, no accidental drags.
- Screen reader check of announcements on at least one platform.
- Performance check with a long list (for example 500 items) to confirm no jank.
- Visual tests of the builder at key viewport widths and of the published output for the same configuration.

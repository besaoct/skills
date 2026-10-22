---
name: clean-cross-platform-ui
description: Rules for building clean, professional, production-quality UI on desktop, web and mobile (iOS, Android, responsive web, Electron, Tauri, Flutter, React Native, SwiftUI, Compose) with a centralized design-token system, near-transparent borders, no hover/focus/outline/press effects on controls, one control height and shape system, darker filled controls, a clean sidebar layout, calm dialogs, overlay scrollbars, plain copy, and a palette and font chosen by the user. Also covers logos and app icons built from geometry, and store screenshots or promo assets made from the app itself. Use this skill whenever the user asks to build, restyle, redesign or review any website, web app, admin panel, dashboard, landing page, storefront, mobile app screen or desktop app interface, or to design a logo, app icon or store listing, or mentions UI, UX, theme, design system, design tokens, sidebar, colors, fonts, icons, scrollbars or styling, even if they do not name this skill.
---

# Clean Cross-Platform UI

Build polished, minimal, professional interfaces that look intentional on desktop, web and mobile. One design system feeds every platform. The section "Overrides" wins over any other guidance, including framework defaults and generic best practice, because these are the user's explicit taste decisions.

## Overrides (highest priority)

### 1. No interaction chrome on controls
Inputs, buttons, selects, checkboxes, radios, textareas, switches, tabs, list rows and menu items have:
- no hover effects
- no focus styles, focus rings or outlines
- no press, ripple or tap highlight

Suppress platform defaults and add no replacements. Per-platform techniques are in `references/platform-suppression.md`; read it when targeting a specific framework.

Keep only functional states: selected/active (for example the current nav item), disabled, invalid, loading.

If the user asks for keyboard accessibility to be restored, add exactly one subtle, centralized focus-visible treatment (a small border-color or background change) in the shared control styles. Do not add it unprompted. Mention once, at the end of the work, that removing focus visibility hurts keyboard users.

### 2. Near-transparent borders
Every border and divider uses one shared border token at roughly 6 to 10 percent opacity of the text color, close to transparent. Define it once and reuse it everywhere, on all platforms. Depth comes from borders and surface shade changes, not heavy shadows.

### 3. Ask before building: palette and font
Before writing UI code, ask the user to choose:
1. **Color palette.** Offer 3 to 5 options, each with a one-line mood description and swatch values (background, surface, text, accent) for light and dark. Make them distinct and neutral-led, not rainbow, neon, pastel-by-default or purple-and-black-by-default.
2. **Font family.** Default is the platform system font:
   - Web: `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`
   - iOS/macOS: San Francisco. Android: Roboto. Windows: Segoe UI. Linux: system UI font.

If the user does not choose, use the system font and a neutral palette. If an existing project already defines palette and font, reuse them and skip the question.

### 4. Look and feel
- Clean and minimal. Generous whitespace, left-aligned content on one consistent edge.
- Three text levels: primary (headlines, key labels), secondary (body), tertiary (section labels, metadata).
- Neutral UI chrome. Color comes mainly from content and a single accent.
- Button hierarchy: primary (filled), secondary (outlined, low-opacity border), tertiary (text link with arrow).

### 5. Navigation adapts by size, same visual language
- **Expanded (desktop, wide web):** fixed left sidebar plus top bar, logo top-left aligned with the sidebar column.
- **Medium (tablet, small window):** collapsible icon rail or collapsible sidebar.
- **Compact (phone):** bottom tab bar with 3 to 5 destinations, secondary items in a drawer or sheet. Never force the desktop sidebar onto small screens.

Sidebar and nav styling everywhere:
- items grouped under small, dim, sentence-case section labels
- outline icons with uniform stroke weight, one per label
- active item shown with a filled, rounded background or tint
- thin near-transparent 1px dividers
- optional tinted tiles: each section gets its own muted hue as a faint tile behind its glyph; the active one becomes a solid, slightly darker tile with a white glyph
- no footer text in the sidebar; keyboard shortcuts may sit right-aligned and tertiary
- a collapsed icon rail must clear the window controls the OS draws in that corner (macOS traffic lights end about 70pt from the left, so a rail is at least 80pt wide)

### 6. One control size and shape system
- Exactly two control heights as tokens: standard (about 32 to 36) for buttons, search fields, segmented controls, text fields, selects and number fields, and compact (about 24 to 28) only for small buttons inside list rows or field labels.
- One shape: every single-line control uses the same radius (pill by default). Multi-line fields use one field radius token (about 12), never a pill.
- Controls that share a toolbar row share the standard height, so a "Refresh" button never looks smaller than the search field next to it.
- Where the platform paints its own chrome, replace it with the themed version: selects get the shared shape plus a themed chevron, number fields lose their stepper arrows. On mobile keep native pickers and only style what the platform allows.

### 7. Filled controls and status colors
- Filled controls (primary and danger buttons, the selected segment, an on switch, the active nav tile) use a fill one shade darker than the accent, with light text at 4.5:1 or better (aim for about 4.8:1). Define `accent-fill`, `danger-fill` and `on-accent` tokens for this.
- Keep the brighter accent for text, links, charts, progress and focus of attention, where it sits on the background rather than behind text.
- Green, amber and red are reserved for status (safe or ok, needs review or warning, caution or error). Never use them for decoration.
- Status labels are colored text only: no pill background, no dot. A "view all" link becomes a small chevron icon button.

### 8. Dialogs
- On layouts with a sidebar, the dialog and its dimming cover the content area only. The sidebar stays visible but inert. Center the dialog in the content area and cap its width to that area.
- Anchor dialogs at a fixed top offset rather than centering vertically, so a dialog whose content changes (for example review, then result) does not jump.
- Confirmations make the safe choice the default (Cancel). Anything permanent (erase, empty trash, delete forever) needs a second, explicit confirmation that names what will be lost and its size.
- Dim the background before the dialog appears and bring the dialog in quickly; never cross-fade a half-transparent dialog over undimmed content.

### 9. Disclosure, alignment and spacing
- One disclosure chevron icon everywhere, never Unicode triangles. It points right when closed and rotates 90 degrees when open, driven by `aria-expanded` or the platform equivalent.
- What a disclosure reveals lines up with its title text, not with the chevron. Details under a list row line up with the row's name.
- A toolbar inside a card keeps the same gap below it as above it, so its buttons never sit on the next divider.
- One spacing scale (for example 4, 8, 12, 16, 24) for every gap. Do not invent in-between values.
- Desktop windows get a minimum size at which nothing overlaps or clips.

### 10. Scrollbars
- No permanent scrollbar chrome. A thin themed thumb (one token for its color) appears only while the content scrolls, on a transparent track, and fades out after about a second. It can be dragged and works inside dialogs.
- If the rendering engine will not repaint styled native scrollbars reliably (WebKit), hide the native ones and draw an overlay thumb. Details in `references/engine-gotchas.md`.

### 11. Motion
- Restrained and purposeful: about 0.15s for state changes, about 0.5s with an ease-out curve for things entering the screen. Stagger a group a few dozen milliseconds per item, capped.
- Respect reduced-motion settings everywhere: content then simply appears.
- Something revealed once does not animate again on resize or re-render.

### 12. Writing
- Sentence case for every label, button, heading and menu item. No em dashes. Plain words, no marketing filler.
- Destructive or lossy actions say what happens and how it comes back ("Deletes build data. Rebuilt the next time you build.").
- Errors say what happened and what to do next, in one or two sentences, never a raw exception.
- Counts and sizes on screen must add up across the interface.

## Compatibility of the styling layer

- Keep tokens to literal values per theme (rgba, hex). Avoid the newest color functions (`color-mix()`, relative colors, `oklch` tricks) unless every target engine supports them; macOS 13 WebKit, older Android WebViews and older Electron builds do not all render them.
- Test layout in the real rendering engine of the app, not only in a desktop browser. Chrome and WebKit disagree on several flex and observer details; the known traps are in `references/engine-gotchas.md`.

## Cross-platform foundation

- Detect the framework and target platforms first. Extend the existing architecture; never add a competing styling system.
- Define design tokens once, in platform-neutral form where possible (JSON, TypeScript, or one source file), and map them to each target: CSS variables, Tailwind theme, SwiftUI assets, Compose theme, Flutter ThemeData, React Native theme object.
- Tokens cover colors, typography, sizes and weights, spacing, radii, borders, shadows, transitions, breakpoints or size classes, elevation. Use semantic names (`color-surface`, `color-border`, `text-primary`, `radius-control`, `spacing-section`), not raw values. No redundant tokens, no second source of truth.
- Light and dark themes live in one theme system and follow the system setting by default.
- Changing a shared token or component style must update every usage on every platform.

Why this matters: the user wants to restyle the product by editing a few files, so scattered values defeat the purpose.

## Centralized styling, no scattered inline styles

- Put styles in dedicated modules adapted to the framework: tokens, theme, typography, global, utilities, plus per-component styles (buttons, forms, cards, dialogs, navigation, tables, feedback).
- No hardcoded hex colors, magic numbers or one-off paddings for ordinary presentation. Use tokens, shared classes, theme values or reusable components.
- Tailwind: use theme tokens, extract repeated utility strings into components, avoid arbitrary values when a token exists, do not replace Tailwind with custom CSS.
- CSS, Sass, CSS Modules: keep component styles in their stylesheets, use central tokens, reuse shared classes.
- CSS-in-JS, React Native StyleSheet, SwiftUI modifiers, Compose modifiers, Flutter widgets: use the framework's theme, variant and composition mechanisms; build shared styled components or view modifiers.
- Inline or dynamic styles only for genuine runtime values (chart coordinates, calculated dimensions, dynamic progress, user-configurable properties).

## Reusable components

Create or extend a shared component when a pattern repeats:
- Buttons, icon buttons
- Text, password and search inputs
- Selects, checkboxes, radios, switches, textareas
- Form labels, validation messages, help text
- Cards, panels, content containers
- Dialogs, drawers, bottom sheets, popovers, dropdown menus
- Tables, pagination, lists, data lists
- Badges, alerts, notifications, toasts
- Tabs, breadcrumbs, sidebar, bottom tab bar, menus
- Loading indicators, skeletons, empty states, error states

Support documented variants (primary, secondary, danger, compact, large), keep them consistent across platforms, use semantic markup and accessible component APIs, skip abstractions for unique or trivial pieces, and re-check existing usages after changing a shared component.

## Responsive and adaptive behavior

- Centralize breakpoints or size classes: compact (phone), medium (tablet or small window), expanded (desktop or large window). Adapt by content, not device name.
- No horizontal overflow, cramped layouts or oversized empty spaces. Desktop windows must resize cleanly.
- Respect safe areas: notches, status bars, home indicators, gesture areas, window insets.
- Support portrait and landscape on phone and tablet.
- Centralize container widths, max content widths, section spacing and grids.

## Input modality

- Touch: tap targets at least 44x44 pt (iOS) or 48x48 dp (Android), adequate spacing, platform-expected gestures.
- Pointer: because hover styling is off, nothing may depend on hover. Every action is reachable by click.
- Keyboard: logical tab order, Enter and Escape behavior in forms and dialogs, standard desktop shortcuts where relevant.
- Never hide essential actions behind hover or long press only.
- On mobile, keep inputs visible above the on-screen keyboard and set correct keyboard types and autofill hints.

## Control styling

- Control borders, backgrounds, radii and states are defined centrally.
- Consistent size, spacing, typography and alignment across controls; no layout shift between states.
- Use native controls where they fit better (date pickers, mobile selects, system menus) and style only what the platform reliably supports. Build custom accessible controls only when truly needed.
- Respect platform conventions (back navigation, dialog button order, desktop menu bar) while keeping the shared visual style.

## Avoid generic AI-generated design

Do not use these unless requested or justified by the brand or product. The full list of 30 with notes is in `references/anti-patterns.md`; read it before finalizing any marketing page, landing page or visual redesign. The most common offenders: harsh gradients, glassmorphism and blur, decorative orbs and dot grids, drop shadows everywhere, rainbow or neon accents, purple-and-black default palettes, Inter/Geist/Space Grotesk by default, Lucide icons by default, emoji icons, three-feature-card rows, fake testimonials or metrics, em dashes in copy, and "It's not X, it's Y" copywriting.

Still include a Terms of Service and Privacy Policy when the product requires them, including app store disclosures, and make sure the policy reflects real data practices.

## UI/UX quality

- **Hierarchy:** clear relationships between titles, headings, body, labels, metadata and primary actions; consistent type scale, line heights and content widths; not every element equally prominent.
- **Layout:** one spacing scale; no arbitrary repeated margins.
- **Interaction:** clear primary and secondary actions; only the functional states from Overrides; sparing, consistent animation; never color alone to convey status.
- **Forms:** aligned labels, inputs, messages and help text; useful error messages; preserve entered values; consistent input heights.
- **Loading and feedback:** loading, success, error, empty, offline and disabled states; prevent duplicate submissions; no spinners or skeletons without a functional reason.
- **Typography:** scale with platform settings (Dynamic Type, Android font scale, browser zoom) with no clipped or overlapping text.
- **Performance:** fast first render, optimized assets, no main-thread blocking, smooth scrolling.
- **Accessibility:** semantic structure, accessible names and roles (ARIA, VoiceOver, TalkBack, desktop screen readers), sufficient contrast, reduced-motion support, screen reader operability on mobile.

## Data-dense views

- Large visual layouts (treemaps, grids, boards) scroll instead of shrinking items until they are unreadable. Give every cell a minimum size big enough for its label, and fold only the true tail into an "other" item.
- Size such a view to the space left in its window, measured at runtime, rather than a fixed guess, so its scroller is always fully on screen; when it cannot fit, let scrolling carry on to the page.
- Color data marks from the accent and a couple of neutral-warm partners at decreasing strength for smaller items, never a rainbow.

## Logos, app icons and marketing assets

- Logos and app icons are built from geometry: one module on a fixed grid, every size and angle a rule, generated by a script that writes every size. No letters or sparkle glyphs unless the user asks. Always preview several options side by side, with their construction, before applying one. Full rules in `references/logo-and-icons.md`.
- Store screenshots, promo videos, GIFs and social images are built from the app's own stylesheets and markup, with example data instead of anyone's real files, at the store's largest required size. Full rules in `references/marketing-assets.md`.

## Brand and theme management

Keep these configurable from the central theme: brand and accent colors; page, surface and component backgrounds; text colors; borders and separators; font families and scales; spacing and layout tokens; radii; elevation; transitions and easing; breakpoints; component variants and states. Theme changes edit shared definitions, never individual screens.

## Working in an existing codebase

1. Inspect structure, framework, target platforms, styling system, components, tokens, conventions.
2. Reuse existing components, classes and tokens.
3. Consolidate duplicated styling when safe.
4. Change the shared layer, not local overrides.
5. Preserve functionality, responsiveness, accessibility and behavior.
6. Avoid new dependencies, migrations and broad rewrites; do not introduce a new design system if one exists.
7. Avoid conflicting overrides, high specificity and repeated `!important`.

## Workflow

1. **Inspect** the project, platforms, framework, rendering engine and conventions.
2. **Ask** for palette and font (unless already defined).
3. **Plan** components, tokens, layout rules, size classes and states.
4. **Centralize** by defining or updating the shared source of truth.
5. **Implement** with existing components, tokens and shared styles.
6. **Validate** consistency, compact/medium/expanded sizes, input modalities, forms, loading and accessibility.
7. **Refine** by removing decoration, duplication, conflicting overrides and one-offs.
8. **Regression-check** shared style changes on every platform, in the real app's rendering engine.
9. **Preview before committing to identity changes.** For icons, logos, palettes and sidebar styles, show several options and let the user pick before changing the app.

Never claim validation or testing was done unless it was actually performed.

## Final rule

Centralize design decisions, reuse styling definitions, build consistent components, avoid inline styling and generic AI-generated design. Every screen on every platform follows the same design system and feels intentional, coherent, responsive and maintainable.

---
name: flutter-app-with-react-admin-architecture
description: Reference architecture for bootstrapping new Flutter mobile apps and React/Vite/Tailwind web admin panels, based on a proven cross-platform codebase. Use whenever the user is starting a new Flutter or React admin project, asking how to structure a Flutter app (layered architecture, Riverpod, GoRouter, Drift), wants a custom animated tab bar, needs Firebase Crashlytics on Android/iOS, is setting up Tailwind CSS v4 with Vite, needs responsive layout down to 320px, or wants theme/design-token conventions instead of hardcoded styles. Also trigger when the user mentions Flutter with Riverpod/GoRouter/Drift, or React with Vite/Tailwind v4 for an admin panel. Trigger even without the words "architecture" or "template" — e.g. "how should I structure my Flutter app", "build me a liquid tab bar", "set up Tailwind v4 with Vite", "add crash reporting to my Flutter app" all qualify.
---

# Flutter + React Cross-Platform App Architecture

A generalized engineering blueprint distilled from a real production codebase (a Flutter mobile app with companion React web admin panel). Use it to bootstrap new projects or to bring existing ones in line with these patterns — not as a rigid spec, but as a set of defaults that are known to work well together and that mirror each other across platforms (mobile app and web admin share design tokens, naming, and structural philosophy).

Treat every section below as a **default to adapt**, not a hardcoded requirement. Item counts, names, color tokens, and specific feature folders in the original source are illustrative — swap them for whatever the user's actual project needs, while keeping the underlying pattern intact.

## When to go deeper

This file covers the architecture at a level enough to start building immediately. For implementation-level detail, read the matching reference file before writing code:

| Topic | Read this when... |
|---|---|
| `references/tab-bar-animation.md` | Building any animated/custom bottom tab bar — drag math, Bezier blob morphing, style variants |
| `references/firebase-crashlytics.md` | Wiring up crash reporting — Dart error boundaries, Android Gradle, iOS Xcode build phases |
| `references/tailwind-v4-setup.md` | Setting up Tailwind CSS v4 in a Vite/React project — v4 has no config file, unlike v3 |
| `references/responsive-strategy.md` | Implementing responsive scaling for Flutter (320px+) or the web admin panel |
| `references/toolchain-versions.md` | Picking dependency/toolchain versions for a new Flutter project (Gradle, Kotlin, package pins) |

Read only what's relevant to the current task — don't load every reference for a question about one piece.

---

## 1. Flutter Project Structure (Layered Architecture)

Use a layered structure that separates UI, state, and data so features stay testable and swappable:

```
lib/
├── core/
│   ├── navigation/        # GoRouter setup, shell transitions
│   ├── theme/             # Light & dark tokens, asset bindings
│   ├── providers/         # Global provider configs (auth, prefs)
│   └── widgets/           # Global reusable widgets
├── data/
│   ├── local/             # Drift SQLite DB, DAOs
│   └── models/            # Serialization, domain models
├── features/              # One directory per feature
│   ├── home/
│   ├── calendar/
│   └── settings/
└── l10n/                  # Localization ARB files
```

**Layer responsibilities:**
- **UI**: `ConsumerWidget` / `ConsumerStatefulWidget`, consuming Riverpod providers. Shared widgets live in `core/widgets/`; feature-local widgets stay inside their feature folder.
- **Logic**: Riverpod with code generation (`@riverpod`). Owns state updates, caching, and auth reactions.
- **Data**: split by shape of data —
  - **Drift (SQLite)** for structured, queryable local data.
  - **SharedPreferences** for simple key-value settings (locale, theme, onboarding flags).
  - **Firestore + Firebase Auth** for cloud sync/backup and premium features.

This split matters because it lets you swap the persistence mechanism (e.g. SQLite → server sync) without touching UI code, and keeps Riverpod providers thin and testable.

## 2. Navigation (GoRouter)

Use GoRouter for declarative, URL-based routing with centralized guards rather than scattering auth/onboarding checks across individual screens.

**Guard pattern** — a single `RouterTransitionNotifier` reacts to state changes and redirects:
- **Onboarding guard**: incomplete onboarding → force `/onboarding`.
- **Auth/lock guard**: app-lock enabled + not authenticated → force `/lock`.
- **Premium guard**: gated features (e.g. notification settings) → redirect non-premium users to `/settings/subscribe`.

**Shell navigation without "sliding through" intermediate tabs**: when a `ShellRoute` wraps top-level tabs in a `PageView`-backed shell, jumping from tab 1 to tab 5 directly would visually slide through 2, 3, 4. Avoid this by:
1. Intercepting the navigation request.
2. If the jump distance > 1, temporarily swap the *adjacent* page in the `PageView` list for the *target* page.
3. Animate to the adjacent index (which now renders the target).
4. On completion, instantly jump the `PageController` to the real target index and restore original page order — invisibly, since the displayed content didn't change.

## 3. Custom Animated Tab Bar

Don't reach for default Material/Cupertino tab bars when the project wants a distinctive nav. Build a `CustomTabBar` that supports three interchangeable presentation styles (pick based on brand):

- **Glassmorphic liquid** (most distinctive): `BackdropFilter` blur + a Bezier-drawn liquid droplet indicator that stretches toward drag direction.
- **Normal/translucent**: simple translucent background, indicator is a rounded pill sliding behind the active tab.
- **Solid flat**: opaque background, indicator simplified to a dot or underline — best for minimal/classic designs.

Core interaction: a `GestureDetector` maps horizontal drag position to a continuous tab index (e.g. `0.0`–`4.0` for 5 tabs); during drag the indicator follows the touch directly and the page view scroll locks; on release, snap to the nearest index with an eased animation (~`380ms`, `Curves.easeOutQuad`).

See `references/tab-bar-animation.md` for the full Bezier math, velocity-based stretch calculation, and icon-scaling detail — read it before implementing any version of this component.

## 4. Mobile Responsiveness

Use a fixed virtual design width (e.g. `390px`) and scale the whole UI to it via `responsive_framework`, rather than hand-tuning breakpoints per widget. This keeps text, padding, and tap targets proportional from `320px` phones up through tablets, and avoids overflow banners.

```dart
builder: (context, child) => ResponsiveBreakpoints.builder(
  child: Builder(
    builder: (context) {
      final isMobile = ResponsiveBreakpoints.of(context).isMobile;
      final scaledChild = isMobile
          ? ResponsiveScaledBox(width: 390, child: child!)
          : child!;
      return Directionality(textDirection: TextDirection.ltr, child: scaledChild);
    },
  ),
  breakpoints: [
    const Breakpoint(start: 0, end: 450, name: MOBILE),
    const Breakpoint(start: 451, end: 800, name: TABLET),
    const Breakpoint(start: 801, end: 1920, name: DESKTOP),
  ],
)
```

Full breakdown (including the web admin panel's parallel responsive strategy) is in `references/responsive-strategy.md`.

## 5. Overflow Prevention

Default to these patterns any time a widget might receive more content than its parent can comfortably hold — this prevents the red/yellow overflow banners far more reliably than ad-hoc fixes:

- **`FittedBox(fit: BoxFit.scaleDown)`** around text/labels inside constrained cards or buttons — shrinks rather than clips.
- **`Flexible` / `Expanded`** for any text-bearing child inside a `Row`/`Column` — unbounded children are the most common overflow cause.
- **`LayoutBuilder`** or **`FractionallySizedBox`** for layouts that need to size relative to their parent (custom cards, charts).

## 6. Theme-Driven Design (No Hardcoded Styles)

Every visual value — color, radius, spacing, font — should resolve from one centralized theme config (e.g. `lib/core/theme/app_theme.dart`). Never inline hex codes or magic numbers in feature widgets; this is what lets the same visual system drive both the Flutter app and the React admin panel.

**Token categories to define:**
- `systemBG`, `systemBGSurface`, `systemBGElevated` — background and elevation layers.
- `brandAccent`, `brandPrimary` — primary brand/action colors.
- Semantic feedback colors — success/warning/info/error.
- Typography — pick a typeface family matching the product's personality (geometric/clean vs. rounded/friendly), declared once, used everywhere.
- Geometric tokens — `radiusSM/MD/LG/XL` and an 8pt spacing grid.

## 7. Custom Vector Assets Only

Forbid raw emoji, generic Material icons, and unicode symbols in product UI — they undercut a premium/branded feel. Instead:

- Define every icon/illustration as an SVG string constant in one file (e.g. `lib/core/theme/app_assets.dart`), rendered via `SvgPicture.string(...)`.
- Use `currentColor` or opacity parameters in the SVG so icons inherit parent color/animation state automatically (important for active-tab color interpolation, etc.).
- Group by purpose: decorative icons, action/navigation glyphs, larger illustrations for empty states/onboarding.

## 8. Firebase & Native Crash Reporting

Wire up both Dart-level and native-level error capture from day one — see `references/firebase-crashlytics.md` for the full `main()` setup, Android Gradle Kotlin DSL plugin block, and the iOS Xcode Run Script build phase (with exact input paths) needed for dSYM symbolication.

## 9. React Web Admin Panel (Vite + Tailwind v4)

When the companion web admin panel is React, default to **Vite + TypeScript + Tailwind CSS v4** rather than CRA or Tailwind v3 — v4 drops the `tailwind.config.js` file entirely in favor of an `@theme` block in CSS, which makes it much easier to mirror the Flutter app's design tokens directly (e.g. `--color-brand-accent: var(--app-accent-color)`). Full setup steps, including the Vite plugin and CSS import change, are in `references/tailwind-v4-setup.md`.

For the admin layout itself: flex-row sidebar + main content, sidebar collapses to an overlay under `768px`, card grids step down via `grid-cols-1 → md:grid-cols-2 → lg:grid-cols-3`, and tight breakpoints (`max-width: 480px`) shrink wrapper padding to `16px` to preserve usable space on small screens.

## 10. Toolchain & Dependency Defaults

When scaffolding a new Flutter project in this style, check `references/toolchain-versions.md` for the pinned Gradle/Kotlin/AGP versions and the known-stable version ranges for `firebase_core`, `flutter_riverpod`, `drift`, `go_router`, and `responsive_framework`. Treat these as a starting point — verify against current released versions if the project is starting fresh, since pins age quickly.

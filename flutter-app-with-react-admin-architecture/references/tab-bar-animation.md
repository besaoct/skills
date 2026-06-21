# Animated Custom Tab Bar — Implementation Detail

Read this when actually implementing a `CustomTabBar`, not just discussing it at a high level.

```
       [Item 1]   [Item 2]       [Item 3]       [Item 4]      [Item 5]
         │            │              │             │             │
   ┌─────┼────────────┼──────────────┼─────────────┼─────────────┼─────┐
   │     │            │      💧      │             │             │     │ <-- Customizable Bar (Dynamic Items)
   └─────────────────────────▲─────────────────────────────────────────┘
                       Active Indicator
```

The number of items, names, and icons are fully configurable — adapt the count to whatever the project needs (this is not locked to 5 tabs).

## 1. Drag Interaction & Math

- A `GestureDetector` tracks horizontal drag locations on the tab bar.
- `onHorizontalDragUpdate` maps the local horizontal coordinate `dx` to a normalized value between `0.0` and `N-1.0` (for `N` tabs — e.g. `0.0` to `4.0` for 5 tabs).
- During an active drag, the active indicator follows the drag coordinate (`_dragPosition`) directly, while the `PageView` scroll is **locked** to prevent the page content fighting the indicator for control.
- On release, the indicator snaps to the nearest tab index using `Curves.easeOutQuad` over `380ms`.

## 2. Dynamic Shape Morphing (`WaterDropPainter`)

Only relevant for the **glassmorphic liquid** style variant. The shape is drawn on a `CustomPaint` canvas using Bezier curves.

**Quiescent blob (idle state):** when at rest, paint an organic, slightly asymmetrical circle using the standard cubic Bezier kappa approximation constant `0.552284` (the standard constant for approximating a circle with 4 cubic Bezier curves).

**Directional water drop (moving state):** as the indicator moves, calculate the real-time velocity delta (`pos - prevPos`):
- Moving **right**: pinch and drag the tail to the left; expand the front "nose" on the right.
- Moving **left**: pinch and drag the tail to the right; expand the front "nose" on the left.
- The degree of horizontal stretch (`stretchWidth`) and vertical flattening (`stretchHeight`) is proportional to `sin(diff * pi)`, where `diff` is the fractional distance to the next tab. This makes the stretch peak at the midpoint of the transition and ease back to zero as it settles on a tab — rather than stretching linearly, which looks mechanical.

**Organic icon scaling:** tab icons scale up (`1.25x`) and color-interpolate in real time as the indicator approaches them, giving instant visual feedback before the snap completes.

## 3. Style Variants

Pick one based on the project's branding — these are meant to be interchangeable behind the same `CustomTabBar` API, not three separate components:

| Style | Background | Indicator |
|---|---|---|
| **Glassmorphic liquid** (default/most distinctive) | `BackdropFilter` with `ImageFilter.blur(sigmaX: 20.0, sigmaY: 20.0)` | Bezier-drawn liquid droplet (`CustomPaint`) |
| **Normal/translucent** | Standard translucent container (e.g. `Colors.white.withOpacity(0.85)` or `Colors.black87`), no backdrop filter | Rounded pill (`BoxDecoration(borderRadius: BorderRadius.circular(8.0))`) sliding behind the active tab |
| **Solid flat** | Solid, fully opaque color with border/shadow elevation | Simple dot or underline beneath the active icon — best for classic minimal UI |

Default to the glassmorphic liquid style only when the product wants a distinctive, premium feel worth the extra implementation complexity. For most admin tools or utility apps, normal/translucent or solid flat is the better default — don't over-engineer the nav bar for a project that doesn't need it.

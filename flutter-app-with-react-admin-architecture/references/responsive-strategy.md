# Responsive Strategy — Flutter App + Web Admin Panel

Read this when implementing responsiveness on either platform. Both follow the same underlying philosophy (scale/reflow proportionally rather than hand-tune per breakpoint) but use different mechanisms.

## Flutter Mobile App: Fixed Virtual Width + Auto-Scale

Use `responsive_framework` to scale the entire UI to a virtual base design width, rather than writing per-widget breakpoint logic.

```dart
builder: (context, child) => ResponsiveBreakpoints.builder(
  child: Builder(
    builder: (context) {
      final isMobile = ResponsiveBreakpoints.of(context).isMobile;
      // Auto-scale all mobile layouts to a base design width of 390px
      final scaledChild = isMobile
          ? ResponsiveScaledBox(
              width: 390,
              child: child!,
            )
          : child!;
      return Directionality(
        textDirection: TextDirection.ltr,
        child: scaledChild,
      );
    },
  ),
  breakpoints: [
    const Breakpoint(start: 0, end: 450, name: MOBILE),
    const Breakpoint(start: 451, end: 800, name: TABLET),
    const Breakpoint(start: 801, end: 1920, name: DESKTOP),
  ],
)
```

**Why this works:** scaling everything to a virtual `390px` base means small viewports (down to `320px`) and larger tablet displays scale text, padding, and tap targets proportionally — instead of clipping content or requiring separate layouts per breakpoint. The 390px figure matches a common modern phone width (e.g. iPhone 14); adjust it to match the actual design files if they use a different base.

Combine this with the overflow-prevention patterns (`FittedBox`, `Flexible`/`Expanded`, `LayoutBuilder`) from the main SKILL.md — scaling alone doesn't prevent overflow if widgets still have unbounded children.

## Web Admin Panel: Flex Layout + Tailwind Breakpoints

The admin panel targets viewports down to **320px** without horizontal scrollbars, using a more traditional responsive-web approach (since CSS doesn't have an equivalent to uniform UI scaling):

- **Layout wrapper**: `.dashboard-body` with `display: flex; flex-direction: row;`, wrapping a sidebar and main content block.
- **Sidebar collapse**: below `768px`, the sidebar becomes an overlay, toggled via a hamburger button — it doesn't just shrink in place.
- **Grid columns**: card lists use `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6` so columns stack automatically rather than needing manual breakpoint-specific layouts.
- **Margins & padding**: at `@media (max-width: 480px)`, reduce wrapper margins/padding down to `16px` to reclaim screen space on small phones.
- **Selectors**: hide text labels on dropdowns/selectors at `<= 480px`, showing only the icon; pair with `text-overflow: ellipsis` and `white-space: nowrap` on the underlying `<select>` to prevent the control itself from wrapping awkwardly.

Adjust the specific breakpoint pixel values to match the project's actual design system — `768px`/`480px` here are defaults from this reference codebase, not universal constants.

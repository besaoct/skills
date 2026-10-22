# Rendering engine gotchas

Read this when the app renders web content in an engine you are not previewing in: a Tauri or Electron app on
macOS (WebKit), an iOS or Android webview, or an older browser. Each item is a bug that looks fine in desktop Chrome
and breaks in the real app. Fix it in the shared styles or components, never per screen.

## Contents
- Flex and grid
- Colors
- Scrollbars
- Observers and animation
- Dialogs
- Selects, numbers and native chrome
- Testing in the real engine

## Flex and grid
- `flex: 1` means a basis of 0%. In a column flex container whose height is not fixed (a dialog with `max-height`),
  WebKit sizes that child to nothing, so a dialog body or form disappears. Use `flex: 1 1 auto` with `min-height: 0`
  for scrollable bodies.
- A form inside a height-limited scroller lays out more reliably as a grid (`display: grid; align-content: start;
  grid-template-columns: minmax(0, 1fr)`) than as a flex column, which WebKit can redistribute, leaving gaps.
- Side-by-side fields with labels on top use `align-items: flex-start`, or their labels sit at different heights.
- A spacer element meant to push items apart needs `flex: 1` in every container it is used in, not just one.

## Colors
- Use literal values per theme for text levels, borders, tints and scrollbars. `color-mix()` needs Safari 16.2 or later.
- A translucent tint over a surface can be an absolutely positioned `::before` layer with `opacity`, instead of a
  mixed color.
- `::backdrop` does not inherit custom properties on older WebKit. Declare the variables it uses on `::backdrop`
  itself, before any media query that overrides them.

## Scrollbars
- WebKit only repaints styled `::-webkit-scrollbar` parts on hover, so a thumb meant to show while scrolling never
  appears. Hide native scrollbars (`scrollbar-width: none` and `::-webkit-scrollbar { display: none }`) and draw an
  overlay thumb: one fixed element per scroller, positioned from `scrollTop`, `scrollHeight` and `clientHeight`,
  shown on the `scroll` event (listen with `capture: true`, `passive: true` on the document) and hidden after about
  900ms. For scrollers inside a modal dialog, append the thumb to the dialog, because the top layer paints above the
  page.
- Nested scrollers: do not set `overscroll-behavior: contain` on an inner scroller if its container may also need to
  scroll, or the bottom of the page becomes unreachable.

## Observers and animation
- Call `IntersectionObserver.observe()` only after the elements are attached to the document; elements observed
  while detached may never report.
- A hidden window or background tab does not run frames, so reveal animations and observers pause. Do not debug
  "nothing appears" in a hidden preview pane.
- Make every reveal idempotent: remember what was shown so a resize or re-render does not replay it.

## Dialogs
- `showModal()` puts the dialog in the top layer with an inset of 0. To keep it inside the content area, set `left`
  on the dialog and on its `::backdrop` to the sidebar width, and cap `max-width` to the space that is left.
- Anchor the dialog with a fixed `top` instead of vertical centering when its content changes size.

## Selects, numbers and native chrome
- `appearance: none` on selects, then add the chevron as a background image. A data URI cannot read CSS variables,
  so keep one chevron token per theme.
- Number inputs: `appearance: textfield` plus `::-webkit-inner-spin-button, ::-webkit-outer-spin-button
  { -webkit-appearance: none; margin: 0 }` removes the steppers.

## Testing in the real engine
- Before calling a layout done, open it in the shipped app (or its exact webview) and look at it, including dialogs,
  collapsed and expanded sections, the smallest window size and the light theme.
- On macOS a native app window can be captured with `screencapture -l <window id>`; on other platforms use the
  framework's screenshot or devtools in the real webview.

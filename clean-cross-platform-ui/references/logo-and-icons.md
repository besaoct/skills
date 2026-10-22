# Logos and app icons

Read this when designing or changing a logo, an app icon, a menu bar or tray icon, or a favicon.

## Contents
- Process
- Construction
- Sizes and variants
- Generation
- Avoid

## Process
1. Ask what the mark should suggest (the product's job, not its name), and whether letters are wanted.
2. Show 6 to 8 options at once, each at app-icon size on a dark and a light tile, at sidebar size (about 18 to 26)
   and as a one-color menu bar or tray icon at 16. Small sizes decide; a mark that only works large is rejected.
3. When the user narrows down, show the shortlist again with its construction drawn on a grid (circles, centers,
   angles), so the logic is visible.
4. Only then apply it everywhere at once: app icon, sidebar mark, tray icon, favicon, docs.

## Construction
- Work on a fixed grid (for example 32 units) with one module `m` (for example 2 units). Every radius, stroke, gap
  and offset is a multiple or simple fraction of `m`.
- Angles are round: multiples of 15 or 22.5 degrees. Relationships are deliberate: an element pointing at the center
  of an opening, three points forming an equilateral triangle, a path that passes through a center.
- Sequences shrink by one ratio, for example the golden ratio: radius `m * phi^-k`, opacity `phi^-k`, with equal gaps
  measured along the path.
- One accent shape and one neutral shape is usually enough. The accent carries the product's color; the neutral
  uses the text color so the mark follows the theme.
- Scale every option to the same bounding box (for example 24 of 32 units, 12 modules) so options compare fairly and
  the final mark sits at a consistent optical size.

## Sizes and variants
- macOS app icon: a 1024 canvas with an 824 tile at 100, corner radius about 190, a subtle surface fill and a hairline
  border in the border token. The mark's box fills about 62 percent of the tile.
- Menu bar or tray: a template image, black on transparent, so the OS tints it. Trim the view box to the mark plus a
  little margin; render at 2x (for example 36 for an 18pt item). Gaps and cuts must survive in one color.
- Sidebar or in-app mark: the accent shape in the accent color, the neutral shapes in the text color, inline as SVG so
  it follows the theme.
- Windows `.ico`: store PNG entries (16, 24, 32, 48, 64, 256), not bitmaps; bitmap entries make the file ten times
  larger.

## Generation
- Keep the geometry in one script (for example `scripts/logo.py`) that writes every SVG variant, and one script that
  renders every raster size and container format (`.icns` through `iconutil`, `.ico`, PNGs). A change is then one
  number and one command.
- Write the rules into the script's header comment in plain words, so the next person can see why each value is what
  it is.
- Commit the generated files too, so builds do not need the tools.

## Avoid
- Letters or monograms unless asked, sparkle and star glyphs, gradients on the mark itself, glow, drop shadows, and
  details thinner than about 1/16 of the icon at 16px.
- Marks that depend on color to be read: the one-color tray version is the test.

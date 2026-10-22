# Suppressing hover, focus, outline and press effects by platform

Read this when implementing the "no interaction chrome" override for a specific framework. Apply the suppression in the shared control component or global style, never per screen.

## Contents
- Web and desktop webview
- Tailwind
- React Native
- Flutter
- SwiftUI / iOS / macOS
- Jetpack Compose / Android
- Electron, Tauri, Windows, Linux

## Web and desktop webview
Put this once in the global stylesheet, using tokens:

```css
button, input, select, textarea, a, [role="button"], [role="tab"], [role="menuitem"] {
  outline: none;
  -webkit-tap-highlight-color: transparent;
}
button:focus, input:focus, select:focus, textarea:focus { outline: none; box-shadow: none; }
```
- Do not write `:hover`, `:focus-visible` or `:active` rules for controls.
- Reset browser appearance where it adds chrome (`appearance: none` on selects and inputs), then restyle through the shared control classes.
- Borders use the single border token, e.g. `border: 1px solid var(--color-border)`.

## Tailwind
- Add `outline-none focus:outline-none focus:ring-0` to the shared control component classes only, not at call sites.
- Do not use `hover:`, `focus:`, `focus-visible:` or `active:` variants on controls.
- Define the border color as a theme token (e.g. `border-subtle`) with low opacity.

## React Native
- Use `Pressable` with no pressed-style callback; do not use `TouchableOpacity` (it dims on press) or set `activeOpacity={1}` if it is used.
- Android ripple: leave `android_ripple` unset on `Pressable`.
- Set `underlayColor="transparent"` on `TouchableHighlight` if present.
- Provide a shared `Button`/`Input` component that centralizes this.

## Flutter
- Set `splashFactory: NoSplash.splashFactory`, `splashColor`, `highlightColor`, `hoverColor`, `focusColor` all to `Colors.transparent` in `ThemeData`.
- Button styles: `overlayColor: WidgetStateProperty.all(Colors.transparent)`.
- Inputs: set `focusedBorder`, `enabledBorder` to the same low-opacity border so nothing changes on focus.
- Use `FocusNode` visuals sparingly; do not draw focus rings.

## SwiftUI / iOS / macOS
- Use `.buttonStyle(.plain)` or a custom `ButtonStyle` that ignores `configuration.isPressed`.
- macOS: `.focusEffectDisabled()` (macOS 14+ / iOS 17+) on controls and containers.
- For `TextField`, use `.textFieldStyle(.plain)` and draw the border yourself with the border token.
- UIKit: avoid `adjustsImageWhenHighlighted` effects and set highlight states to match normal states.

## Jetpack Compose / Android
- Replace the default ripple: provide `LocalIndication provides NoIndication` (or `Indication` that draws nothing) and use `MutableInteractionSource` with `indication = null` on `clickable`.
- Material 3: set `RippleConfiguration` to a transparent ripple, or use a theme with `LocalRippleConfiguration provides null`.
- TextField: set `focusedIndicatorColor`/`unfocusedIndicatorColor` to the same low-opacity border color so nothing changes on focus.

## Electron, Tauri, Windows, Linux
- Electron and Tauri render web content: use the web rules.
- WinUI/WPF: override control templates to remove `PointerOver`, `Pressed` and `Focused` visual states, or map them to the Normal appearance. Set `UseSystemFocusVisuals="False"` and `FocusVisualStyle="{x:Null}"`.
- GTK/Qt: remove `:hover`, `:focus` and `:active` rules from the stylesheet for controls and set `outline: none` / `outline-style: none` equivalents.

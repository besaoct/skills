---
name: production-ui-ux-and-centralized-styling
description: Rules for building polished, production-quality UI/UX with a centralized styling system (design tokens, themes, shared components), consistent control and focus styling, accessibility, and avoidance of generic AI-generated design patterns. Use whenever building, modifying, or reviewing websites, storefronts, admin panels, or application interfaces and their styling.
---

# Production-Quality UI/UX and Centralized Styling Rules

## 1. Core objective

Build polished, production-ready websites and applications with intentional visual design, excellent UI/UX, consistent styling, maintainable architecture, and a distinctive product identity.

Avoid generic AI-generated design patterns, unnecessary decoration, inconsistent components, duplicated styling, and one-off visual decisions.

All styling, design tokens, themes, typography, component variants, and reusable visual rules must be centralized in a clearly organized styling system. Individual pages and components should consume this system rather than independently defining their appearance.

These are default rules unless the user explicitly requests otherwise or the project requirements justify a different approach.

## 2. Mandatory centralized styling architecture

Before implementing or modifying UI, inspect the existing project structure, styling framework, design system, shared components, and conventions. Extend the existing architecture instead of introducing a competing system.

Organize styling into dedicated files and folders according to the project's framework.

A typical structure could be:

```text
src/
├── styles/
│   ├── tokens.css
│   ├── theme.css
│   ├── typography.css
│   ├── global.css
│   ├── utilities.css
│   └── components/
│       ├── buttons.css
│       ├── forms.css
│       ├── cards.css
│       ├── dialogs.css
│       ├── navigation.css
│       ├── tables.css
│       └── feedback.css
├── components/
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Checkbox.tsx
│   │   ├── Textarea.tsx
│   │   └── ...
│   └── ...
└── ...
```

This is an illustrative structure, not a requirement to create every file in every project. Adapt it to the existing framework and application size.

### Centralization requirements

- Define colors, typography, font sizes, font weights, spacing, radii, borders, shadows, transitions, breakpoints, and elevation in centralized design tokens.
- Keep light and dark themes, when supported, in a centralized theme system.
- Keep reusable component styling and variants in shared stylesheets, Tailwind component classes, design-system components, or equivalent framework-specific locations.
- Use semantic tokens such as `--color-primary`, `--color-surface`, `--color-border`, `--text-primary`, `--radius-control`, and `--spacing-section` instead of scattering raw values across files.
- Ensure buttons, inputs, selects, checkboxes, textareas, cards, dialogs, navigation, and other shared elements use the same established design rules.
- Centralize shared layout patterns, container widths, section spacing, responsive behavior, and typography scales.
- Use the existing project's naming conventions and design tokens. Do not create redundant tokens that represent the same concept.
- Import global styles and theme definitions through the appropriate application entry point.
- Make changes to a shared token or component style propagate consistently throughout the application wherever that token or component is used.

The intended result: changing a shared color, radius, font, spacing value, or component style should update all relevant parts of the UI without manually editing numerous page and component files.

## 3. No scattered or unnecessary inline styling

Avoid defining visual styles independently inside every page, component, or element.

Do not use inline styles for ordinary visual presentation when the styling can be represented by a shared class, design token, reusable component, or existing styling utility.

Avoid patterns such as:

```tsx
<div style={{ padding: 24, borderRadius: 12, background: "#ffffff" }}>
  ...
</div>
```

Prefer a centralized styling approach:

```tsx
<div className="content-panel">
  ...
</div>
```

Define `.content-panel` and its design tokens in the appropriate shared styling files.

### Framework-specific rules

**Tailwind CSS**

- Use existing theme tokens and configured design values.
- Reuse shared components and component classes for repeated patterns.
- Extract recurring combinations of utility classes into reusable components or appropriate shared class definitions.
- Avoid repeating long, nearly identical utility strings across many files.
- Avoid arbitrary values when a shared token or standard scale is appropriate.
- Do not replace Tailwind with custom CSS unnecessarily.

**CSS Modules, Sass, or standard CSS**

- Keep component styles in their designated stylesheets.
- Use centralized tokens for shared values.
- Reuse shared classes and component variants instead of duplicating declarations.

**CSS-in-JS or other styling frameworks**

- Use the framework's supported theme, token, variant, and composition mechanisms.
- Keep reusable styling definitions centralized.
- Do not scatter independent styling configurations throughout the application.

### Exceptions

Inline styles or dynamic style values are acceptable when they are genuinely required for runtime-generated values, such as chart coordinates, calculated dimensions, dynamic progress, or user-configurable properties that cannot reasonably be represented by predefined classes.

Do not prohibit inline styles mechanically when a dynamic value is necessary. Keep the underlying design rules centralized.

## 4. Reusable components and design consistency

Create or extend shared UI components when the same interface pattern appears in multiple places.

Examples include:

- Buttons and icon buttons
- Text inputs, password inputs, and search fields
- Selects, checkboxes, radio buttons, switches, and textareas
- Form labels, validation messages, and help text
- Cards, panels, and content containers
- Dialogs, drawers, popovers, and dropdown menus
- Tables, pagination, and data lists
- Badges, alerts, notifications, and toasts
- Tabs, breadcrumbs, navigation, and menus
- Loading indicators, skeletons, empty states, and error states

Requirements:

- Use shared components instead of recreating the same controls on individual pages.
- Support deliberate, documented variants such as primary, secondary, danger, compact, or large when needed.
- Keep variants visually consistent across the application.
- Use semantic HTML and accessible component APIs.
- Preserve the project's existing libraries and architecture unless a change is justified.
- Avoid creating abstractions for components that are genuinely unique or too simple to benefit from one.
- When a shared component changes, verify that existing usages remain compatible.

## 5. Input, button, and focus styling

Avoid browser-default outlines, prominent focus rings, and unwanted borders around inputs and interactive controls. Keep controls visually clean, deliberate, and consistent with the design system.

Apply this rule consistently to:

- Buttons and icon buttons
- Text and password inputs
- Search fields
- Select elements and dropdown triggers
- Checkboxes and radio buttons
- Textareas
- Switches, tabs, and other interactive controls

### Required behavior

- Remove unwanted default outlines and decorative focus rings where appropriate.
- Do not automatically use thick, brightly colored, glowing, or oversized focus rings.
- Avoid inconsistent focus styles between native controls and custom components.
- Define control borders, backgrounds, radii, and interaction states centrally.
- Provide subtle, intentional hover, active, selected, disabled, invalid, and focus states.
- Keep form controls visually consistent in size, spacing, typography, and alignment.
- Avoid layout shifts when borders or states change.
- Ensure focus styles do not obscure content or create unnecessary visual clutter.

### Accessibility requirement

Do not eliminate keyboard focus visibility entirely.

If default outlines or rings are removed, provide an alternative, centralized `:focus-visible` treatment that is subtle and consistent with the design system. It may use a controlled border-color change, background change, inset indicator, or another accessible visual treatment.

For example, use a shared focus style instead of applying unrelated outlines and rings throughout the application.

Keyboard users must still be able to identify the active control. Maintain sufficient contrast and distinguish focus from hover and selected states.

For native selects, dropdown options, checkboxes, and radio buttons, account for browser and operating-system rendering differences. Style what the platform supports reliably, and use accessible custom controls only when there is a real need.

## 6. Anti-vibecoding rules: avoid these by default

Do not automatically introduce the following patterns unless explicitly requested or justified by the product, existing brand, accessibility, or usability.

1. **Harsh gradients:** Avoid excessive or decorative high-contrast gradients.
2. **Lucide icons everywhere:** Do not default to one icon library for every interface. Reuse existing project assets or the most appropriate icon system.
3. **Pure white backgrounds everywhere:** Select background colors deliberately. White remains valid when appropriate.
4. **Rainbow coloring:** Avoid arbitrary, unrelated accent colors.
5. **Drop shadows everywhere:** Use elevation only when it communicates hierarchy or separation.
6. **Three feature cards in every row:** Choose layouts based on content and information hierarchy.
7. **Emojis as UI icons:** Use suitable assets and icons unless emojis suit the product.
8. **Liquid glass:** Avoid unnecessary glassmorphism, blur, and translucent surfaces.
9. **Em dashes:** Avoid em dashes in UI copy and marketing text by default.
10. **Inter, Geist, or Space Grotesk by default:** Choose typography based on the brand, readability, language support, and existing design system.
11. **Decorative colored left stripes:** Use them only when they convey status or meaningful hierarchy.
12. **Fake testimonials:** Never invent customer quotes, ratings, logos, reviews, or success metrics.
13. **Bento grids everywhere:** Use varied card grids only when the content benefits from them.
14. **Decorative terminal windows:** Do not add fake terminal interfaces or code snippets merely to look technical.
15. **"It's not X, it's Y" copywriting:** Avoid repetitive, generic contrast-based marketing formulas.
16. **Checkmark bullets everywhere:** Use list markers appropriate to the content.
17. **Exactly three pricing tiers:** Reflect the real pricing model rather than forcing a template.
18. **Generic product mockups instead of real demos:** Prefer genuine product evidence and realistic workflows when available. Never misrepresent a mockup as a live product.
19. **Soft rounded corners on everything:** Use a deliberate, consistent radius scale appropriate to each component.
20. **Purple and black by default:** Choose the palette based on the brand and product.
21. **Missing skeleton loaders:** Implement appropriate loading states. Skeletons are useful when they improve perceived performance, but are not mandatory for every operation.
22. **Decorative radial orbs:** Avoid unnecessary glowing circles and blurred backgrounds.
23. **Decorative dot grids:** Do not use technical grids as generic filler.
24. **Sparkle icons everywhere:** Use AI-themed symbols only when they communicate a real feature or suit the brand.
25. **Animated arrows everywhere:** Animate only when motion communicates direction or interaction.
26. **Missing Terms of Service:** Include appropriate legal terms when required by the product, business model, or applicable law.
27. **Missing Privacy Policy:** Provide an appropriate privacy policy when applicable and ensure it accurately reflects actual data practices.
28. **Unnecessary hover animations:** Avoid animating every component. Respect reduced-motion preferences.
29. **Neon colors by default:** Avoid excessive saturation and glow unless they are intentional brand elements.
30. **Generic pastel palettes by default:** Do not choose pastel colors merely because they look modern.

These are not absolute prohibitions. Use any of these patterns when the requirements, brand, or existing design system justify them.

## 7. UI/UX quality requirements

### Visual hierarchy

- Establish clear relationships between page titles, section headings, body text, labels, metadata, and primary actions.
- Use consistent typography scales, line heights, spacing, and content widths.
- Avoid making every element equally prominent.
- Keep the interface readable, balanced, and appropriate to the amount of content.

### Layout and spacing

- Use a consistent spacing scale.
- Centralize page containers, maximum widths, section gaps, and grid definitions.
- Avoid arbitrary margins and padding repeated throughout the codebase.
- Use responsive layouts that adapt naturally to mobile, tablet, and desktop.
- Avoid horizontal overflow, cramped layouts, and unnecessarily large empty spaces.

### Interaction design

- Make primary and secondary actions clear.
- Provide appropriate hover, active, focus, disabled, selected, loading, and validation states.
- Use animations sparingly and consistently.
- Make touch targets practical for mobile devices.
- Prevent accidental interactions and confusing navigation.
- Do not use color as the only way to communicate status.

### Forms

- Keep labels, inputs, validation messages, and help text consistently aligned.
- Provide useful error messages and preserve entered values when appropriate.
- Avoid unexpected focus rings, inconsistent input heights, and changing dimensions between states.
- Maintain accessible keyboard navigation and focus visibility.

### Loading and feedback

- Implement appropriate loading, success, error, empty, and disabled states.
- Prevent duplicate submissions where necessary.
- Provide meaningful feedback for user actions.
- Do not show skeletons, spinners, or animations without a functional reason.

### Responsive design

- Follow the existing responsive breakpoints and layout conventions.
- Test navigation, forms, dialogs, tables, cards, and primary actions at relevant screen sizes.
- Use consistent behavior across devices without forcing desktop layouts onto mobile screens.

### Accessibility

- Use semantic HTML and correct accessible names.
- Maintain sufficient color contrast.
- Support keyboard navigation and visible keyboard focus.
- Respect reduced-motion settings.
- Avoid inaccessible custom controls and unnecessary interaction complexity.

## 8. Brand and theme management

Keep the visual identity configurable from centralized theme files or the project's equivalent design-token configuration.

Centralize:

- Brand and accent colors
- Page, surface, and component backgrounds
- Primary and secondary text colors
- Borders and separators
- Typography families and scales
- Spacing and layout tokens
- Border-radius values
- Elevation and shadow levels
- Transition durations and easing
- Breakpoints and responsive layout values
- Component variants and interaction states

When a theme change is requested, update the relevant shared definitions instead of manually changing individual pages.

Do not introduce a second source of truth for the same token or component style.

## 9. Existing project and codebase rules

Before making changes:

1. Inspect the repository structure and identify the framework, styling system, shared components, tokens, and conventions.
2. Reuse existing components, classes, and design tokens wherever possible.
3. Identify duplicated styling and consolidate it when safe.
4. Make changes at the appropriate shared styling layer.
5. Preserve existing functionality, responsiveness, accessibility, and component behavior.
6. Avoid unnecessary dependencies, framework migrations, and broad rewrites.
7. Do not introduce a new design system if a suitable one already exists.

When modifying an existing feature, change its shared styles or component variants wherever possible rather than adding local overrides.

Avoid accumulating conflicting CSS overrides, excessive specificity, repeated `!important` declarations, or duplicated utility classes.

## 10. Implementation and verification workflow

For each UI implementation or substantial modification:

1. **Inspect:** Understand the existing project and its design conventions.
2. **Plan:** Identify the reusable components, tokens, layout rules, and states involved.
3. **Centralize:** Define or update styles at the shared source of truth.
4. **Implement:** Build the interface using existing components, reusable classes, and design tokens.
5. **Validate:** Check visual consistency, responsive behavior, interactions, forms, loading states, and accessibility.
6. **Refine:** Remove unnecessary decoration, duplicated styling, conflicting overrides, and one-off visual decisions.
7. **Regression-check:** Ensure changes to shared styles have not broken other components or pages.

Do not claim that UI validation or testing was completed unless it was actually performed.

## Final rule

Centralize design decisions. Reuse styling definitions. Build consistent components. Avoid unnecessary inline styling. Avoid generic AI-generated design patterns by default.

Every page and component must follow the same underlying design system while retaining the flexibility needed for its specific purpose.

The objective is not to make every interface look identical. It is to make the entire product feel intentionally designed, visually coherent, accessible, responsive, maintainable, and production-ready, with styling changes controlled through a small, well-organized set of shared files.

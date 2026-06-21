# Tailwind CSS v4 + Vite Setup

Read this when setting up or troubleshooting Tailwind in a new React/Vite web admin project.

## Why v4 changes the setup

Unlike Tailwind v3, **v4 does not use a `tailwind.config.js` file at all.** Configuration — custom colors, radii, fonts — lives directly in CSS via `@theme` blocks. If you find yourself creating a `tailwind.config.js` for a v4 project, stop — that's a v3 pattern that doesn't apply here.

## Setup Steps

**1. Install dependencies:**
```bash
npm install tailwindcss @tailwindcss/vite
```

**2. Add the Vite plugin (`vite.config.ts`):**
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
});
```

**3. Import Tailwind in CSS (`src/index.css`):**

Remove any `@tailwind base/components/utilities` directives (v3 pattern) and replace with a single import:
```css
@import "tailwindcss";
```

**4. Define theme tokens with `@theme`:**

This is the key v4 mechanism for custom design tokens. When the project has a companion Flutter app, mirror its theme variables here so both platforms draw from the same visual system:

```css
@theme {
  /* Theme variables mapped to mirror the Flutter app's visual system */
  --color-brand-primary: var(--app-bg-color);    /* Matches Flutter's systemBG */
  --color-brand-accent: var(--app-accent-color);  /* Matches Flutter's brandAccent */
  --radius-custom-xl: var(--app-radius-xl);       /* Matches Flutter's radiusXL */
}
```

These become usable as standard Tailwind utility classes (e.g. `bg-brand-primary`, `rounded-custom-xl`) — no separate config-file mapping step needed like in v3.

## Common Mistake to Avoid

Don't mix v3 and v4 patterns — e.g. don't write both a `tailwind.config.js` *and* `@theme` blocks. Pick v4's CSS-native approach fully, or the build will silently ignore one set of tokens.

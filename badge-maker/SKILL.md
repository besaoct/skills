---
name: badge-maker
description: Use this skill whenever the user wants to create pill-shaped icon+label badges — language selector badges, status badges (Live/Beta/New), tag chips, category labels, or similar small rounded UI badges with an icon square on the left and a text label on the right. Trigger this for requests like "make a badge for X", "create language badges", "design a status pill", "make tag chips for my site", or any request to recreate/extend badges shown in an uploaded screenshot. Always use this skill's interview flow (ask about badge content, colors, and layout) rather than guessing at colors or shapes — it produces transparent PNGs via a tested font pipeline that downloads the exact font needed for whatever text the user wants (Devanagari, Bengali, Arabic, Tamil, Thai, Hebrew, CJK, and more) and renders it with correct shaping, which a generic approach will get wrong.
---

# Badge maker

Produces pill-shaped badges: a colored icon square (short text/glyph) on the left,
a text label on the right, on a rounded pill background. Outputs transparent PNGs,
both individually and combined into a layout. Built to correctly render ~30
scripts (Devanagari, Bengali, Arabic, Tamil, Thai, Hebrew, CJK, and more) via
fonts fetched on demand based on the actual text in the badge, with proper
shaping (conjuncts/joining/matras) — don't try to render this text another way
(e.g. raw SVG `<text>` with a generic font) since shaping will break.

## Workflow — follow these steps in order, one question at a time

Use `ask_user_input_v0` for each step so the user can tap instead of type. Don't
skip ahead or assume answers — but if the user has already specified something
in their initial message (e.g. they pasted exact text and colors), skip the
question for that and confirm your assumption briefly instead.

### Step 1 — What goes in each badge
Ask what the user wants in the badge(s): the icon text/glyph (e.g. a 2-letter
code, initial, or symbol) and the label text, for each badge they want. If they
uploaded a reference image, extract the icon/label pairs from it first and confirm
rather than re-asking from scratch.

If many badges are needed (e.g. a full language list), it's fine to gather the
full list as a single open text answer rather than one-by-one.

### Step 2 — Badge background and text color
Ask for:
- Badge (pill) background color
- Text/label color
Offer a few sensible preset options (e.g. "White bg / coral text (like the
reference)", "Dark bg / white text", "Custom hex") plus a custom option.

### Step 3 — Icon square styling
Ask if the icon square should use a different background/text color than the
label, or match the overall scheme. If different, ask for the icon background
hex and icon text color hex.

### Step 4 — Repeat for additional badges with different styling
If the user has multiple badges that need *different* color schemes from each
other (not all uniform), loop steps 2–3 per badge or per group. Otherwise apply
one scheme to all badges.

### Step 5 — Delivery and shape options
Ask:
1. Individual badge files, a combined sheet, or both?
2. If combined: which layout?
   - **Row** — single line, tight gaps (good for ≤4 badges)
   - **Grid** — wraps into rows of N columns
   - **Triangle** — pyramid (1 badge, then 2, then 3, ...), centered
   - Mention these are the available layouts; let the user pick or describe
     something else (e.g. "circle", "staggered") and adapt the script's layout
     functions if so.

## Execution

1. View `/mnt/skills/.../badge-maker/scripts/badge_gen.py` if you haven't already
   to recall the JSON spec format (documented in its module docstring).
2. Build a spec JSON capturing every badge with: `name`, `icon_text`, `icon_bg`,
   `icon_text_color`, `label_text`, `label_text_color`, `badge_bg`, and `rtl`
   (only set `rtl: true` explicitly if the script's auto-detection might be wrong;
   otherwise omit it — Arabic/Hebrew text auto-detects as RTL).
3. Write the spec to a working file, e.g. `/home/claude/badge_spec.json`.
4. Run: `python3 /mnt/skills/.../badge-maker/scripts/badge_gen.py /home/claude/badge_spec.json`
   (use the actual mounted skill path — check with the available_skills listing
   or the path this SKILL.md was loaded from).
5. The script auto-detects the Unicode script of every icon/label string and
   downloads the matching Noto font on demand from a verified GitHub source
   (requires network access to github.com, already on the allowlist) — Latin
   is the only font bundled in the skill itself, since it covers most requests
   and keeps the skill small. ~30 scripts are covered this way: Devanagari,
   Bengali, Arabic, Tamil, Telugu, Kannada, Malayalam, Gujarati, Gurmukhi,
   Oriya, Sinhala, Thai, Lao, Hebrew, Myanmar, Khmer, Georgian, Armenian,
   Ethiopic, Thaana, Syriac, Javanese, Balinese, Cherokee, Bamum, Vai, N'Ko,
   Ogham, Runic, Mongolian, Tibetan, and CJK (Simplified/Traditional Chinese,
   Japanese, Korean). Fetched fonts are cached in the skill's
   `assets/fonts_cache/` so repeat use doesn't re-download.
   - If a script can't be downloaded (network issue, or genuinely unsupported),
     the script falls back to DejaVu Sans Bold and prints a warning to stderr —
     check for and relay this warning to the user rather than silently shipping
     a badge that may render as boxes/tofu.
   - Plain Han-ideograph text (Kanji-only Japanese, or Chinese with no kana/
     hangul present) is ambiguous by Unicode alone. Pass an explicit `"script"`
     field in that badge's spec entry (e.g. `"script": "japanese"` or
     `"chinese-traditional"`) whenever the user's badge is specifically for
     Japanese or Traditional Chinese, since glyph shapes can differ from the
     Simplified-Chinese default.
6. Copy the requested output files (individual and/or combined) to
   `/mnt/user-data/outputs/` and use `present_files`.
7. Before presenting, glance at the combined PNG against a dark backdrop to sanity
   check transparency and that text isn't clipped — render
   `Image.new('RGBA', size, (30,30,30,255))` composited under the result and view it,
   rather than assuming.

## Verifying text accuracy

Before generating, if the user provided translated label text (e.g. language
names in their own script) and you're not fully confident it's correct/standard
spelling, do a quick web search to verify rather than trusting it blindly or
trusting your own recall for less-common languages — small spelling errors are
easy to miss visually but obvious to native readers.

## Notes on the visual design

The default look (matching the original reference this skill was built from):
icon square ~64px with rx ~40% (rounded square, not full circle), pill height
96px, pink/coral `#DE5E70` on white, generous internal padding. Keep these
proportions unless the user asks for a different shape — e.g. a fully circular
icon badge, square (non-pill) badges, or a different aspect ratio. For shape
changes beyond color/layout, edit `badge_gen.py`'s `make_badge()` function rather
than trying to hack it from outside (e.g. change `icon_radius` calculation for a
circle, or `pill_h_px / 2` radius for a non-pill rounded-rect).

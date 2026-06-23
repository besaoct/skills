# badge-maker

A Claude skill for generating pill-shaped icon+label badges — language
selector badges, status pills (Live/Beta/New), tag chips, category labels,
and similar small rounded UI badges — as transparent PNGs.

## What it does

- Walks through a short interview: what goes in each badge, badge/text
  colors, icon styling, and delivery format (individual files, a combined
  sheet, or both — in a row, grid, or triangle/pyramid layout).
- Renders text with correct script shaping. Only Latin is bundled; every
  other script's font (Devanagari, Bengali, Arabic, Tamil, Thai, Hebrew,
  CJK, and ~20 more) is fetched on demand from Google Fonts via GitHub
  based on the actual text you give it, then cached locally.
- Outputs clean transparent PNGs sized and styled to match a reference
  pill/icon-square aesthetic (customizable colors throughout).

## Install

Download `badge-maker.skill` (or zip this folder yourself) and install it
in your Claude environment's skills directory.

## Structure

```
badge-maker/
├── SKILL.md              — the skill definition (interview flow + execution steps)
├── scripts/
│   └── badge_gen.py       — the generator (see its docstring for the JSON spec format)
└── assets/
    └── fonts/
        └── Inter_bold.ttf — the only bundled font; everything else fetches on demand
```

See `SKILL.md` for the full workflow and `scripts/badge_gen.py`'s module
docstring for the JSON spec the script consumes.

## License

Inter is licensed under the SIL Open Font License. Fonts fetched on demand
(Noto family, via the google/fonts GitHub mirror) are also OFL-licensed.

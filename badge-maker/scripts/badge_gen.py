#!/usr/bin/env python3
"""
badge_gen.py - Generate pill-shaped icon+label badges (language-selector style,
status badges, tag chips, etc.) as transparent PNGs, individually and combined.

Usage:
    python3 badge_gen.py spec.json

spec.json shape:
{
  "output_dir": "/home/claude/badges/out",
  "scale": 4,
  "badges": [
    {
      "name": "english",                 // used for individual filename
      "icon_text": "EN",
      "icon_bg": "#DE5E70",
      "icon_text_color": "#FFFFFF",
      "label_text": "English",
      "label_text_color": "#DE5E70",
      "badge_bg": "#FFFFFF",
      "rtl": false,
      "font": "auto",                    // "auto" picks by script, or give a path
      "script": null                     // optional override, e.g. "japanese",
                                          // "chinese-traditional" — needed when
                                          // text is plain Han ideographs with no
                                          // kana/hangul, since Unicode alone can't
                                          // tell Japanese-Kanji-only / Traditional /
                                          // Simplified Chinese apart (see resolve_font)
    },
    ...
  ],
  "layout": "row" | "grid" | "triangle" | "individual_only",
  "grid_cols": 3,
  "gap": 16,
  "padding": 10,
  "combined_name": "combined_badges"
}

Only Latin (Inter) is bundled, since it's needed by almost every badge and is
small. Every other script's font is downloaded on demand, based on what text is
actually used in the badge spec you give it, then cached in assets/fonts_cache/
so repeat runs (or other badges using the same script) don't re-download. This
keeps the skill's footprint small while still covering ~30 scripts accurately,
with correct text shaping (conjuncts, joining forms, matras) via PIL's raqm
layout engine.
"""

import sys
import os
import json
import unicodedata
import subprocess

from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(SCRIPT_DIR, "..", "assets", "fonts")
CACHE_DIR = os.path.join(SCRIPT_DIR, "..", "assets", "fonts_cache")

# Only Latin is bundled — every badge needs it, and it's small.
BUNDLED_FONTS = {
    "latin": os.path.join(FONTS_DIR, "Inter_bold.ttf"),
}

# Script -> exact, verified raw-file URL on the google/fonts GitHub mirror.
# Confirmed reachable (HTTP 200) at the time this skill was built. If Google
# Fonts reorganizes these paths, see fetch_noto_font()'s fallback attempts.
GITHUB_BASE = "https://github.com/google/fonts/raw/main/ofl"
NOTO_SOURCES = {
    "devanagari": f"{GITHUB_BASE}/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf",
    "bengali": f"{GITHUB_BASE}/notosansbengali/NotoSansBengali%5Bwdth%2Cwght%5D.ttf",
    "arabic": f"{GITHUB_BASE}/notosansarabic/NotoSansArabic%5Bwdth%2Cwght%5D.ttf",
    "tamil": f"{GITHUB_BASE}/notosanstamil/NotoSansTamil%5Bwdth%2Cwght%5D.ttf",
    "telugu": f"{GITHUB_BASE}/notosanstelugu/NotoSansTelugu%5Bwdth%2Cwght%5D.ttf",
    "kannada": f"{GITHUB_BASE}/notosanskannada/NotoSansKannada%5Bwdth%2Cwght%5D.ttf",
    "malayalam": f"{GITHUB_BASE}/notosansmalayalam/NotoSansMalayalam%5Bwdth%2Cwght%5D.ttf",
    "gujarati": f"{GITHUB_BASE}/notosansgujarati/NotoSansGujarati%5Bwdth%2Cwght%5D.ttf",
    "gurmukhi": f"{GITHUB_BASE}/notosansgurmukhi/NotoSansGurmukhi%5Bwdth%2Cwght%5D.ttf",
    "oriya": f"{GITHUB_BASE}/notosansoriya/NotoSansOriya%5Bwdth%2Cwght%5D.ttf",
    "sinhala": f"{GITHUB_BASE}/notosanssinhala/NotoSansSinhala%5Bwdth%2Cwght%5D.ttf",
    "thai": f"{GITHUB_BASE}/notosansthai/NotoSansThai%5Bwdth%2Cwght%5D.ttf",
    "lao": f"{GITHUB_BASE}/notosanslao/NotoSansLao%5Bwdth%2Cwght%5D.ttf",
    "hebrew": f"{GITHUB_BASE}/notosanshebrew/NotoSansHebrew%5Bwdth%2Cwght%5D.ttf",
    "myanmar": f"{GITHUB_BASE}/notosansmyanmar/NotoSansMyanmar%5Bwdth%2Cwght%5D.ttf",
    "khmer": f"{GITHUB_BASE}/notosanskhmer/NotoSansKhmer%5Bwdth%2Cwght%5D.ttf",
    "georgian": f"{GITHUB_BASE}/notosansgeorgian/NotoSansGeorgian%5Bwdth%2Cwght%5D.ttf",
    "armenian": f"{GITHUB_BASE}/notosansarmenian/NotoSansArmenian%5Bwdth%2Cwght%5D.ttf",
    "ethiopic": f"{GITHUB_BASE}/notosansethiopic/NotoSansEthiopic%5Bwdth%2Cwght%5D.ttf",
    "thaana": f"{GITHUB_BASE}/notosansthaana/NotoSansThaana%5Bwght%5D.ttf",
    "syriac": f"{GITHUB_BASE}/notosanssyriac/NotoSansSyriac%5Bwght%5D.ttf",
    "javanese": f"{GITHUB_BASE}/notosansjavanese/NotoSansJavanese%5Bwght%5D.ttf",
    "balinese": f"{GITHUB_BASE}/notosansbalinese/NotoSansBalinese%5Bwght%5D.ttf",
    "cherokee": f"{GITHUB_BASE}/notosanscherokee/NotoSansCherokee%5Bwght%5D.ttf",
    "bamum": f"{GITHUB_BASE}/notosansbamum/NotoSansBamum%5Bwght%5D.ttf",
    "vai": f"{GITHUB_BASE}/notosansvai/NotoSansVai-Regular.ttf",
    "nko": f"{GITHUB_BASE}/notosansnko/NotoSansNKo-Regular.ttf",
    "ogham": f"{GITHUB_BASE}/notosansogham/NotoSansOgham-Regular.ttf",
    "runic": f"{GITHUB_BASE}/notosansrunic/NotoSansRunic-Regular.ttf",
    "mongolian": f"{GITHUB_BASE}/notosansmongolian/NotoSansMongolian-Regular.ttf",
    "tibetan": f"{GITHUB_BASE}/notoseriftibetan/NotoSerifTibetan%5Bwght%5D.ttf",
    "chinese-simplified": f"{GITHUB_BASE}/notosanssc/NotoSansSC%5Bwght%5D.ttf",
    "chinese-traditional": f"{GITHUB_BASE}/notosanstc/NotoSansTC%5Bwght%5D.ttf",
    "japanese": f"{GITHUB_BASE}/notosansjp/NotoSansJP%5Bwght%5D.ttf",
    "korean": f"{GITHUB_BASE}/notosanskr/NotoSansKR%5Bwght%5D.ttf",
}

UNICODE_BLOCK_TO_SCRIPT = [
    (0x0900, 0x097F, "devanagari"),
    (0x0980, 0x09FF, "bengali"),
    (0x0600, 0x06FF, "arabic"),
    (0x0750, 0x077F, "arabic"),
    (0x08A0, 0x08FF, "arabic"),
    (0xFB50, 0xFDFF, "arabic"),
    (0xFE70, 0xFEFF, "arabic"),
    (0x0B80, 0x0BFF, "tamil"),
    (0x0C00, 0x0C7F, "telugu"),
    (0x0C80, 0x0CFF, "kannada"),
    (0x0D00, 0x0D7F, "malayalam"),
    (0x0A80, 0x0AFF, "gujarati"),
    (0x0A00, 0x0A7F, "gurmukhi"),
    (0x0B00, 0x0B7F, "oriya"),
    (0x0D80, 0x0DFF, "sinhala"),
    (0x0E00, 0x0E7F, "thai"),
    (0x0E80, 0x0EFF, "lao"),
    (0x0590, 0x05FF, "hebrew"),
    (0x1000, 0x109F, "myanmar"),
    (0x1780, 0x17FF, "khmer"),
    (0x10A0, 0x10FF, "georgian"),
    (0x0530, 0x058F, "armenian"),
    (0x1200, 0x137F, "ethiopic"),
    (0x0780, 0x07BF, "thaana"),
    (0x0700, 0x074F, "syriac"),
    (0xA980, 0xA9DF, "javanese"),
    (0x1B00, 0x1B7F, "balinese"),
    (0x13A0, 0x13FF, "cherokee"),
    (0xA6A0, 0xA6FF, "bamum"),
    (0xA500, 0xA63F, "vai"),
    (0x07C0, 0x07FF, "nko"),
    (0x1680, 0x169F, "ogham"),
    (0x16A0, 0x16FF, "runic"),
    (0x1800, 0x18AF, "mongolian"),
    (0x0F00, 0x0FFF, "tibetan"),
    (0x4E00, 0x9FFF, "chinese-simplified"),  # CJK unified ideographs;
    (0x3400, 0x4DBF, "chinese-simplified"),  # default to SC unless kana/hangul
]                                            # also appear (see detect_script)


def detect_script(text):
    # Pass 1: look for script-distinguishing ranges first (kana, hangul) so
    # mixed CJK text resolves to the right Noto family instead of defaulting
    # to Simplified Chinese.
    for ch in text:
        cp = ord(ch)
        if 0x3040 <= cp <= 0x30FF:
            return "japanese"
        if 0xAC00 <= cp <= 0xD7AF or 0x1100 <= cp <= 0x11FF:
            return "korean"
    for ch in text:
        cp = ord(ch)
        for lo, hi, name in UNICODE_BLOCK_TO_SCRIPT:
            if lo <= cp <= hi:
                return name
    return "latin"


def fetch_noto_font(script):
    """
    Download the Noto font for `script` from the verified GitHub source, cache
    it locally, and return the path. Returns None if download fails (caller
    falls back to DejaVu and should warn the user).
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    cached = os.path.join(CACHE_DIR, f"{script}.ttf")
    if os.path.exists(cached) and os.path.getsize(cached) > 1000:
        return cached

    url = NOTO_SOURCES.get(script)
    if not url:
        return None

    raw_path = os.path.join(CACHE_DIR, f"{script}_raw.ttf")
    try:
        r = subprocess.run(
            ["curl", "-sL", "-o", raw_path, url, "--max-time", "20", "-f"],
            capture_output=True,
        )
        if r.returncode != 0 or not os.path.exists(raw_path) or os.path.getsize(raw_path) < 1000:
            if os.path.exists(raw_path):
                os.remove(raw_path)
            print(f"  warning: failed to download font for script '{script}' from {url}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"  warning: error downloading font for script '{script}': {e}", file=sys.stderr)
        return None

    # Variable fonts need instancing to a static weight for predictable
    # rendering (and so PIL doesn't default to the thinnest master).
    try:
        from fontTools.ttLib import TTFont
        from fontTools.varLib.instancer import instantiateVariableFont

        f = TTFont(raw_path)
        if "fvar" in f:
            axes = {a.axisTag: 700 if a.axisTag == "wght" else a.defaultValue for a in f["fvar"].axes}
            # prefer normal width if a width axis exists
            for a in f["fvar"].axes:
                if a.axisTag == "wdth":
                    axes["wdth"] = 100
            instantiateVariableFont(f, axes, inplace=True)
        f.save(cached)
    except Exception as e:
        # fontTools instancing failed — use the raw file directly, it's still
        # a valid (if variable) font that PIL/raqm can usually render.
        print(f"  note: using raw font for '{script}' without instancing ({e})", file=sys.stderr)
        os.replace(raw_path, cached)
        return cached

    if os.path.exists(raw_path):
        os.remove(raw_path)
    return cached if os.path.exists(cached) else None


def resolve_font(text, override_path=None, script_hint=None):
    """
    Returns (font_path, warning_or_None). Caller should surface the warning
    to the user if not None — it means the script fell back to a font that
    may not shape the text correctly.

    `script_hint` lets the caller force a specific Noto family (one of the
    NOTO_SOURCES keys, e.g. "japanese" or "chinese-traditional") when the
    text is plain Han ideographs with no kana/hangul markers — Unicode alone
    can't distinguish Japanese-only-Kanji / Traditional / Simplified Chinese
    in that case, so auto-detection defaults to Simplified. Pass a "script"
    field in the badge spec to override when this matters (glyph shapes do
    sometimes differ across these, e.g. some traditional/simplified pairs).
    """
    if override_path and override_path != "auto" and os.path.exists(override_path):
        return override_path, None
    script = script_hint or detect_script(text)
    if script in BUNDLED_FONTS:
        return BUNDLED_FONTS[script], None
    fetched = fetch_noto_font(script)
    if fetched:
        return fetched, None
    fallback = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    warning = (
        f"could not download a font for detected script '{script}' "
        f"(text: {text!r}); falling back to DejaVu Sans, which may not "
        f"shape this script correctly"
    )
    return fallback, warning


def hex_to_rgba(h, alpha=255):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, alpha)


def is_rtl_text(text):
    for ch in text:
        try:
            if unicodedata.bidirectional(ch) in ("R", "AL"):
                return True
        except Exception:
            pass
    return False


def make_badge(badge, scale=4):
    icon_text = badge["icon_text"]
    label_text = badge["label_text"]
    icon_bg = hex_to_rgba(badge.get("icon_bg", "#DE5E70"))
    icon_text_color = hex_to_rgba(badge.get("icon_text_color", "#FFFFFF"))
    label_text_color = hex_to_rgba(badge.get("label_text_color", badge.get("icon_bg", "#DE5E70")))
    badge_bg = hex_to_rgba(badge.get("badge_bg", "#FFFFFF"))
    rtl = badge.get("rtl", is_rtl_text(label_text))

    icon_font_path, icon_warning = resolve_font(
        icon_text, badge.get("icon_font", "auto"), script_hint=badge.get("script")
    )
    label_font_path, label_warning = resolve_font(
        label_text, badge.get("label_font", "auto"), script_hint=badge.get("script")
    )
    for w in (icon_warning, label_warning):
        if w:
            print(f"  warning [{badge.get('name', '?')}]: {w}", file=sys.stderr)

    pill_h = 96
    icon_box = 64
    pad_outer = 12
    gap_icon_text = 16
    pad_right = 28

    s = scale
    pill_h_px = pill_h * s
    icon_box_px = icon_box * s
    pad_outer_px = pad_outer * s
    gap_px = gap_icon_text * s
    pad_right_px = pad_right * s

    icon_font_size = int(34 * s)
    label_font_size = int(40 * s)

    icon_font = ImageFont.truetype(icon_font_path, icon_font_size)
    label_font = ImageFont.truetype(
        label_font_path, label_font_size, layout_engine=ImageFont.Layout.RAQM
    )

    tmp_img = Image.new("RGBA", (10, 10))
    tmp_draw = ImageDraw.Draw(tmp_img)

    label_bbox = tmp_draw.textbbox(
        (0, 0), label_text, font=label_font, direction=("rtl" if rtl else "ltr")
    )
    label_w = label_bbox[2] - label_bbox[0]
    label_h = label_bbox[3] - label_bbox[1]

    icon_bbox = tmp_draw.textbbox((0, 0), icon_text, font=icon_font)
    icon_w = icon_bbox[2] - icon_bbox[0]
    icon_h = icon_bbox[3] - icon_bbox[1]

    pill_w_px = pad_outer_px + icon_box_px + gap_px + label_w + pad_right_px
    canvas_w = int(pill_w_px) + 4 * s
    canvas_h = int(pill_h_px) + 4 * s

    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pill_x0, pill_y0 = 2 * s, 2 * s
    pill_x1 = pill_x0 + pill_w_px
    pill_y1 = pill_y0 + pill_h_px

    draw.rounded_rectangle(
        (pill_x0, pill_y0, pill_x1, pill_y1), radius=pill_h_px / 2, fill=badge_bg
    )

    icon_x0 = pill_x0 + pad_outer_px
    icon_y0 = pill_y0 + (pill_h_px - icon_box_px) / 2
    icon_x1 = icon_x0 + icon_box_px
    icon_y1 = icon_y0 + icon_box_px
    icon_radius = icon_box_px * 0.40

    draw.rounded_rectangle((icon_x0, icon_y0, icon_x1, icon_y1), radius=icon_radius, fill=icon_bg)

    icon_cx = (icon_x0 + icon_x1) / 2
    icon_cy = (icon_y0 + icon_y1) / 2
    draw.text(
        (icon_cx - icon_bbox[0] - icon_w / 2, icon_cy - icon_bbox[1] - icon_h / 2),
        icon_text,
        font=icon_font,
        fill=icon_text_color,
    )

    label_x0 = icon_x1 + gap_px
    label_cy = (pill_y0 + pill_y1) / 2
    draw.text(
        (label_x0 - label_bbox[0], label_cy - label_bbox[1] - label_h / 2),
        label_text,
        font=label_font,
        fill=label_text_color,
        direction=("rtl" if rtl else "ltr"),
    )

    final = img.resize((canvas_w // s, canvas_h // s), Image.LANCZOS)
    return final


def layout_row(images, gap, pad):
    row_h = max(im.height for im in images)
    total_w = sum(im.width for im in images) + gap * (len(images) - 1)
    canvas = Image.new("RGBA", (total_w + pad * 2, row_h + pad * 2), (0, 0, 0, 0))
    x = pad
    for im in images:
        canvas.paste(im, (x, pad + (row_h - im.height) // 2), im)
        x += im.width + gap
    return canvas


def layout_grid(images, cols, gap, pad):
    rows = [images[i : i + cols] for i in range(0, len(images), cols)]
    max_w = max(im.width for im in images)
    max_h = max(im.height for im in images)
    cell_w, cell_h = max_w + gap, max_h + gap
    canvas_w = cell_w * cols - gap + pad * 2
    canvas_h = cell_h * len(rows) - gap + pad * 2
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    for ri, row in enumerate(rows):
        for ci, im in enumerate(row):
            x = pad + ci * cell_w + (max_w - im.width) // 2
            y = pad + ri * cell_h + (max_h - im.height) // 2
            canvas.paste(im, (x, y), im)
    return canvas


def layout_triangle(images, gap, pad):
    # Build pyramid rows: 1, 2, 3, ... until images are consumed (or reverse if longer at top)
    n = len(images)
    rows = []
    i = 0
    row_size = 1
    while i < n:
        rows.append(images[i : i + row_size])
        i += row_size
        row_size += 1
    row_h = max(im.height for im in images)
    row_widths = [sum(im.width for im in r) + gap * (len(r) - 1) for r in rows]
    canvas_w = max(row_widths) + pad * 2
    canvas_h = row_h * len(rows) + gap * (len(rows) - 1) + pad * 2
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    y = pad
    for row, rw in zip(rows, row_widths):
        x = (canvas_w - rw) // 2
        for im in row:
            canvas.paste(im, (x, y + (row_h - im.height) // 2), im)
            x += im.width + gap
        y += row_h + gap
    return canvas


def main():
    spec_path = sys.argv[1]
    with open(spec_path) as f:
        spec = json.load(f)

    out_dir = spec.get("output_dir", "/home/claude/badges/out")
    os.makedirs(out_dir, exist_ok=True)
    scale = spec.get("scale", 4)

    images = []
    for badge in spec["badges"]:
        im = make_badge(badge, scale=scale)
        images.append(im)
        name = badge.get("name", "badge")
        path = os.path.join(out_dir, f"{name}.png")
        im.save(path)
        print(f"saved {path} ({im.size[0]}x{im.size[1]})")

    layout = spec.get("layout", "row")
    gap = spec.get("gap", 16)
    pad = spec.get("padding", 10)
    combined_name = spec.get("combined_name", "combined_badges")

    if layout == "individual_only":
        return

    if layout == "row":
        combined = layout_row(images, gap, pad)
    elif layout == "grid":
        combined = layout_grid(images, spec.get("grid_cols", 3), gap, pad)
    elif layout == "triangle":
        combined = layout_triangle(images, gap, pad)
    else:
        combined = layout_row(images, gap, pad)

    combined_path = os.path.join(out_dir, f"{combined_name}.png")
    combined.save(combined_path)
    print(f"saved {combined_path} ({combined.size[0]}x{combined.size[1]})")


if __name__ == "__main__":
    main()

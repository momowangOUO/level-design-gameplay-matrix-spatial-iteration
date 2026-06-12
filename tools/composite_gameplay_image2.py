from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from gameplay_image2_layouts import ANNOTATION_BOXES, EN_TEXT, EXTRA_CALLOUTS, LAYOUTS
from gameplay_image2_specs import SPECS


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets"
BASE_DIR = ASSET_DIR / "image2-generated-bases"
EN_ASSET_DIR = ASSET_DIR / "en"
EXPECTED_SIZE = (1672, 941)

FONT_REGULAR = "C:/Windows/Fonts/msyh.ttc"
FONT_BOLD = "C:/Windows/Fonts/msyhbd.ttc"

PALETTE = [
    (37, 99, 235),
    (22, 163, 74),
    (234, 88, 12),
    (220, 38, 38),
    (124, 58, 237),
    (202, 138, 4),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size=size)


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    if not text:
        return 0
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    if " " in text and sum(ord(ch) < 128 for ch in text) > len(text) * 0.7:
        lines: list[str] = []
        current = ""
        for word in text.split():
            candidate = word if not current else f"{current} {word}"
            if text_width(draw, candidate, fnt) <= max_width or not current:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return fix_orphan_punctuation(draw, lines, fnt, max_width)

    lines: list[str] = []
    current = ""
    for ch in text:
        candidate = current + ch
        if text_width(draw, candidate, fnt) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return fix_orphan_punctuation(draw, lines, fnt, max_width)


def fix_orphan_punctuation(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    fnt: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    if len(lines) < 2:
        return lines
    punctuation = "，。；：、,.!?;:"
    fixed: list[str] = []
    for line in lines:
        if fixed and line and line[0] in punctuation:
            candidate = fixed[-1] + line[0]
            if text_width(draw, candidate, fnt) <= max_width:
                fixed[-1] = candidate
                line = line[1:]
        if line:
            fixed.append(line)
    if len(fixed) >= 2 and fixed[-1] in punctuation:
        candidate = fixed[-2] + fixed[-1]
        if text_width(draw, candidate, fnt) <= max_width:
            fixed[-2] = candidate
            fixed.pop()
    return fixed


def label_text(text_spec: dict, index: int, lang: str) -> tuple[str, str]:
    title, body = text_spec["labels"][index]
    if lang == "zh":
        return title, body
    return title, body


def draw_text_fit(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    body: str,
    color: tuple[int, int, int],
    lang: str,
) -> None:
    x1, y1, x2, y2 = box
    pad_x = max(8, min(18, (x2 - x1) // 18))
    pad_y = max(5, min(12, (y2 - y1) // 8))
    max_w = max(20, x2 - x1 - pad_x * 2)
    max_h = max(12, y2 - y1 - pad_y * 2)
    body = body.rstrip("。.")
    if max_h < 46:
        body = ""

    title_sizes = [22, 20, 18, 16, 14, 12]
    body_sizes = [14, 13, 12, 11, 10]
    if lang == "en":
        title_sizes = [19, 18, 16, 14, 12]
        body_sizes = [12, 11, 10, 9]

    chosen: tuple[ImageFont.FreeTypeFont, ImageFont.FreeTypeFont, list[str], list[str]] | None = None
    for ts in title_sizes:
        tf = font(ts, True)
        title_lines = wrap(draw, title, tf, max_w)
        for bs in body_sizes:
            bf = font(bs)
            all_body_lines = wrap(draw, body, bf, max_w)
            if max_h < 34:
                body_lines = []
            elif max_h < 54:
                body_lines = all_body_lines[:1]
            elif max_h < 86:
                body_lines = all_body_lines[:2]
            else:
                body_lines = all_body_lines[:3]
            if len(body_lines) < len(all_body_lines) and body_lines:
                body_lines[-1] = body_lines[-1].rstrip("，、,;；:： ") + "..."
            needed = len(title_lines[:2]) * (tf.size + 2) + len(body_lines) * (bf.size + 3)
            if body_lines:
                needed += 3
            if needed <= max_h:
                chosen = (tf, bf, title_lines[:2], body_lines)
                break
        if chosen:
            break

    if chosen is None:
        tf = font(11, True)
        chosen = (tf, font(9), wrap(draw, title, tf, max_w)[:1], [])

    tf, bf, title_lines, body_lines = chosen
    y = y1 + pad_y
    for line in title_lines:
        draw.text((x1 + pad_x, y), line, fill=color, font=tf)
        y += tf.size + 2
    if body_lines:
        y += 2
    for line in body_lines:
        draw.text((x1 + pad_x, y), line, fill=(30, 41, 59), font=bf)
        y += bf.size + 3


def draw_badge(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    index: int,
    color: tuple[int, int, int],
) -> None:
    x1, y1, x2, y2 = box
    r = 13 if y2 - y1 >= 38 else 10
    cx = max(x1 + r + 3, min(x2 - r - 3, x1 + r + 5))
    cy = max(y1 + r + 3, min(y2 - r - 3, y1 + r + 5))
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color, outline=(255, 255, 255), width=2)
    fnt = font(14 if r >= 13 else 11, True)
    txt = str(index + 1)
    tw = text_width(draw, txt, fnt)
    draw.text((cx - tw / 2, cy - fnt.size / 2 - 1), txt, fill=(255, 255, 255), font=fnt)


def draw_annotation(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    body: str,
    index: int,
    lang: str,
    show_badge: bool = True,
) -> None:
    color = PALETTE[index % len(PALETTE)]
    x1, y1, x2, y2 = box

    # Reinforce only the reserved label field, not the artwork underneath.
    fill = (255, 255, 255, 224)
    outline = (*color, 210)
    radius = min(12, max(5, (y2 - y1) // 4))
    draw.rounded_rectangle((x1, y1, x2, y2), radius=radius, fill=fill, outline=outline, width=2)

    if show_badge:
        draw_badge(draw, box, index, color)
    text_box = (x1 + 28, y1 + 2, x2 - 5, y2 - 2) if show_badge and (x2 - x1) > 90 else (x1 + 8, y1 + 2, x2 - 8, y2 - 2)
    draw_text_fit(draw, text_box, title, body, color, lang)


def text_for(spec: dict, lang: str) -> dict:
    if lang == "en":
        return EN_TEXT[spec["stem"]]
    return spec


def composite(spec: dict, lang: str) -> Path | None:
    base_path = BASE_DIR / f"{spec['stem']}.base.png"
    if not base_path.exists():
        print(f"skip missing base: {base_path.name}")
        return None

    canvas = Image.open(base_path).convert("RGBA")
    if canvas.size != EXPECTED_SIZE:
        canvas = canvas.resize(EXPECTED_SIZE, Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(canvas)

    text_spec = text_for(spec, lang)
    boxes = ANNOTATION_BOXES[spec["stem"]]
    if len(boxes) != len(text_spec["labels"]):
        raise ValueError(f"{spec['stem']} has {len(text_spec['labels'])} labels but {len(boxes)} boxes")

    for i, box in enumerate(boxes):
        title, body = label_text(text_spec, i, lang)
        draw_annotation(draw, box, title, body, i, lang)

    for extra_i, (box, zh_text, en_text) in enumerate(EXTRA_CALLOUTS.get(spec["stem"], []), start=len(boxes)):
        title, body = zh_text if lang == "zh" else en_text
        draw_annotation(draw, box, title, body, extra_i, lang, show_badge=False)

    out_dir = EN_ASSET_DIR if lang == "en" else ASSET_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{spec['stem']}.png"
    canvas.convert("RGB").save(out_path, quality=96)
    print(f"wrote {lang}: {out_path.name}")
    return out_path


def write_layout_decisions() -> None:
    out_path = ASSET_DIR / "image2-layout-decisions.csv"
    rows = []
    for spec in SPECS:
        layout = LAYOUTS[spec["stem"]]
        rows.append(
            {
                "Diagram": spec["stem"],
                "Image2Slug": spec["slug"],
                "TextPlacement": "in_artwork_callouts",
                "BoxCount": len(ANNOTATION_BOXES[spec["stem"]]) + len(EXTRA_CALLOUTS.get(spec["stem"], [])),
                "Reason": f"{layout['reason']} 标注已回填到底图预留框或低干扰 callout 区，未再使用图外右栏。",
                "ChineseOutput": f"assets/{spec['stem']}.png",
                "EnglishOutput": f"assets/en/{spec['stem']}.png",
            }
        )
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {out_path.name}")


def make_contact_sheet(paths: list[Path], out_path: Path) -> None:
    thumbs: list[Image.Image] = []
    thumb_w, thumb_h = 520, 292
    foot_font = font(15)
    for path in paths:
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        frame = Image.new("RGB", (thumb_w, thumb_h + 34), (255, 255, 255))
        x = (thumb_w - img.width) // 2
        frame.paste(img, (x, 0))
        d = ImageDraw.Draw(frame)
        d.text((10, thumb_h + 8), path.name, fill=(15, 23, 42), font=foot_font)
        thumbs.append(frame)
    cols = 3
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + 34)), (245, 247, 250))
    for i, thumb in enumerate(thumbs):
        x = (i % cols) * thumb_w
        y = (i // cols) * (thumb_h + 34)
        sheet.paste(thumb, (x, y))
    sheet.save(out_path, quality=95)
    print(f"wrote {out_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*", help="render only the listed stems")
    parser.add_argument("--contact-sheet", action="store_true")
    parser.add_argument("--lang", choices=["zh", "en", "both"], default="both")
    args = parser.parse_args()

    wanted = set(args.only or [])
    zh_paths: list[Path] = []
    en_paths: list[Path] = []
    for spec in SPECS:
        if wanted and spec["stem"] not in wanted:
            continue
        if args.lang in ("zh", "both"):
            out = composite(spec, "zh")
            if out:
                zh_paths.append(out)
        if args.lang in ("en", "both"):
            out = composite(spec, "en")
            if out:
                en_paths.append(out)
    if args.contact_sheet and zh_paths:
        make_contact_sheet(zh_paths, ASSET_DIR / "_contactsheet_gameplay_matrix_image2.png")
    if args.contact_sheet and en_paths:
        make_contact_sheet(en_paths, EN_ASSET_DIR / "_contactsheet_gameplay_matrix_image2_en.png")
    write_layout_decisions()


if __name__ == "__main__":
    main()

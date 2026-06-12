from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from gameplay_image2_specs import SPECS


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets"
BASE_DIR = ASSET_DIR / "image2-generated-bases"
W, H = 1600, 900

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


F_TITLE = font(38, True)
F_SUB = font(22)
F_CARD_TITLE = font(25, True)
F_CARD_BODY = font(19)
F_BADGE = font(18, True)
F_FOOT = font(15)
F_GRID = font(13, True)


def fit_cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    nw, nh = math.ceil(iw * scale), math.ceil(ih * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))


def rounded_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: tuple[int, int, int, int],
    outline: tuple[int, int, int, int],
    width: int = 3,
    radius: int = 18,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> int:
    if not text:
        return 0
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
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
    return lines


def draw_text_block(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    max_width: int,
    line_gap: int = 4,
    max_lines: int | None = None,
) -> int:
    x, y = xy
    lines = wrap(draw, text, fnt, max_width)
    if max_lines is not None:
        lines = lines[:max_lines]
    line_h = fnt.size + line_gap
    for i, line in enumerate(lines):
        draw.text((x, y + i * line_h), line, fill=fill, font=fnt)
    return y + len(lines) * line_h


def draw_header(draw: ImageDraw.ImageDraw, spec: dict) -> None:
    rounded_panel(
        draw,
        (34, 24, 1060, 116),
        (255, 255, 255, 232),
        (15, 23, 42, 95),
        width=2,
        radius=20,
    )
    draw.text((58, 42), spec["title"], fill=(15, 23, 42), font=F_TITLE)
    draw.text((58, 88), spec["subtitle"], fill=(51, 65, 85), font=F_SUB)


def draw_precision_grid(draw: ImageDraw.ImageDraw) -> None:
    left, top, right, bottom = 40, 130, W - 40, H - 62
    for x in range(left, right + 1, 40):
        major = (x - left) % 160 == 0
        draw.line(
            [(x, top), (x, bottom)],
            fill=(30, 41, 59, 42 if major else 22),
            width=2 if major else 1,
        )
    for y in range(top, bottom + 1, 40):
        major = (y - top) % 160 == 0
        draw.line(
            [(left, y), (right, y)],
            fill=(30, 41, 59, 42 if major else 22),
            width=2 if major else 1,
        )

    badge = (W - 376, H - 118, W - 42, H - 72)
    rounded_panel(
        draw,
        badge,
        (255, 255, 255, 225),
        (71, 85, 105, 130),
        width=1,
        radius=12,
    )
    draw.text(
        (badge[0] + 14, badge[1] + 12),
        "40px 基准格 | 关键空间、路线、障碍按格对齐",
        fill=(51, 65, 85),
        font=F_GRID,
    )


def default_label_boxes(count: int) -> list[tuple[int, int, int, int]]:
    left_x, right_x = 42, 1196
    w, h = 362, 104
    boxes = [
        (left_x, 148, left_x + w, 148 + h),
        (left_x, 274, left_x + w, 274 + h),
        (left_x, 400, left_x + w, 400 + h),
        (right_x, 148, right_x + w, 148 + h),
        (right_x, 274, right_x + w, 274 + h),
        (right_x, 400, right_x + w, 400 + h),
        (left_x, 650, left_x + w, 650 + h),
        (right_x, 650, right_x + w, 650 + h),
    ]
    if count <= 4:
        return [boxes[0], boxes[1], boxes[3], boxes[4]][:count]
    if count == 5:
        return [boxes[0], boxes[1], boxes[3], boxes[4], (620, 756, 980, 846)]
    return boxes[:count]


def loop_label_boxes() -> list[tuple[int, int, int, int]]:
    return [
        (704, 94, 1032, 188),
        (1292, 144, 1540, 256),
        (1292, 394, 1542, 516),
        (1074, 690, 1404, 812),
        (552, 704, 880, 818),
        (284, 382, 572, 506),
    ]


def draw_label_cards(draw: ImageDraw.ImageDraw, spec: dict) -> None:
    labels = spec["labels"]
    if spec.get("label_layout") == "loop":
        boxes = loop_label_boxes()
    else:
        boxes = default_label_boxes(len(labels))

    for i, ((title, body), box) in enumerate(zip(labels, boxes)):
        color = PALETTE[i % len(PALETTE)]
        fill = (255, 255, 255, 226)
        outline = (*color, 210)
        rounded_panel(draw, box, fill, outline, width=3, radius=16)
        x1, y1, x2, _ = box
        badge_r = 15
        badge_cx, badge_cy = x1 + 26, y1 + 27
        draw.ellipse(
            (badge_cx - badge_r, badge_cy - badge_r, badge_cx + badge_r, badge_cy + badge_r),
            fill=(*color, 255),
        )
        draw.text(
            (badge_cx - 5, badge_cy - 12),
            str(i + 1),
            fill=(255, 255, 255),
            font=F_BADGE,
        )
        draw.text((x1 + 48, y1 + 14), title, fill=(15, 23, 42), font=F_CARD_TITLE)
        draw_text_block(
            draw,
            (x1 + 18, y1 + 50),
            body,
            F_CARD_BODY,
            (51, 65, 85),
            x2 - x1 - 36,
            line_gap=3,
            max_lines=2,
        )


def draw_footer(draw: ImageDraw.ImageDraw, spec: dict) -> None:
    rounded_panel(
        draw,
        (38, H - 46, W - 38, H - 18),
        (255, 255, 255, 215),
        (148, 163, 184, 110),
        width=1,
        radius=10,
    )
    footer = f"image2://{spec['slug']} | image2 底图 + 精确中文教学标注 | 读图：先看空间范例，再看编号标签，最后回写矩阵"
    draw.text((54, H - 41), footer, fill=(71, 85, 105), font=F_FOOT)


def composite(spec: dict) -> Path | None:
    base_path = BASE_DIR / f"{spec['stem']}.base.png"
    if not base_path.exists():
        print(f"skip missing base: {base_path.name}")
        return None

    base = Image.open(base_path).convert("RGB")
    canvas = fit_cover(base, (W, H)).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    draw_header(draw, spec)
    draw_precision_grid(draw)
    draw_label_cards(draw, spec)
    draw_footer(draw, spec)

    out = Image.alpha_composite(canvas, overlay).convert("RGB")
    out_path = ASSET_DIR / f"{spec['stem']}.png"
    out.save(out_path, quality=96)
    print(f"wrote {out_path.name}")
    return out_path


def make_contact_sheet(paths: list[Path], out_path: Path) -> None:
    thumbs: list[Image.Image] = []
    thumb_w, thumb_h = 520, 292
    for path in paths:
        img = Image.open(path).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        frame = Image.new("RGB", (thumb_w, thumb_h + 36), (255, 255, 255))
        x = (thumb_w - img.width) // 2
        frame.paste(img, (x, 0))
        d = ImageDraw.Draw(frame)
        d.text((10, thumb_h + 8), path.name, fill=(15, 23, 42), font=F_FOOT)
        thumbs.append(frame)
    cols = 3
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + 36)), (245, 247, 250))
    for i, thumb in enumerate(thumbs):
        x = (i % cols) * thumb_w
        y = (i // cols) * (thumb_h + 36)
        sheet.paste(thumb, (x, y))
    sheet.save(out_path, quality=95)
    print(f"wrote {out_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*", help="render only the listed stems")
    parser.add_argument("--contact-sheet", action="store_true")
    args = parser.parse_args()

    wanted = set(args.only or [])
    paths: list[Path] = []
    for spec in SPECS:
        if wanted and spec["stem"] not in wanted:
            continue
        out = composite(spec)
        if out:
            paths.append(out)
    if args.contact_sheet and paths:
        make_contact_sheet(paths, ASSET_DIR / "_contactsheet_gameplay_matrix_image2.png")


if __name__ == "__main__":
    main()

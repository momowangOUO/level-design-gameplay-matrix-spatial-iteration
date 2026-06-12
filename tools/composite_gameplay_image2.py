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


def draw_fit_line(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    color: tuple[int, int, int] = (30, 41, 59),
    bold: bool = False,
    max_size: int = 15,
    min_size: int = 9,
    anchor: str = "la",
) -> None:
    x1, y1, x2, y2 = box
    for size in range(max_size, min_size - 1, -1):
        fnt = font(size, bold)
        if text_width(draw, text, fnt) <= max(8, x2 - x1):
            break
    else:
        fnt = font(min_size, bold)
    if anchor == "mm":
        tw = text_width(draw, text, fnt)
        draw.text((x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - fnt.size) / 2 - 1), text, fill=color, font=fnt)
    else:
        draw.text((x1, y1), text, fill=color, font=fnt)


def draw_matrix_cell(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    text: str,
    color: tuple[int, int, int] = (51, 65, 85),
) -> None:
    if not text:
        return
    draw.rounded_rectangle((cx - 25, cy - 10, cx + 25, cy + 10), radius=5, fill=(255, 255, 255, 210))
    draw_fit_line(draw, (cx - 23, cy - 9, cx + 23, cy + 9), text, color=color, bold=True, max_size=13, min_size=9, anchor="mm")


def draw_publish_overlays(draw: ImageDraw.ImageDraw, stem: str, lang: str) -> None:
    """Fill image2 classroom blanks that would otherwise read as empty labels in GitHub."""
    if stem == "five-beat-blockout-exercise":
        beat_xs = [30, 380, 710, 1041, 1362]
        colors = PALETTE[:5]
        zh_items = [
            ["动作: 短跳", "障碍: 1格坑", "奖励: 旗帜", "反馈: 落点清楚"],
            ["动作: 连续跳", "障碍: 低尖刺", "奖励: 补给", "反馈: 节奏稳定"],
            ["动作: 变向跳", "障碍: 移动平台", "奖励: 星星", "反馈: 新条件"],
            ["动作: 组合执行", "障碍: 敌人+机关", "奖励: 治疗", "反馈: 死亡热区"],
            ["动作: 收束前进", "障碍: 低压力", "奖励: 出口门", "反馈: 节奏下降"],
        ]
        en_items = [
            ["Act: short jump", "Obs: 1u gap", "Reward: flag", "Feedback: clear landing"],
            ["Act: repeat jump", "Obs: low spikes", "Reward: supply", "Feedback: stable rhythm"],
            ["Act: vary jump", "Obs: moving platform", "Reward: star", "Feedback: new condition"],
            ["Act: combine", "Obs: enemy + switch", "Reward: health", "Feedback: death hotspot"],
            ["Act: close route", "Obs: low pressure", "Reward: exit door", "Feedback: pressure down"],
        ]
        items = zh_items if lang == "zh" else en_items
        for col, x in enumerate(beat_xs):
            for row, line in enumerate(items[col]):
                y = 393 + row * 24
                draw_fit_line(draw, (x + 34, y, x + 295, y + 18), line, color=colors[col], max_size=14 if lang == "zh" else 12)
        observations = (
            ["观测: 能否看见目标", "观测: 是否稳定通过", "观测: 是否理解变奏", "观测: 死亡是否集中", "观测: 是否自然回收"]
            if lang == "zh"
            else ["Observe: goal visible", "Observe: stable pass", "Observe: variation clear", "Observe: deaths clustered", "Observe: natural closure"]
        )
        for col, x in enumerate(beat_xs):
            draw_fit_line(draw, (x + 18, 584, x + 292, 610), observations[col], color=colors[col], bold=True, max_size=15 if lang == "zh" else 12, anchor="mm")

        table_zh = [
            ["短跳", "低", "-", "旗帜", "可见", "-"],
            ["连续", "低", "补", "箱", "-", "-"],
            ["变向", "中", "-", "星", "-", "-"],
            ["组合", "高", "补", "验证", "-", "锁"],
            ["收束", "低", "补", "门", "出口", "开"],
        ]
        table_en = [
            ["Jump", "Low", "-", "Flag", "Seen", "-"],
            ["Repeat", "Low", "HP", "Box", "-", "-"],
            ["Vary", "Mid", "-", "Star", "-", "-"],
            ["Combo", "High", "HP", "Check", "-", "Lock"],
            ["Close", "Low", "HP", "Door", "Exit", "Open"],
        ]
        table = table_zh if lang == "zh" else table_en
        cell_xs = [388, 458, 528, 598, 668, 738]
        cell_ys = [704, 736, 768, 800, 832]
        for r, row in enumerate(table):
            for c, value in enumerate(row):
                if value != "-":
                    draw_matrix_cell(draw, cell_xs[c], cell_ys[r], value, colors[r])

        notes = (
            ["B03 停留高 -> 提前露出落点", "B04 死亡高 -> 增加安全窗", "B05 回收长 -> 缩短出口线"]
            if lang == "zh"
            else ["B03 dwell high -> preview landing", "B04 deaths high -> add safety window", "B05 cleanup long -> shorten exit"]
        )
        for i, note in enumerate(notes):
            draw_fit_line(draw, (812, 722 + i * 33, 1158, 746 + i * 33), note, color=(30, 41, 59), max_size=17 if lang == "zh" else 13)

    elif stem == "precise-level-element-difficulty-metrics-matrix":
        headers = ["宽度", "路线", "敌人", "奖励", "视线", "资源"] if lang == "zh" else ["Width", "Route", "Enemy", "Reward", "Sight", "Supply"]
        x_centers = [126, 198, 270, 342, 414, 486]
        for x, label in zip(x_centers, headers):
            draw_fit_line(draw, (x - 32, 84, x + 32, 112), label, color=(255, 255, 255), bold=True, max_size=14 if lang == "zh" else 11, anchor="mm")
        rows_zh = [
            ["1格", "直", "-", "-", "遮", "-"],
            ["2格", "直", "低", "近", "中", "少"],
            ["3路", "绕", "中", "中", "长", "中"],
            ["-", "夹", "高", "-", "扇", "-"],
            ["-", "支", "中", "远", "露", "高"],
            ["-", "弯", "低", "近", "断", "-"],
            ["-", "支", "中", "近", "露", "密"],
        ]
        rows_en = [
            ["1u", "Direct", "-", "-", "Cover", "-"],
            ["2u", "Line", "Low", "Near", "Mid", "Few"],
            ["3r", "Loop", "Mid", "Mid", "Long", "Mid"],
            ["-", "Pinch", "High", "-", "Cone", "-"],
            ["-", "Branch", "Mid", "Far", "Open", "High"],
            ["-", "Bend", "Low", "Near", "Break", "-"],
            ["-", "Branch", "Mid", "Near", "Open", "Dense"],
        ]
        rows = rows_zh if lang == "zh" else rows_en
        y_centers = [140, 174, 208, 242, 276, 310, 344]
        row_colors = [(37, 99, 235), (20, 184, 166), (22, 163, 74), (220, 38, 38), (202, 138, 4), (124, 58, 237), (234, 88, 12)]
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                if value != "-":
                    draw_fit_line(draw, (x_centers[c] - 30, y_centers[r] - 11, x_centers[c] + 30, y_centers[r] + 11), value, color=row_colors[r], bold=True, max_size=13 if lang == "zh" else 10, anchor="mm")

    elif stem == "level-design-pitfalls-correction-board":
        labels = (
            [("问题图", (48, 846, 104, 866), (220, 38, 38)), ("修正图", (48, 882, 104, 902), (22, 163, 74)),
             ("症状", (144, 846, 214, 866), (37, 99, 235)), ("原因", (144, 882, 214, 902), (71, 85, 105)),
             ("低", (278, 851, 304, 870), (37, 99, 235)), ("高", (392, 851, 418, 870), (220, 38, 38)),
             ("问题密度", (316, 883, 404, 902), (71, 85, 105)),
             ("图例: 动作 / 风险 / 补给 / 奖励 / 出口 / 门锁 / 证据", (514, 862, 1002, 886), (51, 65, 85))]
            if lang == "zh"
            else [("Issue", (48, 846, 104, 866), (220, 38, 38)), ("Fix", (48, 882, 104, 902), (22, 163, 74)),
                  ("Symptom", (144, 846, 214, 866), (37, 99, 235)), ("Cause", (144, 882, 214, 902), (71, 85, 105)),
                  ("Low", (278, 851, 304, 870), (37, 99, 235)), ("High", (392, 851, 418, 870), (220, 38, 38)),
                  ("Density", (316, 883, 404, 902), (71, 85, 105)),
                  ("Legend: action / risk / supply / reward / exit / lock / evidence", (514, 862, 1002, 886), (51, 65, 85))]
        )
        for text, box, color in labels:
            draw_fit_line(draw, box, text, color=color, bold=True, max_size=16 if lang == "zh" else 12, anchor="mm")

    elif stem == "telemetry-heatmap-matrix-writeback":
        labels = (
            [("死亡", (184, 600, 236, 624), (220, 38, 38)), ("停留", (432, 600, 484, 624), (202, 138, 4)),
             ("绕路", (670, 600, 722, 624), (124, 58, 237)), ("样本线", (852, 600, 914, 624), (71, 85, 105))]
            if lang == "zh"
            else [("Death", (184, 600, 236, 624), (220, 38, 38)), ("Dwell", (432, 600, 484, 624), (202, 138, 4)),
                  ("Detour", (670, 600, 722, 624), (124, 58, 237)), ("Sample", (852, 600, 914, 624), (71, 85, 105))]
        )
        for text, box, color in labels:
            draw_fit_line(draw, box, text, color=color, bold=True, max_size=15 if lang == "zh" else 11, anchor="mm")


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

    draw_publish_overlays(draw, spec["stem"], lang)

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

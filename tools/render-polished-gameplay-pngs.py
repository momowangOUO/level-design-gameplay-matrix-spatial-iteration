from __future__ import annotations

import csv
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets"
W, H = 1600, 900
GRID = 40
OX, OY = 80, 150

COLORS = {
    "ink": (24, 30, 38),
    "muted": (92, 103, 118),
    "grid": (224, 230, 238),
    "major": (199, 208, 220),
    "blue": (33, 139, 230),
    "cyan": (24, 184, 214),
    "green": (81, 168, 108),
    "orange": (237, 132, 50),
    "yellow": (246, 198, 64),
    "red": (218, 68, 83),
    "purple": (126, 98, 191),
    "wall": (31, 35, 42),
    "panel": (247, 249, 252),
    "line": (60, 72, 86),
}

PASTELS = {
    "blue": (226, 241, 255),
    "green": (226, 244, 232),
    "orange": (255, 235, 218),
    "yellow": (255, 247, 214),
    "red": (255, 229, 233),
    "purple": (238, 233, 250),
    "gray": (235, 240, 246),
}

REPORT_ROWS: list[dict[str, str | int]] = []


def font(size: int, bold: bool = False):
    paths = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


F_TITLE = font(34, True)
F_H2 = font(22, True)
F_BODY = font(17)
F_SMALL = font(14)
F_TINY = font(12)
F_BOLD = font(16, True)


def snapped(*values: float, step: int = 10) -> bool:
    return all(round(v) % step == 0 for v in values)


class Canvas:
    def __init__(self, name: str, title: str, slug: str):
        self.name = name
        self.title = title
        self.slug = slug
        self.img = Image.new("RGB", (W, H), "white")
        self.d = ImageDraw.Draw(self.img)
        self.checked = 0
        self.violations = 0
        self.header()

    def check(self, *values: float, step: int = 10):
        self.checked += 1
        if not snapped(*values, step=step):
            self.violations += 1

    def header(self):
        d = self.d
        d.rectangle([0, 0, W, H], fill=(255, 255, 255))
        d.text((64, 34), self.title, fill=COLORS["ink"], font=F_TITLE)
        d.line([64, 100, W - 64, 100], fill=(41, 132, 181), width=4)
        d.text((64, H - 34), f"image2://{self.slug} | precise PNG redraw | fixed half-grid instructional diagram", fill=(118, 130, 145), font=F_TINY)

    def grid(self, x=OX, y=OY, cols=36, rows=17, cell=GRID, alpha_bg=True):
        if alpha_bg:
            self.d.rectangle([x, y, x + cols * cell, y + rows * cell], fill=(252, 253, 255))
        for i in range(cols + 1):
            xx = x + i * cell
            color = COLORS["major"] if i % 4 == 0 else COLORS["grid"]
            self.d.line([xx, y, xx, y + rows * cell], fill=color, width=1)
        for j in range(rows + 1):
            yy = y + j * cell
            color = COLORS["major"] if j % 4 == 0 else COLORS["grid"]
            self.d.line([x, yy, x + cols * cell, yy], fill=color, width=1)
        self.check(x, y, cols * cell, rows * cell, step=10)

    def pos(self, gx, gy):
        return OX + gx * GRID, OY + gy * GRID

    def rect(self, gx, gy, gw, gh, fill, outline=COLORS["line"], width=2, radius=0):
        x, y = self.pos(gx, gy)
        w, h = gw * GRID, gh * GRID
        self.check(x, y, w, h, step=10)
        if radius:
            self.d.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill, outline=outline, width=width)
        else:
            self.d.rectangle([x, y, x + w, y + h], fill=fill, outline=outline, width=width)
        return x, y, w, h

    def label(self, text, x, y, w, h, fill=COLORS["ink"], fnt=F_SMALL, align="center"):
        lines = wrap_text(self.d, text, fnt, max(1, w - 16))
        line_h = fnt.size + 4 if hasattr(fnt, "size") else 16
        total_h = len(lines) * line_h
        yy = y + max(4, (h - total_h) / 2)
        for line in lines:
            tw = self.d.textlength(line, font=fnt)
            xx = x + 8 if align == "left" else x + (w - tw) / 2
            self.d.text((xx, yy), line, fill=fill, font=fnt)
            yy += line_h

    def card(self, gx, gy, gw, gh, title, body="", fill=PASTELS["blue"], accent=COLORS["blue"]):
        x, y, w, h = self.rect(gx, gy, gw, gh, fill, outline=(163, 178, 196), width=2, radius=8)
        self.d.rectangle([x, y, x + 8, y + h], fill=accent)
        self.label(title, x + 14, y + 10, w - 22, 30, fnt=F_BOLD, align="left")
        if body:
            self.label(body, x + 14, y + 42, w - 22, h - 48, fill=COLORS["muted"], fnt=F_TINY, align="left")
        return x, y, w, h

    def arrow(self, p1, p2, color=COLORS["orange"], width=4, dash=False):
        x1, y1 = p1
        x2, y2 = p2
        self.check(x1, y1, x2, y2, step=10)
        if dash:
            draw_dashed_line(self.d, p1, p2, color, width)
        else:
            self.d.line([p1, p2], fill=color, width=width)
        draw_arrow_head(self.d, p1, p2, color, size=15)

    def g_arrow(self, x1, y1, x2, y2, color=COLORS["orange"], width=4, dash=False):
        self.arrow(self.pos(x1, y1), self.pos(x2, y2), color, width, dash)

    def dot(self, gx, gy, label="", color=COLORS["blue"], r=14):
        x, y = self.pos(gx, gy)
        self.check(x, y, step=10)
        self.d.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=COLORS["ink"], width=2)
        if label:
            tw = self.d.textlength(label, font=F_TINY)
            self.d.text((x - tw / 2, y - 7), label, fill="white", font=F_TINY)

    def finish(self):
        path = ASSET_DIR / self.name
        self.img.save(path, quality=95)
        status = "PASS" if self.violations == 0 else "RECHECK"
        REPORT_ROWS.append(
            {
                "Diagram": self.name.replace(".png", ""),
                "CheckedPrimitives": self.checked,
                "MisalignedPrimitives": self.violations,
                "Status": status,
            }
        )


def wrap_text(draw, text, fnt, width):
    chunks = []
    for para in str(text).split("\n"):
        if not para:
            chunks.append("")
            continue
        current = ""
        for char in para:
            test = current + char
            if draw.textlength(test, font=fnt) <= width or not current:
                current = test
            else:
                chunks.append(current)
                current = char
        if current:
            chunks.append(current)
    return chunks


def draw_arrow_head(draw, p1, p2, color, size=14):
    x1, y1 = p1
    x2, y2 = p2
    angle = math.atan2(y2 - y1, x2 - x1)
    spread = 0.55
    left = (x2 - math.cos(angle - spread) * size, y2 - math.sin(angle - spread) * size)
    right = (x2 - math.cos(angle + spread) * size, y2 - math.sin(angle + spread) * size)
    draw.polygon([(x2, y2), left, right], fill=color)


def draw_dashed_line(draw, p1, p2, color, width=3, dash=14, gap=10):
    x1, y1 = p1
    x2, y2 = p2
    dist = math.hypot(x2 - x1, y2 - y1)
    if dist == 0:
        return
    dx, dy = (x2 - x1) / dist, (y2 - y1) / dist
    t = 0
    while t < dist:
        a = t
        b = min(t + dash, dist)
        draw.line([(x1 + dx * a, y1 + dy * a), (x1 + dx * b, y1 + dy * b)], fill=color, width=width)
        t += dash + gap


def save(c: Canvas):
    c.finish()


def diagram_curriculum():
    c = Canvas("level-design-curriculum-overview.png", "教材整体结构：从玩法问题到迭代回写", "level_design_curriculum_overview")
    c.grid()
    steps = [
        ("玩法目标", "玩家要做什么\n胜利/失败如何发生", PASTELS["blue"], COLORS["blue"]),
        ("Gameplay Matrix", "动作 × 障碍 × 资源\n把体验拆成格子", PASTELS["yellow"], COLORS["yellow"]),
        ("Metrics", "距离、时间、半径\n让判断可测量", PASTELS["green"], COLORS["green"]),
        ("Blockout", "用白盒空间验证\n入口、节奏和风险", PASTELS["orange"], COLORS["orange"]),
        ("Playtest", "观察死亡、停留\n迷路与重复失败", PASTELS["purple"], COLORS["purple"]),
        ("Writeback", "把结果写回矩阵\n形成下一轮假设", PASTELS["red"], COLORS["red"]),
    ]
    for i, (t, b, f, a) in enumerate(steps):
        c.card(1 + i * 5.5, 4, 4.5, 2.5, t, b, f, a)
        if i < len(steps) - 1:
            c.g_arrow(5.5 + i * 5.5, 5, 6.5 + i * 5.5, 5)
    c.g_arrow(31, 7.5, 4, 12.5, COLORS["orange"], width=5, dash=True)
    c.card(8, 12, 20, 2.5, "核心教学观念", "好的关卡不是先摆漂亮场景，而是先让玩法问题、空间结构和验证指标互相咬合。", PASTELS["gray"], COLORS["line"])
    save(c)


def diagram_core_loop():
    c = Canvas("core-gameplay-loop-diagram.png", "玩法核心循环：行动、反馈、奖励与再行动", "core_gameplay_loop_diagram")
    c.grid()
    nodes = [
        (9, 4, "读目标", "看到出口、敌人、奖励或风险", PASTELS["blue"], COLORS["blue"]),
        (22, 4, "执行动作", "移动、跳跃、射击、交互", PASTELS["green"], COLORS["green"]),
        (22, 11, "获得反馈", "命中、失败、开门、掉血", PASTELS["orange"], COLORS["orange"]),
        (9, 11, "调整策略", "换路线、重试、升级理解", PASTELS["purple"], COLORS["purple"]),
    ]
    centers = []
    for gx, gy, t, b, f, a in nodes:
        x, y, w, h = c.card(gx, gy, 6, 2.5, t, b, f, a)
        centers.append((x + w / 2, y + h / 2))
    for a, b in zip(centers, centers[1:] + centers[:1]):
        c.arrow(a, b, COLORS["orange"], 5)
    c.card(13, 7.5, 10, 2.5, "循环质量检查", "每一次失败都应让玩家更懂下一步，而不是只感到随机或冤枉。", PASTELS["yellow"], COLORS["yellow"])
    save(c)


def diagram_obstacle_action():
    c = Canvas("obstacle-action-relation.png", "障碍如何改变玩家动作：六种阻力样本", "obstacle_action_relation")
    c.grid()
    items = [
        ("低墙", "迫使跳跃\n暴露动作节奏", "jump", COLORS["blue"]),
        ("移动平台", "要求等待\n制造时间窗口", "wait", COLORS["green"]),
        ("窄门", "压缩走位\n放大遭遇风险", "door", COLORS["orange"]),
        ("敌人视线", "改变路线\n引入绕行判断", "vision", COLORS["red"]),
        ("锁与钥匙", "让目标分阶段\n先找资源再前进", "key", COLORS["purple"]),
        ("奖励岔路", "把安全路线\n改成风险选择", "reward", COLORS["yellow"]),
    ]
    for i, (t, b, icon, col) in enumerate(items):
        gx = 2 + (i % 3) * 11
        gy = 3 + (i // 3) * 6
        c.card(gx, gy, 8, 4, t, b, PASTELS[["blue", "green", "orange", "red", "purple", "yellow"][i]], col)
        x0, y0 = c.pos(gx + 1, gy + 2.5)
        x1, y1 = c.pos(gx + 7, gy + 2.5)
        c.arrow((x0, y0), (x1, y1), col, 4)
        c.dot(gx + 1, gy + 2.5, "P", COLORS["blue"])
        c.dot(gx + 7, gy + 2.5, "G", COLORS["green"])
        if icon in {"jump", "wait", "door", "vision", "key", "reward"}:
            c.rect(gx + 3, gy + 2, 1.5, 1, col, outline=COLORS["ink"])
    save(c)


def diagram_pacing():
    c = Canvas("pacing-emotion-curve.png", "节奏与情绪曲线：压力、缓冲、验证", "pacing_emotion_curve")
    c.grid()
    points = [(2, 13), (6, 10), (10, 11), (14, 7), (18, 12), (23, 5), (28, 10), (34, 8)]
    px = [c.pos(x, y) for x, y in points]
    c.d.line(px, fill=COLORS["orange"], width=6, joint="curve")
    for i, p in enumerate(px, 1):
        c.d.ellipse([p[0] - 8, p[1] - 8, p[0] + 8, p[1] + 8], fill=COLORS["orange"], outline=COLORS["ink"], width=2)
        c.d.text((p[0] - 7, p[1] - 28), str(i), fill=COLORS["ink"], font=F_TINY)
    c.d.text(c.pos(1, 2), "高压", fill=COLORS["red"], font=F_BOLD)
    c.d.text(c.pos(1, 15), "缓冲", fill=COLORS["green"], font=F_BOLD)
    labels = ["教学", "练习", "小考", "升级", "放松", "Boss", "回收", "新钩子"]
    for i, label in enumerate(labels):
        x, y = c.pos(2 + i * 4, 15)
        c.label(label, x - 50, y, 100, 24, fnt=F_TINY)
    save(c)


def diagram_metrics_overview():
    c = Canvas("precise-metrics-dual-scale-overview.png", "米制标尺总览：角色能力与空间元素", "metrics_dual_scale_overview")
    c.grid()
    c.card(1, 3, 15, 3, "角色能力尺标", "身体盒、速度、跳距、交互半径、受击半径。先测角色，再决定空间。", PASTELS["blue"], COLORS["blue"])
    c.card(20, 3, 15, 3, "关卡元素尺标", "坑宽、墙高、平台间距、房间体量、敌人警戒半径。空间必须能被角色读懂。", PASTELS["green"], COLORS["green"])
    c.rect(4, 8, 1, 3, COLORS["blue"])
    c.rect(6, 10, 5, 1, (250, 206, 168), outline=COLORS["orange"])
    c.dot(4.5, 8, "P", COLORS["blue"], r=12)
    c.d.ellipse([c.pos(10, 7)[0] - 90, c.pos(10, 7)[1] - 90, c.pos(10, 7)[0] + 90, c.pos(10, 7)[1] + 90], outline=COLORS["red"], width=4)
    c.label("角色：1格宽，3格高，4格稳定跳距", *c.pos(2, 13), 520, 40, fnt=F_SMALL, align="left")
    c.rect(23, 8, 8, 5, (255, 248, 230), outline=COLORS["line"])
    c.rect(29, 8, 1, 5, COLORS["wall"], outline=COLORS["wall"])
    c.rect(22, 10, 1, 1, COLORS["green"], outline=COLORS["green"])
    c.dot(26, 10.5, "E", COLORS["red"], r=14)
    c.label("空间：入口、墙体、敌人半径、回撤线", *c.pos(21, 13), 520, 40, fnt=F_SMALL, align="left")
    save(c)


def diagram_character_grid():
    c = Canvas("precise-character-ability-metrics-grid.png", "角色能力标尺网格：身体、跳跃、速度、技能半径", "character_ability_metrics_grid")
    c.grid()
    gx, gy, cell = 9, 3, GRID
    c.rect(gx, gy, 19, 12, (252, 253, 255), outline=COLORS["line"])
    for i in range(20):
        x = OX + (gx + i) * GRID
        c.d.line([x, OY + gy * GRID, x, OY + (gy + 12) * GRID], fill=COLORS["grid"])
    for j in range(13):
        y = OY + (gy + j) * GRID
        c.d.line([OX + gx * GRID, y, OX + (gx + 19) * GRID, y], fill=COLORS["grid"])
    c.rect(10, 12, 1, 1, COLORS["blue"])
    c.rect(10, 9, 1, 3, (174, 190, 204), outline=(174, 190, 204))
    c.rect(11, 12, 4, 1, (250, 206, 168), outline=COLORS["orange"])
    c.g_arrow(10.5, 12.5, 15.5, 12.5, COLORS["orange"], 4)
    c.d.ellipse([*c.pos(20, 6), *c.pos(27, 13)], outline=COLORS["red"], width=4)
    c.d.ellipse([*c.pos(23, 4), *c.pos(29, 10)], outline=COLORS["green"], width=4)
    c.card(1, 3, 6, 2, "身体盒", "1格宽 / 3格高", PASTELS["blue"], COLORS["blue"])
    c.card(1, 6, 6, 2, "稳定跳距", "4格内可教学\n5格以上要铺垫", PASTELS["orange"], COLORS["orange"])
    c.card(1, 9, 6, 2, "交互半径", "绿色圈：安全读到\n红圈：惩罚范围", PASTELS["green"], COLORS["green"])
    c.card(1, 12, 6, 2, "检查规则", "所有关键距离都要能在格子上复述", PASTELS["purple"], COLORS["purple"])
    save(c)


def diagram_element_matrix():
    c = Canvas("precise-level-element-difficulty-metrics-matrix.png", "关卡元素体量与难度标尺：不要只凭感觉调难度", "level_element_difficulty_metrics_matrix")
    c.grid()
    headers = ["元素", "简单", "中等", "困难"]
    rows = ["坑宽", "墙高", "敌人半径", "资源停留"]
    for col, h in enumerate(headers):
        c.card(1 + col * 8, 3, 7, 1.5, h, "", PASTELS["gray"] if col == 0 else [PASTELS["green"], PASTELS["yellow"], PASTELS["red"]][col - 1], [COLORS["line"], COLORS["green"], COLORS["yellow"], COLORS["red"]][col])
    for r, name in enumerate(rows):
        y = 5 + r * 2.5
        c.card(1, y, 7, 1.5, name, "", PASTELS["gray"], COLORS["line"])
        vals = [["2格", "3-4格", "5格+"], ["1格", "2-3格", "4格+"], ["短视野", "半屏", "封入口"], ["可路过", "需停顿", "会被读"]][r]
        for col, val in enumerate(vals):
            c.card(9 + col * 8, y, 7, 1.5, val, "", [PASTELS["green"], PASTELS["yellow"], PASTELS["red"]][col], [COLORS["green"], COLORS["yellow"], COLORS["red"]][col])
    c.card(7, 15, 22, 1.5, "使用方式", "先写元素职责，再写体量阈值；没有数据时只写证据边界，不画成精确热力或密度。", PASTELS["purple"], COLORS["purple"])
    save(c)


def mini_platform(c, gx, gy, title, pit=2, enemy=False, reward=False):
    c.card(gx, gy, 8, 4.5, title, "", PASTELS["gray"], COLORS["line"])
    x0, y0 = c.pos(gx + 1, gy + 3)
    for i in range(7):
        if 2 <= i < 2 + pit:
            continue
        c.d.rectangle([x0 + i * 34, y0, x0 + i * 34 + 32, y0 + 24], fill=COLORS["wall"])
    c.dot(gx + 1, gy + 2.5, "P", COLORS["blue"], 10)
    c.g_arrow(gx + 1.5, gy + 2.5, gx + 4.5, gy + 2.5, COLORS["orange"], 3)
    if enemy:
        c.dot(gx + 5.5, gy + 2.5, "E", COLORS["red"], 10)
    if reward:
        c.dot(gx + 6.5, gy + 1.5, "$", COLORS["yellow"], 10)


def diagram_challenge_variations():
    c = Canvas("precise-challenge-matrix-four-variations.png", "挑战矩阵四格变体：同一技能的四种难度写法", "challenge_matrix_four_variations")
    c.grid()
    mini_platform(c, 2, 3, "A 简单：短坑", pit=1)
    mini_platform(c, 14, 3, "B 中等：宽坑", pit=2)
    mini_platform(c, 2, 10, "C 压力：加敌人", pit=2, enemy=True)
    mini_platform(c, 14, 10, "D 选择：奖励岔路", pit=2, reward=True)
    c.card(27, 6, 7, 5, "设计判断", "难度不是只加数值。你可以改变宽度、时间压力、敌人职责或奖励诱惑。", PASTELS["purple"], COLORS["purple"])
    save(c)


def diagram_horizontal_jump():
    c = Canvas("precise-horizontal-jump-metrics-comparison.png", "横向跳跃尺标：同样是坑，宽度决定教学含义", "horizontal_jump_metrics_comparison")
    c.grid(rows=13)
    for gx, title, pit, col in [(3, "简单：2格坑", 2, COLORS["green"]), (21, "困难：5格坑", 5, COLORS["red"])]:
        c.card(gx, 3, 12, 7, title, "", PASTELS["green"] if pit == 2 else PASTELS["red"], col)
        x0, y0 = c.pos(gx + 1, 7)
        for i in range(10):
            if 3 <= i < 3 + pit:
                continue
            c.d.rectangle([x0 + i * 42, y0, x0 + i * 42 + 40, y0 + 28], fill=COLORS["wall"])
        c.dot(gx + 1.5, 6, "P", COLORS["blue"], 12)
        c.g_arrow(gx + 2, 6, gx + 4 + pit, 6, col, 4)
        c.label(f"坑宽 {pit} 格：{'用于教学' if pit == 2 else '需要助跑、预告或缓冲'}", *c.pos(gx + 1, 9), 390, 38, align="left")
    save(c)


def diagram_matrix_axes():
    c = Canvas("gameplay-matrix-axes.png", "Gameplay Matrix：动作、阻力、资源与反馈的交叉表", "gameplay_matrix_axes")
    c.grid()
    x, y = c.pos(4, 3)
    cw, rh = 160, 70
    cols = ["观察", "移动", "跳跃", "战斗", "交互", "回撤"]
    rows = ["目标", "障碍", "风险", "奖励", "验证"]
    c.d.rectangle([x, y, x + cw * (len(cols) + 1), y + rh * (len(rows) + 1)], fill="white", outline=COLORS["line"], width=3)
    for i, col in enumerate([""] + cols):
        c.d.rectangle([x + i * cw, y, x + (i + 1) * cw, y + rh], fill=PASTELS["blue"] if i else PASTELS["gray"], outline=COLORS["line"])
        c.label(col, x + i * cw, y, cw, rh, fnt=F_BOLD)
    for j, row in enumerate(rows, 1):
        c.d.rectangle([x, y + j * rh, x + cw, y + (j + 1) * rh], fill=PASTELS["gray"], outline=COLORS["line"])
        c.label(row, x, y + j * rh, cw, rh, fnt=F_BOLD)
        for i in range(1, len(cols) + 1):
            fill = (255, 255, 255) if (i + j) % 2 else (250, 252, 255)
            c.d.rectangle([x + i * cw, y + j * rh, x + (i + 1) * cw, y + (j + 1) * rh], fill=fill, outline=(218, 226, 236))
    samples = [(2, 2, "门线"), (3, 3, "坑宽"), (4, 4, "敌人"), (5, 5, "宝箱")]
    for i, j, label in samples:
        c.d.ellipse([x + i * cw + 55, y + j * rh + 20, x + i * cw + 85, y + j * rh + 50], fill=COLORS["orange"])
        c.label(label, x + i * cw + 88, y + j * rh + 14, 70, 42, fnt=F_TINY, align="left")
    save(c)


def platform_scene(c, gx, gy, gw=30, gh=6):
    base_y = gy + gh
    c.rect(gx, base_y, gw, 1, COLORS["wall"], outline=COLORS["wall"])
    blocks = [(4, base_y - 1, 3, 1), (10, base_y - 2, 2, 1), (15, base_y - 1, 4, 1), (23, base_y - 2, 3, 1)]
    for b in blocks:
        c.rect(gx + b[0], b[1], b[2], b[3], COLORS["wall"], outline=COLORS["wall"])
    c.dot(gx + 1, base_y - 0.5, "P", COLORS["blue"], 12)
    c.dot(gx + gw - 1, base_y - 0.5, "G", COLORS["green"], 12)


def diagram_platform_progression():
    c = Canvas("platform-world-1-2-progression.png", "平台动作关卡进程：五段式能力递进", "platform_world_1_2_progression")
    c.grid()
    platform_scene(c, 2, 6, 32, 5)
    labels = [("1 展示", 3), ("2 练习", 9), ("3 组合", 15), ("4 变化", 22), ("5 回收", 29)]
    for label, gx in labels:
        c.card(gx - 1, 3, 4.5, 1.5, label, "", PASTELS["yellow"], COLORS["yellow"])
        if gx < 29:
            c.g_arrow(gx + 2.5, 14.5, gx + 6.0, 14.5, COLORS["orange"], 3)
    save(c)


def diagram_platform_blockout():
    c = Canvas("platform-world-1-2-blockout.png", "平台动作 Blockout：把进程落成可走空间", "platform_world_1_2_blockout")
    c.grid()
    platform_scene(c, 2, 5, 32, 7)
    hazards = [(12, 12.5), (22, 10.5)]
    for gx, gy in hazards:
        c.dot(gx, gy, "E", COLORS["red"], 12)
    c.card(4, 3, 4, 1.5, "B01 起跳", "", PASTELS["blue"], COLORS["blue"])
    c.card(10, 3, 4, 1.5, "B02 宽坑", "", PASTELS["green"], COLORS["green"])
    c.card(16, 3, 4, 1.5, "B03 敌人", "", PASTELS["orange"], COLORS["orange"])
    c.card(22, 3, 4, 1.5, "B04 组合", "", PASTELS["red"], COLORS["red"])
    c.card(28, 3, 4, 1.5, "B05 目标", "", PASTELS["purple"], COLORS["purple"])
    save(c)


def diagram_portal_arc():
    c = Canvas("portal-fling-tutorial-arc.png", "解谜教学弧线：观察、操作、反馈、复用", "portal_fling_tutorial_arc")
    c.grid()
    items = [("观察", "看到入口/出口\n理解目标"), ("操作", "放置 Portal\n建立动线"), ("反馈", "被抛射到高台\n确认规则"), ("复用", "加入门、计时\n形成题目")]
    centers = []
    for i, (t, b) in enumerate(items):
        x, y, w, h = c.card(3 + i * 8, 5, 5.5, 3, t, b, [PASTELS["blue"], PASTELS["green"], PASTELS["yellow"], PASTELS["purple"]][i], [COLORS["blue"], COLORS["green"], COLORS["yellow"], COLORS["purple"]][i])
        centers.append((x + w / 2, y + h / 2))
    for a, b in zip(centers, centers[1:]):
        c.arrow(a, b, COLORS["orange"], 4)
    c.card(7, 12, 22, 2, "解谜图的重点", "不要把谜题画成谜语。图中必须说明玩家看到什么、做什么、怎么知道自己做对了。", PASTELS["gray"], COLORS["line"])
    save(c)


def diagram_portal_room():
    c = Canvas("portal-fling-room-blockout.png", "解谜房间 Blockout：入口、Portal、墙体与目标", "portal_fling_room_blockout")
    c.grid()
    c.rect(5, 3, 26, 12, (252, 253, 255), outline=COLORS["line"])
    c.rect(5, 14, 26, 1, COLORS["wall"], outline=COLORS["wall"])
    c.rect(15, 3, 1, 8, COLORS["wall"], outline=COLORS["wall"])
    c.rect(23, 8, 1, 6, COLORS["wall"], outline=COLORS["wall"])
    c.dot(7, 13, "P", COLORS["blue"], 12)
    c.dot(28, 13, "G", COLORS["green"], 12)
    c.d.ellipse([*c.pos(8, 12), *c.pos(10, 13)], outline=COLORS["blue"], width=4)
    c.d.ellipse([*c.pos(19, 6), *c.pos(21, 7)], outline=COLORS["orange"], width=4)
    c.g_arrow(9, 12, 20, 6, COLORS["orange"], 4, dash=True)
    c.g_arrow(20, 7, 28, 12, COLORS["green"], 4, dash=True)
    c.card(2, 3, 2.5, 3, "规则", "蓝入口\n橙出口", PASTELS["blue"], COLORS["blue"])
    save(c)


def diagram_doom_arena():
    c = Canvas("doom-arena-encounter-layout.png", "射击竞技场遭遇布局：环线、掩体、火力与奖励", "doom_arena_encounter_layout")
    c.grid()
    c.rect(6, 3, 24, 12, (255, 244, 232), outline=COLORS["line"])
    for gx, gy, gw, gh in [(9, 6, 4, 1), (20, 6, 5, 1), (15, 10, 2, 3), (24, 12, 3, 1)]:
        c.rect(gx, gy, gw, gh, COLORS["wall"], outline=COLORS["wall"])
    c.dot(10, 13, "P", COLORS["blue"], 12)
    for gx, gy in [(22, 5), (18, 12), (27, 10)]:
        c.dot(gx, gy, "E", COLORS["red"], 12)
    c.dot(27, 5, "$", COLORS["yellow"], 12)
    c.g_arrow(10, 13, 18, 12, COLORS["orange"], 4)
    c.g_arrow(18, 12, 27, 5, COLORS["orange"], 4)
    c.card(2, 5, 3.5, 5, "设计点", "让玩家不断换角度，而不是站在门口清完所有敌人。", PASTELS["purple"], COLORS["purple"])
    save(c)


def diagram_coop_matrix():
    c = Canvas("coop-role-responsibility-matrix.png", "合作关卡角色责任矩阵：谁看路、谁承压、谁兑现", "coop_role_responsibility_matrix")
    c.grid()
    headers = ["职责", "前排", "输出", "支援"]
    rows = ["进门", "遭遇", "回撤", "奖励"]
    x, y = c.pos(5, 3)
    cw, rh = 250, 90
    for i, h in enumerate(headers):
        c.d.rectangle([x + i * cw, y, x + (i + 1) * cw, y + rh], fill=PASTELS["gray"], outline=COLORS["line"])
        c.label(h, x + i * cw, y, cw, rh, fnt=F_BOLD)
    values = [
        ["先探入口", "架线压制", "保留治疗"],
        ["吃第一波", "打弱点", "救倒地"],
        ["断后", "补伤害", "带收益走"],
        ["开宝箱", "警戒", "分配资源"],
    ]
    for r, row in enumerate(rows):
        c.d.rectangle([x, y + (r + 1) * rh, x + cw, y + (r + 2) * rh], fill=PASTELS["blue"], outline=COLORS["line"])
        c.label(row, x, y + (r + 1) * rh, cw, rh, fnt=F_BOLD)
        for col in range(1, 4):
            c.d.rectangle([x + col * cw, y + (r + 1) * rh, x + (col + 1) * cw, y + (r + 2) * rh], fill="white", outline=COLORS["grid"])
            c.label(values[r][col - 1], x + col * cw, y + (r + 1) * rh, cw, rh, fnt=F_SMALL)
    save(c)


def diagram_iteration():
    c = Canvas("level-design-iteration-loop.png", "关卡设计迭代闭环：假设、空间、测试、回写", "level_design_iteration_loop")
    c.grid()
    nodes = [("概念假设", 5, 4), ("白盒布局", 17, 3), ("可玩测试", 28, 4), ("遥测观察", 28, 11), ("矩阵回写", 17, 12), ("下一轮", 5, 11)]
    centers = []
    for i, (label, gx, gy) in enumerate(nodes):
        x, y, w, h = c.card(gx, gy, 6, 2, label, "", [PASTELS["blue"], PASTELS["green"], PASTELS["yellow"], PASTELS["orange"], PASTELS["purple"], PASTELS["red"]][i], [COLORS["blue"], COLORS["green"], COLORS["yellow"], COLORS["orange"], COLORS["purple"], COLORS["red"]][i])
        centers.append((x + w / 2, y + h / 2))
    for a, b in zip(centers, centers[1:] + centers[:1]):
        c.arrow(a, b, COLORS["orange"], 4)
    save(c)


def diagram_blockout():
    c = Canvas("blockout-level-layout.png", "Blockout 关卡布局：五段 Beat 的空间拼接", "blockout_level_layout")
    c.grid()
    c.rect(2, 6, 32, 8, (252, 253, 255), outline=COLORS["line"])
    c.rect(2, 13, 32, 1, COLORS["wall"], outline=COLORS["wall"])
    for gx, gy, gw, gh in [(6, 11, 3, 2), (12, 10, 3, 3), (19, 9, 4, 4), (27, 11, 3, 2)]:
        c.rect(gx, gy, gw, gh, COLORS["wall"], outline=COLORS["wall"])
    c.dot(3, 12.5, "P", COLORS["blue"], 12)
    c.dot(33, 12.5, "G", COLORS["green"], 12)
    for gx, label in [(4, "B01"), (10, "B02"), (16, "B03"), (23, "B04"), (30, "B05")]:
        c.card(gx - 1, 4, 4, 1.5, label, "", PASTELS["yellow"], COLORS["yellow"])
    c.g_arrow(3, 12, 9, 11, COLORS["orange"], 4)
    c.g_arrow(10, 11, 16, 10, COLORS["orange"], 4)
    c.g_arrow(17, 10, 24, 9, COLORS["orange"], 4)
    c.g_arrow(25, 9, 33, 12, COLORS["orange"], 4)
    save(c)


def diagram_telemetry():
    c = Canvas("telemetry-heatmap-matrix-writeback.png", "遥测热图与矩阵回写：把失败变成修改项", "telemetry_heatmap_matrix_writeback")
    c.grid()
    c.rect(2, 4, 14, 10, (252, 253, 255), outline=COLORS["line"])
    c.d.ellipse([*c.pos(5, 6), *c.pos(10, 11)], fill=(255, 120, 120), outline=COLORS["red"], width=3)
    c.d.ellipse([*c.pos(8, 9), *c.pos(13, 14)], fill=(255, 215, 120), outline=COLORS["yellow"], width=3)
    c.dot(7.5, 8.5, "D", COLORS["red"], 12)
    c.dot(11, 11.5, "S", COLORS["yellow"], 12)
    c.g_arrow(17, 9, 21, 9, COLORS["orange"], 5)
    x, y = c.pos(21, 4)
    headers = ["Beat", "异常", "原因假设", "修改"]
    rows = [["B03", "死亡集中", "坑宽过大", "加缓冲台"], ["B04", "停留过久", "目标不清", "补视觉引导"], ["B05", "回撤失败", "出口太窄", "加侧路"]]
    cw, rh = 160, 70
    for i, h in enumerate(headers):
        c.d.rectangle([x + i * cw, y, x + (i + 1) * cw, y + rh], fill=PASTELS["gray"], outline=COLORS["line"])
        c.label(h, x + i * cw, y, cw, rh, fnt=F_BOLD)
    for r, row in enumerate(rows, 1):
        for i, val in enumerate(row):
            c.d.rectangle([x + i * cw, y + r * rh, x + (i + 1) * cw, y + (r + 1) * rh], fill="white", outline=COLORS["grid"])
            c.label(val, x + i * cw, y + r * rh, cw, rh, fnt=F_SMALL)
    save(c)


def diagram_genre():
    c = Canvas("genre-matrix-adaptation.png", "不同类型关卡的矩阵适配：同一框架，不同重心", "genre_matrix_adaptation")
    c.grid()
    items = [
        ("平台动作", "跳距 / 坑宽 / 节奏", COLORS["blue"]),
        ("解谜", "观察 / 操作 / 反馈", COLORS["green"]),
        ("射击", "视线 / 掩体 / 火力", COLORS["orange"]),
        ("合作", "职责 / 沟通 / 兑现", COLORS["purple"]),
        ("搜打撤", "收益 / 风险 / 撤退", COLORS["red"]),
        ("开放世界", "地标 / 路线 / 回报", COLORS["yellow"]),
    ]
    for i, (t, b, col) in enumerate(items):
        c.card(2 + (i % 3) * 11, 4 + (i // 3) * 6, 8, 3.5, t, b, PASTELS[["blue", "green", "orange", "purple", "red", "yellow"][i]], col)
    save(c)


def diagram_pitfalls():
    c = Canvas("level-design-pitfalls-correction-board.png", "常见陷阱与修正策略：从症状回到矩阵", "level_design_pitfalls_correction_board")
    c.grid()
    rows = [
        ("只加敌人", "玩家觉得乱", "先调入口和视线"),
        ("奖励太远", "玩家不愿冒险", "把奖励放到可读风险后"),
        ("谜题无反馈", "玩家乱试", "加入即时回应"),
        ("路线单一", "重玩无变化", "加二选一与回收"),
        ("难度跳变", "中途劝退", "用小考过渡"),
        ("数据不回写", "问题反复出现", "每轮只改一个变量"),
    ]
    for i, (a, b, fix) in enumerate(rows):
        gx = 2 + (i % 2) * 17
        gy = 3 + (i // 2) * 4.5
        c.card(gx, gy, 7, 2.5, a, b, PASTELS["red"], COLORS["red"])
        c.g_arrow(gx + 7.5, gy + 1.5, gx + 9, gy + 1.5, COLORS["orange"], 4)
        c.card(gx + 9.5, gy, 6, 2.5, "修正", fix, PASTELS["green"], COLORS["green"])
    save(c)


def diagram_five_beat():
    c = Canvas("five-beat-blockout-exercise.png", "练习用五段式 Blockout：把矩阵写成空间草稿", "five_beat_blockout_exercise")
    c.grid()
    beats = [
        ("B01 展示", "安全展示新动作"),
        ("B02 练习", "低惩罚重复一次"),
        ("B03 小考", "加入时间/敌人"),
        ("B04 变化", "换角度或加岔路"),
        ("B05 回收", "奖励或目标确认"),
    ]
    for i, (t, b) in enumerate(beats):
        c.card(2 + i * 6.5, 5, 5.5, 7, t, b, [PASTELS["blue"], PASTELS["green"], PASTELS["yellow"], PASTELS["orange"], PASTELS["purple"]][i], [COLORS["blue"], COLORS["green"], COLORS["yellow"], COLORS["orange"], COLORS["purple"]][i])
        c.dot(3 + i * 6.5, 10.5, "P" if i == 0 else "", COLORS["blue"], 10)
        c.dot(6 + i * 6.5, 10.5, "G" if i == 4 else "", COLORS["green"], 10)
        if i < 4:
            c.g_arrow(7.5 + i * 6.5, 8.5, 8.5 + i * 6.5, 8.5, COLORS["orange"], 3)
    c.card(4, 14, 28, 1.5, "练习要求", "每个 Beat 写清：动作、阻力、奖励、失败反馈。不能只画一个好看的房间。", PASTELS["gray"], COLORS["line"])
    save(c)


def render_all():
    for fn in [
        diagram_curriculum,
        diagram_core_loop,
        diagram_obstacle_action,
        diagram_pacing,
        diagram_metrics_overview,
        diagram_character_grid,
        diagram_element_matrix,
        diagram_challenge_variations,
        diagram_horizontal_jump,
        diagram_matrix_axes,
        diagram_platform_progression,
        diagram_platform_blockout,
        diagram_portal_arc,
        diagram_portal_room,
        diagram_doom_arena,
        diagram_coop_matrix,
        diagram_iteration,
        diagram_blockout,
        diagram_telemetry,
        diagram_genre,
        diagram_pitfalls,
        diagram_five_beat,
    ]:
        fn()

    with (ASSET_DIR / "grid-alignment-report.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Diagram", "CheckedPrimitives", "MisalignedPrimitives", "Status"])
        writer.writeheader()
        writer.writerows(REPORT_ROWS)


if __name__ == "__main__":
    render_all()

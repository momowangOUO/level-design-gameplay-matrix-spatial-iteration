import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const outDir = "assets/generated-level-design";
mkdirSync(outDir, { recursive: true });

const font = "Microsoft YaHei, Noto Sans CJK SC, Arial, sans-serif";
const magenta = "#b01b6a";
const blue = "#14aee8";
const orange = "#f4b183";
const green = "#92d050";
const yellow = "#ffd966";
const red = "#e33131";
const gray = "#d9d9d9";

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function svg(title, body, { w = 1600, h = 900 } = {}) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
<rect width="${w}" height="${h}" fill="#fff"/>
<text x="64" y="76" font-family="${font}" font-size="48" font-weight="700" fill="#111">${esc(title)}</text>
<line x1="64" y1="110" x2="${w - 64}" y2="110" stroke="${magenta}" stroke-width="4"/>
${body}
</svg>`;
}

function text(x, y, value, size = 28, extra = "") {
  return `<text x="${x}" y="${y}" font-family="${font}" font-size="${size}" fill="#111" ${extra}>${esc(value)}</text>`;
}

function box(x, y, w, h, label, fill = "#fff", stroke = "#111", size = 26) {
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="10" fill="${fill}" stroke="${stroke}" stroke-width="4"/>
${text(x + w / 2, y + h / 2 + size / 3, label, size, 'text-anchor="middle" font-weight="700"')}`;
}

function arrow(x1, y1, x2, y2, color = "#111") {
  const id = `arr-${Math.abs(Math.round(x1 * 13 + y1 * 17 + x2 * 19 + y2 * 23))}`;
  return `<defs><marker id="${id}" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="${color}"/></marker></defs>
<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="4" marker-end="url(#${id})"/>`;
}

function grid(x, y, cols, rows, cell, stroke = "#d7d7d7") {
  let s = `<rect x="${x}" y="${y}" width="${cols * cell}" height="${rows * cell}" fill="#fff" stroke="#111" stroke-width="4"/>`;
  for (let c = 1; c < cols; c++) s += `<line x1="${x + c * cell}" y1="${y}" x2="${x + c * cell}" y2="${y + rows * cell}" stroke="${stroke}" stroke-width="2"/>`;
  for (let r = 1; r < rows; r++) s += `<line x1="${x}" y1="${y + r * cell}" x2="${x + cols * cell}" y2="${y + r * cell}" stroke="${stroke}" stroke-width="2"/>`;
  return s;
}

function platformGrid(x, y, cols, rows, cell, blocks, player = [1, rows - 2]) {
  let s = grid(x, y, cols, rows, cell);
  for (const [cx, cy, cw = 1, ch = 1] of blocks) {
    s += `<rect x="${x + cx * cell}" y="${y + cy * cell}" width="${cw * cell}" height="${ch * cell}" fill="#000"/>`;
  }
  s += `<rect x="${x + player[0] * cell}" y="${y + player[1] * cell}" width="${cell}" height="${cell}" fill="${blue}" stroke="#111" stroke-width="2"/>`;
  return s;
}

function write(name, content) {
  writeFileSync(join(outDir, name), content, "utf8");
}

write("level-design-curriculum-overview.svg", svg("关卡设计教材结构", `
${box(92, 310, 180, 90, "基础概念", "#eaf4ff")}
${box(326, 310, 180, 90, "Matrix", "#fff2cc")}
${box(560, 310, 180, 90, "标尺", "#e2f0d9")}
${box(794, 310, 180, 90, "案例", "#fce4d6")}
${box(1028, 310, 180, 90, "迭代", "#e4dfec")}
${box(1262, 310, 180, 90, "回写", "#d9ead3")}
${arrow(272, 355, 326, 355)}${arrow(506, 355, 560, 355)}${arrow(740, 355, 794, 355)}
${arrow(974, 355, 1028, 355)}${arrow(1208, 355, 1262, 355)}
<path d="M1352 428 C1130 610, 580 610, 416 428" fill="none" stroke="#e87722" stroke-width="5" marker-end="url(#loopEnd)"/>
<defs><marker id="loopEnd" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#e87722"/></marker></defs>
${text(565, 650, "测试证据回写矩阵，矩阵再修正空间", 34, 'font-weight="700"')}
`));

write("core-gameplay-loop-diagram.svg", svg("玩法核心循环", `
${box(160, 300, 190, 90, "观察目标", "#eaf4ff")}
${box(510, 190, 190, 90, "执行动作", "#fff2cc")}
${box(860, 300, 190, 90, "系统反馈", "#e2f0d9")}
${box(510, 520, 190, 90, "修正策略", "#fce4d6")}
${arrow(350, 330, 510, 250)}${arrow(700, 250, 860, 330)}${arrow(955, 390, 650, 520)}${arrow(510, 560, 255, 390)}
${text(1120, 240, "玩家动作", 34, 'font-weight="700"')}<circle cx="1180" cy="340" r="54" fill="${blue}" stroke="#111" stroke-width="4"/>
${text(1120, 470, "障碍/资源/情绪都围绕循环服务", 30)}
`));

write("obstacle-action-relation.svg", svg("障碍如何改变玩家动作", `
${box(120, 330, 190, 90, "玩家动作", "#eaf4ff")}
${box(430, 250, 190, 90, "障碍/敌人", "#f4cccc")}
${box(740, 330, 190, 90, "策略变化", "#fff2cc")}
${box(1050, 250, 190, 90, "奖励/资源", "#d9ead3")}
${box(1050, 460, 190, 90, "情绪结果", "#e4dfec")}
${arrow(310, 375, 430, 300)}${arrow(620, 300, 740, 375)}${arrow(930, 360, 1050, 300)}${arrow(930, 405, 1050, 505)}
${text(170, 610, "例：坑洞不是空白，它让跳跃有意义。", 34, 'font-weight="700"')}
`));

write("pacing-emotion-curve.svg", svg("节奏与情绪曲线", `
<polyline points="150,640 330,540 510,470 690,350 870,560 1050,270 1230,520 1410,610" fill="none" stroke="#e87722" stroke-width="7"/>
<g stroke="#bbb" stroke-width="2"><line x1="140" y1="650" x2="1460" y2="650"/><line x1="140" y1="180" x2="140" y2="650"/></g>
${text(100, 170, "强度", 28)}${text(1390, 700, "Beat", 28)}
${box(220, 675, 160, 58, "引介", "#eaf4ff", "#999", 24)}
${box(430, 675, 160, 58, "练习", "#fff2cc", "#999", 24)}
${box(640, 675, 160, 58, "变奏", "#fce4d6", "#999", 24)}
${box(850, 675, 160, 58, "释放", "#d9ead3", "#999", 24)}
${box(1060, 675, 160, 58, "峰值", "#f4cccc", "#999", 24)}
${box(1270, 675, 160, 58, "收束", "#e4dfec", "#999", 24)}
`));

write("gameplay-matrix-axes.svg", svg("Gameplay Matrix 轴线结构", `
<g transform="translate(170 180)">
<rect width="1080" height="520" fill="#fff" stroke="#111" stroke-width="4"/>
<rect x="0" y="0" width="220" height="80" fill="#eeeeee"/><rect x="220" y="0" width="215" height="80" fill="#eaf4ff"/><rect x="435" y="0" width="215" height="80" fill="#fff2cc"/><rect x="650" y="0" width="215" height="80" fill="#fce4d6"/><rect x="865" y="0" width="215" height="80" fill="#d9ead3"/>
<g stroke="#777" stroke-width="3"><path d="M220 0V520 M435 0V520 M650 0V520 M865 0V520 M0 80H1080 M0 190H1080 M0 300H1080 M0 410H1080"/></g>
${text(250, 52, "引介", 26, 'font-weight="700"')} ${text(465, 52, "练习", 26, 'font-weight="700"')} ${text(680, 52, "验证", 26, 'font-weight="700"')} ${text(895, 52, "变奏", 26, 'font-weight="700"')}
${text(34, 150, "动作", 26, 'font-weight="700"')} ${text(34, 260, "障碍", 26, 'font-weight="700"')} ${text(34, 370, "资源", 26, 'font-weight="700"')} ${text(34, 480, "情绪", 26, 'font-weight="700"')}
<circle cx="328" cy="135" r="16" fill="${blue}"/><circle cx="546" cy="245" r="16" fill="${red}"/><circle cx="760" cy="355" r="16" fill="${yellow}"/><circle cx="978" cy="465" r="16" fill="${green}"/>
</g>
`));

write("platform-world-1-2-progression.svg", svg("平台动作关卡进程", `
${platformGrid(110, 260, 24, 7, 48, [[0,6,24,1],[5,5,2,1],[10,4,3,1],[15,5,2,1],[19,4,3,1]], [1,5])}
${text(120, 230, "坡道/滑行", 26, 'font-weight="700"')}${text(355, 230, "P-Switch", 26, 'font-weight="700"')}${text(590, 230, "Jump Block", 26, 'font-weight="700"')}${text(840, 230, "坑洞验证", 26, 'font-weight="700"')}${text(1085, 230, "收束", 26, 'font-weight="700"')}
${arrow(180, 650, 420, 650, "#e87722")}${arrow(455, 650, 700, 650, "#e87722")}${arrow(735, 650, 980, 650, "#e87722")}${arrow(1015, 650, 1210, 650, "#e87722")}
`));

write("platform-world-1-2-blockout.svg", svg("平台动作 Blockout 草图", `
${platformGrid(120, 190, 26, 8, 46, [[0,7,26,1],[4,6,3,1],[8,5,2,1],[12,6,2,1],[16,5,3,1],[21,6,2,1]], [1,6])}
<rect x="418" y="466" width="46" height="46" fill="${yellow}" stroke="#111" stroke-width="3"/><text x="441" y="495" font-family="${font}" font-size="18" text-anchor="middle" font-weight="700">P</text>
<circle cx="700" cy="535" r="22" fill="${red}"/><circle cx="980" cy="489" r="22" fill="${red}"/>
${text(135, 600, "B01 引介", 24)}${text(410, 600, "B02 变奏", 24)}${text(640, 600, "B03 练习", 24)}${text(870, 600, "B04 验证", 24)}${text(1110, 600, "B05 释放", 24)}
`));

write("portal-fling-tutorial-arc.svg", svg("Portal 式 Fling 教学弧线", `
${box(160, 330, 260, 100, "C10\nFling 引介", "#eaf4ff")}
${box(650, 330, 260, 100, "C11\n先看再跳", "#fff2cc")}
${box(1140, 330, 260, 100, "C12\n重新验证", "#d9ead3")}
${arrow(420, 380, 650, 380)}${arrow(910, 380, 1140, 380)}
${text(220, 530, "一次只教一个新概念", 32, 'font-weight="700"')}
${text(730, 530, "限制错误路径", 32, 'font-weight="700"')}
${text(1170, 530, "工具更新后回收旧技能", 32, 'font-weight="700"')}
`));

write("portal-fling-room-blockout.svg", svg("Fling 房间 Blockout", `
${grid(210, 180, 18, 10, 56)}
<rect x="210" y="684" width="1008" height="56" fill="#000"/>
<rect x="210" y="180" width="168" height="56" fill="#000"/>
<rect x="882" y="348" width="336" height="56" fill="#000"/>
<rect x="294" y="124" width="56" height="56" fill="${blue}" stroke="#111" stroke-width="3"/>
<ellipse cx="322" cy="684" rx="46" ry="14" fill="#6fa8dc" stroke="#111" stroke-width="3"/><text x="250" y="790" font-family="${font}" font-size="28">入口 portal</text>
<ellipse cx="966" cy="348" rx="46" ry="14" fill="#f6b26b" stroke="#111" stroke-width="3"/><text x="900" y="328" font-family="${font}" font-size="28">出口 portal</text>
<path d="M322 180 C260 360, 260 560, 322 676" fill="none" stroke="#e87722" stroke-width="5" stroke-dasharray="12 8"/>
<path d="M966 348 C1030 260, 1120 260, 1180 348" fill="none" stroke="#e87722" stroke-width="5" stroke-dasharray="12 8"/>
`));

write("doom-arena-encounter-layout.svg", svg("射击竞技场遭遇布局", `
<rect x="290" y="180" width="900" height="560" rx="26" fill="#f8dfc8" stroke="#111" stroke-width="5"/>
<rect x="360" y="260" width="150" height="80" fill="#111"/><rect x="960" y="580" width="150" height="80" fill="#111"/><rect x="690" y="410" width="120" height="90" fill="#111"/>
<circle cx="740" cy="460" r="34" fill="${blue}" stroke="#111" stroke-width="3"/><text x="710" y="522" font-family="${font}" font-size="24">玩家</text>
<circle cx="475" cy="520" r="26" fill="${red}"/><circle cx="1010" cy="310" r="26" fill="${red}"/><circle cx="900" cy="460" r="30" fill="#8e44ad"/>
<path d="M740 460 C600 330, 450 420, 475 520 C610 655, 910 635, 1010 310 C900 260, 790 350, 740 460" fill="none" stroke="#e87722" stroke-width="6" stroke-dasharray="14 10"/>
${text(310, 790, "设计重点：敌人组合 + 掩体 + 补给点共同迫使玩家移动", 34, 'font-weight="700"')}
`));

write("extraction-risk-reward-heatmap.svg", svg("搜打撤风险收益热区", `
<rect x="250" y="170" width="900" height="600" fill="#e2f0d9" stroke="#111" stroke-width="5"/>
<circle cx="700" cy="470" r="175" fill="#ff0000" opacity="0.28"/><circle cx="700" cy="470" r="95" fill="#ff0000" opacity="0.42"/>
<circle cx="455" cy="355" r="120" fill="#ffd966" opacity="0.65"/><circle cx="945" cy="590" r="120" fill="#ffd966" opacity="0.65"/>
<rect x="320" y="650" width="170" height="70" fill="#92d050" stroke="#111" stroke-width="3"/><text x="405" y="696" font-family="${font}" font-size="26" text-anchor="middle" font-weight="700">低风险补给</text>
<rect x="618" y="425" width="165" height="90" fill="#111" opacity="0.75"/><text x="700" y="480" font-family="${font}" font-size="28" text-anchor="middle" fill="#fff" font-weight="700">高价值热区</text>
${text(1190, 260, "绿色：启动", 30)}${text(1190, 330, "黄色：稳定收益", 30)}${text(1190, 400, "红色：高压高收益", 30)}
`));

write("spawn-extract-route-matrix.svg", svg("出生点到撤离点矩阵", `
<rect x="180" y="160" width="980" height="620" fill="#f3f6f8" stroke="#111" stroke-width="5"/>
<circle cx="280" cy="255" r="30" fill="${blue}"/><circle cx="1030" cy="255" r="30" fill="${blue}"/><circle cx="280" cy="685" r="30" fill="${blue}"/><circle cx="1030" cy="685" r="30" fill="${blue}"/>
<rect x="590" y="380" width="180" height="130" fill="#111" opacity="0.8"/><text x="680" y="455" font-family="${font}" font-size="28" fill="#fff" text-anchor="middle">核心热区</text>
<rect x="480" y="190" width="140" height="70" fill="#ffd966" stroke="#111" stroke-width="3"/><rect x="800" y="645" width="140" height="70" fill="#ffd966" stroke="#111" stroke-width="3"/>
<rect x="150" y="435" width="90" height="60" fill="${green}" stroke="#111" stroke-width="3"/><text x="195" y="475" font-family="${font}" font-size="22" text-anchor="middle">撤离</text>
<rect x="1120" y="435" width="90" height="60" fill="${green}" stroke="#111" stroke-width="3"/><text x="1165" y="475" font-family="${font}" font-size="22" text-anchor="middle">撤离</text>
<path d="M280 255 C420 290, 500 345, 590 405" fill="none" stroke="#e87722" stroke-width="6"/>
<path d="M1030 685 C900 650, 820 560, 770 500" fill="none" stroke="#e87722" stroke-width="6"/>
<path d="M280 685 C360 595, 360 510, 240 465" fill="none" stroke="#4a86e8" stroke-width="6" stroke-dasharray="12 10"/>
<path d="M1030 255 C1000 350, 1080 420, 1120 465" fill="none" stroke="#4a86e8" stroke-width="6" stroke-dasharray="12 10"/>
${text(1230, 250, "检查：近/高收益/低暴露/稳定可用", 28)}
${text(1230, 310, "若同时成立，需要限制或补偿", 28)}
`));

write("coop-role-responsibility-matrix.svg", svg("合作关卡角色责任矩阵", `
<g transform="translate(170 170)">
<rect width="1080" height="520" fill="#fff" stroke="#111" stroke-width="4"/>
<rect x="0" y="0" width="220" height="80" fill="#eeeeee"/><rect x="220" y="0" width="280" height="80" fill="#eaf4ff"/><rect x="500" y="0" width="280" height="80" fill="#fff2cc"/><rect x="780" y="0" width="300" height="80" fill="#d9ead3"/>
<g stroke="#777" stroke-width="3"><path d="M220 0V520 M500 0V520 M780 0V520 M0 80H1080 M0 190H1080 M0 300H1080 M0 410H1080"/></g>
${text(300, 52, "玩家 A", 28, 'font-weight="700"')} ${text(590, 52, "玩家 B", 28, 'font-weight="700"')} ${text(850, 52, "同步/反馈", 28, 'font-weight="700"')}
${text(34, 150, "分工", 26, 'font-weight="700"')} ${text(34, 260, "沟通", 26, 'font-weight="700"')} ${text(34, 370, "同步", 26, 'font-weight="700"')} ${text(34, 480, "轮替", 26, 'font-weight="700"')}
${text(270, 150, "开门", 24)}${text(560, 150, "观察", 24)}${text(845, 150, "路径开启", 24)}
${text(270, 260, "标记", 24)}${text(560, 260, "确认", 24)}${text(845, 260, "共同目标", 24)}
${text(270, 370, "站位", 24)}${text(560, 370, "倒计时", 24)}${text(845, 370, "机关成功", 24)}
${text(270, 480, "战斗", 24)}${text(560, 480, "解谜", 24)}${text(845, 480, "交换责任", 24)}
</g>
`));

write("level-design-iteration-loop.svg", svg("关卡设计迭代闭环", `
${box(190, 190, 210, 86, "概念", "#eaf4ff")}
${box(535, 190, 210, 86, "进程", "#fff2cc")}
${box(880, 190, 210, 86, "空间", "#fce4d6")}
${box(880, 520, 210, 86, "测试", "#e2f0d9")}
${box(535, 520, 210, 86, "分析", "#d9ead3")}
${box(190, 520, 210, 86, "迭代", "#e4dfec")}
${arrow(400, 233, 535, 233)}${arrow(745, 233, 880, 233)}${arrow(985, 276, 985, 520)}${arrow(880, 563, 745, 563)}${arrow(535, 563, 400, 563)}${arrow(295, 520, 295, 276)}
${text(1160, 350, "证据回写：", 32, 'font-weight="700"')}${text(1160, 410, "改矩阵", 30)}${text(1160, 465, "改空间", 30)}${text(1160, 520, "改资源/敌人", 30)}
`));

write("blockout-level-layout.svg", svg("Blockout 关卡布局", `
${platformGrid(145, 180, 26, 9, 46, [[0,8,26,1],[0,7,4,1],[6,6,4,2],[12,7,3,1],[17,5,4,3],[23,7,3,1]], [1,6])}
<rect x="145" y="456" width="70" height="46" fill="${green}" stroke="#111" stroke-width="3"/><text x="180" y="486" font-family="${font}" font-size="18" text-anchor="middle" font-weight="700">ENTER</text>
<rect x="1247" y="502" width="72" height="46" fill="${yellow}" stroke="#111" stroke-width="3"/><text x="1283" y="532" font-family="${font}" font-size="18" text-anchor="middle" font-weight="700">GOAL</text>
<circle cx="690" cy="456" r="22" fill="${red}"/><circle cx="975" cy="364" r="22" fill="${red}"/>
${text(160, 650, "B01 引介", 24)}${text(390, 650, "B02 练习", 24)}${text(620, 650, "B03 验证", 24)}${text(850, 650, "B04 峰值", 24)}${text(1110, 650, "B05 释放", 24)}
`));

write("telemetry-heatmap-matrix-writeback.svg", svg("遥测热图与矩阵回写", `
<rect x="130" y="180" width="560" height="470" fill="#f3f6f8" stroke="#111" stroke-width="4"/>
<circle cx="310" cy="360" r="95" fill="#ff0000" opacity="0.24"/><circle cx="310" cy="360" r="45" fill="#ff0000" opacity="0.45"/>
<circle cx="510" cy="500" r="80" fill="#ffd966" opacity="0.65"/><circle cx="575" cy="285" r="55" fill="#92d050" opacity="0.75"/>
${text(210, 700, "死亡/停留/路线热图", 30, 'font-weight="700"')}
${arrow(720, 410, 840, 410, "#e87722")}
<g transform="translate(840 210)">
<rect width="600" height="380" fill="#fff" stroke="#111" stroke-width="4"/>
<rect width="600" height="70" fill="#eeeeee"/>
<g stroke="#777" stroke-width="3"><path d="M150 0V380 M300 0V380 M450 0V380 M0 70H600 M0 160H600 M0 250H600"/></g>
${text(30, 46, "Beat", 22, 'font-weight="700"')}${text(180, 46, "假设", 22, 'font-weight="700"')}${text(330, 46, "观测", 22, 'font-weight="700"')}${text(480, 46, "修正", 22, 'font-weight="700"')}
${text(36, 125, "B03", 22)}${text(180, 125, "学会跳跃", 22)}${text(330, 125, "死亡高", 22)}${text(480, 125, "加练习", 22)}
${text(36, 215, "B04", 22)}${text(180, 215, "风险可读", 22)}${text(330, 215, "回头多", 22)}${text(480, 215, "改视线", 22)}
${text(36, 305, "B05", 22)}${text(180, 305, "释放", 22)}${text(330, 305, "耗时长", 22)}${text(480, 305, "缩短", 22)}
</g>
`));

write("genre-matrix-adaptation.svg", svg("不同类型关卡的矩阵适配", `
${box(630, 330, 260, 110, "Gameplay\nMatrix", "#fff2cc")}
${box(160, 180, 200, 76, "平台", "#eaf4ff")}${box(620, 160, 200, 76, "解谜", "#e2f0d9")}${box(1080, 180, 200, 76, "射击", "#fce4d6")}
${box(160, 590, 200, 76, "搜打撤", "#d9ead3")}${box(620, 620, 200, 76, "合作", "#e4dfec")}${box(1080, 590, 200, 76, "多角色", "#f4cccc")}
${arrow(360, 218, 630, 350)}${arrow(720, 236, 720, 330)}${arrow(1080, 218, 890, 350)}
${arrow(360, 628, 630, 410)}${arrow(720, 620, 720, 440)}${arrow(1080, 628, 890, 410)}
${text(130, 760, "同一方法，替换动作轴、障碍轴、资源轴和情绪目标。", 34, 'font-weight="700"')}
`));

write("level-design-pitfalls-correction-board.svg", svg("常见陷阱与修正策略", `
<g transform="translate(120 170)">
<rect width="1240" height="560" fill="#fff" stroke="#111" stroke-width="4"/>
<rect width="1240" height="76" fill="#eeeeee"/>
<g stroke="#777" stroke-width="3"><path d="M310 0V560 M620 0V560 M930 0V560 M0 76H1240 M0 172H1240 M0 268H1240 M0 364H1240 M0 460H1240"/></g>
${text(80, 50, "陷阱", 28, 'font-weight="700"')}${text(380, 50, "症状", 28, 'font-weight="700"')}${text(700, 50, "原因", 28, 'font-weight="700"')}${text(1010, 50, "修正", 28, 'font-weight="700"')}
${text(34, 134, "只记内容", 24)}${text(344, 134, "玩家不会用", 24)}${text(654, 134, "资产轴过强", 24)}${text(964, 134, "改成技能轴", 24)}
${text(34, 230, "不记空间", 24)}${text(344, 230, "纸面合理", 24)}${text(654, 230, "缺少尺度", 24)}${text(964, 230, "补blockout", 24)}
${text(34, 326, "一次教太多", 24)}${text(344, 326, "失败说不清", 24)}${text(654, 326, "变量过多", 24)}${text(964, 326, "拆beat", 24)}
${text(34, 422, "只看数据", 24)}${text(344, 422, "知道哪卡", 24)}${text(654, 422, "缺少原因", 24)}${text(964, 422, "加访谈", 24)}
${text(34, 518, "矩阵当真理", 24)}${text(344, 518, "体验被砍", 24)}${text(654, 518, "工具压体验", 24)}${text(964, 518, "证据回写", 24)}
</g>
`));

write("five-beat-blockout-exercise.svg", svg("练习用五段式 Blockout", `
${platformGrid(110, 210, 28, 8, 46, [[0,7,28,1],[0,6,4,1],[6,6,4,1],[12,5,4,2],[18,4,5,3],[25,6,3,1]], [1,5])}
<g font-family="${font}" font-size="24" fill="#111" font-weight="700">
<text x="120" y="626">B01 引介</text><text x="355" y="626">B02 练习</text><text x="585" y="626">B03 验证</text><text x="830" y="626">B04 变奏/峰值</text><text x="1160" y="626">B05 释放</text>
</g>
<rect x="110" y="486" width="70" height="46" fill="${green}" stroke="#111" stroke-width="3"/><text x="145" y="516" font-family="${font}" font-size="18" text-anchor="middle" font-weight="700">ENTER</text>
<rect x="1328" y="486" width="70" height="46" fill="${yellow}" stroke="#111" stroke-width="3"/><text x="1363" y="516" font-family="${font}" font-size="18" text-anchor="middle" font-weight="700">GOAL</text>
`));

console.log(`Generated diagrams in ${outDir}`);

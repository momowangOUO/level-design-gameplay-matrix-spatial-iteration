from __future__ import annotations


COMMON_PROMPT = """
Create a polished 16:9 educational infographic background for a level-design textbook.
Use high information density while keeping every icon, path, obstacle, and panel visually clear.
Use an isometric or clean top-down game-level diagram style, precise icons, visible grid hints,
colored routes, arrows, hazard markers, reward icons, doors, gates, enemies, cameras, switches,
and small representative gameplay scenes where useful.
Important: do not render any readable text, letters, numbers, pseudo-writing, watermark, logo,
or UI captions. Leave clean blank label panels or quiet margins where exact Chinese labels can be
overlaid later. Keep the background light, crisp, and uncluttered; avoid dark cinematic lighting.
The final image should look like a professional game design course diagram, not a sparse slide.
"""


SPECS = [
    {
        "stem": "level-design-curriculum-overview",
        "slug": "level_design_curriculum_overview",
        "title": "教材整体结构",
        "subtitle": "从玩法目标到 Metrics、Gameplay Matrix、Blockout、测试与回写",
        "prompt": COMMON_PROMPT
        + """
Subject: a complete level-design curriculum workflow. Show a left-to-right pipeline with five
large visual stages: player goal, measurable metrics, gameplay matrix, blockout map, playtest
telemetry writeback. Include many small artifacts around the pipeline: ability icon, scale grid,
matrix card, greybox room, heatmap, revision arrows, checklist sheets. Make each stage visually
distinct with clear icons and a representative miniature example.
""",
        "labels": [
            ("玩法目标", "先定义玩家要学什么，而不是先画好看的房间。"),
            ("Metrics", "把身体、跳距、速度、视线与技能半径变成可讨论单位。"),
            ("Gameplay Matrix", "每个 beat 写清动作、障碍、奖励、反馈和情绪。"),
            ("Blockout", "把矩阵落到入口、路线、空间节点与风险位置。"),
            ("测试回写", "用观察、数据和访谈修改矩阵与空间。"),
        ],
    },
    {
        "stem": "core-gameplay-loop-diagram",
        "slug": "core_gameplay_loop_diagram",
        "title": "玩法核心循环",
        "subtitle": "观察目标 -> 执行动作 -> 遭遇阻力 -> 获得反馈 -> 奖励/解锁 -> 调整策略",
        "prompt": COMMON_PROMPT
        + """
Subject: a high-density core gameplay loop. Put a detailed central top-down room blockout in the
middle: player cone of vision, locked door, key, enemy guard, laser gate, crates, spikes, alternate
green route, red danger route, exit door. Around it place six connected loop panels with clear icons:
observe goal, perform action, hazard or enemy, sensory feedback, reward unlock, strategy adjustment.
Use thick directional arrows. Leave blank space in each loop panel for labels.
""",
        "labels": [
            ("观察目标", "入口、出口、锁门、敌人与奖励必须同时给玩家可读线索。"),
            ("执行动作", "移动、跳跃、瞄准、交互或协作，是矩阵中的核心动词。"),
            ("遭遇阻力", "敌人、机关、地形和资源压力会改变玩家动作。"),
            ("反馈信号", "命中、受伤、开门、音效和动效告诉玩家规则是否成立。"),
            ("奖励/解锁", "钥匙、捷径、资源或新路径让循环进入下一轮。"),
            ("调整策略", "玩家根据反馈重新选择路线、节奏或技能组合。"),
        ],
        "label_layout": "loop",
    },
    {
        "stem": "obstacle-action-relation",
        "slug": "obstacle_action_relation",
        "title": "障碍如何改变玩家动作",
        "subtitle": "同一个核心动词会被不同阻力改写成不同关卡问题",
        "prompt": COMMON_PROMPT
        + """
Subject: six representative obstacle micro-scenes arranged as a dense comparison board. Include a
low wall forcing jump timing, moving platform forcing rhythm, narrow gate forcing alignment, enemy
vision cone forcing stealth timing, locked door plus key forcing route planning, optional reward
side path forcing risk choice. Each scene should be a small game-level slice with clear iconography,
arrows, danger color, reward color, and enough geometry to show the action change. No text.
""",
        "labels": [
            ("低墙", "把移动改写成跳跃时机。"),
            ("移动平台", "把跳跃改写成节奏判断。"),
            ("窄门", "把前进改写成角度与速度控制。"),
            ("视线敌人", "把行动改写成观察与等待。"),
            ("锁门/钥匙", "把目标改写成路线规划。"),
            ("支路奖励", "把安全前进改写成风险取舍。"),
        ],
    },
    {
        "stem": "pacing-emotion-curve",
        "slug": "pacing_emotion_curve",
        "title": "节奏与情绪曲线",
        "subtitle": "教学、练习、验证与释放要形成可感知的压力变化",
        "prompt": COMMON_PROMPT
        + """
Subject: a pacing and emotion curve for a game level. Show a rising pressure line over a top-down
or side-scrolling level path with five beats: calm teaching, practice, first pressure, peak
challenge, release reward. Include pressure icons, rest area, resources, enemy clusters, checkpoint,
exit reward, and subtle heat/energy visualization. Make the curve and level path visually connected.
Leave blank label areas near each beat.
""",
        "labels": [
            ("低压教学", "规则首次出现，风险要低，目标要明确。"),
            ("练习段", "重复同一技能，但逐步增加距离、时机或视线。"),
            ("压力峰值", "组合障碍验证玩家是否真正理解规则。"),
            ("释放段", "给奖励、资源或安全空间，让玩家整理经验。"),
            ("回写依据", "卡点、死亡、停留和绕路会暴露节奏问题。"),
        ],
    },
    {
        "stem": "precise-metrics-dual-scale-overview",
        "slug": "metrics_dual_scale_overview",
        "title": "米制标尺总览",
        "subtitle": "角色能力尺标与关卡元素尺标必须使用同一套单位",
        "prompt": COMMON_PROMPT
        + """
Subject: dual-scale metrics overview. Show two connected technical diagrams: left side character
ability metrics with collision box, jump arc, speed arrow, reach circle, skill radius; right side
level element metrics with door width, corridor width, room envelope, enemy aggro radius, reward
distance. Use precise grid hints, transparent colored circles, measurement arrows, and small clean
icons. No text or numerals, leave label panels.
""",
        "labels": [
            ("角色尺标", "身体宽度、跳距、速度、技能半径决定玩家能做到什么。"),
            ("空间尺标", "门宽、通道、房间体量、路线数决定关卡允许什么。"),
            ("风险半径", "敌人视线、警戒区与资源距离共同塑造难度。"),
            ("统一单位", "矩阵、灰盒和测试记录必须引用同一套格距。"),
        ],
    },
    {
        "stem": "precise-character-ability-metrics-grid",
        "slug": "character_ability_metrics_grid",
        "title": "角色能力标尺网格",
        "subtitle": "把身体、跳跃、速度、技能半径画成可复查的单位",
        "prompt": COMMON_PROMPT
        + """
Subject: precise character ability metrics on a large clean grid. Show a side-view platform slice
with a player silhouette, collision box, stable jump arc, risky jump arc, vertical reach, dash or
speed arrow, safe landing zone, and two translucent skill radius circles. Add small icons for body,
jump, speed, reach, attack radius. Keep the grid readable and exact-looking, but no text or numbers.
""",
        "labels": [
            ("身体格", "碰撞盒决定最小通道、台阶和掩体尺度。"),
            ("稳定跳", "新手教学优先使用稳定落点，不要一开始逼极限。"),
            ("风险跳", "风险落点用于验证段，必须给足读秒和反馈。"),
            ("技能半径", "攻击、互动或探测半径要能回写到房间距离。"),
            ("速度/反应", "移动速度决定追逐压力、平台节奏和敌人窗口。"),
        ],
    },
    {
        "stem": "precise-level-element-difficulty-metrics-matrix",
        "slug": "level_element_difficulty_metrics_matrix",
        "title": "关卡元素体量与难度标尺",
        "subtitle": "任何难度调整都要能指出改变的是哪一个空间变量",
        "prompt": COMMON_PROMPT
        + """
Subject: a high-density level element difficulty metrics board. Combine a matrix-like planning
area, three miniature room blockouts, and several metric icons. Show door width, corridor width,
route count, enemy radius, reward distance, line of sight exposure, resource placement. The three
rooms should visibly progress from easy, medium, to hard through geometry and enemy placement.
No readable text or numbers; leave blank table cells and callout panels.
""",
        "labels": [
            ("门/通道", "宽度影响对齐难度、逃生空间和多人协作阻塞。"),
            ("路线数", "单路线强调验证，多路线强调选择与风险分层。"),
            ("敌人半径", "警戒区和视线暴露会把空间变成压力源。"),
            ("资源距离", "奖励靠近风险时，玩家才会做有意义的取舍。"),
            ("难度上调", "只能上调一个或少数变量，避免原因不可诊断。"),
        ],
    },
    {
        "stem": "precise-challenge-matrix-four-variations",
        "slug": "challenge_matrix_four_variations",
        "title": "挑战矩阵四格变体",
        "subtitle": "同一技能可以按方向、距离、组合和缺口风险形成四种变体",
        "prompt": COMMON_PROMPT
        + """
Subject: four precise side-view platform challenge variations arranged in a 2 by 2 board. Each panel
shows a different jump challenge on a clean grid: simple vertical jump, difficult vertical jump,
simple combined gap and height, difficult or incomplete combined challenge. Use player silhouette,
jump arcs, landing zones, hazards, safe and risky color coding. Dense but clear. No text or numbers.
""",
        "labels": [
            ("纵向简单", "低高度、宽落点，用于首次教学。"),
            ("纵向困难", "更高、更窄，但不要同时引入新规则。"),
            ("组合简单", "横向 + 纵向组合，用于练习迁移。"),
            ("组合困难", "距离、时机和落点同时逼近上限，适合验证段。"),
        ],
    },
    {
        "stem": "precise-horizontal-jump-metrics-comparison",
        "slug": "horizontal_jump_metrics_comparison",
        "title": "横向跳跃简单与困难对照",
        "subtitle": "同一横跳技能，难度来自坑宽、落点宽度与失败代价",
        "prompt": COMMON_PROMPT
        + """
Subject: a clear side-by-side horizontal jump metrics comparison. Left panel: simple short gap with
wide landing zone and visible safe arc. Right panel: longer gap with narrow landing zone, spike pit,
risk arc, and higher failure cost. Use grid background, player icon, arrows, safe green and risk red
landing zones. No text or numbers, leave label areas.
""",
        "labels": [
            ("简单横跳", "短坑 + 宽落点，让玩家确认基础输入。"),
            ("困难横跳", "长坑 + 窄落点，把失败代价和压力拉高。"),
            ("稳定区", "稳定落点应覆盖新手误差。"),
            ("风险区", "风险落点必须有清楚预警和即时反馈。"),
        ],
    },
    {
        "stem": "gameplay-matrix-axes",
        "slug": "gameplay_matrix_axes",
        "title": "Gameplay Matrix 轴线结构",
        "subtitle": "把玩家动作、阻力、奖励、反馈与情绪放进同一张可讨论表",
        "prompt": COMMON_PROMPT
        + """
Subject: a filled gameplay matrix board without readable text. Show a clean table-like grid with
colored rows and columns, highlighted cells, arrows from a small level path into matrix cells, and
icons for action, obstacle, resource, feedback, emotion, and beat order. Include small mini-scenes
around the table demonstrating how cells map to space. No letters or numbers; leave room for labels.
""",
        "labels": [
            ("动作轴", "反复执行的核心动词。"),
            ("障碍轴", "改变动作条件。"),
            ("奖励轴", "引导冒险价值。"),
            ("反馈轴", "解释成败原因。"),
            ("情绪轴", "记录压力曲线。"),
        ],
    },
    {
        "stem": "platform-world-1-2-progression",
        "slug": "platform_world_1_2_progression",
        "title": "平台动作关卡进程",
        "subtitle": "五段式教学：引入、练习、变奏、验证、释放",
        "prompt": COMMON_PROMPT
        + """
Subject: a representative side-scrolling platformer level progression with five beats. Show a long
platform path with coins, stars, short pits, moving platforms, one enemy, checkpoint, and exit flag.
Use clear beat segmentation, increasing obstacle complexity, arrows along the route, reward trails,
and safe rest spaces. No readable text or numbers; leave blank beat labels.
""",
        "labels": [
            ("B01 引入", "低风险看到出口，确认移动与跳跃目标。"),
            ("B02 练习", "短坑、宽落点，重复稳定跳。"),
            ("B03 变奏", "加入节奏或移动平台，但保持规则一致。"),
            ("B04 验证", "组合坑、敌人或高度，检查掌握程度。"),
            ("B05 释放", "低压奔向终点，用奖励收束节奏。"),
        ],
    },
    {
        "stem": "platform-world-1-2-blockout",
        "slug": "platform_world_1_2_blockout",
        "title": "平台动作 Blockout 草图",
        "subtitle": "把五段式矩阵落成横向空间、坑位、台阶与奖励线",
        "prompt": COMMON_PROMPT
        + """
Subject: platformer blockout sketch. Use a clean side-view greybox level with five connected beats:
entrance, short jump, repeated gaps, high platform or enemy gate, exit reward. Include player start,
arrows, pits, coins, enemy, checkpoint, secret or optional reward ledge, and simple metric grid.
Make the geometry precise and readable. No text or numbers.
""",
        "labels": [
            ("入口", "先让玩家看懂目标与路径方向。"),
            ("短跳", "用低风险空间验证基础输入。"),
            ("连续短跳", "保持坑宽一致，让玩家练习节奏。"),
            ("组合验证", "把高度、敌人或奖励支路合在一起。"),
            ("出口释放", "降低压力，让节奏自然落下。"),
        ],
    },
    {
        "stem": "portal-fling-tutorial-arc",
        "slug": "portal_fling_tutorial_arc",
        "title": "解谜教学弧线",
        "subtitle": "观察 -> 操作 -> 反馈 -> 复用，避免没教就考",
        "prompt": COMMON_PROMPT
        + """
Subject: puzzle tutorial arc inspired by portal-based momentum puzzles, but generic. Show five small
puzzle-room panels connected left to right: observe unreachable exit, place two portals, launch arc,
land on upper platform, reuse with timing or switch. Include portal rings, cubes, switches, doors,
trajectory arcs, eye icons, feedback flashes. No text or letters; leave labels.
""",
        "labels": [
            ("观察", "先让玩家看到目标、缺口和可交互墙面。"),
            ("操作", "再允许玩家放置、移动或触发机关。"),
            ("反馈", "抛射轨迹、门开、音效和光效确认规则。"),
            ("复用", "同一规则换空间，不要突然换玩法。"),
            ("验证", "把时机、路线或资源限制加入题目。"),
        ],
    },
    {
        "stem": "portal-fling-room-blockout",
        "slug": "portal_fling_room_blockout",
        "title": "解谜房间 Blockout",
        "subtitle": "入口、Portal 面、抛射轨迹、目标平台与反馈线",
        "prompt": COMMON_PROMPT
        + """
Subject: one detailed puzzle room blockout for a portal-like fling mechanic. Show a clean top-down
or sectional room: entrance, low platform, high exit platform, two colored portal surfaces, tall
barrier, cube, switch, locked door, momentum trajectory arc, sightline arrows, safe landing area,
feedback light. No readable text or numbers, leave callout panels.
""",
        "labels": [
            ("入口视线", "玩家进门后必须能看到目标与障碍关系。"),
            ("Portal 面", "可交互表面要和目标路径形成清晰因果。"),
            ("抛射轨迹", "轨迹必须可预判，失败也要可解释。"),
            ("目标平台", "落点大小决定题目的容错。"),
            ("反馈线", "门、灯、音效和动线共同确认解法。"),
        ],
    },
    {
        "stem": "doom-arena-encounter-layout",
        "slug": "doom_arena_encounter_layout",
        "title": "射击竞技场遭遇布局",
        "subtitle": "环形动线、掩体、资源、敌人角度共同制造战斗节奏",
        "prompt": COMMON_PROMPT
        + """
Subject: dense top-down shooter arena encounter layout. Show a loop route around the arena, several
cover blocks, enemy spawn points, crossfire cones, ammo and health pickups, high-value armor reward,
locked exit, central danger zone, flanking lane, and player route arrows. Use clear colors for player
path, enemy pressure, resources, and exits. No text or numbers; leave labels.
""",
        "labels": [
            ("环形动线", "让玩家持续移动，而不是躲在单一掩体后。"),
            ("交叉火力", "敌人角度决定压力峰值。"),
            ("资源诱导", "弹药、血包和护甲把玩家拉向风险区。"),
            ("安全窗口", "短暂掩体和转角用于恢复判断。"),
            ("出口释放", "清场后节奏下降，允许玩家复盘。"),
        ],
    },
    {
        "stem": "coop-role-responsibility-matrix",
        "slug": "coop_role_responsibility_matrix",
        "title": "合作关卡角色责任矩阵",
        "subtitle": "多人关卡要把观察、承压、输出、救援和兑现分清",
        "prompt": COMMON_PROMPT
        + """
Subject: cooperative level responsibility matrix as a split-room blockout. Show two or three player
roles with distinct colors, separated rooms, switches, doors, sightlines, enemy pressure, rescue
route, shared reward, and synchronized arrows. Include small icons for scout, defender, damage,
support, switch, revive, reward. Dense but clear, no text or letters.
""",
        "labels": [
            ("观察者", "负责发现路线、机关和敌人窗口。"),
            ("承压者", "吸引风险或控制敌人视线。"),
            ("输出者", "在窗口内完成击杀、破坏或推进。"),
            ("支援者", "补给、救援、开门或保护撤退。"),
            ("共同兑现", "奖励和出口必须让所有角色看到贡献。"),
        ],
    },
    {
        "stem": "level-design-iteration-loop",
        "slug": "level_design_iteration_loop",
        "title": "关卡设计迭代闭环",
        "subtitle": "假设、白盒、测试、观察、回写，形成下一轮设计证据",
        "prompt": COMMON_PROMPT
        + """
Subject: level design iteration loop. Show six connected stages around a central greybox map:
design hypothesis, quick blockout, playable test, observation and telemetry, matrix writeback,
next revision. Include notebooks, grid map, controller, heatmap, video review, bug/fix markers,
arrows and revision stamps. No readable text; leave label panels.
""",
        "labels": [
            ("概念假设", "先写玩家应学会什么。"),
            ("白盒布局", "用最少美术成本验证空间关系。"),
            ("可玩测试", "让真实操作暴露问题。"),
            ("观察/遥测", "记录死亡、停留、绕路与误解。"),
            ("矩阵回写", "修改原因，而不是只改表面。"),
            ("下一轮", "每轮迭代都要保留证据。"),
        ],
    },
    {
        "stem": "blockout-level-layout",
        "slug": "blockout_level_layout",
        "title": "Blockout 关卡布局",
        "subtitle": "五段 Beat 的空间拼接：入口、障碍、奖励、验证与出口",
        "prompt": COMMON_PROMPT
        + """
Subject: detailed top-down and side-view hybrid blockout map for a five-beat level. Show entrance,
teaching room, practice corridor, optional reward branch, pressure room, validation room, exit,
locked shortcut, enemy patrol cones, resource pickups, checkpoints, and colored player routes.
Use greybox geometry, grid, arrows, and heat hints. No readable text; leave callout panels.
""",
        "labels": [
            ("Beat 对位", "矩阵里的每个 beat 都要有空间位置。"),
            ("主路线", "从入口到出口承载教学顺序。"),
            ("支路奖励", "用风险和距离制造选择。"),
            ("验证房间", "组合前面教过的动作，不突然换规则。"),
            ("回写点", "测试卡点应能定位到具体房间与矩阵格。"),
        ],
    },
    {
        "stem": "telemetry-heatmap-matrix-writeback",
        "slug": "telemetry_heatmap_matrix_writeback",
        "title": "遥测热图与矩阵回写",
        "subtitle": "用死亡、停留、绕路和访谈证据修改矩阵假设",
        "prompt": COMMON_PROMPT
        + """
Subject: telemetry heatmap writeback board. Show a blockout map with overlaid heatmap blobs for
death, long dwell time, failed jumps, backtracking, and route detours. On the side show a clean
matrix-style evidence board with colored cells, arrows from map hot spots to matrix cells, video
review thumbnails, interview icon, and fix markers. No text or numbers; leave labels.
""",
        "labels": [
            ("死亡热区", "说明失败位置，但不能单独解释原因。"),
            ("停留热区", "可能是迷路、观察或资源决策。"),
            ("绕路轨迹", "暴露目标引导、奖励诱导或风险认知问题。"),
            ("访谈/录像", "补充玩家为什么这样做。"),
            ("矩阵回写", "把证据写回动作、障碍、奖励或反馈格。"),
        ],
    },
    {
        "stem": "genre-matrix-adaptation",
        "slug": "genre_matrix_adaptation",
        "title": "不同类型关卡的矩阵适配",
        "subtitle": "同一套矩阵方法，在不同类型中替换核心动词和验证指标",
        "prompt": COMMON_PROMPT
        + """
Subject: six genre adaptation cards around a shared gameplay matrix core. Show representative mini
scenes for platformer, puzzle, shooter, stealth or extraction, cooperative play, and open-world
exploration. Each card should have distinctive gameplay icons, route arrows, obstacles, rewards,
and test evidence icons. Center shows a neutral matrix/grid hub. No readable text, leave labels.
""",
        "labels": [
            ("平台动作", "跳距、落点、节奏与失败代价。"),
            ("解谜", "观察、假设、操作、反馈。"),
            ("射击", "掩体、火力角度、资源和移动压力。"),
            ("搜打撤/潜行", "路线风险、信息、资源和撤离窗口。"),
            ("合作", "角色分工、同步窗口和互救责任。"),
            ("开放世界", "目标引导、探索密度和节奏分区。"),
        ],
    },
    {
        "stem": "level-design-pitfalls-correction-board",
        "slug": "level_design_pitfalls_correction_board",
        "title": "常见陷阱与修正策略",
        "subtitle": "从症状回到矩阵、空间、标尺和测试证据",
        "prompt": COMMON_PROMPT
        + """
Subject: common level design pitfalls and correction board. Show six diagnostic cards with small
game-level scenes: too many enemies, missing objective visibility, unfair jump, reward with no risk,
matrix disconnected from blockout, telemetry ignored. Add correction arrows, tool icons, checklist
marks, heatmap hints, and before/after mini-scenes. No readable text; leave labels.
""",
        "labels": [
            ("只加数量", "敌人更多不等于设计更难，先改位置、视线和资源。"),
            ("目标不清", "入口视线、出口信号和奖励线索不足。"),
            ("缺少尺度", "坑宽、门宽、技能半径没有和角色能力对齐。"),
            ("奖励无风险", "奖励没有形成选择，只是装饰。"),
            ("矩阵悬空", "表格写得整齐，但没有落到空间。"),
            ("忽略证据", "测试数据没有回写到下一版设计。"),
        ],
    },
    {
        "stem": "five-beat-blockout-exercise",
        "slug": "five_beat_blockout_exercise",
        "title": "练习用五段式 Blockout",
        "subtitle": "把一张矩阵转成可走、可测、可复盘的空间草图",
        "prompt": COMMON_PROMPT
        + """
Subject: a practical five-beat blockout exercise worksheet, but without any text. Show five vertical
or horizontal panels for teaching, practice, variation, validation, release. Each panel contains a
mini greybox room with entrance, obstacle, reward, exit, route arrows, hazard icons, and blank task
areas. Include a small checklist area, evidence icons, and a final writeback arrow. No text/numbers.
""",
        "labels": [
            ("引入", "只放一个新规则，让玩家安全理解。"),
            ("练习", "重复核心动作，保持失败代价低。"),
            ("变奏", "改变空间条件，不改变核心规则。"),
            ("验证", "组合前面学过的内容，提高压力。"),
            ("释放", "给出口、奖励或低压空间收束。"),
            ("检查", "每段都要有动作、障碍、奖励、反馈和情绪目标。"),
        ],
    },
]

$ErrorActionPreference = 'Stop'
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()
Add-Type -AssemblyName System.Drawing

$Root = 'C:\Users\liyian.andy\Desktop\搜打撤'
$AssetDir = Join-Path $Root 'assets\generated-level-design'
$W = 1600
$H = 900

$Black = [System.Drawing.Color]::FromArgb(24, 26, 30)
$Gray = [System.Drawing.Color]::FromArgb(112, 120, 132)
$Grid = [System.Drawing.Color]::FromArgb(204, 210, 218)
$Magenta = [System.Drawing.Color]::FromArgb(183, 28, 106)
$Blue = [System.Drawing.Color]::FromArgb(22, 174, 232)
$Green = [System.Drawing.Color]::FromArgb(137, 199, 83)
$Orange = [System.Drawing.Color]::FromArgb(244, 177, 131)
$Yellow = [System.Drawing.Color]::FromArgb(255, 217, 102)
$Red = [System.Drawing.Color]::FromArgb(227, 49, 49)
$Purple = [System.Drawing.Color]::FromArgb(126, 95, 190)
$Wall = [System.Drawing.Color]::FromArgb(36, 39, 44)
$Floor = [System.Drawing.Color]::FromArgb(255, 238, 220)
$Door = [System.Drawing.Color]::FromArgb(219, 237, 252)

function Font($size, $style = 'Regular') {
  New-Object System.Drawing.Font('Microsoft YaHei', $size, [System.Drawing.FontStyle]::$style, [System.Drawing.GraphicsUnit]::Pixel)
}

$FTitle = Font 36 'Regular'
$FHead = Font 24 'Bold'
$FBody = Font 17 'Regular'
$FSmall = Font 14 'Regular'
$FTiny = Font 12 'Regular'

$FmtCenter = New-Object System.Drawing.StringFormat
$FmtCenter.Alignment = [System.Drawing.StringAlignment]::Center
$FmtCenter.LineAlignment = [System.Drawing.StringAlignment]::Center
$FmtLeft = New-Object System.Drawing.StringFormat
$FmtLeft.Alignment = [System.Drawing.StringAlignment]::Near
$FmtLeft.LineAlignment = [System.Drawing.StringAlignment]::Near

function Brush($color, $alpha = 255) {
  New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb($alpha, $color))
}

function PenObj($color, $width = 2, $alpha = 255) {
  New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb($alpha, $color), $width)
}

function Text($g, $s, $font, $color, $x, $y, $w, $h, $fmt = $FmtLeft) {
  $b = Brush $color
  $g.DrawString($s, $font, $b, [System.Drawing.RectangleF]::new($x, $y, $w, $h), $fmt)
  $b.Dispose()
}

function Title($g, $title) {
  Text $g $title $FTitle $Black 64 45 1200 48
  $p = PenObj $Magenta 3
  $g.DrawLine($p, 56, 104, 1544, 104)
  $p.Dispose()
}

function Rect($g, $x, $y, $w, $h, $fill, $stroke = $Black, $sw = 2, $alpha = 255) {
  $b = Brush $fill $alpha
  $g.FillRectangle($b, $x, $y, $w, $h)
  $b.Dispose()
  if ($stroke) {
    $p = PenObj $stroke $sw
    $g.DrawRectangle($p, $x, $y, $w, $h)
    $p.Dispose()
  }
}

function Line($g, $x1, $y1, $x2, $y2, $color = $Black, $width = 2) {
  $p = PenObj $color $width
  $g.DrawLine($p, $x1, $y1, $x2, $y2)
  $p.Dispose()
}

function Arrow($g, $x1, $y1, $x2, $y2, $color = $Orange, $width = 4) {
  $p = PenObj $color $width
  $cap = New-Object System.Drawing.Drawing2D.AdjustableArrowCap(7, 7)
  $p.CustomEndCap = $cap
  $g.DrawLine($p, $x1, $y1, $x2, $y2)
  $p.Dispose(); $cap.Dispose()
}

function Dot($g, $x, $y, $r, $color, $label = '') {
  $b = Brush $color
  $g.FillEllipse($b, $x - $r, $y - $r, $r * 2, $r * 2)
  $b.Dispose()
  if ($label) { Text $g $label $FSmall ([System.Drawing.Color]::White) ($x - $r) ($y - 10) ($r * 2) 22 $FmtCenter }
}

function Grid($g, $x, $y, $cols, $rows, $cell) {
  Rect $g $x $y ($cols * $cell) ($rows * $cell) ([System.Drawing.Color]::White) $Black 2
  $p = PenObj $Grid 1
  for ($i = 1; $i -lt $cols; $i++) {
    $xx = $x + $i * $cell
    $g.DrawLine($p, $xx, $y, $xx, $y + $rows * $cell)
  }
  for ($j = 1; $j -lt $rows; $j++) {
    $yy = $y + $j * $cell
    $g.DrawLine($p, $x, $yy, $x + $cols * $cell, $yy)
  }
  $p.Dispose()
}

function CellRect($g, $x, $y, $cell, $cx, $cy, $cw, $ch, $fill, $stroke = $Black, $alpha = 255) {
  Rect $g ($x + $cx * $cell) ($y + $cy * $cell) ($cw * $cell) ($ch * $cell) $fill $stroke 2 $alpha
}

function Room($g, $x, $y, $cols, $rows, $cell, $title) {
  Grid $g $x $y $cols $rows $cell
  Text $g $title $FBody $Black $x ($y - 30) ($cols * $cell) 26 $FmtCenter
}

function SavePng($name, $title, [scriptblock]$draw) {
  $bmp = New-Object System.Drawing.Bitmap($W, $H)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
  $g.Clear([System.Drawing.Color]::White)
  Title $g $title
  & $draw $g
  $path = Join-Path $AssetDir $name
  $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose()
  $bmp.Dispose()
}

SavePng 'precise-metrics-dual-scale-overview.png' '米制/标尺（Metrics）：角色能力尺标 + 关卡元素尺标' {
  param($g)
  Text $g '角色能力尺标：先量玩家能做什么' $FHead $Black 80 135 620 34
  Text $g '用于定义身体、速度、跳跃、技能半径。所有坑宽、墙高、平台距离都从这里派生。' $FBody $Black 80 172 650 48

  $gx = 90; $gy = 260; $cell = 42
  Grid $g $gx $gy 13 6 $cell
  CellRect $g $gx $gy $cell 1 4 1 1 $Blue
  CellRect $g $gx $gy $cell 1 1 1 3 ([System.Drawing.Color]::FromArgb(190,190,190)) $null 170
  CellRect $g $gx $gy $cell 2 4 3 1 $Orange $null 210
  CellRect $g $gx $gy $cell 5 4 1 1 ([System.Drawing.Color]::White) $Orange 255
  Text $g '1×1 身体格' $FSmall $Black 80 535 160 24
  Text $g '纵向可达 3 格' $FSmall $Black 222 535 180 24
  Text $g '稳定横跳 3 格；第 4 格为风险区' $FSmall $Black 410 535 310 24
  Arrow $g 132 600 300 600 $Blue 5
  Text $g '移动速度：4 格/秒' $FBody $Black 95 620 260 28

  Dot $g 560 315 13 $Blue ''
  $b = Brush $Blue 60; $g.FillEllipse($b, 476, 231, 168, 168); $b.Dispose()
  Dot $g 560 455 13 $Red ''
  $b = Brush $Red 55; $g.FillEllipse($b, 434, 329, 252, 252); $b.Dispose()
  Text $g '技能半径示例' $FHead $Black 720 286 260 30
  Text $g '侦察/声呐：半径 2 格' $FBody $Black 720 330 280 28
  Text $g '爆炸/范围伤害：半径 3 格' $FBody $Black 720 450 300 28

  Line $g 800 140 800 805 $Grid 2

  Text $g '关卡元素尺标：再量空间如何承载玩法' $FHead $Black 850 135 650 34
  Text $g '用于定义门宽、通道宽、房间体量、敌人范围、资源距离和视线暴露。' $FBody $Black 850 172 650 48

  $rx = 900; $ry = 270; $rc = 54
  Room $g $rx $ry 8 5 $rc '房间：8×5 格，主通道宽 2 格'
  CellRect $g $rx $ry $rc 0 2 8 1 $Floor $null 255
  CellRect $g $rx $ry $rc 6 0 1 5 $Door $null 255
  Rect $g ($rx - 76) ($ry + 2 * $rc) 76 $rc $Green $Green 2
  Text $g 'ENTER' $FBody $Black ($rx - 76) ($ry + 2 * $rc + 15) 76 28 $FmtCenter
  Rect $g ($rx + 7 * $rc) ($ry + 1 * $rc) (0.55 * $rc) (0.55 * $rc) ([System.Drawing.Color]::White) $Black 3
  Rect $g ($rx + 7 * $rc) ($ry + 3 * $rc) (0.55 * $rc) (0.55 * $rc) ([System.Drawing.Color]::White) $Black 3
  Dot $g ($rx + 3 * $rc) ($ry + 2.5 * $rc) 18 $Red '敌'
  $b = Brush $Red 45; $g.FillEllipse($b, ($rx + 3 * $rc - 2 * $rc), ($ry + 2.5 * $rc - 2 * $rc), 4 * $rc, 4 * $rc); $b.Dispose()
  Arrow $g ($rx + 1 * $rc) ($ry + 4.5 * $rc) ($rx + 5 * $rc) ($ry + 4.5 * $rc) $Orange 4
  Text $g '奖励距离：4 格' $FSmall $Black ($rx + 1 * $rc) ($ry + 4.55 * $rc) 230 24
  Text $g '敌人半径 2 格；通道、门、出口都按格记录' $FBody $Black 900 590 520 30

  Text $g '读法：左图决定玩家能力边界；右图决定空间、敌人和资源如何落入同一套单位。' $FHead $Black 105 790 1360 34
}

SavePng 'precise-character-ability-metrics-grid.png' '角色能力尺标：身体、速度、跳跃、技能半径' {
  param($g)
  $gx = 470; $gy = 160; $cell = 72
  Grid $g $gx $gy 13 7 $cell
  Text $g '屏幕大小：7×13；每格都是可被关卡引用的设计单位' $FBody $Black $gx ($gy + 7 * $cell + 16) 820 30 $FmtCenter

  CellRect $g $gx $gy $cell 0 6 1 1 $Blue
  CellRect $g $gx $gy $cell 0 3 1 3 ([System.Drawing.Color]::FromArgb(190,190,190)) $null 185
  CellRect $g $gx $gy $cell 1 6 3 1 $Orange $null 215
  CellRect $g $gx $gy $cell 4 6 1 1 ([System.Drawing.Color]::White) $Orange 255
  Line $g ($gx + 0.5 * $cell) ($gy + 6 * $cell) ($gx + 0.5 * $cell) ($gy + 3 * $cell) $Gray 2
  Arrow $g ($gx + 0.5 * $cell) ($gy + 6.5 * $cell) ($gx + 4.5 * $cell) ($gy + 6.5 * $cell) $Orange 4

  Text $g '图例' $FHead $Black 85 150 160 28
  Rect $g 85 210 70 70 $Blue $null
  Text $g '主角：1×1 碰撞盒' $FBody $Black 180 230 260 28
  Rect $g 85 325 70 70 ([System.Drawing.Color]::FromArgb(190,190,190)) $null
  Text $g '纵向可达：向上 3 格' $FBody $Black 180 345 260 28
  Rect $g 85 440 70 70 $Orange $null 2 210
  Text $g '横向稳定跳：3 格' $FBody $Black 180 460 260 28
  Rect $g 85 555 70 70 ([System.Drawing.Color]::White) $Orange 4
  Text $g '第 4 格：风险落点' $FBody $Black 180 575 260 28
  Arrow $g 85 690 245 690 $Blue 5
  Text $g '移动速度：4 格/秒' $FBody $Black 180 705 260 28

  Dot $g 1250 280 15 $Green ''
  $b = Brush $Green 60; $g.FillEllipse($b, 1106, 136, 288, 288); $b.Dispose()
  Text $g '交互/治疗半径：2 格' $FBody $Black 1165 435 310 28
  Dot $g 1250 575 15 $Red ''
  $b = Brush $Red 50; $g.FillEllipse($b, 1034, 359, 432, 432); $b.Dispose()
  Text $g '爆炸/伤害半径：3 格' $FBody $Black 1165 800 310 28
}

SavePng 'precise-level-element-difficulty-metrics-matrix.png' '关卡元素尺标：体量 × 难度 × 敌人配置' {
  param($g)
  $x = 70; $y = 150; $cw = 150; $rh = 80
  $headers = @('体量 / 难度', '简单', '中等', '困难')
  $rows = @('小型`n5房·24格/8间', '中型`n7房·30格/10间', '大型`n9房·36格/12间')
  $fills = @([System.Drawing.Color]::FromArgb(238,238,238), $Green, $Yellow, [System.Drawing.Color]::FromArgb(221,115,22))
  for ($c = 0; $c -lt 4; $c++) {
    Rect $g ($x + $c * $cw) $y $cw $rh $fills[$c] $Black 2
    Text $g $headers[$c] $FBody $Black ($x + $c * $cw) ($y + 22) $cw 30 $FmtCenter
  }
  for ($r = 0; $r -lt 3; $r++) {
    Rect $g $x ($y + ($r + 1) * $rh) $cw $rh ([System.Drawing.Color]::FromArgb(245,245,245)) $Black 2
    Text $g $rows[$r] $FSmall $Black $x ($y + ($r + 1) * $rh + 15) $cw 50 $FmtCenter
    for ($c = 1; $c -lt 4; $c++) {
      Rect $g ($x + $c * $cw) ($y + ($r + 1) * $rh) $cw $rh ([System.Drawing.Color]::White) $Black 2
      $time = @(2, 3, 4, 5, 6, 7)[[Math]::Min(5, $r * 2 + $c - 1)]
      $death = @(0,10,30,0,20,40)[[Math]::Min(5, $r * 2 + $c - 1)]
      Text $g ("时长 {0}m`n死亡率 {1}%" -f $time, $death) $FTiny $Black ($x + $c * $cw) ($y + ($r + 1) * $rh + 22) $cw 38 $FmtCenter
    }
  }
  $ey = 560
  $enemyHeaders = @('敌人种类', '普通敌人', '精英敌人', 'BOSS敌人', '敌方英雄小队')
  for ($c = 0; $c -lt 5; $c++) {
    Rect $g (70 + $c * 130) $ey 130 55 ([System.Drawing.Color]::White) $Black 2
    Text $g $enemyHeaders[$c] $FSmall $Black (70 + $c * 130) ($ey + 16) 130 24 $FmtCenter
    Rect $g (70 + $c * 130) ($ey + 55) 130 55 ([System.Drawing.Color]::White) $Black 2
  }
  Text $g '参考交战时间' $FSmall $Black 70 ($ey + 72) 130 24 $FmtCenter

  Text $g '元素尺标必须在房间小图中同步画出' $FHead $Black 835 145 620 32
  Text $g '门宽、通道宽、路线数、敌人半径、资源距离，都要和左侧矩阵使用同一格数。' $FBody $Black 835 182 650 48
  $rx = 900; $ry = 260; $cell = 52
  Room $g $rx $ry 8 3 $cell '简单体量：2 条路径，每条 1 个敌人'
  CellRect $g $rx $ry $cell 0 1 8 1 $Floor $null 255
  CellRect $g $rx $ry $cell 6 0 1 3 $Door $null 255
  Rect $g ($rx - 82) ($ry + 1 * $cell) 82 $cell $Green $Green 2
  Text $g 'ENTER' $FBody $Black ($rx - 82) ($ry + $cell + 14) 82 28 $FmtCenter
  Dot $g ($rx + 2.5 * $cell) ($ry + 1.5 * $cell) 16 $Red '敌'
  $b = Brush $Red 42; $g.FillEllipse($b, ($rx + 2.5 * $cell - 1.5 * $cell), ($ry + 1.5 * $cell - 1.5 * $cell), 3 * $cell, 3 * $cell); $b.Dispose()
  Rect $g ($rx + 7 * $cell) ($ry + 0.65 * $cell) 30 30 ([System.Drawing.Color]::White) $Black 3

  $ry2 = 555
  Room $g $rx $ry2 8 4 $cell '中等体量：3 条路径，敌人错位压迫'
  CellRect $g $rx $ry2 $cell 0 1 8 1 $Floor $null 255
  CellRect $g $rx $ry2 $cell 0 3 8 1 $Floor $null 255
  CellRect $g $rx $ry2 $cell 6 0 1 4 $Door $null 255
  Rect $g ($rx - 82) ($ry2 + 2 * $cell) 82 $cell $Green $Green 2
  Text $g 'ENTER' $FBody $Black ($rx - 82) ($ry2 + 2 * $cell + 14) 82 28 $FmtCenter
  Dot $g ($rx + 2.5 * $cell) ($ry2 + 1.5 * $cell) 16 $Red '敌'
  Dot $g ($rx + 4.5 * $cell) ($ry2 + 3.5 * $cell) 16 $Red '敌'
  Dot $g ($rx + 5.3 * $cell) ($ry2 + 0.7 * $cell) 16 $Purple '精'
  Arrow $g ($rx + 1 * $cell) ($ry2 + 4.45 * $cell) ($rx + 5 * $cell) ($ry2 + 4.45 * $cell) $Orange 4
  Text $g '资源距离 4 格' $FTiny $Black ($rx + 1 * $cell) ($ry2 + 4.5 * $cell) 220 24

  Text $g '左侧是规划矩阵；右侧是对应空间尺标。任何一格难度上调，都要能在房间图里指出改变了什么。' $FBody $Black 75 790 1380 34
}

Write-Host 'Regenerated 3 precise metrics PNG diagrams with explicit ability and element scales.'

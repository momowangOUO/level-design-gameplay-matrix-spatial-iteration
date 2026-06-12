$ErrorActionPreference = 'Stop'
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()
Add-Type -AssemblyName System.Drawing

$Root = 'C:\Users\liyian.andy\Desktop\搜打撤'
$OutPath = Join-Path $Root 'assets\generated-level-design\precise-level-element-difficulty-metrics-matrix.png'
$IconDir = Join-Path $Root 'assets\generated-level-design\image2-icons'
$W = 1600
$H = 900

$Black = [System.Drawing.Color]::FromArgb(22,24,28)
$Grid = [System.Drawing.Color]::FromArgb(198,205,214)
$Magenta = [System.Drawing.Color]::FromArgb(183,28,106)
$Green = [System.Drawing.Color]::FromArgb(137,199,83)
$Yellow = [System.Drawing.Color]::FromArgb(255,217,102)
$Orange = [System.Drawing.Color]::FromArgb(221,115,22)
$Red = [System.Drawing.Color]::FromArgb(227,49,49)
$Blue = [System.Drawing.Color]::FromArgb(31,136,229)
$Wall = [System.Drawing.Color]::FromArgb(32,35,40)
$Floor = [System.Drawing.Color]::FromArgb(255,238,220)
$Door = [System.Drawing.Color]::FromArgb(220,239,255)
$Purple = [System.Drawing.Color]::FromArgb(126,95,190)

function Font($size, $style = 'Regular') {
  New-Object System.Drawing.Font('Microsoft YaHei', $size, [System.Drawing.FontStyle]::$style, [System.Drawing.GraphicsUnit]::Pixel)
}

$FTitle = Font 36 'Bold'
$FHead = Font 22 'Bold'
$FBody = Font 16 'Regular'
$FSmall = Font 13 'Regular'
$FTiny = Font 11 'Regular'

$FmtCenter = New-Object System.Drawing.StringFormat
$FmtCenter.Alignment = [System.Drawing.StringAlignment]::Center
$FmtCenter.LineAlignment = [System.Drawing.StringAlignment]::Center
$FmtLeft = New-Object System.Drawing.StringFormat
$FmtLeft.Alignment = [System.Drawing.StringAlignment]::Near
$FmtLeft.LineAlignment = [System.Drawing.StringAlignment]::Near
$script:IconCache = @{}

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

function Line($g, $x1, $y1, $x2, $y2, $color = $Black, $width = 2, $alpha = 255) {
  $p = PenObj $color $width $alpha
  $g.DrawLine($p, $x1, $y1, $x2, $y2)
  $p.Dispose()
}

function Arrow($g, $x1, $y1, $x2, $y2, $color, $width = 4, $dash = $false) {
  $p = PenObj $color $width
  if ($dash) { $p.DashStyle = [System.Drawing.Drawing2D.DashStyle]::Dash }
  $cap = New-Object System.Drawing.Drawing2D.AdjustableArrowCap(7, 7)
  $p.CustomEndCap = $cap
  $g.DrawLine($p, $x1, $y1, $x2, $y2)
  $p.Dispose(); $cap.Dispose()
}

function Circle($g, $x, $y, $r, $color, $alpha = 60) {
  $b = Brush $color $alpha
  $g.FillEllipse($b, $x - $r, $y - $r, $r * 2, $r * 2)
  $b.Dispose()
}

function GetIcon($name) {
  if (-not $script:IconCache.ContainsKey($name)) {
    $path = Join-Path $IconDir ($name + '.png')
    $script:IconCache[$name] = [System.Drawing.Image]::FromFile($path)
  }
  return $script:IconCache[$name]
}

function DrawIcon($g, $name, $x, $y, $size = 36) {
  $img = GetIcon $name
  $rect = [System.Drawing.RectangleF]::new($x - $size / 2, $y - $size / 2, $size, $size)
  $g.DrawImage($img, $rect)
}

function EnemyIcon($g, $x, $y, $kind = 'normal') {
  $icon = switch ($kind) {
    'elite' { 'elite' }
    'boss' { 'boss' }
    'squad' { 'squad' }
    default { 'enemy' }
  }
  $size = if ($kind -eq 'boss') { 48 } elseif ($kind -eq 'squad') { 54 } else { 38 }
  DrawIcon $g $icon $x $y $size
}

function GoalIcon($g, $x, $y) {
  DrawIcon $g 'goal' $x $y 44
}

function DoorIcon($g, $x, $y) {
  DrawIcon $g 'door' $x $y 48
}

function StarIcon($g, $x, $y) {
  DrawIcon $g 'reward' $x $y 40
}

function GridRoom($g, $x, $y, $cols, $rows, $cell) {
  Rect $g $x $y ($cols * $cell) ($rows * $cell) ([System.Drawing.Color]::White) $Black 3
  $p = PenObj $Grid 1
  for ($i=1; $i -lt $cols; $i++) {
    $xx = $x + $i * $cell
    $g.DrawLine($p, $xx, $y, $xx, $y + $rows * $cell)
  }
  for ($j=1; $j -lt $rows; $j++) {
    $yy = $y + $j * $cell
    $g.DrawLine($p, $x, $yy, $x + $cols * $cell, $yy)
  }
  $p.Dispose()
}

function CellRect($g, $x, $y, $cell, $cx, $cy, $cw, $ch, $fill, $alpha = 255, $stroke = $null) {
  Rect $g ($x + $cx*$cell) ($y + $cy*$cell) ($cw*$cell) ($ch*$cell) $fill $stroke 1 $alpha
}

function Enter($g, $x, $y, $w, $h) {
  Rect $g $x $y $w $h $Green $Green 2
  Text $g 'ENTER' $FSmall $Black $x ($y + 11) $w 24 $FmtCenter
}

$bmp = New-Object System.Drawing.Bitmap($W, $H)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$g.Clear([System.Drawing.Color]::White)

Text $g '关卡元素尺标：体量 × 难度 × 敌人配置' $FTitle $Black 64 38 1100 54
$p = PenObj $Magenta 3
$g.DrawLine($p, 56, 104, 1544, 104)
$p.Dispose()

Text $g '1. 先用矩阵给段落定量' $FHead $Black 70 125 430 30
$mx = 70; $my = 170; $cw = 148; $rh = 74
$headers = @('体量 / 难度','简单','中等','困难')
$fills = @([System.Drawing.Color]::FromArgb(238,238,238),$Green,$Yellow,$Orange)
for ($c=0; $c -lt 4; $c++) {
  Rect $g ($mx + $c*$cw) $my $cw $rh $fills[$c] $Black 2
  Text $g $headers[$c] $FBody $Black ($mx + $c*$cw) ($my + 22) $cw 28 $FmtCenter
}
$rows = @("小型`n5房·24格/8间","中型`n7房·30格/10间","大型`n9房·36格/12间")
$vals = @(
  @("2m`n死亡 0-5%","3m`n死亡 10%","4m`n死亡 30%"),
  @("4m`n死亡 0-10%","5m`n死亡 15-20%","6m`n死亡 30%"),
  @("6m`n死亡 10%","7m`n死亡 20-30%","8m`n死亡 40%")
)
for ($r=0; $r -lt 3; $r++) {
  Rect $g $mx ($my + ($r+1)*$rh) $cw $rh ([System.Drawing.Color]::FromArgb(246,246,246)) $Black 2
  Text $g $rows[$r] $FSmall $Black $mx ($my + ($r+1)*$rh + 11) $cw 52 $FmtCenter
  for ($c=1; $c -lt 4; $c++) {
    Rect $g ($mx + $c*$cw) ($my + ($r+1)*$rh) $cw $rh ([System.Drawing.Color]::White) $Black 2
    Text $g $vals[$r][$c-1] $FTiny $Black ($mx + $c*$cw) ($my + ($r+1)*$rh + 17) $cw 42 $FmtCenter
  }
}

Text $g '2. 敌人类型也要有图标语言' $FHead $Black 70 492 520 30
$ey = 535; $ecw = 148
$enemyNames = @('普通敌人','精英敌人','BOSS 敌人','敌方小队')
for ($c=0; $c -lt 4; $c++) {
  Rect $g (70 + $c*$ecw) $ey $ecw 58 ([System.Drawing.Color]::White) $Black 2
  Text $g $enemyNames[$c] $FSmall $Black (70 + $c*$ecw) ($ey + 18) $ecw 24 $FmtCenter
  Rect $g (70 + $c*$ecw) ($ey + 58) $ecw 90 ([System.Drawing.Color]::White) $Black 2
}
EnemyIcon $g 144 ($ey+105) 'normal'
EnemyIcon $g 292 ($ey+105) 'elite'
EnemyIcon $g 440 ($ey+105) 'boss'
EnemyIcon $g 588 ($ey+105) 'squad'
Text $g '3. 必填字段检查表' $FHead $Black 70 718 360 30
Rect $g 70 755 592 82 ([System.Drawing.Color]::White) $Black 2
Text $g '体量：房间数/格数/路线数    难度：预计时长/死亡率/失败代价' $FSmall $Black 88 770 555 22
Text $g '元素：入口/出口/门宽/通道宽/敌人数量/半径/资源距离/视线暴露' $FSmall $Black 88 794 555 22
Text $g '回写：参考交战时间、实测死亡点、绕路点、奖励是否诱导成功' $FSmall $Black 88 818 555 22

Line $g 705 128 705 790 $Grid 2
Text $g '4. 房间范例：同一尺标如何改变难度' $FHead $Black 735 125 760 30

$rx = 770

Text $g 'A 小型简单：单一目标 + 安全回收' $FBody $Black 760 168 640 28
$cellA = 30; $ay = 198
GridRoom $g $rx $ay 10 5 $cellA
CellRect $g $rx $ay $cellA 0 2 10 1 $Floor 255 $null
CellRect $g $rx $ay $cellA 6 1 2 1 $Floor 255 $null
Enter $g ($rx - 80) ($ay + 2*$cellA) 80 $cellA
GoalIcon $g ($rx + 9.5*$cellA) ($ay + 2.5*$cellA)
DoorIcon $g ($rx + 8.5*$cellA) ($ay + 2.5*$cellA)
Circle $g ($rx + 5*$cellA) ($ay + 2.5*$cellA) (1.5*$cellA) $Red 32
EnemyIcon $g ($rx + 5*$cellA) ($ay + 2.5*$cellA) 'normal'
StarIcon $g ($rx + 6.8*$cellA) ($ay + 1.5*$cellA)
Arrow $g ($rx + 0.6*$cellA) ($ay + 2.5*$cellA) ($rx + 3.8*$cellA) ($ay + 2.5*$cellA) $Green 3
Text $g "变量：1 房间 / 1 敌人 / 半径 1.5 格`n资源在安全边缘；失败后立即重试" $FTiny $Black 1100 200 320 54

Text $g 'B 中型中等：分岔选择 + 奖励诱导风险' $FBody $Black 760 382 650 28
$cellB = 28; $by = 414
GridRoom $g $rx $by 12 6 $cellB
CellRect $g $rx $by $cellB 0 2 12 1 $Floor 255 $null
CellRect $g $rx $by $cellB 3 1 6 1 $Floor 255 $null
CellRect $g $rx $by $cellB 3 4 7 1 $Floor 255 $null
CellRect $g $rx $by $cellB 3 2 1 3 $Floor 255 $null
CellRect $g $rx $by $cellB 9 2 1 3 $Floor 255 $null
Enter $g ($rx - 80) ($by + 2*$cellB) 80 $cellB
DoorIcon $g ($rx + 11.5*$cellB) ($by + 2.5*$cellB)
GoalIcon $g ($rx + 11.5*$cellB) ($by + 0.8*$cellB)
Circle $g ($rx + 4.2*$cellB) ($by + 1.5*$cellB) (1.8*$cellB) $Red 30
Circle $g ($rx + 7.3*$cellB) ($by + 2.5*$cellB) (2.0*$cellB) $Purple 32
Circle $g ($rx + 5.0*$cellB) ($by + 4.4*$cellB) (1.6*$cellB) $Red 26
EnemyIcon $g ($rx + 4.2*$cellB) ($by + 1.5*$cellB) 'normal'
EnemyIcon $g ($rx + 7.3*$cellB) ($by + 2.5*$cellB) 'elite'
EnemyIcon $g ($rx + 5.0*$cellB) ($by + 4.4*$cellB) 'normal'
StarIcon $g ($rx + 10.0*$cellB) ($by + 4.5*$cellB)
Arrow $g ($rx + 3.2*$cellB) ($by + 5.45*$cellB) ($rx + 10.0*$cellB) ($by + 5.45*$cellB) $Yellow 3 $true
Text $g "变量：3 路线 / 3 敌人 / 精英 1`n奖励距 4 格；拿奖励会穿过重叠半径" $FTiny $Black 1130 424 310 62

Text $g 'C 大型困难：窄口承压 + 长回收路线' $FBody $Black 760 622 650 28
$cellC = 28; $cy = 652
GridRoom $g $rx $cy 14 5 $cellC
CellRect $g $rx $cy $cellC 0 2 14 1 $Floor 255 $null
CellRect $g $rx $cy $cellC 1 1 4 1 $Floor 255 $null
CellRect $g $rx $cy $cellC 8 1 4 1 $Floor 255 $null
CellRect $g $rx $cy $cellC 8 3 4 1 $Floor 255 $null
CellRect $g $rx $cy $cellC 5 0 1 5 $Wall 230 $null
CellRect $g $rx $cy $cellC 9 2 1 3 $Wall 230 $null
Enter $g ($rx - 80) ($cy + 2*$cellC) 80 $cellC
GoalIcon $g ($rx + 13.5*$cellC) ($cy + 2.5*$cellC)
Circle $g ($rx + 4.2*$cellC) ($cy + 2.5*$cellC) (2.0*$cellC) $Purple 32
Circle $g ($rx + 8.3*$cellC) ($cy + 2.3*$cellC) (2.7*$cellC) $Red 34
Circle $g ($rx + 11.8*$cellC) ($cy + 3.5*$cellC) (1.6*$cellC) $Red 26
EnemyIcon $g ($rx + 4.2*$cellC) ($cy + 2.5*$cellC) 'elite'
EnemyIcon $g ($rx + 8.3*$cellC) ($cy + 2.3*$cellC) 'boss'
EnemyIcon $g ($rx + 11.8*$cellC) ($cy + 3.5*$cellC) 'normal'
StarIcon $g ($rx + 12.4*$cellC) ($cy + 1.2*$cellC)
Arrow $g ($rx + 0.5*$cellC) ($cy + 5.3*$cellC) ($rx + 13.3*$cellC) ($cy + 5.3*$cellC) $Purple 3 $true
Text $g "变量：窄口 1 格 / Boss 半径 / 回收 10 格`n难点来自范围重叠和重试成本" $FTiny $Black 1165 664 300 62

Rect $g 760 828 710 44 ([System.Drawing.Color]::FromArgb(255,246,210)) $Yellow 2
Text $g '审图规则：右侧小图必须说清“体量、路线、敌人范围、资源距离、视线暴露”哪个变量变了。' $FSmall $Black 780 840 670 24

$bmp.Save($OutPath, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()
foreach ($img in $script:IconCache.Values) { $img.Dispose() }
Write-Host "Regenerated convincing level element metrics: $OutPath"

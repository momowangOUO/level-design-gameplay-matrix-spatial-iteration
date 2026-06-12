$ErrorActionPreference = 'Stop'
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()
Add-Type -AssemblyName System.Drawing

$Root = 'C:\Users\liyian.andy\Desktop\搜打撤'
$OutPath = Join-Path $Root 'assets\generated-level-design\precise-character-ability-metrics-grid.png'
$IconDir = Join-Path $Root 'assets\generated-level-design\image2-icons'
$script:IconCache = @{}

$W = 1600
$H = 900
$Cell = 68
$GridX = 470
$GridY = 150
$Cols = 13
$Rows = 7

$Black = [System.Drawing.Color]::FromArgb(22,24,28)
$Grid = [System.Drawing.Color]::FromArgb(195,202,212)
$Magenta = [System.Drawing.Color]::FromArgb(183,28,106)
$Blue = [System.Drawing.Color]::FromArgb(22,118,224)
$Sky = [System.Drawing.Color]::FromArgb(18,174,232)
$Gray = [System.Drawing.Color]::FromArgb(190,190,190)
$Orange = [System.Drawing.Color]::FromArgb(244,177,131)
$Green = [System.Drawing.Color]::FromArgb(106,176,73)
$Red = [System.Drawing.Color]::FromArgb(227,49,49)

function Font($size, $style = 'Regular') {
  New-Object System.Drawing.Font('Microsoft YaHei', $size, [System.Drawing.FontStyle]::$style, [System.Drawing.GraphicsUnit]::Pixel)
}

$FTitle = Font 38 'Bold'
$FHead = Font 23 'Bold'
$FBody = Font 18 'Regular'
$FSmall = Font 15 'Regular'
$FTiny = Font 13 'Regular'

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

function DrawText($g, $text, $font, $color, $x, $y, $w, $h, $fmt = $FmtLeft) {
  $b = Brush $color
  $g.DrawString($text, $font, $b, [System.Drawing.RectangleF]::new($x, $y, $w, $h), $fmt)
  $b.Dispose()
}

function FillRect($g, $x, $y, $w, $h, $color, $alpha = 255) {
  $b = Brush $color $alpha
  $g.FillRectangle($b, $x, $y, $w, $h)
  $b.Dispose()
}

function StrokeRect($g, $x, $y, $w, $h, $color = $Black, $width = 2) {
  $p = PenObj $color $width
  $g.DrawRectangle($p, $x, $y, $w, $h)
  $p.Dispose()
}

function Get-Icon($name) {
  if ($script:IconCache.ContainsKey($name)) { return $script:IconCache[$name] }
  $path = Join-Path $IconDir ($name + '.png')
  if (-not (Test-Path -LiteralPath $path)) { return $null }
  $img = [System.Drawing.Image]::FromFile($path)
  $script:IconCache[$name] = $img
  return $img
}

function DrawIcon($g, $name, $x, $y, $size, $alpha = 255) {
  $img = Get-Icon $name
  if ($null -eq $img) { return }
  $cm = New-Object System.Drawing.Imaging.ColorMatrix
  $cm.Matrix33 = $alpha / 255.0
  $ia = New-Object System.Drawing.Imaging.ImageAttributes
  $ia.SetColorMatrix($cm)
  $dst = [System.Drawing.Rectangle]::new([int]$x, [int]$y, [int]$size, [int]$size)
  $g.DrawImage($img, $dst, 0, 0, $img.Width, $img.Height, [System.Drawing.GraphicsUnit]::Pixel, $ia)
  $ia.Dispose()
}

function CellRect($g, $cx, $cy, $cw, $ch, $color, $alpha = 255, $stroke = $null, $strokeWidth = 2) {
  $x = $GridX + $cx * $Cell
  $y = $GridY + $cy * $Cell
  FillRect $g $x $y ($cw * $Cell) ($ch * $Cell) $color $alpha
  if ($stroke) { StrokeRect $g $x $y ($cw * $Cell) ($ch * $Cell) $stroke $strokeWidth }
}

function Arrow($g, $x1, $y1, $x2, $y2, $color, $width = 5) {
  $p = PenObj $color $width
  $cap = New-Object System.Drawing.Drawing2D.AdjustableArrowCap(9, 9)
  $p.CustomEndCap = $cap
  $g.DrawLine($p, $x1, $y1, $x2, $y2)
  $p.Dispose(); $cap.Dispose()
}

function Circle($g, $cx, $cy, $r, $color, $alpha = 70) {
  $b = Brush $color $alpha
  $g.FillEllipse($b, $cx - $r, $cy - $r, $r * 2, $r * 2)
  $b.Dispose()
}

function Dot($g, $cx, $cy, $r, $color) {
  $b = Brush $color
  $g.FillEllipse($b, $cx - $r, $cy - $r, $r * 2, $r * 2)
  $b.Dispose()
}

$bmp = New-Object System.Drawing.Bitmap($W, $H)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$g.Clear([System.Drawing.Color]::White)

DrawText $g '角色能力尺标：身体、跳跃、速度、技能半径' $FTitle $Black 64 40 1100 54
$p = PenObj $Magenta 3
$g.DrawLine($p, 56, 104, 1544, 104)
$p.Dispose()

DrawText $g '图例' $FHead $Black 72 150 200 32
FillRect $g 76 210 68 68 $Sky
StrokeRect $g 76 210 68 68 $Black 2
DrawIcon $g 'player' 78 212 64
DrawText $g "主角`n1×1 碰撞盒" $FBody $Black 170 218 210 56

FillRect $g 76 318 68 (68 * 3) $Gray 200
StrokeRect $g 76 318 68 (68 * 3) $Black 2
for ($i=1; $i -lt 3; $i++) {
  $pp = PenObj $Black 1
  $g.DrawLine($pp, 76, 318 + $i * 68, 144, 318 + $i * 68)
  $pp.Dispose()
}
DrawIcon $g 'ability_vertical_jump' 68 372 84
DrawText $g "纵向可达`n向上 3 格" $FBody $Black 170 374 210 58

for ($i=0; $i -lt 3; $i++) {
  FillRect $g (76 + $i * 52) 560 52 52 $Orange 235
  StrokeRect $g (76 + $i * 52) 560 52 52 $Black 1
}
DrawIcon $g 'ability_horizontal_jump' 82 532 104
DrawText $g "稳定横跳`n3 格" $FBody $Black 250 562 160 56

FillRect $g 76 666 68 68 ([System.Drawing.Color]::White)
StrokeRect $g 76 666 68 68 $Orange 4
DrawIcon $g 'ability_risk_landing' 78 668 64
DrawText $g "第 4 格`n风险落点" $FBody $Black 170 674 210 56

Arrow $g 76 800 215 800 $Blue 6
DrawIcon $g 'ability_speed' 74 752 88
DrawText $g "移动速度`n4 格/秒" $FBody $Black 245 780 160 56

for ($c=0; $c -le $Cols; $c++) {
  $x = $GridX + $c * $Cell
  $pen = if ($c -eq 0 -or $c -eq $Cols) { PenObj $Black 3 } else { PenObj $Grid 1 }
  $g.DrawLine($pen, $x, $GridY, $x, $GridY + $Rows * $Cell)
  $pen.Dispose()
  if ($c -lt $Cols) { DrawText $g ([string]($c + 1)) $FBody $Black ($x + 8) ($GridY - 34) ($Cell - 16) 26 $FmtCenter }
}
for ($r=0; $r -le $Rows; $r++) {
  $y = $GridY + $r * $Cell
  $pen = if ($r -eq 0 -or $r -eq $Rows) { PenObj $Black 3 } else { PenObj $Grid 1 }
  $g.DrawLine($pen, $GridX, $y, $GridX + $Cols * $Cell, $y)
  $pen.Dispose()
  if ($r -lt $Rows) { DrawText $g ([string]($Rows - $r)) $FBody $Black ($GridX - 45) ($y + 20) 34 28 $FmtCenter }
}

CellRect $g 0 6 1 1 $Sky 255 $Black 2
CellRect $g 0 3 1 3 $Gray 205 $null
for ($i=0; $i -lt 3; $i++) {
  CellRect $g (1 + $i) 6 1 1 $Orange 235 $Black 1
}
CellRect $g 4 6 1 1 ([System.Drawing.Color]::White) 255 $Orange 4
DrawIcon $g 'player' ($GridX + 0.08*$Cell) ($GridY + 6.08*$Cell) (0.84*$Cell)
DrawIcon $g 'ability_vertical_jump' ($GridX - 0.08*$Cell) ($GridY + 3.28*$Cell) (1.16*$Cell) 230
DrawIcon $g 'ability_horizontal_jump' ($GridX + 1.05*$Cell) ($GridY + 5.72*$Cell) (1.75*$Cell) 230
DrawIcon $g 'ability_risk_landing' ($GridX + 4.08*$Cell) ($GridY + 6.08*$Cell) (0.84*$Cell) 245
Arrow $g ($GridX + 0.5*$Cell) ($GridY + 6.55*$Cell) ($GridX + 4.5*$Cell) ($GridY + 6.55*$Cell) $Orange 4

$greenCx = $GridX + 11 * $Cell
$greenCy = $GridY + 2 * $Cell
Circle $g $greenCx $greenCy (2 * $Cell) $Green 60
Dot $g $greenCx $greenCy 16 $Green
DrawIcon $g 'ability_interaction_radius' ($greenCx - 46) ($greenCy - 46) 92
DrawText $g "交互/治疗：`n半径 2 格" $FHead $Green ($GridX + 10.2*$Cell) ($GridY + 2.15*$Cell) 320 62 $FmtCenter

$redCx = $GridX + 11 * $Cell
$redCy = $GridY + 5 * $Cell
Circle $g $redCx $redCy (3 * $Cell) $Red 48
Dot $g $redCx $redCy 16 $Red
DrawIcon $g 'ability_damage_radius' ($redCx - 50) ($redCy - 50) 100
DrawText $g "爆炸/伤害：`n半径 3 格" $FHead $Red ($GridX + 10.2*$Cell) ($GridY + 5.15*$Cell) 320 62 $FmtCenter

$speedY = $GridY + $Rows * $Cell + 42
Arrow $g $GridX $speedY ($GridX + 4*$Cell) $speedY $Blue 6
DrawIcon $g 'ability_movement_path' ($GridX + 1.1*$Cell) ($speedY - 58) 88
DrawText $g '移动速度：4 格/秒' $FHead $Blue ($GridX + 1.1*$Cell) ($speedY + 14) 320 34 $FmtCenter
DrawText $g '贴格检查：身体、纵跳、横跳、风险落点均占整格；技能半径中心落在格点，半径为整格数。' $FSmall $Black $GridX 820 840 32 $FmtCenter

$bmp.Save($OutPath, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()
foreach ($img in $script:IconCache.Values) { $img.Dispose() }
Write-Host "Regenerated grid-aligned icon metrics: $OutPath"

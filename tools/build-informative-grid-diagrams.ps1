$ErrorActionPreference = 'Stop'
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()
Add-Type -AssemblyName System.Drawing
Remove-Item Alias:R -ErrorAction SilentlyContinue
Remove-Item Alias:P -ErrorAction SilentlyContinue

$Root = 'C:\Users\liyian.andy\Desktop\搜打撤'
$AssetDir = Join-Path $Root 'assets\generated-level-design'
$BaseDir = Join-Path $AssetDir 'image2-bases'
$IconDir = Join-Path $AssetDir 'image2-icons'
$ReportPath = Join-Path $AssetDir 'grid-alignment-report.csv'
$ViolationPath = Join-Path $AssetDir 'grid-alignment-violations.csv'

$W = 1600
$H = 900
$GridSize = 40
$OX = 80
$OY = 160
$Cols = 36
$Rows = 17

$Black = [System.Drawing.Color]::FromArgb(22, 24, 28)
$Grid = [System.Drawing.Color]::FromArgb(225, 229, 235)
$MajorGrid = [System.Drawing.Color]::FromArgb(198, 205, 214)
$Blue = [System.Drawing.Color]::FromArgb(31, 136, 229)
$Green = [System.Drawing.Color]::FromArgb(89, 171, 95)
$Orange = [System.Drawing.Color]::FromArgb(238, 126, 36)
$Yellow = [System.Drawing.Color]::FromArgb(255, 207, 74)
$Red = [System.Drawing.Color]::FromArgb(218, 64, 64)
$Purple = [System.Drawing.Color]::FromArgb(126, 95, 190)
$Gray = [System.Drawing.Color]::FromArgb(126, 134, 146)
$Wall = [System.Drawing.Color]::FromArgb(32, 35, 40)
$PaleBlue = [System.Drawing.Color]::FromArgb(226, 239, 255)
$PaleGreen = [System.Drawing.Color]::FromArgb(226, 244, 224)
$PaleOrange = [System.Drawing.Color]::FromArgb(255, 235, 217)
$PalePurple = [System.Drawing.Color]::FromArgb(237, 232, 248)
$PaleYellow = [System.Drawing.Color]::FromArgb(255, 246, 210)

function Font($size, $style = 'Regular') {
  New-Object System.Drawing.Font('Microsoft YaHei', $size, [System.Drawing.FontStyle]::$style, [System.Drawing.GraphicsUnit]::Pixel)
}

$FTitle = Font 34 'Bold'
$FSub = Font 22 'Bold'
$FBody = Font 18 'Regular'
$FSmall = Font 15 'Regular'
$FTiny = Font 13 'Regular'
$FBoldSmall = Font 15 'Bold'

$FmtCenter = New-Object System.Drawing.StringFormat
$FmtCenter.Alignment = [System.Drawing.StringAlignment]::Center
$FmtCenter.LineAlignment = [System.Drawing.StringAlignment]::Center
$FmtLeft = New-Object System.Drawing.StringFormat
$FmtLeft.Alignment = [System.Drawing.StringAlignment]::Near
$FmtLeft.LineAlignment = [System.Drawing.StringAlignment]::Near
$FmtTopCenter = New-Object System.Drawing.StringFormat
$FmtTopCenter.Alignment = [System.Drawing.StringAlignment]::Center
$FmtTopCenter.LineAlignment = [System.Drawing.StringAlignment]::Near

$script:Current = ''
$script:Reports = @()
$script:ViolationList = @()
$script:IconCache = @{}

function Brush($color, $alpha = 255) {
  New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb($alpha, $color))
}

function PenObj($color, $width = 2, $alpha = 255) {
  New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb($alpha, $color), $width)
}

function Is-Snapped($value, $step = 20) {
  $rounded = [int][Math]::Round($value)
  return (($rounded % $step) -eq 0)
}

function Register-Primitive($kind, [double[]]$values, $step = 20) {
  if (-not $script:ReportsByName.ContainsKey($script:Current)) {
    $script:ReportsByName[$script:Current] = [pscustomobject]@{
      Diagram = $script:Current
      CheckedPrimitives = 0
      Violations = 0
    }
  }
  $script:ReportsByName[$script:Current].CheckedPrimitives = $script:ReportsByName[$script:Current].CheckedPrimitives + 1
  foreach ($v in $values) {
    if (-not (Is-Snapped $v $step)) {
      $script:ReportsByName[$script:Current].Violations = $script:ReportsByName[$script:Current].Violations + 1
      $script:ViolationList += [pscustomobject]@{ Diagram = $script:Current; Kind = $kind; Value = $v; Step = $step }
    }
  }
}

$script:ReportsByName = @{}

function R($x, $y, $w, $h) {
  $rx = $OX + ($x * $GridSize)
  $ry = $OY + ($y * $GridSize)
  $rw = $w * $GridSize
  $rh = $h * $GridSize
  $null = Register-Primitive 'grid-rect' @($rx, $ry, $rw, $rh) 40
  return [System.Drawing.RectangleF]::new($rx, $ry, $rw, $rh)
}

function P($x, $y) {
  $px = $OX + ($x * $GridSize)
  $py = $OY + ($y * $GridSize)
  $null = Register-Primitive 'grid-point' @($px, $py) 20
  return [System.Drawing.PointF]::new($px, $py)
}

function Draw-Text($g, $text, $font, $color, $x, $y, $w, $h, $fmt = $FmtLeft) {
  $b = Brush $color
  $g.DrawString($text, $font, $b, [System.Drawing.RectangleF]::new($x, $y, $w, $h), $fmt)
  $b.Dispose()
}

function Draw-Title($g, $title) {
  Draw-Text $g $title $FTitle $Black 64 38 1100 48
  $p = PenObj ([System.Drawing.Color]::FromArgb(183, 28, 106)) 3
  $g.DrawLine($p, 64, 104, 1536, 104)
  $p.Dispose()
}

function Draw-Background($g, $stem) {
  $base = Join-Path $BaseDir ($stem + '-image2-base.png')
  if (Test-Path -LiteralPath $base) {
    $img = [System.Drawing.Image]::FromFile($base)
    $cm = New-Object System.Drawing.Imaging.ColorMatrix
    $cm.Matrix33 = 0.12
    $ia = New-Object System.Drawing.Imaging.ImageAttributes
    $ia.SetColorMatrix($cm)
    $dest = [System.Drawing.Rectangle]::new(0, 0, $W, $H)
    $g.DrawImage($img, $dest, 0, 0, $img.Width, $img.Height, [System.Drawing.GraphicsUnit]::Pixel, $ia)
    $ia.Dispose()
    $img.Dispose()
    $b = Brush ([System.Drawing.Color]::White) 228
    $g.FillRectangle($b, 0, 0, $W, $H)
    $b.Dispose()
  }
}

function Draw-Grid($g) {
  $p = PenObj $Grid 1
  $pm = PenObj $MajorGrid 1
  for ($i = 0; $i -le $Cols; $i++) {
    $x = $OX + $i * $GridSize
    $pen = if (($i % 4) -eq 0) { $pm } else { $p }
    $g.DrawLine($pen, $x, $OY, $x, $OY + $Rows * $GridSize)
  }
  for ($j = 0; $j -le $Rows; $j++) {
    $y = $OY + $j * $GridSize
    $pen = if (($j % 4) -eq 0) { $pm } else { $p }
    $g.DrawLine($pen, $OX, $y, $OX + $Cols * $GridSize, $y)
  }
  $p.Dispose(); $pm.Dispose()
}

function Fill-R($g, $rect, $color, $alpha = 255) {
  Register-Primitive 'fill-rect' @($rect.X, $rect.Y, $rect.Width, $rect.Height) 20
  $b = Brush $color $alpha
  $g.FillRectangle($b, $rect)
  $b.Dispose()
}

function Stroke-R($g, $rect, $color = $Black, $width = 3, $alpha = 255) {
  Register-Primitive 'stroke-rect' @($rect.X, $rect.Y, $rect.Width, $rect.Height) 20
  $p = PenObj $color $width $alpha
  $g.DrawRectangle($p, $rect.X, $rect.Y, $rect.Width, $rect.Height)
  $p.Dispose()
}

function Box($g, $x, $y, $w, $h, $label, $fill, $stroke = $Black) {
  $rect = R $x $y $w $h
  Fill-R $g $rect $fill 238
  Stroke-R $g $rect $stroke 3
  Draw-Text $g $label $FBoldSmall $Black $rect.X ($rect.Y + 8) $rect.Width ($rect.Height - 8) $FmtCenter
}

function SmallLabel($g, $x, $y, $text, $color = $Black) {
  $pt = P $x $y
  Draw-Text $g $text $FTiny $color ($pt.X - 80) ($pt.Y - 10) 160 22 $FmtCenter
}

function Arrow($g, $x1, $y1, $x2, $y2, $color = $Orange, $width = 5) {
  $p1 = @(P $x1 $y1)[-1]
  $p2 = @(P $x2 $y2)[-1]
  $pen = PenObj $color $width
  $cap = New-Object System.Drawing.Drawing2D.AdjustableArrowCap(7, 7)
  $pen.CustomEndCap = $cap
  $g.DrawLine($pen, $p1, $p2)
  $pen.Dispose(); $cap.Dispose()
}

function LineG($g, $x1, $y1, $x2, $y2, $color = $Black, $width = 3) {
  $p1 = @(P $x1 $y1)[-1]
  $p2 = @(P $x2 $y2)[-1]
  $pen = PenObj $color $width
  $g.DrawLine($pen, $p1, $p2)
  $pen.Dispose()
}

function Get-Icon($name) {
  if (-not $script:IconCache.ContainsKey($name)) {
    $path = Join-Path $IconDir ($name + '.png')
    $script:IconCache[$name] = [System.Drawing.Image]::FromFile($path)
  }
  return $script:IconCache[$name]
}

function Icon-Name($color, $label) {
  if ($label -match 'P|入|A|玩家') { return 'player' }
  if ($label -match 'G|出|终|目标') { return 'goal' }
  if ($label -match '钥') { return 'key' }
  if ($label -match '锁') { return 'lock' }
  if ($label -match '门') { return 'door' }
  if ($label -match '补|资源') { return 'supply' }
  if ($label -match '奖|金|币') { return 'reward' }
  if ($label -match '关|开') { return 'switch' }
  if ($label -match '看|视') { return 'vision' }
  if ($label -match '死|失败|险|坑') { return 'death' }
  if ($label -match '停|绕') { return 'linger' }
  if ($label -match '敌|近|远|双') { return 'enemy' }
  if ($label -match 'B') { return 'goal' }

  $argb = $color.ToArgb()
  if ($argb -eq $Blue.ToArgb()) { return 'player' }
  if ($argb -eq $Green.ToArgb()) { return 'goal' }
  if ($argb -eq $Yellow.ToArgb()) { return 'reward' }
  if ($argb -eq $Orange.ToArgb()) { return 'switch' }
  if ($argb -eq $Purple.ToArgb()) { return 'linger' }
  if ($argb -eq $Red.ToArgb()) { return 'enemy' }
  return 'switch'
}

function Dot($g, $x, $y, $color, $label = '') {
  $pt = @(P $x $y)[-1]
  $px = [double](@($pt.X)[-1])
  $py = [double](@($pt.Y)[-1])
  Register-Primitive 'dot-center' @($px, $py) 20
  $icon = Get-Icon (Icon-Name $color $label)
  $size = 44
  if ($label -match 'boss|Boss|峰') { $size = 54 }
  if ($label -match '技|尺|险') { $size = 38 }
  $g.DrawImage($icon, [System.Drawing.RectangleF]::new($px - $size / 2, $py - $size / 2, $size, $size))
}

function Legend($g, [array]$items, $x = 28, $y = 15) {
  $rx = $OX + $x * $GridSize
  $ry = $OY + $y * $GridSize
  $w = 8 * $GridSize
  $rawH = [Math]::Max(2, $items.Count + 1) * 28
  $h = [Math]::Ceiling($rawH / 40) * 40
  $rect = [System.Drawing.RectangleF]::new($rx, $ry, $w, $h)
  Fill-R $g $rect ([System.Drawing.Color]::White) 238
  Stroke-R $g $rect $MajorGrid 2
  Draw-Text $g '图例 / 读图顺序' $FBoldSmall $Black ($rx + 12) ($ry + 8) ($w - 24) 24
  for ($i = 0; $i -lt $items.Count; $i++) {
    $item = $items[$i]
    $b = Brush ($item.Color)
    $g.FillRectangle($b, $rx + 14, $ry + 40 + $i * 26, 18, 18)
    $b.Dispose()
    Draw-Text $g ($item.Text) $FTiny $Black ($rx + 40) ($ry + 36 + $i * 26) ($w - 54) 24
  }
}

function CheckCard($g, $x, $y, $title, $body, $fill = $PaleYellow) {
  $rect = R $x $y 7 2
  Fill-R $g $rect $fill 240
  Stroke-R $g $rect $MajorGrid 2
  Draw-Text $g $title $FBoldSmall $Black ($rect.X + 12) ($rect.Y + 8) ($rect.Width - 24) 24
  Draw-Text $g $body $FTiny $Black ($rect.X + 12) ($rect.Y + 36) ($rect.Width - 24) ($rect.Height - 40)
}

function FiveElementStrip($g) {
  $rect = R 1 0 34 1
  Fill-R $g $rect ([System.Drawing.Color]::White) 242
  Stroke-R $g $rect $MajorGrid 1
  $labels = @('核心技能', '玩家动作', '障碍/敌人', '奖励/资源', '教学状态/情绪')
  $cuts = @(1, 8, 15, 22, 29, 35)
  for ($i = 1; $i -lt ($cuts.Count - 1); $i++) {
    LineG $g $cuts[$i] 0 $cuts[$i] 1 $MajorGrid 1
  }
  for ($i = 0; $i -lt $labels.Count; $i++) {
    $left = $OX + ($cuts[$i] * $GridSize)
    $right = $OX + ($cuts[$i + 1] * $GridSize)
    Draw-Text $g $labels[$i] $FTiny $Black $left ($rect.Y + 10) ($right - $left) 22 $FmtCenter
  }
}

function Save-Diagram($stem, $title, [scriptblock]$draw) {
  $script:Current = $stem
  $path = Join-Path $AssetDir ($stem + '.png')
  $bmp = New-Object System.Drawing.Bitmap($W, $H)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
  $g.Clear([System.Drawing.Color]::White)
  Draw-Background $g $stem
  Draw-Grid $g
  Draw-Title $g $title
  FiveElementStrip $g
  & $draw $g
  Draw-Text $g '几何校验：房间、墙线、路径、障碍、奖励均贴 40px 网格；路线中心线使用半格坐标。' $FTiny $Gray 80 850 980 28
  $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
}

Save-Diagram 'level-design-curriculum-overview' '教材整体结构：从玩法到回写' {
  param($g)
  $steps = @(
    @{x=1;y=2;label="1 概念`n核心动词";fill=$PaleBlue;body='玩家要学什么'},
    @{x=8;y=2;label="2 标尺`nMetrics";fill=$PaleGreen;body='角色与空间单位'},
    @{x=15;y=2;label="3 矩阵`nBeat 表";fill=$PaleYellow;body='技能/动作/障碍/奖励'},
    @{x=22;y=2;label="4 灰盒`nBlockout";fill=$PaleOrange;body='入口/路线/出口'},
    @{x=29;y=2;label="5 测试`n回写";fill=$PalePurple;body='数据/访谈/修正'}
  )
  foreach ($s in $steps) { Box $g ($s.x) ($s.y) 5 3 ($s.label) ($s.fill); Draw-Text $g ($s.body) $FTiny $Black (($OX+(($s.x)*$GridSize))+8) (($OY+(($s.y)*$GridSize))+92) 185 28 $FmtCenter }
  Arrow $g 6 3.5 8 3.5; Arrow $g 13 3.5 15 3.5; Arrow $g 20 3.5 22 3.5; Arrow $g 27 3.5 29 3.5
  CheckCard $g 2 9 '新手读法' '每一步都产出可检查工件：一句话目标、标尺表、教学矩阵、灰盒图、测试回写。' $PaleBlue
  CheckCard $g 11 9 '设计检查' '如果图纸和矩阵说不清同一件事，先改矩阵，再改空间。' $PaleGreen
  CheckCard $g 20 9 '迭代检查' '玩家失败时问：没看懂、不会做、还是尺寸太难？' $PaleOrange
}

Save-Diagram 'core-gameplay-loop-diagram' '玩法核心循环：场景里的五步' {
  param($g)
  Box $g 5 3 5 2 '观察目标' $PaleBlue
  Box $g 15 2 5 2 '执行动作' $PaleGreen
  Box $g 25 3 5 2 '遭遇阻力' $PaleOrange
  Box $g 22 10 5 2 '获得反馈' $PaleYellow
  Box $g 10 10 5 2 '调整策略' $PalePurple
  Arrow $g 10 4 15 3; Arrow $g 20 3 25 4; Arrow $g 27 5 24 10; Arrow $g 22 11 15 11; Arrow $g 10 10 7 5
  Box $g 12 5 10 4 '小场景：目标在出口，坑洞阻挡，奖励提示正确动作' ([System.Drawing.Color]::FromArgb(245,245,245))
  Fill-R $g (R 13 8 2 1) $Black 235
  Fill-R $g (R 16 8 1 1) $Red 80
  Dot $g 13.5 7.5 $Blue 'P'
  Dot $g 21 6.5 $Green 'G'
  Arrow $g 14 7.5 18 7.5 $Orange 4
  Legend $g @(
    @{Color=$Blue;Text='玩家动作：看、走、跳、试'},
    @{Color=$Red;Text='阻力：坑、墙、敌人、时间'},
    @{Color=$Green;Text='反馈：奖励、开门、路线变化'}
  )
}

Save-Diagram 'obstacle-action-relation' '障碍如何改变玩家动作：六格案例板' {
  param($g)
  function CardBase($x, $y, $title, $note, $fill) {
    $rect = R $x $y 9 5
    Fill-R $g $rect $fill 238
    Stroke-R $g $rect $Black 3
    Draw-Text $g $title $FBoldSmall $Black $rect.X ($rect.Y + 16) $rect.Width 24 $FmtCenter
    Draw-Text $g $note $FTiny $Black ($rect.X + 10) ($rect.Y + 172) ($rect.Width - 20) 24 $FmtCenter
  }

  CardBase 1 1 '坑洞 -> 跳' '动作：起跳；情绪：安全理解' $PaleBlue
  Fill-R $g (R 2 4 2 1) $Wall 235
  Fill-R $g (R 5 4 3 1) $Wall 235
  Dot $g 2.5 3.5 $Blue 'P'
  Dot $g 6.5 3.5 $Green '奖'
  Arrow $g 2.5 3.5 6.5 3.5 $Orange 4
  Draw-Text $g '1 格坑先单独出现' $FTiny $Black ($OX + 1.6*$GridSize) ($OY + 4.05*$GridSize) 300 22 $FmtCenter

  CardBase 13 1 '巡逻 -> 等' '动作：观察节奏；情绪：可预判' $PaleGreen
  Fill-R $g (R 14 4 7 1) $Wall 220
  Dot $g 14.5 3.5 $Blue 'P'
  Dot $g 18.5 3.5 $Red '敌'
  Dot $g 20.5 3.5 $Green '出'
  LineG $g 16.5 3.5 19.5 3.5 $Red 3
  Arrow $g 16.5 3.5 19.5 3.5 $Red 3
  Draw-Text $g '巡逻线清楚，玩家等窗口' $FTiny $Black ($OX + 13.6*$GridSize) ($OY + 4.05*$GridSize) 320 22 $FmtCenter

  CardBase 25 1 '锁门 -> 找钥匙' '动作：先看目标，再回收信息' $PaleYellow
  Fill-R $g (R 26 4 6 1) $Wall 220
  Dot $g 26.5 3.5 $Blue 'P'
  Dot $g 28.5 3.5 $Yellow '钥'
  Fill-R $g (R 31 2 1 2) $Red 170
  Dot $g 32.5 3.5 $Green '出'
  Arrow $g 26.5 3.5 28.5 3.5 $Orange 4
  Arrow $g 28.5 3.5 31.5 3.5 $Orange 4
  Draw-Text $g '门先可见，钥匙位置可推理' $FTiny $Black ($OX + 25.6*$GridSize) ($OY + 4.05*$GridSize) 320 22 $FmtCenter

  CardBase 1 9 '远程 -> 找掩体' '动作：从掩体间推进；情绪：受压' $PaleOrange
  Fill-R $g (R 2 12 2 1) $Wall 235
  Fill-R $g (R 5 11 1 2) $Wall 235
  Dot $g 2.5 11.5 $Blue 'P'
  Dot $g 7.5 11.5 $Red '敌'
  LineG $g 7.5 11.5 2.5 11.5 $Red 2
  Arrow $g 2.5 11.5 5.5 11.5 $Orange 4
  Draw-Text $g '火线可读，掩体露出安全点' $FTiny $Black ($OX + 1.6*$GridSize) ($OY + 12.05*$GridSize) 320 22 $FmtCenter

  CardBase 13 9 '移动平台 -> 抓时机' '动作：等待周期；情绪：专注' $PalePurple
  Fill-R $g (R 14 12 2 1) $Wall 235
  Fill-R $g (R 19 12 2 1) $Wall 235
  Fill-R $g (R 16 11 2 1) $Purple 180
  Dot $g 14.5 11.5 $Blue 'P'
  Dot $g 20.5 11.5 $Green '出'
  LineG $g 16 13 18 13 $Purple 3
  Arrow $g 16 13 18 13 $Purple 3
  Arrow $g 14.5 11.5 20.5 11.5 $Orange 4
  Draw-Text $g '平台周期可读，再要求执行' $FTiny $Black ($OX + 13.6*$GridSize) ($OY + 12.05*$GridSize) 320 22 $FmtCenter

  CardBase 25 9 '遮挡 -> 观察' '动作：探视线；情绪：谨慎' ([System.Drawing.Color]::FromArgb(236,245,245))
  Fill-R $g (R 28 10 1 3) $Wall 235
  Fill-R $g (R 29 13 4 1) $Wall 235
  Dot $g 26.5 12.5 $Blue 'P'
  Dot $g 31.5 10.5 $Green '?'
  LineG $g 26.5 12.5 28.5 11.5 $Purple 3
  LineG $g 29.5 11.5 31.5 10.5 $Purple 3
  Arrow $g 26.5 12.5 29.5 11.5 $Orange 4
  Draw-Text $g '拐角遮挡信息，先观察再进' $FTiny $Black ($OX + 25.6*$GridSize) ($OY + 12.05*$GridSize) 320 22 $FmtCenter
}

Save-Diagram 'pacing-emotion-curve' '节奏与情绪曲线：压力、资源、释放' {
  param($g)
  Box $g 2 11 5 2 "引介`n好奇" $PaleBlue
  Box $g 9 9 5 2 "练习`n专注" $PaleGreen
  Box $g 16 6 5 2 "验证`n紧张" $PaleOrange
  Box $g 23 3 5 2 "峰值`n高压" ([System.Drawing.Color]::FromArgb(255,225,225))
  Box $g 30 10 4 2 "释放`n释然" $PalePurple
  LineG $g 2 13 35 13 $Gray 2
  LineG $g 2 13 2 2 $Gray 2
  Arrow $g 6.5 12 9 10; Arrow $g 13.5 10 16 7; Arrow $g 20.5 7 23 4; Arrow $g 28 4 30 11
  Dot $g 4 12 $Green '补'
  Dot $g 18 7 $Red '险'
  Dot $g 25 4 $Red '峰'
  Dot $g 32 11 $Blue '休'
  CheckCard $g 3 2 '读图方法' '一条关卡不是持续升压，而是“学习 -> 验证 -> 释放”的波形。' $PaleYellow
  CheckCard $g 24 13 '回写指标' '峰值死亡率、释放段停留、补给是否被看见。' $PaleBlue
}

Save-Diagram 'gameplay-matrix-axes' 'Gameplay Matrix：一张已填好的小矩阵' {
  param($g)
  $rows = @('技能','动作','障碍','奖励','情绪','指标')
  $cols = @('B01','B02','B03','B04','B05')
  $vals = @(
    @('移动','短跳','连跳','宽坑','释放'),
    @('跑','跳','控节奏','助跑','整理'),
    @('低台','1格坑','双坑','3格坑','低压'),
    @('金币','落点','金币线','出口','终点'),
    @('好奇','理解','专注','紧张','释然'),
    @('看向率','首过率','重试','死亡','停留')
  )
  for($c=0;$c -lt 6;$c++){ Box $g (2+$c*5) 1 5 1 ($(if($c -eq 0){'维度'}else{$cols[$c-1]})) ([System.Drawing.Color]::FromArgb(240,240,240)) }
  for($r=0;$r -lt 6;$r++){
    Box $g 2 (2+$r*2) 5 2 $rows[$r] $PaleBlue
    for($c=0;$c -lt 5;$c++){ Box $g (7+$c*5) (2+$r*2) 5 2 $vals[$r][$c] ($(if($r -eq 3){$PaleYellow}elseif($r -eq 4){$PalePurple}else{[System.Drawing.Color]::FromArgb(248,248,248)})) }
  }
  Arrow $g 8 15 29 15 $Orange 4
  Draw-Text $g '横向是教学进程；纵向是每格必须回答的问题。' $FSmall $Black 420 778 680 26 $FmtCenter
}

Save-Diagram 'platform-world-1-2-progression' '平台动作进程：1 格坑到 3 格验证跳' {
  param($g)
  foreach($x in 1..34){ Fill-R $g (R $x 13 1 1) $Black 245 }
  Box $g 1 10 5 2 'B01 移动' $PaleBlue
  Fill-R $g (R 8 13 1 1) ([System.Drawing.Color]::White) 255; Stroke-R $g (R 8 13 1 1) $Red 3
  Box $g 7 10 5 2 'B02 1格坑' $PaleGreen
  foreach($x in @(14,16)){ Fill-R $g (R $x 13 1 1) ([System.Drawing.Color]::White) 255; Stroke-R $g (R $x 13 1 1) $Red 3 }
  Box $g 13 10 5 2 'B03 连续短跳' $PaleYellow
  foreach($x in 23..25){ Fill-R $g (R $x 13 1 1) ([System.Drawing.Color]::White) 255; Stroke-R $g (R $x 13 1 1) $Red 3 }
  Box $g 21 10 6 2 'B04 3格验证' $PaleOrange
  Box $g 30 10 4 2 'B05 出口' $PalePurple
  foreach($x in @(4,8,14,16,23,24,25,32)){ Dot $g $x 9 $Yellow '' }
  Dot $g 2 12 $Blue 'P'; Dot $g 34 12 $Green 'G'
  Arrow $g 2 12 34 12 $Orange 4
  Legend $g @(
    @{Color=$Red;Text='红框：坑宽按格记录'},
    @{Color=$Yellow;Text='金币线：引导正确动作'},
    @{Color=$Purple;Text='释放：峰值后降压'}
  )
}

Save-Diagram 'platform-world-1-2-blockout' '平台动作 Blockout：矩阵落到侧视空间' {
  param($g)
  foreach($x in 1..35){ Fill-R $g (R $x 14 1 1) $Black 245 }
  foreach($x in 9,15,16,24,25,26){ Fill-R $g (R $x 14 1 1) ([System.Drawing.Color]::White) 255; Stroke-R $g (R $x 14 1 1) $Red 3 }
  Fill-R $g (R 18 12 3 2) $Black 245
  Fill-R $g (R 29 11 4 3) $Black 245
  Dot $g 2 13 $Blue 'P'; Dot $g 34 13 $Green '出'
  Arrow $g 2 13 8 13; Arrow $g 10 13 14 13; Arrow $g 17 13 23 13; Arrow $g 27 13 33 13
  $beats=@(@{x=2;t="B01`n移动"},@{x=8;t="B02`n短跳"},@{x=14;t="B03`n连跳"},@{x=23;t="B04`n验证"},@{x=31;t="B05`n释放"})
  foreach($b in $beats){ Box $g ($b.x) 2 4 2 ($b.t) $PaleBlue }
  CheckCard $g 2 6 '落图规则' '每个 beat 必须能指到一个空间段：入口、障碍、奖励、出口都要可见。' $PaleYellow
  CheckCard $g 22 6 '失败回收' '宽坑前后留站立格；失败后能快速重试。' $PaleGreen
}

Save-Diagram 'portal-fling-tutorial-arc' '解谜教学弧线：观察、操作、反馈、迁移' {
  param($g)
  $steps=@(
    @{x=1;t="B01`n看见出口";c=$PaleBlue},
    @{x=8;t="B02`n按下开关";c=$PaleGreen},
    @{x=15;t="B03`n看到反馈";c=$PaleYellow},
    @{x=22;t="B04`n规则迁移";c=$PaleOrange},
    @{x=29;t="B05`n到达出口";c=$PalePurple}
  )
  foreach($s in $steps){ Box $g ($s.x) 4 5 5 ($s.t) ($s.c); Dot $g (($s.x)+1) 7 $Blue 'P'; Dot $g (($s.x)+3.5) 5.5 $Green '出'; Dot $g (($s.x)+2.5) 7 $Orange '关' }
  Arrow $g 6 6.5 8 6.5; Arrow $g 13 6.5 15 6.5; Arrow $g 20 6.5 22 6.5; Arrow $g 27 6.5 29 6.5
  CheckCard $g 3 12 '关键检查' '出口先可见；开关反馈必须在同一视线或可快速回看。' $PaleYellow
  CheckCard $g 21 12 '迁移检查' '同规则换空间，不要同时引入新规则。' $PaleGreen
}

Save-Diagram 'portal-fling-room-blockout' '解谜房间 Blockout：视线与反馈' {
  param($g)
  Box $g 4 3 24 11 '房间边界' ([System.Drawing.Color]::FromArgb(250,250,250))
  Fill-R $g (R 15 3 1 7) $Black 220
  Fill-R $g (R 22 7 1 7) $Black 220
  Dot $g 6 12 $Blue '入'
  Dot $g 26 4 $Green '出'
  Dot $g 10 8 $Orange '关'
  Dot $g 22 6 $Red '门'
  Arrow $g 6 12 10 8 $Orange 4
  LineG $g 10 8 22 6 $Purple 3
  Arrow $g 10 8 24 5 $Green 4
  CheckCard $g 3 1 '读图重点' '玩家先看见出口，再看到开关改变门。紫线表示反馈视线。' $PalePurple
  Legend $g @(
    @{Color=$Blue;Text='入口/玩家'},
    @{Color=$Orange;Text='可操作机关'},
    @{Color=$Red;Text='门/阻断'},
    @{Color=$Green;Text='出口/成功路线'}
  )
}

Save-Diagram 'doom-arena-encounter-layout' '射击遭遇布局：可读的高压 Arena' {
  param($g)
  Box $g 5 3 24 11 'Arena 灰盒' ([System.Drawing.Color]::FromArgb(250,250,250))
  Fill-R $g (R 10 7 3 2) $Gray 210
  Fill-R $g (R 20 6 3 2) $Gray 210
  Fill-R $g (R 16 11 4 1) $Gray 210
  Dot $g 6 12 $Blue '入'; Dot $g 28 4 $Green '出'
  Dot $g 14 8 $Red '近'; Dot $g 24 5 $Red '远'; Dot $g 18 12 $Yellow '补'
  Arrow $g 7 12 12 8 $Orange 4; Arrow $g 12 8 22 6 $Orange 4; Arrow $g 22 6 18 12 $Orange 4; Arrow $g 18 12 28 4 $Orange 4
  CheckCard $g 2 1 '遭遇顺序' '入口读场 -> 移动射击 -> 处理高威胁 -> 冒险补给 -> 出口释放。' $PaleYellow
  Legend $g @(
    @{Color=$Gray;Text='掩体/绕圈结构'},
    @{Color=$Red;Text='近战/远程威胁'},
    @{Color=$Yellow;Text='补给引导冒险'},
    @{Color=$Green;Text='出口方向'}
  )
}

Save-Diagram 'coop-role-responsibility-matrix' '合作关卡：角色责任与同步点' {
  param($g)
  Box $g 5 3 10 10 '玩家 A 路线' $PaleBlue
  Box $g 20 3 10 10 '玩家 B 路线' $PaleGreen
  Fill-R $g (R 15 7 5 2) $PaleYellow 230
  Dot $g 7 11 $Blue 'A'; Dot $g 28 11 $Green 'B'
  Dot $g 12 5 $Purple '看'; Dot $g 23 5 $Orange '开'
  Dot $g 15 8 $Red '双'; Dot $g 20 8 $Red '双'
  Dot $g 18 4 $Green '出'
  LineG $g 12 5 23 5 $Purple 3
  Arrow $g 7 11 15 8 $Orange 4; Arrow $g 28 11 20 8 $Orange 4; Arrow $g 17.5 8 18 4 $Green 4
  CheckCard $g 2 1 '合作检查' 'A 看信息，B 操作机关；双开关验证沟通，不让任何一人空等。' $PaleYellow
  Legend $g @(
    @{Color=$Purple;Text='信息不对称/视线'},
    @{Color=$Red;Text='同步点'},
    @{Color=$Green;Text='共享出口'}
  )
}

Save-Diagram 'level-design-iteration-loop' '关卡设计迭代闭环：每一步都有产出物' {
  param($g)
  $steps=@(
    @{x=4;y=3;t="概念`n一句话目标";c=$PaleBlue},
    @{x=15;y=2;t="进程`n矩阵表";c=$PaleGreen},
    @{x=26;y=3;t="空间`n灰盒图";c=$PaleYellow},
    @{x=23;y=11;t="测试`n观察记录";c=$PaleOrange},
    @{x=8;y=11;t="迭代`n修正清单";c=$PalePurple}
  )
  foreach($s in $steps){ Box $g ($s.x) ($s.y) 6 3 ($s.t) ($s.c) }
  Arrow $g 10 4.5 15 3.5; Arrow $g 21 3.5 26 4.5; Arrow $g 29 6 26 11; Arrow $g 23 12.5 14 12.5; Arrow $g 8 11 6 6
  CheckCard $g 13 7 '核心原则' '不要只改表象。每次修正都要回到：假设、空间、指标。' $PaleYellow
}

Save-Diagram 'blockout-level-layout' 'Blockout 关卡布局：矩阵 beat 落到空间' {
  param($g)
  function Room($x,$y,$w,$h,$fill,$label) {
    $rect = R $x $y $w $h
    Fill-R $g $rect $fill 235
    Stroke-R $g $rect $Black 3
    Draw-Text $g $label $FBoldSmall $Black ($rect.X + 8) ($rect.Y + $rect.Height - 54) ($rect.Width - 16) 46 $FmtCenter
  }
  Room 4 8 5 4 $PaleBlue "B01 观察`n技能: 看目标"
  Room 9 7 6 5 $PaleGreen "B02 练习`n动作: 安全通过"
  Room 15 6 6 6 $PaleYellow "B03 变奏`n障碍: 坑+巡逻"
  Room 21 5 6 7 $PaleOrange "B04 验证`n敌人+门"
  Room 27 7 5 5 $PalePurple "B05 释放`n奖励后出口"

  Fill-R $g (R 2 9 2 2) $Green 220
  Draw-Text $g '入口' $FBoldSmall $Black ($OX+2*$GridSize) ($OY+9*$GridSize+26) 80 28 $FmtCenter
  Dot $g 5 10 $Blue 'P'
  Dot $g 31 9 $Green '出'
  Dot $g 30 8 $Yellow '奖'

  Arrow $g 5.5 10 9 10 $Orange 4
  Arrow $g 10 10 15 9 $Orange 4
  Arrow $g 16 9 21 8 $Orange 4
  Arrow $g 22 8 27 9 $Orange 4
  Arrow $g 28 9 31 9 $Orange 4

  Dot $g 12 8 $Yellow '奖'
  Dot $g 13 6 $Orange '关'
  Dot $g 17 10 $Red '坑'
  Dot $g 19 8 $Red '敌'
  Dot $g 24 7 $Red '敌'
  Dot $g 25 10 $Orange '门'

  Arrow $g 10 8 12 6 $Purple 4
  Arrow $g 12 6 20 5 $Purple 4
  Arrow $g 20 5 23 7 $Purple 4
  LineG $g 18 11 13 11 $Purple 4
  Arrow $g 13 11 10 10 $Purple 4

  Draw-Text $g '第一眼目标线：入口能看见出口方向与奖励诱因' $FTiny $Blue ($OX+4*$GridSize) ($OY+5*$GridSize) 410 24 $FmtCenter
  LineG $g 5 9 31 9 $Blue 2
  Draw-Text $g '支路/回收：奖励支路提供变奏，失败后回到 B02 重试' $FTiny $Purple ($OX+12*$GridSize) ($OY+3*$GridSize) 560 24 $FmtCenter
  Draw-Text $g '读图顺序：先定矩阵格，再把入口、障碍、奖励、出口贴到对应空间节点。' $FSmall $Black ($OX+4*$GridSize) ($OY+13*$GridSize) 980 28 $FmtCenter

  CheckCard $g 3 1 '第一眼目标' '入口处必须能读到目标、奖励诱因或短期路线；看不见，就不是教学。' $PaleBlue
  CheckCard $g 15 1 '失败回收' '验证段失败后回到最近练习段，不强迫玩家重跑整关。' $PaleGreen
  Legend $g @(
    @{Color=$Blue;Text='入口/玩家起点'},
    @{Color=$Red;Text='障碍或敌人'},
    @{Color=$Yellow;Text='奖励/资源'},
    @{Color=$Purple;Text='支路/回收路线'}
  )
}

Save-Diagram 'telemetry-heatmap-matrix-writeback' '遥测热图与矩阵回写：证据改设计' {
  param($g)
  Box $g 2 3 15 10 '测试热图：把失败点贴回空间' ([System.Drawing.Color]::FromArgb(250,250,250))
  Fill-R $g (R 4 10 10 1) $Wall 230
  Fill-R $g (R 4 7 4 3) $PaleBlue 210
  Fill-R $g (R 8 7 4 3) $PaleYellow 210
  Fill-R $g (R 12 7 3 3) $PaleOrange 210
  Fill-R $g (R 10 10 2 1) ([System.Drawing.Color]::White) 255
  Stroke-R $g (R 10 10 2 1) $Red 3
  Dot $g 4.5 9.5 $Blue 'P'
  Dot $g 15 7.5 $Green '出'
  Dot $g 11 6.5 $Yellow '奖'
  Dot $g 9.5 9.5 $Red '死'
  Dot $g 10.5 9.5 $Red '死'
  Dot $g 7 7.5 $Orange '停'
  Dot $g 13.5 10.5 $Purple '绕'
  Arrow $g 5 9.5 8 9.5 $Orange 4
  Arrow $g 8 9.5 10 9.5 $Orange 4
  Arrow $g 12 9.5 15 7.5 $Orange 4
  LineG $g 4.5 7.5 15 7.5 $Blue 2
  Draw-Text $g '死亡聚集：3格跳起跳点偏早' $FTiny $Red ($OX+7*$GridSize) ($OY+11.3*$GridSize) 260 22 $FmtCenter
  Draw-Text $g '停留：入口看不清落点' $FTiny $Orange ($OX+3.4*$GridSize) ($OY+6.1*$GridSize) 260 22 $FmtCenter
  Draw-Text $g '绕路：奖励路径压过主路' $FTiny $Purple ($OX+11.5*$GridSize) ($OY+12.1*$GridSize) 260 22 $FmtCenter

  Box $g 20 2 13 3 "矩阵格：B04 验证跳`n假设：玩家已掌握 3 格跳" $PaleYellow
  Box $g 20 6 13 3 "证据：死亡 6 次 + 停留 18 秒`n访谈：不知道哪里起跳" $PaleOrange
  Box $g 20 10 13 3 "回写：加预告线、放宽首个落点`n下一轮只测 B04" $PaleGreen
  Arrow $g 17 8 20 3.5
  Arrow $g 26.5 5 26.5 6
  Arrow $g 26.5 9 26.5 10
  CheckCard $g 3 14 '使用方式' '热图回答“哪里卡”，录像/访谈回答“为什么卡”，矩阵回写回答“改哪格”。' $PaleBlue
}

Save-Diagram 'genre-matrix-adaptation' '不同类型关卡的矩阵适配' {
  param($g)
  $cards=@(
    @{x=2;y=2;t="平台`n跳距/落点/节奏";c=$PaleBlue},
    @{x=13;y=2;t="解谜`n规则/反馈/视线";c=$PaleYellow},
    @{x=24;y=2;t="射击`n视线/掩体/优先级";c=$PaleOrange},
    @{x=2;y=10;t="潜行`n视锥/巡逻/时机";c=$PaleGreen},
    @{x=13;y=10;t="合作`n分工/沟通/同步";c=$PalePurple},
    @{x=24;y=10;t="多角色`n能力/切换/互补";c=[System.Drawing.Color]::FromArgb(232,245,245)}
  )
  foreach($c in $cards){ Box $g ($c.x) ($c.y) 9 4 ($c.t) ($c.c); Dot $g (($c.x)+1.5) (($c.y)+3) $Blue '技'; Dot $g (($c.x)+4.5) (($c.y)+3) $Orange '尺'; Dot $g (($c.x)+7.5) (($c.y)+3) $Red '险' }
  CheckCard $g 10 7 '迁移规则' '不换工具，只替换动作轴、标尺轴、风险点和验证指标。' $PaleYellow
}

Save-Diagram 'level-design-pitfalls-correction-board' '常见设计陷阱与修正策略：诊断板' {
  param($g)
  $cards=@(
    @{x=1;y=2;t='没教就考';b="症状：首次见机制就死`n修正：加低压引介";c=$PaleOrange},
    @{x=13;y=2;t='标尺漂移';b="症状：同类跳跃忽难忽易`n修正：回到格子";c=$PaleBlue},
    @{x=25;y=2;t='奖励误导';b="症状：玩家总走错路`n修正：重排奖励层级";c=$PaleYellow},
    @{x=1;y=10;t='目标不可读';b="症状：入口停顿过久`n修正：强化第一眼目标";c=$PaleGreen},
    @{x=13;y=10;t='情绪断裂';b="症状：高压后继续高压`n修正：加入释放段";c=$PalePurple},
    @{x=25;y=10;t='只看数据';b="症状：知道哪里卡`n修正：补录像和访谈";c=[System.Drawing.Color]::FromArgb(232,245,245)}
  )
  foreach($c in $cards){ Box $g ($c.x) ($c.y) 9 5 ($c.t) ($c.c); Draw-Text $g ($c.b) $FTiny $Black ($OX+($c.x)*$GridSize+14) ($OY+($c.y)*$GridSize+78) 320 86 $FmtLeft; Arrow $g (($c.x)+2) (($c.y)+3.5) (($c.x)+7) (($c.y)+3.5) $Orange 3 }
}

Save-Diagram 'five-beat-blockout-exercise' '五段式 Blockout 练习工作表' {
  param($g)
  $names=@('B01 引介','B02 练习','B03 验证','B04 变奏','B05 释放')
  for($i=0;$i -lt 5;$i++){
    $x=2+$i*7
    Box $g $x 3 6 8 $names[$i] ($(if($i -eq 0){$PaleBlue}elseif($i -eq 1){$PaleGreen}elseif($i -eq 2){$PaleYellow}elseif($i -eq 3){$PaleOrange}else{$PalePurple}))
    Draw-Text $g "技能：____`n动作：____`n障碍：____`n奖励：____`n情绪：____" $FTiny $Black ($OX+$x*$GridSize+16) ($OY+($GridSize*5)+20) 205 150
    if($i -lt 4){ Arrow $g ($x+6) 7 ($x+7) 7 $Orange 3 }
  }
  Dot $g 2 12 $Blue '入'; Dot $g 36 12 $Green '出'
  CheckCard $g 2 13 '练习要求' '每个 beat 至少标入口、出口、目标、障碍、奖励和失败回收路线。' $PaleYellow
}

$script:ReportsByName.Values | Sort-Object Diagram | Export-Csv -LiteralPath $ReportPath -NoTypeInformation -Encoding UTF8
if ($script:ViolationList.Count -gt 0) {
  $script:ViolationList | Export-Csv -LiteralPath $ViolationPath -NoTypeInformation -Encoding UTF8
  throw "Grid alignment violations found: $($script:ViolationList.Count). See $ViolationPath"
}
if (Test-Path -LiteralPath $ViolationPath) {
  Remove-Item -LiteralPath $ViolationPath -Force
}

foreach ($img in $script:IconCache.Values) { $img.Dispose() }
Write-Output "Generated 17 informative grid-aligned PNG diagrams."
Write-Output "Grid report: $ReportPath"

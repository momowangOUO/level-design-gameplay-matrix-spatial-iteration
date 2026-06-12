$ErrorActionPreference = 'Stop'
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()
Add-Type -AssemblyName System.Drawing

$Root = 'C:\Users\liyian.andy\Desktop\搜打撤'
$IconDir = Join-Path $Root 'assets\generated-level-design\image2-icons'
New-Item -ItemType Directory -Force -Path $IconDir | Out-Null

$Sheet = Get-ChildItem -LiteralPath 'C:\Users\liyian.andy\.codex\generated_images\019eba0e-fa57-7493-bf7b-e991badf0191' -Filter '*.png' |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1 -ExpandProperty FullName

Copy-Item -LiteralPath $Sheet -Destination (Join-Path $IconDir 'image2-ability-icon-sheet.png') -Force

$names = @(
  'ability_player','ability_vertical_jump','ability_horizontal_jump','ability_speed',
  'ability_risk_landing','ability_interaction_radius','ability_damage_radius','ability_body_box',
  'ability_movement_path','ability_platform_tile','ability_high_ledge','ability_checkpoint'
)

$src = [System.Drawing.Bitmap]::FromFile($Sheet)
$cols = 4
$rows = 3
$cellW = [int]($src.Width / $cols)
$cellH = [int]($src.Height / $rows)
$padX = [int]($cellW * 0.08)
$padY = [int]($cellH * 0.10)

for ($i = 0; $i -lt $names.Count; $i++) {
  $col = $i % $cols
  $row = [int][Math]::Floor($i / $cols)
  $crop = [System.Drawing.Rectangle]::new(($col * $cellW) + $padX, ($row * $cellH) + $padY, $cellW - (2 * $padX), $cellH - (2 * $padY))
  $dst = New-Object System.Drawing.Bitmap($crop.Width, $crop.Height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $g = [System.Drawing.Graphics]::FromImage($dst)
  $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  $g.DrawImage($src, [System.Drawing.Rectangle]::new(0,0,$crop.Width,$crop.Height), $crop, [System.Drawing.GraphicsUnit]::Pixel)
  $g.Dispose()

  for ($x = 0; $x -lt $dst.Width; $x++) {
    for ($y = 0; $y -lt $dst.Height; $y++) {
      $p = $dst.GetPixel($x, $y)
      if ($p.R -gt 244 -and $p.G -gt 244 -and $p.B -gt 244) {
        $dst.SetPixel($x, $y, [System.Drawing.Color]::FromArgb(0, $p.R, $p.G, $p.B))
      }
    }
  }

  $out = Join-Path $IconDir ($names[$i] + '.png')
  $dst.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
  $dst.Dispose()
}

$src.Dispose()
Write-Host "Split image2 ability icon sheet into $($names.Count) icons: $IconDir"

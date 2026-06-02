param(
  [Parameter(Mandatory=$true)]
  [string]$DeckDir,

  [Parameter(Mandatory=$true)]
  [string]$OutputDir,

  [string]$Slides = "1,2,6",

  [string]$ChromePath = "",

  [int]$ScreenshotWidth = 1600,

  [int]$ScreenshotHeight = 900,

  [int]$BrowserHeightOffset = 95
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$resolvedDeck = Resolve-Path -LiteralPath $DeckDir
$indexPath = Join-Path $resolvedDeck "index.html"

if (-not (Test-Path -LiteralPath $indexPath)) {
  throw "index.html not found: $indexPath"
}

if (-not $ChromePath) {
  $chrome = Get-Command chrome.exe, msedge.exe -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $chrome) {
    throw "chrome.exe or msedge.exe not found"
  }
  $ChromePath = $chrome.Source
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$resolvedOutput = Resolve-Path -LiteralPath $OutputDir
$indexAbsolutePath = (Resolve-Path -LiteralPath $indexPath).Path
$fileUrl = ([System.Uri]$indexAbsolutePath).AbsoluteUri
Add-Type -AssemblyName System.Drawing
$windowHeight = $ScreenshotHeight + $BrowserHeightOffset

foreach ($slideText in ($Slides -split ",")) {
  $slide = [int]$slideText.Trim()
  if ($slide -lt 1) {
    throw "Slides must start from 1"
  }
  $name = "preview-{0:D2}.png" -f $slide
  $outPath = Join-Path $resolvedOutput $name
  $tmpPath = Join-Path $resolvedOutput ("__tmp-{0:D2}.png" -f $slide)
  if (Test-Path -LiteralPath $tmpPath) {
    Remove-Item -LiteralPath $tmpPath -Force
  }
  & $ChromePath `
    --headless=new `
    --disable-gpu `
    --hide-scrollbars `
    --force-device-scale-factor=1 `
    "--window-size=$ScreenshotWidth,$windowHeight" `
    --run-all-compositor-stages-before-draw `
    --virtual-time-budget=1200 `
    "--screenshot=$tmpPath" `
    "${fileUrl}?slide=$slide&screenshot=1" | Out-Null

  $image = $null
  $bitmap = $null
  $graphics = $null
  try {
    $image = [System.Drawing.Image]::FromFile($tmpPath)
    $bitmap = New-Object System.Drawing.Bitmap $ScreenshotWidth, $ScreenshotHeight
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.DrawImage(
      $image,
      (New-Object System.Drawing.Rectangle 0, 0, $ScreenshotWidth, $ScreenshotHeight),
      (New-Object System.Drawing.Rectangle 0, 0, $ScreenshotWidth, $ScreenshotHeight),
      [System.Drawing.GraphicsUnit]::Pixel
    )
    if (Test-Path -LiteralPath $outPath) {
      Remove-Item -LiteralPath $outPath -Force
    }
    $bitmap.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
  } finally {
    if ($graphics) { $graphics.Dispose() }
    if ($bitmap) { $bitmap.Dispose() }
    if ($image) { $image.Dispose() }
    if (Test-Path -LiteralPath $tmpPath) {
      Remove-Item -LiteralPath $tmpPath -Force
    }
  }
}

Write-Output "Screenshots written to: $resolvedOutput"

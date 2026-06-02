param(
  [Parameter(Mandatory=$true)]
  [string]$DeckDir,

  [Parameter(Mandatory=$true)]
  [string]$OutputZip
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$resolvedDeck = Resolve-Path -LiteralPath $DeckDir
$indexPath = Join-Path $resolvedDeck "index.html"

if (-not (Test-Path -LiteralPath $indexPath)) {
  throw "未找到 index.html: $indexPath"
}

$zipParent = Split-Path -Parent $OutputZip
if ($zipParent) {
  New-Item -ItemType Directory -Force -Path $zipParent | Out-Null
}

if (Test-Path -LiteralPath $OutputZip) {
  Remove-Item -LiteralPath $OutputZip -Force
}

$resolvedOutputZip = Resolve-Path -LiteralPath $OutputZip -ErrorAction SilentlyContinue
$files = Get-ChildItem -LiteralPath $resolvedDeck -Recurse -File | Where-Object {
  $_.FullName -ne $resolvedOutputZip -and
  $_.Name -notlike 'task-*.json' -and
  $_.Name -notlike '__tmp-*.png' -and
  $_.Name -notlike 'test-*.png'
}

$stage = Join-Path ([System.IO.Path]::GetTempPath()) ("anxin-ppt-package-" + [System.Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $stage | Out-Null

try {
  foreach ($file in $files) {
    $relativePath = $file.FullName.Substring($resolvedDeck.Path.Length).TrimStart('\', '/')
    $targetPath = Join-Path $stage $relativePath
    $targetParent = Split-Path -Parent $targetPath
    if ($targetParent) {
      New-Item -ItemType Directory -Force -Path $targetParent | Out-Null
    }
    Copy-Item -LiteralPath $file.FullName -Destination $targetPath -Force
  }

  $stageItems = Get-ChildItem -LiteralPath $stage -Force
  Compress-Archive -Path $stageItems.FullName -DestinationPath $OutputZip -CompressionLevel Optimal
} finally {
  if (Test-Path -LiteralPath $stage) {
    Remove-Item -LiteralPath $stage -Recurse -Force
  }
}

Write-Output "已生成交付压缩包: $OutputZip"

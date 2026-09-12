# KB911 icon source: exact approved 256x256 PNG, stored as split Base64 text.
# Important: do NOT redraw/resample it with System.Drawing. That path produced
# collapsed horizontal-bar icon frames on Windows. ImageMagick is used directly.

$parts = 1..6 | ForEach-Object {
  (Get-Content -Raw ("assets\icon_chunks\part$_.txt")).Trim()
}
$logoBase64 = ($parts -join '') -replace '\s',''
$bytes = [Convert]::FromBase64String($logoBase64)

$sha = [System.Security.Cryptography.SHA256]::Create()
try {
  $actualHash = ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-','').ToLowerInvariant()
} finally {
  $sha.Dispose()
}
$expectedHash = '18ccca99861d621cc0c6018489299b25019411d5a1aa1ca18f2a2d3ef27d80d2'
if ($actualHash -ne $expectedHash) {
  throw "KB911 approved icon source SHA mismatch: $actualHash"
}

if (-not (Test-Path 'build')) { New-Item -ItemType Directory -Path 'build' | Out-Null }
$source = 'build\KB911_icon_source.png'
[IO.File]::WriteAllBytes($source, $bytes)

$dim = (& magick identify -format '%wx%h' $source 2>$null)
if ($LASTEXITCODE -ne 0 -or $dim -ne '256x256') {
  throw "KB911 icon source validation failed: $dim"
}

$sizes = @(256,128,64,48,40,32,24,20,16)
foreach ($size in $sizes) {
  $appOut = "build\kb911_app_$size.png"
  $projectOut = "build\kb911_project_$size.png"

  # Direct high-quality resize from the verified source. No intermediate raster API.
  & magick $source -filter Lanczos -resize "${size}x${size}!" -strip $appOut
  if ($LASTEXITCODE -ne 0) { throw "Failed to render $appOut" }

  & magick $source -colorspace Gray -filter Lanczos -resize "${size}x${size}!" -strip $projectOut
  if ($LASTEXITCODE -ne 0) { throw "Failed to render $projectOut" }

  $appDim = (& magick identify -format '%wx%h' $appOut 2>$null)
  $projectDim = (& magick identify -format '%wx%h' $projectOut 2>$null)
  if ($appDim -ne "${size}x${size}" -or $projectDim -ne "${size}x${size}") {
    throw "Bad rendered icon frame size at $size: app=$appDim project=$projectDim"
  }
}

# Pixel-exact guard for the master application frame. This specifically prevents
# the previous 'black horizontal line on white' regression from passing CI.
& magick compare -metric AE $source 'build\kb911_app_256.png' null: 2>$null
if ($LASTEXITCODE -ne 0) {
  throw 'KB911 256px application icon no longer matches the approved source.'
}

Write-Host "KB911 icon source verified: $actualHash"
Write-Host 'KB911 icon frames rendered directly by ImageMagick: 9 app + 9 grayscale project frames.'

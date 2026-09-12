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

# Keep the approved icon's white lettering, cyan arrow, outline, and exterior.
# Recolor only the dark fill inside its rounded outline for project files.
$darkMask = 'build\kb911_project_dark.png'
$shapeMask = 'build\kb911_project_shape.png'
$fillMask = 'build\kb911_project_mask.png'
$grayLayer = 'build\kb911_project_gray.png'
$projectSource = 'build\kb911_project_source.png'
& magick $source -colorspace Gray -threshold '27%' -negate $darkMask
if ($LASTEXITCODE -ne 0) { throw 'Failed to isolate the project icon dark fill' }
& magick -size '256x256' 'xc:black' -fill white -draw 'roundrectangle 17,17 238,238 34,34' $shapeMask
if ($LASTEXITCODE -ne 0) { throw 'Failed to create the project icon interior mask' }
& magick $darkMask $shapeMask -compose Multiply -composite $fillMask
if ($LASTEXITCODE -ne 0) { throw 'Failed to mask the project icon interior' }
& magick -size '256x256' 'xc:#777777' $fillMask -alpha off -compose CopyOpacity -composite $grayLayer
if ($LASTEXITCODE -ne 0) { throw 'Failed to color the project icon interior' }
& magick $source $grayLayer -compose Over -composite $projectSource
if ($LASTEXITCODE -ne 0) { throw 'Failed to compose the project icon' }
$fillColor = (& magick $projectSource -format '%[pixel:p{128,65}]' info:)
if ($LASTEXITCODE -ne 0 -or $fillColor -ne 'srgb(119,119,119)') {
  throw "KB911 project icon interior is not gray: $fillColor"
}

# Remove the solid black square outside the white rounded outline. Retain the
# entire outline and the existing gray interior, letters, and blue arrow.
$outerMask = 'build\kb911_project_outer_mask.png'
& magick -size '256x256' 'xc:black' -fill white -draw 'roundrectangle 15,16 240,241 38,38' $outerMask
if ($LASTEXITCODE -ne 0) { throw 'Failed to create the project icon transparency mask' }
& magick $projectSource $outerMask -alpha off -compose CopyOpacity -composite $projectSource
if ($LASTEXITCODE -ne 0) { throw 'Failed to make the project icon exterior transparent' }

$sizes = @(256,128,64,48,40,32,24,20,16)
foreach ($size in $sizes) {
  $appOut = "build\kb911_app_$size.png"
  $projectOut = "build\kb911_project_$size.png"

  # Direct high-quality resize from the verified source. No intermediate raster API.
  & magick $source -filter Lanczos -resize "${size}x${size}!" -strip $appOut
  if ($LASTEXITCODE -ne 0) { throw "Failed to render $appOut" }

  & magick $projectSource -filter Lanczos -resize "${size}x${size}!" -strip $projectOut
  if ($LASTEXITCODE -ne 0) { throw "Failed to render $projectOut" }

  $appDim = (& magick identify -format '%wx%h' $appOut 2>$null)
  $projectDim = (& magick identify -format '%wx%h' $projectOut 2>$null)
  if ($appDim -ne "${size}x${size}" -or $projectDim -ne "${size}x${size}") {
    throw "Bad rendered icon frame size at ${size}: app=$appDim project=$projectDim"
  }
}

# Pixel-exact guard for the master application frame. This specifically prevents
# the previous 'black horizontal line on white' regression from passing CI.
& magick compare -metric AE $source 'build\kb911_app_256.png' null: 2>$null
if ($LASTEXITCODE -ne 0) {
  throw 'KB911 256px application icon no longer matches the approved source.'
}

Write-Host "KB911 icon source verified: $actualHash"
Write-Host 'KB911 icon frames rendered directly by ImageMagick: 9 app + 9 gray-interior project frames.'

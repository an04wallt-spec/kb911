Add-Type -AssemblyName System.Drawing

# KB911 v32: build both ICO files directly from the approved source artwork.
# No ImageMagick and no "PNG wrapped as ICO" shortcuts. Each ICO contains
# real PNG frames for the Windows shell sizes below.
$parts = 1..5 | ForEach-Object {
  (Get-Content -Raw ("assets\icon_chunks\part$_.txt")).Trim()
}
$logoBase64 = ($parts -join '') -replace '\s',''
$bytes = [Convert]::FromBase64String($logoBase64)
$sourceStream = New-Object IO.MemoryStream(,$bytes)
$source = [System.Drawing.Bitmap]::FromStream($sourceStream)

function Write-U16LE([IO.BinaryWriter]$bw,[int]$v) {
  $bw.Write([byte]($v -band 0xFF))
  $bw.Write([byte](($v -shr 8) -band 0xFF))
}
function Write-U32LE([IO.BinaryWriter]$bw,[long]$v) {
  $bw.Write([byte]($v -band 0xFF))
  $bw.Write([byte](($v -shr 8) -band 0xFF))
  $bw.Write([byte](($v -shr 16) -band 0xFF))
  $bw.Write([byte](($v -shr 24) -band 0xFF))
}

function New-KB911Ico {
  param(
    [System.Drawing.Bitmap]$Source,
    [string]$Path,
    [bool]$Gray = $false
  )

  $sizes = @(256,128,64,48,40,32,24,20,16)
  $frames = New-Object System.Collections.Generic.List[byte[]]

  $grayAttributes = $null
  if ($Gray) {
    $cm = New-Object System.Drawing.Imaging.ColorMatrix
    $cm.Matrix00 = 0.299; $cm.Matrix01 = 0.299; $cm.Matrix02 = 0.299
    $cm.Matrix10 = 0.587; $cm.Matrix11 = 0.587; $cm.Matrix12 = 0.587
    $cm.Matrix20 = 0.114; $cm.Matrix21 = 0.114; $cm.Matrix22 = 0.114
    $cm.Matrix33 = 1.0; $cm.Matrix44 = 1.0
    $grayAttributes = New-Object System.Drawing.Imaging.ImageAttributes
    $grayAttributes.SetColorMatrix($cm)
  }

  foreach ($size in $sizes) {
    $bmp = New-Object System.Drawing.Bitmap($size,$size,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
    $g.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $dst = New-Object System.Drawing.Rectangle(0,0,$size,$size)

    if ($Gray) {
      $g.DrawImage($Source,$dst,0,0,$Source.Width,$Source.Height,[System.Drawing.GraphicsUnit]::Pixel,$grayAttributes)
    } else {
      $g.DrawImage($Source,$dst,0,0,$Source.Width,$Source.Height,[System.Drawing.GraphicsUnit]::Pixel)
    }

    $png = New-Object IO.MemoryStream
    $bmp.Save($png,[System.Drawing.Imaging.ImageFormat]::Png)
    $frames.Add($png.ToArray())
    $png.Dispose(); $g.Dispose(); $bmp.Dispose()
  }

  if ($grayAttributes) { $grayAttributes.Dispose() }

  $fs = [IO.File]::Open($Path,[IO.FileMode]::Create,[IO.FileAccess]::Write,[IO.FileShare]::Read)
  $bw = New-Object IO.BinaryWriter($fs)

  Write-U16LE $bw 0
  Write-U16LE $bw 1
  Write-U16LE $bw $sizes.Count

  $offset = 6 + (16 * $sizes.Count)
  for ($i=0; $i -lt $sizes.Count; $i++) {
    $size = $sizes[$i]
    $dim = if ($size -eq 256) { 0 } else { $size }
    $data = $frames[$i]
    $bw.Write([byte]$dim)
    $bw.Write([byte]$dim)
    $bw.Write([byte]0)
    $bw.Write([byte]0)
    Write-U16LE $bw 1
    Write-U16LE $bw 32
    Write-U32LE $bw $data.Length
    Write-U32LE $bw $offset
    $offset += $data.Length
  }

  foreach ($data in $frames) { $bw.Write([byte[]]$data) }
  $bw.Flush(); $bw.Dispose(); $fs.Dispose()
}

New-KB911Ico -Source $source -Path 'build\KB911.ico' -Gray $false
New-KB911Ico -Source $source -Path 'build\KB911_project.ico' -Gray $true

$source.Dispose(); $sourceStream.Dispose()
Write-Host 'KB911 v32 ICOs built directly with 9 Windows sizes each.'

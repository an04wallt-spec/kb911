Add-Type -AssemblyName System.Drawing

# KB911 v32: render every Windows icon size explicitly from the approved logo.
# ICO container assembly/validation is handled separately by make_ico_v32.py.
$parts = 1..5 | ForEach-Object {
  (Get-Content -Raw ("assets\icon_chunks\part$_.txt")).Trim()
}
$logoBase64 = ($parts -join '') -replace '\s',''
$bytes = [Convert]::FromBase64String($logoBase64)
$sourceStream = New-Object IO.MemoryStream(,$bytes)
$source = [System.Drawing.Bitmap]::FromStream($sourceStream)

$sizes = @(256,128,64,48,40,32,24,20,16)

$cm = New-Object System.Drawing.Imaging.ColorMatrix
$cm.Matrix00 = 0.299; $cm.Matrix01 = 0.299; $cm.Matrix02 = 0.299
$cm.Matrix10 = 0.587; $cm.Matrix11 = 0.587; $cm.Matrix12 = 0.587
$cm.Matrix20 = 0.114; $cm.Matrix21 = 0.114; $cm.Matrix22 = 0.114
$cm.Matrix33 = 1.0; $cm.Matrix44 = 1.0
$grayAttributes = New-Object System.Drawing.Imaging.ImageAttributes
$grayAttributes.SetColorMatrix($cm)

foreach ($size in $sizes) {
  foreach ($gray in @($false,$true)) {
    $bmp = New-Object System.Drawing.Bitmap($size,$size,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.Clear([System.Drawing.Color]::Transparent)
    $g.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
    $g.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $dst = New-Object System.Drawing.Rectangle(0,0,$size,$size)

    if ($gray) {
      $g.DrawImage($source,$dst,0,0,$source.Width,$source.Height,[System.Drawing.GraphicsUnit]::Pixel,$grayAttributes)
      $name = "build\kb911_project_$size.png"
    } else {
      $g.DrawImage($source,$dst,0,0,$source.Width,$source.Height,[System.Drawing.GraphicsUnit]::Pixel)
      $name = "build\kb911_app_$size.png"
    }

    $bmp.Save($name,[System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
  }
}

$grayAttributes.Dispose(); $source.Dispose(); $sourceStream.Dispose()
Write-Host 'KB911 v32 rendered 18 explicit PNG icon frames.'

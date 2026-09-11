Add-Type -AssemblyName System.Drawing

# Exact approved KB911 artwork supplied by the user, stored as split Base64 text
# only to keep repository/API writes small and lossless.
$parts = 1..5 | ForEach-Object {
  (Get-Content -Raw ("assets\icon_chunks\part$_.txt")).Trim()
}
$logoBase64 = ($parts -join '') -replace '\s',''
$bytes = [Convert]::FromBase64String($logoBase64)
[IO.File]::WriteAllBytes('build\KB911_icon.png',$bytes)

# .kb911 project files use the same approved artwork in grayscale so they
# remain visually distinct from the application icon.
$ms = New-Object IO.MemoryStream(,$bytes)
$src = [System.Drawing.Bitmap]::FromStream($ms)
$dst = New-Object System.Drawing.Bitmap($src.Width,$src.Height,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$g = [System.Drawing.Graphics]::FromImage($dst)
$cm = New-Object System.Drawing.Imaging.ColorMatrix
$cm.Matrix00 = 0.299; $cm.Matrix01 = 0.299; $cm.Matrix02 = 0.299
$cm.Matrix10 = 0.587; $cm.Matrix11 = 0.587; $cm.Matrix12 = 0.587
$cm.Matrix20 = 0.114; $cm.Matrix21 = 0.114; $cm.Matrix22 = 0.114
$cm.Matrix33 = 1.0; $cm.Matrix44 = 1.0
$ia = New-Object System.Drawing.Imaging.ImageAttributes
$ia.SetColorMatrix($cm)
$rect = New-Object System.Drawing.Rectangle(0,0,$src.Width,$src.Height)
$g.DrawImage($src,$rect,0,0,$src.Width,$src.Height,[System.Drawing.GraphicsUnit]::Pixel,$ia)
$dst.Save('build\KB911_project_icon.png',[System.Drawing.Imaging.ImageFormat]::Png)
$ia.Dispose(); $g.Dispose(); $dst.Dispose(); $src.Dispose(); $ms.Dispose()

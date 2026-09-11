Add-Type -AssemblyName System.Drawing
$size=256
$bmp=New-Object System.Drawing.Bitmap $size,$size,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb
$g=[System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint=[System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$g.Clear([System.Drawing.Color]::Transparent)
$bg=[System.Drawing.Color]::FromArgb(255,17,22,28)
$white=[System.Drawing.Color]::White
$blue=[System.Drawing.Color]::FromArgb(255,35,181,246)
$path=New-Object System.Drawing.Drawing2D.GraphicsPath
$r=28;$d=$r*2;$x=5;$y=5;$w=246;$h=246
$path.AddArc($x,$y,$d,$d,180,90);$path.AddArc($x+$w-$d,$y,$d,$d,270,90);$path.AddArc($x+$w-$d,$y+$h-$d,$d,$d,0,90);$path.AddArc($x,$y+$h-$d,$d,$d,90,90);$path.CloseFigure()
$g.FillPath((New-Object System.Drawing.SolidBrush $bg),$path)
$pen=New-Object System.Drawing.Pen $white,4
$g.DrawPath($pen,$path)
$kbFont=New-Object System.Drawing.Font 'Segoe UI',88,[System.Drawing.FontStyle]::Bold,[System.Drawing.GraphicsUnit]::Pixel
$font911=New-Object System.Drawing.Font 'Segoe UI',54,[System.Drawing.FontStyle]::Bold,[System.Drawing.GraphicsUnit]::Pixel
$sf=New-Object System.Drawing.StringFormat;$sf.Alignment=[System.Drawing.StringAlignment]::Center;$sf.LineAlignment=[System.Drawing.StringAlignment]::Center
$g.DrawString('KB',$kbFont,(New-Object System.Drawing.SolidBrush $white),(New-Object System.Drawing.RectangleF 20,36,216,108),$sf)
$g.DrawString('911',$font911,(New-Object System.Drawing.SolidBrush $white),(New-Object System.Drawing.RectangleF 45,137,166,58),$sf)
$arrowPen=New-Object System.Drawing.Pen $blue,7
$g.DrawLine($arrowPen,44,204,212,204)
$brushBlue=New-Object System.Drawing.SolidBrush $blue
$g.FillPolygon($brushBlue,@((New-Object System.Drawing.Point 28,204),(New-Object System.Drawing.Point 53,189),(New-Object System.Drawing.Point 53,219)))
$g.FillPolygon($brushBlue,@((New-Object System.Drawing.Point 228,204),(New-Object System.Drawing.Point 203,189),(New-Object System.Drawing.Point 203,219)))
$bmp.Save('build\KB911_icon.png',[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose();$bmp.Dispose()

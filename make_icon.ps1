Add-Type -AssemblyName System.Drawing
$size=256
$bmp=[System.Drawing.Bitmap]::new($size,$size,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$g=[System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint=[System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$g.Clear([System.Drawing.Color]::Transparent)
$bg=[System.Drawing.Color]::FromArgb(255,17,22,28)
$white=[System.Drawing.Color]::White
$blue=[System.Drawing.Color]::FromArgb(255,35,181,246)
$path=[System.Drawing.Drawing2D.GraphicsPath]::new()
$r=28;$d=$r*2;$x=5;$y=5;$w=246;$h=246
$path.AddArc($x,$y,$d,$d,180,90);$path.AddArc($x+$w-$d,$y,$d,$d,270,90);$path.AddArc($x+$w-$d,$y+$h-$d,$d,$d,0,90);$path.AddArc($x,$y+$h-$d,$d,$d,90,90);$path.CloseFigure()
$bgBrush=[System.Drawing.SolidBrush]::new($bg);$g.FillPath($bgBrush,$path)
$pen=[System.Drawing.Pen]::new($white,4);$g.DrawPath($pen,$path)
$kbFont=[System.Drawing.Font]::new('Segoe UI',88,[System.Drawing.FontStyle]::Bold,[System.Drawing.GraphicsUnit]::Pixel)
$font911=[System.Drawing.Font]::new('Segoe UI',54,[System.Drawing.FontStyle]::Bold,[System.Drawing.GraphicsUnit]::Pixel)
$sf=[System.Drawing.StringFormat]::new();$sf.Alignment=[System.Drawing.StringAlignment]::Center;$sf.LineAlignment=[System.Drawing.StringAlignment]::Center
$whiteBrush=[System.Drawing.SolidBrush]::new($white)
$g.DrawString('KB',$kbFont,$whiteBrush,[System.Drawing.RectangleF]::new(20,36,216,108),$sf)
$g.DrawString('911',$font911,$whiteBrush,[System.Drawing.RectangleF]::new(45,137,166,58),$sf)
$arrowPen=[System.Drawing.Pen]::new($blue,7);$g.DrawLine($arrowPen,44,204,212,204)
$brushBlue=[System.Drawing.SolidBrush]::new($blue)
$g.FillPolygon($brushBlue,[System.Drawing.Point[]]@([System.Drawing.Point]::new(28,204),[System.Drawing.Point]::new(53,189),[System.Drawing.Point]::new(53,219)))
$g.FillPolygon($brushBlue,[System.Drawing.Point[]]@([System.Drawing.Point]::new(228,204),[System.Drawing.Point]::new(203,189),[System.Drawing.Point]::new(203,219)))
$bmp.Save('build\KB911_icon.png',[System.Drawing.Imaging.ImageFormat]::Png)
$brushBlue.Dispose();$arrowPen.Dispose();$whiteBrush.Dispose();$font911.Dispose();$kbFont.Dispose();$pen.Dispose();$bgBrush.Dispose();$path.Dispose();$g.Dispose();$bmp.Dispose()

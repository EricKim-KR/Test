Add-Type -AssemblyName System.Windows.Forms,System.Drawing
$bmp = New-Object System.Drawing.Bitmap([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width, [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0,0,0,0,$bmp.Size)
$out = 'D:\GitHub\Test\openclaw_screenshot.png'
$bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
Write-Output "SCREENSHOT_SAVED:$out"

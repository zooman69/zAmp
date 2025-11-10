# Update English Template with Open Sans 11pt font

$templatePath = "c:\WhisperProject\zAmp\Templates\zAmp and USB Cable Verification - ENGLISH.msg"

# Create Outlook COM object
$outlook = New-Object -ComObject Outlook.Application
$mail = $outlook.CreateItemFromTemplate($templatePath)

# Get current body
$currentBody = $mail.HTMLBody

# Define new HTML body with Open Sans 11pt
$newBody = @"
<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: 'Open Sans', Arial, sans-serif; font-size: 11pt; }
</style>
</head>
<body style="font-family: 'Open Sans', Arial, sans-serif; font-size: 11pt;">
<p>Hello,</p>
<br>
<br>
<p>To accurately diagnose your zAmp issue, please provide clear photos of the following:</p>
<br>
<p>zAmp:<br>
A photo of the back of the zAmp, clearly showing the serial number and the USB cable connected to the zAmp.</p>
<br>
<p>Monoprice USB Cable:<br>
A close-up photo of the Monoprice USB cable, focusing on the section with the "Monoprice" logo.</p>
<br>
<p>System Setup:<br>
A photo of your system setup with the USB cable connected to both the zAmp and the system.</p>
<br>
<p>Please refer to the image below for examples of the requested photos. Once you have taken these photos, please send them to support@neuroptimal.com.</p>
<br>
<br>
<p>Thank you for your cooperation.</p>
</body>
</html>
"@

# Update the body
$mail.HTMLBody = $newBody

# Add verification image
$imagePath = "c:\WhisperProject\zAmp\Images\zAmp verification.png"
if (Test-Path $imagePath) {
    $attachment = $mail.Attachments.Add($imagePath)
    $attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "zAmpVerificationImage")
    $mail.HTMLBody = $mail.HTMLBody.Replace("</body>", "<p><img src=`"cid:zAmpVerificationImage`" alt=`"zAmp Verification`" style=`"max-width: 100%; height: auto;`"></p></body>")
}

# Save the template
$mail.SaveAs($templatePath, 3) # 3 = olTemplate

# Clean up
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($mail) | Out-Null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()

Write-Host "English template updated successfully!" -ForegroundColor Green
Write-Host "File: $templatePath" -ForegroundColor Yellow

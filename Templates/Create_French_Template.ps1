# PowerShell script to create French Outlook template
# Requires: Microsoft Outlook installed

# Create Outlook application object
$outlook = New-Object -ComObject Outlook.Application
$mail = $outlook.CreateItem(0)

# Set subject
$mail.Subject = "Vérification de l'image de zAmp et du câble USB"

# Set HTML body
$htmlBody = @"
<html>
<body style="font-family: Calibri, Arial, sans-serif; font-size: 11pt;">
<p>Bonjour,</p>

<p>Afin de diagnostiquer avec précision le problème de votre zAmp, veuillez fournir des photos claires des éléments suivants :</p>

<ol>
    <li><strong>zAmp :</strong><br>
    Une photo de l'arrière du zAmp, montrant clairement le numéro de série ainsi que le câble USB branché sur le zAmp.</li>
    <br>
    <li><strong>Câble USB Monoprice :</strong><br>
    Une photo en gros plan du câble USB Monoprice, mettant l'accent sur la section avec le logo "Monoprice".</li>
    <br>
    <li><strong>Configuration du système :</strong><br>
    Une photo de votre configuration système avec le câble USB connecté à la fois au zAmp et au système.</li>
</ol>

<p>Veuillez vous référer à l'image ci-dessous pour des exemples des photos demandées. Une fois ces photos prises, envoyez-les à <a href="mailto:support@neuroptimal.com">support@neuroptimal.com</a>.</p>

<p>Merci pour votre coopération.</p>
</body>
</html>
"@

$mail.HTMLBody = $htmlBody

# Add image if it exists
$imagePath = "c:\WhisperProject\zAmp\Templates\zAmp_verification_image.jpg"
if (Test-Path $imagePath) {
    $mail.Attachments.Add($imagePath)
}

# Save as .msg file
$savePath = "c:\WhisperProject\zAmp\Templates\zAmp_Verification_Request_FRENCH.msg"
$mail.SaveAs($savePath, 3)  # 3 = olMSG format

Write-Host "French template created successfully at: $savePath"
Write-Host "Note: Please open the .msg file and embed the image into the body, then save it again."

# Clean up
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($mail) | Out-Null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null

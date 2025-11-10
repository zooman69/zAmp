# PowerShell script to update the French Outlook template with French text
# Requires: Microsoft Outlook installed

try {
    # Create Outlook application object
    $outlook = New-Object -ComObject Outlook.Application

    # Open the French template
    $msgPath = "c:\WhisperProject\Templates\zAmp and USB Cable Verification - FRENCH.msg"
    $mail = $outlook.Session.OpenSharedItem($msgPath)

    # Update subject - PowerShell natively supports Unicode
    $mail.Subject = "Vérification de l'image de zAmp et du câble USB"

    # Get current body to preserve any embedded images
    $currentBody = $mail.HTMLBody

    # Create new French HTML body while preserving image tags
    $newBody = @"
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>
<body style="font-family: 'Open Sans', Arial, sans-serif; font-size: 11pt;">
<p>Bonjour,</p>
<br>
<br>
<p>Afin de diagnostiquer avec précision le problème de votre zAmp, veuillez fournir des photos claires des éléments suivants :</p>
<br>
<p>zAmp :<br>
Une photo de l'arrière du zAmp, montrant clairement le numéro de série ainsi que le câble USB branché sur le zAmp.</p>
<br>
<p>Câble USB Monoprice :<br>
Une photo en gros plan du câble USB Monoprice, mettant l'accent sur la section avec le logo "Monoprice".</p>
<br>
<p>Configuration du système :<br>
Une photo de votre configuration système avec le câble USB connecté à la fois au zAmp et au système.</p>
<br>
<p>Veuillez vous référer à l'image ci-dessous pour des exemples des photos demandées. Une fois ces photos prises, envoyez-les à support@neuroptimal.com.</p>
<br>
<br>
"@

    # Extract image tags from original body if they exist
    if ($currentBody -match '(<img[^>]+>)') {
        $imageTag = $matches[1]
        $newBody += "`n<p>" + $imageTag + "</p>`n"
    }

    $newBody += @"
<p>Merci pour votre coopération.</p>
</body>
</html>
"@

    # Set the new body
    $mail.HTMLBody = $newBody

    # Save the changes
    $mail.Save()
    $mail.Close(0)

    Write-Host "French template updated successfully!"
    Write-Host "File: $msgPath"

} catch {
    $errMsg = $_.Exception.Message
    Write-Host "Error: $errMsg"
} finally {
    # Clean up COM objects
    if ($mail) { [System.Runtime.Interopservices.Marshal]::ReleaseComObject($mail) | Out-Null }
    if ($outlook) { [System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null }
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}

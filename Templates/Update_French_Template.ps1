# PowerShell script to update the French Outlook template with French text
# Requires: Microsoft Outlook installed

try {
    # Create Outlook application object
    $outlook = New-Object -ComObject Outlook.Application

    # Open the French template
    $msgPath = "c:\WhisperProject\zAmp\Templates\zAmp and USB Cable Verification - FRENCH.msg"
    $mail = $outlook.Session.OpenSharedItem($msgPath)

    # Update subject
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
<p>Afin de diagnostiquer avec pr&eacute;cision le probl&egrave;me de votre zAmp, veuillez fournir des photos claires des &eacute;l&eacute;ments suivants :</p>
<br>
<p>zAmp :<br>
Une photo de l'arri&egrave;re du zAmp, montrant clairement le num&eacute;ro de s&eacute;rie ainsi que le c&acirc;ble USB branch&eacute; sur le zAmp.</p>
<br>
<p>C&acirc;ble USB Monoprice :<br>
Une photo en gros plan du c&acirc;ble USB Monoprice, mettant l'accent sur la section avec le logo &quot;Monoprice&quot;.</p>
<br>
<p>Configuration du syst&egrave;me :<br>
Une photo de votre configuration syst&egrave;me avec le c&acirc;ble USB connect&eacute; &agrave; la fois au zAmp et au syst&egrave;me.</p>
<br>
<p>Veuillez vous r&eacute;f&eacute;rer &agrave; l'image ci-dessous pour des exemples des photos demand&eacute;es. Une fois ces photos prises, envoyez-les &agrave; support@neuroptimal.com.</p>
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

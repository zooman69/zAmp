# PowerShell script to recreate French template from scratch
# This approach creates a completely new .msg file to avoid encoding issues

try {
    # Create Outlook application object
    $outlook = New-Object -ComObject Outlook.Application

    # Create a brand new mail item (not from template)
    $mail = $outlook.CreateItem(0) # 0 = olMailItem

    # Set the subject using plain text without accents first
    # We'll ask user to manually update it after creation
    $mail.Subject = "Verification de l'image de zAmp et du cable USB"

    # Create the HTML body with proper encoding
    $htmlBody = @"
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta charset="UTF-8">
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
<p><img src="cid:zAmpVerificationImage" alt="zAmp Verification" style="max-width: 100%; height: auto;"></p>
<br>
<br>
<p>Merci pour votre coop&eacute;ration.</p>
</body>
</html>
"@

    $mail.HTMLBody = $htmlBody

    # Try to add the verification image if it exists
    $imagePath = "c:\WhisperProject\zAmp\Images\zAmp verification"
    if (Test-Path $imagePath) {
        $attachment = $mail.Attachments.Add($imagePath)
        $attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "zAmpVerificationImage")
    }

    # Save as MSG file
    $savePath = "c:\WhisperProject\zAmp\Templates\zAmp and USB Cable Verification - FRENCH-NEW.msg"
    $mail.SaveAs($savePath, 3) # 3 = olMSG

    Write-Host "New French template created at: $savePath"
    Write-Host ""
    Write-Host "IMPORTANT: Please do the following:"
    Write-Host "1. Open the new file: zAmp and USB Cable Verification - FRENCH-NEW.msg"
    Write-Host "2. Manually change the subject to: Vérification de l'image de zAmp et du câble USB"
    Write-Host "3. Save and close"
    Write-Host "4. Delete the old FRENCH.msg file"
    Write-Host "5. Rename FRENCH-NEW.msg to FRENCH.msg"

} catch {
    Write-Host "Error: $($_.Exception.Message)"
} finally {
    # Clean up COM objects
    if ($mail) { [System.Runtime.Interopservices.Marshal]::ReleaseComObject($mail) | Out-Null }
    if ($outlook) { [System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null }
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}

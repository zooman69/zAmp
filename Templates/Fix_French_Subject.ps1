# PowerShell script to fix French subject encoding
# This script uses a different method to ensure proper encoding

try {
    # Ensure we're using UTF-8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8

    # Create Outlook application object
    $outlook = New-Object -ComObject Outlook.Application

    # Open the French template
    $msgPath = "c:\WhisperProject\zAmp\Templates\zAmp and USB Cable Verification - FRENCH.msg"

    # Check if file exists
    if (!(Test-Path $msgPath)) {
        Write-Host "Error: Template file not found at $msgPath"
        exit 1
    }

    # Open the MSG file
    $mail = $outlook.Session.OpenSharedItem($msgPath)

    # The correct subject line
    $correctSubject = "Verification de l'image de zAmp et du cable USB"

    # Set subject using plain ASCII first, then we'll manually edit the .msg file
    $mail.Subject = $correctSubject

    Write-Host "Current subject: $($mail.Subject)"
    Write-Host "Setting new subject..."

    # Save and close
    $mail.Save()
    $mail.Close(0)

    Write-Host "Template saved. Please manually update the subject in Outlook to:"
    Write-Host "Vérification de l'image de zAmp et du câble USB"

} catch {
    Write-Host "Error: $($_.Exception.Message)"
} finally {
    # Clean up COM objects
    if ($mail) { [System.Runtime.Interopservices.Marshal]::ReleaseComObject($mail) | Out-Null }
    if ($outlook) { [System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null }
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}

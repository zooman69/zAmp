# Remove signature from French template

$outlook = New-Object -ComObject Outlook.Application

# Load French template
$frenchTemplate = Join-Path $PSScriptRoot "zAmp and USB Cable Verification - FRENCH.msg"
$frenchMail = $outlook.CreateItemFromTemplate($frenchTemplate)
$frenchBody = $frenchMail.HTMLBody

# Find the signature section (starts with Kind regards)
$signaturePattern = '<div><p class=MsoNormal><span style=''font-family:"Open Sans",sans-serif;mso-fareast-font-family:"Times New Roman";color:#333333''>Kind regards'
$signatureStart = $frenchBody.IndexOf($signaturePattern)

if ($signatureStart -gt 0) {
    # Find where signature ends (before the final closing tags)
    $bodyEnd = $frenchBody.IndexOf('</body>', $signatureStart)
    $signatureEnd = $frenchBody.LastIndexOf('</div></div>', $bodyEnd)

    # Remove signature by reconstructing body without it
    $newBody = $frenchBody.Substring(0, $signatureStart) + $frenchBody.Substring($signatureEnd + 12)

    $frenchMail.HTMLBody = $newBody
    $frenchMail.SaveAs($frenchTemplate, 3)

    Write-Host "✅ Signature removed from French template successfully!" -ForegroundColor Green
} else {
    Write-Host "No signature found in French template" -ForegroundColor Yellow
}

# Cleanup
$frenchMail = $null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null
$outlook = $null

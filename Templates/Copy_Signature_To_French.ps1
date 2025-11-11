# Copy signature from English template to French template

$outlook = New-Object -ComObject Outlook.Application

# Load English template
$englishTemplate = Join-Path $PSScriptRoot "zAmp and USB Cable Verification - ENGLISH.msg"
$englishMail = $outlook.CreateItemFromTemplate($englishTemplate)
$englishBody = $englishMail.HTMLBody

# Extract the signature (everything after the last image tag closing and before </div></div></body>)
# The signature starts with: <p class=MsoNormal style='margin-bottom:12.0pt'>
# Looking for the signature div that starts with "Kind regards,"

# Find the signature section
$signatureStart = $englishBody.IndexOf('<div><p class=MsoNormal><span style=''font-family:"Open Sans",sans-serif;mso-fareast-font-family:"Times New Roman";color:#333333''>Kind regards')
$signatureEnd = $englishBody.LastIndexOf('</div></div></body>')

if ($signatureStart -gt 0 -and $signatureEnd -gt $signatureStart) {
    $signature = $englishBody.Substring($signatureStart, $signatureEnd - $signatureStart + 6)  # +6 for </div>
    Write-Host "Signature extracted successfully!" -ForegroundColor Green
    Write-Host "Length: $($signature.Length) characters" -ForegroundColor Cyan
} else {
    Write-Host "Could not find signature boundaries" -ForegroundColor Red
    $englishMail = $null
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null
    exit
}

# Load French template
$frenchTemplate = Join-Path $PSScriptRoot "zAmp and USB Cable Verification - FRENCH.msg"
$frenchMail = $outlook.CreateItemFromTemplate($frenchTemplate)
$frenchBody = $frenchMail.HTMLBody

# Find where to insert signature in French template (before </div></body>)
$insertPoint = $frenchBody.LastIndexOf('</div></body>')

if ($insertPoint -gt 0) {
    # Insert the signature
    $newFrenchBody = $frenchBody.Substring(0, $insertPoint) + $signature + '</div></body></html>'
    $frenchMail.HTMLBody = $newFrenchBody

    # Save the updated French template
    $frenchMail.SaveAs($frenchTemplate, 3)  # 3 = olMSG format
    Write-Host "✅ Signature added to French template successfully!" -ForegroundColor Green
} else {
    Write-Host "Could not find insertion point in French template" -ForegroundColor Red
}

# Cleanup
$englishMail = $null
$frenchMail = $null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null
$outlook = $null

Write-Host "`nFrench template updated at: $frenchTemplate" -ForegroundColor Cyan

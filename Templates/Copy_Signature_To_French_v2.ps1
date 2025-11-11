# Copy signature from English template to French template (v2)

$outlook = New-Object -ComObject Outlook.Application

# Load English template
$englishTemplate = Join-Path $PSScriptRoot "zAmp and USB Cable Verification - ENGLISH.msg"
$englishMail = $outlook.CreateItemFromTemplate($englishTemplate)
$englishBody = $englishMail.HTMLBody

# Extract the signature div
$signatureStart = $englishBody.IndexOf('<div><p class=MsoNormal><span style=''font-family:"Open Sans",sans-serif;mso-fareast-font-family:"Times New Roman";color:#333333''>Kind regards')
if ($signatureStart -lt 0) {
    Write-Host "ERROR: Could not find signature start" -ForegroundColor Red
    $englishMail = $null
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null
    exit
}

# Find the end of the signature section (the closing </div></div> before </body>)
$bodyTagIndex = $englishBody.IndexOf('</body>', $signatureStart)
$signatureEnd = $englishBody.LastIndexOf('</div></div>', $bodyTagIndex)

$signature = $englishBody.Substring($signatureStart, $signatureEnd - $signatureStart + 12)  # +12 for </div></div>

Write-Host "✓ Signature extracted: $($signature.Length) characters" -ForegroundColor Green

# Load French template
$frenchTemplate = Join-Path $PSScriptRoot "zAmp and USB Cable Verification - FRENCH.msg"
$frenchMail = $outlook.CreateItemFromTemplate($frenchTemplate)
$frenchBody = $frenchMail.HTMLBody

# Find </body> tag in French template
$frenchBodyEnd = $frenchBody.LastIndexOf('</body>')
if ($frenchBodyEnd -lt 0) {
    Write-Host "ERROR: Could not find </body> in French template" -ForegroundColor Red
    $englishMail = $null
    $frenchMail = $null
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null
    exit
}

# Find the last </p> or </div> before </body>
$lastParagraph = $frenchBody.LastIndexOf('</p>', $frenchBodyEnd)
$insertPoint = $lastParagraph + 4  # After </p>

# Insert signature
$newFrenchBody = $frenchBody.Substring(0, $insertPoint) + "`r`n" + $signature + $frenchBody.Substring($insertPoint)
$frenchMail.HTMLBody = $newFrenchBody

# Save
$frenchMail.SaveAs($frenchTemplate, 3)

Write-Host "✅ Signature successfully added to French template!" -ForegroundColor Green

# Cleanup
$englishMail = $null
$frenchMail = $null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null
$outlook = $null

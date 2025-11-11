# Extract signature from English template

$outlook = New-Object -ComObject Outlook.Application
$englishTemplate = Join-Path $PSScriptRoot "zAmp and USB Cable Verification - ENGLISH.msg"
$mailItem = $outlook.CreateItemFromTemplate($englishTemplate)

# Get the HTML body
$htmlBody = $mailItem.HTMLBody

# Save to a temp file for inspection
$outputFile = Join-Path $PSScriptRoot "english_template_body.html"
$htmlBody | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "English template body saved to: $outputFile" -ForegroundColor Green

# Cleanup
$mailItem = $null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null
$outlook = $null

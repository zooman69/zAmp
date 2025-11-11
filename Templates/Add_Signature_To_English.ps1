# PowerShell script to add signature to English email template

# Create Outlook application object
$outlook = New-Object -ComObject Outlook.Application

# Load the existing English template
$templatePath = Join-Path $PSScriptRoot "zAmp and USB Cable Verification - ENGLISH.msg"
$mailItem = $outlook.CreateItemFromTemplate($templatePath)

# Define the signature HTML
$signature = @"
<br><br>
<div style="font-family: 'Open Sans', Arial, sans-serif; color: #333;">
<p style="margin: 0;">Kind regards,</p>
<br>
<p style="margin: 0; font-weight: bold;">The Zengar® Team</p>
<p style="margin: 5px 0;"><a href="mailto:loaners-exchanges@neuroptimal.com" style="color: #5B9BD5;">loaners-exchanges@neuroptimal.com</a></p>
<p style="margin: 5px 0;">Monday – Friday: 9 AM - 5 PM EST</p>
<p style="margin: 5px 0;">(866) 990-6784 Ext. 780</p>
<br>
<table style="border-collapse: collapse;">
<tr>
<td style="padding-right: 20px;">
<img src="https://neuroptimal.com/wp-content/themes/porto-child/header/25yr_logo-400x200_cropped.png" alt="NeurOptimal 25 Years" style="height: 80px; width: auto;">
</td>
<td style="border-left: 3px solid #ccc; padding-left: 20px;">
<p style="margin: 0; font-size: 20px; color: #5B9BD5; font-weight: bold;">NEUROPTIMAL®</p>
<p style="margin: 5px 0; font-size: 16px;"><span style="color: #5B9BD5; font-weight: bold;">Loaners & Exchanges</span> | Zengar Institute Inc.</p>
<p style="margin: 5px 0; font-size: 14px;">
<a href="tel:8669900784" style="color: #333; text-decoration: none;">866.990.Optimal (6784)</a> |
<a href="https://www.neuroptimal.com" style="color: #5B9BD5;">www.neuroptimal.com</a> |
<a href="mailto:loaners-repairs@neuroptimal.com" style="color: #8BC34A;">loaners-repairs@neuroptimal.com</a>
</p>
<p style="margin: 5px 0;">
<a href="https://www.facebook.com/neuroptimal" style="text-decoration: none; margin-right: 5px;"><img src="https://img.icons8.com/color/30/000000/facebook-new.png" alt="Facebook" style="height: 24px; width: 24px;"></a>
<a href="https://www.instagram.com/neuroptimal" style="text-decoration: none; margin-right: 5px;"><img src="https://img.icons8.com/color/30/000000/instagram-new.png" alt="Instagram" style="height: 24px; width: 24px;"></a>
<a href="https://twitter.com/neuroptimal" style="text-decoration: none; margin-right: 5px;"><img src="https://img.icons8.com/color/30/000000/twitter.png" alt="Twitter" style="height: 24px; width: 24px;"></a>
<a href="https://www.youtube.com/neuroptimal" style="text-decoration: none;"><img src="https://img.icons8.com/color/30/000000/youtube-play.png" alt="YouTube" style="height: 24px; width: 24px;"></a>
</p>
</td>
</tr>
</table>
</div>
"@

# Get current body
$currentBody = $mailItem.HTMLBody

# Add signature before the closing body tag
if ($currentBody -match "</body>") {
    $newBody = $currentBody -replace "</body>", "$signature</body>"
} else {
    # If no body tag, just append
    $newBody = $currentBody + $signature
}

# Update the body
$mailItem.HTMLBody = $newBody

# Save as new template
$outputPath = Join-Path $PSScriptRoot "zAmp and USB Cable Verification - ENGLISH.msg"
$mailItem.SaveAs($outputPath, 3) # 3 = olMSG format

# Close and cleanup
$mailItem = $null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null
$outlook = $null

Write-Host "✅ Signature added to English template successfully!" -ForegroundColor Green
Write-Host "Template saved to: $outputPath" -ForegroundColor Cyan

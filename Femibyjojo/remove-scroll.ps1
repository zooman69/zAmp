# Remove scrolling animation from cloned site

$indexFile = "c:\WhisperProject\Femibyjojo\cloned-site\index.html"

# Read the file
$content = Get-Content $indexFile -Raw -Encoding UTF8

# Remove the scrolling CSS block (with multiline regex)
$pattern = '(?s)<style id="custom-scroll-animation">.*?</style>\s*'
$content = $content -replace $pattern, ''

# Save the file
Set-Content -Path $indexFile -Value $content -Encoding UTF8

Write-Host "Scrolling animation removed from index.html" -ForegroundColor Green
Write-Host "File saved: $indexFile" -ForegroundColor Yellow

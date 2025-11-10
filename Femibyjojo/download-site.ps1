# Download femibyjojo.com HTML
$url = "https://femibyjojo.com"
$outputFile = "c:\WhisperProject\Femibyjojo\femibyjojo.html"

Write-Host "Downloading HTML from $url..." -ForegroundColor Cyan

try {
    # Download the page
    $response = Invoke-WebRequest -Uri $url -UseBasicParsing

    # Save the HTML content
    $response.Content | Out-File -FilePath $outputFile -Encoding UTF8

    Write-Host "✓ HTML saved to: $outputFile" -ForegroundColor Green
    Write-Host "File size: $([math]::Round((Get-Item $outputFile).Length / 1KB, 2)) KB" -ForegroundColor Yellow

    # Also save all CSS files referenced
    Write-Host "`nExtracting CSS files..." -ForegroundColor Cyan
    $cssLinks = $response.Links | Where-Object { $_.href -match '\.css' }

    $cssFolder = "c:\WhisperProject\Femibyjojo\css"
    if (-not (Test-Path $cssFolder)) {
        New-Item -ItemType Directory -Path $cssFolder | Out-Null
    }

    # Also save all JS files referenced
    Write-Host "Extracting JavaScript files..." -ForegroundColor Cyan
    $jsLinks = $response.Links | Where-Object { $_.href -match '\.js' }

    $jsFolder = "c:\WhisperProject\Femibyjojo\js"
    if (-not (Test-Path $jsFolder)) {
        New-Item -ItemType Directory -Path $jsFolder | Out-Null
    }

    Write-Host "`n✓ Download complete!" -ForegroundColor Green
    Write-Host "Main HTML file: $outputFile" -ForegroundColor White

} catch {
    Write-Host "✗ Error downloading: $_" -ForegroundColor Red
}

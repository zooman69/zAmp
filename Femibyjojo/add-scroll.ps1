# Add scrolling animation to femibyjojo.html

$inputFile = "c:\WhisperProject\Femibyjojo\femibyjojo.html"
$outputFile = "c:\WhisperProject\Femibyjojo\femibyjojo-scrolling.html"

# Read the original file
$content = Get-Content $inputFile -Raw -Encoding UTF8

# CSS for scrolling animation
$scrollCSS = @"
<style id="custom-scroll-animation">
/* Custom Left-to-Right Auto Scroll Animation */
@keyframes scrollLeft {
    0% { transform: translateX(0); }
    100% { transform: translateX(-30%); }
}

@keyframes scrollRight {
    0% { transform: translateX(-30%); }
    100% { transform: translateX(0); }
}

/* Apply to entire content sections and containers */
[data-mesh-id*="comp-"],
section > div,
[class*="gallery"],
[class*="strip"],
div[id*="comp-"] {
    animation: scrollLeft 10s linear infinite !important;
    will-change: transform;
}

/* Alternate direction */
[data-mesh-id*="comp-"]:nth-of-type(even),
section > div:nth-of-type(even),
div[id*="comp-"]:nth-of-type(even) {
    animation: scrollRight 10s linear infinite !important;
}

/* Pause on hover */
[data-mesh-id*="comp-"]:hover,
section > div:hover,
div[id*="comp-"]:hover {
    animation-play-state: paused !important;
}

/* Ensure no overflow */
body, #SITE_CONTAINER, #site-root, #PAGES_CONTAINER {
    overflow-x: hidden !important;
}
</style>
"@

# Insert CSS before closing html tag
$newContent = $content -replace '</html>', "$scrollCSS`n</html>"

# Save the new file
Set-Content -Path $outputFile -Value $newContent -Encoding UTF8

Write-Host "Scrolling version created: $outputFile" -ForegroundColor Green
$fileSize = [math]::Round((Get-Item $outputFile).Length / 1KB, 2)
Write-Host "File size: $fileSize KB" -ForegroundColor Yellow

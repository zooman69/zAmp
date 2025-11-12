# Simple HTTP Server for zAmp
$port = 5000
$url = "http://localhost:$port/zAmp.html"

Write-Host "Starting web server on port $port..." -ForegroundColor Green
Write-Host "Navigate to: $url" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Create HTTP listener
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
$listener.Start()

# Open browser
Start-Process $url

Write-Host "Server is running..." -ForegroundColor Green

try {
    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response

        # Get the requested file path
        $localPath = $request.Url.LocalPath
        if ($localPath -eq "/") {
            $localPath = "/zAmp.html"
        }

        $filePath = Join-Path $PSScriptRoot $localPath.TrimStart('/')

        Write-Host "$($request.HttpMethod) $localPath" -ForegroundColor Gray

        if (Test-Path $filePath -PathType Leaf) {
            # Serve the file
            $content = [System.IO.File]::ReadAllBytes($filePath)
            $response.ContentLength64 = $content.Length

            # Set content type
            $extension = [System.IO.Path]::GetExtension($filePath)
            switch ($extension) {
                ".html" { $response.ContentType = "text/html" }
                ".css"  { $response.ContentType = "text/css" }
                ".js"   { $response.ContentType = "application/javascript" }
                ".json" { $response.ContentType = "application/json" }
                ".png"  { $response.ContentType = "image/png" }
                ".jpg"  { $response.ContentType = "image/jpeg" }
                ".gif"  { $response.ContentType = "image/gif" }
                ".svg"  { $response.ContentType = "image/svg+xml" }
                default { $response.ContentType = "application/octet-stream" }
            }

            $response.OutputStream.Write($content, 0, $content.Length)
        } else {
            # 404 Not Found
            $response.StatusCode = 404
            $buffer = [System.Text.Encoding]::UTF8.GetBytes("404 - File Not Found")
            $response.ContentLength64 = $buffer.Length
            $response.OutputStream.Write($buffer, 0, $buffer.Length)
        }

        $response.Close()
    }
} finally {
    $listener.Stop()
}


Write-Host "Starting ngrok tunnel..." -ForegroundColor Cyan
Write-Host "This will expose your local server to the internet" -ForegroundColor Yellow
Write-Host ""

# Start ngrok (adjust path if needed)
& "C:\Users\kusum\Downloads\ngrok-v3-stable-windows-amd64\ngrok.exe" http 8000

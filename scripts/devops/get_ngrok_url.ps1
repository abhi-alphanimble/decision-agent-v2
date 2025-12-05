# Get ngrok URL from the API
try {
    $response = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -Method Get
    $publicUrl = $response.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1 -ExpandProperty public_url
    
    if ($publicUrl) {
        Write-Host "`n✅ Your ngrok URL is:" -ForegroundColor Green
        Write-Host "$publicUrl" -ForegroundColor Cyan
        Write-Host "`n📋 Use this URL to install the bot:" -ForegroundColor Yellow
        Write-Host "$publicUrl/slack/install" -ForegroundColor Cyan
        Write-Host "`n🔧 Update these URLs in your Slack app settings:" -ForegroundColor Yellow
        Write-Host "   OAuth Redirect URL: $publicUrl/slack/install/callback" -ForegroundColor White
        Write-Host "   Event Subscriptions: $publicUrl/slack/events" -ForegroundColor White
        Write-Host "   Slash Command: $publicUrl/webhook/slack" -ForegroundColor White
    } else {
        Write-Host "❌ No ngrok tunnel found. Make sure ngrok is running." -ForegroundColor Red
        Write-Host "Run: .\start_ngrok.ps1" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Could not connect to ngrok. Make sure it's running." -ForegroundColor Red
    Write-Host "Run: .\start_ngrok.ps1" -ForegroundColor Yellow
    Write-Host "`nOr check the ngrok dashboard at: http://localhost:4040" -ForegroundColor Cyan
}

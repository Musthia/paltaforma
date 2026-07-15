Write-Host "[+] Deteniendo plataforma..." -ForegroundColor Yellow
& taskkill /f /im uvicorn.exe 2>$null
& taskkill /f /im node.exe 2>$null
& taskkill /f /im cloudflared.exe 2>$null
Start-Sleep -Seconds 1
Write-Host "[OK] Plataforma detenida" -ForegroundColor Green

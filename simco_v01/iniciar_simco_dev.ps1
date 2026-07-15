# ════════════════════════════════════════════════════════════
#  SIMCO - Desarrollo con auto-reload (hot reload)
#  Abre dos ventanas: backend + frontend con recarga automática
# ════════════════════════════════════════════════════════════

$PROJECT_DIR = "C:\proyectos\simco_v01"
$VENV_DIR = "$PROJECT_DIR\backend\venv"
$BACKEND_DIR = "$PROJECT_DIR\backend"
$FRONTEND_DIR = "$PROJECT_DIR\frontend"
$BACKEND_PORT = 8000

# ── Matar instancias previas ──
Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "uvicorn" } | Stop-Process -Force
Get-Process -Name "node*" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "vite" } | Stop-Process -Force

# ── Backend (ventana separada) ──
$backendArgs = @"
/c "$VENV_DIR\Scripts\activate.bat" && uvicorn app.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT
"@
Start-Process -WindowStyle Normal -FilePath "cmd.exe" -ArgumentList $backendArgs -WorkingDirectory $BACKEND_DIR

# ── Frontend (ventana separada) ──
Start-Process -WindowStyle Normal -FilePath "cmd.exe" -ArgumentList "/c npm run dev" -WorkingDirectory $FRONTEND_DIR

# ── Mostrar info ──
Start-Sleep -Seconds 2
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.PrefixOrigin -ne "WellKnown" } | Select-Object -First 1).IPAddress

Clear-Host
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SIMCO - Modo Desarrollo" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Backend API: http://localhost:$BACKEND_PORT" -ForegroundColor Cyan
Write-Host "  Frontend:    http://localhost:5173" -ForegroundColor Cyan
if ($ip) {
    Write-Host "  Red local:   http://$ip`:5173" -ForegroundColor Cyan
}
Write-Host "  Swagger:     http://localhost:$BACKEND_PORT/docs" -ForegroundColor Cyan
Write-Host "--------------------------------------------" -ForegroundColor Cyan
Write-Host "  Hot reload activo:" -ForegroundColor Yellow
Write-Host "  • Cambios en .tsx → recarga automática en :5173" -ForegroundColor Yellow
Write-Host "  • Cambios en .py  → recarga automática del backend" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "`nCerrando esta ventana NO detiene los procesos." -ForegroundColor Gray
Write-Host "Para detener todo cerra las ventanas de backend y frontend.`n" -ForegroundColor Gray

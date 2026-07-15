param(
    [switch]$Dev,
    [switch]$Frontend,
    [switch]$SimcoFrontend,
    [int]$Port = 8000
)

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BACKEND_DIR = Join-Path $ROOT "data_datcorr\backend"
$FRONTEND_DIR = Join-Path $ROOT "data_datcorr\frontend"
$SIMCO_FRONTEND_DIR = Join-Path $ROOT "simco_v01\frontend"
$VENV_DIR = Join-Path $ROOT "data_datcorr\venv"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Plataforma Unificada DATCORR + SIMCO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ── Kill existing processes ──────────────────────────────────────────
Write-Host "[+] Deteniendo procesos previos..." -ForegroundColor Yellow
$pidOnPort = (netstat -ano | Select-String ":8000 " | Select-String "LISTENING") -replace '.*\s+(\d+)$', '$1'
if ($pidOnPort) { Stop-Process -Id $pidOnPort -Force -ErrorAction SilentlyContinue }
& taskkill /f /im uvicorn.exe 2>$null
& taskkill /f /im python.exe 2>$null
& taskkill /f /im node.exe 2>$null
Start-Sleep -Seconds 3

# ── Check PostgreSQL ─────────────────────────────────────────────────
Write-Host "[+] Verificando PostgreSQL..." -ForegroundColor Yellow
try {
    $conn = New-Object System.Data.Odbc.OdbcConnection
    $conn.ConnectionString = "Driver={PostgreSQL Unicode};Server=localhost;Port=5432;Database=postgres;Uid=postgres;Pwd=postgres123;"
    $conn.Open()
    $conn.Close()
    Write-Host "  [OK] PostgreSQL conectado" -ForegroundColor Green
} catch {
    Write-Host "  [!] PostgreSQL no disponible - continuando igual" -ForegroundColor Red
}

# ── Start Backend (uvicorn) ──────────────────────────────────────────
Write-Host "[+] Iniciando backend unificado (puerto $Port)..." -ForegroundColor Yellow
$reload = if ($Dev) { "--reload" } else { "" }
$backendJob = Start-Job -ScriptBlock {
    param($dir, $port, $reload)
    Set-Location $dir
    if ($reload) {
        Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m uvicorn backend.main_unificado:app --host 0.0.0.0 --port $port $reload"
    } else {
        Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m uvicorn backend.main_unificado:app --host 0.0.0.0 --port $port"
    }
} -ArgumentList $BACKEND_DIR, $Port, $reload

Start-Sleep -Seconds 3

# ── Start Frontend DATCORR (optional) ────────────────────────────────
if ($Frontend) {
    Write-Host "[+] Iniciando frontend DATCORR (puerto 5173)..." -ForegroundColor Yellow
    $frontendJob = Start-Job -ScriptBlock {
        param($dir)
        Set-Location $dir
        Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "run dev"
    } -ArgumentList $FRONTEND_DIR
}

# ── Start Frontend SIMCO (optional) ──────────────────────────────────
if ($SimcoFrontend) {
    Write-Host "[+] Iniciando frontend SIMCO (puerto 5174)..." -ForegroundColor Yellow
    $simcoJob = Start-Job -ScriptBlock {
        param($dir)
        Set-Location $dir
        Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "run dev -- --port 5174"
    } -ArgumentList $SIMCO_FRONTEND_DIR
}

# ── Show info ────────────────────────────────────────────────────────
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.PrefixOrigin -eq "Dhcp" }).IPAddress | Select-Object -First 1
if (-not $ip) { $ip = "localhost" }

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Plataforma iniciada!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "  API:        http://$ip`:$Port"
Write-Host "  Docs:       http://$ip`:$Port/docs"
Write-Host "  Health:     http://$ip`:$Port/health"

if ($Frontend) {
    Write-Host "  Frontend DC: http://localhost:5173"
}
if ($SimcoFrontend) {
    Write-Host "  Frontend SC: http://localhost:5174"
}
Write-Host ""
Write-Host "  Para detener: .\detener_plataforma.ps1" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green

# Keep alive
while ($true) {
    $jobs = Get-Job -State Running
    if ($jobs.Count -eq 0) {
        Write-Host "[!] Todos los procesos terminaron" -ForegroundColor Red
        break
    }
    Start-Sleep -Seconds 5
}

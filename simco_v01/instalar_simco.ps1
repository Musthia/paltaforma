# ════════════════════════════════════════════════════════════
#  SIMCO - Script de instalación único
#  Ejecutar como Administrador en PowerShell
# ════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$PROJECT_DIR = "C:\proyectos\simco_v01"
$VENV_DIR = "$PROJECT_DIR\backend\venv"
$BACKEND_DIR = "$PROJECT_DIR\backend"
$FRONTEND_DIR = "$PROJECT_DIR\frontend"

Write-Host "`n=== SIMCO - Instalación ===" -ForegroundColor Cyan

# ── 1. Entorno virtual backend ──
if (-not (Test-Path "$VENV_DIR\Scripts\activate.bat")) {
    Write-Host "[1/5] Creando entorno virtual Python..." -ForegroundColor Yellow
    python -m venv "$VENV_DIR"
    & "$VENV_DIR\Scripts\pip.exe" install -r "$PROJECT_DIR\infra\requirements_backend.txt"
    Write-Host "  OK" -ForegroundColor Green
} else {
    Write-Host "[1/5] Entorno virtual ya existe" -ForegroundColor Green
}

# ── 2. Dependencias frontend ──
if (-not (Test-Path "$FRONTEND_DIR\node_modules")) {
    Write-Host "[2/5] Instalando dependencias del frontend..." -ForegroundColor Yellow
    Push-Location "$FRONTEND_DIR"
    npm install
    Pop-Location
    Write-Host "  OK" -ForegroundColor Green
} else {
    Write-Host "[2/5] Dependencias frontend ya instaladas" -ForegroundColor Green
}

# ── 3. Compilar frontend ──
if (-not (Test-Path "$FRONTEND_DIR\dist\index.html")) {
    Write-Host "[3/5] Compilando frontend..." -ForegroundColor Yellow
    Push-Location "$FRONTEND_DIR"
    npm run build
    Pop-Location
    Write-Host "  OK" -ForegroundColor Green
} else {
    Write-Host "[3/5] Frontend ya compilado" -ForegroundColor Green
}

# ── 4. Firewall: abrir puerto 8000 ──
$ruleName = "SIMCO - Puerto 8000"
$existing = netsh advfirewall firewall show rule name="$ruleName" 2>$null
if (-not $existing) {
    Write-Host "[4/5] Abriendo puerto 8000 en Firewall de Windows..." -ForegroundColor Yellow
    netsh advfirewall firewall add rule name="$ruleName" dir=in action=allow protocol=TCP localport=8000
    Write-Host "  OK" -ForegroundColor Green
} else {
    Write-Host "[4/5] Puerto 8000 ya abierto en firewall" -ForegroundColor Green
}

# ── 5. Seed: crear usuario admin en BD ──
Write-Host "[5/5] Creando usuario admin en la base de datos..." -ForegroundColor Yellow
Push-Location "$BACKEND_DIR"
& "$VENV_DIR\Scripts\python.exe" -c "
import os
os.environ['DB_ENGINE'] = 'postgres'
os.environ['POSTGRES_URL'] = 'postgresql+psycopg2://postgres:postgres123@localhost:5432/simco'
os.environ['ADMIN_USERNAME'] = 'Musthia'
os.environ['ADMIN_PASSWORD'] = '0611'
os.environ['ADMIN_FULLNAME'] = 'Administrador Maestro'
os.environ['ADMIN_ROLE'] = 'admin'
from app.db.seed import create_admin
create_admin()
"
Pop-Location
Write-Host "  OK" -ForegroundColor Green

# ── Resumen ──
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  SIMCO instalado correctamente" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Para iniciar el servidor:"
Write-Host "  .\iniciar_simco.bat"
Write-Host "`nPara acceder desde la misma red:"
Write-Host "  http://<IP_DE_ESTA_PC>:8000"
Write-Host "============================================" -ForegroundColor Cyan

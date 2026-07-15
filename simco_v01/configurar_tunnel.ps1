# ════════════════════════════════════════════════════════════
#  SIMCO - Configurar Cloudflare Tunnel (Quick Tunnel)
#  Sin necesidad de dominio propio
# ════════════════════════════════════════════════════════════

param(
    [switch]$InstallService,
    [switch]$UninstallService
)

$ErrorActionPreference = "Stop"
$PROJECT_DIR = "C:\proyectos\simco_v01"

# ── Detectar cloudflared ──
$cloudflared = Get-Command "cloudflared" -ErrorAction SilentlyContinue
if (-not $cloudflared) {
    Write-Host "cloudflared no está instalado." -ForegroundColor Yellow
    Write-Host "Descargando cloudflared..." -ForegroundColor Yellow
    
    $url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    $out = "$env:TEMP\cloudflared.exe"
    Invoke-WebRequest -Uri $url -OutFile $out
    
    $dest = "$env:ProgramFiles\cloudflared\cloudflared.exe"
    New-Item -ItemType Directory -Force -Path "$env:ProgramFiles\cloudflared" | Out-Null
    Copy-Item -Path $out -Destination $dest -Force
    
    # Agregar al PATH del sistema
    $oldPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $binPath = "$env:ProgramFiles\cloudflared"
    if ($oldPath -notlike "*$binPath*") {
        [Environment]::SetEnvironmentVariable("Path", "$oldPath;$binPath", "Machine")
    }
    $env:Path += ";$binPath"
    
    Write-Host "cloudflared instalado en $dest" -ForegroundColor Green
}

# ── Autenticar (solo la primera vez) ──
$credsPath = "$env:USERPROFILE\.cloudflared\cert.pem"
if (-not (Test-Path $credsPath)) {
    Write-Host "`nAutenticando con Cloudflare..." -ForegroundColor Yellow
    Write-Host "Se abrirá el navegador. Inicia sesión con tu cuenta de Cloudflare (gratis)." -ForegroundColor Cyan
    cloudflared tunnel login
    if (-not (Test-Path $credsPath)) {
        Write-Host "ERROR: No se pudo autenticar. Intentá de nuevo." -ForegroundColor Red
        exit 1
    }
    Write-Host "Autenticación exitosa" -ForegroundColor Green
} else {
    Write-Host "Ya autenticado con Cloudflare" -ForegroundColor Green
}

# ── Modo 1: Quick Tunnel (recomendado, sin dominio) ──
if (-not $InstallService -and -not $UninstallService) {
    Write-Host "`n═══════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  INICIANDO QUICK TUNNEL" -ForegroundColor Cyan
    Write-Host "  Primero asegurate de que el backend" -ForegroundColor Cyan
    Write-Host "  esté corriendo (iniciar_simco.bat)" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "`nPresioná Ctrl+C para detener el tunnel.`n" -ForegroundColor Gray
    
    cloudflared tunnel --url http://localhost:8000
    exit
}

# ── Modo 2: Instalar como servicio de Windows ──
if ($InstallService) {
    $tunnelName = "simco-tunnel"
    
    # Crear tunnel (si no existe)
    $existing = cloudflared tunnel list 2>$null | Select-String $tunnelName
    if (-not $existing) {
        Write-Host "Creando tunnel '$tunnelName'..." -ForegroundColor Yellow
        cloudflared tunnel create $tunnelName
    } else {
        Write-Host "Tunnel '$tunnelName' ya existe" -ForegroundColor Green
    }
    
    # Obtener ID del tunnel
    $tunnelId = cloudflared tunnel list 2>$null | Select-String $tunnelName | ForEach-Object { $_ -replace '.*?([a-f0-9-]{36}).*', '$1' }
    
    if (-not $tunnelId) {
        Write-Host "ERROR: No se pudo obtener el ID del tunnel" -ForegroundColor Red
        exit 1
    }
    
    # Crear archivo de configuración
    $configPath = "$env:USERPROFILE\.cloudflared\$tunnelName.yml"
    $configContent = @"
tunnel: $tunnelName
credentials-file: $env:USERPROFILE\.cloudflared\$tunnelName.json

ingress:
  - hostname: $tunnelName.trycloudflare.com
    service: http://localhost:8000
  - service: http_status:404
"@
    
    Set-Content -Path $configPath -Value $configContent -Force
    Write-Host "Configuración creada en $configPath" -ForegroundColor Green
    
    # Instalar como servicio
    Write-Host "Instalando tunnel como servicio de Windows..." -ForegroundColor Yellow
    cloudflared service install
    Write-Host "`nServicio instalado. Para iniciarlo manualmente:" -ForegroundColor Green
    Write-Host "  net start cloudflared" -ForegroundColor Cyan
    Write-Host "O desde Servicios (services.msc): cloudflared" -ForegroundColor Cyan
    Write-Host "`nPara ver el log del tunnel:" -ForegroundColor Cyan
    Write-Host "  cloudflared tunnel info $tunnelName" -ForegroundColor Cyan
}

if ($UninstallService) {
    Write-Host "Desinstalando servicio cloudflared..." -ForegroundColor Yellow
    cloudflared service uninstall
    Write-Host "Servicio desinstalado" -ForegroundColor Green
}

if (-not $InstallService -and -not $UninstallService) {
    Write-Host "`nUSO:" -ForegroundColor Cyan
    Write-Host "  .\configurar_tunnel.ps1              # Quick Tunnel (recomendado)"
    Write-Host "  .\configurar_tunnel.ps1 -InstallService  # Instalar como servicio"
    Write-Host "  .\configurar_tunnel.ps1 -UninstallService # Desinstalar servicio"
}

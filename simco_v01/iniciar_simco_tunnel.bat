@echo off
:: ════════════════════════════════════════════════════════════════
::  SIMCO - Inicio completo con Cloudflare Tunnel
::  Requiere: cloudflared instalado y tunnel configurado
:: ════════════════════════════════════════════════════════════════

title SIMCO - Servidor + Tunnel

:: ── Configuración ──────────────────────────────────────────────
set PROJECT_DIR=C:\proyectos\simco_v01
set TUNNEL_NAME=simco-tunnel
set BACKEND_PORT=8000

:: ── Paso 1: Iniciar el backend ───────────────────────────────
echo [SIMCO] Iniciando servidor...
start "SIMCO Backend" /B cmd /c "cd /d %PROJECT_DIR%\iniciar_simco.bat"

:: ── Paso 2: Esperar a que el backend esté listo ────────────────
echo [SIMCO] Esperando a que el backend inicie...
timeout /t 5 /nobreak >nul

:: ── Paso 3: Iniciar Cloudflare Tunnel ──────────────────────────
where cloudflared >nul 2>&1
if errorlevel 1 (
    echo [ERROR] cloudflared no esta instalado.
    echo Descargalo desde: https://github.com/cloudflare/cloudflared/releases
    pause
    exit /b 1
)

echo [SIMCO] Iniciando Cloudflare Tunnel "%TUNNEL_NAME%"...
echo.

start "SIMCO Tunnel" /B cloudflared tunnel run %TUNNEL_NAME%

echo.
echo ════════════════════════════════════════════════════════════
echo   SIMCO corriendo con tunnel activo
echo   Local:  http://localhost:%BACKEND_PORT%
echo   Publico: https://simco.tudominio.com  (tu dominio)
echo ════════════════════════════════════════════════════════════
echo.
echo Presiona Ctrl+C para detener todo.
echo.

cmd /k

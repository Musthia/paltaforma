@echo off
:: ════════════════════════════════════════════════════════════════
::  SIMCO - Script de inicio automático (Windows)
::  Ejecutar como administrador si usas Cloudflare Tunnel
:: ════════════════════════════════════════════════════════════════

title SIMCO - Servidor

:: ── Configuración ──────────────────────────────────────────────
:: Cambia estas rutas si instalaste el proyecto en otra ubicación
set PROJECT_DIR=C:\proyectos\simco_v01
set VENV_DIR=%PROJECT_DIR%\backend\venv
set BACKEND_DIR=%PROJECT_DIR%\backend
set FRONTEND_DIR=%PROJECT_DIR%\frontend
set ENV_FILE=%PROJECT_DIR%\.env.production

:: Puerto del backend (FastAPI)
set BACKEND_PORT=8000

:: ── Forzar rebuild si se pasa "rebuild" como argumento ─────────
if /I "%1"=="rebuild" (
    echo [SIMCO] Recompilando frontend por solicitud...
    if exist "%FRONTEND_DIR%\dist" rmdir /s /q "%FRONTEND_DIR%\dist"
)

:: ── Verificar que existe el entorno virtual ────────────────────
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [ERROR] No se encontro el entorno virtual en %VENV_DIR%
    echo Creando entorno virtual...
    python -m venv "%VENV_DIR%"
    call "%VENV_DIR%\Scripts\activate.bat"
    pip install -r "%PROJECT_DIR%\infra\requirements_backend.txt"
)

:: ── Compilar frontend si no existe dist ─────────────────────────
if not exist "%FRONTEND_DIR%\dist\index.html" (
    echo.
    echo [SIMCO] Compilando frontend...
    cd /d "%FRONTEND_DIR%"
    call npm install
    call npm run build

if errorlevel 1 (
    echo [ERROR] Fallo la compilacion del frontend
    pause
    exit /b 1
)

echo [SIMCO] Frontend compilado correctamente.
)

:: ── Cargar variables de entorno ───────────────────────────────
if exist "%ENV_FILE%" (
    echo [SIMCO] Cargando configuracion desde .env.production
    for /f "usebackq tokens=1,* delims==" %%a in ("%ENV_FILE%") do (
        set "%%a=%%b"
    )
)

:: ── Iniciar Backend ────────────────────────────────────────────
echo.
echo ════════════════════════════════════════════════════════════
echo   SIMCO - Iniciando servidor en puerto %BACKEND_PORT%
echo   URL: http://localhost:%BACKEND_PORT%
echo ════════════════════════════════════════════════════════════
echo.

cd /d "%BACKEND_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"

where pg_isready >nul 2>&1

if errorlevel 1 (
    echo [INFO] pg_isready no esta instalado o no esta en el PATH.
) else (
    pg_isready -h localhost -p 5432 >nul 2>&1
    if errorlevel 1 (
        echo [ADVERTENCIA] PostgreSQL no responde en localhost:5432
    )
)

:: Verificar si PostgreSQL está corriendo (intenta conectar)
pg_isready -h localhost -p 5432 >nul 2>&1
if errorlevel 1 (
    echo [ADVERTENCIA] PostgreSQL no parece estar corriendo en localhost:5432
    echo Asegurate de que el servicio de PostgreSQL este iniciado.
    echo.
)

:: Ejecutar uvicorn SIN --reload (producción)
start "SIMCO Backend" /B uvicorn app.main:app --host 0.0.0.0 --port %BACKEND_PORT%

:: Esperar a que el backend esté listo
echo [SIMCO] Esperando a que el backend inicie...
timeout /t 3 /nobreak >nul

:: Verificar que está corriendo
curl -s http://localhost:%BACKEND_PORT%/api/health >nul 2>&1
if errorlevel 1 (
    echo [ERROR] El backend no pudo iniciar. Revisa los logs arriba.
    pause
    exit /b 1
)

echo [SIMCO] Backend iniciado correctamente.
echo.
:: Mostrar IP local para acceso en la misma red
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /C:"IPv4"') do (
    set LOCAL_IP=%%i
)
set LOCAL_IP=%LOCAL_IP: =%
if defined LOCAL_IP (
    echo URL red local: http://%LOCAL_IP%:%BACKEND_PORT%
)
echo URL local:     http://localhost:%BACKEND_PORT%
if defined PUBLIC_URL (
    echo URL publica:   %PUBLIC_URL%
)
echo.
echo Presiona Ctrl+C para detener el servidor.
echo.

:: Mantener el script abierto
cmd /k

@echo off
title SIMCO - Desarrollo (hot reload)
cd /d "C:\proyectos\simco_v01"

:: ── Matar procesos previos ──
echo [SIMCO] Deteniendo procesos anteriores...
taskkill /f /im uvicorn.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 1 /nobreak >nul

:: ── Iniciar Backend (ventana propia) ──
echo [SIMCO] Iniciando backend en http://localhost:8000 ...
start "SIMCO Backend" cmd /c "cd /d backend && ..\backend\venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

:: ── Iniciar Frontend (ventana propia) ──
echo [SIMCO] Iniciando frontend en http://localhost:5173 ...
start "SIMCO Frontend" cmd /c "cd /d frontend && npm run dev"

:: ── Mostrar IP local ──
timeout /t 2 /nobreak >nul
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /R "^[[:space:]]*IPv4"') do set LOCAL_IP=%%i
set LOCAL_IP=%LOCAL_IP: =%

cls
echo.
echo ============================================
echo   SIMCO - Modo Desarrollo ACTIVO
echo ============================================
echo   Backend API: http://localhost:8000
echo   Frontend:    http://localhost:5173
if defined LOCAL_IP (
    echo   Red local:   http://%LOCAL_IP%:5173
)
echo   Swagger:     http://localhost:8000/docs
echo --------------------------------------------
echo   Hot reload activo:
echo   - Cambios en .tsx - recarga automatica
echo   - Cambios en .py  - recarga automatica
echo ============================================
echo.
echo   Para detener: cerrar las 2 ventanas
echo   (Backend / Frontend)
echo.
pause

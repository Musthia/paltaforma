@echo off
title Plataforma Unificada DATCORR + SIMCO
cd /d "%~dp0"

echo ========================================
echo   Plataforma Unificada DATCORR + SIMCO
echo ========================================
echo.

:: Kill existing processes
echo [+] Deteniendo procesos previos...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr /c:":8000 " ^| findstr /c:"LISTENING"') do taskkill /f /pid %%a >nul 2>&1
taskkill /f /im uvicorn.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 3 /nobreak >nul

:: Check arguments
set PORT=8000
set DEV_MODE=
set FRONTEND=

:parse
if "%1"=="" goto :start
if /i "%1"=="--dev" set DEV_MODE=--reload
if /i "%1"=="--port" set PORT=%2
if /i "%1"=="--frontend" set FRONTEND=1
shift
goto :parse

:start
:: Start backend unificado
echo [+] Iniciando backend unificado (puerto %PORT%)...
cd /d "%~dp0data_datcorr"
start "Plataforma Backend" /B cmd /c "python -m uvicorn backend.main_unificado:app --host 0.0.0.0 --port %PORT% %DEV_MODE%"
timeout /t 3 /nobreak >nul

:: Optional: Start DATCORR frontend
if "%FRONTEND%"=="1" (
    echo [+] Iniciando frontend DATCORR (puerto 5173)...
    start "Frontend DATCORR" /B cmd /c "cd /d "%~dp0data_datcorr\frontend" && npm run dev"
    timeout /t 4 /nobreak >nul
)

:: Show info
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "127.0.0.1"') do set IP=%%i
if not defined IP set IP=localhost

echo.
echo ========================================
echo   Plataforma iniciada!
echo ========================================
echo   API:        http://%IP%:%PORT%
echo   Docs:       http://%IP%:%PORT%/docs
echo   Health:     http://%IP%:%PORT%/health
if "%FRONTEND%"=="1" echo   Frontend DC: http://localhost:5173
echo.
echo   Para detener: .\detener_plataforma.bat
echo ========================================

cd /d "%~dp0"
cmd /k

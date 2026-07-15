@echo off
title SIMCO - Detener

echo [SIMCO] Deteniendo procesos...
taskkill /f /im uvicorn.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im cloudflared.exe >nul 2>&1

echo [SIMCO] Todos los procesos detenidos.
timeout /t 2 /nobreak >nul

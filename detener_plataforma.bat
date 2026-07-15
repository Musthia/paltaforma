@echo off
title Plataforma - Detener
echo [+] Deteniendo plataforma...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im uvicorn.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo [OK] Plataforma detenida

@echo off
title QualiManager - Portable
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Lancement de QualiManager (Version Portable)              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

if not exist "output\Portable\QualiManager.exe" (
    echo ❌ ERREUR: Version portable non trouvée!
    echo.
    echo Veuillez d'abord compiler avec: python build_complete.py
    pause
    exit /b 1
)

echo ▶️ Démarrage de l'application...
echo.
start "" "output\Portable\QualiManager.exe"

timeout /t 2 /nobreak >nul
exit

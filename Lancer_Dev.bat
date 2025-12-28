@echo off
title QualiManager - Mode Développement
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Lancement de QualiManager (Mode Développement)            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo ▶️ Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo ▶️ Démarrage de l'application...
echo.
python app_erp.py

pause

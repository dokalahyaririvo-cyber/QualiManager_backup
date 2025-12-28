@echo off
REM Script pour relancer l'application proprement
echo Arret de tous les processus Python...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo Lancement de QualiManager ERP...
cd /d "%~dp0"
python app_erp.py

pause

@echo off
REM Lance la sauvegarde automatique en arrière-plan
echo Lancement de la sauvegarde automatique QualiManager...
echo.
echo Pour arrêter : Fermez la fenêtre ou appuyez sur Ctrl+C
echo.
start "Sauvegarde QualiManager" venv\Scripts\python.exe backup_auto.py

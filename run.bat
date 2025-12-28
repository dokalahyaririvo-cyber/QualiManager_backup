@echo off
chcp 65001 >nul
title QualiManager

:: Vérifier si l'environnement virtuel existe
if not exist "venv\Scripts\python.exe" (
    echo L'environnement virtuel n'existe pas.
    echo Veuillez d'abord exécuter install.bat
    pause
    exit /b 1
)

:: Lancer l'application
echo Démarrage de QualiManager...
venv\Scripts\python app.py

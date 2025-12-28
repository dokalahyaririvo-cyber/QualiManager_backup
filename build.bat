@echo off
chcp 65001 >nul
title QualiManager - Build Complet
color 0A

echo ═══════════════════════════════════════════════════════════
echo    QualiManager - Build Complet (Portable + Installateur)
echo ═══════════════════════════════════════════════════════════
echo.

:: Vérifier si l'environnement virtuel existe
if not exist "venv\Scripts\python.exe" (
    echo ❌ L'environnement virtuel n'existe pas.
    echo.
    echo Création de l'environnement virtuel...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    pip install pyinstaller
    echo.
    echo ✅ Environnement créé!
    echo.
)

:: Activer l'environnement virtuel
call venv\Scripts\activate.bat

:: Vérifier PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installation de PyInstaller...
    pip install pyinstaller
    echo.
)

:: Lancer le script de build complet
python build_complete.py

echo.
echo ═══════════════════════════════════════════════════════════
echo 💡 Les fichiers sont dans le dossier "output"
echo ═══════════════════════════════════════════════════════════

pause

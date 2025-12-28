@echo off
chcp 65001 >nul
title QualiManager - Installation

echo ═══════════════════════════════════════════════════════════
echo        QualiManager - Assistant d'Installation
echo ═══════════════════════════════════════════════════════════
echo.

:: Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installé ou pas dans le PATH.
    echo.
    echo Veuillez installer Python 3.10+ depuis:
    echo https://www.python.org/downloads/
    echo.
    echo Assurez-vous de cocher "Add Python to PATH" lors de l'installation.
    pause
    exit /b 1
)

echo [OK] Python détecté
python --version
echo.

:: Créer un environnement virtuel
echo [1/4] Création de l'environnement virtuel...
if exist "venv" (
    echo      Environnement virtuel existant trouvé.
) else (
    python -m venv venv
    echo      Environnement virtuel créé.
)
echo.

:: Activer l'environnement virtuel
echo [2/4] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
echo      Environnement activé.
echo.

:: Installer les dépendances
echo [3/4] Installation des dépendances...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
echo.
echo      Dépendances installées.
echo.

:: Créer les dossiers nécessaires
echo [4/4] Création des dossiers...
if not exist "data" mkdir data
if not exist "assets" mkdir assets
echo      Dossiers créés.
echo.

echo ═══════════════════════════════════════════════════════════
echo        INSTALLATION TERMINÉE AVEC SUCCÈS!
echo ═══════════════════════════════════════════════════════════
echo.
echo Pour lancer l'application:
echo   1. Double-cliquez sur "run.bat"
echo   OU
echo   2. Exécutez: venv\Scripts\python app.py
echo.
echo Identifiants par défaut:
echo   Email: admin@qualimanager.local
echo   Mot de passe: Admin@2024!
echo.
pause

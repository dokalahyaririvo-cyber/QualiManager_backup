@echo off
chcp 65001 >nul
title Test des deux versions QualiManager
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     Test des versions Portable et Installeur              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo 📋 CHECKLIST DE TEST
echo ═══════════════════
echo.
echo 1️⃣  VERSION PORTABLE
echo    • Lancer output\Portable\QualiManager.exe
echo    • Vérifier que l'onglet Veille fonctionne
echo    • Ajouter une donnée de test
echo    • Fermer et relancer pour vérifier la persistance
echo    • Vérifier que qualimanager_erp.db est DANS le dossier Portable
echo.
echo 2️⃣  VERSION INSTALLEUR
echo    • Compiler l'installeur avec Inno Setup
echo    • Installer l'application
echo    • Vérifier que l'onglet Veille fonctionne
echo    • Vérifier que les données sont dans %%APPDATA%%\QualiManager
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
echo.

:menu
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║               MENU DE TEST                                 ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo [1] Lancer VERSION PORTABLE
echo [2] Vérifier emplacement DB Portable
echo [3] Ouvrir dossier AppData (Installeur)
echo [4] Compiler Installeur (Inno Setup)
echo [5] Ouvrir dossier output\Installer
echo [Q] Quitter
echo.
set /p choice="Votre choix: "

if /i "%choice%"=="1" goto portable
if /i "%choice%"=="2" goto check_portable_db
if /i "%choice%"=="3" goto open_appdata
if /i "%choice%"=="4" goto compile_installer
if /i "%choice%"=="5" goto open_installer_folder
if /i "%choice%"=="Q" goto end
goto menu

:portable
echo.
echo 🚀 Lancement de la version PORTABLE...
echo.
if exist "output\Portable\QualiManager.exe" (
    start "" "output\Portable\QualiManager.exe"
    echo ✅ Version portable lancée
    echo.
    echo 📝 Points à vérifier:
    echo    • Onglet Veille accessible et fonctionnel
    echo    • Onglet Exigences accessible
    echo    • Ajouter une donnée de test dans Veille
    echo    • Fermer et relancer pour vérifier persistance
) else (
    echo ❌ Fichier non trouvé: output\Portable\QualiManager.exe
    echo    Lancez d'abord le build complet!
)
echo.
pause
goto menu

:check_portable_db
echo.
echo 📁 Vérification emplacement base de données PORTABLE...
echo.
if exist "output\Portable\qualimanager_erp.db" (
    echo ✅ Base de données trouvée dans output\Portable\
    echo.
    dir "output\Portable\qualimanager_erp.db"
    echo.
    echo 💡 C'est CORRECT pour la version portable!
    echo    Les données voyagent avec l'exe.
) else (
    echo ⚠️  Base de données non trouvée dans output\Portable\
    echo    Elle devrait être créée au premier lancement.
)
echo.
if exist "%APPDATA%\QualiManager\qualimanager_erp.db" (
    echo ⚠️  ATTENTION: Base trouvée aussi dans AppData
    echo    Ceci ne devrait PAS arriver en mode portable!
    echo.
    dir "%APPDATA%\QualiManager\qualimanager_erp.db"
)
echo.
pause
goto menu

:open_appdata
echo.
echo 📂 Ouverture dossier AppData (version Installeur)...
echo.
set appdata_path=%APPDATA%\QualiManager
if exist "%appdata_path%" (
    echo ✅ Dossier trouvé: %appdata_path%
    explorer "%appdata_path%"
) else (
    echo ⚠️  Dossier non trouvé: %appdata_path%
    echo    Il sera créé après installation de la version Installeur.
    echo.
    set /p create="Créer le dossier maintenant? (O/N): "
    if /i "%create%"=="O" (
        mkdir "%appdata_path%"
        mkdir "%appdata_path%\backups"
        echo ✅ Dossier créé
        explorer "%appdata_path%"
    )
)
echo.
pause
goto menu

:compile_installer
echo.
echo 💿 Compilation de l'installeur avec Inno Setup...
echo.

set iss_file=%CD%\QualiManager_Setup.iss
set iscc_path=C:\Program Files (x86)\Inno Setup 6\ISCC.exe

if not exist "%iss_file%" (
    echo ❌ Fichier .iss non trouvé: %iss_file%
    echo    Lancez d'abord le build complet!
    pause
    goto menu
)

if not exist "%iscc_path%" (
    echo ❌ Inno Setup non trouvé à: %iscc_path%
    echo.
    echo 📥 Téléchargez Inno Setup depuis:
    echo    https://jrsoftware.org/isdl.php
    pause
    goto menu
)

echo ✅ Fichier .iss trouvé
echo ✅ Inno Setup trouvé
echo.
echo 🔧 Compilation en cours...
"%iscc_path%" "%iss_file%"

if errorlevel 1 (
    echo.
    echo ❌ Erreur lors de la compilation
) else (
    echo.
    echo ✅ Installeur créé avec succès!
    echo.
    echo 📦 Fichier créé: output\Installer\QualiManager_v2.1.0_Setup.exe
    echo.
    set /p open_folder="Ouvrir le dossier? (O/N): "
    if /i "%open_folder%"=="O" explorer "output\Installer"
)
echo.
pause
goto menu

:open_installer_folder
echo.
echo 📂 Ouverture du dossier Installer...
if exist "output\Installer" (
    explorer "output\Installer"
) else (
    echo ❌ Dossier non trouvé: output\Installer
    echo    Lancez d'abord le build complet!
)
echo.
pause
goto menu

:end
echo.
echo 👋 Au revoir!
echo.
timeout /t 2 /nobreak >nul
exit /b

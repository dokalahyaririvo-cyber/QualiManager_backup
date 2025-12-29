@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ========================================
REM Script de sauvegarde automatique
REM QualiManager
REM ========================================

cd /d "%~dp0"
set "SOURCE=%CD%"
set "BACKUP_BASE=F:\Sauvegardes_QualiManager"
set "INTERVAL_HOURS=2"
set "KEEP_LAST=10"

echo.
echo ============================================================
echo   SAUVEGARDE AUTOMATIQUE QUALIMANAGER
echo ============================================================
echo Source      : %SOURCE%
echo Destination : %BACKUP_BASE%
echo Frequence   : Toutes les %INTERVAL_HOURS% heure(s)
echo ============================================================
echo.
echo Appuyez sur Ctrl+C pour arreter
echo.

:LOOP
    REM Créer un nom avec horodatage
    for /f "tokens=1-6 delims=/:. " %%a in ("%date% %time%") do (
        set "timestamp=%%c%%b%%a_%%d%%e%%f"
    )
    set "timestamp=!timestamp: =0!"
    
    set "BACKUP_DIR=%BACKUP_BASE%\QualiManager_Backup_!timestamp!"
    
    echo [%date% %time%] Debut de la sauvegarde...
    
    REM Créer le dossier de sauvegarde
    if not exist "%BACKUP_BASE%" mkdir "%BACKUP_BASE%"
    mkdir "!BACKUP_DIR!"
    
    REM Copier les fichiers (exclure build, output, exports, .git)
    xcopy "%SOURCE%\*.py" "!BACKUP_DIR!\" /Y /Q >nul
    xcopy "%SOURCE%\*.bat" "!BACKUP_DIR!\" /Y /Q >nul
    xcopy "%SOURCE%\*.md" "!BACKUP_DIR!\" /Y /Q >nul
    xcopy "%SOURCE%\*.txt" "!BACKUP_DIR!\" /Y /Q >nul
    xcopy "%SOURCE%\*.toml" "!BACKUP_DIR!\" /Y /Q >nul
    xcopy "%SOURCE%\*.iss" "!BACKUP_DIR!\" /Y /Q >nul
    xcopy "%SOURCE%\*.xlsx" "!BACKUP_DIR!\" /Y /Q >nul
    xcopy "%SOURCE%\*.ico" "!BACKUP_DIR!\" /Y /Q >nul
    
    REM Copier les dossiers importants
    if exist "%SOURCE%\flet_app" xcopy "%SOURCE%\flet_app" "!BACKUP_DIR!\flet_app\" /E /I /Y /Q >nul
    if exist "%SOURCE%\database" xcopy "%SOURCE%\database" "!BACKUP_DIR!\database\" /E /I /Y /Q >nul
    if exist "%SOURCE%\assets" xcopy "%SOURCE%\assets" "!BACKUP_DIR!\assets\" /E /I /Y /Q >nul
    if exist "%SOURCE%\data" xcopy "%SOURCE%\data" "!BACKUP_DIR!\data\" /E /I /Y /Q >nul
    
    echo OK Sauvegarde creee : !BACKUP_DIR!
    
    REM Nettoyer les anciennes sauvegardes (garder seulement les 10 dernières)
    set count=0
    for /f "skip=%KEEP_LAST% delims=" %%d in ('dir /b /ad /o-d "%BACKUP_BASE%\QualiManager_Backup_*" 2^>nul') do (
        echo   Suppression ancienne sauvegarde : %%d
        rd /s /q "%BACKUP_BASE%\%%d" 2>nul
    )
    
    echo.
    echo Prochaine sauvegarde dans %INTERVAL_HOURS% heure(s)...
    echo.
    
    REM Attendre X heures (converti en secondes)
    set /a "seconds=%INTERVAL_HOURS% * 3600"
    timeout /t %seconds% /nobreak >nul
    
goto LOOP

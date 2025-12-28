@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo   QualiManager - Compilation Installeur Inno Setup
echo ============================================================
echo.

cd output\Installer

if not exist "QualiManager_Setup.iss" (
    echo ERREUR: Fichier QualiManager_Setup.iss non trouve!
    pause
    exit /b 1
)

echo Compilation du script Inno Setup...
echo.

REM Chercher Inno Setup dans les emplacements communs
set INNO_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe
if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" set INNO_PATH=C:\Program Files (x86)\Inno Setup 5\ISCC.exe

if "%INNO_PATH%"=="" (
    echo ERREUR: Inno Setup non trouve!
    echo.
    echo Telechargez Inno Setup depuis: https://jrsoftware.org/isdl.php
    echo Installez-le et relancez ce script.
    pause
    exit /b 1
)

echo Inno Setup trouve: %INNO_PATH%
echo.

"%INNO_PATH%" QualiManager_Setup.iss

if %errorlevel% neq 0 (
    echo.
    echo ERREUR: Compilation echouee!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   INSTALLEUR CREE AVEC SUCCES!
echo ============================================================
echo.

if exist "QualiManager_v2.1.0_Setup.exe" (
    dir QualiManager_v2.1.0_Setup.exe | findstr /v "Directory"
    echo.
    echo Fichier pret a distribuer:
    echo   output\Installer\QualiManager_v2.1.0_Setup.exe
)

echo.
pause

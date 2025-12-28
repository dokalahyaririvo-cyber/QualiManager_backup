@echo off
chcp 65001 >nul
echo ========================================
echo Test QualiManager Portable
echo ========================================
echo.
echo Lancement de QualiManager.exe...
echo Si une erreur se produit, elle sera affichée ci-dessous.
echo.

cd /d "%~dp0"
if exist "output\Portable\QualiManager.exe" (
    "output\Portable\QualiManager.exe"
    echo.
    echo Code de sortie: %ERRORLEVEL%
) else if exist "dist\QualiManager.exe" (
    "dist\QualiManager.exe"
    echo.
    echo Code de sortie: %ERRORLEVEL%
) else (
    echo ERREUR: QualiManager.exe introuvable
)

echo.
pause

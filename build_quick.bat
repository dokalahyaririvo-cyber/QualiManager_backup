@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo   QualiManager - Build Complet (Portable + Installeur)
echo ============================================================
echo.

echo [1/5] Nettoyage...
rmdir /s /q build dist output 2>nul
del /q *.spec 2>nul
echo    OK

echo.
echo [2/5] Build Version PORTABLE (onefile)...
echo    Cela peut prendre 3-5 minutes...
venv\Scripts\pyinstaller.exe --onefile --windowed --name QualiManager --icon="assets\icon.ico" --add-data "database;database" --add-data "flet_app;flet_app" --add-data "assets;assets" --add-data "data;data" --hidden-import flet --hidden-import pandas --hidden-import openpyxl --hidden-import reportlab --hidden-import matplotlib --hidden-import flet_app.nc_page --hidden-import flet_app.inspections_page --hidden-import flet_app.analysis_page --hidden-import flet_app.lab_page --hidden-import flet_app.kpi_page --hidden-import flet_app.users_page --hidden-import flet_app.veille_page --hidden-import flet_app.layout --hidden-import flet_app.theme --hidden-import flet_app.db_manager --hidden-import flet_app.models --hidden-import flet_app.components --hidden-import flet_app.components_advanced --hidden-import database.db_manager --hidden-import database.auth_manager --hidden-import database.veille_db_manager --collect-all flet --noconfirm app_erp.py

if %errorlevel% neq 0 (
    echo    ERREUR: Build portable echoue!
    pause
    exit /b 1
)

echo    OK Version portable creee

echo.
echo [3/5] Organisation fichiers Portable...
mkdir output\Portable 2>nul
copy dist\QualiManager.exe output\Portable\
copy qualimanager_erp.db output\Portable\ 2>nul
echo    OK

echo.
echo [4/5] Build Version INSTALLEUR (onedir)...
echo    Cela peut prendre 2-3 minutes...
venv\Scripts\pyinstaller.exe --onedir --windowed --name QualiManager --icon="assets\icon.ico" --add-data "database;database" --add-data "flet_app;flet_app" --add-data "assets;assets" --add-data "data;data" --hidden-import flet --hidden-import pandas --hidden-import openpyxl --hidden-import reportlab --hidden-import matplotlib --hidden-import flet_app.nc_page --hidden-import flet_app.inspections_page --hidden-import flet_app.analysis_page --hidden-import flet_app.lab_page --hidden-import flet_app.kpi_page --hidden-import flet_app.users_page --hidden-import flet_app.veille_page --hidden-import flet_app.layout --hidden-import flet_app.theme --hidden-import flet_app.db_manager --hidden-import flet_app.models --hidden-import flet_app.components --hidden-import flet_app.components_advanced --hidden-import database.db_manager --hidden-import database.auth_manager --hidden-import database.veille_db_manager --collect-all flet --noconfirm app_erp.py

if %errorlevel% neq 0 (
    echo    ERREUR: Build installeur echoue!
    pause
    exit /b 1
)

echo    OK Version installeur creee

echo.
echo [5/6] Organisation fichiers Installeur...
mkdir output\Installer 2>nul
xcopy /E /I /Y dist\QualiManager output\Installer\QualiManager
copy qualimanager_erp.db output\Installer\QualiManager\ 2>nul
copy README.md output\Installer\ 2>nul
copy LICENSE.txt output\Installer\ 2>nul
copy GUIDE_MISE_A_JOUR.md output\Installer\ 2>nul
copy GUIDE_IMPORT_EXPORT_VEILLE.md output\Installer\ 2>nul
echo    OK

echo.
echo [6/6] Compilation Installeur Inno Setup...
call build_installer.bat

echo.
echo ============================================================
echo   BUILD COMPLET TERMINE!
echo ============================================================
echo.
echo Version PORTABLE:
dir output\Portable\*.exe | findstr /v "Directory"
echo.
echo Version INSTALLEUR (Dossier):
dir output\Installer\QualiManager\*.exe | findstr /v "Directory"
echo.
echo Setup INSTALLEUR:
dir output\Installer\*Setup.exe 2>nul | findstr /v "Directory"
echo.
echo ============================================================
pause

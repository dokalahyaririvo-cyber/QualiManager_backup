@echo off
cd /d "%~dp0"
echo Compilation de l'installateur...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "QualiManager_Setup.iss"
if exist "output\QualiManager_v2.1.0_Setup.exe" (
    echo.
    echo SUCCESS! Installateur cree:
    dir "output\QualiManager_v2.1.0_Setup.exe" /n
) else (
    echo.
    echo ECHEC - Installateur non cree
)
pause

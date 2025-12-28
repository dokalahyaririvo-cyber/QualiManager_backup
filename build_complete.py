# -*- coding: utf-8 -*-
"""
QualiManager - Build Complet
Génère version portable + installateur
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# Fix pour l'encodage console Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Configuration
APP_NAME = "QualiManager"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Gestion Qualité"
APP_DESCRIPTION = "Système ERP QHSE - Gestion de la Qualité"
MAIN_SCRIPT = "app_erp.py"
ICON_FILE = "assets/icon.ico" if os.path.exists("assets/icon.ico") else None

# Chemin vers PyInstaller dans l'environnement virtuel
VENV_PYINSTALLER = os.path.join("venv", "Scripts", "pyinstaller.exe")
if os.path.exists(VENV_PYINSTALLER):
    PYINSTALLER_CMD = VENV_PYINSTALLER
else:
    PYINSTALLER_CMD = "pyinstaller"  # Fallback vers PATH système

def print_step(message):
    """Affiche une étape du processus."""
    print(f"\n{'='*60}")
    print(f"  {message}")
    print(f"{'='*60}")

def clean_build():
    """Nettoie les dossiers de build précédents."""
    print_step("🧹 Nettoyage des builds précédents")
    folders_to_clean = ['build', 'dist', '__pycache__', 'output']
    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   ✓ Supprimé: {folder}")
    
    # Nettoyer les fichiers .spec
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"   ✓ Supprimé: {spec_file}")

def create_portable_version():
    """Crée la version portable (exécutable unique)."""
    print_step("📦 Création de la version PORTABLE")
    
    # Commande PyInstaller
    cmd = [
        PYINSTALLER_CMD,
        '--onefile',  # Un seul fichier exécutable
        '--windowed',  # Pas de console
        '--name', APP_NAME,
        '--icon', 'assets/icon.ico',  # Icône de l'exécutable
        '--version-file', 'version_info.txt',  # Métadonnées Windows
        '--add-data', 'database;database',
        '--add-data', 'flet_app;flet_app',
        '--add-data', 'assets;assets' if os.path.exists('assets') else '',
        '--add-data', 'data;data',
        '--hidden-import', 'flet',
        '--hidden-import', 'pandas',
        '--hidden-import', 'openpyxl',
        '--hidden-import', 'reportlab',
        '--hidden-import', 'matplotlib',
        '--hidden-import', 'flet_app',
        '--hidden-import', 'flet_app.nc_page',
        '--hidden-import', 'flet_app.inspections_page',
        '--hidden-import', 'flet_app.analysis_page',
        '--hidden-import', 'flet_app.lab_page',
        '--hidden-import', 'flet_app.kpi_page',
        '--hidden-import', 'flet_app.users_page',
        '--hidden-import', 'flet_app.veille_page',
        '--hidden-import', 'flet_app.layout',
        '--hidden-import', 'flet_app.theme',
        '--hidden-import', 'flet_app.db_manager',
        '--hidden-import', 'flet_app.models',
        '--hidden-import', 'flet_app.components',
        '--hidden-import', 'flet_app.components_advanced',
        '--hidden-import', 'database.db_manager',
        '--hidden-import', 'database.auth_manager',
        '--collect-all', 'flet',
        '--noconfirm',
    ]
    
    if ICON_FILE and os.path.exists(ICON_FILE):
        cmd.extend(['--icon', ICON_FILE])
    
    cmd.append(MAIN_SCRIPT)
    
    # Supprimer les entrées vides
    cmd = [c for c in cmd if c]
    
    print("Commande:", ' '.join(cmd))
    print("   En cours... (cela peut prendre quelques minutes)")
    result = subprocess.run(cmd)  # Enlever capture_output pour voir les logs en temps réel
    
    if result.returncode == 0:
        print("   ✅ Version portable créée avec succès!")
        return True
    else:
        print("   ❌ Erreur lors de la création")
        return False

def create_directory_version():
    """Crée la version avec dossier (plus rapide à lancer)."""
    print_step("📁 Création de la version DOSSIER")
    
    # Commande PyInstaller
    cmd = [
        PYINSTALLER_CMD,
        '--onedir',  # Dossier avec DLLs
        '--windowed',
        '--name', f'{APP_NAME}_Dir',
        '--icon', 'assets/icon.ico',  # Icône de l'exécutable
        '--version-file', 'version_info.txt',  # Métadonnées Windows
        '--add-data', 'database;database',
        '--add-data', 'flet_app;flet_app',
        '--add-data', 'assets;assets' if os.path.exists('assets') else '',
        '--add-data', 'data;data',
        '--hidden-import', 'flet',
        '--hidden-import', 'pandas',
        '--hidden-import', 'openpyxl',
        '--hidden-import', 'reportlab',
        '--hidden-import', 'matplotlib',
        '--hidden-import', 'flet_app',
        '--hidden-import', 'flet_app.nc_page',
        '--hidden-import', 'flet_app.inspections_page',
        '--hidden-import', 'flet_app.analysis_page',
        '--hidden-import', 'flet_app.lab_page',
        '--hidden-import', 'flet_app.kpi_page',
        '--hidden-import', 'flet_app.users_page',
        '--hidden-import', 'flet_app.veille_page',
        '--hidden-import', 'flet_app.layout',
        '--hidden-import', 'flet_app.theme',
        '--hidden-import', 'flet_app.db_manager',
        '--hidden-import', 'flet_app.models',
        '--hidden-import', 'flet_app.components',
        '--hidden-import', 'flet_app.components_advanced',
        '--hidden-import', 'database.db_manager',
        '--hidden-import', 'database.auth_manager',
        '--collect-all', 'flet',
        '--noconfirm',
    ]
    
    if ICON_FILE and os.path.exists(ICON_FILE):
        cmd.extend(['--icon', ICON_FILE])
    
    cmd.append(MAIN_SCRIPT)
    
    # Supprimer les entrées vides
    cmd = [c for c in cmd if c]
    
    print("Commande:", ' '.join(cmd))
    print("   En cours... (cela peut prendre quelques minutes)")
    result = subprocess.run(cmd)  # Enlever capture_output pour voir les logs en temps réel
    
    if result.returncode == 0:
        print("   ✅ Version dossier créée avec succès!")
        return True
    else:
        print("   ❌ Erreur lors de la création")
        return False

def create_portable_package():
    """Crée un package ZIP de la version portable."""
    print_step("📦 Création du package portable ZIP")
    
    portable_dir = Path('output') / 'Portable'
    portable_dir.mkdir(parents=True, exist_ok=True)
    
    # Copier l'exécutable
    exe_source = Path('dist') / f'{APP_NAME}.exe'
    if exe_source.exists():
        shutil.copy2(exe_source, portable_dir / f'{APP_NAME}.exe')
        print(f"   ✓ Copié: {APP_NAME}.exe")
    
    # Copier la base de données si elle existe
    if os.path.exists('qualimanager_erp.db'):
        shutil.copy2('qualimanager_erp.db', portable_dir / 'qualimanager_erp.db')
        print(f"   ✓ Copié: qualimanager_erp.db (avec données)")
    
    # Créer le dossier backups
    backups_dir = portable_dir / 'backups'
    backups_dir.mkdir(exist_ok=True)
    print(f"   ✓ Créé: dossier backups/")
    
    # Copier les fichiers nécessaires
    files_to_copy = [
        'README.md',
        'LICENSE.txt',
        'GUIDE_IMPORT_EXPORT_VEILLE.md',
        'GUIDE_MISE_A_JOUR.md',
        'Template_Import_Veilles.xlsx',
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, portable_dir / file)
            print(f"   ✓ Copié: {file}")
    
    # Créer un fichier README pour la version portable
    readme_portable = portable_dir / 'LANCEMENT.txt'
    readme_portable.write_text(f"""
╔════════════════════════════════════════════════════════════╗
║  {APP_NAME} - Version Portable                            ║
║  Version {APP_VERSION}                                     ║
╚════════════════════════════════════════════════════════════╝

📌 LANCEMENT DIRECT - SANS INSTALLATION

1. Double-cliquez sur {APP_NAME}.exe
2. L'application démarre directement
3. Aucune installation nécessaire

💾 DONNÉES
- La base de données est dans le même dossier: qualimanager_erp.db
- Les sauvegardes automatiques dans: backups/
- Vous pouvez déplacer tout ce dossier sur une clé USB

🔄 MISE À JOUR
- Consultez GUIDE_MISE_A_JOUR.md pour les instructions détaillées
- Pour mettre à jour: remplacer UNIQUEMENT {APP_NAME}.exe
- Ne jamais toucher à qualimanager_erp.db (vos données!)

✅ AVANTAGES
+ Aucune installation
+ Portable (clé USB, réseau)
+ Aucun administrateur requis
+ Suppression simple (supprimer le dossier)

⚠️ REMARQUES
- Premier lancement plus lent (extraction des ressources)
- Fichier plus volumineux
- Peut être bloqué par certains antivirus (faux positif)

📞 SUPPORT
En cas de problème, consultez README.md et GUIDE_MISE_A_JOUR.md
""", encoding='utf-8')
    
    print(f"   ✓ Créé: LANCEMENT.txt")
    
    # Créer un ZIP
    timestamp = datetime.now().strftime("%Y%m%d")
    zip_name = f'{APP_NAME}_v{APP_VERSION}_Portable_{timestamp}'
    shutil.make_archive(f'output/{zip_name}', 'zip', portable_dir)
    print(f"   ✅ Package créé: output/{zip_name}.zip")

def create_installer_package():
    """Prépare les fichiers pour l'installateur."""
    print_step("💿 Préparation de l'installateur")
    
    installer_dir = Path('output') / 'Installer'
    installer_dir.mkdir(parents=True, exist_ok=True)
    
    # Copier le dossier dist complet
    dist_source = Path('dist') / f'{APP_NAME}_Dir'
    if dist_source.exists():
        dist_dest = installer_dir / APP_NAME
        if dist_dest.exists():
            shutil.rmtree(dist_dest)
        shutil.copytree(dist_source, dist_dest)
        print(f"   ✓ Copié: Dossier application")
    
    # Copier la base de données si elle existe
    if os.path.exists('qualimanager_erp.db'):
        shutil.copy2('qualimanager_erp.db', dist_dest / 'qualimanager_erp.db')
        print(f"   ✓ Copié: qualimanager_erp.db (avec données)")
    
    # Créer le dossier backups
    backups_dir = dist_dest / 'backups'
    backups_dir.mkdir(exist_ok=True)
    print(f"   ✓ Créé: dossier backups/")
    
    # Copier les fichiers supplémentaires
    files_to_copy = [
        'README.md',
        'LICENSE.txt',
        'GUIDE_IMPORT_EXPORT_VEILLE.md',
        'GUIDE_MISE_A_JOUR.md',
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, installer_dir / file)
            print(f"   ✓ Copié: {file}")
    
    print("   ✅ Fichiers préparés pour l'installateur")
    
    # Copier le script Inno Setup depuis la racine
    iss_source = Path('QualiManager_Setup.iss')
    if iss_source.exists():
        shutil.copy2(iss_source, installer_dir / 'QualiManager_Setup.iss')
        print(f"   ✓ Copié: QualiManager_Setup.iss")
    else:
        print("   ⚠️ ATTENTION: QualiManager_Setup.iss non trouvé à la racine!")
        # Créer le script Inno Setup si absent
        create_inno_script(installer_dir)

def create_inno_script(installer_dir):
    """Crée le script Inno Setup pour l'installateur."""
    print("   📝 Création du script Inno Setup...")
    
    script_content = f"""
; Script Inno Setup pour {APP_NAME}
; Généré automatiquement

#define MyAppName "{APP_NAME}"
#define MyAppVersion "{APP_VERSION}"
#define MyAppPublisher "{APP_AUTHOR}"
#define MyAppExeName "{APP_NAME}_Dir.exe"
#define MyAppAssocName "QualiManager File"
#define MyAppAssocExt ".qmdb"

[Setup]
AppId={{{{B8C9D1E2-3F4A-5B6C-7D8E-9F0A1B2C3D4E}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
DefaultDirName={{commonpf}}\\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=.
OutputBaseFilename={APP_NAME}_v{APP_VERSION}_Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"
Name: "quicklaunchicon"; Description: "Créer une icône dans la barre de lancement rapide"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
Source: "{APP_NAME}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.md"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "GUIDE_IMPORT_EXPORT_VEILLE.md"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{group}}\\Guide d'utilisation"; Filename: "{{app}}\\README.md"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{{app}}\\data"
Type: filesandordirs; Name: "{{app}}\\logs"
"""
    
    script_path = installer_dir / f'{APP_NAME}_Setup.iss'
    script_path.write_text(script_content, encoding='utf-8')
    print(f"   ✓ Script créé: {script_path}")
    print(f"\n   ⚙️ Pour créer l'installateur:")
    print(f"   1. Installez Inno Setup: https://jrsoftware.org/isdl.php")
    print(f"   2. Ouvrez: {script_path}")
    print(f"   3. Cliquez sur Build > Compile")

def create_launchers():
    """Crée des lanceurs pour les deux versions."""
    print_step("🚀 Création des lanceurs")
    
    # Lanceur portable
    portable_launcher = Path('Lancer_Portable.bat')
    portable_launcher.write_text(f"""@echo off
title {APP_NAME} - Portable
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Lancement de {APP_NAME} (Version Portable)              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

if not exist "output\\Portable\\{APP_NAME}.exe" (
    echo ❌ ERREUR: Version portable non trouvée!
    echo.
    echo Veuillez d'abord compiler avec: python build_complete.py
    pause
    exit /b 1
)

echo ▶️ Démarrage de l'application...
echo.
start "" "output\\Portable\\{APP_NAME}.exe"

timeout /t 2 /nobreak >nul
exit
""", encoding='utf-8')
    print(f"   ✓ Créé: {portable_launcher}")
    
    # Lanceur développement
    dev_launcher = Path('Lancer_Dev.bat')
    dev_launcher.write_text(f"""@echo off
title {APP_NAME} - Mode Développement
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Lancement de {APP_NAME} (Mode Développement)            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo ▶️ Activation de l'environnement virtuel...
call venv\\Scripts\\activate.bat

echo ▶️ Démarrage de l'application...
echo.
python {MAIN_SCRIPT}

pause
""", encoding='utf-8')
    print(f"   ✓ Créé: {dev_launcher}")

def main():
    """Fonction principale."""
    print("=" * 60)
    print(f"  {APP_NAME} - Build Complet")
    print(f"  Version {APP_VERSION}")
    print("=" * 60)
    print()
    
    # Vérifier PyInstaller
    try:
        import PyInstaller
        print("OK PyInstaller detecte")
    except ImportError:
        print("ERREUR PyInstaller non installe!")
        print("   Installation: pip install pyinstaller")
        return
    
    # Étapes de build
    try:
        # 1. Nettoyage
        clean_build()
        
        # 2. Version portable (onefile)
        if not create_portable_version():
            print("⚠️ Échec de la version portable, tentative de continuer...")
        
        # 3. Version dossier (onedir)
        if not create_directory_version():
            print("❌ Échec de la version dossier!")
            return
        
        # 4. Packages
        create_portable_package()
        create_installer_package()
        
        # 5. Lanceurs
        create_launchers()
        
        # Résumé final
        print_step("✅ BUILD TERMINÉ AVEC SUCCÈS")
        print(f"""
📦 FICHIERS CRÉÉS:

1️⃣ VERSION PORTABLE (sans installation)
   📁 output/Portable/{APP_NAME}.exe
   📦 output/{APP_NAME}_v{APP_VERSION}_Portable_*.zip
   
   ✨ Avantages:
   • Un seul fichier .exe
   • Aucune installation
   • Portable (clé USB, etc.)
   
   ⚠️ Inconvénients:
   • Premier lancement plus lent
   • Fichier plus volumineux (~50-100 MB)

2️⃣ VERSION INSTALLATEUR (avec installation)
   📁 output/Installer/{APP_NAME}/
   📝 output/Installer/{APP_NAME}_Setup.iss
   
   ✨ Avantages:
   • Installation propre dans Program Files
   • Désinstallation Windows standard
   • Lancement plus rapide
   • Raccourcis automatiques
   
   📝 Pour créer l'installateur:
   • Installez Inno Setup (gratuit)
   • Ouvrez le fichier .iss
   • Compilez!

🚀 LANCEURS:
   • Lancer_Portable.bat → Lance la version portable
   • Lancer_Dev.bat → Lance en mode développement

📖 DOCUMENTATION:
   • README.md
   • GUIDE_IMPORT_EXPORT_VEILLE.md
        """)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

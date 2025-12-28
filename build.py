# -*- coding: utf-8 -*-
"""
QualiManager - Script de build
Crée un exécutable Windows avec PyInstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Configuration
APP_NAME = "QualiManager"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Votre Entreprise"
APP_DESCRIPTION = "Système de Gestion Qualité"
MAIN_SCRIPT = "app.py"
ICON_FILE = "assets/icon.ico"

def clean_build():
    """Nettoie les dossiers de build précédents."""
    print("🧹 Nettoyage des builds précédents...")
    folders_to_clean = ['build', 'dist', '__pycache__']
    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   ✓ Supprimé: {folder}")
    
    # Nettoyer les fichiers .spec
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"   ✓ Supprimé: {spec_file}")

def check_dependencies():
    """Vérifie que les dépendances sont installées."""
    print("\n📦 Vérification des dépendances...")
    
    try:
        import flet
        print(f"   ✓ Flet {flet.__version__}")
    except ImportError:
        print("   ❌ Flet non installé. Installation...")
        subprocess.run([sys.executable, "-m", "pip", "install", "flet"])
    
    try:
        import PyInstaller
        print(f"   ✓ PyInstaller installé")
    except ImportError:
        print("   ❌ PyInstaller non installé. Installation...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

def create_assets_folder():
    """Crée le dossier assets avec une icône par défaut si nécessaire."""
    print("\n🎨 Préparation des assets...")
    
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    # Créer une icône placeholder si elle n'existe pas
    icon_path = assets_dir / "icon.ico"
    if not icon_path.exists():
        print("   ⚠️ Icône non trouvée. Utilisez assets/icon.ico pour personnaliser.")
        return None
    else:
        print(f"   ✓ Icône trouvée: {icon_path}")
        return str(icon_path)

def build_executable():
    """Compile l'application en exécutable."""
    print("\n🔨 Compilation de l'application...")
    
    icon = create_assets_folder()
    
    # Commande PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--onefile",  # Un seul fichier exe
        "--windowed",  # Pas de console
        "--clean",
        "--noconfirm",
        # Ajouter les données
        "--add-data", "flet_app;flet_app",
        "--add-data", "data;data",
        "--add-data", "database;database",
        # Imports cachés pour Flet
        "--hidden-import", "flet",
        "--hidden-import", "flet_runtime",
        "--hidden-import", "flet.fastapi",
        "--hidden-import", "flet_core",
        "--hidden-import", "flet_core.flet_core",
        "--hidden-import", "flet_runtime.flet_runtime",
        "--hidden-import", "sqlite3",
        "--hidden-import", "hashlib",
        "--hidden-import", "json",
        # Collecter tous les packages Flet
        "--collect-all", "flet",
        "--collect-all", "flet_core",
        "--collect-all", "flet_runtime",
    ]
    
    # Ajouter l'icône si elle existe
    if icon:
        cmd.extend(["--icon", icon])
    
    # Ajouter le script principal
    cmd.append(MAIN_SCRIPT)
    
    print(f"   Commande: {' '.join(cmd)}")
    print("\n   ⏳ Compilation en cours (cela peut prendre quelques minutes)...\n")
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print("\n   ✅ Compilation réussie!")
        return True
    else:
        print("\n   ❌ Erreur de compilation")
        return False

def create_installer_script():
    """Crée le script Inno Setup pour l'installeur Windows."""
    print("\n📝 Création du script d'installation Inno Setup...")
    
    inno_script = f'''; QualiManager - Script Inno Setup
; Généré automatiquement par build.py

#define MyAppName "{APP_NAME}"
#define MyAppVersion "{APP_VERSION}"
#define MyAppPublisher "{APP_AUTHOR}"
#define MyAppURL "https://www.qualimanager.local"
#define MyAppExeName "{APP_NAME}.exe"

[Setup]
AppId={{{{B8A3C7D9-1234-5678-9ABC-DEF012345678}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=README.md
OutputDir=installer
OutputBaseFilename={APP_NAME}_Setup_v{APP_VERSION}
SetupIconFile=assets\\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
Source: "dist\\{{#MyAppExeName}}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "data\\*"; DestDir: "{{app}}\\data"; Flags: ignoreversion recursesubdirs createallsubdirs; Permissions: users-modify
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{{group}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{group}}\\{{cm:UninstallProgram,{{#MyAppName}}}}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{{app}}\\data"
Type: filesandordirs; Name: "{{app}}\\logs"
'''
    
    with open("QualiManager.iss", "w", encoding="utf-8") as f:
        f.write(inno_script)
    
    print(f"   ✓ Script créé: QualiManager.iss")
    print("   💡 Compilez avec Inno Setup pour créer l'installeur Windows")

def create_license_file():
    """Crée un fichier LICENSE si nécessaire."""
    if not os.path.exists("LICENSE.txt"):
        license_text = f"""QualiManager - Système de Gestion Qualité
Version {APP_VERSION}

Copyright (c) 2024 {APP_AUTHOR}
Tous droits réservés.

Ce logiciel est fourni "tel quel", sans garantie d'aucune sorte, 
expresse ou implicite. En aucun cas, les auteurs ne pourront être 
tenus responsables de tout dommage résultant de l'utilisation de 
ce logiciel.

L'utilisation de ce logiciel est soumise aux conditions suivantes:
1. Ce logiciel ne peut être redistribué sans autorisation écrite.
2. Ce logiciel ne peut être modifié sans autorisation écrite.
3. Cette notice de licence doit être incluse dans toute copie.
"""
        with open("LICENSE.txt", "w", encoding="utf-8") as f:
            f.write(license_text)
        print("   ✓ Fichier LICENSE.txt créé")

def create_portable_version():
    """Crée une version portable (ZIP)."""
    print("\n📦 Création de la version portable...")
    
    dist_dir = Path("dist")
    if not dist_dir.exists() or not (dist_dir / f"{APP_NAME}.exe").exists():
        print("   ❌ Exécutable non trouvé. Compilez d'abord l'application.")
        return
    
    # Créer le dossier portable
    portable_dir = Path(f"dist/{APP_NAME}_Portable_v{APP_VERSION}")
    portable_dir.mkdir(exist_ok=True)
    
    # Copier l'exe
    shutil.copy(dist_dir / f"{APP_NAME}.exe", portable_dir)
    
    # Copier le dossier data
    if Path("data").exists():
        shutil.copytree("data", portable_dir / "data", dirs_exist_ok=True)
    else:
        (portable_dir / "data").mkdir(exist_ok=True)
    
    # Créer le fichier README portable
    readme_portable = f"""QualiManager v{APP_VERSION} - Version Portable
=============================================

UTILISATION:
1. Extrayez ce dossier où vous voulez
2. Double-cliquez sur {APP_NAME}.exe
3. La base de données sera créée dans le dossier 'data'

CONNEXION PAR DÉFAUT:
- Email: admin@qualimanager.local
- Mot de passe: Admin@2024!

NOTES:
- Cette version est portable et ne nécessite pas d'installation
- Toutes les données sont stockées dans le dossier 'data'
- Vous pouvez copier ce dossier sur une clé USB
"""
    with open(portable_dir / "LISEZ-MOI.txt", "w", encoding="utf-8") as f:
        f.write(readme_portable)
    
    # Créer le ZIP
    zip_name = f"{APP_NAME}_Portable_v{APP_VERSION}"
    shutil.make_archive(f"dist/{zip_name}", 'zip', "dist", f"{APP_NAME}_Portable_v{APP_VERSION}")
    
    print(f"   ✓ Version portable créée: dist/{zip_name}.zip")

def main():
    """Point d'entrée principal."""
    print("=" * 60)
    print(f"  {APP_NAME} - Build System v{APP_VERSION}")
    print("=" * 60)
    
    # Menu
    print("\nOptions disponibles:")
    print("  1. Build complet (nettoyer + compiler + portable)")
    print("  2. Compiler uniquement")
    print("  3. Créer version portable")
    print("  4. Créer script Inno Setup")
    print("  5. Nettoyer les builds")
    print("  0. Quitter")
    
    choice = input("\nVotre choix [1]: ").strip() or "1"
    
    if choice == "1":
        clean_build()
        check_dependencies()
        create_license_file()
        if build_executable():
            create_portable_version()
            create_installer_script()
            print("\n" + "=" * 60)
            print("  ✅ BUILD TERMINÉ AVEC SUCCÈS!")
            print("=" * 60)
            print(f"\n  📁 Fichiers créés dans 'dist/':")
            print(f"     • {APP_NAME}.exe - Exécutable")
            print(f"     • {APP_NAME}_Portable_v{APP_VERSION}.zip - Version portable")
            print(f"\n  📝 Pour créer l'installeur Windows:")
            print(f"     1. Installez Inno Setup (https://jrsoftware.org/isinfo.php)")
            print(f"     2. Ouvrez QualiManager.iss avec Inno Setup")
            print(f"     3. Compilez pour créer l'installeur")
    
    elif choice == "2":
        check_dependencies()
        build_executable()
    
    elif choice == "3":
        create_portable_version()
    
    elif choice == "4":
        create_license_file()
        create_installer_script()
    
    elif choice == "5":
        clean_build()
    
    elif choice == "0":
        print("Au revoir!")
    
    else:
        print("Option invalide")

if __name__ == "__main__":
    main()

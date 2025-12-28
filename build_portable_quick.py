"""
Script de build rapide - Version portable uniquement
Pour tester rapidement les corrections d'icône et de nom
"""
import subprocess
import sys
import os

def build_portable_only():
    """Build uniquement la version portable"""
    
    print("\n" + "="*60)
    print("  BUILD RAPIDE - VERSION PORTABLE UNIQUEMENT")
    print("="*60 + "\n")
    
    PYINSTALLER_CMD = os.path.join('venv', 'Scripts', 'pyinstaller.exe')
    APP_NAME = 'QualiManager'
    
    cmd = [
        PYINSTALLER_CMD,
        '--onefile',
        '--windowed',
        '--name', APP_NAME,
        '--icon', 'assets/icon.ico',
        '--version-file', 'version_info.txt',
        '--add-data', 'database;database',
        '--add-data', 'flet_app;flet_app',
        '--add-data', 'assets;assets',
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
        '--icon', 'assets/icon.ico',
        'app_erp.py'
    ]
    
    print("🔨 Lancement de PyInstaller...")
    print("⏱️  Temps estimé : 3-5 minutes\n")
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print("\n✅ Build réussi!")
        print(f"📁 Fichier créé : dist\\{APP_NAME}.exe")
        
        # Copier vers output/Portable
        import shutil
        output_dir = os.path.join('output', 'Portable')
        os.makedirs(output_dir, exist_ok=True)
        
        src = os.path.join('dist', f'{APP_NAME}.exe')
        dst = os.path.join(output_dir, f'{APP_NAME}.exe')
        
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"✅ Copié vers : {dst}")
            
            # Afficher la taille
            size_mb = os.path.getsize(dst) / (1024 * 1024)
            print(f"💾 Taille : {size_mb:.1f} MB")
    else:
        print("\n❌ Échec du build")
        return False
    
    return True

if __name__ == "__main__":
    success = build_portable_only()
    sys.exit(0 if success else 1)

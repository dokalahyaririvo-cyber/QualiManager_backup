"""
Build avec flet pack - Solution officielle pour Flet
Gère correctement l'icône et le nom dans la taskbar
"""
import subprocess
import sys
import os
import shutil

def build_with_flet_pack():
    """Build avec flet pack au lieu de PyInstaller"""
    
    print("\n" + "="*60)
    print("  BUILD AVEC FLET PACK")
    print("  Solution officielle pour icône et nom corrects")
    print("="*60 + "\n")
    
    # Vérifier que flet est installé
    try:
        import flet
        print(f"✓ Flet installé")
    except ImportError:
        print("❌ Flet non installé")
        return False
    
    # Build version portable (onefile)
    print("\n🔨 Build version PORTABLE...")
    cmd_portable = [
        sys.executable, '-m', 'flet', 'pack',
        'app_erp.py',
        '--name', 'QualiManager',
        '--product-name', 'QualiManager - Gestion Qualité QHSE',
        '--product-version', '2.1.0',
        '--file-description', 'QualiManager - Gestion Qualité QHSE',
        '--icon', 'assets/icon.ico',
        '--add-data', 'database;database',
        '--add-data', 'flet_app;flet_app',
        '--add-data', 'assets;assets',
        '--add-data', 'data;data',
    ]
    
    result = subprocess.run(cmd_portable)
    
    if result.returncode == 0:
        print("\n✅ Build portable réussi!")
        
        # Copier vers output/Portable
        output_dir = 'output/Portable'
        os.makedirs(output_dir, exist_ok=True)
        
        src = 'dist/QualiManager.exe'
        dst = os.path.join(output_dir, 'QualiManager.exe')
        
        if os.path.exists(src):
            shutil.copy2(src, dst)
            size_mb = os.path.getsize(dst) / (1024 * 1024)
            print(f"✅ Copié vers: {dst}")
            print(f"💾 Taille: {size_mb:.1f} MB\n")
            
            # Copier aussi la DB et autres fichiers
            files_to_copy = [
                ('database/qualimanager_erp.db', 'qualimanager_erp.db'),
                ('README.md', 'README.md'),
                ('LICENSE.txt', 'LICENSE.txt'),
            ]
            
            for src_file, dst_file in files_to_copy:
                if os.path.exists(src_file):
                    shutil.copy2(src_file, os.path.join(output_dir, dst_file))
            
            # Créer dossier backups
            os.makedirs(os.path.join(output_dir, 'backups'), exist_ok=True)
            
            return True
    else:
        print("\n❌ Échec du build")
        return False

if __name__ == "__main__":
    success = build_with_flet_pack()
    
    if success:
        print("\n" + "="*60)
        print("  ✅ BUILD TERMINÉ")
        print("="*60)
        print("\nFichier créé: output/Portable/QualiManager.exe")
        print("\n⚠️  IMPORTANT:")
        print("Avec flet pack, l'icône et le nom sont corrects dans la taskbar!")
        print("\nTestez maintenant:")
        print("1. Lancez output/Portable/QualiManager.exe")
        print("2. Faites clic droit > Pin to taskbar")
        print("3. Vérifiez que le nom et l'icône sont corrects\n")
    
    sys.exit(0 if success else 1)

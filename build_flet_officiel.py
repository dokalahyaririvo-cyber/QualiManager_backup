"""
BUILD PROFESSIONNEL avec flet build - Méthode Officielle
Résout définitivement le problème d'icône et de nom dans la taskbar
"""
import subprocess
import sys
import os
import shutil
import time

def build_with_flet_official():
    """Build avec la méthode officielle flet build windows"""
    
    print("\n" + "="*80)
    print("  BUILD PROFESSIONNEL - MÉTHODE OFFICIELLE FLET")
    print("  Résout le problème d'icône et de nom dans la taskbar")
    print("="*80 + "\n")
    
    # Vérifier que pyproject.toml existe
    if not os.path.exists('pyproject.toml'):
        print("❌ pyproject.toml manquant")
        return False
    
    print("📋 Configuration:")
    print("   • Produit: QualiManager - Gestion Qualité QHSE")
    print("   • Version: 2.1.0")
    print("   • Icône: assets/icon_windows.png")
    print("   • Méthode: flet build windows\n")
    
    # Préparer l'icône pour Windows (copier icon.ico comme PNG si nécessaire)
    if os.path.exists('assets/icon.ico') and not os.path.exists('assets/icon_windows.png'):
        print("ℹ️  Conversion de icon.ico en icon_windows.png...")
        # Pour Flet, on peut aussi utiliser .ico directement
        # Mais PNG est recommandé dans la doc
        # On va créer une copie
        if os.path.exists('assets/icon.png'):
            shutil.copy('assets/icon.png', 'assets/icon_windows.png')
            print("   ✓ icon_windows.png créé\n")
    
    # BUILD VERSION WINDOWS (Portable exe)
    print("🔨 Phase 1: Build version PORTABLE (Windows EXE)...\n")
    print("   ⏱️  Durée estimée: 5-8 minutes")
    print("   📦 Flutter SDK sera téléchargé si nécessaire\n")
    
    start_time = time.time()
    
    # Utiliser flet CLI directement (pas python -m flet)
    flet_exe = os.path.join(os.path.dirname(sys.executable), 'flet.exe')
    
    cmd_windows = [
        flet_exe, 'build', 'windows',
        '--project', 'QualiManager',
        '--build-number', '1',
        '--build-version', '2.1.0',
        '--verbose'
    ]
    
    print(f"Commande: {' '.join(cmd_windows)}\n")
    
    try:
        result = subprocess.run(cmd_windows, check=True, capture_output=False, text=True)
        
        elapsed = time.time() - start_time
        print(f"\n✅ Build terminé en {int(elapsed//60)}min {int(elapsed%60)}s")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erreur lors du build: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        return False
    
    # Vérifier les fichiers créés
    build_dir = 'build/windows'
    if os.path.exists(build_dir):
        print(f"\n📁 Fichiers créés dans: {build_dir}")
        
        # Créer le dossier output si nécessaire
        os.makedirs('output/Portable', exist_ok=True)
        
        # Copier les résultats vers output/Portable
        print("\n📋 Copie vers output/Portable...")
        
        # Rechercher le exe
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                if file.endswith('.exe'):
                    src = os.path.join(root, file)
                    dst = os.path.join('output/Portable', file)
                    shutil.copy2(src, dst)
                    size_mb = os.path.getsize(dst) / (1024*1024)
                    print(f"   ✓ {file} ({size_mb:.1f} MB)")
        
        # Copier aussi les fichiers nécessaires
        for item in ['database', 'data', 'assets', 'qualimanager_erp.db']:
            src = item
            dst = os.path.join('output/Portable', item)
            if os.path.exists(src):
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                print(f"   ✓ {item}")
    
    return True

if __name__ == "__main__":
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║  BUILD AVEC MÉTHODE OFFICIELLE FLET                           ║")
    print("║  Cette méthode résout définitivement:                          ║")
    print("║  • Icône correcte dans la taskbar                              ║")
    print("║  • Nom correct (QualiManager - Gestion Qualité QHSE)          ║")
    print("║  • Fonctionne pour portable ET installer                       ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    success = build_with_flet_official()
    
    if success:
        print("\n" + "="*80)
        print("  ✅ BUILD TERMINÉ AVEC SUCCÈS")
        print("="*80)
        print("\n📦 Fichiers disponibles:")
        print("   • output/Portable/QualiManager.exe (ou autre nom selon build)")
        print("\n🎯 TESTS À FAIRE:")
        print("   1. Lancez l'exe depuis output/Portable")
        print("   2. Faites clic-droit sur l'icône taskbar > Pin to taskbar")
        print("   3. Vérifiez que l'icône ET le nom sont corrects!\n")
        print("⚠️  DIFFÉRENCE vs PyInstaller:")
        print("   flet build utilise Flutter et gère correctement les métadonnées Windows\n")
    else:
        print("\n❌ Le build a échoué")
        print("\nSi 'flet build' n'est pas disponible:")
        print("   pip install --upgrade flet")
        print("\nOu consultez: https://flet.dev/docs/publish/windows\n")
    
    sys.exit(0 if success else 1)

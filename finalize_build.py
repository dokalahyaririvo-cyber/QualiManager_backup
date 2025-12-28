"""
Script final : Build complet + Patch + Installateur
"""
import subprocess
import time
import os
import sys

def main():
    print("\n" + "="*70)
    print("  FINALISATION COMPLÈTE DU BUILD")
    print("="*70 + "\n")
    
    print("⏳ Attente de la fin du build en cours...")
    print("   (Vérification toutes les 30 secondes)\n")
    
    # Attendre que les fichiers soient créés
    max_wait = 600  # 10 minutes max
    waited = 0
    
    while waited < max_wait:
        # Vérifier si le portable existe
        portable_exists = os.path.exists('output/Portable/QualiManager.exe')
        installer_dir_exists = os.path.exists('dist/QualiManager_Dir/QualiManager_Dir.exe')
        
        if portable_exists and installer_dir_exists:
            print(f"\n✅ Build terminé ! (après {waited}s)")
            break
        
        if waited % 60 == 0 and waited > 0:
            print(f"   ⏰ {waited//60} minute(s) écoulée(s)...")
        
        time.sleep(30)
        waited += 30
    else:
        print("\n⚠️  Timeout - Le build prend plus de 10 minutes")
        print("Vérifiez le terminal build_complete.py pour voir où il en est.\n")
        return False
    
    # Étape 2: Patch fletd.exe
    print("\n" + "="*70)
    print("  ÉTAPE 2: PATCH DE FLETD.EXE")
    print("="*70 + "\n")
    
    result = subprocess.run([sys.executable, 'patch_fletd.py'])
    
    # Étape 3: Créer l'installateur Inno Setup
    print("\n" + "="*70)
    print("  ÉTAPE 3: CRÉATION DE L'INSTALLATEUR")
    print("="*70 + "\n")
    
    inno_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    iss_file = "QualiManager_Setup.iss"
    
    if os.path.exists(inno_path) and os.path.exists(iss_file):
        print(f"🔨 Compilation avec Inno Setup...")
        result = subprocess.run([inno_path, iss_file], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Installateur créé!\n")
        else:
            print(f"⚠️  Erreur Inno Setup")
            print("Compilez manuellement : ouvrez Compil32.exe et chargez QualiManager_Setup.iss\n")
    else:
        print("⚠️  Inno Setup non trouvé ou fichier .iss manquant")
        print("Pour créer l'installateur manuellement:")
        print(f"  1. Ouvrez: {inno_path}")
        print(f"  2. File > Open > {iss_file}")
        print("  3. Build > Compile\n")
    
    # Résumé final
    print("\n" + "="*70)
    print("  ✅ BUILD COMPLET TERMINÉ")
    print("="*70 + "\n")
    
    print("📦 FICHIERS CRÉÉS:\n")
    
    if os.path.exists('output/Portable/QualiManager.exe'):
        size = os.path.getsize('output/Portable/QualiManager.exe') / (1024*1024)
        print(f"✓ VERSION PORTABLE")
        print(f"   output/Portable/QualiManager.exe ({size:.1f} MB)\n")
    
    setup_file = 'output/QualiManager_v2.1.0_Setup.exe'
    if os.path.exists(setup_file):
        size = os.path.getsize(setup_file) / (1024*1024)
        print(f"✓ INSTALLATEUR")
        print(f"   {setup_file} ({size:.1f} MB)\n")
    else:
        print(f"⚠ INSTALLATEUR non créé")
        print(f"   Lancez manuellement Inno Setup avec QualiManager_Setup.iss\n")
    
    print("🧪 TESTS À FAIRE:\n")
    print("1. Version PORTABLE:")
    print("   • Lancez output/Portable/QualiManager.exe")
    print("   • Faites clic droit > Pin to taskbar")
    print("   • Vérifiez l'icône et le nom\n")
    
    print("2. Version INSTALLEUR:")
    print("   • Lancez l'installateur")
    print("   • Installez l'application")
    print("   • Épinglez à la taskbar")
    print("   • Vérifiez l'icône et le nom\n")
    
    print("⚠️  NOTE IMPORTANTE:")
    print("Si le nom affiche toujours 'flet description':")
    print("• C'est un problème inhérent à Flet (utilise fletd.exe)")
    print("• Solution: Épinglez PENDANT que l'app est ouverte")
    print("• Ou utilisez le raccourci du menu démarrer au lieu de l'exe direct\n")
    
    return True

if __name__ == "__main__":
    main()

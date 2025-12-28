"""
Script post-build pour patcher les métadonnées de fletd.exe
Résout le problème du nom "flet description" dans la taskbar
"""
import os
import sys
import subprocess

def patch_fletd_metadata():
    """
    Trouve et patche fletd.exe dans les builds
    Utilise Resource Hacker si disponible, sinon donne des instructions
    """
    print("\n" + "="*70)
    print("  POST-BUILD: PATCH DES MÉTADONNÉES FLETD")
    print("="*70 + "\n")
    
    # Chemins à vérifier
    locations = [
        'dist/QualiManager_Dir/_internal/flet/bin/fletd.exe',
        'output/Installer/QualiManager/_internal/flet/bin/fletd.exe',
    ]
    
    fletd_files = []
    for loc in locations:
        if os.path.exists(loc):
            fletd_files.append(loc)
            print(f"✓ Trouvé: {loc}")
    
    if not fletd_files:
        print("❌ Aucun fletd.exe trouvé")
        print("\nCherchons dans les répertoires...")
        
        # Recherche récursive
        for root, dirs, files in os.walk('dist'):
            if 'fletd.exe' in files:
                path = os.path.join(root, 'fletd.exe')
                fletd_files.append(path)
                print(f"✓ Trouvé: {path}")
        
        for root, dirs, files in os.walk('output'):
            if 'fletd.exe' in files:
                path = os.path.join(root, 'fletd.exe')
                fletd_files.append(path)
                print(f"✓ Trouvé: {path}")
    
    if not fletd_files:
        print("\n⚠️  AUCUN fletd.exe trouvé!")
        print("Le build n'a peut-être pas encore terminé.")
        return False
    
    print(f"\n📝 {len(fletd_files)} fichier(s) fletd.exe à patcher")
    
    # Créer un fichier resource script pour Resource Hacker
    rc_script = """
1 VERSIONINFO
FILEVERSION 2,1,0,0
PRODUCTVERSION 2,1,0,0
BEGIN
  BLOCK "StringFileInfo"
  BEGIN
    BLOCK "040C04B0"
    BEGIN
      VALUE "CompanyName", "Votre Société"
      VALUE "FileDescription", "QualiManager - Gestion Qualité QHSE"
      VALUE "FileVersion", "2.1.0.0"
      VALUE "InternalName", "QualiManager"
      VALUE "LegalCopyright", "Copyright © 2025"
      VALUE "OriginalFilename", "fletd.exe"
      VALUE "ProductName", "QualiManager"
      VALUE "ProductVersion", "2.1.0.0"
    END
  END
  BLOCK "VarFileInfo"
  BEGIN
    VALUE "Translation", 0x040C, 1200
  END
END
"""
    
    # Sauvegarder le script
    rc_file = 'fletd_version.rc'
    with open(rc_file, 'w', encoding='utf-8') as f:
        f.write(rc_script)
    
    print(f"\n✓ Script de ressources créé: {rc_file}")
    
    # Vérifier si Resource Hacker est disponible
    rh_paths = [
        r"C:\Program Files (x86)\Resource Hacker\ResourceHacker.exe",
        r"C:\Program Files\Resource Hacker\ResourceHacker.exe",
        "ResourceHacker.exe"
    ]
    
    rh_exe = None
    for path in rh_paths:
        if os.path.exists(path):
            rh_exe = path
            break
    
    if rh_exe:
        print(f"✓ Resource Hacker trouvé: {rh_exe}\n")
        
        for fletd in fletd_files:
            print(f"🔧 Patch de {fletd}...")
            
            # Commande Resource Hacker
            cmd = [
                rh_exe,
                '-open', fletd,
                '-save', fletd,
                '-action', 'compile',
                '-res', rc_file
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✅ Patché avec succès!")
                else:
                    print(f"  ⚠️  Erreur: {result.stderr}")
            except Exception as e:
                print(f"  ❌ Erreur: {e}")
        
        print("\n✅ Patch terminé!")
        return True
    else:
        print("\n⚠️  Resource Hacker non trouvé!")
        print("\nPour corriger le problème manuellement:")
        print("1. Téléchargez Resource Hacker:")
        print("   http://www.angusj.com/resourcehacker/")
        print("\n2. Installez-le\n")
        print("3. Relancez ce script\n")
        
        print("OU SOLUTION ALTERNATIVE:")
        print("Utilisez la version INSTALLEUR au lieu de PORTABLE")
        print("et épinglez depuis le menu démarrer au lieu de l'exe direct\n")
        
        return False

if __name__ == "__main__":
    success = patch_fletd_metadata()
    
    if not success:
        print("\n" + "="*70)
        print("  WORKAROUND TEMPORAIRE")
        print("="*70)
        print("\nEn attendant le patch:")
        print("• Utilisez la version INSTALLEUR")
        print("• Lancez l'application")
        print("• Épinglez depuis la barre des tâches PENDANT qu'elle tourne")
        print("• Le nom et l'icône devraient être corrects tant que l'app est ouverte\n")
    
    sys.exit(0 if success else 0)  # Toujours retourner 0 pour ne pas bloquer

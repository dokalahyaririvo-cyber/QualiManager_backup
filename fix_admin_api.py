"""Script pour corriger tous les problèmes d'API Flet 0.28 restants"""

import re
import os
from pathlib import Path

def fix_flet_api_in_file(filepath):
    """Corrige les problèmes d'API Flet 0.28 dans un fichier"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        changes = []
        
        # 1. padding=Padding(...) → padding=ft.Padding(...)
        pattern1 = r'\bpadding\s*=\s*Padding\('
        if re.search(pattern1, content):
            content = re.sub(pattern1, 'padding=ft.Padding(', content)
            changes.append("padding=Padding() -> padding=ft.Padding()")
        
        # 2. margin=Margin(...) → margin=ft.Margin(...)
        pattern2 = r'\bmargin\s*=\s*Margin\('
        if re.search(pattern2, content):
            content = re.sub(pattern2, 'margin=ft.Margin(', content)
            changes.append("margin=Margin() -> margin=ft.Margin()")
        
        # 3. border_radius=BorderRadius(...) → border_radius=ft.BorderRadius(...)
        pattern3 = r'\bborder_radius\s*=\s*BorderRadius\('
        if re.search(pattern3, content):
            content = re.sub(pattern3, 'border_radius=ft.BorderRadius(', content)
            changes.append("border_radius=BorderRadius() -> border_radius=ft.BorderRadius()")
        
        # 4. border=Border(...) → border=ft.Border(...)
        pattern4 = r'\bborder\s*=\s*Border\('
        if re.search(pattern4, content):
            content = re.sub(pattern4, 'border=ft.Border(', content)
            changes.append("border=Border() -> border=ft.Border()")
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes
        return False, []
        
    except Exception as e:
        print(f"Erreur dans {filepath}: {e}")
        return False, []

def main():
    """Corrige tous les fichiers Python dans flet_app"""
    flet_app_dir = Path("flet_app")
    files_fixed = []
    total_changes = 0
    
    print("=" * 70)
    print("CORRECTION API FLET 0.28 - ADMINISTRATION")
    print("=" * 70)
    
    # Priorité aux fichiers administration
    priority_files = [
        "users_page.py",
        "pages.py",
        "components.py",
        "components_advanced.py",
        "layout.py",
        "theme.py",
    ]
    
    # Traiter les fichiers prioritaires
    print("\n[1/2] Traitement fichiers prioritaires...")
    for filename in priority_files:
        filepath = flet_app_dir / filename
        if filepath.exists():
            fixed, changes = fix_flet_api_in_file(filepath)
            if fixed:
                files_fixed.append(str(filepath))
                total_changes += len(changes)
                print(f"  [OK] {filename}")
                for change in changes:
                    print(f"       - {change}")
    
    # Traiter tous les autres fichiers
    print("\n[2/2] Traitement fichiers restants...")
    for py_file in flet_app_dir.rglob("*.py"):
        if py_file.name not in priority_files:
            fixed, changes = fix_flet_api_in_file(py_file)
            if fixed:
                files_fixed.append(str(py_file))
                total_changes += len(changes)
                print(f"  [OK] {py_file.name}")
    
    print("\n" + "=" * 70)
    print(f"RESULTAT: {len(files_fixed)} fichiers corriges, {total_changes} corrections")
    print("=" * 70)
    
    if files_fixed:
        print("\nFichiers modifies:")
        for f in files_fixed:
            print(f"  - {f}")
    else:
        print("\nAucune correction necessaire.")

if __name__ == "__main__":
    main()

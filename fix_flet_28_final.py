"""Correction FINALE pour Flet 0.28"""
import os
import re

def fix_file(filepath):
    """Corrige un fichier pour Flet 0.28"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
        except:
            return False
    
    original = content
    
    # 1. ft.dropdown.Option → ft.Dropdown(...) avec minuscule pour Option
    content = re.sub(r'ft\.dropdown\.Option\(', 'ft.dropdown.Option(', content)
    
    # 2. ft.Alignment.CENTER et autres constantes en MAJUSCULES → minuscules
    alignment_map = {
        'CENTER': 'center',
        'TOP_LEFT': 'top_left',
        'TOP_CENTER': 'top_center',
        'TOP_RIGHT': 'top_right',
        'CENTER_LEFT': 'center_left',
        'CENTER_RIGHT': 'center_right',
        'BOTTOM_LEFT': 'bottom_left',
        'BOTTOM_CENTER': 'bottom_center',
        'BOTTOM_RIGHT': 'bottom_right',
        'START': 'start',
        'END': 'end',
        'SPACE_BETWEEN': 'space_between',
        'SPACE_AROUND': 'space_around',
        'SPACE_EVENLY': 'space_evenly',
    }
    
    for maj, min_val in alignment_map.items():
        content = re.sub(rf'ft\.Alignment\.{maj}\b', f'ft.alignment.{min_val}', content)
        content = re.sub(rf'ft\.MainAxisAlignment\.{maj}\b', f'ft.MainAxisAlignment.{maj}', content)
        content = re.sub(rf'ft\.CrossAxisAlignment\.{maj}\b', f'ft.CrossAxisAlignment.{maj}', content)
    
    # 3. ft.margin.xxx → utiliser directement les valeurs numériques ou ft.Margin()
    # Pour l'instant on laisse tel quel et on verra les erreurs
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

fixed = []
for root, dirs, files in os.walk('.'):
    if any(x in root for x in ['venv', 'dist', 'build', 'output', 'old_versions']):
        continue
    for file in files:
        if file.endswith('.py') and not file.startswith('fix_'):
            filepath = os.path.join(root, file)
            if fix_file(filepath):
                fixed.append(filepath)
                print(f"✅ {filepath}")

print(f"\n🎉 {len(fixed)} fichiers corrigés")

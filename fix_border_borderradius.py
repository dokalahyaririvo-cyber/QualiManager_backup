"""Correction Border.only et BorderRadius.only pour Flet 0.28"""
import os
import re

def fix_border_only(match):
    """Convertit ft.Border.only(...) en ft.Border() avec côtés spécifiques"""
    content = match.group(1)
    
    # Extraire les paramètres
    sides = {}
    for side in ['top', 'right', 'bottom', 'left']:
        pattern = rf'{side}\s*=\s*(ft\.BorderSide\([^)]+\))'
        side_match = re.search(pattern, content)
        if side_match:
            sides[side] = side_match.group(1)
    
    if not sides:
        return match.group(0)
    
    # Construire le nouveau Border
    parts = [f'{k}={v}' for k, v in sides.items()]
    return f'ft.Border({", ".join(parts)})'

def fix_border_radius_only(match):
    """Convertit ft.BorderRadius.only(...) en ft.border_radius.only(...)"""
    content = match.group(1)
    return f'ft.border_radius.only({content})'

fixed = []
for root, dirs, files in os.walk('./flet_app'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                continue
            
            original = content
            
            # Corriger ft.Border.only(...)
            content = re.sub(r'ft\.Border\.only\(([^)]+(?:\([^)]*\))?[^)]*)\)', fix_border_only, content)
            
            # Corriger ft.BorderRadius.only(...)
            content = re.sub(r'ft\.BorderRadius\.only\(([^)]+)\)', fix_border_radius_only, content)
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed.append(filepath)
                print(f"✅ {filepath}")

print(f"\n🎉 {len(fixed)} fichiers corrigés")

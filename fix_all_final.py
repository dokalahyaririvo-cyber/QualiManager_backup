"""Correction COMPLÈTE et FINALE pour Flet 0.28"""
import os
import re

def fix_border_only(match):
    """Convertit ft.Border.only(...) en ft.Border() avec côtés"""
    content = match.group(1)
    
    # Extraire les paramètres
    sides = {}
    for side in ['top', 'right', 'bottom', 'left']:
        # Pattern plus robuste pour capturer BorderSide
        pattern = rf'{side}\s*=\s*(ft\.BorderSide\([^)]+\))'
        side_match = re.search(pattern, content)
        if side_match:
            sides[side] = side_match.group(1)
    
    if not sides:
        return match.group(0)
    
    parts = [f'{k}={v}' for k, v in sides.items()]
    return f'ft.Border({", ".join(parts)})'

def fix_border_radius_only(match):
    """Convertit ft.border_radius.only() en ft.BorderRadius()"""
    content = match.group(1)
    
    # Extraire les corners
    corners = {}
    for corner in ['top_left', 'top_right', 'bottom_left', 'bottom_right']:
        pattern = rf'{corner}\s*=\s*(\d+)'
        corner_match = re.search(pattern, content)
        if corner_match:
            corners[corner] = corner_match.group(1)
    
    if not corners:
        return match.group(0)
    
    parts = [f'{k}={v}' for k, v in corners.items()]
    return f'ft.BorderRadius({", ".join(parts)})'

def fix_dropdown_option(content):
    """Supprime ft.dropdown.Option() car pas supporté en Flet 0.28"""
    # Remplacer ft.dropdown.Option("text") par "text"
    content = re.sub(r'ft\.dropdown\.Option\((["\'][^"\']+["\'])\)', r'\1', content)
    return content

fixed = []
for root, dirs, files in os.walk('.'):
    # Exclure venv, dist, build, output, old_versions
    if any(x in root for x in ['venv', 'dist', 'build', 'output', 'old_versions']):
        continue
        
    for file in files:
        if file.endswith('.py') and not file.startswith('fix_'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                try:
                    with open(filepath, 'r', encoding='latin-1') as f:
                        content = f.read()
                except:
                    continue
            
            original = content
            
            # 1. Corriger ft.Border.only(...)
            content = re.sub(r'ft\.Border\.only\(([^)]+(?:\([^)]*\))?[^)]*)\)', fix_border_only, content)
            
            # 2. Corriger ft.border_radius.only(...)
            content = re.sub(r'ft\.border_radius\.only\(([^)]+)\)', fix_border_radius_only, content)
            
            # 3. Corriger ft.BorderRadius.only(...) aussi
            content = re.sub(r'ft\.BorderRadius\.only\(([^)]+)\)', fix_border_radius_only, content)
            
            # 4. Corriger ft.dropdown.Option
            content = fix_dropdown_option(content)
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed.append(filepath)
                print(f"✅ {filepath}")

print(f"\n🎉 {len(fixed)} fichiers corrigés")

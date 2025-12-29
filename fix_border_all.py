"""Correction ft.border.all() pour Flet 0.28"""
import os
import re

def fix_border_all(match):
    """Convertit ft.border.all(width, color) en ft.Border avec 4 BorderSide"""
    args = match.group(1)
    # Chercher width et color
    parts = [p.strip() for p in args.split(',', 1)]
    if len(parts) == 2:
        width = parts[0]
        color = parts[1]
        return f'''ft.Border(
                top=ft.BorderSide({width}, {color}),
                right=ft.BorderSide({width}, {color}),
                bottom=ft.BorderSide({width}, {color}),
                left=ft.BorderSide({width}, {color}),
            )'''
    return match.group(0)

# Parcourir tous les fichiers Python dans flet_app
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
            
            # Remplacer ft.border.all(...)
            content = re.sub(r'ft\.border\.all\((.*?)\)', fix_border_all, content)
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ {filepath}")

print("✅ Terminé")

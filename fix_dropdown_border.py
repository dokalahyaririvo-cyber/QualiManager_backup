"""Correction finale ft.dropdown.Option et ft.border.all pour Flet 0.28"""
import os
import re

def fix_dropdown_option(content):
    """Remplace ft.dropdown.Option par une simple string (Flet 0.28 accepte les strings directement)"""
    # En Flet 0.28, on peut passer directement des strings comme options
    # Remplacer ft.dropdown.Option("text") par simplement "text"
    content = re.sub(r'ft\.dropdown\.Option\(([^)]+)\)', r'\1', content)
    return content

def fix_border_all_in_line(match):
    """Convertit ft.border.all(width, color) en ft.Border avec BorderSide"""
    args = match.group(1)
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
            
            # Corriger ft.dropdown.Option
            content = fix_dropdown_option(content)
            
            # Corriger ft.border.all
            content = re.sub(r'ft\.border\.all\(([^)]+)\)', fix_border_all_in_line, content)
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed.append(filepath)
                print(f"✅ {filepath}")

print(f"\n🎉 {len(fixed)} fichiers corrigés")

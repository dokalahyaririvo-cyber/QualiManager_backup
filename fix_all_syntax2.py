"""Correction complète syntaxe Flet 0.28 - Round 2"""
import os
import re

def fix_alignment_constants(content):
    """Convertit les valeurs d'alignement en majuscules"""
    alignments = ['center', 'start', 'end', 'space_between', 'space_around', 'space_evenly']
    for align in alignments:
        content = re.sub(rf'ft\.Alignment\.{align}\b', f'ft.Alignment.{align.upper()}', content)
        content = re.sub(rf'ft\.MainAxisAlignment\.{align}\b', f'ft.MainAxisAlignment.{align.upper()}', content)
        content = re.sub(rf'ft\.CrossAxisAlignment\.{align}\b', f'ft.CrossAxisAlignment.{align.upper()}', content)
    return content

corrections = [
    # Dropdown.Option doit rester minuscule
    (r'ft\.Dropdown\.Option', 'ft.dropdown.Option'),
    # Margin methods doivent rester minuscule
    (r'ft\.Margin\.symmetric\(', 'ft.margin.symmetric('),
    (r'ft\.Margin\.only\(', 'ft.margin.only('),
]

fixed = []
for root, dirs, files in os.walk('.'):
    if any(x in root for x in ['venv', 'dist', 'build', 'output', 'old_versions']):
        continue
    for file in files:
        if file.endswith('.py') and not file.startswith('fix_'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                continue
            
            original = content
            
            # Appliquer les corrections simples
            for pattern, replacement in corrections:
                content = re.sub(pattern, replacement, content)
            
            # Corriger les constantes d'alignement
            content = fix_alignment_constants(content)
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed.append(filepath)
                print(f"✅ {filepath}")

print(f"\n🎉 {len(fixed)} fichiers corrigés")

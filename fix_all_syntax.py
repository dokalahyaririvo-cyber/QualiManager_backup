"""Correction complète syntaxe Flet 0.28"""
import os
import re

corrections = [
    (r'ft\.alignment\.', 'ft.Alignment.'),
    (r'ft\.dropdown\.', 'ft.Dropdown.'),
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
            for pattern, replacement in corrections:
                content = re.sub(pattern, replacement, content)
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed.append(filepath)
                print(f"✅ {filepath}")

print(f"\n🎉 {len(fixed)} fichiers corrigés")

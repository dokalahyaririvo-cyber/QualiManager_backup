"""Correction des alignements pour Flet 0.28"""
import os

replacements = [
    ('ft.alignment.center', 'ft.Alignment(0, 0)'),
    ('ft.alignment.top_left', 'ft.Alignment(-1, -1)'),
    ('ft.alignment.bottom_center', 'ft.Alignment(0, 1)'),
    ('ft.Alignment.center_left', 'ft.Alignment(-1, 0)'),
    ('ft.Alignment.center_right', 'ft.Alignment(1, 0)'),
]

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
            for old, new in replacements:
                content = content.replace(old, new)
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ {filepath}")

print("✅ Terminé")

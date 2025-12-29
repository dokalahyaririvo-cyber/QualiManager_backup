"""Script pour trouver tous les emojis dans le code"""

import os
import re

def has_emoji(text):
    """Détecte les emojis dans une string"""
    # Pattern simple pour détecter les caractères non-ASCII
    return any(ord(char) > 127 and ord(char) not in range(192, 256) for char in text)

def scan_file(filepath):
    """Scanne un fichier pour les emojis"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        issues = []
        for i, line in enumerate(lines, 1):
            if has_emoji(line):
                # Trouver les caractères problématiques
                chars = [c for c in line if ord(c) > 127 and ord(c) not in range(192, 256)]
                if chars:
                    issues.append((i, line.strip(), chars))
        
        return issues
    except Exception as e:
        return []

# Scan flet_app directory
print("=" * 70)
print("RECHERCHE D'EMOJIS DANS FLET_APP")
print("=" * 70 + "\n")

for root, dirs, files in os.walk("flet_app"):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            issues = scan_file(filepath)
            if issues:
                print(f"\n{filepath}:")
                for line_num, line, chars in issues:
                    print(f"  Ligne {line_num}: {line[:80]}")
                    print(f"    Chars: {[hex(ord(c)) for c in chars]}")

# Scan app_erp.py
issues = scan_file("app_erp.py")
if issues:
    print(f"\napp_erp.py:")
    for line_num, line, chars in issues:
        print(f"  Ligne {line_num}: {line[:80]}")
        print(f"    Chars: {[hex(ord(c)) for c in chars]}")

print("\n" + "=" * 70)
print("FIN DE L'ANALYSE")
print("=" * 70)

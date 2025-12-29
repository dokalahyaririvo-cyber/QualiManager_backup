"""Script pour créer un fichier listant tous les emojis restants"""
import os
import re

def find_problematic_chars(text):
    """Trouve les caractères qui pourraient causer des problèmes d'encodage"""
    problematic = []
    for i, char in enumerate(text):
        code = ord(char)
        # Caractères > 127 sauf les caractères latins étendus (192-255)
        if code > 127:
            # Exclure les caractères français courants
            if code not in [192, 194, 199, 200, 201, 202, 203, 206, 207, 212, 217, 219, 224, 226, 231, 232, 233, 234, 235, 238, 239, 244, 249, 251]:
                problematic.append((i, char, code, hex(code)))
    return problematic

def scan_file(filepath):
    """Scanne un fichier"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        results = []
        for line_num, line in enumerate(lines, 1):
            prob = find_problematic_chars(line)
            if prob:
                results.append((line_num, line.strip(), prob))
        return results
    except:
        return []

print("=" * 80)
print("RECHERCHE DE CARACTÈRES PROBLÉMATIQUES")
print("=" * 80)

files_to_check = []
for root, dirs, files in os.walk("flet_app"):
    for file in files:
        if file.endswith('.py'):
            files_to_check.append(os.path.join(root, file))

files_to_check.append("app_erp.py")

total_issues = 0
for filepath in sorted(files_to_check):
    results = scan_file(filepath)
    if results:
        print(f"\n{filepath}:")
        for line_num, line, chars in results:
            print(f"  Ligne {line_num}: {line[:80]}")
            for pos, char, code, hex_code in chars:
                print(f"    Position {pos}: '{char}' (code={code}, hex={hex_code})")
            total_issues += len(chars)

print(f"\n{'=' * 80}")
print(f"TOTAL: {total_issues} caractère(s) problématique(s) trouvé(s)")
print("=" * 80)

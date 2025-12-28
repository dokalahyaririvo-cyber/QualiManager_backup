# -*- coding: utf-8 -*-
"""Correction de la f-string ligne 308"""

# Lire le fichier
with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remplacer la ligne incorrecte
old_line = 'f"{alerte.laboratoire.value} " - {alerte.conclusion.value}",'
new_line = 'f"{alerte.laboratoire.value} - {alerte.conclusion.value}",'

content = content.replace(old_line, new_line)

# Sauvegarder
with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ F-string corrigée ligne 308")

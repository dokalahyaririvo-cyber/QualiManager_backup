# -*- coding: utf-8 -*-
"""Correction du caractère cent invalide"""

# Lire le fichier
with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remplacer le caractère cent par un tiret
content = content.replace('"¢', '" -')

# Sauvegarder
with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Caractère ¢ corrigé")

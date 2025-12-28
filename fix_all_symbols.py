# -*- coding: utf-8 -*-
"""Correction complète de TOUS les symboles et emojis mal encodés"""
import re

# Lire le fichier
with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Supprimer tous les emojis mal encodés (ðŸ suivi de caractères)
old_content = content
content = re.sub(r'ðŸ[^\s"]+\s*', '', content)
emoji_count = len(old_content) - len(content)
if emoji_count > 0:
    print(f"  ✓ Supprimé {emoji_count} caractères d'emojis mal encodés")

# Supprimer le symbole d'alerte mal encodé
content = content.replace('âš ï¸', '⚠️')
content = content.replace('â€¢', '•')

# Caractères accentués mal encodés
replacements = [
    ('Ã©', 'é'),
    ('Ã¨', 'è'),
    ('Ã ', 'à'),
    ('Ã§', 'ç'),
    ('Ã´', 'ô'),
    ('Ã»', 'û'),
    ('Ã¢', 'â'),
    ('Ã®', 'î'),
    ('Ã«', 'ë'),
    ('Ã¯', 'ï'),
    ('Ã¹', 'ù'),
    ('Ãª', 'ê'),
    ('Ã‰', 'É'),
    ('Ã‡', 'Ç'),
    ('Ã€', 'À'),
    ('â€™', "'"),
    ('â€œ', '"'),
    ('â€', '"'),
    ('â‚¬', '€'),
]

# Appliquer toutes les corrections
for old, new in replacements:
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        print(f"  ✓ Remplacé {count}x: {repr(old)} → {repr(new)}")

# Sauvegarder avec UTF-8
with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Tous les symboles ont été corrigés")

# -*- coding: utf-8 -*-
"""Correction complète de tous les problèmes d'encodage"""

# Lire le fichier
with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Corrections d'encodage
corrections = {
    'Ã©': 'é',
    'Ã¨': 'è',
    'Ã ': 'à',
    'Ã§': 'ç',
    'Ã´': 'ô',
    'Ã»': 'û',
    'Ã¢': 'â',
    'Ã®': 'î',
    'Ã«': 'ë',
    'Ã¯': 'ï',
    'Ã¹': 'ù',
    'Ãª': 'ê',
    'Ã‰': 'É',
    'Ã‡': 'Ç',
    'Ã€': 'À',
    'â€™': "'",
    'â€œ': '"',
    'â€': '"',
    'â‚¬': '€',
    'â€"': '–',
    'â€"': '—',
    'âž•': '+',
    'ðŸ"Š': '',
    'ðŸ"‹': '',
    'ðŸ"ˆ': '',
    'ðŸ"„': '',
    'ðŸ"': '',
    'ðŸ"¬': '',
    'ðŸ§ª': '',
    '🧬': '',
    '🔬': '',
    '🧪': '',
}

# Appliquer toutes les corrections
for old, new in corrections.items():
    content = content.replace(old, new)

# Sauvegarder avec UTF-8
with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Tous les caractères mal encodés ont été corrigés")
print("✅ Fichier sauvegardé en UTF-8")

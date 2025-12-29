"""Script pour supprimer TOUS les emojis et caractères problématiques"""
import os
import re

# Mapping des remplacements
REPLACEMENTS = {
    '✏️': '[Modifier]',
    '✏': '[Modifier]',
    '⚠️': '[Attention]',
    '⚠': '[Attention]',
    '📜': '[Registre]',
    '⚡': '[Actions]',
    '📊': '[Stats]',
    '📄': '[PDF]',
    '✅': '[OK]',
    '❌': '[Erreur]',
    '📋': '[ID]',
    '📝': '[Note]',
    '⚙️': '[Config]',
    '⚙': '[Config]',
    '📂': '[Fichier]',
    '📤': '[Export]',
    '📅': '[Date]',
    '🔍': '[Recherche]',
    '⏳': '[EnCours]',
    '📚': '[Source]',
    '🎯': '[Origine]',
    '—': '-',  # Em dash
    '°': 'o',  # Degré
    '️': '',   # Variation selector
}

def clean_file(filepath):
    """Nettoie un fichier Python"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Applique tous les remplacements
        for emoji, replacement in REPLACEMENTS.items():
            content = content.replace(emoji, replacement)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"ERREUR sur {filepath}: {e}")
        return False

print("=" * 80)
print("SUPPRESSION DES EMOJIS ET CARACTÈRES PROBLÉMATIQUES")
print("=" * 80)

files_to_clean = []
for root, dirs, files in os.walk("flet_app"):
    for file in files:
        if file.endswith('.py'):
            files_to_clean.append(os.path.join(root, file))

files_to_clean.append("app_erp.py")

cleaned = 0
for filepath in sorted(files_to_clean):
    if clean_file(filepath):
        print(f"✓ {filepath}")
        cleaned += 1

print(f"\n{'=' * 80}")
print(f"TERMINÉ: {cleaned} fichier(s) nettoyé(s)")
print("=" * 80)

"""Script pour supprimer TOUS les caractères problématiques"""
import os

# Mapping complet des remplacements
REPLACEMENTS = {
    # Emojis
    '✏️': '[Modifier]', '✏': '[Modifier]',
    '⚠️': '[Attention]', '⚠': '[Attention]',
    '📜': '[Registre]', '⚡': '[Actions]',
    '📊': '[Stats]', '📄': '[PDF]',
    '✅': '[OK]', '❌': '[Erreur]',
    '📋': '[ID]', '📝': '[Note]',
    '⚙️': '[Config]', '⚙': '[Config]',
    '📂': '[Fichier]', '📤': '[Export]',
    '📅': '[Date]', '🔍': '[Recherche]',
    '⏳': '[EnCours]', '📚': '[Source]',
    '🎯': '[Origine]', '📦': '[Paquet]',
    'ℹ': '[Info]', '🔬': '[Analyse]',
    '💾': '[Sauvegarder]', '👷': '[MO]',
    '🌍': '[Milieu]', '📏': '[Mesure]',
    '🔄': '[Actualiser]', '🏢': '[Equipe]',
    '🛡': '[Protection]', '🚀': '[Action]',
    '🔒': '[Prevention]', '🎉': '[Cloture]',
    '💡': '[Info]', '➕': '[+]',
    '✓': '[OK]', '🔗': '[Lien]',
    '🗓': '[Calendrier]', '💰': '[Cout]',
    '📈': '[Graphique]', '🔧': '[Outil]',
    '👥': '[Utilisateurs]', '👋': '',
    '🏭': '[Production]', '⏰': '[Urgent]',
    '🔴': '[Critique]', '🟠': '[Urgent]',
    '🟡': '[Attention]', '🟢': '[Normal]',
    '📎': '[PJ]', '🔔': '[Alerte]',
    '🚨': '[Retard]', '🥧': '[Graphique]',
    '⏱': '[Performance]',
    
    # Flèches
    '—': '-', '→': '>', '←': '<',
    '↗': '^', '↘': 'v', '↔': '<>',
    '⬅': '<', '➡': '>', '◀': '<',
    '▶': '>', '▼': 'v', '▲': '^',
    '➤': '>',
    
    # Autres symboles
    '°': 'o', '️': '',
    '×': 'x', '€': 'EUR',
    '•': '*', '☑': '[x]',
    '±': '+/-', 'µ': 'u',
    'œ': 'oe', 'Œ': 'Oe',
    
    # Caractères corrompus (replacement characters)
    '�': '',
}

def clean_file(filepath):
    """Nettoie un fichier Python"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        original = content
        
        # Applique tous les remplacements
        for char, replacement in REPLACEMENTS.items():
            content = content.replace(char, replacement)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"ERREUR sur {filepath}: {e}")
        return False

print("=" * 80)
print("SUPPRESSION COMPLÈTE DES CARACTÈRES PROBLÉMATIQUES")
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

"""Test des dépendances pour l'export"""

print("Test des imports pour export...")

# Test CSV (toujours disponible)
try:
    import csv
    print("✅ CSV disponible (standard Python)")
except ImportError:
    print("❌ CSV non disponible")

# Test Excel
try:
    import openpyxl
    print("✅ openpyxl disponible pour export Excel")
except ImportError:
    print("⚠️ openpyxl non disponible - export Excel désactivé")
    print("   Pour installer: pip install openpyxl")

# Test PDF
try:
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate
    print("✅ reportlab disponible pour export PDF")
except ImportError:
    print("⚠️ reportlab non disponible - export PDF désactivé")
    print("   Pour installer: pip install reportlab")

print("\nRésumé:")
print("- Export CSV: Toujours disponible")
print("- Export Excel: Nécessite openpyxl")
print("- Export PDF: Nécessite reportlab")

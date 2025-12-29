"""Script pour tester les pages d'administration et identifier les erreurs"""

import sys
import traceback

def test_import(module_path, class_name):
    """Teste l'import d'une page"""
    try:
        print(f"\n[TEST] Import de {module_path}...")
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        print(f"  ✓ {class_name} importé avec succès")
        return True
    except Exception as e:
        print(f"  ✗ ERREUR lors de l'import de {class_name}:")
        print(f"    {type(e).__name__}: {e}")
        traceback.print_exc()
        return False

# Test des imports
print("=" * 60)
print("TEST DES IMPORTS - PAGES D'ADMINISTRATION")
print("=" * 60)

pages_to_test = [
    ("flet_app.users_page", "UsersPage"),
    ("flet_app.pages", "SettingsPage"),
    ("flet_app.reports_page", "ReportsPage"),
    ("flet_app.inspections_page", "InspectionsPage"),
    ("flet_app.analysis_page", "AnalysisPage"),
]

results = {}
for module_path, class_name in pages_to_test:
    results[class_name] = test_import(module_path, class_name)

print("\n" + "=" * 60)
print("RÉSUMÉ")
print("=" * 60)
success = sum(1 for v in results.values() if v)
total = len(results)
print(f"Succès: {success}/{total}")
for name, success in results.items():
    status = "✓" if success else "✗"
    print(f"  {status} {name}")

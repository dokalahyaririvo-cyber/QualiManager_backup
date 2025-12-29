"""Test direct de la page UsersPage pour identifier les erreurs"""

import sys
import traceback

# Mock minimal pour tester l'import
class MockDB:
    def get_all_users(self):
        return [
            {'id': 1, 'nom': 'Admin', 'email': 'admin@test.com', 'role': 'Administrateur', 'actif': True}
        ]

def mock_navigate(route):
    print(f"Navigate to: {route}")

mock_user = {'id': 1, 'nom': 'Admin', 'role': 'Administrateur'}

try:
    print("=" * 60)
    print("TEST: Import UsersPage")
    print("=" * 60)
    
    from flet_app.users_page import UsersPage
    print("[OK] Import réussi")
    
    print("\n" + "=" * 60)
    print("TEST: Création instance UsersPage")
    print("=" * 60)
    
    # Tenter de créer une instance
    db = MockDB()
    page_instance = UsersPage(user=mock_user, db=db, navigate=mock_navigate)
    print("[OK] Instance créée sans erreur")
    
    print("\n" + "=" * 60)
    print("TEST: Vérification attributs")
    print("=" * 60)
    
    print(f"  - content type: {type(page_instance.content)}")
    print(f"  - expand: {page_instance.expand}")
    print(f"  - padding: {page_instance.padding}")
    
    print("\n[SUCCESS] Tous les tests passés!")
    
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    print("\nTraceback complet:")
    traceback.print_exc()
    sys.exit(1)

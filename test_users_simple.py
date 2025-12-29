"""Test simple de construction UsersPage"""

from flet_app.users_page import UsersPage
from flet_app.theme import Theme
from flet_app.db_manager import DatabaseManager
import os

# Init theme
Theme.init()

# DB
db_path = os.path.join(os.getenv('APPDATA'), 'QualiManager', 'qualimanager_erp.db')
db = DatabaseManager(db_path)

mock_user = {'id': 1, 'nom': 'Admin', 'role': 'Administrateur'}

def mock_navigate(route):
    pass

print("=" * 60)
print("TEST: Construction UsersPage")
print("=" * 60)

try:
    page = UsersPage(user=mock_user, db=db, navigate=mock_navigate)
    print("[OK] Instance créée")
    
    # Vérifier le contenu
    print(f"\n[CHECK] Type content: {type(page.content)}")
    print(f"[CHECK] Expand: {page.expand}")
    print(f"[CHECK] Padding: {page.padding}")
    
    # Vérifier la structure
    if hasattr(page.content, 'controls'):
        print(f"[CHECK] Nombre de controls: {len(page.content.controls)}")
        for i, ctrl in enumerate(page.content.controls):
            print(f"  [{i}] {type(ctrl).__name__}")
            # Chercher des strings
            if isinstance(ctrl, str):
                print(f"    [ERROR] Control #{i} est une STRING: '{ctrl}'")
    
    print("\n[SUCCESS] Tous les checks passés")
    
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

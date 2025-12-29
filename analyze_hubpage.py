"""Analyse détaillée de la structure HubPage pour trouver les strings"""

import flet as ft
from flet_app.theme import Theme
from flet_app.layout import HubPage
from flet_app.db_manager import DatabaseManager
import os

db_path = os.path.join(os.getenv('APPDATA'), 'QualiManager', 'qualimanager_erp.db')
db = DatabaseManager(db_path)

mock_user = {'id': 1, 'nom': 'Admin', 'role': 'Administrateur'}

def mock_navigate(route):
    pass

def mock_logout():
    pass

Theme.init()

print("=" * 70)
print("ANALYSE STRUCTURE HUBPAGE")
print("=" * 70)

# Créer HubPage
hub = HubPage(
    user=mock_user,
    db=db,
    navigate=mock_navigate,
    on_logout=mock_logout,
)

def check_controls(obj, path="root", depth=0):
    """Vérifie récursivement tous les controls"""
    indent = "  " * depth
    
    # Si c'est une string, c'est le problème!
    if isinstance(obj, str):
        print(f"{indent}[ERROR] STRING FOUND at {path}: '{obj}'")
        return True
    
    # Si c'est None, pas de problème
    if obj is None:
        return False
    
    found_string = False
    
    # Vérifier si c'est un contrôle avec des controls
    if hasattr(obj, 'controls'):
        if isinstance(obj.controls, list):
            for i, ctrl in enumerate(obj.controls):
                if isinstance(ctrl, str):
                    print(f"{indent}[ERROR] STRING in controls[{i}] at {path}: '{ctrl}'")
                    found_string = True
                else:
                    found_string |= check_controls(ctrl, f"{path}.controls[{i}]", depth+1)
    
    # Vérifier si c'est un contrôle avec content
    if hasattr(obj, 'content') and obj.content is not None:
        if isinstance(obj.content, str):
            print(f"{indent}[ERROR] STRING in content at {path}: '{obj.content}'")
            found_string = True
        else:
            found_string |= check_controls(obj.content, f"{path}.content", depth+1)
    
    return found_string

print("\nVérification de la structure HubPage...")
found = check_controls(hub, "HubPage")

if found:
    print("\n" + "=" * 70)
    print("[ERROR] DES STRINGS ONT ÉTÉ TROUVÉES DANS LES CONTROLS!")
    print("=" * 70)
else:
    print("\n" + "=" * 70)
    print("[OK] Aucune string trouvée dans les controls")
    print("=" * 70)

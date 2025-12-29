"""Test direct de l'erreur administration"""

import flet as ft
from flet_app.theme import Theme
from flet_app.users_page import UsersPage
from flet_app.layout import MainLayout
from database.db_manager import DatabaseManager
import os

# Chemin base de données
db_path = os.path.join(os.getenv('APPDATA'), 'QualiManager', 'qualimanager_erp.db')
db = DatabaseManager(db_path)

mock_user = {'id': 1, 'nom': 'Admin Test', 'role': 'Administrateur'}

def mock_navigate(route):
    print(f"Navigate to: {route}")

def mock_logout():
    print("Logout")

def main(page: ft.Page):
    Theme.init()
    page.title = "Test Admin"
    page.bgcolor = Theme.BG_PRIMARY
    
    print("[TEST] Création UsersPage...")
    try:
        users_page = UsersPage(user=mock_user, db=db, navigate=mock_navigate)
        print("[OK] UsersPage créée")
        
        print("[TEST] Création MainLayout avec UsersPage...")
        layout = MainLayout(
            user=mock_user,
            db=db,
            navigate=mock_navigate,
            on_logout=mock_logout,
            content=users_page,
            current_route="/admin",
        )
        print("[OK] MainLayout créé")
        
        print("[TEST] Ajout à la page...")
        page.add(layout)
        print("[OK] Ajouté à la page")
        
        print("[TEST] Update de la page...")
        page.update()
        print("[OK] Page mise à jour avec succès!")
        
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ft.app(target=main)

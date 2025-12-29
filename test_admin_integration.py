"""Test intégration UsersPage avec MainLayout et page.update()"""

import flet as ft
from flet_app.theme import Theme
from flet_app.users_page import UsersPage
from flet_app.layout import MainLayout
from flet_app.db_manager import DatabaseManager
import os

db_path = os.path.join(os.getenv('APPDATA'), 'QualiManager', 'qualimanager_erp.db')
db = DatabaseManager(db_path)

mock_user = {'id': 1, 'nom': 'Admin', 'role': 'Administrateur'}

def main(page: ft.Page):
    Theme.init()
    page.title = "Test Admin Integration"
    page.bgcolor = Theme.BG_PRIMARY
    page.padding = 0
    
    def mock_navigate(route):
        print(f"[NAV] Navigate to: {route}")
    
    def mock_logout():
        print("[LOGOUT]")
    
    try:
        print("[1] Création UsersPage...")
        users_page = UsersPage(user=mock_user, db=db, navigate=mock_navigate)
        print("[OK] UsersPage créée")
        
        print("[2] Création MainLayout...")
        layout = MainLayout(
            user=mock_user,
            db=db,
            navigate=mock_navigate,
            on_logout=mock_logout,
            content=users_page,
            current_route="/admin",
        )
        print("[OK] MainLayout créé")
        
        print("[3] Création View...")
        view = ft.View(
            route="/admin",
            bgcolor=Theme.BG_PRIMARY,
            padding=0,
            controls=[layout],
        )
        print("[OK] View créée")
        
        print("[4] Ajout view à page.views...")
        page.views.clear()
        page.views.append(view)
        print("[OK] View ajoutée")
        
        print("[5] Appel page.update()...")
        page.update()
        print("[SUCCESS] Page mise à jour!")
        
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 70)
    print("TEST INTEGRATION ADMIN")
    print("=" * 70 + "\n")
    ft.app(target=main)

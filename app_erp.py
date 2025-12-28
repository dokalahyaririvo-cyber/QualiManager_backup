# -*- coding: utf-8 -*-
"""
QualiManager ERP QHSE - Application principale
Version: 2.0 - ERP Agroalimentaire complet
Framework: Flet (Material Design 3)
"""

import os
import sys

# IMPORTANT: Configurer les variables d'environnement AVANT d'importer Flet
# Cela force Flet à utiliser le bon titre pour la fenêtre Windows
os.environ["FLET_APP_TITLE"] = "QualiManager - Gestion Qualité QHSE"
os.environ["FLET_APP_NAME"] = "QualiManager"

import flet as ft
from typing import Dict, Any, Optional
import shutil

# Déterminer le répertoire de base de l'application
if getattr(sys, 'frozen', False):
    # Mode exécutable PyInstaller
    application_path = os.path.dirname(sys.executable)
else:
    # Mode développement
    application_path = os.path.dirname(os.path.abspath(__file__))

# Déterminer si on est en mode portable ou installeur
def is_portable_mode():
    """Détecte si on est en mode portable (onefile) ou installé."""
    if not getattr(sys, 'frozen', False):
        return False  # Mode dev
    
    # En mode portable (onefile), le fichier exe est dans le dossier principal
    # En mode installeur (onedir), il y a un dossier _internal
    internal_path = os.path.join(application_path, '_internal')
    return not os.path.exists(internal_path)

# Déterminer le dossier des données utilisateur
def get_user_data_path():
    """Retourne le chemin vers le dossier de données utilisateur."""
    # En mode portable, stocker les données à côté de l'exécutable
    if is_portable_mode():
        return application_path
    
    # En mode installeur ou dev, utiliser AppData
    if sys.platform == 'win32':
        appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
        user_data_dir = os.path.join(appdata, 'QualiManager')
    else:
        user_data_dir = os.path.expanduser('~/.qualimanager')
    
    # Créer le dossier s'il n'existe pas
    os.makedirs(user_data_dir, exist_ok=True)
    
    # Créer le dossier backups s'il n'existe pas
    backups_dir = os.path.join(user_data_dir, 'backups')
    os.makedirs(backups_dir, exist_ok=True)
    
    return user_data_dir

# Initialiser la base de données dans le dossier utilisateur
user_data_path = get_user_data_path()
db_filename = "qualimanager_erp.db"
user_db_path = os.path.join(user_data_path, db_filename)

# Si la base n'existe pas dans le dossier utilisateur, la copier depuis l'installation
if not os.path.exists(user_db_path):
    install_db_path = os.path.join(application_path, db_filename)
    if os.path.exists(install_db_path):
        print(f"📦 Copie de la base de données initiale vers {user_db_path}")
        shutil.copy2(install_db_path, user_db_path)
    else:
        print(f"ℹ️ Nouvelle installation - Base de données sera créée dans {user_db_path}")

# Définir le répertoire de travail sur le répertoire de l'application
os.chdir(application_path)

# Ajouter le dossier au path
sys.path.insert(0, application_path)

from flet_app.theme import Theme, ThemeMode
from flet_app.db_manager import DatabaseManager
from flet_app.layout import MainLayout, HubPage


def main(page: ft.Page):
    """Point d'entrée principal de l'application ERP QHSE."""
    
    print("=" * 80)
    print("🚀 DEMARRAGE QUALIMANAGER ERP QHSE")
    print("=" * 80)
    print(f"📂 Mode: {'PORTABLE (données locales)' if is_portable_mode() else 'INSTALLEUR (AppData)'}")
    print(f"📂 Répertoire application: {application_path}")
    print(f"📂 Répertoire données: {user_data_path}")
    
    # INITIALISER LE THEME AU DEMARRAGE
    Theme.init()
    print(f"✅ Theme initialisé - Mode: {Theme._mode}")
    print(f"   BG_PRIMARY: {Theme.BG_PRIMARY}")
    print(f"   TEXT_PRIMARY: {Theme.TEXT_PRIMARY}")
    
    # Configuration de la page - IMPORTANT: définir en premier pour Windows taskbar
    page.title = "QualiManager - Gestion Qualité QHSE"
    page.window.title = "QualiManager - Gestion Qualité QHSE"  # Pour la taskbar Windows
    page.window.title_bar_hidden = False
    page.window.title_bar_buttons_hidden = False
    
    # Configurer l'icône de l'application (chemins multiples pour compatibilité)
    icon_found = False
    possible_icon_paths = [
        os.path.join(application_path, "assets", "icon.ico"),  # Installé
        os.path.join(application_path, "_internal", "assets", "icon.ico"),  # PyInstaller onedir
        os.path.join(sys._MEIPASS, "assets", "icon.ico") if getattr(sys, 'frozen', False) else None,  # PyInstaller onefile
    ]
    
    for icon_path in possible_icon_paths:
        if icon_path and os.path.exists(icon_path):
            page.window.icon = icon_path
            print(f"✅ Icône chargée: {icon_path}")
            icon_found = True
            break
    
    if not icon_found:
        print("⚠️ Icône non trouvée")
    
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = Theme.BG_PRIMARY
    page.padding = 0
    page.window.width = 1500
    page.window.height = 950
    page.window.center()
    page.window.min_width = 1200
    page.window.min_height = 700
    
    # Initialiser la base de données dans le dossier utilisateur
    print(f"📊 Base de données: {user_db_path}")
    db = DatabaseManager(user_db_path)
    
    # État de l'application
    current_user: Optional[Dict[str, Any]] = None
    pages_cache = {}  # Cache des pages pour navigation instantanée
    
    def logout():
        """Déconnexion."""
        nonlocal current_user, pages_cache
        current_user = None
        pages_cache.clear()  # Vider le cache
        navigate("/login")
    
    def navigate(route: str):
        """Navigation entre les pages avec cache."""
        nonlocal current_user, pages_cache
        
        page.views.clear()
        
        if route == "/login" or current_user is None:
            page.views.append(create_login_view())
        elif route == "/hub" or route == "/home":
            page.views.append(HubPage(
                user=current_user,
                db=db,
                navigate=navigate,
                on_logout=logout,
            ))
        elif route == "/nc":
            # Utiliser le cache ou créer
            if route not in pages_cache:
                try:
                    print("[NC] Tentative d'import de nc_page...")
                    from flet_app.nc_page import NCPage
                    print("[NC] Import réussi, création de l'instance...")
                    pages_cache[route] = NCPage(user=current_user, db=db, navigate=navigate)
                    print("[NC] Instance créée avec succès")
                    # Activer les raccourcis clavier
                    if hasattr(pages_cache[route], '_handle_keyboard_event'):
                        page.on_keyboard_event = pages_cache[route]._handle_keyboard_event
                        print("[NC] Raccourcis clavier activés depuis app_erp.py")
                except Exception as e:
                    print(f"[NC] ❌ ERREUR: {type(e).__name__}: {e}")
                    import traceback
                    traceback.print_exc()
                    # Afficher l'erreur à l'utilisateur
                    page.views.append(ft.View(
                        "/nc",
                        [
                            ft.Text(f"Erreur lors du chargement du module NC:", size=20, weight=ft.FontWeight.BOLD, color="red"),
                            ft.Text(f"{type(e).__name__}: {str(e)}", size=14),
                            ft.ElevatedButton("Retour", on_click=lambda _: navigate("/hub"))
                        ],
                        bgcolor=Theme.BG_PRIMARY
                    ))
                    page.update()
                    return
            else:
                # Réactiver les raccourcis si la page existe déjà
                if hasattr(pages_cache[route], '_handle_keyboard_event'):
                    page.on_keyboard_event = pages_cache[route]._handle_keyboard_event
                    print("[NC] Raccourcis clavier réactivés")
            page.views.append(create_layout_view(pages_cache[route], route))
        elif route == "/veille":
            if route not in pages_cache:
                from flet_app.veille_page import VeillePage
                pages_cache[route] = VeillePage(user=current_user, db=db, navigate=navigate)
            page.views.append(create_layout_view(pages_cache[route], route))
        elif route == "/inspections":
            if route not in pages_cache:
                from flet_app.inspections_page import InspectionsPage
                pages_cache[route] = InspectionsPage(user=current_user, db=db, navigate=navigate)
            page.views.append(create_layout_view(pages_cache[route], route))
        elif route in ["/labo", "/lab"]:
            if "/labo" not in pages_cache:
                from flet_app.lab_page_new import LabPage
                pages_cache["/labo"] = LabPage(user=current_user, db=db, navigate=navigate)
            page.views.append(create_layout_view(pages_cache["/labo"], route))
        elif route == "/kpi":
            if route not in pages_cache:
                from flet_app.kpi_page import KPIPage
                pages_cache[route] = KPIPage(user=current_user, db=db, navigate=navigate)
            page.views.append(create_layout_view(pages_cache[route], route))
        elif route == "/reports":
            if route not in pages_cache:
                from flet_app.reports_page import ReportsPage
                pages_cache[route] = ReportsPage(user=current_user, db=db, navigate=navigate)
            page.views.append(create_layout_view(pages_cache[route], route))
        elif route == "/admin" or route == "/users":
            if "/admin" not in pages_cache:
                from flet_app.users_page import UsersPage
                pages_cache["/admin"] = UsersPage(user=current_user, db=db, navigate=navigate)
            page.views.append(create_layout_view(pages_cache["/admin"], route))
        else:
            # Route par défaut -> Hub
            page.views.append(HubPage(
                user=current_user,
                db=db,
                navigate=navigate,
                on_logout=logout,
            ))
        
        page.update()
    
    def create_layout_view(content: ft.View, route: str) -> ft.View:
        """Crée une vue avec le layout principal (sidebar)."""
        return ft.View(
            route=route,
            bgcolor=Theme.BG_PRIMARY,
            padding=0,
            controls=[
                MainLayout(
                    user=current_user,
                    db=db,
                    navigate=navigate,
                    on_logout=logout,
                    content=content,
                    current_route=route,
                ),
            ],
        )
    
    def create_login_view() -> ft.View:
        """Page de connexion moderne."""
        
        email_field = ft.TextField(
            label="Email",
            prefix_icon=ft.Icons.EMAIL,
            border_radius=12,
            filled=True,
            bgcolor=Theme.BG_SECONDARY,
            text_style=ft.TextStyle(color=Theme.TEXT_PRIMARY),
            value="admin@qualimanager.local",  # Pré-rempli pour test
        )
        
        password_field = ft.TextField(
            label="Mot de passe",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            border_radius=12,
            filled=True,
            bgcolor=Theme.BG_SECONDARY,
            text_style=ft.TextStyle(color=Theme.TEXT_PRIMARY),
            value="Admin@2024!",  # Pré-rempli pour test
        )
        
        error_text = ft.Text("", color=Theme.DANGER, size=12)
        
        def login_click(e):
            nonlocal current_user
            
            if not email_field.value or not password_field.value:
                error_text.value = "Veuillez remplir tous les champs"
                page.update()
                return
            
            # Authentification
            user = db.authenticate(email_field.value, password_field.value)
            
            if user:
                current_user = user
                navigate("/hub")
            else:
                error_text.value = "Email ou mot de passe incorrect"
                page.update()
        
        return ft.View(
            route="/login",
            bgcolor=Theme.BG_PRIMARY,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=450,
                    padding=40,
                    border_radius=20,
                    bgcolor=Theme.BG_SECONDARY,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=30,
                        color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                    ),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.VERIFIED_USER, size=60, color=Theme.PRIMARY),
                            ft.Container(height=10),
                            ft.Text(
                                "QualiManager",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.TEXT_PRIMARY,
                            ),
                            ft.Text(
                                "ERP QHSE Agroalimentaire",
                                size=14,
                                color=Theme.TEXT_MUTED,
                            ),
                            ft.Divider(height=30, color="transparent"),
                            email_field,
                            ft.Container(height=10),
                            password_field,
                            error_text,
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                "Se connecter",
                                icon=ft.Icons.LOGIN,
                                style=ft.ButtonStyle(
                                    bgcolor=Theme.PRIMARY,
                                    color=ft.Colors.WHITE,
                                    padding=20,
                                    shape=ft.RoundedRectangleBorder(radius=12),
                                ),
                                width=300,
                                on_click=login_click,
                            ),
                            ft.Container(height=15),
                            ft.Container(
                                padding=10,
                                border_radius=10,
                                bgcolor=Theme.BG_TERTIARY,
                                content=ft.Column(
                                    spacing=5,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text("🔑 Identifiants de test", size=11, color=Theme.TEXT_MUTED),
                                        ft.Text("admin@qualimanager.local", size=12, color=Theme.INFO),
                                        ft.Text("Admin@2024!", size=12, color=Theme.INFO),
                                    ]
                                ),
                            ),
                        ],
                    ),
                ),
            ],
        )
    
    # Route change handler
    def route_change(e):
        navigate(page.route)
    
    page.on_route_change = route_change
    
    # Démarrer avec la page de login
    navigate("/login")
    print("✅ Application démarrée - Page login chargée")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("LANCEMENT DE L'APPLICATION FLET")
    print("=" * 80 + "\n")
    
    # Configuration Flet avec métadonnées correctes
    ft.app(
        target=main,
        name="QualiManager - Gestion Qualité QHSE",  # Nom complet pour Windows
        assets_dir="assets",
        view=ft.AppView.FLET_APP,  # Force le mode application natif
        web_renderer=ft.WebRenderer.AUTO  # Renderer automatique
    )

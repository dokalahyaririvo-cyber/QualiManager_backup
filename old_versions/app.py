# -*- coding: utf-8 -*-
"""
QualiManager - Application principale Flet
Version moderne avec Material Design 3
"""

import flet as ft
from typing import Dict, Any, Optional

from flet_app.theme import Theme, Styles
from flet_app.database import DatabaseManager
from flet_app.pages import (
    LoginPage,
    HomePage,
    NCListPage,
    NCFormPage,
    NCFichePage,
    UsersPage,
    ComingSoonPage,
)
from flet_app.analysis_page import AnalysisPage


def main(page: ft.Page):
    """Point d'entrée de l'application."""
    
    # Configuration de la page
    page.title = "QualiManager - Système de Gestion Qualité"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = Theme.BG_PRIMARY
    page.padding = 0
    page.window.width = 1400
    page.window.height = 900
    page.window.min_width = 1200
    page.window.min_height = 700
    page.window.center()
    
    # Initialisation de la base de données
    db = DatabaseManager()
    
    # État de l'application
    current_user: Optional[Dict[str, Any]] = None
    
    def navigate(route: str):
        """Navigue vers une route."""
        nonlocal current_user
        
        page.views.clear()
        
        # Routes publiques
        if route == "/login" or current_user is None:
            page.views.append(LoginPage(on_login, db))
        
        # Routes protégées
        elif route == "/home":
            page.views.append(HomePage(current_user, db, navigate, on_logout))
        
        elif route == "/nc":
            page.views.append(NCListPage(current_user, db, navigate))
        
        elif route == "/nc/new":
            page.views.append(NCFormPage(current_user, db, navigate))
        
        elif route.startswith("/nc/") and route.endswith("/edit"):
            nc_id = int(route.split("/")[2])
            page.views.append(NCFormPage(current_user, db, navigate, nc_id))

        elif route == "/nc-fiche":
            page.views.append(NCFichePage(current_user, db, navigate))
        
        elif route == "/analysis":
            page.views.append(AnalysisPage(current_user, db, navigate))
        
        elif route.startswith("/analysis/"):
            nc_id = int(route.split("/")[2])
            page.views.append(AnalysisPage(current_user, db, navigate, nc_id))
        
        elif route == "/analyses":
            page.views.append(AnalysisPage(current_user, db, navigate))
        
        elif route == "/actions":
            page.views.append(ComingSoonPage("Plans d'actions", ft.Icons.CHECKLIST, Theme.PRIMARY, navigate, "/actions"))
        
        elif route == "/veille":
            page.views.append(ComingSoonPage("Veille réglementaire", ft.Icons.VISIBILITY, Theme.INFO, navigate, "/veille"))
        
        elif route == "/inspections":
            page.views.append(ComingSoonPage("Inspections", ft.Icons.FACT_CHECK, Theme.SUCCESS, navigate, "/inspections"))
        
        elif route == "/reports":
            page.views.append(ComingSoonPage("Rapports", ft.Icons.ASSESSMENT, Theme.WARNING, navigate, "/reports"))
        
        elif route == "/settings":
            page.views.append(ComingSoonPage("Paramètres", ft.Icons.SETTINGS, Theme.TEXT_MUTED, navigate, "/settings"))
        
        elif route == "/users":
            if current_user.get('role') == 'Administrateur':
                page.views.append(UsersPage(current_user, db, navigate))
            else:
                navigate("/home")
                return
        
        else:
            navigate("/home")
            return
        
        page.update()
    
    def on_login(user: Dict[str, Any]):
        """Callback de connexion."""
        nonlocal current_user
        current_user = user
        navigate("/home")
    
    def on_logout():
        """Callback de déconnexion."""
        nonlocal current_user
        current_user = None
        navigate("/login")
    
    def on_route_change(e):
        """Gestion du changement de route."""
        navigate(e.route)
    
    page.on_route_change = on_route_change
    
    # Démarrage sur la page de login
    navigate("/login")


if __name__ == "__main__":
    ft.app(target=main)

# -*- coding: utf-8 -*-
"""
QualiManager ERP QHSE - Layout principal avec NavigationRail
Sidebar rétractable persistante sur toutes les pages sauf Hub
"""

import flet as ft
from typing import Dict, Any, Callable, Optional
from datetime import datetime

from .theme import Theme, ThemeMode
from .components import create_button


class MainLayout(ft.Container):
    """
    Layout principal avec NavigationRail rétractable.
    Utilisé sur toutes les pages sauf le Hub de démarrage.
    """
    
    def __init__(
        self,
        user: Dict[str, Any],
        db,
        navigate: Callable,
        on_logout: Callable,
        content: ft.Control,
        current_route: str = "/home",
        show_nav: bool = True,
    ):
        self.user = user
        self.db = db
        self.navigate = navigate
        self.on_logout = on_logout
        self._content = content
        self.current_route = current_route
        self.show_nav = show_nav
        self.nav_extended = False  # État de la sidebar (réduite par défaut)
        
        super().__init__(
            expand=True,
            content=self._build(),
        )
    
    def _build(self):
        if not self.show_nav:
            return self._content
        
        # Définition des destinations de navigation
        nav_destinations = [
            ft.NavigationRailDestination(
                icon=ft.Icons.HUB_OUTLINED,
                selected_icon=ft.Icons.HUB,
                label="Hub",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.WARNING_AMBER_OUTLINED,
                selected_icon=ft.Icons.WARNING_AMBER,
                label="Non-Conformités",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.VISIBILITY_OUTLINED,
                selected_icon=ft.Icons.VISIBILITY,
                label="Veille",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.FACT_CHECK_OUTLINED,
                selected_icon=ft.Icons.FACT_CHECK,
                label="Inspections",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SCIENCE_OUTLINED,
                selected_icon=ft.Icons.SCIENCE,
                label="Laboratoire",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.INSIGHTS_OUTLINED,
                selected_icon=ft.Icons.INSIGHTS,
                label="KPI",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.DESCRIPTION_OUTLINED,
                selected_icon=ft.Icons.DESCRIPTION,
                label="Rapports",
            ),
        ]
        
        # Ajouter Admin si administrateur
        if self.user.get('role') == 'Administrateur':
            nav_destinations.append(
                ft.NavigationRailDestination(
                    icon=ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.ADMIN_PANEL_SETTINGS,
                    label="Administration",
                )
            )
        
        # Déterminer l'index sélectionné
        route_to_index = {
            "/hub": 0,
            "/home": 0,
            "/nc": 1,
            "/veille": 2,
            "/inspections": 3,
            "/labo": 4,
            "/kpi": 5,
            "/reports": 6,
            "/admin": 7,
            "/users": 7,
            "/settings": 7,
        }
        # Extraire la route principale (ex: "/nc/detail" -> "/nc")
        main_route = "/" + self.current_route.split('/')[1] if self.current_route.startswith('/') and len(self.current_route) > 1 else self.current_route
        selected_index = route_to_index.get(main_route, 0)
        
        # NavigationRail
        self.nav_rail = ft.NavigationRail(
            selected_index=selected_index,
            label_type=ft.NavigationRailLabelType.ALL if self.nav_extended else ft.NavigationRailLabelType.NONE,
            extended=self.nav_extended,
            min_width=60,
            min_extended_width=220,
            bgcolor=Theme.BG_SECONDARY,
            indicator_color=Theme.PRIMARY,
            destinations=nav_destinations,
            on_change=self._on_nav_change,
            # Animation fluide lors de l'extension/réduction
            animate_size=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
            leading=ft.Column(
                controls=[
                    ft.Container(
                        padding=ft.padding.symmetric(vertical=10),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(ft.Icons.VERIFIED_USER, color=Theme.PRIMARY, size=28),
                                ft.Text(
                                    "QM",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=Theme.TEXT_PRIMARY,
                                    visible=self.nav_extended,
                                ),
                            ]
                        )
                    ),
                    ft.Divider(color=Theme.BG_TERTIARY),
                ]
            ),
            trailing=ft.Container(
                padding=10,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Divider(color=Theme.BG_TERTIARY),
                        # Toggle sidebar
                        ft.IconButton(
                            icon=ft.Icons.MENU if not self.nav_extended else ft.Icons.MENU_OPEN,
                            icon_color=Theme.TEXT_MUTED,
                            tooltip="Étendre/Réduire le menu",
                            on_click=self._toggle_nav,
                        ),
                        # Toggle theme
                        ft.IconButton(
                            icon=ft.Icons.DARK_MODE if Theme.is_dark() else ft.Icons.LIGHT_MODE,
                            icon_color=Theme.TEXT_MUTED,
                            tooltip="Mode sombre/clair",
                            on_click=self._toggle_theme,
                        ),
                        # User info
                        ft.Container(
                            padding=10,
                            visible=self.nav_extended,
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=4,
                                controls=[
                                    ft.CircleAvatar(
                                        content=ft.Text(
                                            self.user.get('nom', 'U')[0].upper(),
                                            color=ft.Colors.WHITE,
                                        ),
                                        bgcolor=Theme.PRIMARY,
                                        radius=20,
                                    ),
                                    ft.Text(
                                        self.user.get('nom', 'Utilisateur'),
                                        size=12,
                                        color=Theme.TEXT_PRIMARY,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                    ft.Text(
                                        self.user.get('role', ''),
                                        size=10,
                                        color=Theme.TEXT_MUTED,
                                    ),
                                ]
                            )
                        ),
                        # Logout
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT,
                            icon_color=Theme.DANGER,
                            tooltip="Déconnexion",
                            on_click=lambda e: self.on_logout(),
                        ),
                    ]
                )
            ),
        )
        
        return ft.Row(
            expand=True,
            spacing=0,
            controls=[
                self.nav_rail,
                ft.VerticalDivider(width=1, color=Theme.BG_TERTIARY),
                ft.Container(
                    expand=True,
                    bgcolor=Theme.BG_PRIMARY,
                    content=self._content,
                    # Animation fluide lors du changement de contenu
                    animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
                ),
            ]
        )
    
    def _on_nav_change(self, e):
        """Gestion du changement de navigation."""
        routes = ["/hub", "/nc", "/veille", "/inspections", "/labo", "/kpi", "/reports", "/admin"]
        if e.control.selected_index < len(routes):
            self.navigate(routes[e.control.selected_index])
    
    def _toggle_nav(self, e):
        """Bascule l'état de la sidebar."""
        self.nav_extended = not self.nav_extended
        self.nav_rail.extended = self.nav_extended
        self.nav_rail.label_type = ft.NavigationRailLabelType.ALL if self.nav_extended else ft.NavigationRailLabelType.NONE
        # Mettre à jour l'icône du bouton
        e.control.icon = ft.Icons.MENU if not self.nav_extended else ft.Icons.MENU_OPEN
        self.update()
    
    def _toggle_theme(self, e):
        """Bascule le thème."""
        print("🌙 _toggle_theme dans MainLayout appelé")
        Theme.toggle()
        # Mettre à jour le theme_mode de la page Flet via page
        if self.page:
            print(f"   📄 Page trouvée - Nouveau bgcolor: {Theme.BG_PRIMARY}")
            self.page.theme_mode = ft.ThemeMode.LIGHT if not Theme.is_dark() else ft.ThemeMode.DARK
            self.page.bgcolor = Theme.BG_PRIMARY
            
            # Forcer la reconstruction complète en nettoyant d'abord
            print(f"   🧹 Nettoyage complet de la page...")
            self.page.controls.clear()
            self.page.update()
            
            # Puis naviguer pour reconstruire
            print(f"   🔄 Navigation vers: {self.current_route}")
            self.navigate(self.current_route)
        else:
            print("   ⚠️ Pas de page trouvée!")


class HubPage(ft.View):
    """
    Hub de Démarrage - Landing page avec 6 tuiles actives.
    Affichée après connexion, pas de sidebar.
    """
    
    def __init__(
        self,
        user: Dict[str, Any],
        db,
        navigate: Callable,
        on_logout: Callable,
    ):
        self.user = user
        self.db = db
        self.navigate = navigate
        self.on_logout = on_logout
        self.stats = {}
        
        super().__init__(
            route="/hub",
            bgcolor=Theme.BG_PRIMARY,
            padding=0,
            controls=[self._build_ui()],
        )
    
    def _load_stats(self):
        """Charge les statistiques pour les badges."""
        try:
            # Forcer le rechargement des stats depuis la DB
            self.stats = self.db.get_stats()
        except Exception as e:
            print(f"Erreur chargement stats: {e}")
            self.stats = {}
        
        # Stats veille
        try:
            late_raci = self.db.get_late_raci()
            self.stats['late_raci_count'] = len(late_raci)
        except:
            self.stats['late_raci_count'] = 0
        
        # Prochain atelier à auditer
        try:
            next_atelier = self.db.get_next_atelier_to_audit()
            self.stats['next_atelier'] = next_atelier.get('nom', '-') if next_atelier else '-'
        except:
            self.stats['next_atelier'] = '-'
        
        # Derniers lots labo
        try:
            last_lots = self.db.get_last_lot_status()
            blocked = sum(1 for l in last_lots if l.get('statut') == 'Bloquée' or l.get('conforme') == 0)
            self.stats['lab_blocked'] = blocked
            self.stats['lab_status'] = "Bloqué" if blocked > 0 else "Conforme"
        except:
            self.stats['lab_blocked'] = 0
            self.stats['lab_status'] = "-"
    
    def did_mount(self):
        """Appelé lorsque la page est montée - Rafraîchir les stats."""
        # Forcer le rechargement des statistiques
        self._load_stats()
        # Reconstruire complètement l'UI avec les stats à jour
        if hasattr(self, 'page') and self.page:
            try:
                self.controls.clear()
                self.controls.append(self._build_ui())
                self.update()
            except Exception as e:
                print(f"Erreur mise à jour Hub: {e}")
    
    def _build_ui(self):
        """Construit l'interface du Hub."""
        self._load_stats()
        
        # Header
        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=30, vertical=8),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.VERIFIED_USER, color=Theme.PRIMARY, size=40),
                            ft.Column(
                                spacing=0,
                                controls=[
                                    ft.Text(
                                        "QualiManager",
                                        size=24,
                                        weight=ft.FontWeight.BOLD,
                                        color=Theme.TEXT_PRIMARY,
                                    ),
                                    ft.Text(
                                        "ERP QHSE Agroalimentaire",
                                        size=12,
                                        color=Theme.TEXT_MUTED,
                                    ),
                                ]
                            ),
                        ]
                    ),
                    ft.Row(
                        spacing=10,
                        controls=[
                            # Toggle theme
                            ft.IconButton(
                                icon=ft.Icons.DARK_MODE if Theme.is_dark() else ft.Icons.LIGHT_MODE,
                                icon_color=Theme.TEXT_MUTED,
                                tooltip="Mode sombre/clair",
                                on_click=self._toggle_theme,
                            ),
                            # User menu
                            ft.Container(
                                padding=ft.padding.symmetric(horizontal=15, vertical=8),
                                border_radius=20,
                                bgcolor=Theme.BG_SECONDARY,
                                content=ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.CircleAvatar(
                                            content=ft.Text(
                                                self.user.get('nom', 'U')[0].upper(),
                                                color=ft.Colors.WHITE,
                                            ),
                                            bgcolor=Theme.PRIMARY,
                                            radius=16,
                                        ),
                                        ft.Text(
                                            self.user.get('nom', 'Utilisateur'),
                                            size=14,
                                            color=Theme.TEXT_PRIMARY,
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.LOGOUT,
                                            icon_size=18,
                                            icon_color=Theme.TEXT_MUTED,
                                            tooltip="Déconnexion",
                                            on_click=lambda e: self.on_logout(),
                                        ),
                                    ]
                                ),
                            ),
                        ]
                    ),
                ]
            ),
        )
        
        # Salutation
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Bonjour"
        elif hour < 18:
            greeting = "Bon après-midi"
        else:
            greeting = "Bonsoir"
        
        greeting_section = ft.Container(
            padding=ft.padding.only(left=30, right=30, top=5, bottom=10),
            content=ft.Column(
                spacing=2,
                controls=[
                    ft.Text(
                        f"{greeting}, {self.user.get('nom', 'Utilisateur').split()[0]} 👋",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=Theme.TEXT_PRIMARY,
                    ),
                    ft.Text(
                        datetime.now().strftime("%A %d %B %Y"),
                        size=11,
                        color=Theme.TEXT_MUTED,
                    ),
                ]
            ),
        )
        
        # Tuiles des modules - Grid responsive 3x2 avec expansion verticale
        tiles = ft.Container(
            expand=True,
            padding=ft.padding.only(left=30, right=30, bottom=20),
            content=ft.ResponsiveRow(
                spacing=12,
                run_spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    self._create_tile(
                        "Non-Conformités",
                        ft.Icons.WARNING_AMBER,
                        Theme.DANGER,
                        badge_count=self.stats.get('open', 0),
                        badge_color=Theme.DANGER,
                        subtitle=f"{self.stats.get('open', 0)} ouvertes",
                        route="/nc",
                    ),
                    self._create_tile(
                        "Veille & Exigences",
                        ft.Icons.VISIBILITY,
                        Theme.WARNING,
                        badge_count=self.stats.get('late_raci_count', 0),
                        badge_color=Theme.WARNING,
                        subtitle=f"{self.stats.get('late_raci_count', 0)} actions en retard",
                        route="/veille",
                    ),
                    self._create_tile(
                        "Inspections",
                        ft.Icons.FACT_CHECK,
                        Theme.SUCCESS,
                        badge_count=None,
                        subtitle=f"Prochain: {self.stats.get('next_atelier', '-')}",
                        route="/inspections",
                    ),
                    self._create_tile(
                        "Laboratoire",
                        ft.Icons.SCIENCE,
                        Theme.INFO,
                        badge_count=self.stats.get('lab_blocked', 0) if self.stats.get('lab_blocked', 0) > 0 else None,
                        badge_color=Theme.DANGER,
                        subtitle=f"Statut: {self.stats.get('lab_status', '-')}",
                        route="/labo",
                    ),
                    self._create_tile(
                        "Data Intelligence",
                        ft.Icons.INSIGHTS,
                        Theme.SECONDARY,
                        badge_count=None,
                        subtitle="KPI & Tableaux de bord",
                        route="/kpi",
                    ),
                    self._create_tile(
                        "Rapports",
                        ft.Icons.DESCRIPTION,
                        ft.Colors.BLUE_700,
                        badge_count=None,
                        subtitle="Génération de rapports",
                        route="/reports",
                    ),
                    self._create_tile(
                        "Administration",
                        ft.Icons.ADMIN_PANEL_SETTINGS,
                        Theme.TEXT_MUTED,
                        badge_count=None,
                        subtitle="Paramètres & Utilisateurs",
                        route="/admin",
                        visible=self.user.get('role') == 'Administrateur',
                    ),
                ],
            ),
        )
        
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
            controls=[
                header,
                greeting_section,
                tiles,
            ]
        )
    
    def _create_tile(
        self,
        title: str,
        icon: str,
        color: str,
        badge_count: int = None,
        badge_color: str = None,
        subtitle: str = None,
        route: str = None,
        visible: bool = True,
    ) -> ft.Container:
        """Crée une tuile de module responsive."""
        if not visible:
            return ft.Container(col={"sm": 12, "md": 6, "lg": 4, "xl": 4})
        
        badge_color = badge_color or Theme.DANGER
        
        badge = None
        if badge_count is not None and badge_count > 0:
            badge = ft.Container(
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                border_radius=14,
                bgcolor=badge_color,
                content=ft.Text(
                    str(badge_count),
                    size=16,
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                ),
            )
        
        return ft.Container(
            col={"sm": 12, "md": 6, "lg": 4, "xl": 4},  # 1 colonne sur mobile, 2 sur tablette, 3 sur desktop
            padding=18,
            border_radius=18,
            bgcolor=Theme.BG_SECONDARY,
            border=ft.border.all(1, Theme.BG_TERTIARY),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
            ink=True,
            on_click=lambda e, r=route: self.navigate(r) if r else None,
            on_hover=lambda e: self._tile_hover(e, color),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            aspect_ratio=1.6,  # Ratio largeur/hauteur optimisé pour minimiser la hauteur
            content=ft.Column(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Container(
                                padding=14,
                                border_radius=14,
                                bgcolor=color,
                                shadow=ft.BoxShadow(
                                    spread_radius=1,
                                    blur_radius=8,
                                    color=ft.Colors.with_opacity(0.3, color),
                                    offset=ft.Offset(0, 2),
                                ),
                                content=ft.Icon(icon, color=ft.Colors.WHITE, size=56),
                            ),
                            badge or ft.Container(),
                        ]
                    ),
                    ft.Column(
                        spacing=6,
                        controls=[
                            ft.Text(
                                title,
                                size=26,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.TEXT_PRIMARY,
                            ),
                            ft.Text(
                                subtitle or "",
                                size=18,
                                weight=ft.FontWeight.W_500,
                                color=Theme.TEXT_SECONDARY,
                            ),
                        ]
                    )
                ]
            ),
        )
    
    def _tile_hover(self, e, color):
        """Animation survol tuile."""
        try:
            ctrl = getattr(e, "control", None)
            if not ctrl or not ctrl.page:
                return
            if e.data == "true":
                ctrl.border = ft.border.all(2, color)
                ctrl.bgcolor = Theme.BG_TERTIARY
            else:
                ctrl.border = ft.border.all(1, Theme.BG_TERTIARY)
                ctrl.bgcolor = Theme.BG_SECONDARY
            ctrl.update()
        except Exception:
            pass
    
    def _create_summary_card(
        self,
        title: str,
        value: str,
        icon: str,
        color: str,
    ) -> ft.Container:
        """Crée une carte de résumé."""
        return ft.Container(
            expand=True,
            padding=20,
            border_radius=16,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                            ft.Text(title, size=12, color=Theme.TEXT_MUTED),
                        ]
                    ),
                    ft.Container(
                        padding=10,
                        border_radius=10,
                        bgcolor=Theme.BG_TERTIARY,
                        content=ft.Icon(icon, color=color, size=24),
                    ),
                ]
            ),
        )
    
    def _toggle_theme(self, e):
        """Bascule le thème."""
        print("☀️ _toggle_theme dans HubPage appelé")
        Theme.toggle()
        # Mettre à jour le theme_mode de la page Flet
        if self.page:
            print(f"   📄 Page trouvée - Nouveau bgcolor: {Theme.BG_PRIMARY}")
            self.page.theme_mode = ft.ThemeMode.LIGHT if not Theme.is_dark() else ft.ThemeMode.DARK
            self.page.bgcolor = Theme.BG_PRIMARY
            
            # Forcer la reconstruction complète
            print("   🧹 Nettoyage complet de la page...")
            self.page.controls.clear()
            self.page.update()
            
            # Puis reconstruire le Hub
            print("   🔄 Navigation vers /hub")
            self.navigate("/hub")
        else:
            print("   ⚠️ Pas de page trouvée!")

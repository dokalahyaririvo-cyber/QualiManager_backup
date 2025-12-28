# -*- coding: utf-8 -*-
"""
QualiManager - Version Flet (Modern UI)
Framework: Flet (basé sur Flutter)
Interface: Material Design 3, GPU-accelerated
"""

import flet as ft
from datetime import datetime
from typing import Optional, Callable
import sqlite3
import hashlib


class ModernTheme:
    """Thème Material Design 3."""
    PRIMARY = "#3B82F6"
    PRIMARY_DARK = "#1E40AF"
    SECONDARY = "#8B5CF6"
    SUCCESS = "#10B981"
    DANGER = "#EF4444"
    WARNING = "#F59E0B"
    INFO = "#06B6D4"
    
    BG_PRIMARY = "#0F172A"
    BG_SECONDARY = "#1E293B"
    BG_TERTIARY = "#334155"
    
    TEXT_PRIMARY = "#F8FAFC"
    TEXT_SECONDARY = "#CBD5E1"
    TEXT_MUTED = "#64748B"


def main(page: ft.Page):
    """Application principale Flet."""
    
    # Configuration de la page
    page.title = "QualiManager - Gestion Qualité"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ModernTheme.BG_PRIMARY
    page.padding = 0
    page.window.width = 1400
    page.window.height = 900
    page.window.center()
    
    # État de l'application
    current_user = {"name": None, "role": None}
    
    def navigate(route: str):
        """Navigation entre les pages."""
        page.views.clear()
        
        if route == "/login":
            page.views.append(create_login_view())
        elif route == "/home":
            page.views.append(create_home_view())
        elif route == "/nc/new":
            page.views.append(create_nc_form_view())
        elif route == "/analysis":
            page.views.append(create_analysis_view())
        
        page.update()
    
    def create_login_view() -> ft.View:
        """Page de connexion moderne."""
        
        email_field = ft.TextField(
            label="Email",
            prefix_icon=ft.Icons.EMAIL,
            border_radius=12,
            filled=True,
            bgcolor=ModernTheme.BG_SECONDARY,
        )
        
        password_field = ft.TextField(
            label="Mot de passe",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            border_radius=12,
            filled=True,
            bgcolor=ModernTheme.BG_SECONDARY,
        )
        
        error_text = ft.Text("", color=ModernTheme.DANGER, size=12)
        
        def login_click(e):
            if email_field.value and password_field.value:
                current_user["name"] = "Admin"
                current_user["role"] = "Administrateur"
                navigate("/home")
            else:
                error_text.value = "Veuillez remplir tous les champs"
                page.update()
        
        return ft.View(
            route="/login",
            bgcolor=ModernTheme.BG_PRIMARY,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=450,
                    padding=40,
                    border_radius=20,
                    bgcolor=ModernTheme.BG_SECONDARY,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=30,
                        color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                    ),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.VERIFIED_USER, size=60, color=ModernTheme.PRIMARY),
                            ft.Text("QualiManager", size=28, weight=ft.FontWeight.BOLD, color=ModernTheme.TEXT_PRIMARY),
                            ft.Text("Système de Gestion Qualité", size=14, color=ModernTheme.TEXT_MUTED),
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
                                    bgcolor=ModernTheme.PRIMARY,
                                    color=ft.Colors.WHITE,
                                    padding=20,
                                    shape=ft.RoundedRectangleBorder(radius=12),
                                ),
                                width=300,
                                on_click=login_click,
                            ),
                            ft.Container(height=15),
                            ft.TextButton(
                                "Mot de passe oublié ?",
                                style=ft.ButtonStyle(color=ModernTheme.TEXT_MUTED),
                            ),
                        ],
                    ),
                ),
            ],
        )
    
    def create_home_view() -> ft.View:
        """Dashboard principal."""
        
        def create_stat_card(icon: str, title: str, value: str, color: str, trend: str = None):
            return ft.Container(
                expand=1,
                padding=20,
                border_radius=16,
                bgcolor=ModernTheme.BG_SECONDARY,
                animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
                on_hover=lambda e: setattr(e.control, 'scale', 1.02 if e.data == "true" else 1),
                content=ft.Column(
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Container(
                                    padding=12,
                                    border_radius=12,
                                    bgcolor=ft.Colors.with_opacity(0.15, color),
                                    content=ft.Icon(icon, color=color, size=24),
                                ),
                                ft.Text(trend or "", color=ModernTheme.SUCCESS, size=12) if trend else ft.Container(),
                            ],
                        ),
                        ft.Container(height=15),
                        ft.Text(value, size=32, weight=ft.FontWeight.BOLD, color=ModernTheme.TEXT_PRIMARY),
                        ft.Text(title, size=14, color=ModernTheme.TEXT_MUTED),
                    ],
                ),
            )
        
        def create_action_button(icon: str, text: str, color: str, route: str):
            return ft.Container(
                expand=1,
                padding=25,
                border_radius=16,
                bgcolor=color,
                ink=True,
                on_click=lambda e: navigate(route),
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(icon, color=ft.Colors.WHITE, size=36),
                        ft.Container(height=10),
                        ft.Text(text, size=14, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                    ],
                ),
            )
        
        return ft.View(
            route="/home",
            bgcolor=ModernTheme.BG_PRIMARY,
            padding=0,
            controls=[
                ft.Row(
                    expand=True,
                    controls=[
                        # Sidebar
                        ft.Container(
                            width=280,
                            bgcolor=ModernTheme.BG_SECONDARY,
                            padding=20,
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.VERIFIED_USER, color=ModernTheme.PRIMARY, size=32),
                                            ft.Text("QualiManager", size=20, weight=ft.FontWeight.BOLD, color=ModernTheme.TEXT_PRIMARY),
                                        ],
                                    ),
                                    ft.Divider(height=30, color=ModernTheme.BG_TERTIARY),
                                    
                                    # Menu items
                                    ft.NavigationRail(
                                        selected_index=0,
                                        label_type=ft.NavigationRailLabelType.ALL,
                                        bgcolor="transparent",
                                        destinations=[
                                            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD, label="Dashboard"),
                                            ft.NavigationRailDestination(icon=ft.Icons.WARNING_AMBER, label="Non-Conformités"),
                                            ft.NavigationRailDestination(icon=ft.Icons.ANALYTICS, label="Analyses"),
                                            ft.NavigationRailDestination(icon=ft.Icons.PEOPLE, label="Utilisateurs"),
                                            ft.NavigationRailDestination(icon=ft.Icons.SETTINGS, label="Paramètres"),
                                        ],
                                    ),
                                    
                                    ft.Container(expand=True),
                                    
                                    # User info
                                    ft.Container(
                                        padding=15,
                                        border_radius=12,
                                        bgcolor=ModernTheme.BG_TERTIARY,
                                        content=ft.Row(
                                            controls=[
                                                ft.CircleAvatar(
                                                    content=ft.Text(current_user.get("name", "U")[0]),
                                                    bgcolor=ModernTheme.PRIMARY,
                                                ),
                                                ft.Column(
                                                    spacing=0,
                                                    controls=[
                                                        ft.Text(current_user.get("name", "User"), size=14, weight=ft.FontWeight.W_500, color=ModernTheme.TEXT_PRIMARY),
                                                        ft.Text(current_user.get("role", "Role"), size=12, color=ModernTheme.TEXT_MUTED),
                                                    ],
                                                ),
                                                ft.IconButton(ft.Icons.LOGOUT, icon_color=ModernTheme.TEXT_MUTED, on_click=lambda e: navigate("/login")),
                                            ],
                                        ),
                                    ),
                                ],
                            ),
                        ),
                        
                        # Main content
                        ft.Container(
                            expand=True,
                            padding=30,
                            content=ft.Column(
                                scroll=ft.ScrollMode.AUTO,
                                controls=[
                                    # Header
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Column(
                                                spacing=5,
                                                controls=[
                                                    ft.Text(f"Bonjour, {current_user.get('name', 'User')} 👋", size=28, weight=ft.FontWeight.BOLD, color=ModernTheme.TEXT_PRIMARY),
                                                    ft.Text(datetime.now().strftime("%A %d %B %Y"), size=14, color=ModernTheme.TEXT_MUTED),
                                                ],
                                            ),
                                            ft.ElevatedButton(
                                                "Nouvelle NC",
                                                icon=ft.Icons.ADD,
                                                style=ft.ButtonStyle(bgcolor=ModernTheme.PRIMARY, color=ft.Colors.WHITE, padding=15, shape=ft.RoundedRectangleBorder(radius=12)),
                                                on_click=lambda e: navigate("/nc/new"),
                                            ),
                                        ],
                                    ),
                                    
                                    ft.Container(height=30),
                                    
                                    # Stats cards
                                    ft.Row(
                                        controls=[
                                            create_stat_card(ft.Icons.WARNING_AMBER, "NC Ouvertes", "12", ModernTheme.DANGER, "↓ -3"),
                                            create_stat_card(ft.Icons.PENDING_ACTIONS, "En cours", "8", ModernTheme.WARNING, None),
                                            create_stat_card(ft.Icons.CHECK_CIRCLE, "Résolues", "156", ModernTheme.SUCCESS, "↑ +12"),
                                            create_stat_card(ft.Icons.SCHEDULE, "Délai moyen", "4.2j", ModernTheme.INFO, None),
                                        ],
                                    ),
                                    
                                    ft.Container(height=30),
                                    
                                    # Quick actions
                                    ft.Text("Actions rapides", size=20, weight=ft.FontWeight.BOLD, color=ModernTheme.TEXT_PRIMARY),
                                    ft.Container(height=15),
                                    ft.Row(
                                        controls=[
                                            create_action_button(ft.Icons.ADD_ALERT, "Signaler NC", ModernTheme.DANGER, "/nc/new"),
                                            create_action_button(ft.Icons.ANALYTICS, "Analyse causes", ModernTheme.SECONDARY, "/analysis"),
                                            create_action_button(ft.Icons.ASSESSMENT, "Rapports", ModernTheme.INFO, "/reports"),
                                            create_action_button(ft.Icons.INVENTORY, "Audits", ModernTheme.SUCCESS, "/audits"),
                                        ],
                                    ),
                                    
                                    ft.Container(height=30),
                                    
                                    # Recent NC table
                                    ft.Text("Non-conformités récentes", size=20, weight=ft.FontWeight.BOLD, color=ModernTheme.TEXT_PRIMARY),
                                    ft.Container(height=15),
                                    ft.Container(
                                        border_radius=16,
                                        bgcolor=ModernTheme.BG_SECONDARY,
                                        padding=20,
                                        content=ft.DataTable(
                                            columns=[
                                                ft.DataColumn(ft.Text("Référence", color=ModernTheme.TEXT_MUTED)),
                                                ft.DataColumn(ft.Text("Date", color=ModernTheme.TEXT_MUTED)),
                                                ft.DataColumn(ft.Text("Type", color=ModernTheme.TEXT_MUTED)),
                                                ft.DataColumn(ft.Text("Gravité", color=ModernTheme.TEXT_MUTED)),
                                                ft.DataColumn(ft.Text("Statut", color=ModernTheme.TEXT_MUTED)),
                                            ],
                                            rows=[
                                                ft.DataRow(cells=[
                                                    ft.DataCell(ft.Text("NC-2024-001", color=ModernTheme.TEXT_PRIMARY)),
                                                    ft.DataCell(ft.Text("18/12/2024", color=ModernTheme.TEXT_SECONDARY)),
                                                    ft.DataCell(ft.Text("Produit", color=ModernTheme.TEXT_SECONDARY)),
                                                    ft.DataCell(ft.Container(
                                                        padding=ft.padding.symmetric(8, 12),
                                                        border_radius=8,
                                                        bgcolor=ft.Colors.with_opacity(0.15, ModernTheme.DANGER),
                                                        content=ft.Text("Critique", color=ModernTheme.DANGER, size=12),
                                                    )),
                                                    ft.DataCell(ft.Container(
                                                        padding=ft.padding.symmetric(8, 12),
                                                        border_radius=8,
                                                        bgcolor=ft.Colors.with_opacity(0.15, ModernTheme.WARNING),
                                                        content=ft.Text("En cours", color=ModernTheme.WARNING, size=12),
                                                    )),
                                                ]),
                                                ft.DataRow(cells=[
                                                    ft.DataCell(ft.Text("NC-2024-002", color=ModernTheme.TEXT_PRIMARY)),
                                                    ft.DataCell(ft.Text("17/12/2024", color=ModernTheme.TEXT_SECONDARY)),
                                                    ft.DataCell(ft.Text("Process", color=ModernTheme.TEXT_SECONDARY)),
                                                    ft.DataCell(ft.Container(
                                                        padding=ft.padding.symmetric(8, 12),
                                                        border_radius=8,
                                                        bgcolor=ft.Colors.with_opacity(0.15, ModernTheme.WARNING),
                                                        content=ft.Text("Majeure", color=ModernTheme.WARNING, size=12),
                                                    )),
                                                    ft.DataCell(ft.Container(
                                                        padding=ft.padding.symmetric(8, 12),
                                                        border_radius=8,
                                                        bgcolor=ft.Colors.with_opacity(0.15, ModernTheme.SUCCESS),
                                                        content=ft.Text("Résolu", color=ModernTheme.SUCCESS, size=12),
                                                    )),
                                                ]),
                                            ],
                                        ),
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        )
    
    def create_nc_form_view() -> ft.View:
        """Formulaire NC moderne."""
        return ft.View(
            route="/nc/new",
            bgcolor=ModernTheme.BG_PRIMARY,
            appbar=ft.AppBar(
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("/home")),
                title=ft.Text("Nouvelle Non-Conformité"),
                bgcolor=ModernTheme.BG_SECONDARY,
            ),
            padding=30,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    border_radius=20,
                    bgcolor=ModernTheme.BG_SECONDARY,
                    padding=30,
                    content=ft.Column(
                        controls=[
                            ft.Text("📝 Informations générales", size=20, weight=ft.FontWeight.BOLD, color=ModernTheme.TEXT_PRIMARY),
                            ft.Divider(height=20, color=ModernTheme.BG_TERTIARY),
                            
                            ft.Row(
                                controls=[
                                    ft.TextField(label="Référence", prefix_icon=ft.Icons.TAG, expand=1, border_radius=12, filled=True, bgcolor=ModernTheme.BG_TERTIARY),
                                    ft.TextField(label="Date détection", prefix_icon=ft.Icons.CALENDAR_TODAY, expand=1, border_radius=12, filled=True, bgcolor=ModernTheme.BG_TERTIARY),
                                ],
                            ),
                            
                            ft.Row(
                                controls=[
                                    ft.Dropdown(
                                        label="Type de NC",
                                        options=[ft.dropdown.Option(t) for t in ["Produit", "Process", "Système", "Fournisseur", "Client"]],
                                        expand=1,
                                        border_radius=12,
                                        filled=True,
                                        bgcolor=ModernTheme.BG_TERTIARY,
                                    ),
                                    ft.Dropdown(
                                        label="Gravité",
                                        options=[ft.dropdown.Option(g) for g in ["Mineure", "Majeure", "Critique"]],
                                        expand=1,
                                        border_radius=12,
                                        filled=True,
                                        bgcolor=ModernTheme.BG_TERTIARY,
                                    ),
                                ],
                            ),
                            
                            ft.TextField(
                                label="Description du problème",
                                multiline=True,
                                min_lines=4,
                                border_radius=12,
                                filled=True,
                                bgcolor=ModernTheme.BG_TERTIARY,
                            ),
                            
                            ft.Container(height=20),
                            ft.Text("🔍 Analyse des causes", size=20, weight=ft.FontWeight.BOLD, color=ModernTheme.TEXT_PRIMARY),
                            ft.Divider(height=20, color=ModernTheme.BG_TERTIARY),
                            
                            ft.Row(
                                controls=[
                                    ft.ElevatedButton(
                                        "5 Pourquoi",
                                        icon=ft.Icons.HELP,
                                        style=ft.ButtonStyle(bgcolor=ModernTheme.BG_TERTIARY, color=ModernTheme.TEXT_PRIMARY),
                                        on_click=lambda e: navigate("/analysis"),
                                    ),
                                    ft.ElevatedButton(
                                        "Ishikawa",
                                        icon=ft.Icons.ACCOUNT_TREE,
                                        style=ft.ButtonStyle(bgcolor=ModernTheme.BG_TERTIARY, color=ModernTheme.TEXT_PRIMARY),
                                    ),
                                    ft.ElevatedButton(
                                        "AMDEC",
                                        icon=ft.Icons.GRID_VIEW,
                                        style=ft.ButtonStyle(bgcolor=ModernTheme.BG_TERTIARY, color=ModernTheme.TEXT_PRIMARY),
                                    ),
                                ],
                            ),
                            
                            ft.Container(height=30),
                            
                            ft.Row(
                                alignment=ft.MainAxisAlignment.END,
                                controls=[
                                    ft.OutlinedButton("Annuler", on_click=lambda e: navigate("/home")),
                                    ft.ElevatedButton(
                                        "Enregistrer",
                                        icon=ft.Icons.SAVE,
                                        style=ft.ButtonStyle(bgcolor=ModernTheme.SUCCESS, color=ft.Colors.WHITE, padding=15),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ],
        )
    
    def create_analysis_view() -> ft.View:
        """Page d'analyse des causes."""
        
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="5 Pourquoi", icon=ft.Icons.HELP),
                ft.Tab(text="Ishikawa", icon=ft.Icons.ACCOUNT_TREE),
                ft.Tab(text="AMDEC", icon=ft.Icons.GRID_VIEW),
                ft.Tab(text="8D", icon=ft.Icons.FORMAT_LIST_NUMBERED),
                ft.Tab(text="Pareto", icon=ft.Icons.BAR_CHART),
            ],
        )
        
        # Contenu 5 Pourquoi
        why_controls = []
        colors = [ModernTheme.DANGER, ModernTheme.WARNING, ModernTheme.SUCCESS, ModernTheme.PRIMARY, ModernTheme.SECONDARY]
        
        for i in range(5):
            why_controls.append(
                ft.Container(
                    margin=ft.margin.only(bottom=15),
                    padding=20,
                    border_radius=16,
                    bgcolor=ModernTheme.BG_SECONDARY,
                    border=ft.border.all(2, colors[i]),
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        width=50, height=50,
                                        border_radius=25,
                                        bgcolor=colors[i],
                                        content=ft.Text(f"P{i+1}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                                        alignment=ft.alignment.center,
                                    ),
                                    ft.Column(
                                        expand=True,
                                        controls=[
                                            ft.TextField(
                                                label=f"Pourquoi {i+1} ?",
                                                border_radius=12,
                                                filled=True,
                                                bgcolor=ModernTheme.BG_TERTIARY,
                                            ),
                                            ft.TextField(
                                                label="Réponse",
                                                border_radius=12,
                                                filled=True,
                                                bgcolor=ModernTheme.BG_TERTIARY,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                )
            )
        
        return ft.View(
            route="/analysis",
            bgcolor=ModernTheme.BG_PRIMARY,
            appbar=ft.AppBar(
                leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: navigate("/home")),
                title=ft.Text("🔬 Analyse des Causes"),
                bgcolor=ModernTheme.BG_SECONDARY,
            ),
            padding=20,
            controls=[
                tabs,
                ft.Container(
                    expand=True,
                    padding=20,
                    content=ft.Column(
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            ft.Container(
                                padding=20,
                                border_radius=16,
                                bgcolor=ModernTheme.BG_SECONDARY,
                                content=ft.Column(
                                    controls=[
                                        ft.Text("🎯 Problème initial", size=16, weight=ft.FontWeight.BOLD, color=ModernTheme.TEXT_PRIMARY),
                                        ft.TextField(
                                            multiline=True,
                                            min_lines=2,
                                            border_radius=12,
                                            filled=True,
                                            bgcolor=ModernTheme.BG_TERTIARY,
                                            hint_text="Décrivez le problème à analyser...",
                                        ),
                                    ],
                                ),
                            ),
                            ft.Container(height=20),
                            *why_controls,
                            ft.Container(
                                padding=20,
                                border_radius=16,
                                bgcolor=ModernTheme.SECONDARY,
                                content=ft.Column(
                                    controls=[
                                        ft.Text("🎯 CAUSE RACINE IDENTIFIÉE", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                        ft.TextField(
                                            border_radius=12,
                                            filled=True,
                                            bgcolor=ft.Colors.WHITE,
                                            color=ModernTheme.BG_PRIMARY,
                                            hint_text="Synthèse de la cause racine...",
                                        ),
                                    ],
                                ),
                            ),
                            ft.Container(height=20),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.ElevatedButton(
                                        "💾 Sauvegarder l'analyse",
                                        style=ft.ButtonStyle(bgcolor=ModernTheme.SUCCESS, color=ft.Colors.WHITE, padding=20),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ],
        )
    
    # Démarrer sur la page login
    navigate("/login")


if __name__ == "__main__":
    ft.app(target=main)

# -*- coding: utf-8 -*-
"""
QualiManager ERP QHSE - Module Rapports
Page dédiée à la génération de rapports personnalisés
"""

import flet as ft
from flet_core.dropdown import Option as DropdownOption
from typing import Dict, Any, Callable
from .theme import Theme


class ReportsPage(ft.Container):
    """Page de génération de rapports personnalisés."""
    
    def __init__(
        self,
        user: Dict[str, Any],
        db,
        navigate: Callable,
    ):
        self.user = user
        self.db = db
        self.navigate = navigate
        
        super().__init__(
            expand=True,
            bgcolor=Theme.BG_PRIMARY,
            padding=30,
            content=self._build(),
        )
    
    def did_mount(self):
        """Appelé lorsque le composant est monté."""
        pass
    
    def _build(self):
        """Construit l'interface de la page des rapports."""
        return ft.Column(
            expand=True,
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            auto_scroll=False,
            alignment=ft.MainAxisAlignment.START,
            controls=[
                # Header
                ft.Container(
                    padding=20,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.DESCRIPTION, size=32, color=ft.Colors.BLUE_700),
                                    ft.Column(
                                        spacing=0,
                                        controls=[
                                            ft.Text(
                                                "[PDF] Rapports",
                                                size=28,
                                                weight=ft.FontWeight.BOLD,
                                                color=Theme.TEXT_PRIMARY,
                                            ),
                                            ft.Text(
                                                "Génération de rapports personnalisés",
                                                size=14,
                                                color=Theme.TEXT_MUTED,
                                            ),
                                        ]
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                # Section rapports personnalisés
                ft.Container(
                    padding=20,
                    bgcolor=Theme.BG_SECONDARY,
                    border_radius=10,
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            ft.Text(
                                "[Outil] Rapport Personnalisé",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.TEXT_PRIMARY,
                            ),
                            ft.Divider(height=1, color=Theme.OUTLINE),
                            ft.Text(
                                "Sélectionnez vos critères pour générer un rapport sur mesure",
                                size=14,
                                color=Theme.TEXT_SECONDARY,
                            ),
                            ft.Row(
                                spacing=15,
                                wrap=True,
                                controls=[
                                    ft.TextField(
                                        label="Date début",
                                        hint_text="AAAA-MM-JJ",
                                        width=200,
                                        suffix=ft.Icon(ft.Icons.CALENDAR_TODAY),
                                    ),
                                    ft.TextField(
                                        label="Date fin",
                                        hint_text="AAAA-MM-JJ",
                                        width=200,
                                        suffix=ft.Icon(ft.Icons.CALENDAR_TODAY),
                                    ),
                                    ft.Dropdown(
                                        label="Type NC",
                                        hint_text="Tous",
                                        width=200,
                                        options=[
                                            DropdownOption("Tous"),
                                            DropdownOption("Interne"),
                                            DropdownOption("Client"),
                                            DropdownOption("Fournisseur"),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Row(
                                spacing=15,
                                controls=[
                                    ft.ElevatedButton(
                                        "[PDF] Générer PDF",
                                        icon=ft.Icons.PICTURE_AS_PDF,
                                        on_click=lambda e: self._generate_report("pdf"),
                                        bgcolor=Theme.PRIMARY,
                                        color="#FFFFFF",
                                    ),
                                    ft.ElevatedButton(
                                        "[Stats] Exporter Excel",
                                        icon=ft.Icons.TABLE_CHART,
                                        on_click=lambda e: self._generate_report("excel"),
                                        bgcolor=ft.Colors.GREEN_600,
                                        color="#FFFFFF",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ],
        )
    
    def _generate_report(self, format_type: str):
        """Génère un rapport dans le format spécifié."""
        # TODO: Implémenter la génération de rapports
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Génération du rapport {format_type.upper()} en cours..."),
                bgcolor=Theme.INFO,
            )
            self.page.snack_bar.open = True
            self.page.update()

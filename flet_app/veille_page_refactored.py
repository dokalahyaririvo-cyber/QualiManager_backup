# -*- coding: utf-8 -*-
"""
Page Veille Réglementaire & Exigences Client - Version Refactorisée.
Architecture : Pages séparées pour les formulaires, tableaux plein écran.
"""
import flet as ft
from database.veille_db_manager import VeilleDBManager
from flet_app.theme import Theme
from flet_app.components import create_button, create_text_field, create_dropdown, create_snackbar
from datetime import datetime
import json
from typing import Dict, Optional, List
import pandas as pd
from pathlib import Path


class VeillePage(ft.Container):
    """Page principale du module Veille Réglementaire avec navigation vers sous-pages."""
    
    def __init__(self, user, db, navigate):
        super().__init__()
        self.user = user
        self.db_general = db
        self.navigate = navigate
        self.db = VeilleDBManager()
        self.expand = True
        
        # État navigation
        self.current_view = "main"  # main, veille_form, plan_form
        self.current_tab = 0
        self.edit_veille_id = None
        self.edit_plan_id = None
        
        # FilePicker
        self.file_picker = None
        self.selected_file_path = None
        
        # Construction
        self.content = self._build_main_view()
    
    def did_mount(self):
        """Initialisation après montage."""
        if not self.file_picker and self.page:
            self.file_picker = ft.FilePicker(on_result=self._on_file_picked)
            self.page.overlay.append(self.file_picker)
            self.page.update()
    
    def _navigate_to(self, view: str, **kwargs):
        """Navigation interne entre vues."""
        self.current_view = view
        
        if view == "main":
            self.content = self._build_main_view()
        elif view == "veille_form":
            self.edit_veille_id = kwargs.get("veille_id")
            self.content = self._build_veille_form_page()
        elif view == "plan_form":
            self.edit_plan_id = kwargs.get("plan_id")
            self.content = self._build_plan_form_page()
        
        if self.page:
            self.page.update()
    
    # ==================== VUE PRINCIPALE ====================
    
    def _build_main_view(self):
        """Vue principale avec onglets."""
        header = ft.Container(
            padding=20,
            bgcolor=Theme.PRIMARY,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=15,
                        controls=[
                            ft.Icon(ft.Icons.GAVEL_ROUNDED, size=32, color=ft.Colors.WHITE),
                            ft.Text(
                                "Veille Réglementaire & Exigences Client",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                    ),
                ],
            ),
        )
        
        # Onglets
        self.tabs = ft.Tabs(
            selected_index=self.current_tab,
            animation_duration=300,
            on_change=self._on_tab_change,
            scrollable=False,
            tab_alignment=ft.TabAlignment.START,
            label_color=Theme.PRIMARY,
            unselected_label_color=Theme.TEXT_MUTED,
            indicator_color=Theme.PRIMARY,
            indicator_tab_size=True,
            divider_color=Theme.OUTLINE,
            tabs=[
                ft.Tab(text="[Registre] Registre des Veilles", icon=ft.Icons.ARTICLE_ROUNDED),
                ft.Tab(text="[Actions] Plans d'Actions", icon=ft.Icons.FACT_CHECK_ROUNDED),
                ft.Tab(text="[Stats] Tableau de Bord", icon=ft.Icons.DASHBOARD_ROUNDED),
            ],
        )
        
        # Contenu onglet
        self.tab_content = ft.Container(
            expand=True,
            padding=20,
            content=self._get_current_tab_content(),
        )
        
        return ft.Column(
            expand=True,
            spacing=0,
            controls=[header, self.tabs, self.tab_content],
        )
    
    def _on_tab_change(self, e):
        """Changement d'onglet."""
        self.current_tab = e.control.selected_index
        self.tab_content.content = self._get_current_tab_content()
        if self.page:
            self.page.update()
    
    def _get_current_tab_content(self):
        """Retourne le contenu de l'onglet actuel."""
        if self.current_tab == 0:
            return self._build_registre_tab()
        elif self.current_tab == 1:
            return self._build_plans_tab()
        elif self.current_tab == 2:
            return self._build_dashboard_tab()
    
    # ==================== ONGLET 1 : REGISTRE VEILLES ====================
    
    def _build_registre_tab(self):
        """Tableau des veilles avec actions."""
        veilles = self.db.get_all_veilles()
        
        # Barre d'actions
        actions_bar = ft.Container(
            padding=15,
            bgcolor=Theme.BG_SECONDARY,
            border_radius=10,
            margin=15,
            content=ft.Row(
                spacing=15,
                controls=[
                    ft.ElevatedButton(
                        "Nouvelle Veille",
                        icon=ft.Icons.ADD,
                        bgcolor=Theme.PRIMARY,
                        color=ft.Colors.WHITE,
                        on_click=lambda e: self._navigate_to("veille_form"),
                    ),
                    ft.ElevatedButton(
                        "Importer Excel",
                        icon=ft.Icons.UPLOAD_FILE,
                        on_click=lambda e: self._import_excel(),
                    ),
                    ft.PopupMenuButton(
                        icon=ft.Icons.DOWNLOAD,
                        tooltip="Exporter",
                        items=[
                            ft.PopupMenuItem(text="[PDF] Exporter en PDF", on_click=lambda e: self._export_veilles("pdf")),
                            ft.PopupMenuItem(text="[Stats] Exporter en Excel", on_click=lambda e: self._export_veilles("excel")),
                        ],
                    ),
                ],
            ),
        )
        
        # Tableau
        if not veilles:
            table_content = ft.Container(
                expand=True,
                padding=40,
                alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.INBOX, size=64, color=Theme.TEXT_MUTED),
                        ft.Text("Aucune veille enregistrée", size=16, color=Theme.TEXT_MUTED),
                    ],
                ),
            )
        else:
            rows = []
            for v in veilles:
                status_color = self._get_status_color(v['statut_veille'])
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(v['id']), size=12)),
                            ft.DataCell(ft.Text(v['source'] or '-', size=12, width=150)),
                            ft.DataCell(ft.Text(str(v['annee']) if v['annee'] else '-', size=12)),
                            ft.DataCell(ft.Text(v['date_publication'] or '-', size=12)),
                            ft.DataCell(
                                ft.Container(
                                    width=300,
                                    content=ft.Text(
                                        (v['description'] or '-')[:80] + ('...' if len(v['description'] or '') > 80 else ''),
                                        size=12,
                                    ),
                                ),
                            ),
                            ft.DataCell(
                                ft.Container(
                                    padding=8,
                                    bgcolor=ft.Colors.with_opacity(0.2, status_color),
                                    border_radius=5,
                                    content=ft.Text(
                                        v['statut_veille'] or '-',
                                        size=11,
                                        weight=ft.FontWeight.BOLD,
                                        color=status_color,
                                    ),
                                ),
                            ),
                            ft.DataCell(ft.Text("[OK]" if v['plan_action_id'] else "-", size=12)),
                            ft.DataCell(
                                ft.Row(
                                    spacing=5,
                                    controls=[
                                        ft.IconButton(
                                            icon=ft.Icons.EDIT,
                                            icon_size=18,
                                            tooltip="Modifier",
                                            on_click=lambda e, vid=v['id']: self._navigate_to("veille_form", veille_id=vid),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE,
                                            icon_size=18,
                                            tooltip="Supprimer",
                                            on_click=lambda e, vid=v['id']: self._delete_veille(vid),
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    )
                )
            
            table_content = ft.Container(
                expand=True,
                content=ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("No", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Source", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Année", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Date Pub.", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Description", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Statut", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("P.A.", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD)),
                            ],
                            rows=rows,
                            border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                            border_radius=10,
                            horizontal_lines=ft.BorderSide(1, Theme.OUTLINE),
                            heading_row_color=Theme.BG_SECONDARY,
                        ),
                    ],
                ),
            )
        
        return ft.Column(
            expand=True,
            spacing=0,
            controls=[actions_bar, table_content],
        )
    
    # ==================== ONGLET 2 : PLANS D'ACTIONS ====================
    
    def _build_plans_tab(self):
        """Tableau des plans d'actions."""
        plans = self.db.get_all_action_plans()
        
        # Barre d'actions
        actions_bar = ft.Container(
            padding=15,
            bgcolor=Theme.BG_SECONDARY,
            border_radius=10,
            margin=15,
            content=ft.Row(
                spacing=15,
                controls=[
                    ft.ElevatedButton(
                        "Nouveau Plan d'Action",
                        icon=ft.Icons.ADD,
                        bgcolor=Theme.SECONDARY,
                        color=ft.Colors.WHITE,
                        on_click=lambda e: self._navigate_to("plan_form"),
                    ),
                ],
            ),
        )
        
        # Tableau
        if not plans:
            table_content = ft.Container(
                expand=True,
                padding=40,
                alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.ASSIGNMENT, size=64, color=Theme.TEXT_MUTED),
                        ft.Text("Aucun plan d'action", size=16, color=Theme.TEXT_MUTED),
                    ],
                ),
            )
        else:
            rows = []
            for p in plans:
                avancement = p.get('statut_calcule', 0.0)
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(f"PA-{p['id']}", size=12, weight=ft.FontWeight.BOLD)),
                            ft.DataCell(ft.Text(p['origine'] or '-', size=12, width=150)),
                            ft.DataCell(ft.Text(p['date_creation'] or '-', size=12)),
                            ft.DataCell(
                                ft.Container(
                                    width=200,
                                    content=ft.Text((p['resume_origine'] or '-')[:60] + ('...' if len(p.get('resume_origine', '')) > 60 else ''), size=12),
                                ),
                            ),
                            ft.DataCell(ft.Text(p['priorite'] or '-', size=12)),
                            ft.DataCell(ft.Text(p['type_action'] or '-', size=12)),
                            ft.DataCell(ft.Text(p['date_fin_prevue'] or '-', size=12)),
                            ft.DataCell(
                                ft.Container(
                                    width=120,
                                    content=ft.Column(
                                        spacing=5,
                                        controls=[
                                            ft.ProgressBar(value=avancement / 100, width=100, height=8, color=ft.Colors.GREEN_500),
                                            ft.Text(f"{avancement:.0f}%", size=10, text_align=ft.TextAlign.CENTER),
                                        ],
                                    ),
                                ),
                            ),
                            ft.DataCell(ft.Text("[OK]" if p['date_solde'] else "[EnCours]", size=12)),
                            ft.DataCell(
                                ft.Row(
                                    spacing=5,
                                    controls=[
                                        ft.IconButton(
                                            icon=ft.Icons.EDIT,
                                            icon_size=18,
                                            tooltip="Modifier",
                                            on_click=lambda e, pid=p['id']: self._navigate_to("plan_form", plan_id=pid),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE,
                                            icon_size=18,
                                            tooltip="Supprimer",
                                            on_click=lambda e, pid=p['id']: self._delete_plan(pid),
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    )
                )
            
            table_content = ft.Container(
                expand=True,
                content=ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("No", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Origine", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Création", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Résumé", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Priorité", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Échéance", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Avancement", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Statut", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD)),
                            ],
                            rows=rows,
                            border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                            border_radius=10,
                            horizontal_lines=ft.BorderSide(1, Theme.OUTLINE),
                            heading_row_color=Theme.BG_SECONDARY,
                        ),
                    ],
                ),
            )
        
        return ft.Column(
            expand=True,
            spacing=0,
            controls=[actions_bar, table_content],
        )
    
    # ==================== ONGLET 3 : TABLEAU DE BORD ====================
    
    def _build_dashboard_tab(self):
        """Tableau de bord avec statistiques."""
        stats_veilles = self.db.get_veilles_stats()
        stats_plans = self.db.get_action_plans_stats()
        todo = self.db.get_todo_items()
        
        # Stats veilles
        total = stats_veilles.get('total_annee', 0)
        statuts_dict = stats_veilles.get('statuts', {})
        conformes = statuts_dict.get('Conforme', 0)
        concernes = statuts_dict.get('Concerné', 0)
        a_etudier = statuts_dict.get('À l\'étude', 0)
        
        stats_cards = ft.Row(
            spacing=15,
            wrap=True,
            controls=[
                self._create_stat_card("[ID] Total Veilles", str(total), Theme.PRIMARY),
                self._create_stat_card("[OK] Conformes", str(conformes), ft.Colors.GREEN_500),
                self._create_stat_card("[Attention] Concernés", str(concernes), ft.Colors.ORANGE_500),
                self._create_stat_card("[Recherche] À Étudier", str(a_etudier), ft.Colors.YELLOW_700),
            ],
        )
        
        # Graphique
        chart_container = ft.Container(
            padding=20,
            bgcolor=Theme.BG_CARD,
            border_radius=10,
            border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Text("[Stats] Répartition des Statuts", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    ft.Column(
                        spacing=10,
                        controls=[
                            self._create_bar_chart_row("Conformes", conformes, total, ft.Colors.GREEN_400),
                            self._create_bar_chart_row("Concernés", concernes, total, ft.Colors.ORANGE_400),
                            self._create_bar_chart_row("À Étudier", a_etudier, total, ft.Colors.YELLOW_600),
                        ],
                    ),
                ],
            ),
        )
        
        # Plans d'actions
        plans_card = ft.Container(
            padding=20,
            bgcolor=Theme.BG_CARD,
            border_radius=10,
            border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.FACT_CHECK, size=28, color=ft.Colors.GREEN_700),
                            ft.Text("Plans d'Actions", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                        ],
                    ),
                    ft.Row(
                        spacing=30,
                        controls=[
                            ft.Text(f"[OK] Soldées: {stats_plans['soldees']}", size=14, weight=ft.FontWeight.W_500, color=Theme.TEXT_PRIMARY),
                            ft.Text(f"[EnCours] En cours: {stats_plans['en_cours']}", size=14, weight=ft.FontWeight.W_500, color=Theme.TEXT_PRIMARY),
                        ],
                    ),
                    ft.ProgressBar(
                        value=stats_plans['soldees'] / (stats_plans['soldees'] + stats_plans['en_cours']) if (stats_plans['soldees'] + stats_plans['en_cours']) > 0 else 0,
                        color=ft.Colors.GREEN_700,
                        bgcolor=Theme.OUTLINE,
                        height=10,
                    ),
                ],
            ),
        )
        
        # TODO List
        todo_cards = []
        if todo['veilles_etude']:
            for v in todo['veilles_etude']:
                todo_cards.append(self._create_todo_card("veille", v))
        
        if todo['plans_retard']:
            for p in todo['plans_retard']:
                todo_cards.append(self._create_todo_card("plan", p))
        
        if not todo_cards:
            todo_cards.append(
                ft.Container(
                    padding=30,
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=10,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.GREEN_700, size=40),
                            ft.Text("[OK] Aucune action en attente", size=16, color=ft.Colors.GREEN_700, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                )
            )
        
        return ft.Column(
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("[Stats] Tableau de Bord", size=24, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                stats_cards,
                ft.Row(spacing=15, wrap=True, controls=[chart_container, plans_card]),
                ft.Divider(height=2, color=Theme.OUTLINE),
                ft.Text("[Note] Actions Prioritaires", size=20, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                ft.Column(spacing=10, controls=todo_cards),
            ],
        )
    
    def _create_stat_card(self, title, value, color):
        """Crée une carte stat."""
        return ft.Container(
            width=200,
            height=120,
            padding=20,
            bgcolor=Theme.BG_CARD,
            border_radius=10,
            border=ft.Border(
                top=ft.BorderSide(2, color),
                right=ft.BorderSide(2, color),
                bottom=ft.BorderSide(2, color),
                left=ft.BorderSide(2, color),
            ),
            content=ft.Column(
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text(title, size=14, color=Theme.TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                    ft.Text(value, size=32, weight=ft.FontWeight.BOLD, color=color),
                ],
            ),
        )
    
    def _create_bar_chart_row(self, label, value, total, color):
        """Crée une barre de graphique."""
        percentage = (value / total * 100) if total > 0 else 0
        return ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(width=100, content=ft.Text(label, size=13, weight=ft.FontWeight.W_500, color=Theme.TEXT_PRIMARY)),
                ft.Container(
                    expand=True,
                    height=30,
                    bgcolor=Theme.OUTLINE,
                    border_radius=5,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                expand=int(percentage) if percentage > 0 else 0,
                                height=30,
                                bgcolor=color,
                                alignment=ft.Alignment(-1, 0),
                                padding=10,
                                content=ft.Text(f"{value}", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE) if percentage > 5 else ft.Container(),
                            ),
                            ft.Container(expand=int(100-percentage)) if percentage > 0 else ft.Container(expand=1),
                        ],
                    ),
                ),
                ft.Text(f"{percentage:.0f}%", size=13, weight=ft.FontWeight.BOLD, color=color, width=50),
            ],
        )
    
    def _create_todo_card(self, item_type, item):
        """Crée une carte TODO."""
        if item_type == "veille":
            icon = ft.Icons.ARTICLE_OUTLINED
            color = ft.Colors.ORANGE_500
            bgcolor = ft.Colors.ORANGE_50
            title = f"No{item['id']} - {item['source']}"
            desc = item['description']
            action = lambda e: self._navigate_to("veille_form", veille_id=item['id'])
        else:
            icon = ft.Icons.ASSIGNMENT_LATE_OUTLINED
            color = ft.Colors.RED_500
            bgcolor = ft.Colors.RED_50
            title = f"PA-{item['id']} - {item['source']}"
            desc = f"Échéance : {item['date_fin_prevue']}"
            action = lambda e: self._navigate_to("plan_form", plan_id=item['id'])
        
        return ft.Container(
            padding=15,
            bgcolor=bgcolor,
            border_radius=10,
            border=ft.Border(
                top=ft.BorderSide(1, color),
                right=ft.BorderSide(1, color),
                bottom=ft.BorderSide(1, color),
                left=ft.BorderSide(1, color),
            ),
            content=ft.Row(
                spacing=15,
                controls=[
                    ft.Icon(icon, size=28, color=color),
                    ft.Column(
                        expand=True,
                        spacing=5,
                        controls=[
                            ft.Text(title, size=14, weight=ft.FontWeight.BOLD),
                            ft.Text(desc[:100] + ('...' if len(desc) > 100 else ''), size=12),
                        ],
                    ),
                    ft.ElevatedButton("Ouvrir", icon=ft.Icons.ARROW_FORWARD, bgcolor=color, color=ft.Colors.WHITE, on_click=action),
                ],
            ),
        )
    
    # ==================== HELPERS ====================
    
    def _get_status_color(self, statut):
        """Retourne la couleur selon le statut."""
        if statut == 'Concerné':
            return ft.Colors.ORANGE_700
        elif statut == 'Conforme':
            return ft.Colors.GREEN_700
        elif statut == 'À l\'étude':
            return ft.Colors.BLUE_700
        else:
            return ft.Colors.GREY_700
    
    def _on_file_picked(self, e: ft.FilePickerResultEvent):
        """Callback file picker."""
        if e.files:
            self.selected_file_path = e.files[0].path
            if self.page:
                self.page.update()
    
    def _delete_veille(self, veille_id):
        """Supprime une veille."""
        self.db.delete_veille(veille_id)
        create_snackbar(self.page, "[OK] Veille supprimée", "success")
        self._navigate_to("main")
    
    def _delete_plan(self, plan_id):
        """Supprime un plan."""
        self.db.delete_action_plan(plan_id)
        create_snackbar(self.page, "[OK] Plan d'action supprimé", "success")
        self._navigate_to("main")
    
    def _import_excel(self):
        """Import Excel - À implémenter."""
        create_snackbar(self.page, "[Stats] Import Excel à implémenter", "info")
    
    def _export_veilles(self, format_type):
        """Export - À implémenter."""
        create_snackbar(self.page, f"[Export] Export {format_type} à implémenter", "info")
    
    # ==================== PAGE FORMULAIRE VEILLE ====================
    
    def _build_veille_form_page(self):
        """Page complète formulaire veille."""
        is_edit = self.edit_veille_id is not None
        veille = self.db.get_veille_by_id(self.edit_veille_id) if is_edit else None
        
        # En-tête
        header = ft.Container(
            padding=20,
            bgcolor=Theme.PRIMARY,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=15,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                icon_color=ft.Colors.WHITE,
                                on_click=lambda e: self._navigate_to("main"),
                            ),
                            ft.Icon(ft.Icons.ARTICLE_ROUNDED, color=ft.Colors.WHITE, size=28),
                            ft.Text(
                                "Modifier la Veille" if is_edit else "Nouvelle Veille",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                    ),
                ],
            ),
        )
        
        # Champs du formulaire
        source_field = ft.TextField(
            label="Source *",
            value=veille['source'] if is_edit else "",
            hint_text="Ex: Journal Officiel, Client X",
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.PRIMARY,
        )
        
        annee_field = ft.TextField(
            label="Année",
            value=str(veille['annee']) if is_edit and veille['annee'] else str(datetime.now().year),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.PRIMARY,
            width=150,
        )
        
        date_pub_field = ft.TextField(
            label="Date de Publication",
            value=veille['date_publication'] if is_edit else "",
            hint_text="YYYY-MM-DD",
            read_only=True,
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.PRIMARY,
            width=200,
            suffix=ft.IconButton(
                icon=ft.Icons.CALENDAR_MONTH,
                on_click=lambda e: self._open_date_picker(date_pub_field),
            ),
        )
        
        date_lecture_field = ft.TextField(
            label="Date de Lecture",
            value=veille['date_lecture'] if is_edit else datetime.now().strftime('%Y-%m-%d'),
            read_only=True,
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.PRIMARY,
            width=200,
            suffix=ft.IconButton(
                icon=ft.Icons.CALENDAR_MONTH,
                on_click=lambda e: self._open_date_picker(date_lecture_field),
            ),
        )
        
        description_field = ft.TextField(
            label="Description *",
            value=veille['description'] if is_edit else "",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.PRIMARY,
        )
        
        resume_field = ft.TextField(
            label="Résumé",
            value=veille['resume'] if is_edit else "",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.PRIMARY,
        )
        
        lien_field = ft.TextField(
            label="Lien URL",
            value=veille['lien_url'] if is_edit else "",
            hint_text="https://...",
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.PRIMARY,
        )
        
        commentaire_field = ft.TextField(
            label="Commentaire Interne",
            value=veille['commentaire_interne'] if is_edit else "",
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.PRIMARY,
        )
        
        statut_dropdown = ft.Dropdown(
            label="Statut de la Veille *",
            options=[
                "Non concerné",
                "À l'étude",
                "Concerné",
                "Conforme",
            ],
            value=veille['statut_veille'] if is_edit else "Non concerné",
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.PRIMARY,
        )
        
        # Fichier joint
        self.selected_file_path = veille['fichier_joint'] if is_edit else None
        fichier_display = ft.Text(
            Path(self.selected_file_path).name if self.selected_file_path else "Aucun fichier",
            size=12,
            color=Theme.TEXT_SECONDARY,
        )
        
        fichier_button = ft.ElevatedButton(
            "Joindre Fichier",
            icon=ft.Icons.ATTACH_FILE,
            on_click=lambda e: self.file_picker.pick_files() if self.file_picker else None,
        )
        
        # Checkbox plan d'action
        create_plan_checkbox = ft.Checkbox(
            label="Créer un Plan d'Action",
            value=False,
        )
        
        checkbox_container = ft.Container(
            visible=False if is_edit else (statut_dropdown.value == "Concerné"),
            content=create_plan_checkbox,
        )
        
        def on_statut_change(e):
            if not is_edit:
                checkbox_container.visible = (statut_dropdown.value == "Concerné")
                checkbox_container.update()
        
        statut_dropdown.on_change = on_statut_change
        
        # Formulaire
        form_content = ft.Container(
            expand=True,
            padding=30,
            content=ft.Column(
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    # Section Identification
                    ft.Container(
                        padding=20,
                        bgcolor=Theme.BG_CARD,
                        border_radius=10,
                        border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                        content=ft.Column(
                            spacing=15,
                            controls=[
                                ft.Text("[ID] Identification", size=16, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
                                source_field,
                                ft.Row(spacing=15, controls=[annee_field, date_pub_field, date_lecture_field]),
                            ],
                        ),
                    ),
                    # Section Contenu
                    ft.Container(
                        padding=20,
                        bgcolor=Theme.BG_CARD,
                        border_radius=10,
                        border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                        content=ft.Column(
                            spacing=15,
                            controls=[
                                ft.Text("[PDF] Contenu", size=16, weight=ft.FontWeight.BOLD, color=Theme.SECONDARY),
                                description_field,
                                resume_field,
                                lien_field,
                                commentaire_field,
                            ],
                        ),
                    ),
                    # Section Statut & Fichiers
                    ft.Container(
                        padding=20,
                        bgcolor=Theme.BG_CARD,
                        border_radius=10,
                        border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                        content=ft.Column(
                            spacing=15,
                            controls=[
                                ft.Text("[Config] Statut & Fichiers", size=16, weight=ft.FontWeight.BOLD, color=Theme.WARNING),
                                statut_dropdown,
                                ft.Row(spacing=10, controls=[fichier_button, fichier_display]),
                                checkbox_container,
                            ],
                        ),
                    ),
                ],
            ),
        )
        
        # Boutons actions
        def save_veille(e):
            if not source_field.value or not description_field.value:
                create_snackbar(self.page, "[Attention] Source et Description obligatoires", "error")
                return
            
            data = {
                'source': source_field.value,
                'annee': int(annee_field.value) if annee_field.value else None,
                'date_publication': date_pub_field.value,
                'description': description_field.value,
                'resume': resume_field.value,
                'lien_url': lien_field.value,
                'commentaire_interne': commentaire_field.value,
                'date_lecture': date_lecture_field.value,
                'statut_veille': statut_dropdown.value,
                'fichier_joint': self.selected_file_path,
            }
            
            if is_edit:
                self.db.update_veille(self.edit_veille_id, data)
                create_snackbar(self.page, "[OK] Veille mise à jour", "success")
            else:
                veille_id = self.db.create_veille(data)
                create_snackbar(self.page, f"[OK] Veille créée (No{veille_id})", "success")
                
                # Créer plan si demandé
                if create_plan_checkbox.value and statut_dropdown.value == "Concerné":
                    plan_data = {
                        'veille_id': veille_id,
                        'date_creation': datetime.now().strftime('%Y-%m-%d'),
                        'resume_origine': resume_field.value or description_field.value[:100],
                        'origine': source_field.value,
                        'objectif': '',
                        'priorite': 'Mineure',
                        'type_action': 'Amélioration',
                        'auteurs': '',
                        'date_fin_prevue': '',
                        'moyen_controle': '',
                        'date_solde': '',
                        'remarques': '',
                        'taches_liste': [],
                        'statut_calcule': 0.0,
                    }
                    plan_id = self.db.create_action_plan(plan_data)
                    create_snackbar(self.page, f"[OK] Plan d'action No{plan_id} créé", "info")
            
            self._navigate_to("main")
        
        actions_bar = ft.Container(
            padding=20,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.END,
                spacing=15,
                controls=[
                    ft.TextButton("Annuler", on_click=lambda e: self._navigate_to("main")),
                    ft.ElevatedButton(
                        "Supprimer" if is_edit else None,
                        icon=ft.Icons.DELETE,
                        on_click=lambda e: (self._delete_veille(self.edit_veille_id) if is_edit else None),
                    ) if is_edit else ft.Container(),
                    ft.ElevatedButton(
                        "Enregistrer",
                        icon=ft.Icons.SAVE,
                        bgcolor=Theme.PRIMARY,
                        color=ft.Colors.WHITE,
                        on_click=save_veille,
                    ),
                ],
            ),
        )
        
        return ft.Column(
            expand=True,
            spacing=0,
            controls=[header, form_content, actions_bar],
        )
    
    def _open_date_picker(self, target_field):
        """Ouvre le date picker pour un champ."""
        def on_change(e):
            if e.control.value:
                target_field.value = e.control.value.strftime('%Y-%m-%d')
                target_field.update()
        
        date_picker = ft.DatePicker(
            on_change=on_change,
            first_date=datetime(2000, 1, 1),
            last_date=datetime(2099, 12, 31),
        )
        
        self.page.overlay.append(date_picker)
        self.page.update()
        date_picker.open = True
        self.page.update()
    
    # ==================== PAGE FORMULAIRE PLAN D'ACTION ====================
    
    def _build_plan_form_page(self):
        """Page complète formulaire plan d'action."""
        is_edit = self.edit_plan_id is not None
        plan = self.db.get_action_plan_by_id(self.edit_plan_id) if is_edit else None
        
        # En-tête
        header = ft.Container(
            padding=20,
            bgcolor=Theme.SECONDARY,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=15,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                icon_color=ft.Colors.WHITE,
                                on_click=lambda e: self._navigate_to("main"),
                            ),
                            ft.Icon(ft.Icons.FACT_CHECK_ROUNDED, color=ft.Colors.WHITE, size=28),
                            ft.Text(
                                f"Plan d'Action No{plan['id']}" if is_edit else "Nouveau Plan d'Action",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                    ),
                ],
            ),
        )
        
        # Champs
        origine_field = ft.TextField(
            label="Origine / Source *",
            value=plan['origine'] if is_edit else "",
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.SECONDARY,
        )
        
        resume_field = ft.TextField(
            label="Résumé de l'origine",
            value=plan['resume_origine'] if is_edit else "",
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.SECONDARY,
        )
        
        objectif_field = ft.TextField(
            label="Objectif du Plan d'Action *",
            value=plan['objectif'] if is_edit else "",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.SECONDARY,
        )
        
        priorite_dropdown = ft.Dropdown(
            label="Priorité *",
            options=[
                "Mineure",
                "Majeure",
            ],
            value=plan['priorite'] if is_edit else "Mineure",
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.SECONDARY,
            width=200,
        )
        
        type_dropdown = ft.Dropdown(
            label="Type d'Action *",
            options=[
                "Amélioration",
                "Corrective",
                "Mise à jour",
            ],
            value=plan['type_action'] if is_edit else "Amélioration",
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.SECONDARY,
            width=200,
        )
        
        auteurs_field = ft.TextField(
            label="Auteurs / Pilotes (séparés par virgule)",
            value=plan['auteurs'] if is_edit else "",
            hint_text="Ex: Jean Dupont, Marie Martin",
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.SECONDARY,
        )
        
        date_fin_field = ft.TextField(
            label="Date Fin Prévue *",
            value=plan['date_fin_prevue'] if is_edit else "",
            hint_text="YYYY-MM-DD",
            read_only=True,
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.SECONDARY,
            width=200,
            suffix=ft.IconButton(
                icon=ft.Icons.CALENDAR_MONTH,
                on_click=lambda e: self._open_date_picker(date_fin_field),
            ),
        )
        
        moyen_field = ft.TextField(
            label="Moyen de Contrôle",
            value=plan['moyen_controle'] if is_edit else "",
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.SECONDARY,
        )
        
        date_solde_field = ft.TextField(
            label="Date de Solde (laisser vide si en cours)",
            value=plan['date_solde'] if is_edit else "",
            hint_text="YYYY-MM-DD",
            read_only=True,
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.SECONDARY,
            width=200,
            suffix=ft.IconButton(
                icon=ft.Icons.CALENDAR_MONTH,
                on_click=lambda e: self._open_date_picker(date_solde_field),
            ),
        )
        
        remarques_field = ft.TextField(
            label="Remarques",
            value=plan['remarques'] if is_edit else "",
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.SECONDARY,
        )
        
        # Gestion des tâches
        taches_list = json.loads(plan['taches_liste']) if is_edit and plan['taches_liste'] else []
        taches_controls = []
        
        def calculer_avancement():
            """Calcule l'avancement automatique."""
            total = len(taches_controls)
            if total == 0:
                return 0.0
            faites = sum(1 for t in taches_controls if t.controls[0].value)
            return (faites / total) * 100
        
        def update_progress():
            """Met à jour la barre de progression."""
            avancement = calculer_avancement()
            progress_bar.value = avancement / 100
            progress_text.value = f"{avancement:.0f}%"
            progress_bar.update()
            progress_text.update()
        
        def add_task(e):
            """Ajoute une nouvelle tâche."""
            new_task_field = ft.TextField(hint_text="Nouvelle tâche", expand=True)
            
            def remove_this_task(e):
                taches_column.controls.remove(task_row)
                taches_controls.remove(task_row)
                update_progress()
                taches_column.update()
            
            task_row = ft.Row(
                spacing=10,
                controls=[
                    ft.Checkbox(value=False, on_change=lambda e: update_progress()),
                    new_task_field,
                    ft.IconButton(icon=ft.Icons.DELETE, on_click=remove_this_task, icon_size=18),
                ],
            )
            taches_controls.append(task_row)
            taches_column.controls.append(task_row)
            update_progress()
            taches_column.update()
        
        # Initialiser tâches existantes
        for t in taches_list:
            task_field = ft.TextField(value=t['tache'], expand=True)
            
            def remove_this(e, row=None):
                taches_column.controls.remove(row)
                taches_controls.remove(row)
                update_progress()
                taches_column.update()
            
            task_row = ft.Row(
                spacing=10,
                controls=[
                    ft.Checkbox(value=t.get('fait', False), on_change=lambda e: update_progress()),
                    task_field,
                    ft.IconButton(icon=ft.Icons.DELETE, on_click=lambda e, r=None: remove_this(e, r), icon_size=18),
                ],
            )
            # Fix lambda closure
            task_row.controls[2].on_click = lambda e, r=task_row: remove_this(e, r)
            taches_controls.append(task_row)
        
        taches_column = ft.Column(
            spacing=10,
            controls=taches_controls,
        )
        
        # Progress bar
        progress_bar = ft.ProgressBar(value=calculer_avancement() / 100, width=300, height=10, color=ft.Colors.GREEN_500)
        progress_text = ft.Text(f"{calculer_avancement():.0f}%", size=14, weight=ft.FontWeight.BOLD)
        
        # Formulaire
        form_content = ft.Container(
            expand=True,
            padding=30,
            content=ft.Column(
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    # Section Info de base
                    ft.Container(
                        padding=20,
                        bgcolor=Theme.BG_CARD,
                        border_radius=10,
                        border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                        content=ft.Column(
                            spacing=15,
                            controls=[
                                ft.Text("[ID] Informations de Base", size=16, weight=ft.FontWeight.BOLD, color=Theme.SECONDARY),
                                origine_field,
                                resume_field,
                                objectif_field,
                                ft.Row(spacing=15, controls=[priorite_dropdown, type_dropdown]),
                                auteurs_field,
                            ],
                        ),
                    ),
                    # Section Planification
                    ft.Container(
                        padding=20,
                        bgcolor=Theme.BG_CARD,
                        border_radius=10,
                        border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                        content=ft.Column(
                            spacing=15,
                            controls=[
                                ft.Text("[Date] Planification", size=16, weight=ft.FontWeight.BOLD, color=Theme.WARNING),
                                ft.Row(spacing=15, controls=[date_fin_field, date_solde_field]),
                                moyen_field,
                                remarques_field,
                            ],
                        ),
                    ),
                    # Section Tâches
                    ft.Container(
                        padding=20,
                        bgcolor=Theme.BG_CARD,
                        border_radius=10,
                        border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                        content=ft.Column(
                            spacing=15,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("[OK] Liste des Tâches", size=16, weight=ft.FontWeight.BOLD, color=Theme.SUCCESS),
                                        ft.ElevatedButton("Ajouter Tâche", icon=ft.Icons.ADD, on_click=add_task),
                                    ],
                                ),
                                taches_column,
                                ft.Divider(),
                                ft.Row(
                                    spacing=15,
                                    controls=[
                                        ft.Text("Avancement Calculé:", size=14, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                                        progress_bar,
                                        progress_text,
                                    ],
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )
        
        # Boutons actions
        def save_plan(e):
            if not origine_field.value or not objectif_field.value or not date_fin_field.value:
                create_snackbar(self.page, "[Attention] Origine, Objectif et Date fin obligatoires", "error")
                return
            
            # Récupérer les tâches
            taches = []
            for row in taches_controls:
                checkbox = row.controls[0]
                text_field = row.controls[1]
                if text_field.value:
                    taches.append({"tache": text_field.value, "fait": checkbox.value})
            
            data = {
                'origine': origine_field.value,
                'resume_origine': resume_field.value,
                'objectif': objectif_field.value,
                'priorite': priorite_dropdown.value,
                'type_action': type_dropdown.value,
                'auteurs': auteurs_field.value,
                'date_fin_prevue': date_fin_field.value,
                'moyen_controle': moyen_field.value,
                'date_solde': date_solde_field.value,
                'remarques': remarques_field.value,
                'taches_liste': json.dumps(taches),
                'statut_calcule': calculer_avancement(),
            }
            
            if is_edit:
                self.db.update_action_plan(self.edit_plan_id, data)
                create_snackbar(self.page, "[OK] Plan d'action mis à jour", "success")
            else:
                data['date_creation'] = datetime.now().strftime('%Y-%m-%d')
                data['veille_id'] = None
                plan_id = self.db.create_action_plan(data)
                create_snackbar(self.page, f"[OK] Plan d'action créé (No{plan_id})", "success")
            
            self._navigate_to("main")
        
        actions_bar = ft.Container(
            padding=20,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.END,
                spacing=15,
                controls=[
                    ft.TextButton("Annuler", on_click=lambda e: self._navigate_to("main")),
                    ft.ElevatedButton(
                        "Supprimer" if is_edit else None,
                        icon=ft.Icons.DELETE,
                        on_click=lambda e: (self._delete_plan(self.edit_plan_id) if is_edit else None),
                    ) if is_edit else ft.Container(),
                    ft.ElevatedButton(
                        "Enregistrer",
                        icon=ft.Icons.SAVE,
                        bgcolor=Theme.SECONDARY,
                        color=ft.Colors.WHITE,
                        on_click=save_plan,
                    ),
                ],
            ),
        )
        
        return ft.Column(
            expand=True,
            spacing=0,
            controls=[header, form_content, actions_bar],
        )

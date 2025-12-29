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
        # Utiliser la même base de données que le reste de l'application
        self.db = VeilleDBManager(db.db_path if hasattr(db, 'db_path') else None)
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
                
                # Lien cliquable
                lien_control = ft.Text('-', size=10) if not v['lien_url'] else ft.TextButton(
                    v['lien_url'],
                    url=v['lien_url'],
                    style=ft.ButtonStyle(
                        padding=0,
                    ),
                    tooltip=v['lien_url'],
                )
                
                # Fichiers multiples cliquables
                fichiers_json = v.get('fichier_joint', '')
                if fichiers_json:
                    try:
                        fichiers = json.loads(fichiers_json) if isinstance(fichiers_json, str) else []
                        if not isinstance(fichiers, list):
                            fichiers = [fichiers_json] if fichiers_json else []
                    except:
                        fichiers = [fichiers_json] if fichiers_json else []
                else:
                    fichiers = []
                
                if fichiers:
                    fichier_control = ft.PopupMenuButton(
                        icon=ft.Icons.ATTACH_FILE,
                        icon_size=16,
                        icon_color=Theme.PRIMARY,
                        tooltip=f"{len(fichiers)} fichier(s)",
                        items=[
                            ft.PopupMenuItem(
                                text=Path(f).name,
                                on_click=lambda e, path=f: self._open_file(path),
                            )
                            for f in fichiers
                        ],
                    )
                else:
                    fichier_control = ft.Icon(ft.Icons.REMOVE, size=16, color=Theme.TEXT_MUTED)
                
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(v['source'] or '-', size=11, no_wrap=False, width=100)),
                            ft.DataCell(ft.Text(v['date_publication'] or '-', size=11)),
                            ft.DataCell(ft.Text(v['date_lecture'] or '-', size=11)),
                            ft.DataCell(
                                ft.Container(
                                    expand=True,
                                    content=ft.Text(
                                        v['description'] or '-',
                                        size=11,
                                        no_wrap=False,
                                    ),
                                )
                            ),
                            ft.DataCell(
                                ft.Container(
                                    width=180,
                                    content=ft.Column(
                                        spacing=2,
                                        scroll=ft.ScrollMode.AUTO,
                                        controls=[lien_control] if lien_control else [],
                                    ),
                                )
                            ),
                            ft.DataCell(
                                ft.Text(
                                    v['commentaire_interne'] or '-',
                                    size=11,
                                    no_wrap=False,
                                    width=150,
                                )
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
                            ft.DataCell(fichier_control),
                            ft.DataCell(
                                ft.Text(
                                    v.get('plan_action_numero', '-') if v.get('plan_action_numero') else "-",
                                    size=11,
                                    weight=ft.FontWeight.BOLD if v.get('plan_action_numero') else ft.FontWeight.NORMAL,
                                    color=Theme.SECONDARY if v.get('plan_action_numero') else Theme.TEXT_MUTED,
                                )
                            ),
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
                                ft.DataColumn(ft.Text("Source", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Date Pub.", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Date Lect.", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Description", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Lien URL", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Commentaire", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Statut", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Fichier", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("No Plan", weight=ft.FontWeight.BOLD)),
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
                            column_spacing=15,
                            data_row_max_height=float('inf'),  # Hauteur illimitée pour les lignes
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
                    ft.PopupMenuButton(
                        icon=ft.Icons.DOWNLOAD,
                        tooltip="Exporter",
                        items=[
                            ft.PopupMenuItem(text="[PDF] Exporter en PDF", on_click=lambda e: self._export_plans("pdf")),
                            ft.PopupMenuItem(text="[Stats] Exporter en Excel", on_click=lambda e: self._export_plans("excel")),
                        ],
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
                
                # Récupérer le No de plan depuis la veille
                plan_numero = "-"
                if p.get('veille_id'):
                    veille_data = self.db.get_veille_by_id(p['veille_id'])
                    if veille_data and veille_data.get('plan_action_numero'):
                        plan_numero = veille_data['plan_action_numero']
                
                # Bouton pour ouvrir le dialog des tâches
                taches_button = ft.IconButton(
                    icon=ft.Icons.CHECKLIST,
                    icon_size=18,
                    tooltip="Gérer les tâches",
                    icon_color=Theme.INFO,
                    on_click=lambda e, pid=p['id']: self._open_taches_dialog(pid),
                )
                
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(plan_numero, size=11, weight=ft.FontWeight.BOLD, color=Theme.SECONDARY if plan_numero != "-" else Theme.TEXT_MUTED, width=50)),
                            ft.DataCell(ft.Text(p['date_creation'] or '-', size=11)),
                            ft.DataCell(ft.Text(p['origine'] or '-', size=11, no_wrap=False, width=120)),
                            ft.DataCell(
                                ft.Container(
                                    expand=True,
                                    content=ft.Text(
                                        p['resume_origine'] or '-',
                                        size=11,
                                        no_wrap=False,
                                    ),
                                )
                            ),
                            ft.DataCell(ft.Text(p['objectif'] or '-', size=11, no_wrap=False, width=150)),
                            ft.DataCell(ft.Text(p['priorite'] or '-', size=11)),
                            ft.DataCell(ft.Text(p['type_action'] or '-', size=11, width=80)),
                            ft.DataCell(ft.Text(p['auteurs'] or '-', size=11, no_wrap=False, width=100)),
                            ft.DataCell(ft.Text(p['date_fin_prevue'] or '-', size=11)),
                            ft.DataCell(ft.Text(p['date_solde'] or '-', size=11)),
                            ft.DataCell(ft.Text(p['moyen_controle'] or '-', size=11, no_wrap=False, width=120)),
                            ft.DataCell(
                                ft.Container(
                                    width=100,
                                    content=ft.Column(
                                        spacing=3,
                                        controls=[
                                            ft.ProgressBar(value=avancement / 100, width=80, height=6, color=ft.Colors.GREEN_500),
                                            ft.Text(f"{avancement:.0f}%", size=10, text_align=ft.TextAlign.CENTER),
                                        ],
                                    ),
                                ),
                            ),
                            ft.DataCell(
                                ft.Row(
                                    spacing=5,
                                    controls=[
                                        taches_button,
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
                                ft.DataColumn(ft.Text("Créé le", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Origine", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Résumé", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Objectif", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Priorité", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Auteurs", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Échéance", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Soldé le", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Moyen Contrôle", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Avancement", weight=ft.FontWeight.BOLD)),
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
                            column_spacing=12,
                            data_row_max_height=float('inf'),  # Hauteur illimitée
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
        
        # Calculer les statistiques des tâches
        all_plans = self.db.get_all_action_plans()
        total_taches = 0
        taches_completees = 0
        plans_avec_taches = 0
        
        for plan in all_plans:
            taches = plan.get('taches_liste', [])
            if taches:
                plans_avec_taches += 1
                total_taches += len(taches)
                taches_completees += sum(1 for t in taches if t.get('fait', False))
        
        taux_completion_taches = (taches_completees / total_taches * 100) if total_taches > 0 else 0
        
        # Calculer l'avancement moyen des plans
        avancements = [p.get('statut_calcule', 0) for p in all_plans]
        avancement_moyen = sum(avancements) / len(avancements) if avancements else 0
        
        # Stats veilles
        total = stats_veilles.get('total_annee', 0)
        statuts_dict = stats_veilles.get('statuts', {})
        sources_dict = stats_veilles.get('sources', {})
        
        # Tous les statuts
        conformes = statuts_dict.get('Conforme', 0)
        concernes = statuts_dict.get('Concerné', 0)
        a_etudier = statuts_dict.get('À l\'étude', 0)
        non_concernes = statuts_dict.get('Non concerné', 0)
        
        # KPI Cards améliorées
        stats_cards = ft.Row(
            spacing=15,
            wrap=True,
            controls=[
                self._create_stat_card("[ID] Total Veilles", str(total), Theme.PRIMARY, f"dont {concernes} concernés"),
                self._create_stat_card("[Note] Plans d'Actions", str(len(all_plans)), Theme.SECONDARY, f"{stats_plans['en_cours']} en cours"),
                self._create_stat_card("[OK] Taux Complétion", f"{taux_completion_taches:.0f}%", ft.Colors.GREEN_500, f"{taches_completees}/{total_taches} tâches"),
                self._create_stat_card("[Stats] Avancement Moyen", f"{avancement_moyen:.0f}%", ft.Colors.BLUE_500, f"sur {len(all_plans)} plans"),
            ],
        )
        
        # Graphique répartition des statuts (TOUS les statuts)
        total_statuts = sum(statuts_dict.values()) if statuts_dict else 1
        chart_statuts = ft.Container(
            width=550,
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
                            self._create_bar_chart_row(statut, count, total_statuts, self._get_status_color(statut))
                            for statut, count in sorted(statuts_dict.items(), key=lambda x: x[1], reverse=True)
                        ] if statuts_dict else [ft.Text("Aucune donnée", color=Theme.TEXT_MUTED)],
                    ),
                ],
            ),
        )
        
        # Graphique répartition par source (TOUTES les sources)
        total_sources = sum(sources_dict.values()) if sources_dict else 1
        chart_sources = ft.Container(
            width=550,
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
                    ft.Text("[Source] Répartition par Source", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    ft.Column(
                        spacing=10,
                        controls=[
                            self._create_bar_chart_row(source, count, total_sources, Theme.INFO)
                            for source, count in sorted(sources_dict.items(), key=lambda x: x[1], reverse=True)
                        ] if sources_dict else [ft.Text("Aucune donnée", color=Theme.TEXT_MUTED)],
                    ),
                ],
            ),
        )
        
        # Stats plans d'actions (TOUTES les données)
        origines_dict = stats_plans.get('origines', {})
        types_dict = stats_plans.get('types', {})
        
        # Graphique répartition par origine
        total_origines = sum(origines_dict.values()) if origines_dict else 1
        chart_origines = ft.Container(
            width=550,
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
                    ft.Text("[Origine] Répartition par Origine", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    ft.Column(
                        spacing=10,
                        controls=[
                            self._create_bar_chart_row(origine, count, total_origines, Theme.SECONDARY)
                            for origine, count in sorted(origines_dict.items(), key=lambda x: x[1], reverse=True)
                        ] if origines_dict else [ft.Text("Aucune donnée", color=Theme.TEXT_MUTED)],
                    ),
                ],
            ),
        )
        
        # Graphique répartition par type
        total_types = sum(types_dict.values()) if types_dict else 1
        chart_types = ft.Container(
            width=550,
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
                    ft.Text("[Note] Répartition par Type", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    ft.Column(
                        spacing=10,
                        controls=[
                            self._create_bar_chart_row(type_action, count, total_types, Theme.WARNING)
                            for type_action, count in sorted(types_dict.items(), key=lambda x: x[1], reverse=True)
                        ] if types_dict else [ft.Text("Aucune donnée", color=Theme.TEXT_MUTED)],
                    ),
                ],
            ),
        )
        
        # Plans d'actions - summary card
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
        
        # Section Statistiques des Tâches
        taches_stats_card = ft.Container(
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
                            ft.Icon(ft.Icons.CHECKLIST, size=28, color=Theme.INFO),
                            ft.Text("Statistiques des Tâches", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                        ],
                    ),
                    ft.Row(
                        spacing=30,
                        wrap=True,
                        controls=[
                            ft.Column(
                                spacing=5,
                                controls=[
                                    ft.Text("Total tâches", size=12, color=Theme.TEXT_MUTED),
                                    ft.Text(str(total_taches), size=24, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
                                ],
                            ),
                            ft.Column(
                                spacing=5,
                                controls=[
                                    ft.Text("Complétées", size=12, color=Theme.TEXT_MUTED),
                                    ft.Text(str(taches_completees), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_600),
                                ],
                            ),
                            ft.Column(
                                spacing=5,
                                controls=[
                                    ft.Text("En cours", size=12, color=Theme.TEXT_MUTED),
                                    ft.Text(str(total_taches - taches_completees), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_600),
                                ],
                            ),
                            ft.Column(
                                spacing=5,
                                controls=[
                                    ft.Text("Plans avec tâches", size=12, color=Theme.TEXT_MUTED),
                                    ft.Text(str(plans_avec_taches), size=24, weight=ft.FontWeight.BOLD, color=Theme.SECONDARY),
                                ],
                            ),
                        ],
                    ),
                    ft.ProgressBar(
                        value=taches_completees / total_taches if total_taches > 0 else 0,
                        color=ft.Colors.GREEN_600,
                        bgcolor=Theme.OUTLINE,
                        height=12,
                    ),
                    ft.Text(
                        f"Taux de complétion: {taux_completion_taches:.1f}%",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN_600,
                    ),
                ],
            ),
        )
        
        return ft.Column(
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("[Stats] Tableau de Bord", size=24, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                stats_cards,
                # Graphiques veilles (2 colonnes)
                ft.Row(spacing=15, wrap=True, controls=[chart_statuts, chart_sources]),
                # Section Plans et Tâches (2 colonnes)
                ft.Row(spacing=15, wrap=True, controls=[plans_card, taches_stats_card]),
                # Graphiques plans d'actions (2 colonnes)
                ft.Row(spacing=15, wrap=True, controls=[chart_origines, chart_types]),
                ft.Divider(height=2, color=Theme.OUTLINE),
                ft.Text("[Note] Actions Prioritaires", size=20, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                ft.Column(spacing=10, controls=todo_cards),
            ],
        )
    
    def _create_stat_card(self, title, value, color, subtitle=None):
        """Crée une carte stat avec sous-titre optionnel."""
        controls = [
            ft.Text(title, size=14, color=Theme.TEXT_SECONDARY, weight=ft.FontWeight.W_500),
            ft.Text(value, size=32, weight=ft.FontWeight.BOLD, color=color),
        ]
        if subtitle:
            controls.append(ft.Text(subtitle, size=11, color=Theme.TEXT_MUTED, italic=True))
        
        return ft.Container(
            width=220,
            height=140,
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
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=controls,
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
    
    def _open_taches_dialog(self, plan_id):
        """Ouvre un dialog pour gérer les tâches du plan d'action."""
        if not self.page:
            print("Erreur: self.page n'est pas disponible")
            return
            
        plan = self.db.get_action_plan_by_id(plan_id)
        if not plan:
            create_snackbar(self.page, "[Erreur] Plan d'action introuvable", "error")
            return
        
        # Récupérer les tâches (déjà parsées par get_action_plan_by_id)
        taches = plan.get('taches_liste', [])
        if not isinstance(taches, list):
            taches = []
        
        print(f"Dialog ouvert pour plan {plan_id}, {len(taches)} tâches chargées")
        print(f"Type de taches_liste: {type(taches)}, contenu: {taches}")
        
        # Créer les contrôles pour chaque tâche
        taches_controls = []
        
        def calculer_avancement():
            """Calcule l'avancement basé sur les tâches cochées."""
            if not taches_controls:
                return 0.0
            total = len(taches_controls)
            faites = sum(1 for row in taches_controls if row.controls[0].value)
            return (faites / total * 100) if total > 0 else 0.0
        
        def on_checkbox_change(e):
            """Met à jour l'avancement quand une checkbox change."""
            avancement = calculer_avancement()
            avancement_text.value = f"Avancement: {avancement:.0f}%"
            avancement_bar.value = avancement / 100
            if avancement_text.page:
                avancement_text.update()
                avancement_bar.update()
        
        # Construire la liste des tâches
        taches_display_controls = []
        if taches:
            for t in taches:
                checkbox = ft.Checkbox(
                    label="",
                    value=t.get('fait', False),
                    on_change=on_checkbox_change,
                )
                text = ft.Text(t.get('tache', ''), size=13, color=Theme.TEXT_PRIMARY, expand=True)
                row = ft.Row(spacing=10, controls=[checkbox, text])
                taches_controls.append(row)
                taches_display_controls.append(row)
        
        if not taches_display_controls:
            taches_display_controls.append(
                ft.Text("Aucune tâche définie", size=13, italic=True, color=Theme.TEXT_MUTED)
            )
        
        # Avancement
        avancement_initial = calculer_avancement()
        avancement_bar = ft.ProgressBar(value=avancement_initial / 100, width=300, height=10, color=ft.Colors.GREEN_500)
        avancement_text = ft.Text(f"Avancement: {avancement_initial:.0f}%", size=14, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY)
        
        def save_taches(e):
            """Enregistre les tâches mises à jour."""
            try:
                # Mettre à jour les tâches avec les nouvelles valeurs
                updated_taches = []
                for i, t in enumerate(taches):
                    if i < len(taches_controls) and taches_controls[i].controls[0].value is not None:
                        t['fait'] = taches_controls[i].controls[0].value
                    updated_taches.append(t)
                
                # Calculer l'avancement final
                avancement = calculer_avancement()
                
                print(f"Sauvegarde: {len(updated_taches)} tâches, avancement={avancement:.0f}%")
                
                # Mettre à jour dans la base (seulement tâches et avancement)
                self.db.update_plan_taches(plan_id, json.dumps(updated_taches), avancement)
                
                # Fermer le dialog avec page.close()
                self.page.close(dialog)
                
                # Message de succès
                create_snackbar(self.page, "[OK] Tâches mises à jour", "success")
                
                # Rafraîchir la vue
                self.content = self._build_main_view()
                self.update()
                
            except Exception as ex:
                print(f"Erreur lors de la sauvegarde: {ex}")
                import traceback
                traceback.print_exc()
                create_snackbar(self.page, f"[Erreur] Erreur: {str(ex)}", "error")
        
        # Fermeture du dialog
        def close_dialog_handler(e):
            try:
                self.page.close(dialog)
            except Exception as ex:
                print(f"Erreur fermeture dialog: {ex}")
        
        # Créer le dialog
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CHECKLIST, color=Theme.INFO, size=28),
                    ft.Text("Gestion des Tâches", size=20, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                ],
            ),
            content=ft.Container(
                width=500,
                height=400,
                content=ft.Column(
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Container(
                            padding=15,
                            bgcolor=Theme.BG_SECONDARY,
                            border_radius=8,
                            content=ft.Column(
                                spacing=10,
                                controls=[
                                    avancement_text,
                                    avancement_bar,
                                ],
                            ),
                        ),
                        ft.Divider(height=2, color=Theme.OUTLINE),
                        ft.Column(spacing=10, controls=taches_display_controls),
                    ],
                ),
            ),
            actions=[
                ft.TextButton("Annuler", on_click=close_dialog_handler),
                ft.ElevatedButton(
                    "Enregistrer",
                    icon=ft.Icons.SAVE,
                    bgcolor=Theme.PRIMARY,
                    color=ft.Colors.WHITE,
                    on_click=save_taches,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=Theme.BG_CARD,  # Fond du dialog
            surface_tint_color=Theme.PRIMARY,  # Teinte de surface
        )
        
        # Utiliser page.overlay + page.open() pour afficher le dialog
        print(f"Création dialog avec {len(taches_display_controls)} contrôles")
        print(f"Dialog modal={dialog.modal}, open avant affichage={dialog.open}")
        
        # Ouvrir le dialog avec page.open() (méthode standard Flet)
        self.page.open(dialog)
        print(f"Dialog ouvert avec page.open() pour plan {plan_id}")
    
    def _open_file(self, file_path):
        """Ouvre un fichier avec l'application par défaut."""
        if file_path and Path(file_path).exists():
            import os
            import platform
            try:
                if platform.system() == 'Windows':
                    os.startfile(file_path)
                elif platform.system() == 'Darwin':  # macOS
                    os.system(f'open "{file_path}"')
                else:  # Linux
                    os.system(f'xdg-open "{file_path}"')
                create_snackbar(self.page, f"[Fichier] Ouverture du fichier...", "success")
            except Exception as e:
                create_snackbar(self.page, f"[Erreur] Erreur: {str(e)}", "error")
        else:
            create_snackbar(self.page, "[Erreur] Fichier introuvable", "error")
    
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
            min_lines=4,
            max_lines=8,
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
        
        # Fichiers joints multiples
        if is_edit and veille.get('fichier_joint'):
            try:
                fichiers_json = veille['fichier_joint']
                self.selected_files = json.loads(fichiers_json) if isinstance(fichiers_json, str) else []
                if not isinstance(self.selected_files, list):
                    self.selected_files = [fichiers_json] if fichiers_json else []
            except:
                self.selected_files = [veille['fichier_joint']] if veille.get('fichier_joint') else []
        else:
            self.selected_files = []
        
        fichiers_list = ft.Column(spacing=5)
        
        def update_fichiers_display():
            fichiers_list.controls.clear()
            if self.selected_files:
                for i, f in enumerate(self.selected_files):
                    fichiers_list.controls.append(
                        ft.Row(
                            spacing=5,
                            controls=[
                                ft.Icon(ft.Icons.ATTACH_FILE, size=16, color=Theme.PRIMARY),
                                ft.Text(Path(f).name, size=12, color=Theme.TEXT_PRIMARY),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    icon_size=16,
                                    tooltip="Retirer",
                                    on_click=lambda e, idx=i: remove_file(idx),
                                ),
                            ],
                        )
                    )
            else:
                fichiers_list.controls.append(
                    ft.Text("Aucun fichier", size=12, color=Theme.TEXT_MUTED)
                )
            # Ne pas appeler update() ici car le control n'est pas encore dans la page
        
        def remove_file(idx):
            if 0 <= idx < len(self.selected_files):
                self.selected_files.pop(idx)
                update_fichiers_display()
                if fichiers_list.page:
                    fichiers_list.update()
        
        def on_file_picked(e: ft.FilePickerResultEvent):
            if e.files:
                for f in e.files:
                    if f.path not in self.selected_files:
                        self.selected_files.append(f.path)
                update_fichiers_display()
                if fichiers_list.page:
                    fichiers_list.update()
        
        # FilePicker avec sélection multiple
        self.file_picker.on_result = on_file_picked
        
        # Initialiser l'affichage (sans update)
        update_fichiers_display()
        
        fichier_button = ft.ElevatedButton(
            "Ajouter Fichier(s)",
            icon=ft.Icons.ATTACH_FILE,
            on_click=lambda e: self.file_picker.pick_files(allow_multiple=True) if self.file_picker else None,
        )
        
        # No de Plan d'Action (saisi manuellement si Concerné)
        plan_numero_field = ft.TextField(
            label="No du Plan d'Action",
            value=veille.get('plan_action_numero', '') if is_edit else "",
            hint_text="Ex: PA-2024-001",
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.PRIMARY,
        )
        
        # Container pour le plan (visible si Concerné)
        plan_container = ft.Container(
            visible=(statut_dropdown.value == "Concerné"),
            content=ft.Column(
                spacing=10,
                controls=[
                    plan_numero_field,
                    ft.Text(
                        "[Note] Saisissez le numéro du plan d'action à créer",
                        size=11,
                        color=Theme.TEXT_MUTED,
                        italic=True,
                    ),
                ],
            ),
        )
        
        def on_statut_change(e):
            plan_container.visible = (statut_dropdown.value == "Concerné")
            plan_container.update()
        
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
                                ft.Row(spacing=15, controls=[date_pub_field, date_lecture_field]),
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
                                ft.Container(
                                    padding=15,
                                    bgcolor=Theme.BG_SECONDARY,
                                    border_radius=8,
                                    border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                                    content=ft.Column(
                                        spacing=10,
                                        controls=[
                                            ft.Row(
                                                spacing=10,
                                                controls=[
                                                    ft.Icon(ft.Icons.ATTACH_FILE, color=Theme.PRIMARY, size=20),
                                                    ft.Text("Fichiers Joints", size=13, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                                                ],
                                            ),
                                            fichier_button,
                                            fichiers_list,
                                        ],
                                    ),
                                ),
                                plan_container,
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
            
            # Récupérer le No de plan si Concerné
            plan_numero = None
            if statut_dropdown.value == "Concerné" and plan_numero_field.value:
                plan_numero = plan_numero_field.value.strip()
            
            # Convertir liste fichiers en JSON
            fichiers_json = json.dumps(self.selected_files) if self.selected_files else None
            
            data = {
                'source': source_field.value,
                'annee': None,  # Plus utilisé
                'date_publication': date_pub_field.value,
                'description': description_field.value,
                'resume': None,  # Plus utilisé pour les veilles
                'lien_url': lien_field.value,
                'commentaire_interne': commentaire_field.value,
                'date_lecture': date_lecture_field.value,
                'statut_veille': statut_dropdown.value,
                'fichier_joint': fichiers_json,
                'plan_action_numero': plan_numero,
            }
            
            if is_edit:
                self.db.update_veille(self.edit_veille_id, data)
                create_snackbar(self.page, "[OK] Veille mise à jour", "success")
            else:
                veille_id = self.db.create_veille(data)
                if plan_numero:
                    create_snackbar(self.page, f"[OK] Veille créée avec plan {plan_numero}", "success")
                else:
                    create_snackbar(self.page, f"[OK] Veille créée (No{veille_id})", "success")
            
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
        
        # Récupérer le No de plan depuis la veille si disponible
        plan_numero_titre = ""
        if is_edit and plan and plan.get('veille_id'):
            veille_data = self.db.get_veille_by_id(plan['veille_id'])
            if veille_data and veille_data.get('plan_action_numero'):
                plan_numero_titre = f" - {veille_data['plan_action_numero']}"
        
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
                                f"Plan d'Action{plan_numero_titre}" if is_edit else "Nouveau Plan d'Action",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                    ),
                ],
            ),
        )
        
        # Dropdown des veilles avec No de plan
        all_veilles = self.db.get_all_veilles()
        veilles_avec_plan = [v for v in all_veilles if v.get('plan_action_numero')]
        
        veille_options = ["Aucune veille associée"]
        for v in veilles_avec_plan:
            veille_options.append(
                f"{v['plan_action_numero']} - {v['source'][:40]}"
            )
        
        # Trouver la veille associée si mode édition
        veille_id_selected = None
        plan_numero_from_veille = None
        if is_edit and plan and plan.get('veille_id'):
            veille_id_selected = str(plan['veille_id'])
            veille_data = self.db.get_veille_by_id(plan['veille_id'])
            if veille_data:
                plan_numero_from_veille = veille_data.get('plan_action_numero', '')
        
        veille_dropdown = ft.Dropdown(
            label="Veille Réglementaire d'Origine (avec No Plan)",
            options=veille_options,
            value=veille_id_selected if veille_id_selected else "0",
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.SECONDARY,
        )
        
        # Affichage du No de plan depuis la veille
        plan_numero_display = ft.Container(
            padding=10,
            bgcolor=Theme.BG_SECONDARY,
            border_radius=5,
            border=ft.Border(
                top=ft.BorderSide(2, Theme.PRIMARY if plan_numero_from_veille else Theme.OUTLINE),
                right=ft.BorderSide(2, Theme.PRIMARY if plan_numero_from_veille else Theme.OUTLINE),
                bottom=ft.BorderSide(2, Theme.PRIMARY if plan_numero_from_veille else Theme.OUTLINE),
                left=ft.BorderSide(2, Theme.PRIMARY if plan_numero_from_veille else Theme.OUTLINE),
            ),
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(
                        ft.Icons.TAG,
                        size=20,
                        color=Theme.PRIMARY if plan_numero_from_veille else Theme.TEXT_MUTED,
                    ),
                    ft.Text(
                        f"No Plan: {plan_numero_from_veille}" if plan_numero_from_veille else "Sélectionnez une veille pour obtenir le No",
                        size=14,
                        weight=ft.FontWeight.BOLD if plan_numero_from_veille else ft.FontWeight.NORMAL,
                        color=Theme.PRIMARY if plan_numero_from_veille else Theme.TEXT_MUTED,
                    ),
                ],
            ),
        )
        
        # Callback pour mettre à jour le No de plan quand on change de veille
        def on_veille_change(e):
            if veille_dropdown.value and veille_dropdown.value != "0":
                veille_data = self.db.get_veille_by_id(int(veille_dropdown.value))
                if veille_data and veille_data.get('plan_action_numero'):
                    plan_numero_display.content = ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.TAG, size=20, color=Theme.PRIMARY),
                            ft.Text(
                                f"No Plan: {veille_data['plan_action_numero']}",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.PRIMARY,
                            ),
                        ],
                    )
                    plan_numero_display.border = ft.Border(
                top=ft.BorderSide(2, Theme.PRIMARY),
                right=ft.BorderSide(2, Theme.PRIMARY),
                bottom=ft.BorderSide(2, Theme.PRIMARY),
                left=ft.BorderSide(2, Theme.PRIMARY),
            )
                    plan_numero_display.bgcolor = ft.Colors.with_opacity(0.1, Theme.PRIMARY)
                else:
                    plan_numero_display.content = ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.WARNING, size=20, color=Theme.DANGER),
                            ft.Text(
                                "Cette veille n'a pas de No de plan",
                                size=14,
                                color=Theme.DANGER,
                            ),
                        ],
                    )
                    plan_numero_display.border = ft.Border(
                top=ft.BorderSide(2, Theme.DANGER),
                right=ft.BorderSide(2, Theme.DANGER),
                bottom=ft.BorderSide(2, Theme.DANGER),
                left=ft.BorderSide(2, Theme.DANGER),
            )
                    plan_numero_display.bgcolor = ft.Colors.with_opacity(0.1, Theme.DANGER)
            else:
                plan_numero_display.content = ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(ft.Icons.TAG, size=20, color=Theme.TEXT_MUTED),
                        ft.Text(
                            "Sélectionnez une veille pour obtenir le No",
                            size=14,
                            color=Theme.TEXT_MUTED,
                        ),
                    ],
                )
                plan_numero_display.border = ft.Border(
                top=ft.BorderSide(2, Theme.OUTLINE),
                right=ft.BorderSide(2, Theme.OUTLINE),
                bottom=ft.BorderSide(2, Theme.OUTLINE),
                left=ft.BorderSide(2, Theme.OUTLINE),
            )
                plan_numero_display.bgcolor = Theme.BG_SECONDARY
            plan_numero_display.update()
        
        veille_dropdown.on_change = on_veille_change
        
        # Date de création (affichage uniquement)
        date_creation_display = ft.Container(
            padding=15,
            bgcolor=Theme.BG_SECONDARY,
            border_radius=8,
            border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=20, color=Theme.INFO),
                    ft.Text(
                        f"Créé le: {plan['date_creation'] if is_edit else datetime.now().strftime('%Y-%m-%d')}",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=Theme.TEXT_PRIMARY,
                    ),
                ],
            ),
        )
        
        # Champs
        origine_field = ft.TextField(
            label="Origine / Source *",
            value=plan['origine'] if is_edit else "",
            hint_text="Ex: Veille réglementaire, Audit, Réclamation client",
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
        
        # Gestion des tâches (déjà parsées par get_action_plan_by_id)
        taches_list = plan.get('taches_liste', []) if is_edit else []
        if not isinstance(taches_list, list):
            taches_list = []
        taches_controls = []
        
        # Créer taches_column AVANT de l'utiliser
        taches_column = ft.Column(
            spacing=10,
            controls=[],
        )
        
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
            if progress_bar.page:
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
            taches_column.controls.append(task_row)
        
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
                                date_creation_display,
                                veille_dropdown,
                                plan_numero_display,
                                ft.Divider(),
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
            
            print(f"Sauvegarde plan: {len(taches)} tâches récupérées depuis taches_controls")
            print(f"Tâches: {taches}")
            
            # Veille associée
            veille_id_selected = int(veille_dropdown.value) if veille_dropdown.value != "0" else None
            
            data = {
                'veille_id': veille_id_selected,
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
                'taches_liste': taches,  # Envoyer la liste directement, pas JSON
                'statut_calcule': calculer_avancement(),
            }
            
            if is_edit:
                self.db.update_action_plan(self.edit_plan_id, data)
                # Mettre à jour la veille si associée
                if veille_id_selected:
                    self.db.link_plan_to_veille(veille_id_selected, self.edit_plan_id)
                create_snackbar(self.page, "[OK] Plan d'action mis à jour", "success")
            else:
                data['date_creation'] = datetime.now().strftime('%Y-%m-%d')
                plan_id = self.db.create_action_plan(data)
                # Mettre à jour la veille si associée
                if veille_id_selected:
                    self.db.link_plan_to_veille(veille_id_selected, plan_id)
                create_snackbar(self.page, f"[OK] Plan d'action créé (PA-{plan_id})", "success")
            
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
    # ==================== IMPORT / EXPORT ====================
    
    def _import_excel(self):
        """Importe des veilles depuis un fichier Excel."""
        if not self.file_picker:
            create_snackbar(self.page, "[Erreur] FilePicker non initialisé", "error")
            return
        
        self.file_picker.pick_files(
            dialog_title="Sélectionner un fichier Excel",
            allowed_extensions=["xlsx", "xls"],
            file_type=ft.FilePickerFileType.CUSTOM,
        )
        self.file_picker.on_result = self._process_excel_import
    
    def _process_excel_import(self, e: ft.FilePickerResultEvent):
        """Traite le fichier Excel sélectionné."""
        if not e.files:
            return
        
        try:
            file_path = e.files[0].path
            df = pd.read_excel(file_path)
            
            # Colonnes attendues
            required_cols = ['source', 'description']
            if not all(col in df.columns for col in required_cols):
                create_snackbar(self.page, f"[Erreur] Colonnes requises: {', '.join(required_cols)}", "error")
                return
            
            imported = 0
            for _, row in df.iterrows():
                data = {
                    'source': str(row.get('source', '')),
                    'annee': None,
                    'date_publication': str(row.get('date_publication', '')) if pd.notna(row.get('date_publication')) else None,
                    'description': str(row.get('description', '')),
                    'resume': None,
                    'lien_url': str(row.get('lien_url', '')) if pd.notna(row.get('lien_url')) else None,
                    'commentaire_interne': str(row.get('commentaire_interne', '')) if pd.notna(row.get('commentaire_interne')) else None,
                    'date_lecture': str(row.get('date_lecture', '')) if pd.notna(row.get('date_lecture')) else None,
                    'statut_veille': str(row.get('statut_veille', 'À l\'étude')),
                    'fichier_joint': None,
                    'plan_action_numero': str(row.get('plan_action_numero', '')) if pd.notna(row.get('plan_action_numero')) else None,
                }
                
                if data['source'] and data['description']:
                    self.db.create_veille(data)
                    imported += 1
            
            create_snackbar(self.page, f"[OK] {imported} veille(s) importée(s)", "success")
            self._navigate_to("main")
            
        except Exception as ex:
            create_snackbar(self.page, f"[Erreur] Erreur import: {str(ex)}", "error")
    
    def _export_veilles(self, format_type):
        """Exporte les veilles en PDF ou Excel."""
        veilles = self.db.get_all_veilles()
        
        if not veilles:
            create_snackbar(self.page, "[Attention] Aucune veille à exporter", "error")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format_type == "excel":
                self._export_veilles_excel(veilles, timestamp)
            else:
                self._export_veilles_pdf(veilles, timestamp)
                
        except Exception as ex:
            create_snackbar(self.page, f"[Erreur] Erreur export: {str(ex)}", "error")
    
    def _export_veilles_excel(self, veilles, timestamp):
        """Exporte les veilles en Excel."""
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Veilles Réglementaires"
        
        # En-têtes
        headers = ['ID', 'Source', 'Date Pub.', 'Date Lecture', 'Description', 
                   'Lien URL', 'Commentaire', 'Statut', 'No Plan']
        ws.append(headers)
        
        # Style des en-têtes
        header_fill = PatternFill(start_color="3B82F6", end_color="3B82F6", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Données
        for v in veilles:
            ws.append([
                v['id'],
                v['source'],
                v['date_publication'],
                v['date_lecture'],
                v['description'],
                v['lien_url'],
                v['commentaire_interne'],
                v['statut_veille'],
                v.get('plan_action_numero', ''),
            ])
        
        # Ajuster largeurs
        ws.column_dimensions['A'].width = 8
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 12
        ws.column_dimensions['E'].width = 50
        ws.column_dimensions['F'].width = 30
        ws.column_dimensions['G'].width = 30
        ws.column_dimensions['H'].width = 15
        ws.column_dimensions['I'].width = 12
        
        # Sauvegarder
        filename = f"Veilles_Export_{timestamp}.xlsx"
        filepath = Path.cwd() / filename
        wb.save(filepath)
        
        create_snackbar(self.page, f"[OK] Exporté: {filename}", "success")
    
    def _export_veilles_pdf(self, veilles, timestamp):
        """Exporte les veilles en PDF."""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        
        filename = f"Veilles_Export_{timestamp}.pdf"
        filepath = Path.cwd() / filename
        
        doc = SimpleDocTemplate(str(filepath), pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()
        
        # Titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#3B82F6'),
            spaceAfter=30,
            alignment=1,
        )
        elements.append(Paragraph("Registre des Veilles Réglementaires", title_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Tableau
        data = [['ID', 'Source', 'Date', 'Description', 'Statut', 'No Plan']]
        
        for v in veilles:
            desc = (v['description'][:80] + '...') if len(v['description']) > 80 else v['description']
            data.append([
                str(v['id']),
                v['source'][:15],
                v['date_lecture'] or '-',
                desc,
                v['statut_veille'],
                v.get('plan_action_numero', '-'),
            ])
        
        table = Table(data, colWidths=[2*cm, 4*cm, 3*cm, 10*cm, 3*cm, 2.5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        create_snackbar(self.page, f"[OK] Exporté: {filename}", "success")
    
    def _export_plans(self, format_type):
        """Exporte les plans d'actions en PDF ou Excel."""
        plans = self.db.get_all_action_plans()
        
        if not plans:
            create_snackbar(self.page, "[Attention] Aucun plan à exporter", "error")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format_type == "excel":
                self._export_plans_excel(plans, timestamp)
            else:
                self._export_plans_pdf(plans, timestamp)
                
        except Exception as ex:
            create_snackbar(self.page, f"[Erreur] Erreur export: {str(ex)}", "error")
    
    def _export_plans_excel(self, plans, timestamp):
        """Exporte les plans d'actions en Excel."""
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Plans d'Actions"
        
        # En-têtes
        headers = ['ID', 'Date Création', 'Origine', 'Objectif', 'Priorité', 'Type', 
                   'Auteurs', 'Échéance', 'Soldé le', 'Avancement %']
        ws.append(headers)
        
        # Style des en-têtes
        header_fill = PatternFill(start_color="8B5CF6", end_color="8B5CF6", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Données
        for p in plans:
            ws.append([
                p['id'],
                p['date_creation'],
                p['origine'],
                p['objectif'],
                p['priorite'],
                p['type_action'],
                p['auteurs'],
                p['date_fin_prevue'],
                p['date_solde'] or '-',
                f"{p.get('statut_calcule', 0):.0f}%",
            ])
        
        # Ajuster largeurs
        for idx, width in enumerate([8, 12, 20, 40, 12, 15, 20, 12, 12, 12], start=1):
            ws.column_dimensions[chr(64 + idx)].width = width
        
        # Sauvegarder
        filename = f"Plans_Actions_Export_{timestamp}.xlsx"
        filepath = Path.cwd() / filename
        wb.save(filepath)
        
        create_snackbar(self.page, f"[OK] Exporté: {filename}", "success")
    
    def _export_plans_pdf(self, plans, timestamp):
        """Exporte les plans d'actions en PDF."""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        
        filename = f"Plans_Actions_Export_{timestamp}.pdf"
        filepath = Path.cwd() / filename
        
        doc = SimpleDocTemplate(str(filepath), pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()
        
        # Titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#8B5CF6'),
            spaceAfter=30,
            alignment=1,
        )
        elements.append(Paragraph("Plans d'Actions", title_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Tableau
        data = [['ID', 'Créé', 'Origine', 'Objectif', 'Priorité', 'Type', 'Échéance', 'Avancement']]
        
        for p in plans:
            obj = (p['objectif'][:60] + '...') if len(p['objectif']) > 60 else p['objectif']
            data.append([
                str(p['id']),
                p['date_creation'][:10],
                p['origine'][:15],
                obj,
                p['priorite'],
                p['type_action'][:10],
                p['date_fin_prevue'],
                f"{p.get('statut_calcule', 0):.0f}%",
            ])
        
        table = Table(data, colWidths=[1.5*cm, 2.5*cm, 3*cm, 9*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B5CF6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        create_snackbar(self.page, f"[OK] Exporté: {filename}", "success")
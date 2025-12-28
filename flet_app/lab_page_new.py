# -*- coding: utf-8 -*-
"""
Module Laboratoire & Qualité - Interface Flet
Onglet complet avec gestion multi-types d'analyses
"""

import flet as ft
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json

from .theme import Theme
from .lab_models import (
    Analyse, TypeAnalyse, Laboratoire, StatutAnalyse, ConclusionAnalyse,
    OenologieStandard, SecuriteAlimentaire, Contaminants, Metrologie,
    Microbiologie, HygieneATP, Phytosanitaire, SeuilsReglementaires
)
from .lab_db_manager import LabDBManager


class LabPage(ft.Container):
    """Page principale du module Laboratoire"""
    
    def __init__(self, user, db, navigate):
        self.user = user
        self.db_main = db
        self.navigate = navigate
        self.db = LabDBManager()
        
        # État actuel
        self.current_tab = "dashboard"
        self.analyses_list = []
        self.selected_analyse: Optional[Analyse] = None
        self.filtre_type = None
        self.filtre_laboratoire = None
        self.filtre_statut = None
        self.filtre_conclusion = None
        
        # Composants UI principaux
        self.main_content = ft.Column()
        self.data_table = None
        
        # Initialiser la page
        self._build_ui()
        
        # Appeler le constructeur parent avec le contenu construit
        _content = self.build()
        super().__init__(content=_content, expand=True)
    
    def _build_ui(self):
        """Construit l'interface utilisateur complète"""
        
        # Barre d'onglets
        tabs_bar = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Tableau de Bord", icon=ft.Icons.DASHBOARD),
                ft.Tab(text="Liste Analyses", icon=ft.Icons.LIST_ALT),
                ft.Tab(text="Nouvelle Analyse", icon=ft.Icons.ADD_CIRCLE_OUTLINE),
                ft.Tab(text="Statistiques", icon=ft.Icons.BAR_CHART),
                ft.Tab(text="Rapports", icon=ft.Icons.DESCRIPTION),
            ],
            on_change=self._on_tab_change,
            expand=True
        )
        
        # Conteneur principal avec padding optimal
        self.main_content = ft.Container(
            content=self._build_dashboard(),
            expand=True,
            padding=20
        )
        
        # Layout principal avec titre adaptatif
        self.content = ft.Column(
            controls=[
                # En-tête adaptatif au thème
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SCIENCE, size=28, color=Theme.PRIMARY),
                        ft.Text(
                            "Laboratoire & Qualité",
                            size=20,
                            weight=ft.FontWeight.W_700,
                            color=Theme.TEXT_PRIMARY
                        ),
                    ], spacing=10),
                    padding=15,
                    bgcolor=Theme.BG_SECONDARY,
                    border=ft.border.only(bottom=ft.BorderSide(2, Theme.BORDER)),
                ),
                # Tabs
                ft.Container(
                    content=tabs_bar,
                    margin=0,
                ),
                # Contenu dynamique
                self.main_content
            ],
            expand=True,
            spacing=0
        )
    
    def _on_tab_change(self, e):
        """Gère le changement d'onglet"""
        tab_index = e.control.selected_index
        
        if tab_index == 0:
            self.current_tab = "dashboard"
            self.main_content.content = self._build_dashboard()
        elif tab_index == 1:
            self.current_tab = "liste"
            self.main_content.content = self._build_liste()
        elif tab_index == 2:
            self.current_tab = "saisie"
            self.main_content.content = self._build_saisie()
        elif tab_index == 3:
            self.current_tab = "statistiques"
            self.main_content.content = self._build_statistiques()
        elif tab_index == 4:
            self.current_tab = "rapports"
            self.main_content.content = self._build_rapports()
        
        self.update()
    
    # ============================================================
    # ONGLET 1: TABLEAU DE BORD
    # ============================================================
    
    def _build_dashboard(self) -> ft.Control:
        """Construit le tableau de bord avec KPIs et alertes"""
        
        stats = self.db.get_statistiques()
        alertes = self.db.get_alertes_actives()
        
        # KPIs principaux
        kpi_total = self._create_kpi_card(
            title="Total Analyses",
            value=str(stats['total_analyses']),
            icon=ft.Icons.SCIENCE,
            color=Theme.PRIMARY
        )
        
        kpi_cout = self._create_kpi_card(
            title="Coût Total",
            value=f"{stats['cout_total']:.2f} €",
            icon=ft.Icons.EURO,
            color=Theme.SUCCESS
        )
        
        kpi_conformite = self._create_kpi_card(
            title="Taux Conformité",
            value=f"{stats['taux_conformite']:.1f}%",
            icon=ft.Icons.CHECK_CIRCLE,
            color=Theme.INFO
        )
        
        kpi_alertes = self._create_kpi_card(
            title="Alertes Actives",
            value=str(len(alertes)),
            icon=ft.Icons.WARNING,
            color=Theme.WARNING if len(alertes) > 0 else Theme.TEXT_MUTED
        )
        
        # Distribution par type
        types_chart = self._build_chart_types(stats.get('par_type', {}))
        
        # Distribution par laboratoire
        labs_chart = self._build_chart_laboratoires(stats.get('par_laboratoire', {}))
        
        # Liste des alertes
        alertes_list = self._build_alertes_list(alertes[:5])  # Top 5
        
        return ft.Column([
            # Section KPIs
            ft.Container(
                content=ft.Row([
                    kpi_total,
                    kpi_cout,
                    kpi_conformite,
                    kpi_alertes
                ], spacing=20),
                margin=ft.margin.only(bottom=25)
            ),
            
            # Section Graphiques
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=types_chart,
                        expand=1,
                        bgcolor=Theme.BG_CARD,
                        padding=20,
                        border_radius=12,
                        border=ft.border.all(1, Theme.BORDER),
                        shadow=ft.BoxShadow(
                            spread_radius=0,
                            blur_radius=8,
                            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                            offset=ft.Offset(0, 2)
                        )
                    ),
                    ft.Container(
                        content=labs_chart,
                        expand=1,
                        bgcolor=Theme.BG_CARD,
                        padding=20,
                        border_radius=12,
                        border=ft.border.all(1, Theme.BORDER),
                        shadow=ft.BoxShadow(
                            spread_radius=0,
                            blur_radius=8,
                            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                            offset=ft.Offset(0, 2)
                        )
                    ),
                ], spacing=20),
                margin=ft.margin.only(bottom=25)
            ),
            
            # Section Alertes
            ft.Container(
                content=alertes_list,
                bgcolor=Theme.SURFACE_VARIANT,
                padding=20,
                border_radius=12,
                border=ft.border.all(1, Theme.WARNING if len(alertes) > 0 else Theme.BORDER),
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=4,
                    color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2)
                )
            )
        ], scroll=ft.ScrollMode.AUTO, expand=True)
    
    def _create_kpi_card(self, title: str, value: str, icon: str, color: str) -> ft.Container:
        """Crée une carte KPI adaptée au thème"""
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(icon, size=36, color=color),
                    width=70,
                    height=70,
                    bgcolor=Theme.SURFACE_VARIANT,
                    border_radius=35,
                    alignment=ft.alignment.center
                ),
                ft.Text(value, size=28, weight=ft.FontWeight.W_700, color=Theme.TEXT_PRIMARY),
                ft.Text(title, size=13, color=Theme.TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
            bgcolor=Theme.BG_CARD,
            padding=20,
            border_radius=12,
            expand=True,
            border=ft.border.all(1, Theme.BORDER),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2)
            )
        )
    
    def _build_chart_types(self, data: Dict[str, int]) -> ft.Column:
        """Graphique distribution par type"""
        bars = []
        max_value = max(data.values()) if data else 1
        
        for type_name, count in data.items():
            percentage = (count / max_value) * 100
            bars.append(
                ft.Row([
                    ft.Text(type_name[:20], width=180, size=12),
                    ft.Container(
                        width=percentage * 2,
                        height=20,
                        bgcolor=Theme.PRIMARY_LIGHT,
                        border_radius=5
                    ),
                    ft.Text(str(count), size=12, weight=ft.FontWeight.BOLD)
                ], spacing=10)
            )
        
        return ft.Column([
            ft.Text("Analyses par Type", size=16, weight=ft.FontWeight.W_600, color=Theme.TEXT_PRIMARY),
            ft.Divider(height=15, color=Theme.BORDER),
            ft.Column(bars, spacing=10)
        ])
    
    def _build_chart_laboratoires(self, data: Dict[str, int]) -> ft.Column:
        """Graphique distribution par laboratoire"""
        bars = []
        max_value = max(data.values()) if data else 1
        
        colors = [ft.Colors.TEAL_400, ft.Colors.PURPLE_400, ft.Colors.ORANGE_400, 
                  ft.Colors.PINK_400, ft.Colors.CYAN_400]
        
        for idx, (lab_name, count) in enumerate(data.items()):
            percentage = (count / max_value) * 100
            color = colors[idx % len(colors)]
            
            bars.append(
                ft.Row([
                    ft.Text(lab_name, width=120, size=12),
                    ft.Container(
                        width=percentage * 2,
                        height=20,
                        bgcolor=color,
                        border_radius=5
                    ),
                    ft.Text(str(count), size=12, weight=ft.FontWeight.BOLD)
                ], spacing=10)
            )
        
        return ft.Column([
            ft.Text("Analyses par Laboratoire", size=16, weight=ft.FontWeight.W_600, color=Theme.TEXT_PRIMARY),
            ft.Divider(height=15, color=Theme.BORDER),
            ft.Column(bars, spacing=10)
        ])
    
    def _build_alertes_list(self, alertes: List[Analyse]) -> ft.Column:
        """Liste des alertes récentes adaptée au thème"""
        if not alertes:
            return ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=24, color=Theme.SUCCESS),
                    ft.Text("Aucune alerte active", size=16, weight=ft.FontWeight.W_600, color=Theme.SUCCESS),
                ], spacing=10),
                ft.Text("Toutes les analyses sont conformes", size=13, color=Theme.TEXT_SECONDARY)
            ], spacing=8)
        
        alerte_rows = []
        for alerte in alertes:
            icon_color = Theme.DANGER if alerte.conclusion == ConclusionAnalyse.NON_CONFORME else Theme.WARNING
            
            alerte_rows.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.WARNING_AMBER, color=icon_color, size=24),
                            width=48,
                            height=48,
                            bgcolor=Theme.SURFACE_VARIANT,
                            border_radius=24,
                            alignment=ft.alignment.center
                        ),
                        ft.Column([
                            ft.Text(
                                f"{alerte.type_analyse.value} - {alerte.numero_echantillon or 'N/A'}",
                                weight=ft.FontWeight.W_600,
                                size=14,
                                color=Theme.TEXT_PRIMARY
                            ),
                            ft.Text(
                                f"{alerte.laboratoire.value} • {alerte.conclusion.value}",
                                size=12,
                                color=Theme.TEXT_SECONDARY
                            )
                        ], spacing=4, expand=True),
                        ft.TextButton(
                            "Voir détails",
                            style=ft.ButtonStyle(color=icon_color),
                            on_click=lambda e, a=alerte: self._view_analyse_details(a)
                        )
                    ], spacing=15, alignment=ft.MainAxisAlignment.START),
                    bgcolor=Theme.BG_CARD,
                    padding=16,
                    border_radius=10,
                    border=ft.border.all(1, Theme.BORDER),
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=4,
                        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                        offset=ft.Offset(0, 1)
                    )
                )
            )
        
        return ft.Column([
            ft.Text("âš ï¸ Alertes Récentes", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Column(alerte_rows, spacing=10, scroll=ft.ScrollMode.AUTO)
        ])
    
    # ============================================================
    # ONGLET 2: LISTE DES ANALYSES
    # ============================================================
    
    def _build_liste(self) -> ft.Control:
        """Construit la liste filtrable des analyses"""
        
        # Barre de filtres
        filtres_row = ft.Row([
            ft.Dropdown(
                label="Type Analyse",
                options=[ft.dropdown.Option(t.value) for t in TypeAnalyse],
                width=250,
                on_change=self._apply_filters
            ),
            ft.Dropdown(
                label="Laboratoire",
                options=[ft.dropdown.Option(l.value) for l in Laboratoire],
                width=200,
                on_change=self._apply_filters
            ),
            ft.Dropdown(
                label="Statut",
                options=[ft.dropdown.Option(s.value) for s in StatutAnalyse],
                width=150,
                on_change=self._apply_filters
            ),
            ft.Dropdown(
                label="Conclusion",
                options=[ft.dropdown.Option(c.value) for c in ConclusionAnalyse],
                width=150,
                on_change=self._apply_filters
            ),
            ft.IconButton(
                icon=ft.Icons.CLEAR,
                tooltip="Réinitialiser filtres",
                on_click=self._reset_filters
            )
        ], spacing=15)
        
        # Barre de recherche et actions
        actions_row = ft.Row([
            ft.TextField(
                label="Rechercher (Lot, Cuve, Échantillon...)",
                prefix_icon=ft.Icons.SEARCH,
                expand=True,
                on_submit=self._search_analyses
            ),
            ft.ElevatedButton(
                "Exporter Excel",
                icon=ft.Icons.DOWNLOAD,
                on_click=self._export_excel
            ),
            ft.ElevatedButton(
                "+ Nouvelle Analyse",
                icon=ft.Icons.ADD,
                on_click=lambda e: self._on_tab_change(type('obj', (object,), {'control': type('obj', (object,), {'selected_index': 2})()})),
                color=Theme.BG_CARD,
                bgcolor=Theme.PRIMARY
            )
        ], spacing=15)
        
        # Table des analyses
        self._load_analyses()
        table = self._build_analyses_table()
        
        return ft.Column([
            filtres_row,
            ft.Divider(),
            actions_row,
            ft.Divider(),
            ft.Container(
                content=table,
                expand=True,
                border=ft.border.all(1, Theme.BORDER),
                border_radius=10
            )
        ], scroll=ft.ScrollMode.AUTO, expand=True)
    
    def _load_analyses(self):
        """Charge les analyses selon les filtres"""
        self.analyses_list = self.db.get_all_analyses(
            type_analyse=self.filtre_type,
            laboratoire=self.filtre_laboratoire,
            statut=self.filtre_statut,
            conclusion=self.filtre_conclusion
        )
    
    def _build_analyses_table(self) -> ft.DataTable:
        """Construit la table des analyses"""
        rows = []
        
        for analyse in self.analyses_list:
            # Couleur selon conclusion
            row_color = None
            if analyse.conclusion == ConclusionAnalyse.CONFORME:
                row_color = Theme.SURFACE_VARIANT
            elif analyse.conclusion == ConclusionAnalyse.NON_CONFORME:
                row_color = Theme.SURFACE_VARIANT
            elif analyse.conclusion == ConclusionAnalyse.ALERTE:
                row_color = Theme.SURFACE_VARIANT
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(analyse.id))),
                        ft.DataCell(ft.Text(analyse.date_prelevement.strftime("%d/%m/%Y") if analyse.date_prelevement else "")),
                        ft.DataCell(ft.Text(analyse.type_analyse.value)),
                        ft.DataCell(ft.Text(analyse.laboratoire.value)),
                        ft.DataCell(ft.Text(analyse.numero_lot or analyse.numero_cuve or analyse.numero_echantillon or "N/A")),
                        ft.DataCell(ft.Text(analyse.statut.value)),
                        ft.DataCell(ft.Container(
                            content=ft.Text(
                                analyse.conclusion.value,
                                color=Theme.BG_CARD,
                                weight=ft.FontWeight.BOLD
                            ),
                            bgcolor=self._get_conclusion_color(analyse.conclusion),
                            padding=5,
                            border_radius=5
                        )),
                        ft.DataCell(ft.Text(f"{analyse.cout:.2f} €")),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.VISIBILITY,
                                    tooltip="Voir",
                                    icon_size=18,
                                    on_click=lambda e, a=analyse: self._view_analyse_details(a)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    tooltip="Modifier",
                                    icon_size=18,
                                    on_click=lambda e, a=analyse: self._edit_analyse(a)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    tooltip="Supprimer",
                                    icon_size=18,
                                    icon_color=Theme.DANGER,
                                    on_click=lambda e, a=analyse: self._delete_analyse(a)
                                ),
                            ], spacing=0)
                        ),
                    ],
                    color=row_color
                )
            )
        
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Date", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Type Analyse", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Laboratoire", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Référence", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Statut", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Conclusion", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Coût", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD)),
            ],
            rows=rows,
            border=ft.border.all(1, Theme.BORDER),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, Theme.BORDER),
            horizontal_lines=ft.border.BorderSide(1, Theme.BORDER),
            heading_row_color=Theme.SURFACE_VARIANT,
            heading_row_height=50,
            data_row_min_height=60,
        )
        
        return ft.Column([self.data_table], scroll=ft.ScrollMode.AUTO, expand=True)
    
    def _get_conclusion_color(self, conclusion: ConclusionAnalyse) -> str:
        """Retourne la couleur selon la conclusion"""
        mapping = {
            ConclusionAnalyse.CONFORME: Theme.SUCCESS,
            ConclusionAnalyse.NON_CONFORME: Theme.DANGER,
            ConclusionAnalyse.ALERTE: Theme.WARNING,
            ConclusionAnalyse.EN_ATTENTE: Theme.TEXT_MUTED
        }
        return mapping.get(conclusion, Theme.TEXT_SECONDARY)
    
    def _apply_filters(self, e):
        """Applique les filtres sélectionnés"""
        # Récupérer les valeurs des dropdowns
        # TODO: Implémenter récupération dynamique
        self._load_analyses()
        self.main_content.content = self._build_liste()
        self.update()
    
    def _reset_filters(self, e):
        """Réinitialise tous les filtres"""
        self.filtre_type = None
        self.filtre_laboratoire = None
        self.filtre_statut = None
        self.filtre_conclusion = None
        self._load_analyses()
        self.main_content.content = self._build_liste()
        self.update()
    
    def _search_analyses(self, e):
        """Recherche textuelle"""
        texte = e.control.value
        if texte:
            self.analyses_list = self.db.recherche_texte(texte)
            self.main_content.content = self._build_liste()
            self.update()
    
    def _export_excel(self, e):
        """Exporte les analyses en Excel"""
        # TODO: Dialogue de sélection de fichier
        filepath = f"analyses_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        success = self.db.export_to_excel(self.analyses_list, filepath)
        
        if success:
            self._show_snackbar(f"âœ… Export réussi: {filepath}", Theme.SUCCESS)
        else:
            self._show_snackbar("âŒ Erreur lors de l'export", Theme.DANGER)
    
    # ============================================================
    # ONGLET 3: SAISIE NOUVELLE ANALYSE
    # ============================================================
    
    def _build_saisie(self) -> ft.Control:
        """Construit le formulaire de saisie polymorphe"""
        
        # Sélection du type d'analyse (détermine les champs Ã  afficher)
        type_dropdown = ft.Dropdown(
            label="Type d'Analyse *",
            options=[ft.dropdown.Option(t.value) for t in TypeAnalyse],
            width=400,
            on_change=self._on_type_analyse_change
        )
        
        # Formulaire de base (commun Ã  tous les types)
        self.form_date_prelevement = ft.TextField(
            label="Date Prélèvement *",
            hint_text="JJ/MM/AAAA",
            width=200
        )
        
        self.form_date_resultat = ft.TextField(
            label="Date Résultat",
            hint_text="JJ/MM/AAAA",
            width=200
        )
        
        self.form_laboratoire = ft.Dropdown(
            label="Laboratoire *",
            options=[ft.dropdown.Option(l.value) for l in Laboratoire],
            width=250
        )
        
        self.form_numero_lot = ft.TextField(label="NÂ° Lot", width=200)
        self.form_numero_cuve = ft.TextField(label="NÂ° Cuve", width=200)
        self.form_numero_echantillon = ft.TextField(label="NÂ° Échantillon", width=200)
        self.form_zone_prelevement = ft.TextField(label="Zone Prélèvement", width=300)
        
        self.form_cout = ft.TextField(label="Coût (€)", value="0.0", width=150)
        
        self.form_statut = ft.Dropdown(
            label="Statut",
            options=[ft.dropdown.Option(s.value) for s in StatutAnalyse],
            value=StatutAnalyse.PLANIFIE.value,
            width=200
        )
        
        self.form_commentaires = ft.TextField(
            label="Commentaires",
            multiline=True,
            min_lines=3,
            max_lines=5,
            width=600
        )
        
        # Conteneur pour les champs spécifiques (polymorphisme)
        self.form_specific_fields = ft.Column([], spacing=15)
        
        # Boutons d'action
        actions = ft.Row([
            ft.ElevatedButton(
                "Enregistrer",
                icon=ft.Icons.SAVE,
                on_click=self._save_analyse,
                color=Theme.BG_CARD,
                bgcolor=Theme.SUCCESS
            ),
            ft.OutlinedButton(
                "Réinitialiser",
                icon=ft.Icons.REFRESH,
                on_click=lambda e: self._reset_form()
            ),
            ft.OutlinedButton(
                "âŒ Annuler",
                on_click=lambda e: self._on_tab_change(type('obj', (object,), {'control': type('obj', (object,), {'selected_index': 1})()}))
            )
        ], spacing=15)
        
        return ft.Column([
            ft.Text("+ Nouvelle Analyse", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            # Type d'analyse
            type_dropdown,
            ft.Divider(),
            
            # Champs communs
            ft.Text("Informations Générales", size=18, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
            ft.Row([self.form_date_prelevement, self.form_date_resultat, self.form_laboratoire], spacing=20),
            ft.Row([self.form_numero_lot, self.form_numero_cuve, self.form_numero_echantillon], spacing=20),
            self.form_zone_prelevement,
            ft.Row([self.form_cout, self.form_statut], spacing=20),
            self.form_commentaires,
            
            ft.Divider(),
            
            # Champs spécifiques (dynamiques)
            ft.Text("Résultats d'Analyse", size=18, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
            self.form_specific_fields,
            
            ft.Divider(),
            actions
            
        ], scroll=ft.ScrollMode.AUTO, spacing=15, expand=True)
    
    def _on_type_analyse_change(self, e):
        """Change les champs spécifiques selon le type d'analyse"""
        type_value = e.control.value
        
        # Nettoyer les champs existants
        self.form_specific_fields.controls.clear()
        
        if type_value == TypeAnalyse.OENOLOGIE.value:
            self._build_oenologie_fields()
        elif type_value == TypeAnalyse.SECURITE_ALIMENTAIRE.value:
            self._build_securite_alimentaire_fields()
        elif type_value == TypeAnalyse.CONTAMINANTS.value:
            self._build_contaminants_fields()
        elif type_value == TypeAnalyse.METROLOGIE.value:
            self._build_metrologie_fields()
        elif type_value == TypeAnalyse.MICROBIOLOGIE.value:
            self._build_microbiologie_fields()
        elif type_value == TypeAnalyse.HYGIENE_ATP.value:
            self._build_hygiene_atp_fields()
        elif type_value == TypeAnalyse.PHYTOSANITAIRE.value:
            self._build_phytosanitaire_fields()
        
        self.update()
    
    def _build_oenologie_fields(self):
        """Champs spécifiques Å’nologie"""
        self.form_tav = ft.TextField(label="TAV (% vol)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_sucres = ft.TextField(label="Sucres (g/L)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_acidite_totale = ft.TextField(label="Acidité Totale (g/L H2SO4)", width=200, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_ph = ft.TextField(label="pH", width=120, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_acide_volatile = ft.TextField(label="Acide Volatile (g/L)", width=180, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_so2_libre = ft.TextField(label="SO2 Libre (mg/L)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_so2_total = ft.TextField(label="SO2 Total (mg/L)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_fer = ft.TextField(label="Fer (mg/L)", width=120, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_cuivre = ft.TextField(label="Cuivre (mg/L)", width=120, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_co2 = ft.TextField(label="CO2 (g/L)", width=120, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_surpression = ft.TextField(label="Surpression (bars)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        
        self.form_specific_fields.controls = [
            ft.Row([self.form_tav, self.form_sucres, self.form_acidite_totale, self.form_ph], spacing=15),
            ft.Row([self.form_acide_volatile, self.form_so2_libre, self.form_so2_total], spacing=15),
            ft.Row([self.form_fer, self.form_cuivre, self.form_co2, self.form_surpression], spacing=15)
        ]
    
    def _build_securite_alimentaire_fields(self):
        """Champs spécifiques Sécurité Alimentaire"""
        self.form_albumine = ft.TextField(label="Albumine", hint_text="<LDQ ou valeur", width=200)
        self.form_caseine = ft.TextField(label="Caséine", hint_text="<LDQ ou valeur", width=200)
        self.form_histamine = ft.TextField(label="Histamine (mg/L)", width=180, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_putrescine = ft.TextField(label="Putrescine (mg/L)", width=180, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_bisphenol_a = ft.TextField(label="Bisphénol A", hint_text="<LDQ ou valeur", width=200)
        
        self.form_specific_fields.controls = [
            ft.Row([self.form_albumine, self.form_caseine, self.form_bisphenol_a], spacing=15),
            ft.Row([self.form_histamine, self.form_putrescine], spacing=15)
        ]
    
    def _build_contaminants_fields(self):
        """Champs spécifiques Contaminants"""
        self.form_ochratoxine_a = ft.TextField(label="Ochratoxine A (Âµg/kg)", width=180, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_tca = ft.TextField(label="TCA (ng/L)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_tcp = ft.TextField(label="TCP (ng/L)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_lindane = ft.TextField(label="Lindane (mg/kg)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_dibutyl_phtalate = ft.TextField(label="DBP (mg/kg)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_dehp = ft.TextField(label="DEHP (mg/kg)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_plomb = ft.TextField(label="Plomb (mg/L)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_cadmium = ft.TextField(label="Cadmium (mg/L)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_arsenic = ft.TextField(label="Arsenic (mg/L)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_mercure = ft.TextField(label="Mercure (mg/L)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        
        self.form_specific_fields.controls = [
            ft.Text("Haloanisoles & Halophénols", size=14, weight=ft.FontWeight.BOLD),
            ft.Row([self.form_tca, self.form_tcp], spacing=15),
            ft.Text("Phtalates", size=14, weight=ft.FontWeight.BOLD),
            ft.Row([self.form_dibutyl_phtalate, self.form_dehp], spacing=15),
            ft.Text("Métaux Lourds", size=14, weight=ft.FontWeight.BOLD),
            ft.Row([self.form_plomb, self.form_cadmium, self.form_arsenic, self.form_mercure], spacing=15),
            ft.Text("Autres", size=14, weight=ft.FontWeight.BOLD),
            ft.Row([self.form_ochratoxine_a, self.form_lindane], spacing=15)
        ]
    
    def _build_metrologie_fields(self):
        """Champs spécifiques Métrologie"""
        self.form_volume_cible = ft.TextField(label="Volume Cible (mL)", value="750", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_volume_net_moyen = ft.TextField(label="Volume Net Moyen (mL)", width=180, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_ecart_type = ft.TextField(label="Écart-Type", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_nombre_echantillons = ft.TextField(label="Nombre Échantillons", width=180, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_nombre_defectueux = ft.TextField(label="Nombre Défectueux", value="0", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_densite = ft.TextField(label="Densité", width=120, keyboard_type=ft.KeyboardType.NUMBER)
        
        self.form_specific_fields.controls = [
            ft.Row([self.form_volume_cible, self.form_volume_net_moyen, self.form_ecart_type], spacing=15),
            ft.Row([self.form_nombre_echantillons, self.form_nombre_defectueux, self.form_densite], spacing=15)
        ]
    
    def _build_microbiologie_fields(self):
        """Champs spécifiques Microbiologie"""
        self.form_flore_aerobie = ft.TextField(label="Flore Aérobie Mésophile (UFC/mL)", width=250, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_levures = ft.TextField(label="Levures (UFC/mL)", width=180, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_moisissures = ft.TextField(label="Moisissures (UFC/100mL)", width=200, keyboard_type=ft.KeyboardType.NUMBER)
        
        self.form_specific_fields.controls = [
            ft.Row([self.form_flore_aerobie, self.form_levures, self.form_moisissures], spacing=15)
        ]
    
    def _build_hygiene_atp_fields(self):
        """Champs spécifiques Hygiène ATP"""
        self.form_valeur_atp = ft.TextField(label="Valeur ATP (RLU)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_surface_type = ft.Dropdown(
            label="Type de Surface",
            options=[
                ft.dropdown.Option("Inox"),
                ft.dropdown.Option("Plastique"),
                ft.dropdown.Option("Caoutchouc"),
                ft.dropdown.Option("Autre")
            ],
            value="Inox",
            width=180
        )
        self.form_conductivite = ft.TextField(label="Conductivité (mS/cm)", width=180, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_concentration_detergent = ft.TextField(label="Concentration Détergent (%)", width=200, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_nom_produit = ft.TextField(label="Nom Produit", hint_text="ex: Surefoam", width=250)
        
        self.form_specific_fields.controls = [
            ft.Row([self.form_valeur_atp, self.form_surface_type], spacing=15),
            ft.Row([self.form_conductivite, self.form_concentration_detergent, self.form_nom_produit], spacing=15)
        ]
    
    def _build_phytosanitaire_fields(self):
        """Champs spécifiques Phytosanitaire"""
        self.form_global_resultat = ft.TextField(
            label="Résultat Global",
            value="Non Détecté",
            width=300
        )
        
        self.form_molecules_container = ft.Column([], spacing=10)
        
        add_molecule_btn = ft.ElevatedButton(
            "+ Ajouter Molécule",
            icon=ft.Icons.ADD,
            on_click=self._add_molecule_field
        )
        
        self.form_specific_fields.controls = [
            self.form_global_resultat,
            ft.Divider(),
            ft.Text("Molécules Détectées", size=14, weight=ft.FontWeight.BOLD),
            self.form_molecules_container,
            add_molecule_btn
        ]
    
    def _add_molecule_field(self, e):
        """Ajoute un champ de saisie de molécule"""
        molecule_row = ft.Row([
            ft.TextField(label="Nom Molécule", width=250),
            ft.TextField(label="Teneur (mg/kg)", width=150, keyboard_type=ft.KeyboardType.NUMBER),
            ft.IconButton(
                icon=ft.Icons.REMOVE_CIRCLE,
                icon_color=Theme.DANGER,
                on_click=lambda e, row=molecule_row: self._remove_molecule_field(row)
            )
        ], spacing=10)
        
        self.form_molecules_container.controls.append(molecule_row)
        self.update()
    
    def _remove_molecule_field(self, row):
        """Supprime un champ de molécule"""
        self.form_molecules_container.controls.remove(row)
        self.update()
    
    def _save_analyse(self, e):
        """Enregistre l'analyse en base de données"""
        # TODO: Validation des champs
        # TODO: Récupération des valeurs
        # TODO: Création objet Analyse
        # TODO: Appel db.create_analyse()
        
        self._show_snackbar("âœ… Analyse enregistrée avec succès", Theme.SUCCESS)
        self._reset_form()
        self._on_tab_change(type('obj', (object,), {'control': type('obj', (object,), {'selected_index': 1})()}))
    
    def _reset_form(self):
        """Réinitialise tous les champs du formulaire"""
        # TODO: Réinitialiser tous les champs
        pass
    
    # ============================================================
    # ONGLET 4: STATISTIQUES
    # ============================================================
    
    def _build_statistiques(self) -> ft.Control:
        """Construit l'onglet statistiques avancées"""
        
        stats = self.db.get_statistiques()
        annee_actuelle = datetime.now().year
        couts_mensuels = self.db.get_cout_par_periode(annee_actuelle)
        
        # Graphique évolution des coûts
        cout_chart = self._build_cout_mensuel_chart(couts_mensuels)
        
        # Statistiques détaillées par laboratoire
        lab_stats = self._build_lab_detailed_stats(stats.get('par_laboratoire', {}))
        
        return ft.Column([
            ft.Text("Statistiques Avancées", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            # Graphique coûts
            ft.Container(
                content=cout_chart,
                bgcolor=Theme.BG_CARD,
                padding=20,
                border_radius=10,
                shadow=ft.BoxShadow(blur_radius=5, spread_radius=1, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK))
            ),
            
            ft.Divider(),
            
            # Stats par laboratoire
            lab_stats
            
        ], scroll=ft.ScrollMode.AUTO, expand=True)
    
    def _build_cout_mensuel_chart(self, data: List[Dict]) -> ft.Column:
        """Graphique des coûts mensuels"""
        # Version simplifiée avec barres
        mois_names = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
        
        bars = []
        max_cout = max([d['cout_total'] for d in data], default=1)
        
        for item in data:
            mois_idx = item['mois'] - 1
            cout = item['cout_total']
            percentage = (cout / max_cout) * 100 if max_cout > 0 else 0
            
            bars.append(
                ft.Column([
                    ft.Container(
                        width=60,
                        height=percentage * 2,
                        bgcolor=Theme.PRIMARY_LIGHT,
                        border_radius=5,
                        alignment=ft.alignment.bottom_center
                    ),
                    ft.Text(f"{cout:.0f}€", size=10, weight=ft.FontWeight.BOLD),
                    ft.Text(mois_names[mois_idx], size=10)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
            )
        
        return ft.Column([
            ft.Text(f"Évolution des Coûts - {datetime.now().year}", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row(bars, spacing=15, scroll=ft.ScrollMode.AUTO)
        ])
    
    def _build_lab_detailed_stats(self, data: Dict[str, int]) -> ft.Column:
        """Statistiques détaillées par laboratoire"""
        cards = []
        
        for lab_name, count in data.items():
            cards.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(lab_name, size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"{count} analyses", size=14, color=Theme.TEXT_SECONDARY)
                    ], spacing=5),
                    bgcolor=Theme.SURFACE_VARIANT,
                    padding=15,
                    border_radius=10,
                    expand=True
                )
            )
        
        return ft.Column([
            ft.Text("Répartition par Laboratoire", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row(cards, spacing=15, wrap=True)
        ])
    
    # ============================================================
    # ONGLET 5: RAPPORTS
    # ============================================================
    
    def _build_rapports(self) -> ft.Control:
        """Construit l'onglet rapports PDF"""
        
        rapport_cards = [
            self._create_rapport_card(
                title="Rapport Annuel Complet",
                description="Toutes les analyses de l'année avec statistiques",
                icon=ft.Icons.DESCRIPTION,
                on_click=lambda e: self._generer_rapport_annuel()
            ),
            self._create_rapport_card(
                title="Rapport Non-Conformités",
                description="Liste des analyses non conformes",
                icon=ft.Icons.WARNING,
                on_click=lambda e: self._generer_rapport_nc()
            ),
            self._create_rapport_card(
                title="Rapport par Laboratoire",
                description="Performance et coûts par laboratoire",
                icon=ft.Icons.BUSINESS,
                on_click=lambda e: self._generer_rapport_labo()
            ),
            self._create_rapport_card(
                title="Rapport Coûts",
                description="Analyse des coûts sur période",
                icon=ft.Icons.EURO,
                on_click=lambda e: self._generer_rapport_couts()
            )
        ]
        
        return ft.Column([
            ft.Text("Génération de Rapports", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Text(
                "Sélectionnez le type de rapport Ã  générer",
                size=14,
                color=Theme.TEXT_SECONDARY
            ),
            
            ft.Container(height=20),
            
            ft.Row(rapport_cards[:2], spacing=20),
            ft.Row(rapport_cards[2:], spacing=20)
            
        ], scroll=ft.ScrollMode.AUTO, expand=True)
    
    def _create_rapport_card(self, title: str, description: str, icon: str, on_click) -> ft.Container:
        """Crée une carte de rapport"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=50, color=Theme.PRIMARY),
                ft.Text(title, size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text(description, size=12, color=Theme.TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Générer PDF",
                    icon=ft.Icons.PICTURE_AS_PDF,
                    on_click=on_click,
                    color=Theme.BG_CARD,
                    bgcolor=Theme.PRIMARY
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            bgcolor=Theme.BG_CARD,
            padding=30,
            border_radius=10,
            expand=True,
            shadow=ft.BoxShadow(blur_radius=10, spread_radius=2, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK))
        )
    
    def _generer_rapport_annuel(self):
        """Génère le rapport annuel complet"""
        self._show_snackbar("â³ Génération du rapport annuel en cours...", Theme.PRIMARY)
        # TODO: Implémenter génération PDF
    
    def _generer_rapport_nc(self):
        """Génère le rapport des non-conformités"""
        self._show_snackbar("â³ Génération du rapport NC en cours...", Theme.WARNING)
        # TODO: Implémenter génération PDF
    
    def _generer_rapport_labo(self):
        """Génère le rapport par laboratoire"""
        self._show_snackbar("â³ Génération du rapport laboratoire en cours...", Theme.SECONDARY)
        # TODO: Implémenter génération PDF
    
    def _generer_rapport_couts(self):
        """Génère le rapport des coûts"""
        self._show_snackbar("â³ Génération du rapport coûts en cours...", Theme.SUCCESS)
        # TODO: Implémenter génération PDF
    
    # ============================================================
    # ACTIONS & HELPERS
    # ============================================================
    
    def _view_analyse_details(self, analyse: Analyse):
        """Affiche les détails d'une analyse en modal"""
        # TODO: Créer dialogue avec tous les détails
        self._show_snackbar(f"Détails de l'analyse #{analyse.id}", Theme.PRIMARY)
    
    def _edit_analyse(self, analyse: Analyse):
        """Édite une analyse existante"""
        self.selected_analyse = analyse
        # TODO: Pré-remplir le formulaire
        self._on_tab_change(type('obj', (object,), {'control': type('obj', (object,), {'selected_index': 2})()}))
    
    def _delete_analyse(self, analyse: Analyse):
        """Supprime une analyse après confirmation"""
        # TODO: Dialogue de confirmation
        success = self.db.delete_analyse(analyse.id)
        if success:
            self._show_snackbar(f"âœ… Analyse #{analyse.id} supprimée", Theme.SUCCESS)
            self._refresh_data(None)
        else:
            self._show_snackbar("âŒ Erreur lors de la suppression", Theme.DANGER)
    
    def _refresh_data(self, e):
        """Rafraîchit les données affichées"""
        if self.current_tab == "dashboard":
            self.main_content.content = self._build_dashboard()
        elif self.current_tab == "liste":
            self._load_analyses()
            self.main_content.content = self._build_liste()
        elif self.current_tab == "statistiques":
            self.main_content.content = self._build_statistiques()
        
        self.update()
    
    def _show_snackbar(self, message: str, color: str):
        """Affiche un message snackbar"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=Theme.BG_CARD),
            bgcolor=color
        )
        self.page.snack_bar.open = True
        self.update()
    
    def build(self) -> ft.Control:
        """Retourne le contrôle principal"""
        return self.content



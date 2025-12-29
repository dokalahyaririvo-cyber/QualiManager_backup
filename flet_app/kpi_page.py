# -*- coding: utf-8 -*-
"""
QualiManager ERP QHSE - Module KPI / Data Intelligence
Dashboard consolidé, pyramide des coûts, corrélation, heatmap
"""

import flet as ft
from typing import Dict, Any, Callable, List
from datetime import datetime, timedelta
import math

from .theme import Theme
from .components import (
    create_card, create_text_field, create_dropdown, create_button,
    create_empty_state
)
from .components_advanced import KPICard, CostIndicator


class KPIPage(ft.Container):
    """Page principale du module KPI / Data Intelligence."""
    
    def __init__(self, user: Dict, db, navigate: Callable):
        self.user = user
        self.db = db
        self.navigate = navigate
        self.current_tab = 0
        
        super().__init__(
            expand=True,
            bgcolor=Theme.BG_PRIMARY,
            padding=0,
            content=self._build_ui(),
        )
    
    def _build_ui(self):
        """Construit l'interface principale."""
        header = ft.Container(
            padding=20,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                ft.Icons.ARROW_BACK,
                                icon_color=Theme.TEXT_MUTED,
                                on_click=lambda e: self.navigate("/hub"),
                            ),
                            ft.Column(
                                spacing=0,
                                controls=[
                                    ft.Text(
                                        "[Stats] KPI & Data Intelligence",
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                        color=Theme.TEXT_PRIMARY,
                                    ),
                                    ft.Text(
                                        "Dashboard consolidé et analyses avancées",
                                        size=13,
                                        color=Theme.TEXT_MUTED,
                                    ),
                                ]
                            ),
                        ]
                    ),
                    create_dropdown(
                        "Période",
                        ["Ce mois", "Ce trimestre", "Cette année", "Personnalisé"],
                        value="Ce mois",
                        width=150,
                    ),
                ]
            ),
        )
        
        # Tabs
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=200,
            on_change=self._on_tab_change,
            tabs=[
                ft.Tab(text="[Graphique] Dashboard", icon=ft.Icons.DASHBOARD),
                ft.Tab(text="[Cout] Pyramide Coûts", icon=ft.Icons.STACKED_BAR_CHART),
                ft.Tab(text="[Lien] Corrélations", icon=ft.Icons.HUB),
                ft.Tab(text="[Calendrier] Heatmap", icon=ft.Icons.GRID_VIEW),
            ],
        )
        
        self.tab_content = ft.Container(
            expand=True,
            padding=20,
            content=self._build_dashboard_tab(),
        )
        
        return ft.Column(
            expand=True,
            spacing=0,
            controls=[
                header,
                ft.Container(
                    padding=ft.Padding(left=20, right=20, top=0, bottom=0),
                    content=self.tabs,
                ),
                self.tab_content,
            ]
        )
    
    def _on_tab_change(self, e):
        """Change de tab."""
        self.current_tab = e.control.selected_index
        if self.current_tab == 0:
            self.tab_content.content = self._build_dashboard_tab()
        elif self.current_tab == 1:
            self.tab_content.content = self._build_pyramid_tab()
        elif self.current_tab == 2:
            self.tab_content.content = self._build_correlation_tab()
        else:
            self.tab_content.content = self._build_heatmap_tab()
        self.update()
    
    # ========================================================================
    # TAB 1: DASHBOARD CONSOLIDÉ
    # ========================================================================
    
    def _build_dashboard_tab(self):
        """Construit le dashboard consolidé."""
        stats = self.db.get_stats()
        
        # KPI Row 1 - NC
        kpi_row1 = ft.Row(
            spacing=15,
            controls=[
                KPICard(
                    title="NC Ouvertes",
                    value=str(stats.get('nc_ouvertes', 0)),
                    icon=ft.Icons.WARNING,
                    color=Theme.DANGER,
                    subtitle="Non-conformités actives",
                ),
                KPICard(
                    title="NC Ce mois",
                    value=str(stats.get('nc_ce_mois', 0)),
                    icon=ft.Icons.CALENDAR_TODAY,
                    color=Theme.WARNING,
                    trend=stats.get('nc_trend', 0),
                ),
                KPICard(
                    title="Taux clôture",
                    value=f"{stats.get('taux_cloture_nc', 0):.0f}%",
                    icon=ft.Icons.CHECK_CIRCLE,
                    color=Theme.SUCCESS,
                ),
                KPICard(
                    title="Coût CNQ Total",
                    value=f"{stats.get('cout_cnq_total', 0):,.0f} EUR",
                    icon=ft.Icons.EURO,
                    color=Theme.PRIMARY,
                ),
            ]
        )
        
        # KPI Row 2 - Inspections et Lab
        kpi_row2 = ft.Row(
            spacing=15,
            controls=[
                KPICard(
                    title="Inspections",
                    value=str(stats.get('inspections_total', 0)),
                    icon=ft.Icons.CHECKLIST,
                    color=Theme.INFO,
                    subtitle="Ce mois",
                ),
                KPICard(
                    title="Score moyen",
                    value=f"{stats.get('score_moyen_insp', 0):.0f}%",
                    icon=ft.Icons.SCORE,
                    color=Theme.SUCCESS if stats.get('score_moyen_insp', 0) >= 80 else Theme.WARNING,
                ),
                KPICard(
                    title="Analyses labo",
                    value=str(stats.get('analyses_total', 0)),
                    icon=ft.Icons.SCIENCE,
                    color=Theme.PRIMARY,
                ),
                KPICard(
                    title="Taux conformité",
                    value=f"{stats.get('taux_conformite_lab', 0):.0f}%",
                    icon=ft.Icons.VERIFIED,
                    color=Theme.SUCCESS if stats.get('taux_conformite_lab', 0) >= 95 else Theme.WARNING,
                ),
            ]
        )
        
        # KPI Row 3 - Veille et RACI
        kpi_row3 = ft.Row(
            spacing=15,
            controls=[
                KPICard(
                    title="Veilles actives",
                    value=str(stats.get('veilles_actives', 0)),
                    icon=ft.Icons.RADAR,
                    color=Theme.INFO,
                ),
                KPICard(
                    title="Actions RACI",
                    value=str(stats.get('raci_en_cours', 0)),
                    icon=ft.Icons.ASSIGNMENT,
                    color=Theme.WARNING,
                    subtitle="En cours",
                ),
                KPICard(
                    title="Actions en retard",
                    value=str(stats.get('raci_en_retard', 0)),
                    icon=ft.Icons.ALARM,
                    color=Theme.DANGER,
                ),
                KPICard(
                    title="Utilisateurs actifs",
                    value=str(stats.get('users_actifs', 0)),
                    icon=ft.Icons.PEOPLE,
                    color=Theme.PRIMARY,
                ),
            ]
        )
        
        # Graphiques
        nc_by_month_chart = self._create_nc_by_month_chart()
        nc_by_type_chart = self._create_nc_by_type_chart()
        
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[
                # KPIs
                ft.Text("Non-Conformités", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                kpi_row1,
                ft.Text("Inspections & Laboratoire", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                kpi_row2,
                ft.Text("Veille & Actions", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                kpi_row3,
                # Graphiques
                ft.Row(
                    spacing=20,
                    controls=[
                        nc_by_month_chart,
                        nc_by_type_chart,
                    ]
                ),
            ]
        )
    
    def _create_nc_by_month_chart(self) -> ft.Container:
        """Crée un graphique des NC par mois."""
        data = self.db.get_nc_by_month()
        
        if not data:
            return ft.Container(
                expand=True,
                padding=20,
                border_radius=12,
                bgcolor=Theme.BG_SECONDARY,
                content=ft.Text("Pas de données", color=Theme.TEXT_MUTED),
            )
        
        max_val = max(d['count'] for d in data) if data else 1
        
        bars = []
        for d in data[-6:]:  # 6 derniers mois
            height = (d['count'] / max_val) * 120 if max_val > 0 else 0
            bars.append(
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                    controls=[
                        ft.Text(str(d['count']), size=12, color=Theme.TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            width=40,
                            height=height,
                            border_radius=ft.BorderRadius(4, 4, 0, 0),
                            bgcolor=Theme.PRIMARY,
                        ),
                        ft.Text(d['month'][-2:], size=10, color=Theme.TEXT_MUTED),
                    ]
                )
            )
        
        return ft.Container(
            expand=True,
            padding=20,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Column(
                controls=[
                    ft.Text("NC par mois", size=14, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    ft.Container(height=10),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        controls=bars,
                    ),
                ]
            ),
        )
    
    def _create_nc_by_type_chart(self) -> ft.Container:
        """Crée un graphique des NC par type."""
        data = self.db.get_nc_by_type_and_month()
        
        # Agréger par type
        by_type = {}
        for d in data:
            t = d.get('type_nc', 'Autre')
            by_type[t] = by_type.get(t, 0) + d.get('count', 0)
        
        if not by_type:
            return ft.Container(
                expand=True,
                padding=20,
                border_radius=12,
                bgcolor=Theme.BG_SECONDARY,
                content=ft.Text("Pas de données", color=Theme.TEXT_MUTED),
            )
        
        total = sum(by_type.values())
        
        # Couleurs par type
        type_colors = {
            'Produit': Theme.DANGER,
            'Process': Theme.WARNING,
            'Équipement': Theme.INFO,
            'Fournisseur': Theme.PRIMARY,
            'Client': Theme.SUCCESS,
        }
        
        bars = []
        for type_name, count in by_type.items():
            pct = (count / total * 100) if total > 0 else 0
            width = (pct / 100) * 200
            bars.append(
                ft.Row(
                    controls=[
                        ft.Container(
                            width=100,
                            content=ft.Text(type_name, size=12, color=Theme.TEXT_SECONDARY),
                        ),
                        ft.Container(
                            width=width,
                            height=20,
                            border_radius=4,
                            bgcolor=type_colors.get(type_name, Theme.TEXT_MUTED),
                        ),
                        ft.Text(f"{count} ({pct:.0f}%)", size=11, color=Theme.TEXT_PRIMARY),
                    ]
                )
            )
        
        return ft.Container(
            expand=True,
            padding=20,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Column(
                controls=[
                    ft.Text("NC par type", size=14, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    ft.Container(height=10),
                    *bars,
                ]
            ),
        )
    
    # ========================================================================
    # TAB 2: PYRAMIDE DES COÛTS
    # ========================================================================
    
    def _build_pyramid_tab(self):
        """Construit la pyramide des coûts qualité."""
        costs = self.db.get_quality_costs()
        
        # Catégories de coûts COQ (Cost of Quality)
        prevention = costs.get('prevention', 0)  # Formation, HACCP, etc.
        evaluation = costs.get('evaluation', 0)  # Contrôles, analyses
        defaillance_int = costs.get('defaillance_interne', 0)  # Rebuts, retouches
        defaillance_ext = costs.get('defaillance_externe', 0)  # Réclamations, rappels
        
        total_coq = prevention + evaluation + defaillance_int + defaillance_ext
        
        # Calcul des pourcentages
        def pct(val):
            return (val / total_coq * 100) if total_coq > 0 else 0
        
        # Pyramide visuelle
        pyramid = ft.Container(
            padding=30,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                controls=[
                    ft.Text("Pyramide des Coûts Qualité", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    ft.Container(height=20),
                    # Niveau 4 - Défaillance externe (sommet)
                    self._create_pyramid_level(
                        "Défaillance externe",
                        defaillance_ext,
                        pct(defaillance_ext),
                        Theme.DANGER,
                        width=150,
                        tooltip="Réclamations clients, rappels, pénalités",
                    ),
                    # Niveau 3 - Défaillance interne
                    self._create_pyramid_level(
                        "Défaillance interne",
                        defaillance_int,
                        pct(defaillance_int),
                        Theme.WARNING,
                        width=250,
                        tooltip="Rebuts, retouches, arrêts production",
                    ),
                    # Niveau 2 - Évaluation
                    self._create_pyramid_level(
                        "Évaluation",
                        evaluation,
                        pct(evaluation),
                        Theme.INFO,
                        width=350,
                        tooltip="Contrôles, analyses, inspections, audits",
                    ),
                    # Niveau 1 - Prévention (base)
                    self._create_pyramid_level(
                        "Prévention",
                        prevention,
                        pct(prevention),
                        Theme.SUCCESS,
                        width=450,
                        tooltip="Formation, HACCP, maintenance préventive",
                    ),
                    ft.Container(height=20),
                    # Total
                    ft.Container(
                        padding=15,
                        border_radius=10,
                        bgcolor=Theme.BG_TERTIARY,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20,
                            controls=[
                                ft.Text("COÛT TOTAL QUALITÉ:", size=14, color=Theme.TEXT_MUTED),
                                ft.Text(f"{total_coq:,.0f} EUR", size=20, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
                            ]
                        ),
                    ),
                ]
            ),
        )
        
        # Détail des coûts par NC
        nc_costs = self.db.get_nc_costs_detail()
        
        cost_table_rows = []
        for nc in nc_costs[:10]:  # Top 10
            cost_table_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(nc.get('reference', '-'), size=12, color=Theme.PRIMARY)),
                        ft.DataCell(ft.Text(nc.get('designation', '-')[:30], size=12, color=Theme.TEXT_PRIMARY)),
                        ft.DataCell(ft.Text(f"{nc.get('cout_matiere', 0):,.0f} EUR", size=12, color=Theme.TEXT_SECONDARY)),
                        ft.DataCell(ft.Text(f"{nc.get('cout_mo', 0):,.0f} EUR", size=12, color=Theme.TEXT_SECONDARY)),
                        ft.DataCell(ft.Text(f"{nc.get('cout_destruction', 0):,.0f} EUR", size=12, color=Theme.TEXT_SECONDARY)),
                        ft.DataCell(
                            CostIndicator(
                                value=nc.get('cout_total', 0),
                                size="small",
                            )
                        ),
                    ]
                )
            )
        
        cost_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Référence", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Désignation", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Matière", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Main d'oeuvre", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Destruction", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Total", size=12, weight=ft.FontWeight.BOLD)),
            ],
            rows=cost_table_rows,
            border=ft.Border(
                top=ft.BorderSide(1, Theme.BG_TERTIARY),
                right=ft.BorderSide(1, Theme.BG_TERTIARY),
                bottom=ft.BorderSide(1, Theme.BG_TERTIARY),
                left=ft.BorderSide(1, Theme.BG_TERTIARY),
            ),
            border_radius=8,
            heading_row_color=Theme.BG_TERTIARY,
        )
        
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[
                pyramid,
                ft.Text("Top 10 NC par coût", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                ft.Row(scroll=ft.ScrollMode.AUTO, controls=[cost_table]),
            ]
        )
    
    def _create_pyramid_level(self, label: str, value: float, pct: float, 
                              color: str, width: float, tooltip: str) -> ft.Container:
        """Crée un niveau de la pyramide."""
        return ft.Container(
            width=width,
            padding=ft.Padding(left=0, right=0, top=15, bottom=15),
            bgcolor=color,
            tooltip=tooltip,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
                controls=[
                    ft.Text(label, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{value:,.0f} EUR ({pct:.1f}%)", size=11, color=ft.Colors.WHITE),
                ]
            ),
        )
    
    # ========================================================================
    # TAB 3: CORRÉLATIONS
    # ========================================================================
    
    def _build_correlation_tab(self):
        """Construit l'onglet des corrélations."""
        # Données de corrélation
        correlations = self.db.get_correlation_data()
        
        # Matrice de corrélation simplifiée
        variables = ['NC', 'Inspections', 'Analyses', 'Coûts']
        
        # Génération de la matrice (exemple avec données simulées)
        matrix_data = [
            [1.0, -0.65, -0.45, 0.85],  # NC
            [-0.65, 1.0, 0.72, -0.58],  # Inspections
            [-0.45, 0.72, 1.0, -0.42],  # Analyses
            [0.85, -0.58, -0.42, 1.0],  # Coûts
        ]
        
        # Créer la matrice visuelle
        matrix_rows = []
        
        # Header
        header_cells = [ft.Container(width=100)]
        for var in variables:
            header_cells.append(
                ft.Container(
                    width=80,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(var, size=11, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                )
            )
        matrix_rows.append(ft.Row(controls=header_cells))
        
        # Lignes de données
        for i, row_var in enumerate(variables):
            row_cells = [
                ft.Container(
                    width=100,
                    content=ft.Text(row_var, size=11, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                )
            ]
            for j, val in enumerate(matrix_data[i]):
                # Couleur selon la valeur
                if val >= 0.7:
                    bg = Theme.SUCCESS
                elif val >= 0.3:
                    bg = Theme.INFO
                elif val <= -0.7:
                    bg = Theme.DANGER
                elif val <= -0.3:
                    bg = Theme.WARNING
                else:
                    bg = Theme.BG_TERTIARY
                
                row_cells.append(
                    ft.Container(
                        width=80,
                        height=50,
                        bgcolor=bg,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(
                            f"{val:.2f}",
                            size=12,
                            color=ft.Colors.WHITE if abs(val) > 0.3 else Theme.TEXT_PRIMARY,
                            weight=ft.FontWeight.BOLD if abs(val) > 0.5 else None,
                        ),
                    )
                )
            matrix_rows.append(ft.Row(controls=row_cells))
        
        matrix_card = ft.Container(
            padding=20,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Column(
                controls=[
                    ft.Text("Matrice de corrélation", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    ft.Container(height=10),
                    ft.Column(spacing=2, controls=matrix_rows),
                    ft.Container(height=15),
                    # Légende
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=15,
                        controls=[
                            self._create_corr_legend("Forte +", Theme.SUCCESS),
                            self._create_corr_legend("Modérée +", Theme.INFO),
                            self._create_corr_legend("Faible", Theme.BG_TERTIARY),
                            self._create_corr_legend("Modérée -", Theme.WARNING),
                            self._create_corr_legend("Forte -", Theme.DANGER),
                        ]
                    ),
                ]
            ),
        )
        
        # Insights
        insights = [
            {
                'icon': ft.Icons.TRENDING_UP,
                'color': Theme.DANGER,
                'title': "NC <> Coûts: +0.85",
                'desc': "Forte corrélation positive - plus de NC = plus de coûts CNQ",
            },
            {
                'icon': ft.Icons.TRENDING_DOWN,
                'color': Theme.SUCCESS,
                'title': "Inspections <> NC: -0.65",
                'desc': "Plus d'inspections = moins de NC détectées en aval",
            },
            {
                'icon': ft.Icons.INSIGHTS,
                'color': Theme.INFO,
                'title': "Analyses <> Inspections: +0.72",
                'desc': "Les contrôles labo et terrain sont complémentaires",
            },
        ]
        
        insight_cards = []
        for ins in insights:
            insight_cards.append(
                ft.Container(
                    expand=True,
                    padding=15,
                    border_radius=10,
                    bgcolor=Theme.BG_SECONDARY,
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                padding=10,
                                border_radius=8,
                                bgcolor=ins['color'],
                                content=ft.Icon(ins['icon'], size=20, color=ft.Colors.WHITE),
                            ),
                            ft.Container(width=10),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(ins['title'], size=13, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                                    ft.Text(ins['desc'], size=11, color=Theme.TEXT_SECONDARY),
                                ]
                            ),
                        ]
                    ),
                )
            )
        
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[
                matrix_card,
                ft.Text("Insights clés", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                ft.Row(spacing=15, controls=insight_cards),
            ]
        )
    
    def _create_corr_legend(self, label: str, color: str) -> ft.Row:
        """Crée un item de légende pour la corrélation."""
        return ft.Row(
            spacing=5,
            controls=[
                ft.Container(width=20, height=20, bgcolor=color, border_radius=4),
                ft.Text(label, size=10, color=Theme.TEXT_MUTED),
            ]
        )
    
    # ========================================================================
    # TAB 4: HEATMAP
    # ========================================================================
    
    def _build_heatmap_tab(self):
        """Construit la heatmap des NC par jour/mois."""
        # Données pour les 12 derniers mois
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        days = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
        
        # Récupérer les données réelles
        heatmap_data = self.db.get_nc_heatmap_data()
        
        # Si pas de données, générer un exemple
        if not heatmap_data:
            import random
            heatmap_data = [[random.randint(0, 8) for _ in range(12)] for _ in range(7)]
        
        # Trouver le max pour normaliser
        max_val = max(max(row) for row in heatmap_data) if heatmap_data else 1
        
        # Créer la heatmap
        heatmap_rows = []
        
        # Header mois
        month_header = [ft.Container(width=50)]
        for month in months:
            month_header.append(
                ft.Container(
                    width=45,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(month, size=10, color=Theme.TEXT_MUTED),
                )
            )
        heatmap_rows.append(ft.Row(controls=month_header))
        
        # Lignes par jour
        for day_idx, day_name in enumerate(days):
            row_cells = [
                ft.Container(
                    width=50,
                    content=ft.Text(day_name, size=11, color=Theme.TEXT_SECONDARY),
                )
            ]
            
            for month_idx in range(12):
                val = heatmap_data[day_idx][month_idx] if day_idx < len(heatmap_data) and month_idx < len(heatmap_data[day_idx]) else 0
                intensity = val / max_val if max_val > 0 else 0
                
                # Gradient de couleur adapté au thème
                if intensity == 0:
                    bg = Theme.BG_TERTIARY
                elif intensity < 0.25:
                    bg = ft.Colors.with_opacity(0.3, Theme.SUCCESS)
                elif intensity < 0.5:
                    bg = ft.Colors.with_opacity(0.5, Theme.SUCCESS)
                elif intensity < 0.75:
                    bg = ft.Colors.with_opacity(0.6, Theme.WARNING)
                else:
                    bg = ft.Colors.with_opacity(0.6, Theme.DANGER)
                
                row_cells.append(
                    ft.Container(
                        width=45,
                        height=30,
                        bgcolor=bg,
                        border_radius=4,
                        alignment=ft.Alignment(0, 0),
                        tooltip=f"{day_name} {months[month_idx]}: {val} NC",
                        content=ft.Text(
                            str(val) if val > 0 else "",
                            size=10,
                            color=ft.Colors.WHITE if intensity > 0.25 else Theme.TEXT_MUTED,
                        ),
                    )
                )
            
            heatmap_rows.append(ft.Row(controls=row_cells, spacing=2))
        
        heatmap_card = ft.Container(
            padding=20,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Column(
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Heatmap NC par jour de la semaine", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                            create_dropdown(
                                "Année",
                                ["2024", "2023", "2022"],
                                value="2024",
                                width=100,
                            ),
                        ]
                    ),
                    ft.Container(height=15),
                    ft.Column(spacing=2, controls=heatmap_rows),
                    ft.Container(height=15),
                    # Légende
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            ft.Text("Moins", size=10, color=Theme.TEXT_MUTED),
                            ft.Container(width=20, height=15, bgcolor=Theme.BG_TERTIARY, border_radius=3),
                            ft.Container(width=20, height=15, bgcolor=ft.Colors.with_opacity(0.3, Theme.SUCCESS), border_radius=3),
                            ft.Container(width=20, height=15, bgcolor=ft.Colors.with_opacity(0.5, Theme.SUCCESS), border_radius=3),
                            ft.Container(width=20, height=15, bgcolor=ft.Colors.with_opacity(0.6, Theme.WARNING), border_radius=3),
                            ft.Container(width=20, height=15, bgcolor=ft.Colors.with_opacity(0.6, Theme.DANGER), border_radius=3),
                            ft.Text("Plus", size=10, color=Theme.TEXT_MUTED),
                        ]
                    ),
                ]
            ),
        )
        
        # Stats complémentaires
        stats_row = ft.Row(
            spacing=15,
            controls=[
                self._create_heatmap_stat("Jour le plus chargé", "Vendredi", "23 NC ce mois"),
                self._create_heatmap_stat("Mois le plus chargé", "Novembre", "45 NC au total"),
                self._create_heatmap_stat("Tendance", "v -12%", "vs mois précédent"),
            ]
        )
        
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[
                heatmap_card,
                stats_row,
            ]
        )
    
    def _create_heatmap_stat(self, title: str, value: str, subtitle: str) -> ft.Container:
        """Crée une stat pour la heatmap."""
        return ft.Container(
            expand=True,
            padding=15,
            border_radius=10,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Column(
                spacing=5,
                controls=[
                    ft.Text(title, size=12, color=Theme.TEXT_MUTED),
                    ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
                    ft.Text(subtitle, size=11, color=Theme.TEXT_SECONDARY),
                ]
            ),
        )

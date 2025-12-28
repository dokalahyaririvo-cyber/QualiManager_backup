# -*- coding: utf-8 -*-
"""
QualiManager ERP QHSE - Module Laboratoire / LIMS
Onglets: Saisie analyses, SPC Control Charts, Historique
"""

import flet as ft
from typing import Dict, Any, Callable, List, Optional
from datetime import datetime
import math

from .theme import Theme
from .components import (
    create_card, create_text_field, create_dropdown, create_button,
    create_status_badge, create_snackbar, create_empty_state
)
from .components_advanced import (
    StatusBadge, SeverityBadge, KPICard, AlertBanner
)


class LabPage(ft.Container):
    """Page principale du module Laboratoire / LIMS."""
    
    def __init__(self, user: Dict, db, navigate: Callable):
        self.user = user
        self.db = db
        self.navigate = navigate
        self.current_tab = 0
        self.current_analysis_id = None
        
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
                                        "🔬 Laboratoire / LIMS",
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                        color=Theme.TEXT_PRIMARY,
                                    ),
                                    ft.Text(
                                        "Saisie analyses, contrôle SPC et traçabilité",
                                        size=13,
                                        color=Theme.TEXT_MUTED,
                                    ),
                                ]
                            ),
                        ]
                    ),
                    create_button(
                        "Nouvelle analyse",
                        icon=ft.Icons.ADD,
                        on_click=lambda e: self._show_new_analysis_dialog(),
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
                ft.Tab(text="📝 Saisie", icon=ft.Icons.EDIT_NOTE),
                ft.Tab(text="📈 SPC", icon=ft.Icons.SHOW_CHART),
                ft.Tab(text="📚 Historique", icon=ft.Icons.HISTORY),
            ],
        )
        
        self.tab_content = ft.Container(
            expand=True,
            padding=20,
            content=self._build_saisie_tab(),
        )
        
        return ft.Column(
            expand=True,
            spacing=0,
            controls=[
                header,
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=20),
                    content=self.tabs,
                ),
                self.tab_content,
            ]
        )
    
    def _on_tab_change(self, e):
        """Change de tab."""
        self.current_tab = e.control.selected_index
        if self.current_tab == 0:
            self.tab_content.content = self._build_saisie_tab()
        elif self.current_tab == 1:
            self.tab_content.content = self._build_spc_tab()
        else:
            self.tab_content.content = self._build_history_tab()
        self.update()
    
    # ========================================================================
    # TAB 1: SAISIE - Nouvelles analyses
    # ========================================================================
    
    def _build_saisie_tab(self):
        """Construit l'onglet Saisie."""
        # Si une analyse est en cours
        if self.current_analysis_id:
            return self._build_active_analysis()
        
        # Analyses en attente
        analyses = self.db.get_analyses_by_status(['En cours', 'En attente'])
        
        if not analyses:
            return create_empty_state(
                ft.Icons.SCIENCE,
                "Aucune analyse en attente",
                "Créez une nouvelle analyse pour commencer",
                "Nouvelle analyse",
                lambda e: self._show_new_analysis_dialog(),
            )
        
        # Liste des analyses en attente
        cards = []
        for analysis in analyses:
            cards.append(self._create_analysis_card(analysis))
        
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text(
                    "Analyses en attente",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=Theme.TEXT_PRIMARY,
                ),
                ft.Container(height=10),
                ft.Row(wrap=True, spacing=15, controls=cards),
            ]
        )
    
    def _build_active_analysis(self):
        """Construit l'interface de saisie pour l'analyse active."""
        analysis = self.db.get_analysis(self.current_analysis_id)
        if not analysis:
            self.current_analysis_id = None
            return self._build_saisie_tab()
        
        # Récupérer le produit et ses paramètres
        produit = self.db.get_lab_produit(analysis.get('produit_id'))
        parametres = self.db.get_parametres_for_produit(analysis.get('produit_id'))
        
        # Résultats existants
        results = self.db.get_analysis_results(self.current_analysis_id)
        results_by_param = {r['parametre_id']: r for r in results}
        
        # Header de l'analyse
        header_card = ft.Container(
            padding=20,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        analysis.get('reference', '-'),
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=Theme.PRIMARY,
                                    ),
                                    StatusBadge(analysis.get('statut', '')),
                                ]
                            ),
                            self._create_conformity_indicator(analysis),
                        ]
                    ),
                    ft.Row(
                        spacing=30,
                        controls=[
                            ft.Row(
                                spacing=5,
                                controls=[
                                    ft.Icon(ft.Icons.INVENTORY_2, size=14, color=Theme.TEXT_MUTED),
                                    ft.Text(f"Produit: {produit.get('nom', '-') if produit else '-'}", size=13, color=Theme.TEXT_SECONDARY),
                                ]
                            ),
                            ft.Row(
                                spacing=5,
                                controls=[
                                    ft.Icon(ft.Icons.NUMBERS, size=14, color=Theme.TEXT_MUTED),
                                    ft.Text(f"Lot: {analysis.get('numero_lot', '-')}", size=13, color=Theme.TEXT_SECONDARY),
                                ]
                            ),
                            ft.Row(
                                spacing=5,
                                controls=[
                                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color=Theme.TEXT_MUTED),
                                    ft.Text(f"Date: {analysis.get('date_prelevement', '-')}", size=13, color=Theme.TEXT_SECONDARY),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
        )
        
        # Formulaire de saisie des résultats
        param_rows = []
        for param in parametres:
            result = results_by_param.get(param['id'], {})
            param_rows.append(self._create_param_input_row(param, result))
        
        # Boutons d'action
        action_buttons = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            spacing=10,
            controls=[
                ft.TextButton(
                    "Annuler",
                    on_click=lambda e: self._cancel_analysis(),
                ),
                create_button(
                    "Enregistrer brouillon",
                    icon=ft.Icons.SAVE,
                    on_click=lambda e: self._save_analysis('En cours'),
                    secondary=True,
                ),
                create_button(
                    "Valider l'analyse",
                    icon=ft.Icons.CHECK,
                    on_click=lambda e: self._save_analysis('Terminée'),
                ),
            ]
        )
        
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=15,
            controls=[
                header_card,
                ft.Text(
                    f"Paramètres à contrôler ({len(parametres)})",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=Theme.TEXT_PRIMARY,
                ),
                # En-tête du tableau
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=15, vertical=10),
                    bgcolor=Theme.BG_TERTIARY,
                    border_radius=ft.border_radius.only(top_left=8, top_right=8),
                    content=ft.Row(
                        controls=[
                            ft.Container(width=180, content=ft.Text("Paramètre", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                            ft.Container(width=100, content=ft.Text("Cible", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                            ft.Container(width=100, content=ft.Text("Min", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                            ft.Container(width=100, content=ft.Text("Max", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                            ft.Container(width=120, content=ft.Text("Valeur mesurée", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                            ft.Container(width=80, content=ft.Text("Unité", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                            ft.Container(width=100, content=ft.Text("Conformité", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                        ]
                    ),
                ),
                ft.Column(spacing=0, controls=param_rows),
                ft.Container(height=15),
                action_buttons,
            ]
        )
    
    def _create_param_input_row(self, param: Dict, result: Dict) -> ft.Container:
        """Crée une ligne de saisie pour un paramètre."""
        param_id = param['id']
        current_value = result.get('valeur_mesuree', '')
        
        # Déterminer la conformité
        conformity = self._check_conformity(
            current_value,
            param.get('valeur_min'),
            param.get('valeur_max'),
        )
        
        # Champ de saisie
        value_field = ft.TextField(
            value=str(current_value) if current_value else '',
            width=100,
            text_size=13,
            dense=True,
            on_change=lambda e, pid=param_id: self._update_result(pid, e.control.value),
        )
        
        # Indicateur de conformité
        conf_indicator = ft.Container(
            width=90,
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=8,
            bgcolor=Theme.SUCCESS if conformity == 'Conforme' else (Theme.DANGER if conformity == 'Non Conforme' else Theme.BG_TERTIARY),
            content=ft.Text(
                conformity,
                size=11,
                color=ft.Colors.WHITE if conformity in ['Conforme', 'Non Conforme'] else Theme.TEXT_MUTED,
            ),
        )
        
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=15, vertical=8),
            bgcolor=Theme.BG_SECONDARY,
            border=ft.border.only(bottom=ft.BorderSide(1, Theme.BG_TERTIARY)),
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=180,
                        content=ft.Text(param.get('nom', '-'), size=13, color=Theme.TEXT_PRIMARY),
                    ),
                    ft.Container(
                        width=100,
                        content=ft.Text(str(param.get('valeur_cible', '-')), size=12, color=Theme.INFO),
                    ),
                    ft.Container(
                        width=100,
                        content=ft.Text(str(param.get('valeur_min', '-')), size=12, color=Theme.TEXT_MUTED),
                    ),
                    ft.Container(
                        width=100,
                        content=ft.Text(str(param.get('valeur_max', '-')), size=12, color=Theme.TEXT_MUTED),
                    ),
                    ft.Container(width=120, content=value_field),
                    ft.Container(
                        width=80,
                        content=ft.Text(param.get('unite', '-'), size=12, color=Theme.TEXT_MUTED),
                    ),
                    conf_indicator,
                ]
            ),
        )
    
    def _check_conformity(self, value, min_val, max_val) -> str:
        """Vérifie la conformité d'une valeur."""
        if value is None or value == '':
            return '-'
        try:
            v = float(value)
            if min_val is not None and v < float(min_val):
                return 'Non Conforme'
            if max_val is not None and v > float(max_val):
                return 'Non Conforme'
            return 'Conforme'
        except (ValueError, TypeError):
            return '-'
    
    def _create_analysis_card(self, analysis: Dict) -> ft.Container:
        """Crée une carte d'analyse."""
        return ft.Container(
            width=280,
            padding=15,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            border=ft.border.all(1, Theme.BG_TERTIARY),
            on_click=lambda e, a=analysis: self._open_analysis(a),
            ink=True,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                analysis.get('reference', '-'),
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.PRIMARY,
                            ),
                            StatusBadge(analysis.get('statut', '')),
                        ]
                    ),
                    ft.Row(
                        spacing=5,
                        controls=[
                            ft.Icon(ft.Icons.INVENTORY_2, size=14, color=Theme.TEXT_MUTED),
                            ft.Text(
                                analysis.get('produit_nom', '-'),
                                size=12,
                                color=Theme.TEXT_SECONDARY,
                            ),
                        ]
                    ),
                    ft.Row(
                        spacing=5,
                        controls=[
                            ft.Icon(ft.Icons.NUMBERS, size=14, color=Theme.TEXT_MUTED),
                            ft.Text(
                                f"Lot: {analysis.get('numero_lot', '-')}",
                                size=12,
                                color=Theme.TEXT_SECONDARY,
                            ),
                        ]
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                analysis.get('date_prelevement', '-'),
                                size=11,
                                color=Theme.TEXT_MUTED,
                            ),
                            self._create_conformity_indicator(analysis, mini=True),
                        ]
                    ),
                ]
            ),
        )
    
    def _create_conformity_indicator(self, analysis: Dict, mini: bool = False) -> ft.Container:
        """Crée un indicateur de conformité global."""
        status = analysis.get('conformite_globale', 'En attente')
        
        colors = {
            'Conforme': Theme.SUCCESS,
            'Non Conforme': Theme.DANGER,
            'En attente': Theme.WARNING,
            'Partiel': Theme.WARNING,
        }
        
        icons = {
            'Conforme': ft.Icons.CHECK_CIRCLE,
            'Non Conforme': ft.Icons.CANCEL,
            'En attente': ft.Icons.PENDING,
            'Partiel': ft.Icons.WARNING,
        }
        
        if mini:
            return ft.Container(
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                border_radius=8,
                bgcolor=colors.get(status, Theme.BG_TERTIARY),
                content=ft.Icon(
                    icons.get(status, ft.Icons.HELP),
                    size=14,
                    color=ft.Colors.WHITE,
                ),
            )
        
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=10,
            bgcolor=colors.get(status, Theme.BG_TERTIARY),
            content=ft.Row(
                spacing=5,
                controls=[
                    ft.Icon(
                        icons.get(status, ft.Icons.HELP),
                        size=16,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Text(
                        status,
                        size=12,
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                ]
            ),
        )
    
    def _show_new_analysis_dialog(self):
        """Dialogue de création d'une nouvelle analyse."""
        produits = self.db.get_all_lab_produits()
        produit_options = [p['nom'] for p in produits]
        
        produit_field = create_dropdown(
            "Produit *",
            produit_options,
            width=300,
        )
        
        lot_field = create_text_field(
            "Numéro de lot *",
            width=200,
        )
        
        date_field = create_text_field(
            "Date prélèvement",
            value=datetime.now().strftime('%Y-%m-%d'),
            width=150,
        )
        
        point_field = create_text_field(
            "Point de prélèvement",
            hint_text="Ex: Ligne 1, Sortie four...",
            width=200,
        )
        
        type_field = create_dropdown(
            "Type d'analyse",
            ["Routine", "Libération", "Investigation", "Validation"],
            value="Routine",
            width=150,
        )
        
        error_text = ft.Text("", color=Theme.DANGER, size=12)
        
        def create_analysis(e):
            if not produit_field.value or not lot_field.value:
                error_text.value = "Produit et numéro de lot sont obligatoires"
                error_text.update()
                return
            
            produit = next((p for p in produits if p['nom'] == produit_field.value), None)
            if not produit:
                error_text.value = "Produit invalide"
                error_text.update()
                return
            
            try:
                analysis_id = self.db.create_lab_analysis({
                    'produit_id': produit['id'],
                    'numero_lot': lot_field.value,
                    'date_prelevement': date_field.value,
                    'point_prelevement': point_field.value,
                    'type_analyse': type_field.value,
                    'analyste_id': self.user['id'],
                    'statut': 'En cours',
                })
                
                self.current_analysis_id = analysis_id
                dialog.open = False
                self.page.update()
                self.tab_content.content = self._build_saisie_tab()
                self.update()
            except Exception as ex:
                error_text.value = f"Erreur: {str(ex)}"
                error_text.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nouvelle analyse"),
            content=ft.Container(
                width=400,
                content=ft.Column(
                    spacing=15,
                    controls=[
                        produit_field,
                        lot_field,
                        ft.Row(controls=[date_field, type_field]),
                        point_field,
                        error_text,
                    ]
                ),
            ),
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: self._close_dialog(dialog)),
                create_button("Créer", on_click=create_analysis),
            ],
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def _open_analysis(self, analysis: Dict):
        """Ouvre une analyse existante."""
        self.current_analysis_id = analysis['id']
        self.tab_content.content = self._build_saisie_tab()
        self.update()
    
    def _update_result(self, param_id: int, value: str):
        """Met à jour un résultat d'analyse."""
        param = self.db.get_lab_parametre(param_id)
        conformity = self._check_conformity(
            value,
            param.get('valeur_min') if param else None,
            param.get('valeur_max') if param else None,
        )
        
        self.db.save_lab_result(
            self.current_analysis_id,
            param_id,
            {
                'valeur_mesuree': float(value) if value else None,
                'conforme': 1 if conformity == 'Conforme' else (0 if conformity == 'Non Conforme' else None),
            }
        )
    
    def _save_analysis(self, status: str):
        """Enregistre l'analyse avec le statut donné."""
        # Mettre à jour la conformité globale
        results = self.db.get_analysis_results(self.current_analysis_id)
        non_conformes = sum(1 for r in results if r.get('conforme') == 0)
        total = sum(1 for r in results if r.get('conforme') is not None)
        
        if total == 0:
            conformite = 'En attente'
        elif non_conformes == 0:
            conformite = 'Conforme'
        else:
            conformite = 'Non Conforme'
        
        self.db.update_lab_analysis(self.current_analysis_id, {
            'statut': status,
            'conformite_globale': conformite,
        })
        
        if status == 'Terminée':
            self.current_analysis_id = None
        
        self.tab_content.content = self._build_saisie_tab()
        self.update()
    
    def _cancel_analysis(self):
        """Annule la saisie en cours."""
        self.current_analysis_id = None
        self.tab_content.content = self._build_saisie_tab()
        self.update()
    
    # ========================================================================
    # TAB 2: SPC - Cartes de contrôle
    # ========================================================================
    
    def _build_spc_tab(self):
        """Construit l'onglet SPC avec cartes de contrôle."""
        produits = self.db.get_all_lab_produits()
        
        if not produits:
            return create_empty_state(
                ft.Icons.SHOW_CHART,
                "Pas de données SPC",
                "Configurez vos produits et paramètres d'abord",
            )
        
        # Sélecteur de produit et paramètre
        produit_options = [p['nom'] for p in produits]
        
        self.spc_produit = create_dropdown(
            "Produit",
            produit_options,
            value=produit_options[0] if produit_options else None,
            on_change=lambda e: self._update_spc_params(e),
            width=250,
        )
        
        self.spc_param = create_dropdown(
            "Paramètre",
            [],
            width=250,
        )
        
        self.spc_period = create_dropdown(
            "Période",
            ["7 derniers jours", "30 derniers jours", "90 derniers jours", "Cette année"],
            value="30 derniers jours",
            width=180,
        )
        
        # Charger les paramètres du premier produit
        if produit_options:
            first_produit = produits[0]
            params = self.db.get_parametres_for_produit(first_produit['id'])
            self.spc_param.options = [ft.dropdown.Option(p['nom']) for p in params]
            if params:
                self.spc_param.value = params[0]['nom']
        
        # Bouton pour générer le graphique
        generate_btn = create_button(
            "Générer",
            icon=ft.Icons.AUTO_GRAPH,
            on_click=lambda e: self._generate_spc_chart(),
        )
        
        # Zone du graphique
        self.spc_chart_container = ft.Container(
            expand=True,
            padding=20,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.SHOW_CHART, size=48, color=Theme.TEXT_MUTED),
                    ft.Text(
                        "Sélectionnez un produit et un paramètre puis cliquez sur 'Générer'",
                        size=14,
                        color=Theme.TEXT_MUTED,
                    ),
                ]
            ),
        )
        
        return ft.Column(
            expand=True,
            spacing=15,
            controls=[
                # Filtres
                ft.Row(
                    spacing=15,
                    controls=[
                        self.spc_produit,
                        self.spc_param,
                        self.spc_period,
                        generate_btn,
                    ]
                ),
                # Graphique
                self.spc_chart_container,
            ]
        )
    
    def _update_spc_params(self, e):
        """Met à jour la liste des paramètres selon le produit."""
        produits = self.db.get_all_lab_produits()
        produit = next((p for p in produits if p['nom'] == e.control.value), None)
        if produit:
            params = self.db.get_parametres_for_produit(produit['id'])
            self.spc_param.options = [ft.dropdown.Option(p['nom']) for p in params]
            self.spc_param.value = params[0]['nom'] if params else None
            self.spc_param.update()
    
    def _generate_spc_chart(self):
        """Génère la carte de contrôle SPC."""
        produit_nom = self.spc_produit.value
        param_nom = self.spc_param.value
        
        if not produit_nom or not param_nom:
            return
        
        # Récupérer les données
        produits = self.db.get_all_lab_produits()
        produit = next((p for p in produits if p['nom'] == produit_nom), None)
        if not produit:
            return
        
        params = self.db.get_parametres_for_produit(produit['id'])
        param = next((p for p in params if p['nom'] == param_nom), None)
        if not param:
            return
        
        # Récupérer les données SPC
        spc_data = self.db.get_spc_data(param['id'])
        
        if not spc_data or len(spc_data) < 2:
            self.spc_chart_container.content = ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.INFO, size=48, color=Theme.WARNING),
                    ft.Text(
                        "Pas assez de données pour générer le graphique SPC",
                        size=14,
                        color=Theme.TEXT_MUTED,
                    ),
                ]
            )
            self.spc_chart_container.update()
            return
        
        # Calculer les limites de contrôle
        values = [d['valeur_mesuree'] for d in spc_data if d['valeur_mesuree'] is not None]
        mean = sum(values) / len(values)
        std_dev = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
        
        ucl = mean + 3 * std_dev  # Upper Control Limit
        lcl = mean - 3 * std_dev  # Lower Control Limit
        usl = param.get('valeur_max', ucl)  # Upper Spec Limit
        lsl = param.get('valeur_min', lcl)  # Lower Spec Limit
        target = param.get('valeur_cible', mean)
        
        # Créer le graphique
        chart = self._create_spc_chart(spc_data, mean, ucl, lcl, usl, lsl, target, param)
        
        # Stats
        stats_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[
                self._create_stat_chip("Moyenne", f"{mean:.2f}", Theme.INFO),
                self._create_stat_chip("Écart-type", f"{std_dev:.2f}", Theme.WARNING),
                self._create_stat_chip("UCL", f"{ucl:.2f}", Theme.DANGER),
                self._create_stat_chip("LCL", f"{lcl:.2f}", Theme.DANGER),
                self._create_stat_chip("Cible", f"{target:.2f}", Theme.SUCCESS),
            ]
        )
        
        self.spc_chart_container.content = ft.Column(
            spacing=15,
            controls=[
                ft.Text(
                    f"Carte de contrôle - {param_nom}",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=Theme.TEXT_PRIMARY,
                ),
                chart,
                stats_row,
            ]
        )
        self.spc_chart_container.update()
    
    def _create_spc_chart(self, data: List[Dict], mean: float, ucl: float, lcl: float, 
                          usl: float, lsl: float, target: float, param: Dict) -> ft.Container:
        """Crée un graphique SPC simple (représentation visuelle)."""
        # Normaliser les valeurs pour l'affichage
        values = [d['valeur_mesuree'] for d in data if d['valeur_mesuree'] is not None]
        max_val = max(max(values), ucl, usl)
        min_val = min(min(values), lcl, lsl)
        range_val = max_val - min_val if max_val != min_val else 1
        
        chart_height = 200
        chart_width = 700
        
        def normalize(v):
            return chart_height - ((v - min_val) / range_val * chart_height)
        
        # Points de données
        data_points = []
        point_width = chart_width / len(values)
        
        for i, v in enumerate(values):
            y = normalize(v)
            is_out = v > ucl or v < lcl
            data_points.append(
                ft.Container(
                    left=i * point_width + point_width/2 - 5,
                    top=y - 5,
                    width=10,
                    height=10,
                    border_radius=5,
                    bgcolor=Theme.DANGER if is_out else Theme.PRIMARY,
                    tooltip=f"Valeur: {v:.2f}",
                )
            )
        
        # Lignes de limite (représentées comme des containers horizontaux)
        def create_limit_line(value: float, color: str, label: str, dashed: bool = False):
            y = normalize(value)
            return ft.Container(
                left=0,
                top=y,
                width=chart_width,
                height=2 if not dashed else 1,
                bgcolor=color,
                border=ft.border.all(1, color) if dashed else None,
                tooltip=f"{label}: {value:.2f}",
            )
        
        # Zone de graphique
        chart_area = ft.Stack(
            width=chart_width,
            height=chart_height,
            controls=[
                # Fond
                ft.Container(
                    width=chart_width,
                    height=chart_height,
                    bgcolor=Theme.BG_PRIMARY,
                    border_radius=8,
                ),
                # Lignes de limites
                create_limit_line(ucl, Theme.DANGER, "UCL"),
                create_limit_line(lcl, Theme.DANGER, "LCL"),
                create_limit_line(mean, Theme.INFO, "Moyenne"),
                create_limit_line(target, Theme.SUCCESS, "Cible"),
                # Points
                *data_points,
            ]
        )
        
        # Légende
        legend = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
            controls=[
                self._create_legend_item("UCL/LCL", Theme.DANGER),
                self._create_legend_item("Moyenne", Theme.INFO),
                self._create_legend_item("Cible", Theme.SUCCESS),
                self._create_legend_item("Valeur", Theme.PRIMARY),
                self._create_legend_item("Hors limite", Theme.DANGER, is_point=True),
            ]
        )
        
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    padding=10,
                    content=ft.Row(
                        scroll=ft.ScrollMode.AUTO,
                        controls=[chart_area],
                    ),
                ),
                legend,
            ]
        )
    
    def _create_stat_chip(self, label: str, value: str, color: str) -> ft.Container:
        """Crée un chip de statistique."""
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border_radius=8,
            bgcolor=Theme.BG_TERTIARY,
            content=ft.Column(
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(label, size=11, color=Theme.TEXT_MUTED),
                    ft.Text(value, size=14, weight=ft.FontWeight.BOLD, color=color),
                ]
            ),
        )
    
    def _create_legend_item(self, label: str, color: str, is_point: bool = False) -> ft.Row:
        """Crée un item de légende."""
        if is_point:
            indicator = ft.Container(
                width=10,
                height=10,
                border_radius=5,
                bgcolor=color,
            )
        else:
            indicator = ft.Container(
                width=20,
                height=3,
                bgcolor=color,
            )
        
        return ft.Row(
            spacing=5,
            controls=[
                indicator,
                ft.Text(label, size=11, color=Theme.TEXT_MUTED),
            ]
        )
    
    # ========================================================================
    # TAB 3: HISTORIQUE
    # ========================================================================
    
    def _build_history_tab(self):
        """Construit l'onglet Historique."""
        analyses = self.db.get_all_lab_analyses()
        
        if not analyses:
            return create_empty_state(
                ft.Icons.HISTORY,
                "Aucun historique",
                "Les analyses terminées apparaîtront ici",
            )
        
        # Filtres
        filters = ft.Row(
            spacing=10,
            controls=[
                create_dropdown(
                    "Produit",
                    ["Tous"] + list(set(a.get('produit_nom', '') for a in analyses if a.get('produit_nom'))),
                    value="Tous",
                    width=180,
                ),
                create_dropdown(
                    "Conformité",
                    ["Tous", "Conforme", "Non Conforme", "En attente"],
                    value="Tous",
                    width=150,
                ),
                create_text_field(
                    "N° Lot...",
                    prefix_icon=ft.Icons.SEARCH,
                    width=200,
                ),
            ]
        )
        
        # Tableau
        rows = []
        for analysis in analyses:
            conf = analysis.get('conformite_globale', '-')
            conf_color = Theme.SUCCESS if conf == 'Conforme' else (Theme.DANGER if conf == 'Non Conforme' else Theme.WARNING)
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(analysis.get('reference', '-'), size=12, color=Theme.PRIMARY)),
                        ft.DataCell(ft.Text(analysis.get('produit_nom', '-'), size=12, color=Theme.TEXT_PRIMARY)),
                        ft.DataCell(ft.Text(analysis.get('numero_lot', '-'), size=12, color=Theme.TEXT_SECONDARY)),
                        ft.DataCell(ft.Text(analysis.get('type_analyse', '-'), size=12, color=Theme.TEXT_SECONDARY)),
                        ft.DataCell(ft.Text(analysis.get('date_prelevement', '-'), size=12, color=Theme.TEXT_MUTED)),
                        ft.DataCell(
                            ft.Container(
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=8,
                                bgcolor=conf_color,
                                content=ft.Text(conf, size=11, color=ft.Colors.WHITE),
                            )
                        ),
                        ft.DataCell(StatusBadge(analysis.get('statut', ''))),
                        ft.DataCell(
                            ft.IconButton(
                                ft.Icons.VISIBILITY,
                                icon_size=16,
                                icon_color=Theme.TEXT_MUTED,
                                tooltip="Voir détail",
                                on_click=lambda e, a=analysis: self._open_analysis(a),
                            )
                        ),
                    ]
                )
            )
        
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Référence", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                ft.DataColumn(ft.Text("Produit", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                ft.DataColumn(ft.Text("Lot", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                ft.DataColumn(ft.Text("Type", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                ft.DataColumn(ft.Text("Date", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                ft.DataColumn(ft.Text("Conformité", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                ft.DataColumn(ft.Text("Statut", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                ft.DataColumn(ft.Text("Actions", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY, no_wrap=True)),
            ],
            rows=rows,
            border=ft.border.all(1, Theme.BG_TERTIARY),
            border_radius=8,
            column_spacing=15,
            heading_row_color=Theme.BG_TERTIARY,
        )
        
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                filters,
                ft.Container(height=15),
                ft.Row(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[table],
                ),
            ]
        )
    
    # ========================================================================
    # HELPERS
    # ========================================================================
    
    def _close_dialog(self, dialog):
        """Ferme un dialogue."""
        dialog.open = False
        self.page.update()

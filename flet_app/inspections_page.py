# -*- coding: utf-8 -*-
"""
QualiManager ERP QHSE - Module Inspections Terrain
Onglets: Checklist (saisie), Historique, Scoring
"""

import flet as ft
from typing import Dict, Any, Callable, List
from datetime import datetime

from .theme import Theme
from .components import (
    create_card, create_text_field, create_dropdown, create_button,
    create_status_badge, create_snackbar, create_empty_state
)
from .components_advanced import (
    StatusBadge, SeverityBadge, KPICard, ScoringIndicator, AlertBanner
)


class InspectionsPage(ft.Container):
    """Page principale du module Inspections Terrain."""
    
    def __init__(self, user: Dict, db, navigate: Callable):
        self.user = user
        self.db = db
        self.navigate = navigate
        self.current_tab = 0
        self.current_inspection_id = None
        
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
                                        "🔍 Inspections Terrain",
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                        color=Theme.TEXT_PRIMARY,
                                    ),
                                    ft.Text(
                                        "Checklists dynamiques et scoring automatique",
                                        size=13,
                                        color=Theme.TEXT_MUTED,
                                    ),
                                ]
                            ),
                        ]
                    ),
                    create_button(
                        "Nouvelle inspection",
                        icon=ft.Icons.ADD,
                        on_click=lambda e: self._show_new_inspection_dialog(),
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
                ft.Tab(text="📋 Checklist", icon=ft.Icons.CHECKLIST),
                ft.Tab(text="📚 Historique", icon=ft.Icons.HISTORY),
                ft.Tab(text="🎯 Scoring", icon=ft.Icons.ANALYTICS),
            ],
        )
        
        self.tab_content = ft.Container(
            expand=True,
            padding=20,
            content=self._build_checklist_tab(),
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
            self.tab_content.content = self._build_checklist_tab()
        elif self.current_tab == 1:
            self.tab_content.content = self._build_history_tab()
        else:
            self.tab_content.content = self._build_scoring_tab()
        self.update()
    
    # ========================================================================
    # TAB 1: CHECKLIST - Saisie d'inspection
    # ========================================================================
    
    def _build_checklist_tab(self):
        """Construit l'onglet Checklist."""
        # Si une inspection est en cours
        if self.current_inspection_id:
            return self._build_active_checklist()
        
        # Sinon, afficher les inspections en cours/brouillon
        inspections = self.db.get_inspections_by_status(['Brouillon', 'En cours'])
        
        if not inspections:
            return create_empty_state(
                ft.Icons.CHECKLIST,
                "Aucune inspection en cours",
                "Démarrez une nouvelle inspection terrain",
                "Nouvelle inspection",
                lambda e: self._show_new_inspection_dialog(),
            )
        
        # Liste des inspections en cours
        cards = []
        for insp in inspections:
            cards.append(self._create_inspection_card(insp))
        
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text(
                    "Inspections en cours",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=Theme.TEXT_PRIMARY,
                ),
                ft.Container(height=10),
                ft.Row(wrap=True, spacing=15, controls=cards),
            ]
        )
    
    def _build_active_checklist(self):
        """Construit la checklist active pour l'inspection en cours."""
        inspection = self.db.get_inspection(self.current_inspection_id)
        if not inspection:
            self.current_inspection_id = None
            return self._build_checklist_tab()
        
        # Récupérer les points de contrôle pour cette zone
        zone_id = inspection.get('zone_id')
        points_controle = self.db.get_points_controle_for_zone(zone_id)
        
        # Récupérer les réponses existantes
        details = self.db.get_inspection_details(self.current_inspection_id)
        details_by_point = {d['point_controle_id']: d for d in details}
        
        # Header de l'inspection
        header_card = ft.Container(
            padding=20,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=5,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        inspection.get('reference', '-'),
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=Theme.PRIMARY,
                                    ),
                                    StatusBadge(inspection.get('statut', '')),
                                ]
                            ),
                            ft.Text(
                                f"Atelier: {inspection.get('atelier_nom', '-')} | Zone: {inspection.get('zone_nom', '-')}",
                                size=14,
                                color=Theme.TEXT_SECONDARY,
                            ),
                            ft.Text(
                                f"Type: {inspection.get('type_inspection', '-')} | Date: {inspection.get('date_inspection', '-')}",
                                size=12,
                                color=Theme.TEXT_MUTED,
                            ),
                        ]
                    ),
                    ScoringIndicator(
                        score=inspection.get('score_global', 0),
                        label="Score global",
                    ),
                ]
            ),
        )
        
        # Liste des points de contrôle
        checklist_items = []
        for idx, point in enumerate(points_controle, 1):
            detail = details_by_point.get(point['id'], {})
            checklist_items.append(
                self._create_checklist_item(point, detail, idx)
            )
        
        # Boutons d'action
        action_buttons = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            spacing=10,
            controls=[
                ft.TextButton(
                    "Annuler",
                    on_click=lambda e: self._cancel_inspection(),
                ),
                create_button(
                    "Enregistrer brouillon",
                    icon=ft.Icons.SAVE,
                    on_click=lambda e: self._save_inspection('Brouillon'),
                    secondary=True,
                ),
                create_button(
                    "Valider l'inspection",
                    icon=ft.Icons.CHECK,
                    on_click=lambda e: self._save_inspection('Terminée'),
                ),
            ]
        )
        
        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=15,
            controls=[
                # Header
                header_card,
                # Checklist
                ft.Text(
                    f"Points de contrôle ({len(points_controle)})",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=Theme.TEXT_PRIMARY,
                ),
                ft.Column(spacing=10, controls=checklist_items),
                ft.Container(height=10),
                action_buttons,
            ]
        )
    
    def _create_checklist_item(self, point: Dict, detail: Dict, index: int) -> ft.Container:
        """Crée un item de checklist."""
        point_id = point['id']
        libelle = point.get('libelle', '')
        ponderation = point.get('ponderation', 1)
        current_result = detail.get('resultat', '')
        current_note = detail.get('note', '')
        
        # Radios pour Conforme/Non Conforme/NA
        result_group = ft.RadioGroup(
            value=current_result,
            on_change=lambda e, pid=point_id: self._update_point_result(pid, e.control.value),
            content=ft.Row(
                spacing=15,
                controls=[
                    ft.Radio(
                        value="Conforme",
                        label="✅ Conforme",
                        fill_color={ft.ControlState.SELECTED: Theme.SUCCESS},
                    ),
                    ft.Radio(
                        value="Non Conforme",
                        label="❌ Non Conforme",
                        fill_color={ft.ControlState.SELECTED: Theme.DANGER},
                    ),
                    ft.Radio(
                        value="NA",
                        label="N/A",
                        fill_color={ft.ControlState.SELECTED: Theme.TEXT_MUTED},
                    ),
                ]
            ),
        )
        
        # Champ de commentaire
        note_field = create_text_field(
            "Commentaire / Observation",
            value=current_note,
            on_change=lambda e, pid=point_id: self._update_point_note(pid, e.control.value),
            width=350,
        )
        
        # Couleur de fond selon le résultat - adaptée au thème
        bg_color = Theme.BG_SECONDARY
        if current_result == 'Conforme':
            bg_color = ft.Colors.with_opacity(0.15, Theme.SUCCESS) if Theme.is_dark() else ft.Colors.with_opacity(0.08, Theme.SUCCESS)
        elif current_result == 'Non Conforme':
            bg_color = ft.Colors.with_opacity(0.15, Theme.DANGER) if Theme.is_dark() else ft.Colors.with_opacity(0.08, Theme.DANGER)
        
        return ft.Container(
            padding=15,
            border_radius=10,
            bgcolor=bg_color,
            border=ft.border.all(1, Theme.BG_TERTIARY),
            content=ft.Column(
                spacing=10,
                controls=[
                    # Header du point
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        width=30,
                                        height=30,
                                        border_radius=15,
                                        bgcolor=Theme.PRIMARY,
                                        alignment=ft.alignment.center,
                                        content=ft.Text(
                                            str(index),
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.WHITE,
                                        ),
                                    ),
                                    ft.Text(
                                        libelle,
                                        size=14,
                                        color=Theme.TEXT_PRIMARY,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ],
                            ),
                            ft.Container(
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=8,
                                bgcolor=Theme.BG_TERTIARY,
                                content=ft.Text(
                                    f"Pond. {ponderation}",
                                    size=11,
                                    color=Theme.TEXT_MUTED,
                                ),
                            ),
                        ]
                    ),
                    # Résultat et note
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            result_group,
                            note_field,
                        ]
                    ),
                ]
            ),
        )
    
    def _create_inspection_card(self, insp: Dict) -> ft.Container:
        """Crée une carte d'inspection."""
        return ft.Container(
            width=280,
            padding=15,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            border=ft.border.all(1, Theme.BG_TERTIARY),
            on_click=lambda e, i=insp: self._open_inspection(i),
            ink=True,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                insp.get('reference', '-'),
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.PRIMARY,
                            ),
                            StatusBadge(insp.get('statut', '')),
                        ]
                    ),
                    ft.Text(
                        f"Type: {insp.get('type_inspection', '-')}",
                        size=12,
                        color=Theme.TEXT_SECONDARY,
                    ),
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.FACTORY, size=14, color=Theme.TEXT_MUTED),
                            ft.Text(
                                insp.get('atelier_nom', '-'),
                                size=12,
                                color=Theme.TEXT_SECONDARY,
                            ),
                        ]
                    ),
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.LOCATION_ON, size=14, color=Theme.TEXT_MUTED),
                            ft.Text(
                                insp.get('zone_nom', '-'),
                                size=12,
                                color=Theme.TEXT_SECONDARY,
                            ),
                        ]
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                insp.get('date_inspection', '-'),
                                size=11,
                                color=Theme.TEXT_MUTED,
                            ),
                            ScoringIndicator(
                                score=insp.get('score_global', 0),
                                mini=True,
                            ),
                        ]
                    ),
                ]
            ),
        )
    
    def _show_new_inspection_dialog(self):
        """Dialogue de création d'une nouvelle inspection."""
        # Récupérer ateliers et zones
        ateliers = self.db.get_all_ateliers()
        atelier_options = [a['nom'] for a in ateliers]
        
        zones = []
        zone_options = []
        
        atelier_field = create_dropdown(
            "Atelier *",
            atelier_options,
            on_change=lambda e: self._update_zones_dropdown(e, zones_field, ateliers),
            width=250,
        )
        
        zones_field = create_dropdown(
            "Zone *",
            zone_options,
            width=250,
        )
        
        type_field = create_dropdown(
            "Type d'inspection *",
            ["Audit interne", "Inspection hygiène", "5S", "Sécurité", "Environnement", "HACCP"],
            width=250,
        )
        
        date_field = create_text_field(
            "Date",
            value=datetime.now().strftime('%Y-%m-%d'),
            width=150,
        )
        
        planifie_field = create_dropdown(
            "Type",
            ["Planifiée", "Inopinée"],
            value="Planifiée",
            width=150,
        )
        
        error_text = ft.Text("", color=Theme.DANGER, size=12)
        
        def create_inspection(e):
            if not atelier_field.value or not zones_field.value or not type_field.value:
                error_text.value = "Veuillez remplir tous les champs obligatoires"
                error_text.update()
                return
            
            # Trouver les IDs
            atelier = next((a for a in ateliers if a['nom'] == atelier_field.value), None)
            zone = next((z for z in zones if z['nom'] == zones_field.value), None)
            
            if not atelier or not zone:
                error_text.value = "Atelier ou zone invalide"
                error_text.update()
                return
            
            try:
                inspection_id = self.db.create_inspection({
                    'type_inspection': type_field.value,
                    'atelier_id': atelier['id'],
                    'zone_id': zone['id'],
                    'date_inspection': date_field.value,
                    'planifie': planifie_field.value == 'Planifiée',
                    'inspecteur_id': self.user['id'],
                    'statut': 'En cours',
                })
                
                self.current_inspection_id = inspection_id
                dialog.open = False
                self.page.update()
                self.tab_content.content = self._build_checklist_tab()
                self.update()
            except Exception as ex:
                error_text.value = f"Erreur: {str(ex)}"
                error_text.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nouvelle inspection"),
            content=ft.Container(
                width=400,
                content=ft.Column(
                    spacing=15,
                    controls=[
                        atelier_field,
                        zones_field,
                        type_field,
                        ft.Row(controls=[date_field, planifie_field]),
                        error_text,
                    ]
                ),
            ),
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: self._close_dialog(dialog)),
                create_button("Démarrer", on_click=create_inspection),
            ],
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def _update_zones_dropdown(self, e, zones_field, ateliers):
        """Met à jour le dropdown des zones selon l'atelier sélectionné."""
        atelier = next((a for a in ateliers if a['nom'] == e.control.value), None)
        if atelier:
            zones = self.db.get_zones_for_atelier(atelier['id'])
            zones_field.options = [ft.dropdown.Option(z['nom']) for z in zones]
            zones_field.value = None
            zones_field.update()
    
    def _open_inspection(self, insp: Dict):
        """Ouvre une inspection existante."""
        self.current_inspection_id = insp['id']
        self.tab_content.content = self._build_checklist_tab()
        self.update()
    
    def _update_point_result(self, point_id: int, result: str):
        """Met à jour le résultat d'un point de contrôle."""
        self.db.save_inspection_detail(
            self.current_inspection_id,
            point_id,
            {'resultat': result}
        )
        self._recalculate_score()
    
    def _update_point_note(self, point_id: int, note: str):
        """Met à jour la note d'un point de contrôle."""
        self.db.save_inspection_detail(
            self.current_inspection_id,
            point_id,
            {'note': note}
        )
    
    def _recalculate_score(self):
        """Recalcule le score global de l'inspection."""
        self.db.update_inspection_score(self.current_inspection_id)
        # Rafraîchir l'affichage
        self.tab_content.content = self._build_checklist_tab()
        self.update()
    
    def _save_inspection(self, status: str):
        """Enregistre l'inspection avec le statut donné."""
        self.db.update_inspection_status(self.current_inspection_id, status)
        if status == 'Terminée':
            self.current_inspection_id = None
        self.tab_content.content = self._build_checklist_tab()
        self.update()
    
    def _cancel_inspection(self):
        """Annule l'inspection en cours."""
        self.current_inspection_id = None
        self.tab_content.content = self._build_checklist_tab()
        self.update()
    
    # ========================================================================
    # TAB 2: HISTORIQUE
    # ========================================================================
    
    def _build_history_tab(self):
        """Construit l'onglet Historique."""
        inspections = self.db.get_all_inspections()
        
        if not inspections:
            return create_empty_state(
                ft.Icons.HISTORY,
                "Aucun historique",
                "Les inspections terminées apparaîtront ici",
            )
        
        # Filtres
        filters = ft.Row(
            spacing=10,
            controls=[
                create_dropdown(
                    "Type",
                    ["Tous", "Audit interne", "Inspection hygiène", "5S", "Sécurité", "Environnement", "HACCP"],
                    value="Tous",
                    width=180,
                ),
                create_dropdown(
                    "Atelier",
                    ["Tous"] + list(set(i.get('atelier_nom', '') for i in inspections)),
                    value="Tous",
                    width=150,
                ),
                create_dropdown(
                    "Période",
                    ["Tout", "Ce mois", "Ce trimestre", "Cette année"],
                    value="Tout",
                    width=150,
                ),
                create_text_field(
                    "Rechercher...",
                    prefix_icon=ft.Icons.SEARCH,
                    width=200,
                ),
            ]
        )
        
        # Tableau d'historique
        rows = []
        for insp in inspections:
            score = insp.get('score_global', 0)
            score_color = Theme.SUCCESS if score >= 80 else (Theme.WARNING if score >= 60 else Theme.DANGER)
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(insp.get('reference', '-'), size=12, color=Theme.PRIMARY)),
                        ft.DataCell(ft.Text(insp.get('type_inspection', '-'), size=12, color=Theme.TEXT_PRIMARY)),
                        ft.DataCell(ft.Text(insp.get('atelier_nom', '-'), size=12, color=Theme.TEXT_SECONDARY)),
                        ft.DataCell(ft.Text(insp.get('zone_nom', '-'), size=12, color=Theme.TEXT_SECONDARY)),
                        ft.DataCell(ft.Text(insp.get('date_inspection', '-'), size=12, color=Theme.TEXT_MUTED)),
                        ft.DataCell(
                            ft.Container(
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=8,
                                bgcolor=score_color,
                                content=ft.Text(f"{score}%", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            )
                        ),
                        ft.DataCell(StatusBadge(insp.get('statut', ''))),
                        ft.DataCell(
                            ft.IconButton(
                                ft.Icons.VISIBILITY,
                                icon_size=16,
                                icon_color=Theme.TEXT_MUTED,
                                tooltip="Voir détail",
                                on_click=lambda e, i=insp: self._show_inspection_detail(i),
                            )
                        ),
                    ]
                )
            )
        
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Référence", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                ft.DataColumn(ft.Text("Type", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                ft.DataColumn(ft.Text("Atelier", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                ft.DataColumn(ft.Text("Zone", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                ft.DataColumn(ft.Text("Date", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
                ft.DataColumn(ft.Text("Score", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)),
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
    
    def _show_inspection_detail(self, insp: Dict):
        """Affiche le détail d'une inspection."""
        # Pour l'instant, on ouvre l'inspection dans la checklist
        self.current_inspection_id = insp['id']
        self.tabs.selected_index = 0
        self.current_tab = 0
        self.tab_content.content = self._build_checklist_tab()
        self.update()
    
    # ========================================================================
    # TAB 3: SCORING
    # ========================================================================
    
    def _build_scoring_tab(self):
        """Construit l'onglet Scoring avec statistiques."""
        inspections = self.db.get_all_inspections()
        
        # Calcul des statistiques
        total = len(inspections)
        if total == 0:
            return create_empty_state(
                ft.Icons.ANALYTICS,
                "Pas de données",
                "Les statistiques apparaîtront après vos premières inspections",
            )
        
        scores = [i.get('score_global', 0) for i in inspections if i.get('score_global')]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        by_type = {}
        by_atelier = {}
        for insp in inspections:
            t = insp.get('type_inspection', 'Autre')
            a = insp.get('atelier_nom', 'Autre')
            
            if t not in by_type:
                by_type[t] = {'count': 0, 'scores': []}
            by_type[t]['count'] += 1
            if insp.get('score_global'):
                by_type[t]['scores'].append(insp['score_global'])
            
            if a not in by_atelier:
                by_atelier[a] = {'count': 0, 'scores': []}
            by_atelier[a]['count'] += 1
            if insp.get('score_global'):
                by_atelier[a]['scores'].append(insp['score_global'])
        
        # KPI Cards
        kpi_row = ft.Row(
            spacing=15,
            controls=[
                KPICard(
                    title="Total inspections",
                    value=str(total),
                    icon=ft.Icons.CHECKLIST,
                    color=Theme.PRIMARY,
                ),
                KPICard(
                    title="Score moyen",
                    value=f"{avg_score:.0f}%",
                    icon=ft.Icons.SCORE,
                    color=Theme.SUCCESS if avg_score >= 80 else (Theme.WARNING if avg_score >= 60 else Theme.DANGER),
                ),
                KPICard(
                    title="Ce mois",
                    value=str(sum(1 for i in inspections if i.get('date_inspection', '').startswith(datetime.now().strftime('%Y-%m')))),
                    icon=ft.Icons.CALENDAR_TODAY,
                    color=Theme.INFO,
                ),
            ]
        )
        
        # Graphique par type
        type_bars = []
        for type_name, data in by_type.items():
            avg = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
            bar_color = Theme.SUCCESS if avg >= 80 else (Theme.WARNING if avg >= 60 else Theme.DANGER)
            type_bars.append(
                ft.Container(
                    padding=10,
                    border_radius=8,
                    bgcolor=Theme.BG_SECONDARY,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(type_name, size=13, color=Theme.TEXT_PRIMARY),
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Text(f"{data['count']} insp.", size=12, color=Theme.TEXT_MUTED),
                                    ScoringIndicator(score=avg, mini=True),
                                ]
                            ),
                        ]
                    ),
                )
            )
        
        # Graphique par atelier
        atelier_bars = []
        for atelier_name, data in by_atelier.items():
            avg = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
            atelier_bars.append(
                ft.Container(
                    padding=10,
                    border_radius=8,
                    bgcolor=Theme.BG_SECONDARY,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(atelier_name, size=13, color=Theme.TEXT_PRIMARY),
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Text(f"{data['count']} insp.", size=12, color=Theme.TEXT_MUTED),
                                    ScoringIndicator(score=avg, mini=True),
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
                kpi_row,
                ft.Row(
                    spacing=20,
                    crossAxisAlignment=ft.CrossAxisAlignment.START,
                    controls=[
                        # Par type
                        ft.Container(
                            expand=True,
                            padding=20,
                            border_radius=12,
                            bgcolor=Theme.BG_SECONDARY,
                            content=ft.Column(
                                controls=[
                                    ft.Text("Scores par type", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                                    ft.Container(height=10),
                                    *type_bars,
                                ]
                            ),
                        ),
                        # Par atelier
                        ft.Container(
                            expand=True,
                            padding=20,
                            border_radius=12,
                            bgcolor=Theme.BG_SECONDARY,
                            content=ft.Column(
                                controls=[
                                    ft.Text("Scores par atelier", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                                    ft.Container(height=10),
                                    *atelier_bars,
                                ]
                            ),
                        ),
                    ]
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

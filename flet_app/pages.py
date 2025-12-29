# -*- coding: utf-8 -*-
"""
QualiManager - Pages de l'application (refonte NC & utilisateurs)
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, Callable, List

import flet as ft

from .theme import Theme, Styles
from .components import (
    create_card, create_stat_card, create_action_card,
    create_text_field, create_dropdown, create_button,
    create_status_badge, create_severity_badge, create_snackbar,
    create_empty_state
)

# Listes de référence
TYPE_NC_CHOICES = ["Interne", "Client", "Fournisseur", "Prestataire", "Audit"]
ANOMALY_CHOICES = [
    "Habillage", "Commande", "Casse occulte", "Erreur validation", "Erreur procédé",
    "Erreur préparation", "Casse", "Conditionnement", "Marquage", "Matériel",
    "Réglementaire", "Livraison", "Facturation", "Documentation", "Environnement",
    "Corps étranger", "Quantité"
]
IMPUTATION_CHOICES = [
    "Expédition", "Dégorgement", "QSE", "Cuverie", "Tirage", "Fournisseur",
    "Transport", "Indéterminée", "Ordonnancement", "Espaces ventes",
    "Prestataire", "Habillage", "WLS", "Caves"
]
M5_CHOICES = ["Matériel", "Matière première", "Méthode", "Milieu", "Management", "Moyen", "Main d'oeuvre"]


class LoginPage(ft.View):
    def __init__(self, on_login: Callable, db):
        self.on_login = on_login
        self.db = db
        self.email_field = create_text_field(label="Email", prefix_icon=ft.Icons.EMAIL, on_change=self._clear_error)
        self.password_field = create_text_field(label="Mot de passe", prefix_icon=ft.Icons.LOCK, password=True, on_change=self._clear_error)
        self.error_text = ft.Text("", color=Theme.DANGER, size=12)
        super().__init__(
            route="/login",
            bgcolor=Theme.BG_PRIMARY,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[self._build_ui()],
        )

    def _build_ui(self):
        return ft.Container(
            width=450,
            padding=40,
            border_radius=Styles.RADIUS_XL,
            bgcolor=Theme.BG_SECONDARY,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=30, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK)),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.VERIFIED_USER, size=60, color=Theme.PRIMARY),
                    ft.Text("QualiManager", size=28, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    ft.Text("Système de Gestion Qualité", size=14, color=Theme.TEXT_MUTED),
                    ft.Divider(height=30, color="transparent"),
                    self.email_field,
                    self.password_field,
                    self.error_text,
                    ft.Container(height=15),
                    create_button("Se connecter", icon=ft.Icons.LOGIN, width=300, on_click=self._handle_login),
                    ft.Text("admin@qualimanager.local / Admin@2024!", size=11, color=Theme.TEXT_MUTED, italic=True),
                ],
            ),
        )

    def _clear_error(self, e):
        self.error_text.value = ""
        self.error_text.update()

    def _handle_login(self, e):
        user = self.db.authenticate(self.email_field.value, self.password_field.value)
        if user:
            self.on_login(user)
        else:
            self.error_text.value = "Email ou mot de passe incorrect"
            self.error_text.update()


class HomePage(ft.View):
    def __init__(self, user: Dict, db, navigate: Callable, on_logout: Callable):
        self.user = user
        self.db = db
        self.navigate = navigate
        self.on_logout = on_logout
        super().__init__(route="/home", bgcolor=Theme.BG_PRIMARY, padding=0, controls=[self._build_ui()])

    def _build_sidebar(self):
        module_items = [
            (ft.Icons.WARNING_AMBER, "Non-Conformités", "/nc"),
            (ft.Icons.SEARCH, "Fiche NC", "/nc-fiche"),
        ]
        admin_items = [
            (ft.Icons.PEOPLE, "Utilisateurs", "/users"),
            (ft.Icons.SETTINGS, "Paramètres", "/settings"),
        ]
        controls = [ft.Row(controls=[ft.Icon(ft.Icons.VERIFIED_USER, color=Theme.PRIMARY, size=32), ft.Text("QualiManager", size=20, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)]), ft.Divider(height=20, color=Theme.BG_TERTIARY)]
        for icon, text, route in module_items:
            controls.append(self._menu_item(icon, text, route))
        if self.user['role'] == 'Administrateur':
            controls.append(ft.Text("ADMIN", size=11, color=Theme.TEXT_MUTED, weight=ft.FontWeight.BOLD))
            for icon, text, route in admin_items:
                controls.append(self._menu_item(icon, text, route))
        controls.append(ft.Container(expand=True))
        controls.append(ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
            ft.Row(controls=[ft.CircleAvatar(content=ft.Text(self.user['nom'][0].upper()), bgcolor=Theme.PRIMARY, radius=18), ft.Column(spacing=0, controls=[ft.Text(self.user['nom'], color=Theme.TEXT_PRIMARY), ft.Text(self.user['role'], size=12, color=Theme.TEXT_MUTED)])]),
            ft.IconButton(ft.Icons.LOGOUT, icon_color=Theme.TEXT_MUTED, tooltip="Déconnexion", on_click=lambda e: self.on_logout()),
        ]))
        return ft.Container(width=260, bgcolor=Theme.BG_SECONDARY, padding=20, content=ft.Column(controls=controls))

    def _menu_item(self, icon, text, route):
        return ft.Container(
            padding=ft.Padding(left=10, right=10, top=12, bottom=12),
            border_radius=Styles.RADIUS_MD,
            ink=True,
            on_click=lambda e, r=route: self.navigate(r),
            content=ft.Row(controls=[ft.Icon(icon, color=Theme.TEXT_MUTED, size=20), ft.Text(text, color=Theme.TEXT_SECONDARY)])
        )

    def _build_main_content(self):
        stats = self.db.get_stats()
        
        def stat_card(icon, title, value, color):
            return ft.Container(
                width=200,
                height=120,
                padding=15,
                border_radius=12,
                bgcolor=Theme.BG_SECONDARY,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Row(controls=[
                            ft.Icon(icon, color=color, size=24),
                        ]),
                        ft.Text(str(value), size=28, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                        ft.Text(title, size=12, color=Theme.TEXT_MUTED),
                    ],
                ),
            )
        
        return ft.Container(expand=True, padding=30, content=ft.Column(scroll=ft.ScrollMode.AUTO, controls=[
            ft.Text(f"Bonjour, {self.user['nom']} ", size=26, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
            ft.Text(datetime.now().strftime("%A %d %B %Y"), size=14, color=Theme.TEXT_MUTED),
            ft.Container(height=20),
            ft.Text("Vue d'ensemble", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
            ft.Container(height=10),
            ft.Row(spacing=15, controls=[
                stat_card(ft.Icons.WARNING, "NC Ouvertes", stats.get('open', 0), Theme.DANGER),
                stat_card(ft.Icons.PENDING, "En cours", stats.get('in_progress', 0), Theme.WARNING),
                stat_card(ft.Icons.CHECK_CIRCLE, "Clôturées", stats.get('resolved', 0), Theme.SUCCESS),
                stat_card(ft.Icons.SCHEDULE, "Délai moyen", f"{stats.get('avg_resolution_days', 0)} j", Theme.INFO),
            ]),
            ft.Container(height=25),
            ft.Text("Actions rapides", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
            ft.Container(height=10),
            ft.Row(spacing=12, controls=[
                create_action_card(ft.Icons.ADD_ALERT, "Nouvelle NC", Theme.DANGER, lambda e: self.navigate("/nc/new")),
                create_action_card(ft.Icons.SEARCH, "Fiche NC", Theme.SECONDARY, lambda e: self.navigate("/nc-fiche")),
            ]),
        ]))

    def _build_ui(self):
        return ft.Row(expand=True, controls=[self._build_sidebar(), self._build_main_content()])


class NCListPage(ft.View):
    def __init__(self, user: Dict, db, navigate: Callable):
        self.user = user
        self.db = db
        self.navigate = navigate
        self.filters = {}
        self.table_container = None
        self.search_field = create_text_field(label="Rechercher", prefix_icon=ft.Icons.SEARCH, on_change=self._on_search, width=250)
        super().__init__(route="/nc", bgcolor=Theme.BG_PRIMARY, padding=0, scroll=ft.ScrollMode.HIDDEN, controls=[self._build_ui()])

    def _build_ui(self):
        self.table_container = self._build_table()
        return ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Container(
                    padding=20,
                    content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                        ft.Row(controls=[ft.IconButton(ft.Icons.ARROW_BACK, icon_color=Theme.TEXT_MUTED, on_click=lambda e: self.navigate("/home")), ft.Column(spacing=0, controls=[ft.Text("[ID] Non-Conformités", size=22, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY), ft.Text("Liste principale", size=13, color=Theme.TEXT_MUTED)])]),
                        create_button("Nouvelle NC", icon=ft.Icons.ADD, on_click=lambda e: self.navigate("/nc/new")),
                    ])
                ),
                ft.Container(
                    padding=ft.Padding(left=20, right=20, top=0, bottom=10),
                    content=create_card(content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                        ft.Row(controls=[self.search_field]),
                        ft.IconButton(ft.Icons.REFRESH, icon_color=Theme.PRIMARY, tooltip="Actualiser", on_click=self._refresh),
                    ]), padding=12)
                ),
                ft.Container(
                    expand=True,
                    padding=ft.Padding(left=20, right=20, top=0, bottom=20),
                    content=self.table_container
                ),
            ]
        )

    def _build_table(self):
        ncs = self.db.get_all_nc(self.filters)
        if not ncs:
            return create_card(content=create_empty_state(ft.Icons.SEARCH_OFF, "Aucune NC", "Aucune donnée"), expand=True)
        
        def wrap_text(text, max_chars=100):
            """Découpe le texte en lignes de max_chars caractères max"""
            if not text or text == '-':
                return text
            words = text.split()
            lines = []
            current_line = ""
            for word in words:
                if len(current_line) + len(word) + 1 <= max_chars:
                    current_line = current_line + " " + word if current_line else word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            return "\n".join(lines)
        
        # Configuration des colonnes: (nom, largeur fixe ou None pour expand, clé données)
        columns_config = [
            ("No NC", 60, "reference"),
            ("Date", 85, "date_detection"),
            ("Type", 70, "type_nc"),
            ("Origine", 95, "origine"),
            ("Anomalie", 115, "type_anomalie"),
            ("Produit", 95, "produit_concerne"),
            ("Lot", 70, "lot_serie"),
            ("Qte", 45, "quantite_affectee"),
            ("Détail", None, "description"),  # expand=True, min 180px
            ("Cause Racine", None, "cause_racine"),  # expand=True, min 180px
            ("Catégorie", 85, "categorie_nc"),
            ("Imputation", 95, "imputation"),
            ("Gravité", 75, None),
            ("Statut", 85, None),
            ("Actions", 50, None),
        ]
        
        MIN_EXPAND_WIDTH = 180  # ~30 caractères minimum
        
        # Construire l'en-tête
        header_cells = []
        for i, (col_name, width, _) in enumerate(columns_config):
            is_last = i == len(columns_config) - 1
            if width is not None:
                header_cells.append(
                    ft.Container(
                        width=width,
                        padding=ft.Padding(left=6, right=6, top=12, bottom=12),
                        border=ft.Border(right=ft.BorderSide(1, Theme.BG_PRIMARY)) if not is_last else None,
                        content=ft.Text(
                            col_name,
                            color=Theme.TEXT_MUTED,
                            weight=ft.FontWeight.BOLD,
                            size=11,
                            no_wrap=col_name == "Actions",
                        ),
                    )
                )
            else:
                # Colonnes expand (Détail et Cause Racine)
                header_cells.append(
                    ft.Container(
                        expand=True,
                        padding=ft.Padding(left=6, right=6, top=12, bottom=12),
                        border=ft.Border(right=ft.BorderSide(1, Theme.BG_PRIMARY)) if not is_last else None,
                        content=ft.Text(col_name, color=Theme.TEXT_MUTED, weight=ft.FontWeight.BOLD, size=11),
                    )
                )
        
        header_row = ft.Container(
            bgcolor=Theme.BG_TERTIARY,
            border_radius=ft.BorderRadius(8, 8, 0, 0),
            content=ft.Row(controls=header_cells, spacing=0),
        )
        
        # Construire les lignes de données
        data_rows = []
        for nc in ncs:
            nc_id = nc['id']
            
            row_cells = []
            for i, (col_name, width, data_key) in enumerate(columns_config):
                is_last = i == len(columns_config) - 1
                
                # Déterminer le contenu de la cellule
                if col_name == "Gravité":
                    cell_content = create_severity_badge(nc.get('gravite', ''))
                elif col_name == "Statut":
                    cell_content = create_status_badge(nc.get('statut', ''))
                elif col_name == "Actions":
                    cell_content = ft.IconButton(
                        ft.Icons.EDIT, 
                        icon_color=Theme.WARNING, 
                        icon_size=16, 
                        tooltip="Modifier", 
                        on_click=lambda e, id=nc_id: self.navigate(f"/nc/{id}/edit")
                    )
                elif col_name == "No NC":
                    cell_content = ft.Text(
                        nc.get(data_key, '-') or '-', 
                        color=Theme.TEXT_PRIMARY, 
                        weight=ft.FontWeight.W_500, 
                        size=11,
                        no_wrap=True,
                    )
                elif col_name in ("Détail", "Cause Racine"):
                    # Ces colonnes peuvent contenir jusqu'à 100 caractères sur une ligne
                    text = nc.get(data_key, '-') or '-'
                    cell_content = ft.Text(wrap_text(text, 100), color=Theme.TEXT_SECONDARY, size=11)
                elif col_name in ("Origine", "Produit", "Catégorie"):
                    text = nc.get(data_key, '-') or '-'
                    cell_content = ft.Text(wrap_text(text, 18), color=Theme.TEXT_SECONDARY, size=11)
                elif col_name == "Qte":
                    cell_content = ft.Text(
                        str(nc.get(data_key) or '-'), 
                        color=Theme.TEXT_SECONDARY, 
                        size=11,
                        no_wrap=True,
                    )
                else:
                    cell_content = ft.Text(
                        nc.get(data_key, '-') or '-', 
                        color=Theme.TEXT_SECONDARY, 
                        size=11,
                        no_wrap=True,
                    )
                
                # Créer la cellule
                if width is not None:
                    row_cells.append(
                        ft.Container(
                            width=width,
                            padding=ft.Padding(left=6, right=6, top=10, bottom=10),
                            border=ft.Border(right=ft.BorderSide(1, Theme.BG_TERTIARY)) if not is_last else None,
                            content=cell_content,
                        )
                    )
                else:
                    # Cellules expand (Détail et Cause Racine)
                    row_cells.append(
                        ft.Container(
                            expand=True,
                            padding=ft.Padding(left=6, right=6, top=10, bottom=10),
                            border=ft.Border(right=ft.BorderSide(1, Theme.BG_TERTIARY)) if not is_last else None,
                            content=cell_content,
                        )
                    )
            
            data_rows.append(
                ft.Container(
                    border=ft.Border(bottom=ft.BorderSide(1, Theme.BG_TERTIARY)),
                    content=ft.Row(controls=row_cells, spacing=0),
                    on_click=lambda e, id=nc_id: self.navigate(f"/nc/{id}/edit"),
                    ink=True,
                )
            )
        
        # Conteneur du tableau - scroll vertical uniquement
        table_column = ft.Column(
            controls=[header_row] + data_rows,
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        
        return ft.Container(
            content=table_column,
            border_radius=8,
            bgcolor=Theme.BG_SECONDARY,
            expand=True,
        )

    def _on_search(self, e):
        self.filters['search'] = e.control.value
        self._refresh(e)

    def _refresh(self, e=None):
        self.table_container = self._build_table()
        self.controls[0].controls[2].content = self.table_container
        self.update()


class NCFormPage(ft.View):
    def __init__(self, user: Dict, db, navigate: Callable, nc_id: int = None):
        self.user = user
        self.db = db
        self.navigate = navigate
        self.nc_id = nc_id
        self.nc_data = db.get_nc(nc_id) if nc_id else {}
        self.attachments: List[Dict[str, Any]] = []
        self.selected_5m: List[str] = []
        self.immediate_rows: List[Dict[str, ft.TextField]] = []
        self.corrective_rows: List[Dict[str, ft.Control]] = []
        self._picker_registered = False
        self._sections_cache = None
        self._init_fields()
        super().__init__(route="/nc/new" if not nc_id else f"/nc/{nc_id}/edit", bgcolor=Theme.BG_PRIMARY, padding=0, scroll=ft.ScrollMode.HIDDEN, controls=[])
        self.controls.append(self._build_ui())

    def _init_fields(self):
        # Section A
        self.ref_field = create_text_field("Référence", prefix_icon=ft.Icons.TAG)
        self.ref_field.value = self.nc_data.get('reference', '')
        self.date_field = create_text_field("Date de détection", prefix_icon=ft.Icons.CALENDAR_TODAY, read_only=True)
        self.date_field.value = self.nc_data.get('date_detection', datetime.now().strftime("%Y-%m-%d"))
        self.date_picker = ft.DatePicker(on_change=self._on_date_change)
        self.type_dropdown = create_dropdown("Type de NC", TYPE_NC_CHOICES, value=self.nc_data.get('type_nc'))
        self.severity_dropdown = create_dropdown("Gravité", ["Mineure", "Majeure", "Critique"], value=self.nc_data.get('gravite'))
        self.origin_field = create_text_field("Origine", prefix_icon=ft.Icons.TRAVEL_EXPLORE)
        self.origin_field.value = self.nc_data.get('origine', '')
        self.anomaly_dropdown = create_dropdown("Type d'anomalie", ANOMALY_CHOICES, value=self.nc_data.get('type_anomalie'))
        self.category_field = create_text_field("Catégorie de la NC")
        self.category_field.value = self.nc_data.get('categorie_nc', '')
        self.imputation_dropdown = create_dropdown("Imputation", IMPUTATION_CHOICES, value=self.nc_data.get('imputation'))
        self.description_field = create_text_field("Description du problème", multiline=True, min_lines=3)
        self.description_field.value = self.nc_data.get('description', '')
        self.product_field = create_text_field("Produit concerné")
        self.product_field.value = self.nc_data.get('produit_concerne', '')
        self.lot_field = create_text_field("Lot / Série")
        self.lot_field.value = self.nc_data.get('lot_serie', '')
        self.qty_field = create_text_field("Quantité affectée")
        self.qty_field.value = str(self.nc_data.get('quantite_affectee', '') or '')
        self.location_field = create_text_field("Lieu de détection")
        self.location_field.value = self.nc_data.get('lieu_detection', '')

        # Attachments
        try:
            existing_pj = json.loads(self.nc_data.get('pieces_jointes', '[]') or '[]')
            if isinstance(existing_pj, list):
                self.attachments = existing_pj
        except Exception:
            self.attachments = []
        self.file_picker = ft.FilePicker(on_result=self._on_files_chosen)

        # Section B
        # Choix méthodologies (multi-sélection)
        saved_method = self.nc_data.get('methode_analyse') or ''
        use_5why = '5' in saved_method or saved_method.lower().startswith('5') or saved_method == ''
        use_ishikawa = 'ishi' in saved_method.lower() or 'm' in saved_method.lower()
        self.method_5why = ft.Checkbox(label="5 Pourquoi", value=use_5why, on_change=self._on_method_toggle)
        self.method_ishikawa = ft.Checkbox(label="Ishikawa (5M)", value=use_ishikawa, on_change=self._on_method_toggle)

        self.root_cause_field = create_text_field("Cause racine", multiline=True, min_lines=2)
        self.root_cause_field.value = self.nc_data.get('cause_racine', '')
        try:
            saved_5m = json.loads(self.nc_data.get('analyse_5m', '[]') or '[]')
            if isinstance(saved_5m, list):
                self.selected_5m = saved_5m
        except Exception:
            self.selected_5m = []
        self.portee_field = create_text_field("Portée de la NC", multiline=True, min_lines=2)
        self.portee_field.value = self.nc_data.get('analyse_portee', '')

        # Analyse détaillée (5Why / Ishikawa)
        try:
            self.analysis_details = json.loads(self.nc_data.get('analyse_details', '{}') or '{}')
            if not isinstance(self.analysis_details, dict):
                self.analysis_details = {}
        except Exception:
            self.analysis_details = {}

        fivewhy_data = self.analysis_details.get('5why', {}) if isinstance(self.analysis_details.get('5why', {}), dict) else {}
        fivewhy_whys = fivewhy_data.get('whys', []) if isinstance(fivewhy_data, dict) else []
        self.fivewhy_fields = []
        for i in range(5):
            placeholder = "Parce que..."
            self.fivewhy_fields.append(create_text_field(f"Pourquoi {i+1}?", value=fivewhy_whys[i] if i < len(fivewhy_whys) else "", multiline=True, min_lines=1, hint_text=placeholder))

        # Ishikawa categories dynamiques
        ishikawa_data = self.analysis_details.get('ishikawa', {}) if isinstance(self.analysis_details.get('ishikawa', {}), dict) else {}
        default_cats = [
            "Main d'oeuvre",
            "Matériel",
            "Matière",
            "Méthode",
            "Milieu",
            "Mesure",
        ]
        categories_data = ishikawa_data.get('categories', {}) if isinstance(ishikawa_data.get('categories', {}), dict) else {}
        self.ishikawa_categories = {}
        self.selected_ishikawa_cats = set(categories_data.keys()) if categories_data else set()
        for cat in default_cats:
            values = categories_data.get(cat, []) if isinstance(categories_data, dict) else []
            if values:
                self.selected_ishikawa_cats.add(cat)
            fields = [create_text_field(f"{cat} - cause {idx+1}", value=values[idx] if idx < len(values) else "", multiline=True, min_lines=1, hint_text="Cause...") for idx in range(max(1, len(values)))]
            self.ishikawa_categories[cat] = fields
        if not self.selected_ishikawa_cats and self.method_ishikawa.value:
            # activer une catégorie par défaut
            self.selected_ishikawa_cats.add(default_cats[0])
        self.ishikawa_synth_field = create_text_field("Synthèse Ishikawa", multiline=True, min_lines=2, value=ishikawa_data.get('synthesis', ""))

        # Section C - actions immédiates (dynamiques)
        try:
            immediate_data = json.loads(self.nc_data.get('actions_immediates_table', '[]') or '[]')
            if not isinstance(immediate_data, list):
                immediate_data = []
        except Exception:
            immediate_data = []
        if not immediate_data:
            immediate_data = [{}]
        self.immediate_rows = [self._build_immediate_row(row_data) for row_data in immediate_data]

        # Section C - actions correctives dynamiques
        try:
            corrective_data = json.loads(self.nc_data.get('actions_correctives_table', '[]') or '[]')
            if not isinstance(corrective_data, list):
                corrective_data = []
        except Exception:
            corrective_data = []
        if not corrective_data:
            corrective_data = [{}]
        self.corrective_rows = []
        for row_data in corrective_data:
            self.corrective_rows.append(self._build_corrective_row(row_data))

        # Section D
        self.status_dropdown = create_dropdown("Statut", ["En cours", "Clôturée"], value=self.nc_data.get('statut', 'En cours'))
        self.closure_date_field = create_text_field("Date de clôture", prefix_icon=ft.Icons.EVENT_AVAILABLE, read_only=True)
        self.closure_date_field.value = self.nc_data.get('date_cloture', '')
        self.closure_date_picker = ft.DatePicker(on_change=self._on_closure_date_change)
        self.verifier_field = create_text_field("Vérificateur")
        self.verifier_field.value = ''
        self.efficacy_dropdown = create_dropdown("Efficacité des actions", ["Non évaluée", "Efficace", "Partiellement efficace", "Non efficace"], value=self.nc_data.get('efficacite', 'Non évaluée'))
        self.closure_comments_field = create_text_field("Commentaires de clôture", multiline=True, min_lines=2, value=self.nc_data.get('commentaires_cloture', ''))

    def _register_overlays(self):
        """Attach pickers to the page overlay once available."""
        if self._picker_registered:
            return
        try:
            page = self.page
            if not page:
                return
            if self.date_picker not in page.overlay:
                page.overlay.append(self.date_picker)
            if self.closure_date_picker not in page.overlay:
                page.overlay.append(self.closure_date_picker)
            if self.file_picker not in page.overlay:
                page.overlay.append(self.file_picker)
            self._picker_registered = True
            page.update()
        except (AttributeError, Exception):
            pass

    def did_mount(self):
        # Enregistre les pickers une fois la page attachée
        self._register_overlays()

    def _open_date_picker(self, e=None):
        if self.page:
            if self.date_picker not in self.page.overlay:
                self.page.overlay.append(self.date_picker)
                self.page.update()
            self.date_picker.open = True
            self.page.update()

    def _open_file_picker(self, e=None):
        self._register_overlays()
        if self.page and self.file_picker in self.page.overlay:
            self.file_picker.pick_files(allow_multiple=True)

    def _on_date_change(self, e):
        try:
            self.page.close(self.date_picker)
        except:
            self.date_picker.open = False
            self.page.update()
        if e.data != "dismissed" and e.control.value:
            self.date_field.value = e.control.value.strftime("%Y-%m-%d")
            self.date_field.update()

    def _on_closure_date_change(self, e):
        try:
            self.page.close(self.closure_date_picker)
        except:
            self.closure_date_picker.open = False
            self.page.update()
        if e.data != "dismissed" and e.control.value:
            self.closure_date_field.value = e.control.value.strftime("%Y-%m-%d")
            self.closure_date_field.update()

    def _open_closure_date_picker(self, e=None):
        if self.page:
            if self.closure_date_picker not in self.page.overlay:
                self.page.overlay.append(self.closure_date_picker)
                self.page.update()
            self.closure_date_picker.open = True
            self.page.update()

    def _open_action_date_picker(self, field, e=None):
        """Ouvre un DatePicker temporaire pour un champ de date d'action."""
        temp_picker = None
        
        def on_change(ev):
            try:
                self.page.close(temp_picker)
            except:
                temp_picker.open = False
                self.page.update()
            if ev.data != "dismissed" and ev.control.value:
                field.value = ev.control.value.strftime("%Y-%m-%d")
                field.update()
        
        temp_picker = ft.DatePicker(on_change=on_change)
        self.page.overlay.append(temp_picker)
        self.page.update()
        temp_picker.open = True
        self.page.update()

    def _on_files_chosen(self, e: ft.FilePickerResultEvent):
        if e.files:
            for f in e.files:
                self.attachments.append({"name": f.name, "path": f.path, "size": f.size})
            self._refresh_attachments()

    def _refresh_attachments(self):
        self.attachments_container.content = self._render_attachments()
        try:
            page = self.attachments_container.page
        except AttributeError:
            page = None
        if page:
            self.attachments_container.update()

    def _remove_attachment(self, name):
        self.attachments = [a for a in self.attachments if a['name'] != name]
        self._refresh_attachments()

    def _open_file(self, file_path):
        """Ouvre un fichier avec l'application par défaut du système"""
        if not file_path:
            create_snackbar(self.page, "[Attention] Fichier introuvable", "error")
            return
        try:
            import os
            import subprocess
            import platform
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
            create_snackbar(self.page, f"[OK] Ouverture de {os.path.basename(file_path)}", "success")
        except Exception as ex:
            create_snackbar(self.page, f"[ERROR] Erreur: {str(ex)}", "error")

    def _render_attachments(self):
        chips = [
            ft.Row(
                spacing=4,
                controls=[
                    ft.Chip(
                        label=ft.Text(a['name'], size=12),
                        leading=ft.Icon(ft.Icons.ATTACH_FILE, size=16),
                        on_click=lambda e, path=a.get('path'): self._open_file(path) if path else None,
                        delete_icon=ft.Icon(ft.Icons.CLOSE, size=14),
                        on_delete=lambda e, name=a['name']: self._remove_attachment(name)
                    )
                ]
            ) for a in self.attachments
        ]
        return ft.Column(spacing=6, controls=chips) if chips else ft.Text("Aucune pièce jointe")

    def _build_corrective_row(self, row_data=None):
        row_data = row_data or {}
        date_debut_field = create_text_field("Date de début", value=row_data.get('date_debut', ''), read_only=True, hint_text="Calendrier")
        date_fin_field = create_text_field("Date de fin", value=row_data.get('date_fin', ''), read_only=True, hint_text="Calendrier")
        return {
            'desc': create_text_field("Action corrective", value=row_data.get('desc', '')),
            'responsable': create_text_field("Responsable", value=row_data.get('responsable', '')),
            'date_debut': date_debut_field,
            'date_debut_picker_btn': ft.IconButton(ft.Icons.CALENDAR_MONTH, icon_color=Theme.PRIMARY, icon_size=20, tooltip="Choisir une date", on_click=lambda e, f=date_debut_field: self._open_action_date_picker(f, e)),
            'cost': create_text_field("Coût (EUR)", value=row_data.get('cost', '')),
            'verification': create_dropdown("Vérification de l'efficacité", ["Non évaluée", "Efficace", "Partiellement efficace", "Non efficace"], value=row_data.get('verification')),
            'statut': create_dropdown("Statut", ["En cours", "Clôturée"], value=row_data.get('statut', 'En cours')),
            'date_fin': date_fin_field,
            'date_fin_picker_btn': ft.IconButton(ft.Icons.CALENDAR_MONTH, icon_color=Theme.PRIMARY, icon_size=20, tooltip="Choisir une date", on_click=lambda e, f=date_fin_field: self._open_action_date_picker(f, e)),
        }

    def _build_ui(self):
        self.attachments_container = ft.Container(content=self._render_attachments())
        self.tabs = ft.Tabs(
            selected_index=0,
            on_change=self._on_tab_change,
            expand=False,
            tabs=[
                ft.Tab(text="A. Identification", icon=ft.Icons.INFO),
                ft.Tab(text="B. Analyse", icon=ft.Icons.ANALYTICS),
                ft.Tab(text="C. Actions", icon=ft.Icons.BUILD),
                ft.Tab(text="D. Clôture", icon=ft.Icons.CHECK_CIRCLE),
            ]
        )
        self.current_tab_index = 0
        self.content_container = ft.Container(expand=True, content=self._build_section_a())
        
        # Boutons de navigation entre onglets - TOUJOURS VISIBLES POUR TEST
        self.prev_button = ft.ElevatedButton(
            text="< Précédent",
            icon=ft.Icons.ARROW_BACK,
            on_click=self._go_prev_tab,
            bgcolor=Theme.PRIMARY,
            color=ft.Colors.WHITE,
        )
        self.next_button = ft.ElevatedButton(
            text="Suivant >",
            icon=ft.Icons.ARROW_FORWARD,
            on_click=self._go_next_tab,
            bgcolor=Theme.SUCCESS,
            color=ft.Colors.WHITE,
        )
        
        print(f"[OK] BOUTONS CREES: prev_button={self.prev_button}, next_button={self.next_button}")
        
        # Retourner un conteneur qui remplit l'écran
        content = ft.Column(
            expand=True,
            spacing=10,
            controls=[
                ft.Row(controls=[ft.IconButton(ft.Icons.ARROW_BACK, icon_color=Theme.TEXT_MUTED, on_click=lambda e: self.navigate("/nc")), ft.Text("[Note] Nouvelle NC" if not self.nc_id else f"[Note] Modifier {self.nc_data.get('reference', '')}", size=22, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)]),
                self.tabs,
                self.content_container,
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            controls=[self.prev_button, self.next_button],
                            spacing=10,
                        ),
                        ft.Row(controls=[create_button("Annuler", style="secondary", on_click=lambda e: self.navigate("/nc")), create_button("Enregistrer", icon=ft.Icons.SAVE, style="success", on_click=self._save)]),
                    ]
                ),
            ]
        )
        return ft.Container(expand=True, padding=20, content=content)

    def _on_tab_change(self, e):
        sections = [self._build_section_a, self._build_section_b, self._build_section_c, self._build_section_d]
        self.current_tab_index = e.control.selected_index
        self.content_container.content = sections[self.current_tab_index]()
        self._update_nav_buttons()
        self.content_container.update()
    
    def _go_prev_tab(self, e):
        """Aller à l'onglet précédent."""
        if self.current_tab_index > 0:
            self.current_tab_index -= 1
            self.tabs.selected_index = self.current_tab_index
            sections = [self._build_section_a, self._build_section_b, self._build_section_c, self._build_section_d]
            self.content_container.content = sections[self.current_tab_index]()
            self._update_nav_buttons()
            self.tabs.update()
            self.content_container.update()
    
    def _go_next_tab(self, e):
        """Aller à l'onglet suivant."""
        if self.current_tab_index < 3:
            self.current_tab_index += 1
            self.tabs.selected_index = self.current_tab_index
            sections = [self._build_section_a, self._build_section_b, self._build_section_c, self._build_section_d]
            self.content_container.content = sections[self.current_tab_index]()
            self._update_nav_buttons()
            self.tabs.update()
            self.content_container.update()
    
    def _update_nav_buttons(self):
        """Met à jour la visibilité des boutons de navigation."""
        self.prev_button.visible = self.current_tab_index > 0
        self.next_button.visible = self.current_tab_index < 3
        try:
            self.prev_button.update()
            self.next_button.update()
        except:
            pass  # Pas encore attaché à la page

    def _on_method_toggle(self, e=None):
        if self.current_tab_index == 1:
            self.content_container.content = self._build_section_b()
            self.content_container.update()

    def _build_section_a(self):
        return create_card(content=ft.Column(spacing=10, controls=[
            ft.Text("Identification", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
            ft.Row(controls=[ft.Container(expand=1, content=self.ref_field), ft.Container(expand=1, content=ft.Row(controls=[self.date_field, ft.IconButton(ft.Icons.DATE_RANGE, tooltip="Choisir une date", on_click=self._open_date_picker)]))]),
            ft.Row(controls=[ft.Container(expand=1, content=self.type_dropdown), ft.Container(expand=1, content=self.severity_dropdown), ft.Container(expand=1, content=self.imputation_dropdown)]),
            ft.Row(controls=[ft.Container(expand=1, content=self.origin_field), ft.Container(expand=1, content=self.anomaly_dropdown)]),
            ft.Row(controls=[ft.Container(expand=1, content=self.category_field), ft.Container(expand=1, content=self.location_field)]),
            self.description_field,
            ft.Row(controls=[ft.Container(expand=1, content=self.product_field), ft.Container(expand=1, content=self.lot_field), ft.Container(expand=1, content=self.qty_field)]),
            ft.Text("Pièces jointes", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
            ft.Row(controls=[create_button("Ajouter des fichiers", icon=ft.Icons.ATTACH_FILE, style="secondary", on_click=self._open_file_picker), self.attachments_container]),
        ]))

    def _build_section_b(self):
        body = self._render_analysis_body()
        return create_card(content=ft.Column(spacing=10, controls=[
            ft.Text("Analyse", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
            ft.Text("Méthodologies", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
            ft.Row(spacing=20, controls=[self.method_5why, self.method_ishikawa]),
            self.root_cause_field,
            body,
            self.portee_field,
        ]))

    def _render_analysis_body(self):
        sections = []
        if self.method_5why.value:
            sections.append(create_card(content=ft.Column(spacing=8, controls=[ft.Text("5 Pourquoi", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)] + self.fivewhy_fields), padding=10, bgcolor=Theme.BG_TERTIARY))
        if self.method_ishikawa.value:
            sections.append(self._render_ishikawa())
        if not sections:
            return ft.Text("Sélectionnez au moins une méthodologie", color=Theme.TEXT_MUTED)
        return ft.Column(spacing=12, controls=sections)

    def _render_ishikawa(self):
        # Sélection des axes 5M
        cat_checks = []
        for cat in self.ishikawa_categories.keys():
            cat_checks.append(ft.Checkbox(label=cat, value=cat in self.selected_ishikawa_cats, on_change=lambda e, c=cat: self._toggle_ishikawa_cat(c, e.control.value)))

        # Blocs causes pour les catégories actives
        rows = []
        active = [c for c in self.ishikawa_categories.keys() if c in self.selected_ishikawa_cats]
        if not active:
            return ft.Column(spacing=8, controls=[ft.Text("Ishikawa", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY), ft.Text("Choisir au moins un axe 5M", color=Theme.TEXT_MUTED), ft.Row(wrap=True, spacing=10, controls=cat_checks)])

        for cat in active:
            fields = self.ishikawa_categories[cat]
            add_btn = create_button("Ajouter une cause", icon=ft.Icons.ADD, style="secondary", on_click=lambda e, c=cat: self._add_ishikawa_cause(c))
            card = create_card(content=ft.Column(spacing=6, controls=[ft.Text(cat, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)] + fields + [add_btn]), padding=10, bgcolor=Theme.BG_TERTIARY, expand=True)
            rows.append(card)

        return ft.Column(spacing=10, controls=[ft.Text("Ishikawa (5M)", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY), ft.Row(wrap=True, spacing=10, controls=cat_checks)] + rows + [self.ishikawa_synth_field])

    def _toggle_ishikawa_cat(self, cat, selected):
        if selected:
            self.selected_ishikawa_cats.add(cat)
        else:
            self.selected_ishikawa_cats.discard(cat)
        if self.current_tab_index == 1:
            self.content_container.content = self._build_section_b()
            self.content_container.update()

    def _add_ishikawa_cause(self, cat):
        fields = self.ishikawa_categories.get(cat, [])
        fields.append(create_text_field(f"{cat} - cause {len(fields)+1}", multiline=True, min_lines=1, hint_text="Cause..."))
        self.ishikawa_categories[cat] = fields
        if self.current_tab_index == 1:
            self.content_container.content = self._build_section_b()
            self.content_container.update()

    def _build_immediate_table(self):
        rows = []
        for idx, row in enumerate(self.immediate_rows, start=1):
            rows.append(create_card(content=ft.Row(spacing=8, controls=[
                ft.Text(f"{idx}.", color=Theme.TEXT_MUTED, width=20), 
                ft.Container(expand=3, content=row['correction']), 
                ft.Container(expand=2, content=row['responsable']), 
                ft.Container(expand=1, content=ft.Row(spacing=0, controls=[row['date'], row['date_picker_btn']])), 
                ft.Container(expand=1, content=row['cost'])
            ]), padding=12, bgcolor=Theme.BG_TERTIARY))
        add_btn = create_button("Ajouter une action immédiate", icon=ft.Icons.ADD, style="secondary", on_click=lambda e: self._add_immediate_row())
        rows.append(add_btn)
        return ft.Column(spacing=10, controls=rows)

    def _build_immediate_row(self, row_data=None):
        row_data = row_data or {}
        date_field = create_text_field("Quand (date)", value=row_data.get('date', ''), read_only=True, hint_text="Cliquer sur le calendrier")
        return {
            'correction': create_text_field("Correction effectuée", value=row_data.get('correction', '')),
            'responsable': create_text_field("Responsable / Qui", value=row_data.get('responsable', '')),
            'date': date_field,
            'date_picker_btn': ft.IconButton(ft.Icons.CALENDAR_MONTH, icon_color=Theme.PRIMARY, tooltip="Choisir une date", on_click=lambda e, f=date_field: self._open_action_date_picker(f, e)),
            'cost': create_text_field("Coût (EUR)", value=row_data.get('cost', '')),
        }

    def _add_immediate_row(self):
        self.immediate_rows.append(self._build_immediate_row())
        self.content_container.content = self._build_section_c()
        self.update()

    def _build_corrective_table(self):
        rows = []
        for row in self.corrective_rows:
            rows.append(create_card(content=ft.Column(spacing=6, controls=[
                row['desc'],
                ft.Row(spacing=8, controls=[
                    ft.Container(expand=1, content=row['responsable']), 
                    ft.Container(expand=1, content=ft.Row(spacing=0, controls=[row['date_debut'], row['date_debut_picker_btn']])), 
                    ft.Container(expand=1, content=row['cost'])
                ]),
                ft.Row(spacing=8, controls=[
                    ft.Container(expand=1, content=row['verification']), 
                    ft.Container(expand=1, content=row['statut']), 
                    ft.Container(expand=1, content=ft.Row(spacing=0, controls=[row['date_fin'], row['date_fin_picker_btn']]))
                ]),
            ])))
        add_btn = create_button("Ajouter une action corrective", icon=ft.Icons.ADD, style="secondary", on_click=lambda e: self._add_corrective_row())
        rows.append(add_btn)
        return ft.Column(spacing=10, controls=rows)

    def _add_corrective_row(self):
        self.corrective_rows.append(self._build_corrective_row())
        self.content_container.content = self._build_section_c()
        self.update()

    def _build_section_c(self):
        return create_card(content=ft.Column(spacing=12, controls=[
            ft.Text("Actions", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
            ft.Text("Actions immédiates (Corrections)", weight=ft.FontWeight.BOLD, color=Theme.DANGER),
            self._build_immediate_table(),
            ft.Text("Actions correctives", weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
            self._build_corrective_table(),
        ]))

    def _build_section_d(self):
        return create_card(content=ft.Column(spacing=10, controls=[
            ft.Text("Clôture", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
            ft.Row(spacing=8, controls=[
                ft.Container(expand=1, content=self.status_dropdown), 
                ft.Container(expand=1, content=ft.Row(controls=[
                    ft.Container(expand=True, content=self.closure_date_field),
                    ft.IconButton(ft.Icons.CALENDAR_MONTH, icon_color=Theme.PRIMARY, tooltip="Choisir une date de clôture", on_click=self._open_closure_date_picker)
                ]))
            ]),
            ft.Row(spacing=8, controls=[ft.Container(expand=1, content=self.verifier_field), ft.Container(expand=1, content=self.efficacy_dropdown)]),
            self.closure_comments_field,
        ]))

    def _collect_actions(self):
        immediate_data = []
        for row in self.immediate_rows:
            immediate_data.append({
                'correction': row['correction'].value,
                'responsable': row['responsable'].value,
                'date': row['date'].value,
                'cost': row['cost'].value,
            })
        corrective_data = []
        for row in self.corrective_rows:
            corrective_data.append({
                'desc': row['desc'].value,
                'responsable': row['responsable'].value,
                'date_debut': row['date_debut'].value,
                'cost': row['cost'].value,
                'verification': row['verification'].value,
                'statut': row['statut'].value,
                'date_fin': row['date_fin'].value,
            })
        return immediate_data, corrective_data

    def _collect_analysis_details(self):
        details = {}
        # 5 Why
        details['5why'] = {
            'whys': [f.value for f in self.fivewhy_fields],
            'root_cause': self.root_cause_field.value,
        }
        # Ishikawa
        ishikawa_cats = {}
        for cat, fields in self.ishikawa_categories.items():
            ishikawa_cats[cat] = [f.value for f in fields]
        details['ishikawa'] = {
            'categories': ishikawa_cats,
            'synthesis': self.ishikawa_synth_field.value,
        }
        selected_methods = []
        if self.method_5why.value:
            selected_methods.append("5 Pourquoi")
        if self.method_ishikawa.value:
            selected_methods.append("Ishikawa")
        details['method'] = ', '.join(selected_methods) if selected_methods else ''
        return details

    def _save(self, e):
        try:
            # Collecter toutes les données
            immediate_data, corrective_data = self._collect_actions()
            analysis_details = self._collect_analysis_details()
            selected_methods = analysis_details.get('method', '')

            # Valeurs par défaut
            if not self.date_field.value:
                self.date_field.value = datetime.now().strftime("%Y-%m-%d")
            if not self.type_dropdown.value:
                self.type_dropdown.value = "Interne"
            if not self.severity_dropdown.value:
                self.severity_dropdown.value = "Mineure"
            if not self.status_dropdown.value:
                self.status_dropdown.value = "En cours"

            # Parse quantité
            qty_val = None
            if self.qty_field.value:
                try:
                    qty_val = int(self.qty_field.value)
                except ValueError:
                    pass

            # Préparer les données
            data = {
                'reference': self.ref_field.value or self.db.generate_nc_reference(),
                'date_detection': self.date_field.value,
                'type_nc': self.type_dropdown.value or "Interne",
                'gravite': self.severity_dropdown.value or "Mineure",
                'origine': self.origin_field.value or '',
                'type_anomalie': self.anomaly_dropdown.value or '',
                'categorie_nc': self.category_field.value or '',
                'imputation': self.imputation_dropdown.value or '',
                'description': self.description_field.value or '',
                'produit_concerne': self.product_field.value or '',
                'lot_serie': self.lot_field.value or '',
                'quantite_affectee': qty_val,
                'lieu_detection': self.location_field.value or '',
                'pieces_jointes': json.dumps(self.attachments or []),
                'methode_analyse': selected_methods or '',
                'cause_racine': self.root_cause_field.value or '',
                'analyse_5m': json.dumps(self.selected_5m or []),
                'analyse_portee': self.portee_field.value or '',
                'analyse_details': json.dumps(analysis_details or {}),
                'actions_immediates_table': json.dumps(immediate_data or []),
                'actions_correctives_table': json.dumps(corrective_data or []),
                'statut': self.status_dropdown.value or "En cours",
                'date_cloture': self.closure_date_field.value or None,
                'efficacite': self.efficacy_dropdown.value or '',
                'commentaires_cloture': self.closure_comments_field.value or '',
                'detecteur_id': self.user['id'],
            }

            # Sauvegarder
            if self.nc_id:
                success = self.db.update_nc(self.nc_id, data)
                if success:
                    create_snackbar(self.page, f"[OK] NC {data['reference']} mise a jour", "success")
                    self.navigate("/nc")
                else:
                    create_snackbar(self.page, "Erreur lors de la mise à jour", "error")
            else:
                nc_id = self.db.create_nc(data)
                if nc_id:
                    create_snackbar(self.page, f"[OK] NC {data['reference']} creee (ID: {nc_id})", "success")
                    self.navigate("/nc")
                else:
                    create_snackbar(self.page, "Erreur lors de la création", "error")

        except Exception as ex:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Erreur sauvegarde: {error_detail}")
            create_snackbar(self.page, f"Erreur: {str(ex)[:100]}", "error")


class NCFichePage(ft.View):
    def __init__(self, user: Dict, db, navigate: Callable):
        self.user = user
        self.db = db
        self.navigate = navigate
        self.search_field = create_text_field("No NC ou No Lot", prefix_icon=ft.Icons.SEARCH)
        self.result_container = ft.Container(expand=True)
        super().__init__(route="/nc-fiche", bgcolor=Theme.BG_PRIMARY, padding=20, scroll=ft.ScrollMode.HIDDEN, controls=[self._build_ui()])

    def _build_ui(self):
        return ft.Container(
            expand=True,
            content=ft.Column(
                expand=True,
                spacing=10,
                controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                        ft.Row(controls=[ft.IconButton(ft.Icons.ARROW_BACK, icon_color=Theme.TEXT_MUTED, on_click=lambda e: self.navigate("/home")), ft.Text("Fiche unique", size=22, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)]),
                        create_button("Chercher", icon=ft.Icons.SEARCH, on_click=self._search),
                    ]),
                    self.search_field,
                    self.result_container,
                ]
            )
        )

    def _search(self, e):
        query = self.search_field.value
        if not query:
            create_snackbar(self.page, "Saisir un No de NC ou Lot", "warning")
            return
        nc = self.db.find_nc(query)
        if not nc:
            self.result_container.content = create_card(content=create_empty_state(ft.Icons.SEARCH_OFF, "Aucun résultat", ""))
            self.update()
            return
        # Afficher toutes les sections sans onglets
        self.result_container.content = self._build_full_nc_view(nc)
        self.update()

    def _build_full_nc_view(self, nc):
        """Affiche toutes les sections de la NC sur une seule page"""
        attachments = json.loads(nc.get('pieces_jointes', '[]')) if nc.get('pieces_jointes') else []
        immediate_actions = json.loads(nc.get('actions_immediates_table', '[]')) if nc.get('actions_immediates_table') else []
        corrective_actions = json.loads(nc.get('actions_correctives_table', '[]')) if nc.get('actions_correctives_table') else []
        selected_5m = json.loads(nc.get('analyse_5m', '[]')) if nc.get('analyse_5m') else []

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=15,
            controls=[
                # Header
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    ft.Text(f"[ID] NC {nc.get('reference', '-')}", size=20, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    ft.Row(controls=[
                        create_button("Modifier", icon=ft.Icons.EDIT, style="warning", on_click=lambda e: self.navigate(f"/nc/{nc['id']}/edit")),
                        create_button("Nouvelle recherche", icon=ft.Icons.SEARCH, style="secondary", on_click=lambda e: self._reset_search()),
                    ])
                ]),
                # Section A: Identification
                create_card(content=ft.Column(spacing=8, controls=[
                    ft.Text("A. Identification", size=18, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
                    ft.Divider(height=1, color=Theme.BG_TERTIARY),
                    self._info_row("Référence", nc.get('reference', '-')),
                    self._info_row("Date", nc.get('date_detection', '-')),
                    self._info_row("Type", nc.get('type_nc', '-')),
                    self._info_row("Gravité", nc.get('gravite', '-')),
                    self._info_row("Origine", nc.get('origine', '-')),
                    self._info_row("Anomalie", nc.get('type_anomalie', '-')),
                    self._info_row("Catégorie", nc.get('categorie_nc', '-')),
                    self._info_row("Imputation", nc.get('imputation', '-')),
                    self._info_row("Description", nc.get('description', '-'), multiline=True),
                    self._info_row("Produit", nc.get('produit_concerne', '-')),
                    self._info_row("Lot", nc.get('lot_serie', '-')),
                    self._info_row("Quantité", str(nc.get('quantite_affectee', '-'))),
                    self._info_row("Lieu", nc.get('lieu_detection', '-')),
                    ft.Text("Pièces jointes:", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY, size=13),
                    self._build_attachments_viewer(attachments) if attachments else ft.Text("Aucune", color=Theme.TEXT_MUTED, size=12),
                ])),
                # Section B: Analyse
                create_card(content=ft.Column(spacing=8, controls=[
                    ft.Text("B. Analyse", size=18, weight=ft.FontWeight.BOLD, color=Theme.SECONDARY),
                    ft.Divider(height=1, color=Theme.BG_TERTIARY),
                    self._info_row("Méthode(s)", nc.get('methode_analyse', '-')),
                    self._info_row("Cause racine", nc.get('cause_racine', '-'), multiline=True),
                    self._info_row("5M", ', '.join(selected_5m) if selected_5m else '-'),
                    self._info_row("Portée", nc.get('analyse_portee', '-'), multiline=True),
                ])),
                # Section C: Actions
                create_card(content=ft.Column(spacing=8, controls=[
                    ft.Text("C. Actions", size=18, weight=ft.FontWeight.BOLD, color=Theme.SUCCESS),
                    ft.Divider(height=1, color=Theme.BG_TERTIARY),
                    ft.Text("Actions immédiates:", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY, size=13),
                    self._build_actions_table(immediate_actions, True) if immediate_actions else ft.Text("Aucune", color=Theme.TEXT_MUTED, size=12),
                    ft.Container(height=5),
                    ft.Text("Actions correctives:", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY, size=13),
                    self._build_actions_table(corrective_actions, False) if corrective_actions else ft.Text("Aucune", color=Theme.TEXT_MUTED, size=12),
                ])),
                # Section D: Clôture
                create_card(content=ft.Column(spacing=8, controls=[
                    ft.Text("D. Clôture", size=18, weight=ft.FontWeight.BOLD, color=Theme.WARNING),
                    ft.Divider(height=1, color=Theme.BG_TERTIARY),
                    self._info_row("Statut", nc.get('statut', '-')),
                    self._info_row("Date clôture", nc.get('date_cloture', '-')),
                    self._info_row("Efficacité", nc.get('efficacite', '-')),
                    self._info_row("Commentaires", nc.get('commentaires_cloture', '-'), multiline=True),
                ])),
            ]
        )

    def _info_row(self, label, value, multiline=False):
        return ft.Row(controls=[
            ft.Container(width=180, content=ft.Text(label + ":", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY, size=13)),
            ft.Container(expand=True, content=ft.Text(str(value) if value else "-", color=Theme.TEXT_SECONDARY, size=13, max_lines=None if multiline else 1)),
        ])

    def _build_actions_table(self, actions, is_immediate):
        if is_immediate:
            rows = [ft.DataRow(cells=[
                ft.DataCell(ft.Text(a.get('desc', '-'), size=11)),
                ft.DataCell(ft.Text(a.get('responsable', '-'), size=11)),
                ft.DataCell(ft.Text(a.get('date', '-'), size=11)),
            ]) for a in actions]
            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Action", size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Responsable", size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Date", size=12, weight=ft.FontWeight.BOLD)),
                ],
                rows=rows,
                column_spacing=8,
            )
        else:
            rows = [ft.DataRow(cells=[
                ft.DataCell(ft.Text(a.get('desc', '-'), size=11)),
                ft.DataCell(ft.Text(a.get('responsable', '-'), size=11)),
                ft.DataCell(ft.Text(a.get('date_debut', '-'), size=11)),
                ft.DataCell(ft.Text(str(a.get('cost', '-')), size=11)),
                ft.DataCell(ft.Text(a.get('echeance', '-'), size=11)),
                ft.DataCell(ft.Text(a.get('statut', '-'), size=11)),
            ]) for a in actions]
            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Action", size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Responsable", size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Date", size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Coût", size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Échéance", size=12, weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Statut", size=12, weight=ft.FontWeight.BOLD)),
                ],
                rows=rows,
                column_spacing=8,
            )

    def _reset_search(self):
        self.search_field.value = ""
        self.result_container.content = None
        self.update()

    def _build_attachments_viewer(self, attachments):
        """Construit un viewer pour les pièces jointes avec affichage interne pour PDF/images"""
        import os
        attachment_controls = []
        
        for att in attachments:
            file_name = att.get('name', 'Fichier')
            file_path = att.get('path', '')
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # Déterminer le type de fichier
            is_image = file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
            is_pdf = file_ext == '.pdf'
            is_office = file_ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
            is_email = file_ext in ['.msg', '.eml']
            
            # Icône selon le type
            if is_image:
                icon = ft.Icons.IMAGE
                color = Theme.SUCCESS
            elif is_pdf:
                icon = ft.Icons.PICTURE_AS_PDF
                color = Theme.DANGER
            elif is_office:
                icon = ft.Icons.DESCRIPTION
                color = Theme.PRIMARY
            elif is_email:
                icon = ft.Icons.EMAIL
                color = Theme.SECONDARY
            else:
                icon = ft.Icons.ATTACH_FILE
                color = Theme.TEXT_MUTED
            
            # Bouton pour chaque fichier
            file_button = ft.Container(
                content=ft.Row(
                    spacing=8,
                    controls=[
                        ft.Icon(icon, color=color, size=20),
                        ft.Text(file_name, size=13, color=Theme.TEXT_PRIMARY),
                        ft.IconButton(
                            icon=ft.Icons.OPEN_IN_NEW if not (is_image or is_pdf) else ft.Icons.VISIBILITY,
                            icon_size=16,
                            tooltip="Ouvrir" if not (is_image or is_pdf) else "Visualiser",
                            on_click=lambda e, path=file_path, name=file_name, img=is_image, pdf=is_pdf: self._open_attachment(path, name, img, pdf)
                        )
                    ]
                ),
                padding=8,
                border=ft.Border(
                top=ft.BorderSide(1, Theme.BG_TERTIARY),
                right=ft.BorderSide(1, Theme.BG_TERTIARY),
                bottom=ft.BorderSide(1, Theme.BG_TERTIARY),
                left=ft.BorderSide(1, Theme.BG_TERTIARY),
            ),
                border_radius=8,
                bgcolor=Theme.BG_SECONDARY,
            )
            attachment_controls.append(file_button)
        
        return ft.Column(spacing=6, controls=attachment_controls)

    def _open_attachment(self, file_path, file_name, is_image, is_pdf):
        """Ouvre une pièce jointe en interne (image/PDF) ou externe (autres)"""
        import os
        if not file_path or not os.path.exists(file_path):
            create_snackbar(self.page, "[Attention] Fichier introuvable", "error")
            return
        
        if is_image:
            # Afficher l'image dans un dialog
            self._show_image_viewer(file_path, file_name)
        elif is_pdf:
            # Afficher le PDF dans un dialog (ou ouvrir en externe si viewer non dispo)
            self._show_pdf_viewer(file_path, file_name)
        else:
            # Ouvrir avec l'application par défaut (Word, PPT, Outlook, etc.)
            self._open_external(file_path, file_name)

    def _show_image_viewer(self, file_path, file_name):
        """Affiche une image dans un dialog"""
        import base64
        try:
            with open(file_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
            
            img = ft.Image(src_base64=img_data, fit=ft.ImageFit.CONTAIN)
            
            dialog = ft.AlertDialog(
                title=ft.Text(file_name),
                content=ft.Container(
                    width=800,
                    height=600,
                    content=img
                ),
                actions=[
                    ft.TextButton("Fermer", on_click=lambda e: self.page.close(dialog)),
                    ft.TextButton("Ouvrir en externe", on_click=lambda e: self._open_external(file_path, file_name)),
                ]
            )
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
        except Exception as ex:
            create_snackbar(self.page, f"[ERROR] Erreur: {str(ex)}", "error")

    def _show_pdf_viewer(self, file_path, file_name):
        """Affiche un PDF (pour l'instant, ouvre en externe)"""
        # Flet ne supporte pas nativement le viewer PDF, on ouvre en externe
        self._open_external(file_path, file_name)

    def _open_external(self, file_path, file_name):
        """Ouvre un fichier avec l'application par défaut du système"""
        import os
        import subprocess
        import platform
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
            create_snackbar(self.page, f"[OK] Ouverture de {file_name}", "success")
        except Exception as ex:
            create_snackbar(self.page, f"[ERROR] Erreur: {str(ex)}", "error")


class ComingSoonPage(ft.View):
    def __init__(self, title: str, icon: str, color: str, navigate: Callable, route: str):
        super().__init__(route=route, bgcolor=Theme.BG_PRIMARY, padding=30, vertical_alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[ft.Container(width=500, padding=50, border_radius=Styles.RADIUS_XL, bgcolor=Theme.BG_SECONDARY, content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[ft.Container(padding=20, border_radius=50, bgcolor=ft.Colors.with_opacity(0.15, color), content=ft.Icon(icon, color=color, size=50)), ft.Text(title, size=24, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY), ft.Text("[!] En developpement", size=14, color=Theme.TEXT_MUTED), create_button("Retour", icon=ft.Icons.HOME, on_click=lambda e: navigate("/home"))]))])


# === Users management page with password visibility ===
class UsersPage(ft.View):
    def __init__(self, user: Dict, db, navigate: Callable):
        self.user = user
        self.db = db
        self.navigate = navigate
        self.search_field = create_text_field(label="Rechercher", prefix_icon=ft.Icons.SEARCH, on_change=self._on_search, width=220)
        self.role_filter = create_dropdown("Rôle", ["Tous", "Administrateur", "Responsable", "Utilisateur"], on_change=self._on_filter, width=150)
        super().__init__(route="/users", bgcolor=Theme.BG_PRIMARY, padding=30, controls=[self._build_ui()])

    def _build_ui(self):
        return ft.Column(expand=True, controls=[
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                ft.Row(controls=[ft.IconButton(ft.Icons.ARROW_BACK, icon_color=Theme.TEXT_MUTED, on_click=lambda e: self.navigate("/home")), ft.Column(spacing=0, controls=[ft.Text("[Utilisateurs] Gestion des Utilisateurs", size=22, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY), ft.Text("Mots de passe visibles (admin)", size=12, color=Theme.TEXT_MUTED)])]),
                create_button("Nouvel utilisateur", icon=ft.Icons.PERSON_ADD, style="success", on_click=self._show_add_dialog),
            ]),
            ft.Container(height=15),
            create_card(content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Row(controls=[self.search_field, self.role_filter]), ft.IconButton(ft.Icons.REFRESH, icon_color=Theme.PRIMARY, tooltip="Actualiser", on_click=self._refresh)])),
            ft.Container(height=15),
            ft.Container(expand=True, content=self._build_table()),
        ])

    def _build_table(self):
        users = self.db.get_all_users()
        search = self.search_field.value.lower() if self.search_field.value else ""
        role_filter = self.role_filter.value if self.role_filter.value else "Tous"
        filtered = []
        for u in users:
            if search and search not in u['nom'].lower() and search not in u['email'].lower():
                continue
            if role_filter != "Tous" and u['role'] != role_filter:
                continue
            filtered.append(u)
        if not filtered:
            return create_card(content=create_empty_state(ft.Icons.PEOPLE_OUTLINE, "Aucun utilisateur", ""))
        rows = []
        for u in filtered:
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(u['nom'], color=Theme.TEXT_PRIMARY)),
                ft.DataCell(ft.Text(u['email'], color=Theme.TEXT_SECONDARY)),
                ft.DataCell(ft.Text(u.get('password_plain') or "N/A", color=Theme.TEXT_SECONDARY)),
                ft.DataCell(ft.Text(u['role'], color=Theme.TEXT_SECONDARY)),
                ft.DataCell(ft.Row(controls=[ft.Switch(value=bool(u['actif']), on_change=lambda e, uid=u['id']: self._toggle_active(uid, e.control.value)), ft.Text("Actif" if u['actif'] else "Inactif", color=Theme.SUCCESS if u['actif'] else Theme.TEXT_MUTED, size=12)])),
                ft.DataCell(ft.Row(controls=[ft.IconButton(ft.Icons.EDIT, icon_color=Theme.PRIMARY, icon_size=18, tooltip="Modifier", on_click=lambda e, uid=u['id']: self._show_edit_dialog(uid)), ft.IconButton(ft.Icons.DELETE, icon_color=Theme.DANGER, icon_size=18, tooltip="Supprimer", on_click=lambda e, uid=u['id']: self._delete_user(uid))])),
            ]))
        return create_card(content=ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Nom", color=Theme.TEXT_MUTED)),
            ft.DataColumn(ft.Text("Email", color=Theme.TEXT_MUTED)),
            ft.DataColumn(ft.Text("Mot de passe", color=Theme.TEXT_MUTED)),
            ft.DataColumn(ft.Text("Rôle", color=Theme.TEXT_MUTED)),
            ft.DataColumn(ft.Text("Statut", color=Theme.TEXT_MUTED)),
            ft.DataColumn(ft.Text("Actions", color=Theme.TEXT_MUTED)),
        ], rows=rows, column_spacing=12, horizontal_lines=ft.BorderSide(1, Theme.BG_TERTIARY)))

    def _toggle_active(self, user_id, active):
        self.db.update_user(user_id, actif=int(bool(active)))
        create_snackbar(self.page, "Statut mis à jour", "success")
        self._refresh(None)

    def _on_search(self, e):
        self._refresh(e)

    def _on_filter(self, e):
        self._refresh(e)

    def _refresh(self, e):
        self.controls[0].controls[-1].content = self._build_table()
        self.update()

    def _show_add_dialog(self, e):
        nom_field = create_text_field("Nom complet")
        email_field = create_text_field("Email")
        password_field = create_text_field("Mot de passe", password=True)
        role_dropdown = create_dropdown("Rôle", ["Utilisateur", "Responsable", "Administrateur"], value="Utilisateur")
        error_text = ft.Text("", color=Theme.DANGER, size=12)

        def save_user(ev):
            if not all([nom_field.value, email_field.value, password_field.value]):
                error_text.value = "Champs requis"
                error_text.update()
                return
            self.db.create_user(nom_field.value, email_field.value, password_field.value, role_dropdown.value or "Utilisateur")
            dialog.open = False
            self.page.update()
            self._refresh(ev)
            create_snackbar(self.page, "Utilisateur créé", "success")

        dialog = ft.AlertDialog(modal=True, title=ft.Text("Nouvel utilisateur"), content=ft.Column(tight=True, controls=[nom_field, email_field, password_field, role_dropdown, error_text]), actions=[ft.TextButton("Annuler", on_click=lambda ev: self._close_dialog(dialog)), create_button("Créer", style="success", on_click=save_user)], actions_alignment=ft.MainAxisAlignment.END)
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _show_edit_dialog(self, user_id):
        user = self.db.get_user(user_id)
        if not user:
            return
        nom_field = create_text_field("Nom complet", value=user['nom'])
        email_field = create_text_field("Email", value=user['email'])
        password_field = create_text_field("Nouveau mot de passe (optionnel)", password=True)
        role_dropdown = create_dropdown("Rôle", ["Utilisateur", "Responsable", "Administrateur"], value=user['role'])
        actif_switch = ft.Switch(label="Compte actif", value=bool(user['actif']))
        error_text = ft.Text("", color=Theme.DANGER, size=12)

        def save(ev):
            update_data = {'nom': nom_field.value, 'email': email_field.value, 'role': role_dropdown.value, 'actif': actif_switch.value}
            if password_field.value:
                update_data['password'] = password_field.value
            self.db.update_user(user_id, **update_data)
            dialog.open = False
            self.page.update()
            self._refresh(ev)
            create_snackbar(self.page, "Utilisateur modifié", "success")

        dialog = ft.AlertDialog(modal=True, title=ft.Text("Modifier utilisateur"), content=ft.Column(tight=True, controls=[nom_field, email_field, password_field, role_dropdown, actif_switch, ft.Text(f"Mot de passe actuel: {user.get('password_plain') or 'N/A'}", size=12, color=Theme.TEXT_MUTED), error_text]), actions=[ft.TextButton("Annuler", on_click=lambda ev: self._close_dialog(dialog)), create_button("Enregistrer", style="primary", on_click=save)], actions_alignment=ft.MainAxisAlignment.END)
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _delete_user(self, user_id):
        def do_delete():
            self.db.delete_user(user_id)
            self._refresh(None)
            create_snackbar(self.page, "Utilisateur supprimé", "success")
        confirm = ft.AlertDialog(modal=True, title=ft.Text("Supprimer ?"), content=ft.Text("Cette action est définitive."), actions=[ft.TextButton("Annuler", on_click=lambda e: self._close_dialog(confirm)), create_button("Supprimer", style="danger", on_click=lambda e: (do_delete(), self._close_dialog(confirm)))], actions_alignment=ft.MainAxisAlignment.END)
        self.page.overlay.append(confirm)
        confirm.open = True
        self.page.update()

    def _close_dialog(self, dialog):
        dialog.open = False
        self.page.update()


__all__ = [
    "LoginPage",
    "HomePage",
    "NCListPage",
    "NCFormPage",
    "NCFichePage",
    "UsersPage",
    "ComingSoonPage",
]

# -*- coding: utf-8 -*-
"""
QualiManager ERP QHSE - Module NC Avancé
Saisie NC avec gravité, coûts CNQ, Ishikawa 5M, Timeline Lot
"""

import flet as ft
from flet_core.dropdown import Option as DropdownOption
import os
from typing import Dict, Any, Callable, List, Optional
from datetime import datetime, timedelta
import calendar

from .theme import Theme
from .components import (
    create_card, create_text_field, create_dropdown, create_button,
    create_status_badge, create_severity_badge, create_snackbar, create_empty_state
)
from .components_advanced import (
    StatusBadge, SeverityBadge, KPICard, TimelineWidget, CostIndicator, AlertBanner
)
from .custom_calendar import CustomCalendar


class NCPage(ft.Container):
    """Page principale du module NC avancé."""
    
    def __init__(self, user: Dict, db, navigate: Callable):
        self.user = user
        self.db = db
        self.navigate = navigate
        self.current_tab = 0
        self.current_nc_id = None
        
        # Restaurer les filtres depuis les préférences ou valeurs par défaut
        saved_filters = self.db.get_user_preference(user['id'], 'nc', 'filters', default={})
        self.filter_status = saved_filters.get('status', "Tous")
        self.filter_gravite = saved_filters.get('gravite', "Tous")
        self.filter_type = saved_filters.get('type', "Tous")
        self.filter_search = saved_filters.get('search', "")
        self.filter_origine = saved_filters.get('origine', "Tous")
        self.filter_categorie = saved_filters.get('categorie', "Tous")
        self.filter_imputation = saved_filters.get('imputation', "Tous")
        self.filter_date_start = saved_filters.get('date_start', "")
        self.filter_date_end = saved_filters.get('date_end', "")
        
        self.show_form = False  # Mode formulaire pleine page
        self.editing_nc = None  # NC en cours d'édition
        self.form_tab_index = 0  # Onglet actif du formulaire
        self.selected_nc_ids = set()  # Ensemble des NC sélectionnées pour suppression multiple
        self._filter_date_picker_start = None
        self._filter_date_picker_end = None
        self._search_filter_field = None
        self._pending_search_focus = False
        self.detail_search_value = ""
        self.detail_selected_ref = ""
        self.detail_status_filter = "Tout"  # Nouveau filtre pour l'onglet Détail
        self.show_kpi_filters = False  # État pour afficher/masquer KPI et filtres (masqué par défaut)
        self.show_selection_column = False  # État pour afficher/masquer la colonne de sélection
        self._kpi_filters_container = None  # Référence au conteneur KPI/filtres
        self._nc_cache = None  # Cache des NC pour éviter rechargements multiples
        self._last_window_width = None  # Pour détecter les changements de largeur d'écran
        self._responsive_threshold = 1450  # Seuil de basculement responsive (inclut 1366px)
        
        # Pagination
        self.current_page = 1
        self.items_per_page = 25  # Réduit de 50 à 25 pour meilleures performances
        self.total_nc_count = 0
        
        # Lazy loading des onglets
        self._tabs_cache = {}  # Cache des onglets construits
        self._search_timer = None  # Timer pour debouncing de recherche
        
        # Popup NC actuelle
        self._current_popup = None  # Référence à la popup actuellement ouverte
        
        # Listes de choix pour dropdowns (modifiables)
        self.type_nc_choices = ["Interne", "Client", "Fournisseur", "Prestataire", "Audit"]
        self.anomaly_choices = [
            "Habillage", "Commande", "Casse occulte", "Erreur validation", "Erreur procédé",
            "Erreur préparation", "Casse", "Conditionnement", "Marquage", "Matériel",
            "Réglementaire", "Livraison", "Facturation", "Documentation", "Environnement",
            "Corps étranger", "Quantité"
        ]
        self.imputation_choices = [
            "Expédition", "Dégorgement", "QSE", "Cuverie", "Tirage", "Fournisseur",
            "Transport", "Indéterminée", "Ordonnancement", "Espaces ventes",
            "Prestataire", "Habillage", "WLS", "Caves"
        ]
        self.matieres_choices = [
            "Crémants", "VMQ", "Vins tranquiles", "Bouchons", "Bouteilles", "Muselets",
            "Contre-étiquettes", "Étiquettes", "Collerettes", "Coiffes", "Cartons",
            "Boxes", "Machines", "Capsules", "Bidules", "Cerises", "Crèmes", "Ratafia", "Coffrets"
        ]
        
        # Filtres pour statistiques
        self.stats_selected_type = "Tout"  # Un seul type sélectionné à la fois (Tout, Audit, Client, etc)
        self.stats_evolution_year = datetime.now().year  # Année sélectionnée pour évolution mensuelle
        self.stats_years_selected = [2025, 2024, 2023]  # Années sélectionnées par défaut
        self.stats_zone_b_dates = {}  # Filtres de dates par graphique Zone B
        self.stats_zone_b_temp_dates = {}  # Dates temporaires avant validation
        self._stats_date_pickers = {}  # DatePickers pour Zone B (debut/fin par chart_id)
        self.stats_zone_b_top_limit = {}  # Limite du nombre de valeurs à afficher par graphique ("Tout" ou nombre)
        self._preload_started = False  # Flag pour éviter les préchargements multiples
        
        # Suivi Actions - Pagination, cache, recherche, tri
        self._actions_page = 1  # Page actuelle
        self._actions_per_page = 50  # Nombre d'actions par page
        self._actions_cache = None  # Cache des actions
        self._actions_cache_time = None  # Timestamp du cache
        self._actions_search = ""  # Recherche textuelle
        self._actions_sort_field = "nc_ref"  # Champ de tri (nc_ref, date_echeance, statut)
        self._actions_sort_order = "desc"  # Ordre de tri (asc/desc)
        self._actions_filter_category = "Tout"  # Filtre catégorie
        self._actions_filter_deadline = "Tout"  # Filtre échéance
        self._actions_table_container = None  # Référence au conteneur du tableau
        self._actions_show_filters = False  # Afficher/masquer filtres et KPI (masqué par défaut)
        
        # Cache pour optimisation de performance
        self._chart_cache = {}  # Cache des graphiques matplotlib
        self._stats_data_cache = None  # Cache des données statistiques
        self._stats_loaded = False  # Flag pour lazy loading des statistiques
        
        # Références aux containers pour actualisation partielle
        self._evolution_container = None
        self._comparateur_container = None
        self._actions_correctives_container = None
        
        super().__init__(
            expand=True,
            bgcolor=Theme.BG_PRIMARY,
            padding=0,
            content=self._build_ui(),
        )
    
    def _build_ui(self):
        """Construit l'interface principale."""
        try:
            if self.show_form:
                return self._build_form_page()
            
            self.header = ft.Container(
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
                                            "[Attention] Gestion des Non-Conformités",
                                            size=22,
                                            weight=ft.FontWeight.BOLD,
                                            color=Theme.TEXT_PRIMARY,
                                        ),
                                        ft.Text(
                                            "Saisie, analyse causale et suivi des coûts CNQ",
                                            size=13,
                                            color=Theme.TEXT_MUTED,
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        create_button(
                            "Nouvelle NC",
                            icon=ft.Icons.ADD,
                            on_click=lambda e: self._open_form(),
                        ),
                    ]
                ),
            )
            
            # Tabs avec design amélioré
            self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            on_change=self._on_tab_change,
            scrollable=True,
            tab_alignment=ft.TabAlignment.START,
            label_color=Theme.PRIMARY,
            unselected_label_color=Theme.TEXT_MUTED,
            indicator_color=Theme.PRIMARY,
            indicator_tab_size=True,
            divider_color=Theme.OUTLINE,
            tabs=[
                ft.Tab(
                    text="Tableau de Bord",
                    icon=ft.Icons.DASHBOARD_ROUNDED,
                ),
                ft.Tab(
                    text="Liste NC",
                    icon=ft.Icons.FORMAT_LIST_BULLETED_ROUNDED,
                ),
                ft.Tab(
                    text="Détail",
                    icon=ft.Icons.DESCRIPTION_ROUNDED,
                ),
                ft.Tab(
                    text="Analyse",
                    icon=ft.Icons.ANALYTICS_ROUNDED,
                ),
                ft.Tab(
                    text="Suivi Actions",
                    icon=ft.Icons.TRACK_CHANGES_ROUNDED,
                ),
                ft.Tab(
                    text="Statistiques",
                    icon=ft.Icons.SHOW_CHART_ROUNDED,
                ),
            ],
            )
            
            self.tab_content = ft.Container(
                expand=True,
                padding=20,
                content=self._build_dashboard_tab(),
            )
            
            
            result = ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    self.header,
                    ft.Container(
                        padding=ft.Padding(left=20, right=20, top=10, bottom=10),
                        bgcolor=Theme.BG_SECONDARY,
                        border=ft.Border(
                            bottom=ft.BorderSide(2, Theme.OUTLINE)
                        ),
                        content=self.tabs,
                    ),
                    self.tab_content,
                ]
            )
            return result
            
        except Exception as e:
            print(f"[NCPage._build_ui] [Erreur] ERREUR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            # Retourner une interface d'erreur
            return ft.Column(
                controls=[
                    ft.Text("[Erreur] Erreur lors de la construction de l'interface", size=20, weight=ft.FontWeight.BOLD, color="red"),
                    ft.Text(f"{type(e).__name__}: {str(e)}", size=14),
                ]
            )
    
    def _open_form(self, nc: Dict = None):
        """Ouvre le formulaire en pleine page."""
        try:
            self.show_form = True
            self.editing_nc = nc
            # Ne réinitialiser form_tab_index que si ce n'est pas déjà défini
            if not hasattr(self, 'form_tab_index') or self.form_tab_index is None:
                self.form_tab_index = 0
            
            self._init_form_fields()
            self.content = self._build_ui()
            self.page.update()
        except Exception as ex:
            print(f"[ERREUR] _open_form: {ex}")
            import traceback
            traceback.print_exc()
            # Utiliser une notification simple sans dépendance à self.page
            if hasattr(self, 'page') and self.page:
                create_snackbar(self.page, f"[Erreur] Erreur lors de l'ouverture: {str(ex)}", "error")
    
    def _close_form(self):
        """Ferme le formulaire et retourne à la liste."""
        self.show_form = False
        self.editing_nc = None
        self.form_tab_index = None  # Réinitialiser pour la prochaine ouverture
        self.content = self._build_ui()
        self.page.update()
    
    def _open_form_readonly(self, nc: Dict):
        """Affiche la NC dans l'onglet Détail (lecture seule) de manière optimisée."""
        try:
            # Définir la NC courante
            self.current_nc_id = nc.get('id')
            
            # Passer à l'onglet Détail (index 2 maintenant)
            self.tabs.selected_index = 2
            self.current_tab = 2
            
            # Invalider le cache de l'onglet Détail pour forcer la reconstruction
            if 2 in self._tabs_cache:
                del self._tabs_cache[2]
            
            # Construire l'onglet Détail
            self.tab_content.content = self._build_detail_tab()
            self._tabs_cache[2] = self.tab_content.content  # CORRECTION: cache pour l'onglet 2 (Détail), pas 1
            
            # Mise à jour unique
            self.page.update()
        except Exception as ex:
            print(f"Erreur affichage NC: {ex}")
            if hasattr(self, 'page') and self.page:
                create_snackbar(self.page, f"[Erreur] Erreur: {str(ex)}", "error")
    
    def _duplicate_nc(self, nc: Dict):
        """Duplique une NC existante."""
        try:
            # Créer une copie de la NC
            nc_copy = nc.copy()
            
            # Supprimer les champs qui ne doivent pas être dupliqués
            if 'id' in nc_copy:
                del nc_copy['id']
            if 'reference' in nc_copy:
                del nc_copy['reference']  # Sera généré automatiquement
            
            # Modifier certains champs
            nc_copy['statut'] = 'En cours'
            nc_copy['date_cloture'] = None
            nc_copy['date_detection'] = datetime.now().strftime('%Y-%m-%d')
            
            # Ajouter un préfixe à la description
            if 'description' in nc_copy and nc_copy['description']:
                nc_copy['description'] = f"[COPIE] {nc_copy['description']}"
            
            # Ouvrir le formulaire avec les données copiées
            self._open_form(nc_copy)
            
            create_snackbar(self.page, f"[OK] NC dupliquée - Modifiez et sauvegardez", "success")
            
        except Exception as ex:
            print(f"Erreur duplication NC: {ex}")
            create_snackbar(self.page, f"[Erreur] Erreur lors de la duplication: {str(ex)}", "error")

    def _export_to_csv(self, e=None):
        """Exporte la liste des NC filtrées vers un fichier CSV."""
        try:
            import csv
            from datetime import datetime
            
            ncs = self._get_nc_list()
            
            if not ncs:
                create_snackbar(self.page, "[Attention] Aucune NC à exporter", "warning")
                return
            
            # Utiliser FilePicker pour choisir l'emplacement
            def on_file_result(e: ft.FilePickerResultEvent):
                if e.path:
                    try:
                        filepath = e.path
                        if not filepath.endswith('.csv'):
                            filepath += '.csv'
                        
                        # Écrire le CSV
                        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                            writer = csv.writer(f, delimiter=';')
                            
                            # En-têtes avec Lot et Quantité
                            headers = [
                                'Référence', 'Date', 'Statut', 'Type', 'Gravité', 'Origine',
                                'Produit', 'Lot', 'Quantité', 'Description', 'Catégorie', 
                                'Imputation', 'Responsable', 'Actions', 'Coût'
                            ]
                            writer.writerow(headers)
                            
                            # Données avec texte complet (retours à la ligne)
                            for nc in ncs:
                                row = [
                                    nc.get('reference', ''),
                                    nc.get('date_detection', ''),
                                    nc.get('statut', ''),
                                    nc.get('type_nc', ''),
                                    nc.get('gravite', ''),
                                    nc.get('origine', ''),
                                    nc.get('produit_concerne', ''),
                                    nc.get('lot_serie', ''),
                                    nc.get('quantite_affectee', ''),
                                    nc.get('description', ''),  # Texte complet
                                    nc.get('categorie_nc', ''),
                                    nc.get('imputation', ''),
                                    nc.get('responsable_traitement', ''),
                                    nc.get('actions_immediates', ''),  # Texte complet
                                    nc.get('cout_estime', ''),
                                ]
                                writer.writerow(row)
                        
                        # Confirmation
                        create_snackbar(self.page, f"[OK] Fichier exporté : {os.path.basename(filepath)} ({len(ncs)} NC)", "success")
                    except Exception as ex:
                        print(f"Erreur écriture CSV: {ex}")
                        create_snackbar(self.page, f"[Erreur] Erreur lors de l'écriture: {str(ex)}", "error")
            
            # Créer et ouvrir le FilePicker
            file_picker = ft.FilePicker(on_result=on_file_result)
            self.page.overlay.append(file_picker)
            self.page.update()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_picker.save_file(
                dialog_title="Enregistrer le fichier CSV",
                file_name=f"export_nc_{timestamp}.csv",
                allowed_extensions=["csv"]
            )
            
        except Exception as ex:
            print(f"Erreur export CSV: {ex}")
            create_snackbar(self.page, f"[Erreur] Erreur export CSV: {str(ex)}", "error")

    def _export_to_excel(self, e=None):
        """Exporte la liste des NC filtrées vers un fichier Excel."""
        try:
            from datetime import datetime
            
            ncs = self._get_nc_list()
            
            if not ncs:
                create_snackbar(self.page, "[Attention] Aucune NC à exporter", "warning")
                return
            
            try:
                import openpyxl
                from openpyxl.styles import Font, PatternFill, Alignment
            except ImportError:
                create_snackbar(self.page, "[Attention] Bibliothèque openpyxl non disponible. Export CSV disponible.", "warning")
                return
            
            def on_file_result(e: ft.FilePickerResultEvent):
                if e.path:
                    try:
                        filepath = e.path
                        if not filepath.endswith('.xlsx'):
                            filepath += '.xlsx'
                        
                        # Créer le workbook
                        wb = openpyxl.Workbook()
                        ws = wb.active
                        ws.title = "Non-Conformités"
                        
                        # Style d'en-tête
                        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                        header_font = Font(bold=True, color="FFFFFF")
                        
                        # En-têtes avec Lot et Quantité
                        headers = [
                            'Référence', 'Date', 'Statut', 'Type', 'Gravité', 'Origine',
                            'Produit', 'Lot', 'Quantité', 'Description', 'Catégorie', 
                            'Imputation', 'Responsable', 'Actions', 'Coût'
                        ]
                        
                        for col_num, header in enumerate(headers, 1):
                            cell = ws.cell(row=1, column=col_num, value=header)
                            cell.fill = header_fill
                            cell.font = header_font
                            cell.alignment = Alignment(horizontal='center', vertical='center')
                        
                        # Données avec wrap text
                        for row_num, nc in enumerate(ncs, 2):
                            ws.cell(row=row_num, column=1, value=nc.get('reference', ''))
                            ws.cell(row=row_num, column=2, value=nc.get('date_detection', ''))
                            ws.cell(row=row_num, column=3, value=nc.get('statut', ''))
                            ws.cell(row=row_num, column=4, value=nc.get('type_nc', ''))
                            ws.cell(row=row_num, column=5, value=nc.get('gravite', ''))
                            ws.cell(row=row_num, column=6, value=nc.get('origine', ''))
                            ws.cell(row=row_num, column=7, value=nc.get('produit_concerne', ''))
                            ws.cell(row=row_num, column=8, value=nc.get('lot_serie', ''))
                            ws.cell(row=row_num, column=9, value=nc.get('quantite_affectee', ''))
                            
                            # Description avec wrap text
                            desc_cell = ws.cell(row=row_num, column=10, value=nc.get('description', ''))
                            desc_cell.alignment = Alignment(wrap_text=True, vertical='top')
                            
                            ws.cell(row=row_num, column=11, value=nc.get('categorie_nc', ''))
                            ws.cell(row=row_num, column=12, value=nc.get('imputation', ''))
                            ws.cell(row=row_num, column=13, value=nc.get('responsable_traitement', ''))
                            
                            # Actions avec wrap text
                            actions_cell = ws.cell(row=row_num, column=14, value=nc.get('actions_immediates', ''))
                            actions_cell.alignment = Alignment(wrap_text=True, vertical='top')
                            
                            ws.cell(row=row_num, column=15, value=nc.get('cout_estime', ''))
                        
                        # Ajuster largeur colonnes
                        ws.column_dimensions['A'].width = 12
                        ws.column_dimensions['B'].width = 12
                        ws.column_dimensions['C'].width = 10
                        ws.column_dimensions['D'].width = 12
                        ws.column_dimensions['E'].width = 10
                        ws.column_dimensions['F'].width = 15
                        ws.column_dimensions['G'].width = 20
                        ws.column_dimensions['H'].width = 15
                        ws.column_dimensions['I'].width = 10
                        ws.column_dimensions['J'].width = 50  # Description
                        ws.column_dimensions['K'].width = 15
                        ws.column_dimensions['L'].width = 15
                        ws.column_dimensions['M'].width = 20
                        ws.column_dimensions['N'].width = 40  # Actions
                        ws.column_dimensions['O'].width = 12
                        
                        # Sauvegarder
                        wb.save(filepath)
                        
                        # Confirmation
                        create_snackbar(self.page, f"[OK] Fichier exporté : {os.path.basename(filepath)} ({len(ncs)} NC)", "success")
                    except Exception as ex:
                        print(f"Erreur écriture Excel: {ex}")
                        create_snackbar(self.page, f"[Erreur] Erreur lors de l'écriture: {str(ex)}", "error")
            
            # Créer et ouvrir le FilePicker
            file_picker = ft.FilePicker(on_result=on_file_result)
            self.page.overlay.append(file_picker)
            self.page.update()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_picker.save_file(
                dialog_title="Enregistrer le fichier Excel",
                file_name=f"export_nc_{timestamp}.xlsx",
                allowed_extensions=["xlsx"]
            )
            
        except Exception as ex:
            print(f"Erreur export Excel: {ex}")
            create_snackbar(self.page, f"[Erreur] Erreur export Excel: {str(ex)}", "error")

    def _export_to_pdf(self, e=None):
        """Exporte la liste des NC filtrées vers un fichier PDF avec format ISO 9001:2015."""
        try:
            from datetime import datetime
            
            ncs = self._get_nc_list()
            
            if not ncs:
                create_snackbar(self.page, "[Attention] Aucune NC à exporter", "warning")
                return
            
            try:
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import A4, landscape
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import cm
                from reportlab.lib.utils import ImageReader
                from PIL import Image as PILImage, ImageOps
            except ImportError:
                create_snackbar(self.page, "[Attention] Bibliothèque reportlab non disponible. Export CSV disponible.", "warning")
                return
            
            # Date et heure d'export
            now = datetime.now()
            export_datetime = now.strftime('%d/%m/%Y à %H:%M')
            
            def add_header_footer(canvas, doc):
                """Ajoute en-tête et pied de page ISO 9001:2015 à chaque page."""
                canvas.saveState()
                
                # Logo entreprise
                current_dir = os.path.dirname(os.path.abspath(__file__))
                parent_dir = os.path.dirname(current_dir)
                
                possible_paths = [
                    os.path.join(parent_dir, 'assets', 'logo_entreprise.png'),
                    os.path.join(os.getcwd(), 'assets', 'logo_entreprise.png'),
                    'assets/logo_entreprise.png',
                ]
                
                logo_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        logo_path = path
                        break
                
                if logo_path:
                    try:
                        pil_img = PILImage.open(logo_path)
                        
                        # Traitement spécial pour mode LA (gris + alpha)
                        if pil_img.mode == 'LA':
                            luminance, alpha = pil_img.split()
                            gray_img = ImageOps.invert(alpha)
                            pil_img = gray_img.convert('RGB')
                        elif pil_img.mode in ('RGBA', 'P'):
                            background = PILImage.new('RGB', pil_img.size, (255, 255, 255))
                            if pil_img.mode == 'P':
                                pil_img = pil_img.convert('RGBA')
                            background.paste(pil_img, (0, 0), pil_img.split()[-1])
                            pil_img = background
                        elif pil_img.mode == 'L':
                            pil_img = pil_img.convert('RGB')
                        elif pil_img.mode != 'RGB':
                            pil_img = pil_img.convert('RGB')
                        
                        # Logo en haut à gauche (landscape format)
                        img_reader = ImageReader(pil_img)
                        canvas.drawImage(img_reader, 2*cm, landscape(A4)[1] - 1.8*cm, width=3.5*cm, height=1.3*cm, preserveAspectRatio=True)
                    except Exception as e:
                        print(f"[PDF] Erreur logo: {e}")
                
                # Titre document en haut à droite
                canvas.setFont('Helvetica-Bold', 12)
                canvas.setFillColor(colors.HexColor('#3B82F6'))
                canvas.drawRightString(landscape(A4)[0] - 2*cm, landscape(A4)[1] - 1.3*cm, "LISTE DES NON-CONFORMITÉS")
                
                # Mentions ISO sous le titre
                canvas.setFont('Helvetica', 8)
                canvas.setFillColor(colors.HexColor('#666666'))
                canvas.drawRightString(landscape(A4)[0] - 2*cm, landscape(A4)[1] - 1.6*cm, "Conforme ISO 9001:2015 / IATF 16949")
                
                # Ligne de séparation
                canvas.setStrokeColor(colors.HexColor('#3B82F6'))
                canvas.setLineWidth(2)
                canvas.line(2*cm, landscape(A4)[1] - 2.1*cm, landscape(A4)[0] - 2*cm, landscape(A4)[1] - 2.1*cm)
                
                # Pied de page
                canvas.setStrokeColor(colors.HexColor('#CCCCCC'))
                canvas.setLineWidth(1)
                canvas.line(2*cm, 1.5*cm, landscape(A4)[0] - 2*cm, 1.5*cm)
                
                canvas.setFont('Helvetica', 8)
                canvas.setFillColor(colors.grey)
                canvas.drawString(2*cm, 1.2*cm, f"Document généré le {export_datetime}")
                canvas.drawString(2*cm, 0.9*cm, f"{len(ncs)} non-conformité(s) listée(s)")
                
                page_num = canvas.getPageNumber()
                canvas.drawRightString(landscape(A4)[0] - 2*cm, 1.2*cm, f"Page {page_num}")
                canvas.drawRightString(landscape(A4)[0] - 2*cm, 0.9*cm, "QualiManager ERP")
                
                canvas.restoreState()
            
            def on_file_result(e: ft.FilePickerResultEvent):
                if e.path:
                    try:
                        filepath = e.path
                        if not filepath.endswith('.pdf'):
                            filepath += '.pdf'
                        
                        # Créer le document avec marges pour en-tête/pied de page
                        doc = SimpleDocTemplate(
                            filepath, 
                            pagesize=landscape(A4),
                            topMargin=3*cm,
                            bottomMargin=2.5*cm,
                            leftMargin=2*cm,
                            rightMargin=2*cm
                        )
                        
                        # Styles
                        styles = getSampleStyleSheet()
                        cell_style = ParagraphStyle(
                            'CellStyle',
                            parent=styles['Normal'],
                            fontSize=7,
                            leading=9,
                        )
                        
                        # Données du tableau
                        data = [['Réf', 'Date', 'Statut', 'Type', 'Origine', 'Produit', 'Lot', 'Qté', 'Description']]
                        
                        for nc in ncs:
                            origine = Paragraph(nc.get('origine') or '', cell_style)
                            produit = Paragraph(nc.get('produit_concerne') or '', cell_style)
                            lot = Paragraph(nc.get('lot_serie') or '', cell_style)
                            desc = Paragraph(nc.get('description') or '', cell_style)
                            
                            row = [
                                nc.get('reference', ''),
                                nc.get('date_detection', '')[:10] if nc.get('date_detection') else '',
                                nc.get('statut', ''),
                                nc.get('type_nc', ''),
                                origine,
                                produit,
                                lot,
                                nc.get('quantite_affectee') or '',
                                desc,
                            ]
                            data.append(row)
                        
                        # Créer le tableau
                        table = Table(data, colWidths=[2.5*cm, 2*cm, 2*cm, 2.5*cm, 3*cm, 3.5*cm, 2.5*cm, 1.5*cm, 6*cm])
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 9),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('FONTSIZE', (0, 1), (-1, -1), 7),
                            ('TOPPADDING', (0, 1), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
                            ('LEFTPADDING', (0, 0), (-1, -1), 3),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                        ]))
                        
                        # Construire le PDF avec en-tête et pied de page
                        doc.build([table], onFirstPage=add_header_footer, onLaterPages=add_header_footer)
                        
                        # Confirmation
                        create_snackbar(self.page, f"[OK] Fichier exporté : {os.path.basename(filepath)} ({len(ncs)} NC)", "success")
                    except Exception as ex:
                        print(f"Erreur écriture PDF: {ex}")
                        import traceback
                        traceback.print_exc()
                        create_snackbar(self.page, f"[Erreur] Erreur lors de l'écriture: {str(ex)}", "error")
            
            # Créer et ouvrir le FilePicker
            file_picker = ft.FilePicker(on_result=on_file_result)
            self.page.overlay.append(file_picker)
            self.page.update()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_picker.save_file(
                dialog_title="Enregistrer le fichier PDF",
                file_name=f"export_nc_{timestamp}.pdf",
                allowed_extensions=["pdf"]
            )
            
        except Exception as ex:
            print(f"Erreur export PDF: {ex}")
            create_snackbar(self.page, f"[Erreur] Erreur export PDF: {str(ex)}", "error")
    
    def _import_from_excel(self, e=None):
        """Importe des NC depuis un fichier Excel."""
        try:
            try:
                import openpyxl
            except ImportError:
                create_snackbar(self.page, "[Attention] Bibliothèque openpyxl non disponible pour l'import.", "warning")
                return
            
            def on_file_result(e: ft.FilePickerResultEvent):
                if e.files:
                    # Afficher un indicateur de chargement
                    progress_dialog = ft.AlertDialog(
                        modal=True,
                        title=ft.Text("[EnCours] Import en cours...", weight=ft.FontWeight.BOLD),
                        content=ft.Container(
                            padding=20,
                            content=ft.Column([
                                ft.ProgressRing(),
                                ft.Text("Lecture et import du fichier Excel...", size=14),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True)
                        ),
                    )
                    self.page.overlay.append(progress_dialog)
                    progress_dialog.open = True
                    self.page.update()
                    
                    try:
                        filepath = e.files[0].path
                        
                        # Lire le fichier Excel
                        wb = openpyxl.load_workbook(filepath)
                        ws = wb.active
                        
                        # Lire les en-têtes de la première ligne
                        headers = [str(cell.value).strip().lower() if cell.value else '' for cell in ws[1]]
                        
                        # Mapping des colonnes Excel vers les champs de la base
                        # Format Excel attendu : Référence, Date, Type, Gravité, Origine, Type anomalie, Catégorie, Imputation, Description, Produit, Quantité, Lot, Statut, Cause racine, Lieu
                        col_mapping = {}
                        for idx, header in enumerate(headers):
                            h = header.lower().strip()
                            if h in ['référence', 'reference', 'ref', 'no']:
                                col_mapping['reference'] = idx
                            elif h in ['date', 'date detection']:
                                col_mapping['date_detection'] = idx
                            elif h in ['type', 'type nc']:
                                col_mapping['type_nc'] = idx
                            elif h in ['gravité', 'gravite']:
                                col_mapping['gravite'] = idx
                            elif h in ['origine']:
                                col_mapping['origine'] = idx
                            elif h in ['type anomalie', 'anomalie']:
                                col_mapping['type_anomalie'] = idx
                            elif h in ['catégorie', 'categorie']:
                                col_mapping['categorie_nc'] = idx
                            elif h in ['imputation']:
                                col_mapping['imputation'] = idx
                            elif h in ['description']:
                                col_mapping['description'] = idx
                            elif h in ['produit', 'produit concerné']:
                                col_mapping['produit_concerne'] = idx
                            elif h in ['quantité', 'quantite', 'qté']:
                                col_mapping['quantite_affectee'] = idx
                            elif h in ['lot', 'no lot']:
                                col_mapping['lot_serie'] = idx
                            elif h in ['statut', 'état']:
                                col_mapping['statut'] = idx
                            elif h in ['cause racine', 'cause']:
                                col_mapping['cause_racine'] = idx
                            elif h in ['lieu']:
                                col_mapping['lieu_detection'] = idx
                        
                        # Validation des colonnes obligatoires
                        if 'reference' not in col_mapping:
                            create_snackbar(self.page, "[Erreur] Colonne 'Référence' manquante", "error")
                            return
                        
                        imported_count = 0
                        error_count = 0
                        errors = []
                        
                        # Importer chaque ligne (à partir de la ligne 2)
                        for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                            try:
                                # Créer un dictionnaire avec les valeurs mappées
                                nc_data = {}
                                for field, col_idx in col_mapping.items():
                                    if col_idx < len(row) and row[col_idx]:
                                        value = str(row[col_idx]).strip()
                                        if field == 'date_detection' and value:
                                            # Gérer les dates
                                            try:
                                                from datetime import datetime
                                                if isinstance(row[col_idx], datetime):
                                                    value = row[col_idx].strftime('%Y-%m-%d')
                                                elif '/' in value:
                                                    # Format DD/MM/YYYY ou MM/DD/YYYY
                                                    parts = value.split('/')
                                                    if len(parts) == 3:
                                                        value = f"{parts[2]}-{parts[1]:0>2}-{parts[0]:0>2}"
                                            except:
                                                pass
                                        nc_data[field] = value
                                
                                # Ajouter les valeurs par défaut
                                if 'statut' not in nc_data:
                                    nc_data['statut'] = 'En cours'
                                if 'gravite' not in nc_data:
                                    nc_data['gravite'] = 'Mineure'
                                if 'type_nc' not in nc_data:
                                    nc_data['type_nc'] = 'Interne'
                                
                                # Ajouter le détecteur (utilisateur actuel)
                                nc_data['detecteur_id'] = self.user.get('id')
                                
                                # Valider les champs obligatoires
                                if 'reference' not in nc_data or not nc_data.get('reference'):
                                    errors.append(f"Ligne {row_num}: Référence obligatoire")
                                    error_count += 1
                                    continue
                                
                                # Ajouter la date de création
                                from datetime import datetime
                                if 'date_detection' not in nc_data or not nc_data['date_detection']:
                                    nc_data['date_detection'] = datetime.now().strftime('%Y-%m-%d')
                                
                                # Insérer dans la base de données
                                nc_id = self.db.create_nc(nc_data)
                                if nc_id:
                                    imported_count += 1
                                else:
                                    errors.append(f"Ligne {row_num}: Erreur insertion en base")
                                    error_count += 1
                                
                            except Exception as row_ex:
                                errors.append(f"Ligne {row_num}: {str(row_ex)}")
                                error_count += 1
                                print(f"Erreur import ligne {row_num}: {row_ex}")
                        
                        # Rafraîchir les caches et l'interface
                        self._refresh_nc_cache()
                        
                        # Invalider les caches des onglets pour forcer la reconstruction
                        if 0 in self._tabs_cache:
                            del self._tabs_cache[0]  # Tableau de bord
                        if 1 in self._tabs_cache:
                            del self._tabs_cache[1]  # Liste NC
                        if 4 in self._tabs_cache:
                            del self._tabs_cache[4]  # Suivi Actions
                        
                        # Invalider le cache actions
                        self._actions_cache = None
                        self._actions_cache_time = None
                        
                        # Si on est sur l'onglet Liste (1), le reconstruire immédiatement
                        if self.current_tab == 1:
                            self._tabs_cache[1] = self._build_list_tab()
                            self.tab_content.content = self._tabs_cache[1]
                        
                        # Fermer le dialog de progression
                        progress_dialog.open = False
                        self.page.update()
                        
                        # Afficher TOUJOURS le résumé d'import
                        if error_count == 0:
                            # Succès complet
                            def close_success_dialog(e):
                                success_dialog.open = False
                                self.page.update()
                            
                            success_dialog = ft.AlertDialog(
                                modal=True,
                                title=ft.Text("[OK] Import réussi", color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD),
                                content=ft.Container(
                                    padding=20,
                                    content=ft.Column([
                                        ft.Text(f"[Stats] {imported_count} NC importées avec succès", size=16),
                                        ft.Container(height=10),
                                        ft.Text("Toutes les NC ont été ajoutées à votre base de données.", size=14),
                                    ], tight=True)
                                ),
                                actions=[ft.TextButton("OK", on_click=close_success_dialog)],
                            )
                            self.page.overlay.append(success_dialog)
                            success_dialog.open = True
                            self.page.update()
                        else:
                            # Import avec erreurs - afficher le détail
                            error_text = "\\n".join(errors[:10])  # Limiter à 10 premières erreurs
                            if len(errors) > 10:
                                error_text += f"\\n... et {len(errors) - 10} autres erreurs"
                            
                            def close_dialog(e):
                                dialog.open = False
                                self.page.update()
                            
                            dialog = ft.AlertDialog(
                                modal=True,
                                title=ft.Text(f"[Attention] Import terminé : {imported_count} réussies, {error_count} erreurs", weight=ft.FontWeight.BOLD),
                                content=ft.Container(
                                    width=500,
                                    height=300,
                                    content=ft.Column([
                                        ft.Text(error_text, selectable=True, size=13),
                                    ], scroll=ft.ScrollMode.AUTO)
                                ),
                                actions=[ft.TextButton("OK", on_click=close_dialog)],
                            )
                            self.page.overlay.append(dialog)
                            dialog.open = True
                            self.page.update()
                        
                    except Exception as ex:
                        # Fermer le dialog de progression en cas d'erreur
                        progress_dialog.open = False
                        self.page.update()
                        
                        print(f"Erreur lecture Excel: {ex}")
                        create_snackbar(self.page, f"[Erreur] Erreur lors de la lecture: {str(ex)}", "error")
            
            # Créer et ouvrir le FilePicker
            file_picker = ft.FilePicker(on_result=on_file_result)
            self.page.overlay.append(file_picker)
            self.page.update()
            
            file_picker.pick_files(
                dialog_title="Sélectionner un fichier Excel",
                allowed_extensions=["xlsx", "xls"],
                allow_multiple=False
            )
            
        except Exception as ex:
            print(f"Erreur import Excel: {ex}")
            create_snackbar(self.page, f"[Erreur] Erreur import Excel: {str(ex)}", "error")
    
    def _export_chart_image(self, chart_container, chart_name):
        """Exporte un graphique en image PNG en utilisant matplotlib."""
        try:
            from datetime import datetime
            
            # Utiliser FilePicker pour choisir l'emplacement
            def on_file_result(e: ft.FilePickerResultEvent):
                if e.path:
                    try:
                        filepath = e.path
                        if not filepath.endswith('.png'):
                            filepath += '.png'
                        
                        print(f"Début export vers: {filepath}")
                        print(f"Type de graphique: {chart_name}")
                        
                        # Générer le graphique selon le type
                        if 'evolution_mensuelle' in chart_name:
                            self._generate_evolution_chart_image(filepath)
                        elif 'comparateur_annuel' in chart_name:
                            self._generate_comparateur_chart_image(filepath)
                        elif 'comparateur_par_type' in chart_name:
                            self._generate_comparateur_type_chart_image(filepath)
                        elif 'pareto_' in chart_name:
                            # Extraire le type de répartition pour le Pareto
                            repartition_type = chart_name.replace('pareto_', '')
                            self._generate_pareto_chart_image(filepath, repartition_type)
                        elif 'repartition_' in chart_name:
                            # Extraire le type de répartition
                            repartition_type = chart_name.replace('repartition_', '')
                            self._generate_repartition_chart_image(filepath, repartition_type)
                        else:
                            create_snackbar(self.page, "[Erreur] Type de graphique non supporté", "error")
                            return
                        
                        # Vérifier que le fichier a été créé
                        if os.path.exists(filepath):
                            file_size = os.path.getsize(filepath)
                            print(f"Fichier créé: {filepath} ({file_size} bytes)")
                            create_snackbar(self.page, f"[OK] Graphique exporté : {os.path.basename(filepath)} ({file_size//1024} Ko)", "success")
                        else:
                            print(f"ERREUR: Fichier non créé: {filepath}")
                            create_snackbar(self.page, "[Erreur] Le fichier n'a pas été créé", "error")
                            
                    except Exception as ex:
                        print(f"Erreur génération image: {ex}")
                        import traceback
                        traceback.print_exc()
                        create_snackbar(self.page, f"[Erreur] Erreur génération: {str(ex)}", "error")
                else:
                    print("FilePicker annulé - aucun chemin sélectionné")
            
            # Créer et ouvrir le FilePicker
            file_picker = ft.FilePicker(on_result=on_file_result)
            self.page.overlay.append(file_picker)
            self.page.update()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_picker.save_file(
                dialog_title="Enregistrer le graphique",
                file_name=f"{chart_name}_{timestamp}.png",
                allowed_extensions=["png"]
            )
            
        except Exception as ex:
            print(f"Erreur export image: {ex}")
            create_snackbar(self.page, f"[Erreur] Erreur export image: {str(ex)}", "error")
    
    def _generate_evolution_chart_image(self, filepath):
        """Génère l'image du graphique d'évolution mensuelle avec matplotlib."""
        print(f"[Evolution] Début génération vers: {filepath}")
        try:
            import matplotlib
            matplotlib.use('Agg')  # Backend non-interactif
            import matplotlib.pyplot as plt
            from datetime import datetime
            from collections import defaultdict
            
            print("[Evolution] Matplotlib importé")
            
            all_ncs = self.db.get_all_nc()
            current_year = datetime.now().year
            print(f"[Evolution] {len(all_ncs)} NC récupérées, année: {current_year}")
            
            # Collecter les données
            monthly_data = defaultdict(lambda: defaultdict(int))
            monthly_global = defaultdict(int)
            
            for nc in all_ncs:
                date_str = nc.get('date_detection', '')
                type_nc = nc.get('type_nc', 'Non défini')
                if date_str:
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                        if date.year == current_year:
                            month = date.month
                            monthly_data[type_nc][month] += 1
                            monthly_global[month] += 1
                    except:
                        pass
            
            # Créer le graphique
            fig, ax = plt.subplots(figsize=(12, 6))
            mois_labels = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jui', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            
            if self.stats_selected_type == "Tout":
                # Graphique empilé par type
                types_nc = list(monthly_data.keys())
                bottom = [0] * 12
                colors = {'Audit': '#9333EA', 'Client': '#1D4ED8', 'Fournisseur': '#EA580C', 
                         'Interne': '#16A34A', 'Prestataire': '#0D9488'}
                
                for type_nc in types_nc:
                    values = [monthly_data[type_nc].get(m, 0) for m in range(1, 13)]
                    ax.bar(mois_labels, values, bottom=bottom, label=type_nc, 
                          color=colors.get(type_nc, '#6B7280'))
                    bottom = [b + v for b, v in zip(bottom, values)]
                
                ax.legend(loc='upper left')
            else:
                # Graphique simple pour un type
                values = [monthly_data[self.stats_selected_type].get(m, 0) for m in range(1, 13)]
                colors = {'Audit': '#9333EA', 'Client': '#1D4ED8', 'Fournisseur': '#EA580C', 
                         'Interne': '#16A34A', 'Prestataire': '#0D9488'}
                ax.bar(mois_labels, values, color=colors.get(self.stats_selected_type, '#2563EB'))
            
            ax.set_title(f'Évolution Mensuelle des NC - {current_year}', fontsize=14, fontweight='bold')
            ax.set_xlabel('Mois')
            ax.set_ylabel('Nombre de NC')
            ax.grid(axis='y', alpha=0.3)
            
            print(f"[Evolution] Sauvegarde dans: {filepath}")
            plt.tight_layout()
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"[Evolution] Fichier sauvegardé avec succès")
            
        except ImportError as ie:
            print(f"[Evolution] ImportError: {ie}")
            create_snackbar(self.page, "[Erreur] Bibliothèque matplotlib non disponible", "error")
            raise
        except Exception as ex:
            print(f"[Evolution] Exception: {ex}")
            import traceback
            traceback.print_exc()
            raise ex
    
    def _generate_comparateur_chart_image(self, filepath):
        """Génère l'image du comparateur annuel avec matplotlib."""
        print(f"[Comparateur] Début génération vers: {filepath}")
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from datetime import datetime
            from collections import defaultdict
            import numpy as np
            
            all_ncs = self.db.get_all_nc()
            
            # Collecter les données par année
            yearly_data = defaultdict(lambda: defaultdict(int))
            for nc in all_ncs:
                date_str = nc.get('date_detection', '')
                if date_str:
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                        yearly_data[date.year][date.month] += 1
                    except:
                        pass
            
            # Créer le graphique
            fig, ax = plt.subplots(figsize=(14, 6))
            mois_labels = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jui', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            x = np.arange(len(mois_labels))
            
            colors_map = {2025: '#1D4ED8', 2024: '#EA580C', 2023: '#16A34A', 
                         2022: '#9333EA', 2021: '#0D9488', 2020: '#DC2626'}
            
            width = 0.15
            offset = 0
            
            # Calculer la valeur maximale pour dimensionner correctement
            all_bar_values = []
            for year in sorted(self.stats_years_selected):
                for m in range(1, 13):
                    value = yearly_data[year].get(m, 0)
                    all_bar_values.append(value)
            
            max_bar_value = max(all_bar_values) if all_bar_values else 0
            trend_space_ratio = 0.20
            trend_offset = max_bar_value * 0.10
            y_max_final = max_bar_value * (1 + trend_space_ratio + 0.10)
            
            ax.set_ylim(0, y_max_final)
            
            for year in sorted(self.stats_years_selected):
                values = [yearly_data[year].get(m, 0) for m in range(1, 13)]
                bars = ax.bar(x + offset, values, width, label=str(year), 
                      color=colors_map.get(year, '#6B7280'))
                
                # Afficher les valeurs
                for bar, value in zip(bars, values):
                    if value > 0:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width() / 2, height, str(int(value)),
                               ha='center', va='bottom', fontsize=9, fontweight='bold')
                
                offset += width
            
            # Ajouter les courbes de tendance si activées
            if hasattr(self, 'show_comparateur_annuel_trends') and self.show_comparateur_annuel_trends:
                # Ajouter les courbes de tendance
                month_colors = ['#EF4444', '#F59E0B', '#10B981', '#06B6D4', '#8B5CF6', '#EC4899',
                               '#F97316', '#84CC16', '#14B8A6', '#6366F1', '#A855F7', '#F43F5E']
                
                ax2 = ax.twinx()
                ax2.set_ylabel('')
                ax2.spines['right'].set_visible(False)
                ax2.set_yticks([])
                ax2.set_ylim(0, y_max_final)
                
                years_sorted = sorted(self.stats_years_selected)
                if len(years_sorted) >= 2:
                    for month_idx in range(12):
                        first_year_value = yearly_data[years_sorted[0]].get(month_idx + 1, 0)
                        last_year_value = yearly_data[years_sorted[-1]].get(month_idx + 1, 0)
                        
                        if first_year_value > 0 or last_year_value > 0:
                            color = month_colors[month_idx]
                            x_first = month_idx
                            x_last = month_idx + width * (len(years_sorted) - 1)
                            y_first = first_year_value + trend_offset
                            y_last = last_year_value + trend_offset
                            
                            ax2.plot([x_first, x_last], [y_first, y_last],
                                   linestyle='--', linewidth=1.5,
                                   color=color, alpha=0.7, zorder=10)
                            
                            ax2.plot([x_first, x_last], [y_first, y_last],
                                   marker='o', linestyle='none',
                                   markersize=4, color=color, alpha=0.9,
                                   markeredgecolor='white', markeredgewidth=1, zorder=11)
            
            ax.set_xticks(x + width * (len(self.stats_years_selected) - 1) / 2)
            ax.set_xticklabels(mois_labels)
            ax.set_title('Comparateur Annuel Multi-années avec Tendances', fontsize=14, fontweight='bold')
            ax.set_xlabel('Mois', fontsize=11)
            ax.set_ylabel('Nombre de NC', fontsize=11)
            ax.legend(fontsize=10, loc='upper left')
            ax.grid(axis='y', alpha=0.3)
            
            print(f"[Comparateur] Sauvegarde dans: {filepath}")
            plt.tight_layout()
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"[Comparateur] Fichier sauvegardé avec succès")
            
        except ImportError as ie:
            print(f"[Comparateur] ImportError: {ie}")
            create_snackbar(self.page, "[Erreur] Bibliothèque matplotlib non disponible", "error")
            raise
        except Exception as ex:
            print(f"[Comparateur] Exception: {ex}")
            import traceback
            traceback.print_exc()
            raise ex
    
    def _generate_comparateur_type_chart_image(self, filepath):
        """Génère l'image du comparateur par type avec matplotlib."""
        print(f"[Comparateur Type] Début génération vers: {filepath}")
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from datetime import datetime
            from collections import defaultdict
            import numpy as np
            
            all_ncs = self.db.get_all_nc()
            
            # Utiliser les années sélectionnées du comparateur type
            selected_years = sorted(self.stats_years_selected_type) if hasattr(self, 'stats_years_selected_type') else []
            if not selected_years:
                print("[Comparateur Type] Aucune année sélectionnée")
                return
            
            # Filtrer les NC par années sélectionnées
            year_strs = [str(y) for y in selected_years]
            filtered_ncs = [nc for nc in all_ncs if any(nc.get('date_detection', '').startswith(y) for y in year_strs)]
            
            # Types de NC possibles
            all_types_nc = ['Client', 'Fournisseur', 'Interne', 'Audit', 'Prestataire']
            
            # Collecter les données
            yearly_type_data = defaultdict(lambda: defaultdict(int))
            for nc in filtered_ncs:
                date_str = nc.get('date_detection', '')
                type_nc = nc.get('type_nc', '')
                if date_str and type_nc in all_types_nc:
                    try:
                        parts = date_str.split('-')
                        year = int(parts[0])
                        if year in selected_years:
                            yearly_type_data[year][type_nc] += 1
                    except:
                        pass
            
            # Filtrer les types qui ont au moins une donnée
            types_nc = []
            for type_nc in all_types_nc:
                has_data = any(yearly_type_data[year].get(type_nc, 0) > 0 for year in selected_years)
                if has_data:
                    types_nc.append(type_nc)
            
            if not types_nc:
                print("[Comparateur Type] Aucune donnée à exporter")
                return
            
            # Créer le graphique avec taille optimisée pour export
            fig, ax = plt.subplots(figsize=(12, 6))
            
            x = np.arange(len(types_nc))
            colors_map = {2025: '#1D4ED8', 2024: '#EA580C', 2023: '#16A34A', 
                         2022: '#9333EA', 2021: '#0D9488', 2020: '#DC2626'}
            
            width = 0.15
            offset = 0
            
            # Calculer la valeur maximale de TOUTES les barres pour dimensionner correctement
            all_bar_values = []
            for type_nc in types_nc:
                for year in sorted(selected_years):
                    value = yearly_type_data[year].get(type_nc, 0)
                    all_bar_values.append(value)
            
            max_bar_value = max(all_bar_values) if all_bar_values else 0
            trend_space_ratio = 0.20
            trend_offset = max_bar_value * 0.10
            y_max_final = max_bar_value * (1 + trend_space_ratio + 0.10)
            
            # Appliquer les limites Y
            ax.set_ylim(0, y_max_final)
            
            for year in sorted(selected_years):
                values = [yearly_type_data[year].get(type_nc, 0) for type_nc in types_nc]
                bars = ax.bar(x + offset, values, width, label=str(year), 
                      color=colors_map.get(year, '#6B7280'))
                
                # Afficher les valeurs
                for bar, value in zip(bars, values):
                    if value > 0:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width() / 2, height, str(int(value)),
                               ha='center', va='bottom', fontsize=10, fontweight='bold')
                
                offset += width
            
            # Ajouter les courbes de tendance si activées
            if hasattr(self, 'show_comparateur_type_trends') and self.show_comparateur_type_trends:
                # Ajouter les courbes de tendance
                type_colors_map = {
                    'Client': '#EF4444',
                    'Fournisseur': '#F59E0B', 
                    'Interne': '#10B981',
                    'Audit': '#8B5CF6',
                    'Prestataire': '#06B6D4'
                }
                
                ax2 = ax.twinx()
                ax2.set_ylabel('')
                ax2.spines['right'].set_visible(False)
                ax2.set_yticks([])
                ax2.set_ylim(0, y_max_final)
                
                for i, type_nc in enumerate(types_nc):
                    years_sorted = sorted(selected_years)
                    first_year_value = yearly_type_data[years_sorted[0]].get(type_nc, 0)
                    last_year_value = yearly_type_data[years_sorted[-1]].get(type_nc, 0)
                    
                    if len(selected_years) >= 2 and (first_year_value > 0 or last_year_value > 0):
                        color = type_colors_map.get(type_nc, '#6B7280')
                        x_first = i
                        x_last = i + width * (len(selected_years) - 1)
                        y_first = first_year_value + trend_offset
                        y_last = last_year_value + trend_offset
                        
                        if y_last > y_first:
                            trend_arrow = '^'
                        elif y_last < y_first:
                            trend_arrow = 'v'
                        else:
                            trend_arrow = '>'
                        
                        ax2.plot([x_first, x_last], [y_first, y_last], 
                               linestyle='--', linewidth=2.5, 
                               color=color, alpha=0.85,
                               label=f'{trend_arrow} {type_nc}', zorder=10)
                        
                        ax2.plot([x_first, x_last], [y_first, y_last], 
                               marker='o', linestyle='none',
                               markersize=7, color=color, alpha=0.95,
                               markeredgecolor='white', markeredgewidth=1.5, zorder=11)
                
                # Combiner les légendes
                handles1, labels1 = ax.get_legend_handles_labels()
                handles2, labels2 = ax2.get_legend_handles_labels()
                ax.legend(handles1 + handles2, labels1 + labels2, fontsize=10, loc='upper left', ncol=2)
            else:
                # Pas de tendances, légende simple
                ax.legend(fontsize=11, loc='upper left')
            
            ax.set_xticks(x + width * (len(selected_years) - 1) / 2)
            ax.set_xticklabels(types_nc, fontsize=11)
            ax.set_ylabel('Nombre de NC', fontsize=12)
            ax.set_title('Comparateur par Type NC Multi-années avec Tendances', fontsize=14, fontweight='bold')
            
            ax.grid(axis='y', alpha=0.3)
            
            print(f"[Comparateur Type] Sauvegarde dans: {filepath}")
            plt.tight_layout()
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"[Comparateur Type] Fichier sauvegardé avec succès")
            
        except ImportError as ie:
            print(f"[Comparateur Type] ImportError: {ie}")
            create_snackbar(self.page, "[Erreur] Bibliothèque matplotlib non disponible", "error")
            raise
        except Exception as ex:
            print(f"[Comparateur Type] Exception: {ex}")
            import traceback
            traceback.print_exc()
            raise ex
    
    def _generate_repartition_chart_image(self, filepath, repartition_type):
        """Génère l'image d'un graphique de répartition avec matplotlib."""
        print(f"[Répartition] Début génération {repartition_type} vers: {filepath}")
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from datetime import datetime, timedelta
            from collections import defaultdict
            
            all_ncs = self.db.get_all_nc()
            
            # Mapper les types aux champs de données
            field_map = {
                'imputation': 'imputation',
                'anomalie': 'type_anomalie',
                'categorie': 'categorie_nc',
                'gravite': 'gravite',
                'matieres': 'matieres_reclames'
            }
            
            title_map = {
                'imputation': 'Répartition par Imputation',
                'anomalie': 'Répartition par Anomalie',
                'categorie': 'Répartition par Catégorie',
                'gravite': 'Répartition par Gravité',
                'matieres': 'Répartition par Matières Réclamées'
            }
            
            field_name = field_map.get(repartition_type, 'imputation')
            title = title_map.get(repartition_type, 'Répartition')
            
            # Filtrer par date
            date_debut, date_fin = self.stats_zone_b_dates.get(repartition_type, 
                (datetime.now().date() - timedelta(days=30), datetime.now().date()))
            
            filtered_ncs = []
            for nc in all_ncs:
                date_str = nc.get('date_detection', '')
                if date_str:
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        if date_debut <= date <= date_fin:
                            filtered_ncs.append(nc)
                    except:
                        pass
            
            # Collecter les données
            data_dict = defaultdict(int)
            for nc in filtered_ncs:
                value = nc.get(field_name, 'Non défini')
                if value:
                    data_dict[value] += 1
            
            # Créer le graphique
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Trier et appliquer la limite configurée
            sorted_data = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)
            # Récupérer la limite pour ce graphique
            top_limit = self.stats_zone_b_top_limit.get(repartition_type, "Tout")
            if top_limit != "Tout":
                sorted_data = sorted_data[:int(top_limit)]
            
            labels = [item[0] for item in sorted_data]
            values = [item[1] for item in sorted_data]
            
            colors = plt.cm.Set3(range(len(labels)))
            ax.barh(labels, values, color=colors)
            
            ax.set_title(f'{title}\n({date_debut} à {date_fin})', fontsize=12, fontweight='bold')
            ax.set_xlabel('Nombre de NC')
            ax.grid(axis='x', alpha=0.3)
            
            # Ajouter les valeurs
            for i, v in enumerate(values):
                ax.text(v, i, f' {v}', va='center')
            
            print(f"[Répartition] Sauvegarde dans: {filepath}")
            plt.tight_layout()
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"[Répartition] Fichier sauvegardé avec succès")
            
        except ImportError as ie:
            print(f"[Répartition] ImportError: {ie}")
            create_snackbar(self.page, "[Erreur] Bibliothèque matplotlib non disponible", "error")
            raise
        except Exception as ex:
            print(f"[Répartition] Exception: {ex}")
            import traceback
            traceback.print_exc()
            raise ex
    
    def _generate_pareto_chart_image(self, filepath, repartition_type):
        """Génère l'image d'un graphique de Pareto avec matplotlib."""
        print(f"[Pareto] Début génération {repartition_type} vers: {filepath}")
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from datetime import datetime, timedelta
            from collections import defaultdict
            import numpy as np
            
            all_ncs = self.db.get_all_nc()
            
            # Mapper les types aux champs de données
            field_map = {
                'imputation': 'imputation',
                'anomalie': 'type_anomalie',
                'categorie': 'categorie_nc',
                'gravite': 'gravite',
                'matieres': 'matieres_reclames'
            }
            
            title_map = {
                'imputation': 'Répartition par Imputation',
                'anomalie': 'Répartition par Anomalie',
                'categorie': 'Répartition par Catégorie',
                'gravite': 'Répartition par Gravité',
                'matieres': 'Répartition par Matières Réclamées'
            }
            
            color_map = {
                'imputation': '#1976D2',
                'anomalie': '#F57C00',
                'categorie': '#388E3C',
                'gravite': '#D32F2F',
                'matieres': '#7B1FA2'
            }
            
            field_name = field_map.get(repartition_type, 'imputation')
            title = title_map.get(repartition_type, 'Répartition')
            color_hex = color_map.get(repartition_type, '#1976D2')
            
            # Filtrer par date
            date_debut, date_fin = self.stats_zone_b_dates.get(repartition_type, 
                (datetime.now().date() - timedelta(days=30), datetime.now().date()))
            
            filtered_ncs = []
            for nc in all_ncs:
                date_str = nc.get('date_detection', '')
                if date_str:
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        if date_debut <= date <= date_fin:
                            filtered_ncs.append(nc)
                    except:
                        pass
            
            # Collecter les données
            data_dict = defaultdict(int)
            for nc in filtered_ncs:
                value = nc.get(field_name, 'Non défini')
                if value:
                    data_dict[value] += 1
            
            # Trier par ordre décroissant
            sorted_data = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)
            labels = [item[0][:25] for item in sorted_data]
            values = [item[1] for item in sorted_data]
            
            # Calculer les pourcentages cumulés
            total = sum(values)
            cumul_percent = np.cumsum([v/total*100 for v in values]) if total > 0 else []
            
            # Créer la figure avec deux axes Y (hauteur augmentée pour export haute qualité)
            fig, ax1 = plt.subplots(figsize=(12, 8))
            
            # Barres (axe gauche)
            x_pos = np.arange(len(labels))
            bars = ax1.bar(x_pos, values, color=color_hex, alpha=0.7)
            ax1.set_xlabel('Valeurs', fontsize=11)
            ax1.set_ylabel('Nombre de NC', fontsize=12)
            ax1.tick_params(axis='x', rotation=45)
            ax1.set_xticks(x_pos)
            ax1.set_xticklabels(labels, ha='right')
            
            # Ligne cumulative (axe droit)
            ax2 = ax1.twinx()
            ax2.plot(x_pos, cumul_percent, color='#FF4444', marker='o', 
                    linewidth=2, markersize=5)
            ax2.set_ylabel('% Cumulé', fontsize=12)
            ax2.set_ylim([0, 105])
            
            # Ligne horizontale à 80%
            ax2.axhline(y=80, color='#FFD700', linestyle='--', linewidth=2, alpha=0.9)
            
            # Zone ombrée
            if len(cumul_percent) > 0:
                idx_80 = next((i for i, cp in enumerate(cumul_percent) if cp >= 80), len(cumul_percent))
                total_values = len(labels)  # Nombre total de valeurs
                if idx_80 < len(cumul_percent):
                    ax1.axvspan(-0.5, idx_80 + 0.5, alpha=0.2, color='#00FF00')
                    ax1.axvspan(idx_80 + 0.5, len(labels) - 0.5, alpha=0.15, color='#FF6B6B')
                    ax1.text(idx_80 / 2, max(values) * 0.95, 
                            f'< {idx_80 + 1} valeurs sur {total_values} = 80% des NC',
                            fontsize=11, fontweight='bold',
                            ha='center', bbox=dict(boxstyle='round,pad=0.5', 
                            facecolor='white', edgecolor='#00FF00', linewidth=2))
            
            ax1.set_title(f'Pareto: {title} ({date_debut} à {date_fin})', 
                         fontsize=14, fontweight='bold', pad=20)
            ax1.grid(axis='y', alpha=0.3)
            
            print(f"[Pareto] Sauvegarde dans: {filepath}")
            plt.subplots_adjust(top=0.85, bottom=0.12, left=0.1, right=0.9)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"[Pareto] Fichier sauvegardé avec succès")
            
        except Exception as ex:
            print(f"[Pareto] Exception: {ex}")
            import traceback
            traceback.print_exc()
            raise ex

    def did_mount(self):
        """Hook Flet appelé quand le control est monté; on prépare les DatePickers et le préchargement."""
        self._ensure_filter_date_pickers()
        # Lancer le préchargement en arrière-plan après 0.5s (une seule fois)
        if not self._preload_started:
            self._preload_started = True
            import threading
            threading.Timer(0.5, self._preload_heavy_tabs).start()
    
    def _preload_heavy_tabs(self):
        """Précharge les onglets lourds en arrière-plan pour une ouverture instantanée."""
        import time
        import threading
        
        def preload_tab(tab_index, tab_name):
            """Précharge un onglet spécifique."""
            try:
                print(f"[PRELOAD] Début préchargement {tab_name}...")
                
                if tab_index == 1:  # Liste NC
                    self._tabs_cache[1] = self._build_list_tab()
                elif tab_index == 5:  # Statistiques
                    self._tabs_cache[5] = self._build_statistics_tab()
                elif tab_index == 3:  # Analyse
                    self._tabs_cache[3] = self._build_analysis_tab()
                
                print(f"[PRELOAD] [OK] {tab_name} préchargé")
            except Exception as ex:
                print(f"[PRELOAD] Erreur {tab_name}: {ex}")
        
        # Précharger dans l'ordre de priorité avec délais
        # 1. Liste NC (le plus utilisé)
        preload_tab(1, "Liste NC")
        time.sleep(0.8)  # Pause entre chaque
        
        # 2. Statistiques (graphiques lourds)
        preload_tab(5, "Statistiques")
        time.sleep(0.8)
        
        # 3. Analyse (tableaux complexes)
        preload_tab(3, "Analyse")
        
        print("[PRELOAD] [OK] Tous les onglets préchargés")
    
    def _on_tab_change(self, e):
        """Change de tab avec lazy loading optimisé."""
        self.current_tab = e.control.selected_index
        
        # Réinitialiser la sélection lors du changement d'onglet
        self.selected_nc_ids.clear()
        if hasattr(self, 'delete_multiple_btn'):
            self._update_delete_multiple_button()
        
        # Lazy loading: ne construire que si pas déjà en cache
        # Exceptions: onglets 0 (Tableau de bord), 1 (Liste NC), 2 (Détail) et 4 (Suivi) toujours reconstruits pour données à jour
        if self.current_tab not in self._tabs_cache or self.current_tab in [0, 1, 2, 4]:
            if self.current_tab == 0:
                # Toujours reconstruire le tableau de bord pour données à jour
                self._tabs_cache[0] = self._build_dashboard_tab()
            elif self.current_tab == 1:
                # Vérifier si la largeur actuelle nécessite un mode différent
                current_width = self.page.window_width if self.page and hasattr(self.page, 'window_width') else 1920
                should_be_compact = current_width < self._responsive_threshold
                
                # Si on a préchargé avec une mauvaise largeur, forcer la reconstruction
                if self._last_window_width and abs(current_width - self._last_window_width) > 100:
                    print(f"[RESPONSIVE] Correction détectée: préchargé à {self._last_window_width}px, réel à {current_width}px")
                    self._last_window_width = current_width
                
                # Toujours reconstruire la liste NC pour afficher les modifications
                self._tabs_cache[1] = self._build_list_tab()
            elif self.current_tab == 2:
                # Toujours reconstruire le détail pour éviter les états figés
                self._tabs_cache[2] = self._build_detail_tab()
            elif self.current_tab == 3:
                self._tabs_cache[3] = self._build_analysis_tab()
            elif self.current_tab == 4:
                # Toujours reconstruire pour avoir les dernières données
                self._tabs_cache[4] = self._build_suivi_actions_tab()
            elif self.current_tab == 5:
                self._tabs_cache[5] = self._build_statistics_tab()
        
        # Mise à jour unique du contenu
        self.tab_content.content = self._tabs_cache[self.current_tab]
        if self.page:
            self.page.update()

    def _on_window_resize(self, e=None):
        """Gère le redimensionnement de la fenêtre pour le mode responsive."""
        try:
            if not self.page or not hasattr(self.page, 'window_width'):
                return
            
            current_width = self.page.window_width
            
            # Ne rien faire si la largeur n'a pas changé significativement
            if self._last_window_width and abs(current_width - self._last_window_width) < 50:
                return
            
            # Vérifier si on traverse le seuil responsive
            was_small = self._last_window_width and self._last_window_width < self._responsive_threshold
            is_small = current_width < self._responsive_threshold
            
            print(f"[RESPONSIVE] Redimensionnement: {self._last_window_width}px > {current_width}px (Seuil: {self._responsive_threshold}px)")
            
            # Reconstruire uniquement si on change de mode (petit <> grand écran)
            if self._last_window_width and was_small != is_small:
                print(f"[RESPONSIVE] Changement de mode détecté - Reconstruction des tableaux")
                # Invalider le cache de la liste NC et du Suivi Actions
                if 1 in self._tabs_cache:
                    del self._tabs_cache[1]
                if 4 in self._tabs_cache:
                    del self._tabs_cache[4]
                
                # Si on est sur l'onglet Liste NC, reconstruire immédiatement
                if self.current_tab == 1:
                    self.tab_content.content = self._build_list_tab()
                    self._tabs_cache[1] = self.tab_content.content
                    if self.page:
                        self.page.update()
                
                # Si on est sur l'onglet Suivi Actions, reconstruire immédiatement
                if self.current_tab == 4:
                    self.tab_content.content = self._build_suivi_actions_tab()
                    self._tabs_cache[4] = self.tab_content.content
                    if self.page:
                        self.page.update()
            
            self._last_window_width = current_width
            
        except Exception as ex:
            print(f"[RESPONSIVE] Erreur lors du redimensionnement: {ex}")

    def _handle_keyboard_event(self, e: ft.KeyboardEvent):
        """Gère les événements clavier (raccourcis)."""
        try:
            print(f"[KEYBOARD] Événement: key={e.key}, ctrl={e.ctrl}, alt={e.alt}, shift={e.shift}, meta={e.meta}")
            
            # Ignorer les événements de type KEY_UP
            if e.key == "Key Up":
                return
            
            # Ctrl+N : Nouvelle NC
            if e.ctrl and e.key.lower() == "n":
                print("[KEYBOARD] Ctrl+N détecté - Ouverture formulaire")
                if not self.show_form:
                    self._open_form()
                    if self.page:
                        self.page.update()
                return
            
            # Ctrl+S : Sauvegarder (si formulaire ouvert)
            if e.ctrl and e.key.lower() == "s":
                print("[KEYBOARD] Ctrl+S détecté - Sauvegarde")
                if self.show_form and hasattr(self, '_save_form'):
                    self._save_form(None)
                    if self.page:
                        self.page.update()
                return
            
            # Ctrl+E : Export PDF (si détail NC ouvert dans formulaire OU onglet Détail)
            if e.ctrl and e.key.lower() == "e":
                print("[KEYBOARD] Ctrl+E détecté - Export PDF")
                nc_to_export = None
                
                # Cas 1 : Formulaire ouvert avec NC en édition
                if self.show_form and self.editing_nc:
                    nc_to_export = self.editing_nc
                    print("[KEYBOARD] Export depuis formulaire")
                
                # Cas 2 : Onglet Détail (tab 2) avec NC sélectionnée
                elif not self.show_form and self.current_tab == 2 and self.current_nc_id:
                    nc_to_export = self.db.get_nc(self.current_nc_id)
                    print("[KEYBOARD] Export depuis onglet Détail")
                
                if nc_to_export:
                    self._export_nc_to_pdf(nc_to_export)
                    if self.page:
                        self.page.update()
                else:
                    print("[KEYBOARD] Aucune NC à exporter")
                return
            
            # Ctrl+F : Focus sur la recherche
            if e.ctrl and e.key.lower() == "f":
                print("[KEYBOARD] Ctrl+F détecté - Focus recherche")
                if not self.show_form and hasattr(self, '_search_filter_field') and self._search_filter_field:
                    try:
                        self._search_filter_field.focus()
                        if self.page:
                            self.page.update()
                    except Exception as ex:
                        print(f"[KEYBOARD] Erreur focus recherche: {ex}")
                return
            
            # F5 : Rafraîchir
            if e.key == "F5":
                print("[KEYBOARD] F5 détecté - Rafraîchir")
                if not self.show_form:
                    self._refresh_nc_cache()
                    self._tabs_cache.clear()
                    self.tab_content.content = self._get_current_tab_content()
                    if self.page:
                        create_snackbar(self.page, "[Actualiser] Liste rafraîchie", "info")
                        self.page.update()
                return
            
            # Échap : Fermer le formulaire ou annuler
            if e.key == "Escape":
                print("[KEYBOARD] Échap détecté - Fermer formulaire")
                if self.show_form:
                    self._close_form()
                    if self.page:
                        self.page.update()
                return
            
            # Flèche gauche/droite : Navigation entre NC (si formulaire ouvert)
            if e.key == "Arrow Left" or e.key == "Arrow Right":
                print(f"[KEYBOARD] {e.key} détecté - Navigation NC")
                if self.show_form and self.editing_nc:
                    all_ncs = self._get_filtered_ncs()
                    if not all_ncs:
                        return
                    
                    current_id = self.editing_nc.get('id')
                    current_index = next((i for i, nc in enumerate(all_ncs) if nc['id'] == current_id), -1)
                    
                    if current_index != -1:
                        if e.key == "Arrow Left" and current_index > 0:
                            # NC précédente
                            prev_nc = all_ncs[current_index - 1]
                            self._open_form(prev_nc)
                            if self.page:
                                self.page.update()
                        elif e.key == "Arrow Right" and current_index < len(all_ncs) - 1:
                            # NC suivante
                            next_nc = all_ncs[current_index + 1]
                            self._open_form(next_nc)
                            if self.page:
                                self.page.update()
                return
            
            # Ctrl+H : Afficher l'aide des raccourcis
            if e.ctrl and e.key.lower() == "h":
                print("[KEYBOARD] Ctrl+H détecté - Aide raccourcis")
                self._show_keyboard_shortcuts_help()
                return
                
        except Exception as ex:
            print(f"[KEYBOARD] Erreur gestion raccourci: {ex}")
    
    def _show_keyboard_shortcuts_help(self):
        """Affiche une boîte de dialogue avec l'aide des raccourcis clavier."""
        shortcuts = [
            ("Ctrl+N", "Créer une nouvelle NC"),
            ("Ctrl+S", "Sauvegarder le formulaire"),
            ("Ctrl+E", "Exporter en PDF (depuis le détail)"),
            ("Ctrl+F", "Focus sur la recherche"),
            ("F5", "Rafraîchir la liste"),
            ("Échap", "Fermer le formulaire"),
            ("< >", "Naviguer entre les NC (dans le formulaire)"),
            ("Ctrl+H", "Afficher cette aide"),
        ]
        
        def close_dlg(e):
            dlg.open = False
            if self.page:
                self.page.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.KEYBOARD, color=Theme.PRIMARY),
                    ft.Text(" Raccourcis clavier", weight=ft.FontWeight.BOLD, size=18),
                ]
            ),
            content=ft.Container(
                width=500,
                padding=10,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        ft.Text(
                            "Utilisez ces raccourcis pour gagner du temps :",
                            size=13,
                            color=Theme.TEXT_MUTED,
                        ),
                        ft.Divider(height=1, color=Theme.OUTLINE),
                        *[
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                                        border_radius=4,
                                        bgcolor=Theme.BG_TERTIARY,
                                        border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                                        content=ft.Text(
                                            shortcut,
                                            size=13,
                                            weight=ft.FontWeight.BOLD,
                                            color=Theme.PRIMARY,
                                        ),
                                    ),
                                    ft.Container(width=20),
                                    ft.Text(description, size=13, color=Theme.TEXT_PRIMARY),
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            )
                            for shortcut, description in shortcuts
                        ],
                    ],
                ),
            ),
            actions=[
                ft.TextButton(
                    "Fermer",
                    on_click=close_dlg,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=Theme.PRIMARY,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        if self.page:
            self.page.overlay.append(dlg)
            dlg.open = True
            self.page.update()

    def _go_to_list_tab(self):
        """Revient sur la liste des NC de manière optimisée."""
        self.tabs.selected_index = 1
        self.current_tab = 1
        # Invalider le cache pour forcer le refresh
        if 1 in self._tabs_cache:
            del self._tabs_cache[1]
        self.tab_content.content = self._build_list_tab()
        self._tabs_cache[1] = self.tab_content.content
        self.page.update()
    
    # ========================================================================
    # TAB 1: LISTE DES NC
    # ========================================================================
    
    def _get_nc_list(self, force_refresh=False):
        """Récupère la liste des NC avec pagination et filtres SQL optimisés."""
        # Construire les filtres pour la requête DB
        filters = {}
        if self.filter_status != "Tous":
            filters['statut'] = self.filter_status
        if self.filter_gravite != "Tous":
            filters['gravite'] = self.filter_gravite
        if self.filter_type != "Tous":
            filters['type_nc'] = self.filter_type
        if self.filter_origine != "Tous":
            filters['origine'] = self.filter_origine
        if self.filter_categorie != "Tous":
            filters['categorie_nc'] = self.filter_categorie
        if self.filter_imputation != "Tous":
            filters['imputation'] = self.filter_imputation
        if self.filter_date_start:
            filters['date_start'] = self.filter_date_start
        if self.filter_date_end:
            filters['date_end'] = self.filter_date_end
        if self.filter_search:
            filters['search'] = self.filter_search
        
        # Obtenir le compte total avec les filtres
        self.total_nc_count = self.db.get_all_nc(filters=filters, count_only=True)
        
        # Calculer l'offset
        offset = (self.current_page - 1) * self.items_per_page
        
        # Récupérer la page actuelle
        return self.db.get_all_nc(filters=filters, limit=self.items_per_page, offset=offset)
    
    def _refresh_nc_cache(self):
        """Force le rechargement du cache des NC."""
        self._nc_cache = None
        self.current_page = 1  # Reset à la première page
        # Invalider aussi le cache d'analyse
        if hasattr(self, '_analysis_nc_cache'):
            self._analysis_nc_cache = None
        # Réinitialiser la sélection lors du rafraîchissement
        self.selected_nc_ids.clear()
        # Ne mettre à jour le bouton que si on n'est pas dans le formulaire
        if not self.show_form and hasattr(self, 'delete_multiple_btn'):
            self._update_delete_multiple_button()
    
    def _save_filters_preferences(self):
        """Sauvegarde les filtres actuels dans les préférences utilisateur."""
        filters = {
            'status': self.filter_status,
            'gravite': self.filter_gravite,
            'type': self.filter_type,
            'search': self.filter_search,
            'origine': self.filter_origine,
            'categorie': self.filter_categorie,
            'imputation': self.filter_imputation,
            'date_start': self.filter_date_start,
            'date_end': self.filter_date_end,
        }
        self.db.save_user_preference(self.user['id'], 'nc', 'filters', filters)
    
    def _reset_filters(self):
        """Réinitialise tous les filtres aux valeurs par défaut."""
        self.filter_status = "Tous"
        self.filter_gravite = "Tous"
        self.filter_type = "Tous"
        self.filter_search = ""
        self.filter_origine = "Tous"
        self.filter_categorie = "Tous"
        self.filter_imputation = "Tous"
        self.filter_date_start = ""
        self.filter_date_end = ""
        
        # Sauvegarder les filtres réinitialisés
        self._save_filters_preferences()
        
        # Rafraîchir la liste
        self._refresh_nc_cache()
        self._tabs_cache.clear()
        if not self.show_form and self.current_tab == 1:
            self.tab_content.content = self._build_list_tab()
            if self.page:
                create_snackbar(self.page, "[Actualiser] Filtres réinitialisés", "success")
                self.page.update()
    
    def _build_list_tab(self):
        """Construit la liste des NC avec pagination."""
        ncs = self._get_nc_list()
        
        # Préparer les listes déroulantes dynamiques
        TYPE_NC_CHOICES = ["Interne", "Client", "Fournisseur", "Prestataire", "Audit"]
        origins = sorted({(nc.get('origine') or '').strip() for nc in ncs if (nc.get('origine') or '').strip()})
        categories = sorted({(nc.get('categorie_nc') or '').strip() for nc in ncs if (nc.get('categorie_nc') or '').strip()})
        imputation_choices = ["Tous"] + [
            "Expédition", "Dégorgement", "QSE", "Cuverie", "Tirage", "Fournisseur",
            "Transport", "Indéterminée", "Ordonnancement", "Espaces ventes",
            "Prestataire", "Habillage", "WLS", "Caves"
        ]
        origin_options = ["Tous"] + origins
        category_options = ["Tous"] + categories
        
        # DatePickers pour filtres
        self._ensure_filter_date_pickers()
        
        # Filtres dans une carte stylisée
        filters = ft.Container(
            padding=20,
            margin=15,
            bgcolor=Theme.BG_SECONDARY,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            content=ft.Column(
                spacing=15,
                controls=[
                    # Titre de la section filtres
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.FILTER_ALT_ROUNDED, size=24, color=Theme.PRIMARY),
                            ft.Text(
                                "Filtres de recherche",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.TEXT_PRIMARY,
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color=Theme.OUTLINE),
                    # Ligne 1 - Filtres principaux
                    ft.Row(
                        wrap=True,
                        spacing=12,
                        run_spacing=10,
                        controls=[
                            create_dropdown(
                                "Statut",
                                ["Tous", "En cours", "Clôturée"],
                                value=self.filter_status,
                                on_change=lambda e: self._apply_filter('status', e.control.value),
                                width=200,
                            ),
                            create_dropdown(
                                "Gravité",
                                ["Tous", "Mineure", "Majeure", "Critique"],
                                value=self.filter_gravite,
                                on_change=lambda e: self._apply_filter('gravite', e.control.value),
                                width=180,
                            ),
                            create_dropdown(
                                "Type NC",
                                ["Tous"] + TYPE_NC_CHOICES,
                                value=self.filter_type,
                                on_change=lambda e: self._apply_filter('type', e.control.value),
                                width=180,
                            ),
                            create_dropdown(
                                "Origine",
                                origin_options,
                                value=self.filter_origine if self.filter_origine in origin_options else "Tous",
                                on_change=lambda e: self._apply_filter('origine', e.control.value),
                                width=180,
                            ),
                            create_dropdown(
                                "Catégorie",
                                category_options,
                                value=self.filter_categorie if self.filter_categorie in category_options else "Tous",
                                on_change=lambda e: self._apply_filter('categorie', e.control.value),
                                width=180,
                            ),
                            create_dropdown(
                                "Imputation",
                                imputation_choices,
                                value=self.filter_imputation if self.filter_imputation in imputation_choices else "Tous",
                                on_change=lambda e: self._apply_filter('imputation', e.control.value),
                                width=180,
                            ),
                            self._build_search_field(),
                        ],
                    ),
                    # Ligne 2 - Filtres de dates
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Row(
                                spacing=4,
                                controls=[
                                    ft.TextField(
                                        label="Date début (AAAA-MM-JJ)",
                                        value=self.filter_date_start,
                                        hint_text="2025-01-15",
                                        width=180,
                                        text_size=13,
                                        height=48,
                                        read_only=True,
                                        bgcolor=Theme.BG_PRIMARY,
                                        border_color=Theme.OUTLINE,
                                        focused_border_color=Theme.PRIMARY,
                                        suffix=ft.IconButton(
                                            icon=ft.Icons.CALENDAR_TODAY,
                                            icon_size=18,
                                            tooltip="Ouvrir le calendrier",
                                            on_click=lambda e: self._open_custom_calendar('date_start', self.filter_date_start),
                                        ),
                                    ),
                                    ft.IconButton(
                                        ft.Icons.CANCEL_OUTLINED,
                                        icon_size=18,
                                        icon_color=Theme.TEXT_MUTED,
                                        tooltip="Réinitialiser date début",
                                        on_click=lambda e: self._apply_filter('date_start', ''),
                                    ),
                                ],
                            ),
                            ft.Row(
                                spacing=4,
                                controls=[
                                    ft.TextField(
                                        label="Date fin (AAAA-MM-JJ)",
                                        value=self.filter_date_end,
                                        hint_text="2025-12-31",
                                        width=180,
                                        text_size=13,
                                        height=48,
                                        read_only=True,
                                        bgcolor=Theme.BG_PRIMARY,
                                        border_color=Theme.OUTLINE,
                                        focused_border_color=Theme.PRIMARY,
                                        suffix=ft.IconButton(
                                            icon=ft.Icons.CALENDAR_TODAY,
                                            icon_size=18,
                                            tooltip="Ouvrir le calendrier",
                                            on_click=lambda e: self._open_custom_calendar('date_end', self.filter_date_end),
                                        ),
                                    ),
                                    ft.IconButton(
                                        ft.Icons.CANCEL_OUTLINED,
                                        icon_size=18,
                                        icon_color=Theme.TEXT_MUTED,
                                        tooltip="Réinitialiser date fin",
                                        on_click=lambda e: self._apply_filter('date_end', ''),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Ligne 3 - Boutons d'action (Export et Import)
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.ElevatedButton(
                                "Réinitialiser filtres",
                                icon=ft.Icons.REFRESH,
                                on_click=lambda e: self._reset_filters(),
                                style=ft.ButtonStyle(
                                    bgcolor=Theme.WARNING,
                                    color=ft.Colors.WHITE,
                                ),
                                height=36,
                            ),
                            ft.Container(width=20),  # Séparateur
                            ft.Text(
                                "Export :",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.TEXT_PRIMARY,
                            ),
                            ft.ElevatedButton(
                                "Excel",
                                icon=ft.Icons.TABLE_CHART,
                                on_click=self._export_to_excel,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.GREEN_700,
                                    color=ft.Colors.WHITE,
                                ),
                                height=36,
                            ),
                            ft.ElevatedButton(
                                "PDF",
                                icon=ft.Icons.PICTURE_AS_PDF,
                                on_click=self._export_to_pdf,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.RED_700,
                                    color=ft.Colors.WHITE,
                                ),
                                height=36,
                            ),
                            ft.ElevatedButton(
                                "CSV",
                                icon=ft.Icons.INSERT_DRIVE_FILE,
                                on_click=self._export_to_csv,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.BLUE_700,
                                    color=ft.Colors.WHITE,
                                ),
                                height=36,
                            ),
                            ft.Container(width=20),  # Séparateur
                            ft.Text(
                                "Import :",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.TEXT_PRIMARY,
                            ),
                            ft.ElevatedButton(
                                "Depuis Excel",
                                icon=ft.Icons.UPLOAD_FILE,
                                on_click=self._import_from_excel,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.ORANGE_700,
                                    color=ft.Colors.WHITE,
                                ),
                                height=36,
                            ),
                        ],
                    ),
                ],
            ),
        )
        
        # Plus de filtrage côté Python - tout se fait dans la DB maintenant
        filtered_ncs = ncs  # Les filtres sont déjà appliqués dans la requête SQL
        
        if not filtered_ncs:
            return ft.Column(
                controls=[
                    filters,
                    ft.Container(height=20),
                    create_empty_state(
                        ft.Icons.CHECK_CIRCLE,
                        "Aucune NC trouvée",
                        "Modifiez vos filtres ou créez une nouvelle NC",
                        "Nouvelle NC",
                        lambda e: self._open_form(),
                    ),
                ]
            )
        
        # Tableau des NC (aligné sur la liste principale)
        def wrap_text(text, max_chars=100):
            """Découpe le texte en lignes de max_chars caractères max."""
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
        
        # Détecter la largeur de l'écran pour mode responsive
        # Essayer plusieurs méthodes de détection
        try:
            # Tenter plusieurs sources de largeur
            width_sources = []
            if self.page:
                if hasattr(self.page, 'window_width') and self.page.window_width:
                    width_sources.append(('window_width', self.page.window_width))
                if hasattr(self.page, 'width') and self.page.width:
                    width_sources.append(('width', self.page.width))
            
            # Par défaut, considérer comme petit écran (approche conservative)
            # Car si la fenêtre est vraiment grande, window_width sera > 1450
            screen_width = 1366 if not width_sources else width_sources[0][1]
            
            print(f"[RESPONSIVE DEBUG] Sources de largeur: {width_sources}")
            print(f"[RESPONSIVE DEBUG] Largeur retenue: {screen_width}px")
            
            # Initialiser _last_window_width si pas encore fait
            if self._last_window_width is None:
                self._last_window_width = screen_width
            
            is_small_screen = screen_width < self._responsive_threshold
            print(f"[RESPONSIVE DEBUG] Mode compact activé: {is_small_screen} (seuil: {self._responsive_threshold}px)")
        except Exception as e:
            print(f"[RESPONSIVE DEBUG] Erreur détection largeur: {e}")
            is_small_screen = False
        
        # Configuration des colonnes (responsive)
        columns_config = []
        
        # Ajouter la colonne checkbox seulement si activée
        if self.show_selection_column:
            columns_config.append(("[x]", 30, None, False))
        
        columns_config.extend([
            ("No NC", 60, "reference", False),
            ("Date", 80, "date_detection", False),
            ("Type", 80, "type_nc", False),
            ("Origine", 110, "origine", False),
            # Masquer sur petits écrans
            ("Anomalie", 110, "type_anomalie", False) if not is_small_screen else None,
            ("Produit", 120, "produit_concerne", False),
            ("Lot", 80, "lot_serie", False),
            ("Qte", 55, "quantite_affectee", False),
            ("Détail", 205, "description", True),  # Expandable
            # Masquer sur petits écrans
            ("Cause Racine", 205, "cause_racine", True) if not is_small_screen else None,
            ("Catégorie", 110, "categorie_nc", False),
            ("Imputation", 110, "imputation", False),
            # Masquer sur petits écrans
            ("Gravité", 85, None, False) if not is_small_screen else None,
            ("Statut", 85, None, False),
            ("Actions", 80, None, False),  # Colonne pour actions rapides (réduite)
        ])
        
        # Filtrer les colonnes None (masquées)
        columns_config = [col for col in columns_config if col is not None]

        header_cells = []
        for i, config in enumerate(columns_config):
            col_name = config[0]
            width = config[1]
            is_expandable = config[3] if len(config) > 3 else False
            is_last = i == len(columns_config) - 1
            
            if is_expandable:
                # Colonnes responsive avec largeur minimale
                header_cells.append(
                    ft.Container(
                        expand=1,
                        width=width,  # Largeur minimale
                        padding=ft.Padding(left=8, right=8, top=14, bottom=14),
                        border=ft.Border(right=ft.BorderSide(1, Theme.BG_PRIMARY)) if not is_last else None,
                        content=ft.Text(
                            col_name,
                            color=Theme.TEXT_PRIMARY,
                            weight=ft.FontWeight.BOLD,
                            size=13,
                            no_wrap=False,
                        ),
                    )
                )
            elif width is not None:
                header_cells.append(
                    ft.Container(
                        width=width,
                        padding=ft.Padding(left=8, right=8, top=14, bottom=14),
                        border=ft.Border(right=ft.BorderSide(1, Theme.BG_PRIMARY)) if not is_last else None,
                        content=ft.Text(
                            col_name,
                            color=Theme.TEXT_PRIMARY,
                            weight=ft.FontWeight.BOLD,
                            size=13,
                            no_wrap=False,
                        ),
                    )
                )
            else:
                header_cells.append(
                    ft.Container(
                        expand=True,
                        padding=ft.Padding(left=8, right=8, top=14, bottom=14),
                        border=ft.Border(right=ft.BorderSide(1, Theme.BG_PRIMARY)) if not is_last else None,
                        content=ft.Text(col_name, color=Theme.TEXT_PRIMARY, weight=ft.FontWeight.BOLD, size=13),
                    )
                )

        header_row = ft.Container(
            bgcolor=Theme.BG_TERTIARY,
            border_radius=ft.BorderRadius(8, 8, 0, 0),
            content=ft.Row(controls=header_cells, spacing=0),
        )

        data_rows = []
        for nc in filtered_ncs:
            nc_id = nc.get('id')
            is_selected = nc_id in self.selected_nc_ids
            
            # Checkbox pour sélection
            checkbox = ft.Checkbox(
                value=is_selected,
                on_change=lambda e, nid=nc_id: self._toggle_nc_selection(nid, e.control.value),
            )
            row_cells = []
            for i, config in enumerate(columns_config):
                col_name = config[0]
                width = config[1]
                data_key = config[2]
                is_expandable = config[3] if len(config) > 3 else False
                is_last = i == len(columns_config) - 1
                
                if col_name == "[x]":
                    # Colonne checkbox
                    cell_content = checkbox
                elif col_name == "Gravité":
                    cell_content = create_severity_badge(nc.get('gravite', ''))
                elif col_name == "Statut":
                    cell_content = create_status_badge(nc.get('statut', ''))
                elif col_name == "Actions":
                    # Boutons d'actions rapides
                    cell_content = ft.Row(
                        spacing=2,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.VISIBILITY,
                                icon_size=16,
                                tooltip="Voir la NC",
                                icon_color=Theme.INFO,
                                on_click=lambda e, n=nc: self._open_form_readonly(n),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_size=16,
                                tooltip="Éditer la NC",
                                icon_color=Theme.PRIMARY,
                                on_click=lambda e, n=nc: self._open_form(n),
                            ),
                        ],
                    )
                elif col_name == "No NC":
                    cell_content = ft.Text(
                        nc.get(data_key, '-') or '-',
                        color=Theme.TEXT_PRIMARY,
                        weight=ft.FontWeight.W_500,
                        size=13,
                        no_wrap=True,
                    )
                elif col_name == "Anomalie":
                    text = nc.get(data_key, '-') or '-'
                    # Retour à la ligne pour Anomalie
                    cell_content = ft.Text(wrap_text(text, 20), color=Theme.TEXT_SECONDARY, size=12)
                elif col_name in ("Détail", "Cause Racine"):
                    text = nc.get(data_key, '-') or '-'
                    # Colonnes responsive avec texte adapté
                    cell_content = ft.Text(wrap_text(text, 45), color=Theme.TEXT_SECONDARY, size=11)
                elif col_name in ("Origine",):
                    text = nc.get(data_key, '-') or '-'
                    cell_content = ft.Text(wrap_text(text, 20), color=Theme.TEXT_SECONDARY, size=12)
                elif col_name == "Catégorie":
                    text = nc.get(data_key, '-') or '-'
                    cell_content = ft.Text(wrap_text(text, 20), color=Theme.TEXT_SECONDARY, size=12)
                elif col_name == "Produit":
                    text = nc.get(data_key, '-') or '-'
                    cell_content = ft.Text(wrap_text(text, 22), color=Theme.TEXT_SECONDARY, size=12)
                elif col_name == "Lot":
                    text = nc.get(data_key, '-') or '-'
                    cell_content = ft.Text(wrap_text(text, 12), color=Theme.TEXT_SECONDARY, size=12)
                elif col_name == "Qte":
                    cell_content = ft.Text(
                        str(nc.get(data_key) or '-'),
                        color=Theme.TEXT_SECONDARY,
                        size=12,
                        no_wrap=True,
                    )
                else:
                    cell_content = ft.Text(
                        nc.get(data_key, '-') or '-',
                        color=Theme.TEXT_SECONDARY,
                        size=12,
                        no_wrap=True,
                    )
                
                if is_expandable:
                    # Colonnes responsive avec largeur minimale
                    row_cells.append(
                        ft.Container(
                            expand=1,
                            width=width,  # Largeur minimale
                            padding=ft.Padding(left=6, right=6, top=10, bottom=10),
                            border=ft.Border(right=ft.BorderSide(1, Theme.BG_TERTIARY)) if not is_last else None,
                            content=cell_content,
                        )
                    )
                elif width is not None:
                    row_cells.append(
                        ft.Container(
                            width=width,
                            padding=ft.Padding(left=6, right=6, top=10, bottom=10),
                            border=ft.Border(right=ft.BorderSide(1, Theme.BG_TERTIARY)) if not is_last else None,
                            content=cell_content,
                        )
                    )
                else:
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
                    # on_click supprimé car remplacé par les boutons d'actions
                    ink=False,
                )
            )

        # Zone de données scrollable (sans l'en-tête)
        data_column = ft.Column(
            controls=data_rows,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        )

        # Table avec en-tête fixe et données scrollables
        table = ft.Container(
            border_radius=8,
            bgcolor=Theme.BG_SECONDARY,
            expand=True,
            content=ft.Column(
                spacing=0,
                controls=[
                    header_row,  # En-tête fixe - reste toujours visible
                    ft.Container(
                        expand=True,
                        bgcolor=Theme.BG_SECONDARY,
                        content=data_column,  # Column avec scroll indépendant
                    )
                ],
            ),
        )

        # Si un focus différé est demandé pour la recherche, l'appliquer maintenant que le champ est attaché
        if self._pending_search_focus and getattr(self._search_filter_field, "page", None):
            try:
                pos = len(self.filter_search or "")
                self._search_filter_field.cursor_position = pos
                self._search_filter_field.selection = (pos, pos)
                self._search_filter_field.page.set_focus(self._search_filter_field)
                self._search_filter_field.update()
                self._search_filter_field.page.update()
            except Exception:
                pass
            self._pending_search_focus = False
        
        # Bouton pour afficher/masquer les filtres - Icônes et texte
        toggle_icon = ft.Icon(
            ft.Icons.VISIBILITY_OFF if self.show_kpi_filters else ft.Icons.VISIBILITY,
            size=18,
        )
        toggle_text = ft.Text(
            "Masquer Filtres" if self.show_kpi_filters else "Afficher Filtres",
            size=13,
        )
        
        # Conteneur pour filtres (avec référence)
        self._kpi_filters_container = ft.Column(
            spacing=15,
            visible=self.show_kpi_filters,
            controls=[filters],
        )
        
        # Contrôles de pagination
        total_pages = max(1, (self.total_nc_count + self.items_per_page - 1) // self.items_per_page)
        start_item = (self.current_page - 1) * self.items_per_page + 1
        end_item = min(self.current_page * self.items_per_page, self.total_nc_count)
        
        pagination_controls = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(
                    f"Affichage de {start_item} à {end_item} sur {self.total_nc_count} NC",
                    size=13,
                    color=Theme.TEXT_MUTED,
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.ElevatedButton(
                            "< Précédent",
                            on_click=lambda e: self._change_page(self.current_page - 1),
                            disabled=self.current_page <= 1,
                            bgcolor=Theme.BG_SECONDARY if self.current_page > 1 else Theme.BG_TERTIARY,
                        ),
                        ft.Text(
                            f"Page {self.current_page} / {total_pages}",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=Theme.TEXT_PRIMARY,
                        ),
                        ft.ElevatedButton(
                            "Suivant >",
                            on_click=lambda e: self._change_page(self.current_page + 1),
                            disabled=self.current_page >= total_pages,
                            bgcolor=Theme.BG_SECONDARY if self.current_page < total_pages else Theme.BG_TERTIARY,
                        ),
                    ],
                ),
            ],
        )
        
        # Créer le bouton de suppression multiple
        self.delete_multiple_btn = ft.ElevatedButton(
            "Supprimer sélection",
            icon=ft.Icons.DELETE_SWEEP,
            on_click=self._confirm_delete_multiple,
            disabled=len(self.selected_nc_ids) == 0,
            visible=self.show_selection_column,  # Visible seulement si colonne activée
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: ft.Colors.RED_700, ft.ControlState.DISABLED: ft.Colors.GREY_400},
                color=ft.Colors.WHITE,
            ),
            height=40,
        )
        
        # Bouton pour afficher/masquer la colonne de sélection
        toggle_selection_btn = ft.ElevatedButton(
            content=ft.Row(
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.CHECK_BOX if self.show_selection_column else ft.Icons.CHECK_BOX_OUTLINE_BLANK, size=20),
                    ft.Text("Masquer sélection" if self.show_selection_column else "Afficher sélection"),
                ],
            ),
            on_click=lambda e: self._toggle_selection_column(),
            bgcolor=Theme.PRIMARY if self.show_selection_column else Theme.BG_SECONDARY,
            color=ft.Colors.WHITE if self.show_selection_column else Theme.TEXT_PRIMARY,
            height=40,
        )
        
        # Bouton pour sélectionner/désélectionner tout
        select_all_btn = ft.ElevatedButton(
            content=ft.Row(
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.SELECT_ALL, size=20),
                    ft.Text("Tout sélectionner"),
                ],
            ),
            on_click=lambda e: self._select_all_nc(),
            visible=self.show_selection_column,  # Visible seulement si colonne activée
            bgcolor=Theme.INFO,
            color=ft.Colors.WHITE,
            height=40,
        )
        
        # Bouton pour afficher/masquer les filtres
        toggle_button = ft.ElevatedButton(
            content=ft.Row(
                spacing=8,
                controls=[toggle_icon, toggle_text],
            ),
            on_click=lambda e: self._toggle_kpi_filters(toggle_icon, toggle_text),
            bgcolor=Theme.BG_SECONDARY,
            color=Theme.TEXT_PRIMARY,
            height=40,
        )
        
        # Ligne avec les boutons alignés
        buttons_row = ft.Container(
            padding=ft.Padding(left=0, right=0, top=0, bottom=10),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=10,
                        controls=[
                            toggle_selection_btn,
                            select_all_btn,
                            self.delete_multiple_btn,
                        ],
                    ),
                    toggle_button,
                ],
            ),
        )
        
        return ft.Column(
            expand=True,
            spacing=15,
            controls=[
                # Ligne avec les deux boutons
                buttons_row,
                self._kpi_filters_container,
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            table,
                        ]
                    ),
                ),
                ft.Container(
                    padding=ft.Padding(left=0, right=0, top=10, bottom=10),
                    content=pagination_controls,
                ),
            ],
        )
    
    def _change_page(self, new_page):
        """Change la page de pagination."""
        self.current_page = new_page
        
        # Invalider le cache de l'onglet liste pour forcer la reconstruction
        if 1 in self._tabs_cache:
            del self._tabs_cache[1]
        
        self.tab_content.content = self._build_list_tab()
        self._tabs_cache[1] = self.tab_content.content
        self.page.update()

    def _build_search_field(self):
        """Construit le champ de recherche avec autocomplétion et historique."""
        # Récupérer l'historique des recherches
        search_history = self.db.get_user_preference(self.user['id'], 'nc', 'search_history', default=[])
        
        # Générer les suggestions depuis toutes les NC
        all_ncs = self.db.get_all_nc()
        suggestions = set()
        
        # Ajouter références, produits, descriptions
        for nc in all_ncs[:100]:  # Limiter à 100 pour performance
            if nc.get('reference'):
                suggestions.add(nc['reference'])
            if nc.get('produit_concerne'):
                suggestions.add(nc['produit_concerne'])
            if nc.get('description') and len(nc['description']) < 50:
                # Ajouter description courte uniquement
                suggestions.add(nc['description'][:50])
        
        # Ajouter l'historique aux suggestions
        suggestions.update(search_history[:10])
        
        # Convertir en liste triée
        suggestions_list = sorted(list(suggestions))[:50]  # Max 50 suggestions
        
        # Bouton pour effacer
        suffix_controls = []
        if self.filter_search:
            suffix_controls.append(
                ft.IconButton(
                    icon=ft.Icons.CLEAR,
                    icon_size=18,
                    tooltip="Effacer la recherche",
                    on_click=lambda e: self._apply_filter('search', ''),
                )
            )
        
        # TextField avec autocomplete
        self._search_filter_field = ft.TextField(
            label="Rechercher (réf, produit, description...)...",
            width=350,
            value=self.filter_search,
            on_change=lambda e: self._on_search_change_with_fuzzy(e.control.value),
            on_submit=lambda e: self._on_search_submit(e.control.value),
            on_focus=self._on_search_focus,
            prefix_icon=ft.Icons.SEARCH,
            suffix=suffix_controls[0] if suffix_controls else None,
            border_radius=8,
            filled=True,
            bgcolor=Theme.BG_TERTIARY,
            border_color=Theme.OUTLINE,
            focused_border_color=Theme.PRIMARY,
            text_size=13,
            hint_text="Tapez pour rechercher... (Ctrl+F)",
            autocorrect=False,
            enable_suggestions=True,
        )
        
        # Stocker les suggestions pour la recherche fuzzy
        self._search_suggestions = suggestions_list
        
        return self._search_filter_field
    
    def _on_search_change_with_fuzzy(self, value: str):
        """Gère le changement de recherche avec suggestions fuzzy."""
        if not value:
            self._apply_filter('search', '')
            return
        
        # Recherche fuzzy pour suggestions
        if len(value) >= 2 and hasattr(self, '_search_suggestions'):
            import difflib
            matches = difflib.get_close_matches(
                value, 
                self._search_suggestions, 
                n=5, 
                cutoff=0.5
            )
            # Afficher les suggestions dans la console pour débogage
            if matches:
                print(f"[SEARCH] Suggestions: {matches[:3]}")
        
        # Appliquer le filtre après un court délai (debounce)
        self._on_search_change(value)
    
    def _on_search_submit(self, value: str):
        """Enregistre la recherche dans l'historique."""
        if value and value.strip():
            search_text = value.strip()
            
            # Récupérer l'historique actuel
            history = self.db.get_user_preference(self.user['id'], 'nc', 'search_history', default=[])
            
            # Ajouter en première position (retirer si déjà présent)
            if search_text in history:
                history.remove(search_text)
            history.insert(0, search_text)
            
            # Garder seulement les 10 dernières
            history = history[:10]
            
            # Sauvegarder
            self.db.save_user_preference(self.user['id'], 'nc', 'search_history', history)
            print(f"[SEARCH] Historique mis à jour: {history[:3]}...")
    
    def _apply_filter(self, filter_type: str, value: str, event=None):
        """Applique un filtre et reset la pagination."""
        if filter_type == 'status':
            self.filter_status = value
        elif filter_type == 'gravite':
            self.filter_gravite = value
        elif filter_type == 'type':
            self.filter_type = value
        elif filter_type == 'search':
            self.filter_search = value or ""
        elif filter_type == 'origine':
            self.filter_origine = value or "Tous"
        elif filter_type == 'categorie':
            self.filter_categorie = value or "Tous"
        elif filter_type == 'imputation':
            self.filter_imputation = value or "Tous"
        elif filter_type == 'date_start':
            if isinstance(value, datetime):
                value_str = value.date().isoformat()
            else:
                value_str = value or ""
            self.filter_date_start = value_str
        elif filter_type == 'date_end':
            if isinstance(value, datetime):
                value_str = value.date().isoformat()
            else:
                value_str = value or ""
            self.filter_date_end = value_str
        
        # Sauvegarder les filtres dans les préférences
        self._save_filters_preferences()
        
        # Reset à la page 1 quand on change les filtres
        self.current_page = 1
        
        # Invalider le cache de l'onglet liste (onglet 1 maintenant)
        if 1 in self._tabs_cache:
            del self._tabs_cache[1]
        
        self.tab_content.content = self._build_list_tab()
        self._tabs_cache[1] = self.tab_content.content  # Sauvegarder le nouvel onglet
        self.page.update()
        if filter_type == 'search' and getattr(self, '_search_filter_field', None):
            # Ne pas forcer le focus pendant la reconstruction; le faire après via le flag
            pos = len(self.filter_search or "")
            try:
                self._search_filter_field.cursor_position = pos
                self._search_filter_field.selection = (pos, pos)
            except Exception:
                pass
            self._pending_search_focus = True

    def _on_search_change(self, value: str):
        """Met à jour la valeur de recherche avec debouncing."""
        import threading
        
        self.filter_search = value or ""
        
        # Annuler le timer précédent s'il existe
        if hasattr(self, '_search_timer') and self._search_timer:
            self._search_timer.cancel()
        
        # Créer un nouveau timer pour appliquer le filtre après 500ms
        def apply_search():
            try:
                self._apply_filter('search', self.filter_search)
            except Exception as ex:
                print(f"Erreur recherche: {ex}")
        
        self._search_timer = threading.Timer(0.5, apply_search)
        self._search_timer.start()

    def _on_search_focus(self, e):
        """Place le curseur en fin de texte sans sélection quand le champ prend le focus."""
        try:
            control = e.control
            pos = len(control.value or "")
            control.cursor_position = pos
            control.selection = (pos, pos)
            control.update()
            if control.page:
                control.page.update()
        except Exception:
            pass
    
    def _toggle_kpi_filters(self, icon, text):
        """Bascule l'affichage des KPI et filtres de manière instantanée."""
        self.show_kpi_filters = not self.show_kpi_filters
        
        # Mise à jour instantanée de la visibilité
        if self._kpi_filters_container and hasattr(self._kpi_filters_container, 'page') and self._kpi_filters_container.page:
            self._kpi_filters_container.visible = self.show_kpi_filters
            self._kpi_filters_container.update()
        
        # Mise à jour du bouton
        icon.name = ft.Icons.VISIBILITY_OFF if self.show_kpi_filters else ft.Icons.VISIBILITY
        text.value = "Masquer KPI/Filtres" if self.show_kpi_filters else "Afficher KPI/Filtres"
        if hasattr(icon, 'page') and icon.page:
            icon.update()
        if hasattr(text, 'page') and text.page:
            text.update()
        
        # Forcer la mise à jour de la page si les éléments ne sont pas encore attachés
        if self.page:
            self.page.update()
    
    def _toggle_selection_column(self):
        """Bascule l'affichage de la colonne de sélection et reconstruit le tableau."""
        self.show_selection_column = not self.show_selection_column
        
        # Réinitialiser la sélection lors du masquage
        if not self.show_selection_column:
            self.selected_nc_ids.clear()
        
        # Invalider le cache pour forcer la reconstruction
        if 1 in self._tabs_cache:
            del self._tabs_cache[1]
        
        # Reconstruire l'onglet Liste
        self._tabs_cache[1] = self._build_list_tab()
        self.tab_content.content = self._tabs_cache[1]
        
        # Mettre à jour la page
        if self.page:
            self.page.update()
    
    def _select_all_nc(self):
        """Sélectionne ou désélectionne toutes les NC de la page actuelle."""
        # Récupérer les NC de la page actuelle
        ncs = self._get_nc_list()
        
        if not ncs:
            return
        
        # Récupérer tous les IDs de la page actuelle
        current_page_ids = {nc.get('id') for nc in ncs if nc.get('id')}
        
        # Si toutes les NC de la page sont déjà sélectionnées, les désélectionner
        if current_page_ids.issubset(self.selected_nc_ids):
            # Désélectionner toutes les NC de la page actuelle
            self.selected_nc_ids -= current_page_ids
        else:
            # Sélectionner toutes les NC de la page actuelle
            self.selected_nc_ids.update(current_page_ids)
        
        # Mettre à jour le bouton de suppression
        self._update_delete_multiple_button()
        
        # Reconstruire le tableau pour mettre à jour les checkboxes
        if 1 in self._tabs_cache:
            del self._tabs_cache[1]
        self._tabs_cache[1] = self._build_list_tab()
        self.tab_content.content = self._tabs_cache[1]
        
        # Mettre à jour la page
        if self.page:
            self.page.update()

    def _ensure_filter_date_pickers(self):
        """Prépare les DatePickers des filtres avec un seul exemplaire dans l'overlay."""
        if not self._filter_date_picker_start:
            self._filter_date_picker_start = ft.DatePicker(
                on_change=lambda e: self._apply_filter('date_start', e.control.value),
            )
        if not self._filter_date_picker_end:
            self._filter_date_picker_end = ft.DatePicker(
                on_change=lambda e: self._apply_filter('date_end', e.control.value),
            )

        # Accès page sécurisé (évite l'AttributeError avant montage)
        try:
            page_obj = self.page
        except AttributeError:
            page_obj = getattr(self, "_Control__page", None)
        if page_obj:
            if self._filter_date_picker_start not in page_obj.overlay:
                page_obj.overlay.append(self._filter_date_picker_start)
            if self._filter_date_picker_end not in page_obj.overlay:
                page_obj.overlay.append(self._filter_date_picker_end)
            page_obj.update()

    def _open_filter_date_picker(self, which: str):
        """Ouvre le DatePicker start/end pour les filtres."""
        self._ensure_filter_date_pickers()
        picker = self._filter_date_picker_start if which == 'start' else self._filter_date_picker_end
        if not picker:
            return
        if getattr(picker, "page", None):
            picker.open = True
            picker.update()
            picker.page.update()
    
    def _open_custom_calendar(self, filter_type: str, current_value: str):
        """Ouvre le calendrier personnalisé hors ligne."""
        # Parser la date actuelle si elle existe
        initial_date = None
        if current_value:
            try:
                initial_date = datetime.strptime(current_value, '%Y-%m-%d').date()
            except:
                initial_date = None
        
        # Callback quand une date est sélectionnée
        def on_date_selected(selected_date):
            date_str = selected_date.strftime('%Y-%m-%d')
            self._apply_filter(filter_type, date_str)
        
        # Créer et ouvrir le calendrier
        calendar_dialog = CustomCalendar(on_date_selected, initial_date)
        
        # Ajouter à l'overlay de la page
        if self.page:
            self.page.overlay.append(calendar_dialog)
            calendar_dialog.open = True
            self.page.update()
    
    def _open_stats_custom_calendar(self, chart_id: str, which: str, field_ref, current_value: str):
        """Ouvre le calendrier personnalisé pour les filtres Zone B."""
        # Parser la date actuelle
        initial_date = None
        if current_value:
            try:
                initial_date = datetime.strptime(current_value, '%Y-%m-%d').date()
            except:
                initial_date = None
        
        # Callback quand une date est sélectionnée
        def on_date_selected(selected_date):
            date_str = selected_date.strftime('%Y-%m-%d')
            field_ref.value = date_str
            field_ref.error_text = None
            field_ref.update()
            
            # Déclencher le handler de changement de date
            # Créer un événement fictif
            class FakeEvent:
                def __init__(self, control):
                    self.control = control
            
            fake_event = FakeEvent(field_ref)
            if field_ref.on_blur:
                field_ref.on_blur(fake_event)
        
        # Créer et ouvrir le calendrier
        calendar_dialog = CustomCalendar(on_date_selected, initial_date)
        
        # Ajouter à l'overlay de la page
        if self.page:
            self.page.overlay.append(calendar_dialog)
            calendar_dialog.open = True
            self.page.update()
    
    def _validate_and_apply_date_filter(self, filter_type: str, value: str):
        """Valide et applique un filtre de date depuis un TextField (fonctionne hors ligne)."""
        if not value or value.strip() == '':
            # Valeur vide = réinitialiser le filtre
            self._apply_filter(filter_type, '')
            return
        
        # Valider le format de la date (AAAA-MM-JJ ou AAAA/MM/JJ)
        from datetime import datetime
        try:
            # Accepter les formats avec - ou /
            value_normalized = value.replace('/', '-')
            
            # Vérifier le format
            if len(value_normalized) == 10 and value_normalized.count('-') == 2:
                # Tenter de parser la date
                parsed_date = datetime.strptime(value_normalized, '%Y-%m-%d')
                # Appliquer le filtre avec la date normalisée
                self._apply_filter(filter_type, value_normalized)
            else:
                # Format invalide, ne rien faire (l'utilisateur est encore en train de taper)
                pass
        except ValueError:
            # Date invalide, ne rien faire (l'utilisateur est encore en train de taper)
            pass
    
    def _on_stats_date_picker_change(self, chart_id: str, which: str, value):
        """Gère le changement de date depuis un DatePicker des statistiques Zone B."""
        if value:
            try:
                new_date = value.date() if hasattr(value, 'date') else value
                current_debut, current_fin = self.stats_zone_b_dates.get(chart_id, (None, None))
                
                if which == 'debut':
                    self.stats_zone_b_dates[chart_id] = (new_date, current_fin)
                else:  # fin
                    self.stats_zone_b_dates[chart_id] = (current_debut, new_date)
            except Exception as ex:
                print(f"Erreur changement date: {ex}")
    
    def _select_nc(self, nc: Dict):
        """Sélectionne une NC."""
        self.current_nc_id = nc['id']
    
    def _view_nc(self, nc: Dict):
        """Affiche le détail d'une NC."""
        self.current_nc_id = nc['id']
        self.tabs.selected_index = 2
        self.current_tab = 2
        self.tab_content.content = self._build_detail_tab()
        self.page.update()
    
    # ========================================================================
    # TAB 2: DÉTAIL NC
    # ========================================================================
    
    def _build_5m_visual_display(self, ishikawa_categories: Dict) -> ft.Container:
        """Crée une visualisation des 5M sélectionnés avec leurs causes."""
        if not ishikawa_categories:
            return None
        
        # Les 5M possibles avec leurs icônes (noms exacts depuis la base de données)
        all_5m_icons = {
            "Main d'oeuvre": (ft.Icons.GROUPS, "#8B5CF6"),
            "Matériel": (ft.Icons.PRECISION_MANUFACTURING, "#F59E0B"),
            "Matière": (ft.Icons.INVENTORY_2, "#EF4444"),
            "Méthode": (ft.Icons.ACCOUNT_TREE, "#3B82F6"),
            "Milieu": (ft.Icons.PUBLIC, "#10B981"),
            "Mesure": (ft.Icons.STRAIGHTEN, "#EC4899"),
        }
        
        # Créer les cartes pour chaque 5M avec ses causes
        cards = []
        for m_name, causes in ishikawa_categories.items():
            if not causes or not any(c.strip() for c in causes if c):
                continue
                
            icon, color = all_5m_icons.get(m_name, (ft.Icons.HELP_OUTLINE, "#6B7280"))
            
            # Créer la liste des causes
            cause_controls = []
            for idx, cause in enumerate(causes, 1):
                if cause and cause.strip():
                    cause_controls.append(
                        ft.Row(
                            spacing=6,
                            controls=[
                                ft.Text("*", size=12, color="white"),
                                ft.Text(cause.strip(), size=11, color="white", expand=True),
                            ],
                        )
                    )
            
            if cause_controls:
                cards.append(
                    ft.Container(
                        padding=12,
                        border_radius=10,
                        bgcolor=color,
                        border=ft.Border(
                top=ft.BorderSide(2, color),
                right=ft.BorderSide(2, color),
                bottom=ft.BorderSide(2, color),
                left=ft.BorderSide(2, color),
            ),
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        ft.Icon(icon, size=20, color="white"),
                                        ft.Text(
                                            m_name,
                                            size=13,
                                            weight=ft.FontWeight.BOLD,
                                            color="white",
                                        ),
                                    ],
                                ),
                                ft.Column(
                                    spacing=4,
                                    controls=cause_controls,
                                ),
                            ],
                        ),
                    )
                )
        
        if not cards:
            return None
            
        return ft.Container(
            padding=16,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Column(
                spacing=10,
                controls=cards,
            ),
        )
    
    def _build_costs_section(self, nc: Dict) -> ft.Container:
        """Construit la section expandable des coûts détaillés."""
        # Récupérer les actions pour calculer les coûts
        immediate_actions = self._safe_json(nc.get('actions_immediates_table'), [])
        corrective_actions = self._safe_json(nc.get('actions_correctives_table'), [])
        
        # Calculer coût correction (actions immédiates) - depuis tableau corrections
        cout_correction = 0
        for action in immediate_actions:
            cout = action.get('cost', 0)  # Utiliser 'cost' car c'est le nom du champ dans le formulaire
            if isinstance(cout, (int, float)):
                cout_correction += float(cout or 0)
            elif isinstance(cout, str) and cout:
                try:
                    cout_correction += float(cout.replace(',', '.').replace(' ', ''))
                except:
                    pass
        
        # Calculer coût actions correctives - depuis tableau actions correctives
        cout_action_corrective = 0
        for action in corrective_actions:
            cout = action.get('cost', 0)  # Utiliser 'cost' car c'est le nom du champ dans le formulaire
            if isinstance(cout, (int, float)):
                cout_action_corrective += float(cout or 0)
            elif isinstance(cout, str) and cout:
                try:
                    cout_action_corrective += float(cout.replace(',', '.').replace(' ', ''))
                except:
                    pass
        
        # Coût global = corrections + actions correctives (pas de coût NC pour l'instant)
        cout_global = cout_correction + cout_action_corrective
        
        # Créer les cartes de coûts
        def create_cost_card(label: str, montant: float, icon, color: str):
            return ft.Container(
                expand=1,
                padding=16,
                border_radius=12,
                bgcolor=Theme.BG_TERTIARY,
                border=ft.Border(
                top=ft.BorderSide(2, color),
                right=ft.BorderSide(2, color),
                bottom=ft.BorderSide(2, color),
                left=ft.BorderSide(2, color),
            ),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Icon(icon, size=32, color=color),
                        ft.Text(label, size=12, color=Theme.TEXT_MUTED, text_align=ft.TextAlign.CENTER),
                        ft.Text(
                            f"{montant:,.2f} EUR",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=color,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                ),
            )
        
        return ft.Container(
            padding=16,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.EURO, size=18, color=Theme.WARNING),
                            ft.Text("Coûts de Non-Qualité (CNQ)", size=15, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                        ],
                    ),
                    ft.Row(
                        spacing=12,
                        controls=[
                            create_cost_card("Coût Global", cout_global, ft.Icons.ATTACH_MONEY, Theme.DANGER),
                            create_cost_card("Corrections", cout_correction, ft.Icons.BUILD_CIRCLE, Theme.WARNING),
                            create_cost_card("Actions Correctives", cout_action_corrective, ft.Icons.ASSIGNMENT_TURNED_IN, Theme.SUCCESS),
                        ],
                    ),
                ],
            ),
        )
    
    def _build_nc_timeline(self, nc: Dict) -> ft.Container:
        """Construit une timeline horizontale montrant l'évolution de la NC."""
        from datetime import datetime
        
        # Extraire les dates
        date_detection = nc.get('date_detection', '')
        date_cloture = nc.get('date_cloture', '')
        
        # Extraire les actions pour obtenir leurs dates
        immediate_actions = self._safe_json(nc.get('actions_immediates_table'), [])
        corrective_actions = self._safe_json(nc.get('actions_correctives_table'), [])
        
        # Dates des corrections (première action immédiate)
        date_correction = None
        if immediate_actions:
            for action in immediate_actions:
                if action.get('date_limite'):
                    date_correction = action.get('date_limite')
                    break
        
        # Dates des actions correctives (première action corrective)
        date_action_corrective = None
        if corrective_actions:
            for action in corrective_actions:
                if action.get('date_limite'):
                    date_action_corrective = action.get('date_limite')
                    break
        
        # Définir les étapes de la timeline
        timeline_steps = [
            {
                "label": "Détection",
                "date": date_detection,
                "icon": ft.Icons.SEARCH,
                "color": Theme.INFO,
                "completed": bool(date_detection),
            },
            {
                "label": "Corrections",
                "date": date_correction if date_correction else "En cours" if immediate_actions else "Non démarré",
                "icon": ft.Icons.BUILD,
                "color": Theme.WARNING,
                "completed": bool(date_correction),
            },
            {
                "label": "Actions correctives",
                "date": date_action_corrective if date_action_corrective else "En cours" if corrective_actions else "Non démarré",
                "icon": ft.Icons.ASSIGNMENT_TURNED_IN,
                "color": Theme.PRIMARY,
                "completed": bool(date_action_corrective),
            },
            {
                "label": "Clôture",
                "date": date_cloture if date_cloture else "Non clôturée",
                "icon": ft.Icons.CHECK_CIRCLE,
                "color": Theme.SUCCESS,
                "completed": bool(date_cloture),
            },
        ]
        
        # Construire les étapes visuelles
        timeline_controls = []
        for i, step in enumerate(timeline_steps):
            is_last = i == len(timeline_steps) - 1
            
            # Point de la timeline
            step_column = ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    # Icône avec cercle
                    ft.Container(
                        width=50,
                        height=50,
                        border_radius=25,
                        bgcolor=step["color"] if step["completed"] else Theme.BG_TERTIARY,
                        border=ft.Border(
                top=ft.BorderSide(3, step["color"]),
                right=ft.BorderSide(3, step["color"]),
                bottom=ft.BorderSide(3, step["color"]),
                left=ft.BorderSide(3, step["color"]),
            ),
                        content=ft.Icon(
                            step["icon"],
                            size=24,
                            color=ft.Colors.WHITE if step["completed"] else step["color"],
                        ),
                    ),
                    # Label
                    ft.Text(
                        step["label"],
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=Theme.TEXT_PRIMARY if step["completed"] else Theme.TEXT_MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    # Date
                    ft.Text(
                        step["date"] if step["date"] else "-",
                        size=11,
                        color=Theme.TEXT_SECONDARY if step["completed"] else Theme.TEXT_MUTED,
                        text_align=ft.TextAlign.CENTER,
                        italic=not step["completed"],
                    ),
                ],
            )
            
            timeline_controls.append(step_column)
            
            # Ligne de connexion (sauf pour la dernière étape)
            if not is_last:
                timeline_controls.append(
                    ft.Container(
                        expand=1,
                        padding=ft.Padding(left=0, right=0, top=32, bottom=32),
                        content=ft.Container(
                            height=3,
                            bgcolor=step["color"] if step["completed"] and timeline_steps[i+1]["completed"] else Theme.BG_TERTIARY,
                        ),
                    )
                )
        
        return ft.Container(
            padding=20,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        spacing=6,
                        controls=[
                            ft.Icon(ft.Icons.TIMELINE, size=18, color=Theme.PRIMARY),
                            ft.Text("Chronologie de la NC", size=15, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=timeline_controls,
                    ),
                ],
            ),
        )
    
    def _build_history_section(self, nc: Dict) -> ft.Container:
        """Construit la section d'historique des modifications."""
        nc_id = nc.get('id')
        if not nc_id:
            return ft.Container()
        
        # Utiliser la méthode du DatabaseManager
        history = self.db.get_nc_history(nc_id)
        
        # Icônes par type d'action
        action_icons = {
            'creation': (ft.Icons.ADD_CIRCLE, Theme.SUCCESS),
            'modification': (ft.Icons.EDIT, Theme.INFO),
            'cloture': (ft.Icons.CHECK_CIRCLE, Theme.SUCCESS),
            'suppression': (ft.Icons.DELETE, Theme.DANGER),
        }
        
        # Libellés d'actions en français
        action_labels = {
            'creation': 'Création',
            'modification': 'Modification',
            'cloture': 'Clôture',
            'suppression': 'Suppression',
        }
        
        history_items = []
        for entry in history:
            icon, color = action_icons.get(entry['action'], (ft.Icons.INFO, Theme.TEXT_MUTED))
            action_label = action_labels.get(entry['action'], entry['action'])
            
            # Construire le texte de description
            if entry['field_changed']:
                if entry['old_value'] and entry['new_value']:
                    description = f"{entry['field_changed']}: '{entry['old_value']}' > '{entry['new_value']}'"
                elif entry['new_value']:
                    description = f"{entry['field_changed']}: {entry['new_value']}"
                else:
                    description = f"{entry['field_changed']} modifié"
            else:
                description = action_label
            
            history_items.append(
                ft.Container(
                    padding=10,
                    border_radius=8,
                    bgcolor=Theme.BG_PRIMARY,
                    content=ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(
                                width=40,
                                height=40,
                                border_radius=20,
                                bgcolor=f"{color}20",
                                content=ft.Icon(icon, size=20, color=color),
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Column(
                                expand=True,
                                spacing=2,
                                controls=[
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Text(action_label, size=13, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                                            ft.Text("*", size=13, color=Theme.TEXT_MUTED),
                                            ft.Text(entry['user_name'], size=12, color=Theme.TEXT_SECONDARY),
                                        ],
                                    ),
                                    ft.Text(description, size=12, color=Theme.TEXT_MUTED, max_lines=2),
                                    ft.Text(
                                        entry['timestamp'],
                                        size=11,
                                        color=Theme.TEXT_MUTED,
                                        italic=True,
                                    ),
                                ],
                            ),
                        ],
                    ),
                )
            )
        
        if not history_items:
            history_items.append(
                ft.Container(
                    padding=20,
                    content=ft.Text(
                        "Aucune modification enregistrée",
                        size=13,
                        color=Theme.TEXT_MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.Alignment(0, 0),
                )
            )
        
        return ft.Container(
            padding=20,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            border=ft.Border(
                top=ft.BorderSide(1, Theme.BG_TERTIARY),
                right=ft.BorderSide(1, Theme.BG_TERTIARY),
                bottom=ft.BorderSide(1, Theme.BG_TERTIARY),
                left=ft.BorderSide(1, Theme.BG_TERTIARY),
            ),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.HISTORY, size=20, color=Theme.PRIMARY),
                                    ft.Text("Historique des modifications", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                                ],
                            ),
                            ft.Container(
                                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                                border_radius=12,
                                bgcolor=Theme.PRIMARY + "20",
                                content=ft.Text(
                                    f"{len(history)} événement{'s' if len(history) > 1 else ''}",
                                    size=11,
                                    color=Theme.PRIMARY,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color=Theme.BG_TERTIARY),
                    ft.Column(
                        spacing=8,
                        scroll=ft.ScrollMode.AUTO,
                        controls=history_items,
                    ),
                ],
            ),
        )
    
    def _build_similar_ncs_section(self, nc: Dict) -> ft.Container:
        """Construit la section des NC similaires (basée sur lot, produit, catégorie, type, cause)."""
        nc_id = nc.get('id')
        if not nc_id:
            return ft.Container()
        
        # Récupérer toutes les NC sauf celle en cours
        all_ncs = [n for n in self.db.get_all_nc() if n.get('id') != nc_id]
        
        # Critères de similarité (gérer None explicitement)
        lot_serie = (nc.get('lot_serie') or '').strip().lower()
        produit = (nc.get('produit_concerne') or '').strip().lower()
        categorie = (nc.get('categorie_nc') or '').strip().lower()
        type_nc = (nc.get('type_nc') or '').strip().lower()
        cause_racine = (nc.get('cause_racine') or '').strip().lower()
        
        # Calculer les scores de similarité
        similar_ncs = []
        for other_nc in all_ncs:
            score = 0
            matches = []
            
            # +5 points : même no de lot (critère TRÈS fort - prioritaire)
            other_lot = (other_nc.get('lot_serie') or '').strip().lower()
            if lot_serie and len(lot_serie) > 2 and other_lot == lot_serie:
                score += 5
                matches.append("Même lot/série")
            
            # +4 points : même produit (critère fort)
            other_produit = (other_nc.get('produit_concerne') or '').strip().lower()
            if produit and other_produit == produit:
                score += 4
                matches.append("Même produit")
            
            # +3 points : même cause racine (critère important)
            other_cause = (other_nc.get('cause_racine') or '').strip().lower()
            if cause_racine and len(cause_racine) > 5 and other_cause == cause_racine:
                score += 3
                matches.append("Même cause racine")
            
            # +2 points : même catégorie
            other_categorie = (other_nc.get('categorie_nc') or '').strip().lower()
            if categorie and other_categorie == categorie:
                score += 2
                matches.append("Même catégorie")
            
            # +1 point : même type
            other_type = (other_nc.get('type_nc') or '').strip().lower()
            if type_nc and other_type == type_nc:
                score += 1
                matches.append("Même type")
            
            # Ne garder que les NC avec au moins 2 points de similarité
            if score >= 2:
                similar_ncs.append({
                    'nc': other_nc,
                    'score': score,
                    'matches': matches,
                })
        
        # Trier par score décroissant et prendre les 5 premières
        similar_ncs.sort(key=lambda x: x['score'], reverse=True)
        similar_ncs = similar_ncs[:5]
        
        # Construire les cartes de NC similaires
        similar_items = []
        for item in similar_ncs:
            other_nc = item['nc']
            score = item['score']
            matches = item['matches']
            
            # Badge de similarité (score sur 10)
            score_percentage = min(100, int((score / 10) * 100))
            score_color = Theme.SUCCESS if score >= 7 else (Theme.WARNING if score >= 4 else Theme.INFO)
            
            similar_items.append(
                ft.Container(
                    padding=12,
                    border_radius=8,
                    bgcolor=Theme.BG_PRIMARY,
                    border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                    content=ft.Row(
                        spacing=12,
                        controls=[
                            # Score de similarité
                            ft.Container(
                                width=50,
                                height=50,
                                border_radius=25,
                                bgcolor=f"{score_color}20",
                                border=ft.Border(
                top=ft.BorderSide(2, score_color),
                right=ft.BorderSide(2, score_color),
                bottom=ft.BorderSide(2, score_color),
                left=ft.BorderSide(2, score_color),
            ),
                                content=ft.Column(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=0,
                                    controls=[
                                        ft.Text(f"{score_percentage}%", size=12, weight=ft.FontWeight.BOLD, color=score_color),
                                    ],
                                ),
                            ),
                            # Informations NC
                            ft.Column(
                                expand=True,
                                spacing=4,
                                controls=[
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Text(
                                                other_nc.get('reference', 'N/A'),
                                                size=14,
                                                weight=ft.FontWeight.BOLD,
                                                color=Theme.PRIMARY,
                                            ),
                                            create_severity_badge(other_nc.get('gravite', 'Mineure')),
                                            create_status_badge(other_nc.get('statut', 'Ouverte')),
                                        ],
                                    ),
                                    ft.Text(
                                        other_nc.get('description', 'Aucune description')[:80] + ('...' if len(other_nc.get('description', '')) > 80 else ''),
                                        size=12,
                                        color=Theme.TEXT_SECONDARY,
                                        max_lines=2,
                                    ),
                                    ft.Row(
                                        spacing=6,
                                        controls=[
                                            ft.Icon(ft.Icons.LINK, size=12, color=Theme.INFO),
                                            ft.Text(
                                                ' * '.join(matches),
                                                size=11,
                                                color=Theme.INFO,
                                                italic=True,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            # Bouton pour ouvrir
                            ft.IconButton(
                                icon=ft.Icons.OPEN_IN_NEW,
                                icon_size=20,
                                tooltip="Ouvrir cette NC",
                                on_click=lambda e, nc_data=other_nc: self._open_form(nc_data),
                                icon_color=Theme.PRIMARY,
                            ),
                        ],
                    ),
                )
            )
        
        if not similar_items:
            similar_items.append(
                ft.Container(
                    padding=30,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.SEARCH_OFF, size=40, color=Theme.TEXT_MUTED),
                            ft.Text(
                                "Aucune NC similaire trouvée",
                                size=13,
                                color=Theme.TEXT_MUTED,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "Les NC sont comparées sur le produit, le type, la gravité et la cause racine",
                                size=11,
                                color=Theme.TEXT_MUTED,
                                text_align=ft.TextAlign.CENTER,
                                italic=True,
                            ),
                        ],
                    ),
                    alignment=ft.Alignment(0, 0),
                )
            )
        
        return ft.Container(
            padding=20,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            border=ft.Border(
                top=ft.BorderSide(1, Theme.BG_TERTIARY),
                right=ft.BorderSide(1, Theme.BG_TERTIARY),
                bottom=ft.BorderSide(1, Theme.BG_TERTIARY),
                left=ft.BorderSide(1, Theme.BG_TERTIARY),
            ),
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.COMPARE_ARROWS, size=20, color=Theme.PRIMARY),
                                    ft.Text("NC similaires", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                                ],
                            ),
                            ft.Container(
                                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                                border_radius=12,
                                bgcolor=Theme.INFO + "20",
                                content=ft.Text(
                                    f"{len(similar_ncs)} trouvée{'s' if len(similar_ncs) > 1 else ''}",
                                    size=11,
                                    color=Theme.INFO,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color=Theme.BG_TERTIARY),
                    ft.Column(
                        spacing=8,
                        scroll=ft.ScrollMode.AUTO,
                        controls=similar_items,
                    ),
                ],
            ),
        )
    
    def _build_detail_tab(self):
        """Construit le détail complet d'une NC avec recherche."""
        ncs = self.db.get_all_nc()
        search_controls = self._build_detail_search_controls(ncs)

        if not self.current_nc_id:
            return ft.Column(
                expand=True,
                spacing=15,
                controls=[
                    search_controls,
                    create_empty_state(
                        ft.Icons.SEARCH,
                        "Rechercher une NC",
                        "Utilisez la barre de recherche ou la liste déroulante pour sélectionner une NC.",
                    ),
                ],
            )

        nc = self.db.get_nc(self.current_nc_id)
        if not nc:
            return ft.Column(
                expand=True,
                spacing=15,
                controls=[
                    search_controls,
                    create_empty_state(
                        ft.Icons.ERROR,
                        "NC introuvable",
                        "Cette NC n'existe plus dans la base de données",
                    ),
                ],
            )

        # Parse JSON fields
        attachments = self._safe_json(nc.get('pieces_jointes'), [])
        immediate_actions = self._safe_json(nc.get('actions_immediates_table'), [])
        corrective_actions = self._safe_json(nc.get('actions_correctives_table'), [])
        
        # Extraire les 5M depuis les catégories Ishikawa
        analyse_details = self._safe_json(nc.get('analyse_details'), {})
        ishikawa_data = analyse_details.get('ishikawa', {}) if isinstance(analyse_details, dict) else {}
        ishikawa_categories = ishikawa_data.get('categories', {}) if isinstance(ishikawa_data, dict) else {}
        # Les 5M sélectionnés sont les clés des catégories qui ont des causes
        selected_5m = [cat for cat, causes in ishikawa_categories.items() if causes and any(c.strip() for c in causes if c)]
        
        fivewhy_data = analyse_details.get('5why', {}) if isinstance(analyse_details, dict) else {}
        fivewhy_whys = fivewhy_data.get('whys', []) if isinstance(fivewhy_data, dict) else []
        ishikawa_synth = ishikawa_data.get('synthesis', '') if isinstance(ishikawa_data, dict) else ''
        
        # Vérifier si les méthodologies sont cochées
        methode_analyse = nc.get('methode_analyse', '') or ''
        use_5why = '5 Pourquoi' in methode_analyse or '5 Why' in methode_analyse
        use_ishikawa = 'Ishikawa' in methode_analyse or '5M' in methode_analyse

        # Header avec boutons
        header_card = ft.Container(
            padding=20,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Column(
                        spacing=6,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Text(
                                        f"NC {nc.get('reference', '-')}",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=Theme.PRIMARY,
                                    ),
                                    StatusBadge(nc.get('statut', '')),
                                    SeverityBadge(nc.get('gravite', 'Mineure')),
                                ],
                            ),
                            ft.Text(nc.get('designation', '-') or nc.get('description', '-'), size=13, color=Theme.TEXT_PRIMARY),
                            ft.Row(
                                spacing=16,
                                controls=[
                                    ft.Row(spacing=6, controls=[ft.Icon(ft.Icons.CATEGORY, size=14, color=Theme.TEXT_MUTED), ft.Text(nc.get('type_nc', '-'), size=12, color=Theme.TEXT_SECONDARY)]),
                                    ft.Row(spacing=6, controls=[ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color=Theme.TEXT_MUTED), ft.Text(nc.get('date_detection', '-'), size=12, color=Theme.TEXT_SECONDARY)]),
                                    ft.Row(spacing=6, controls=[ft.Icon(ft.Icons.NUMBERS, size=14, color=Theme.TEXT_MUTED), ft.Text(nc.get('lot_serie', nc.get('numero_lot', '-')) or '-', size=12, color=Theme.TEXT_SECONDARY)]),
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=8,
                        controls=[
                            # Boutons de navigation
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK_IOS,
                                icon_size=20,
                                tooltip="NC précédente",
                                icon_color=Theme.PRIMARY,
                                bgcolor=Theme.BG_TERTIARY,
                                on_click=self._navigate_to_previous_nc,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ARROW_FORWARD_IOS,
                                icon_size=20,
                                tooltip="NC suivante",
                                icon_color=Theme.PRIMARY,
                                bgcolor=Theme.BG_TERTIARY,
                                on_click=self._navigate_to_next_nc,
                            ),
                            ft.Container(width=8),  # Séparateur
                            create_button("Exporter PDF", icon=ft.Icons.PICTURE_AS_PDF, style="secondary", on_click=lambda e, data=nc: self._export_nc_to_pdf(data)),
                            create_button("Modifier", icon=ft.Icons.EDIT, style="warning", on_click=lambda e, data=nc: self._open_form(data)),
                            create_button("Retour liste", icon=ft.Icons.LIST_ALT, style="secondary", on_click=lambda e: self._go_to_list_tab()),
                        ],
                    ),
                ],
            ),
        )

        # Section A - Identification
        identification_card = create_card(
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Text("A. Identification", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    ft.Container(
                        height=2,
                        border_radius=1,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(-1, 0),
                            end=ft.Alignment(1, 0),
                            colors=[Theme.PRIMARY, Theme.INFO],
                        ),
                    ),
                    ft.Row(
                        spacing=15,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Column(
                                expand=1,
                                spacing=6,
                                controls=[
                                    self._info_row("Référence", nc.get('reference', '-'), icon=ft.Icons.TAG),
                                    self._info_row("Date détection", nc.get('date_detection', '-'), icon=ft.Icons.CALENDAR_MONTH),
                                    self._info_row("Type de NC", nc.get('type_nc', '-'), icon=ft.Icons.CATEGORY),
                                    self._info_row("Origine", nc.get('origine', '-'), icon=ft.Icons.TRAVEL_EXPLORE),
                                    self._info_row("Type d'anomalie", nc.get('type_anomalie', '-'), icon=ft.Icons.BUG_REPORT),
                                ],
                            ),
                            ft.Column(
                                expand=1,
                                spacing=6,
                                controls=[
                                    self._info_row("Gravité", nc.get('gravite', '-'), icon=ft.Icons.WARNING_AMBER),
                                    self._info_row("Catégorie NC", nc.get('categorie_nc', '-'), icon=ft.Icons.FOLDER),
                                    self._info_row("Imputation", nc.get('imputation', '-'), icon=ft.Icons.ACCOUNT_TREE),
                                    self._info_row("Lieu détection", nc.get('lieu_detection', '-'), icon=ft.Icons.LOCATION_ON),
                                ],
                            ),
                        ],
                    ),
                    ft.Container(height=8),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.DESCRIPTION, size=18, color=Theme.PRIMARY),
                            ft.Text("Description du problème", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY, size=14),
                        ],
                    ),
                    ft.Container(
                        padding=16,
                        border_radius=8,
                        bgcolor=Theme.BG_TERTIARY,
                        border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                        content=ft.Text(
                            nc.get('description', '-') or 'Non renseigné',
                            size=13,
                            color=Theme.TEXT_PRIMARY if nc.get('description') else Theme.TEXT_MUTED,
                            max_lines=None,
                            weight=ft.FontWeight.W_400,
                        ),
                    ),
                    ft.Container(height=10),
                    ft.Text("> Produit et traçabilité", size=14, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
                    ft.Container(
                        padding=16,
                        border_radius=8,
                        bgcolor=Theme.BG_SECONDARY,
                        border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                        content=ft.Column(
                            spacing=12,
                            controls=[
                                self._info_row("Produit concerné", nc.get('produit_concerne', '-'), icon=ft.Icons.INVENTORY, multiline=True),
                                ft.Divider(height=1, color=Theme.BG_TERTIARY),
                                ft.Row(
                                    spacing=15,
                                    controls=[
                                        ft.Column(
                                            expand=1,
                                            spacing=6,
                                            controls=[
                                                self._info_row("Lot / Série", nc.get('lot_serie', '-') or '-', icon=ft.Icons.QR_CODE),
                                            ],
                                        ),
                                        ft.Column(
                                            expand=1,
                                            spacing=6,
                                            controls=[
                                                self._info_row("Quantité affectée", str(nc.get('quantite_affectee', '-')), icon=ft.Icons.NUMBERS),
                                            ],
                                        ),
                                    ],
                                ),
                                ft.Divider(height=1, color=Theme.BG_TERTIARY),
                                self._info_row("Matières réclamées", nc.get('matieres_reclames', '-') or 'Aucune', icon=ft.Icons.CATEGORY, multiline=True),
                            ],
                        ),
                    ),
                    ft.Container(height=4),
                    ft.Text("Pièces jointes", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY, size=13),
                    self._build_attachments_viewer(attachments) if attachments else ft.Text("Aucune pièce jointe", color=Theme.TEXT_MUTED, size=12, italic=True),
                ],
            ),
        )

        # Section B - Analyse causale
        fivewhy_controls = []
        for idx, why in enumerate(fivewhy_whys):
            if not why:
                continue
            fivewhy_controls.append(
                ft.Container(
                    padding=12,
                    border_radius=8,
                    bgcolor=Theme.BG_TERTIARY,
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Icon(ft.Icons.HELP_OUTLINE, size=16, color=Theme.SECONDARY),
                                    ft.Text(f"Pourquoi {idx+1}?", size=12, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                                ]
                            ),
                            ft.Text(f"> {why}", size=12, color=Theme.TEXT_SECONDARY, max_lines=None),
                        ],
                    ),
                )
            )

        ishikawa_controls = []
        for cat, causes in ishikawa_categories.items():
            if not causes:
                continue
            ishikawa_controls.append(
                ft.Container(
                    padding=12,
                    border_radius=8,
                    bgcolor=Theme.BG_TERTIARY,
                    border=ft.Border(
                top=ft.BorderSide(1, Theme.BG_TERTIARY),
                right=ft.BorderSide(1, Theme.BG_TERTIARY),
                bottom=ft.BorderSide(1, Theme.BG_TERTIARY),
                left=ft.BorderSide(1, Theme.BG_TERTIARY),
            ),
                    content=ft.Column(
                        spacing=6,
                        controls=[
                            ft.Row(spacing=6, controls=[ft.Icon(ft.Icons.CATEGORY, size=16, color=Theme.PRIMARY), ft.Text(cat, size=13, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)]),
                            ft.Column(spacing=4, controls=[ft.Text(f"* {c}", size=12, color=Theme.TEXT_SECONDARY, max_lines=None) for c in causes if c]),
                        ],
                    ),
                )
            )

        analysis_card = create_card(
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Text("B. Analyse causale", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    ft.Container(
                        height=2,
                        border_radius=1,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(-1, 0),
                            end=ft.Alignment(1, 0),
                            colors=[Theme.WARNING, Theme.PRIMARY],
                        ),
                    ),
                    ft.Row(
                        spacing=8,
                        wrap=True,
                        controls=[
                            ft.Text("Méthode(s) d'analyse:", size=13, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                            self._pill(nc.get('methode_analyse', '-') or '-'),
                        ],
                    ),
                    ft.Container(height=8),
                    # Cause racine affichée seulement si aucune méthode cochée
                    *(
                        [
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.TROUBLESHOOT, size=18, color=Theme.WARNING),
                                    ft.Text("Cause racine identifiée", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY, size=14),
                                ],
                            ),
                            ft.Container(
                                padding=16,
                                border_radius=8,
                                bgcolor=Theme.BG_TERTIARY,
                                border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                                content=ft.Text(
                                    nc.get('cause_racine', '-') or 'Non identifiée',
                                    size=13,
                                    color=Theme.TEXT_PRIMARY if nc.get('cause_racine') else Theme.TEXT_MUTED,
                                    max_lines=None,
                                    weight=ft.FontWeight.W_400,
                                ),
                            ),
                            ft.Container(height=8),
                        ] if (not use_5why and not use_ishikawa) else []
                    ),
                    # Visualisation 5M (afficher seulement si méthode cochée ET données présentes)
                    *(
                        [
                            ft.Container(height=8),
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.BUBBLE_CHART, size=18, color=Theme.PRIMARY),
                                    ft.Text("Analyse des 5M", size=14, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
                                ],
                            ),
                            self._build_5m_visual_display(ishikawa_categories),
                            ft.Container(height=8),
                            # Cause racine après 5M
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.TROUBLESHOOT, size=18, color=Theme.WARNING),
                                    ft.Text("Cause racine identifiée", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY, size=14),
                                ],
                            ),
                            ft.Container(
                                padding=16,
                                border_radius=8,
                                bgcolor=Theme.BG_TERTIARY,
                                border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                                content=ft.Text(
                                    nc.get('cause_racine', '-') or 'Non identifiée',
                                    size=13,
                                    color=Theme.TEXT_PRIMARY if nc.get('cause_racine') else Theme.TEXT_MUTED,
                                    max_lines=None,
                                    weight=ft.FontWeight.W_400,
                                ),
                            ),
                        ] if (use_ishikawa and selected_5m) else []
                    ),
                    ft.Container(height=10),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.RADAR, size=18, color=Theme.DANGER),
                            ft.Text("Portée de la NC", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY, size=14),
                            ft.Container(
                                padding=ft.Padding(left=8, right=8, top=2, bottom=2),
                                border_radius=4,
                                bgcolor=Theme.DANGER if nc.get('analyse_portee') and len(nc.get('analyse_portee', '')) > 10 else Theme.BG_TERTIARY,
                                content=ft.Text(
                                    "Critique" if nc.get('analyse_portee') and len(nc.get('analyse_portee', '')) > 10 else "À définir",
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE if nc.get('analyse_portee') and len(nc.get('analyse_portee', '')) > 10 else Theme.TEXT_MUTED,
                                ),
                            ),
                        ],
                    ),
                    ft.Container(
                        padding=16,
                        border_radius=8,
                        bgcolor=Theme.BG_TERTIARY,
                        border=ft.Border(
                            top=ft.BorderSide(2, Theme.DANGER if (nc.get('analyse_portee') and len(nc.get('analyse_portee', '')) > 10) else Theme.OUTLINE),
                            right=ft.BorderSide(2, Theme.DANGER if (nc.get('analyse_portee') and len(nc.get('analyse_portee', '')) > 10) else Theme.OUTLINE),
                            bottom=ft.BorderSide(2, Theme.DANGER if (nc.get('analyse_portee') and len(nc.get('analyse_portee', '')) > 10) else Theme.OUTLINE),
                            left=ft.BorderSide(2, Theme.DANGER if (nc.get('analyse_portee') and len(nc.get('analyse_portee', '')) > 10) else Theme.OUTLINE),
                        ),
                        content=ft.Text(
                            nc.get('analyse_portee', '-') or 'La portée de la non-conformité n\'a pas encore été analysée',
                            size=13,
                            color=Theme.TEXT_PRIMARY if nc.get('analyse_portee') else Theme.TEXT_MUTED,
                            max_lines=None,
                            weight=ft.FontWeight.W_500 if nc.get('analyse_portee') else ft.FontWeight.W_400,
                            italic=not nc.get('analyse_portee'),
                        ),
                    ),
                    # N'afficher 5 Pourquoi que si la méthodologie est cochée
                    *(
                        [
                            ft.Container(height=8),
                            ft.Text("Analyse 5 Pourquoi", size=14, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
                            ft.Column(spacing=6, controls=fivewhy_controls if fivewhy_controls else [ft.Text("Non renseigné", size=12, color=Theme.TEXT_MUTED, italic=True)]),
                            ft.Container(height=8),
                            # Cause racine après 5WHY
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.TROUBLESHOOT, size=18, color=Theme.WARNING),
                                    ft.Text("Cause racine identifiée", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY, size=14),
                                ],
                            ),
                            ft.Container(
                                padding=16,
                                border_radius=8,
                                bgcolor=Theme.BG_TERTIARY,
                                border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                                content=ft.Text(
                                    fivewhy_data.get('root_cause') or nc.get('cause_racine', '-') or 'Non identifiée',
                                    size=13,
                                    color=Theme.TEXT_PRIMARY if (fivewhy_data.get('root_cause') or nc.get('cause_racine')) else Theme.TEXT_MUTED,
                                    max_lines=None,
                                    weight=ft.FontWeight.W_400,
                                ),
                            ),
                        ] if use_5why else []
                    ),
                ],
            ),
        )

        # Section C - Actions
        actions_card = create_card(
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Text("C. Actions (immédiates et correctives)", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    ft.Container(
                        height=2,
                        border_radius=1,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(-1, 0),
                            end=ft.Alignment(1, 0),
                            colors=[Theme.SUCCESS, Theme.PRIMARY],
                        ),
                    ),
                    ft.Text("Actions immédiates (Corrections)", size=14, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
                    ft.Container(
                        padding=10,
                        border_radius=8,
                        bgcolor=Theme.BG_TERTIARY,
                        content=self._build_actions_table(immediate_actions, is_immediate=True) if immediate_actions else ft.Text("Aucune action immédiate définie", color=Theme.TEXT_MUTED, size=12, italic=True),
                    ),
                    ft.Container(height=8),
                    ft.Text("Actions correctives", size=14, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
                    ft.Container(
                        padding=10,
                        border_radius=8,
                        bgcolor=Theme.BG_TERTIARY,
                        content=self._build_actions_table(corrective_actions, is_immediate=False) if corrective_actions else ft.Text("Aucune action corrective définie", color=Theme.TEXT_MUTED, size=12, italic=True),
                    ),
                ],
            ),
        )

        # Section D - Clôture
        closure_card = create_card(
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Text("D. Clôture et validation", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    ft.Container(
                        height=2,
                        border_radius=1,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(-1, 0),
                            end=ft.Alignment(1, 0),
                            colors=[Theme.DANGER, Theme.WARNING],
                        ),
                    ),
                    ft.Row(
                        spacing=15,
                        controls=[
                            ft.Column(
                                expand=1,
                                spacing=6,
                                controls=[
                                    self._info_row("Statut", nc.get('statut', '-'), icon=ft.Icons.FLAG),
                                    self._info_row("Date de clôture", nc.get('date_cloture', '-') or 'Non clôturée', icon=ft.Icons.EVENT_AVAILABLE),
                                ],
                            ),
                            ft.Column(
                                expand=1,
                                spacing=6,
                                controls=[
                                    self._info_row("Vérificateur", nc.get('verificateur', '-') or 'Non assigné', icon=ft.Icons.PERSON),
                                    self._info_row("Efficacité des actions", nc.get('efficacite', '-') or 'Non évaluée', icon=ft.Icons.TRACK_CHANGES),
                                ],
                            ),
                        ],
                    ),
                    ft.Container(height=4),
                    ft.Text("Commentaires de clôture", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY, size=13),
                    ft.Container(
                        padding=12,
                        border_radius=8,
                        bgcolor=Theme.BG_PRIMARY,
                        content=ft.Text(nc.get('commentaires_cloture', '-') or 'Aucun commentaire', size=13, color=Theme.TEXT_SECONDARY, max_lines=None),
                    ),
                ],
            ),
        )

        return ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=15,
            controls=[
                search_controls,
                header_card,
                self._build_nc_timeline(nc),  # Timeline chronologique
                identification_card,
                analysis_card,
                self._build_costs_section(nc),  # Coûts CNQ détaillés
                actions_card,
                closure_card,
                self._build_history_section(nc),  # Historique des modifications
                self._build_similar_ncs_section(nc),  # NC similaires (en bas)
            ],
        )

    def _build_detail_search_controls(self, ncs: List[Dict]) -> ft.Container:
        """Barre de recherche/sélection améliorée avec filtrage dynamique par statut."""
        
        # Filtrer les NC selon le statut sélectionné
        if self.detail_status_filter == "En cours":
            filtered_ncs = [nc for nc in ncs if nc.get('statut') == 'En cours']
        elif self.detail_status_filter == "Clôturées":
            filtered_ncs = [nc for nc in ncs if nc.get('statut') == 'Clôturée']
        else:  # "Tout"
            filtered_ncs = ncs
        
        # Extraire les références filtrées
        refs = sorted({(nc.get('reference') or '').strip() for nc in filtered_ncs if (nc.get('reference') or '').strip()})
        
        # Boutons radio pour le filtre de statut (Choice Chips style)
        def create_filter_chip(label: str, value: str):
            is_selected = self.detail_status_filter == value
            return ft.Container(
                padding=ft.Padding(left=16, right=16, top=8, bottom=8),
                border_radius=20,
                bgcolor=Theme.PRIMARY if is_selected else Theme.BG_SECONDARY,
                border=ft.Border(
                top=ft.BorderSide(2, Theme.PRIMARY if is_selected else Theme.BG_TERTIARY),
                right=ft.BorderSide(2, Theme.PRIMARY if is_selected else Theme.BG_TERTIARY),
                bottom=ft.BorderSide(2, Theme.PRIMARY if is_selected else Theme.BG_TERTIARY),
                left=ft.BorderSide(2, Theme.PRIMARY if is_selected else Theme.BG_TERTIARY),
            ),
                content=ft.Text(
                    label,
                    size=13,
                    weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                    color=ft.Colors.WHITE if is_selected else Theme.TEXT_PRIMARY,
                ),
                on_click=lambda e, v=value: self._on_detail_status_filter_change(v),
                ink=True,
            )
        
        filter_chips = ft.Row(
            spacing=10,
            controls=[
                create_filter_chip("Tout", "Tout"),
                create_filter_chip("En cours", "En cours"),
                create_filter_chip("Clôturées", "Clôturées"),
            ],
        )
        
        # Champ de recherche texte avec autocomplétion
        search_field = ft.TextField(
            label="Rechercher par référence",
            hint_text="Tapez pour rechercher...",
            prefix_icon=ft.Icons.SEARCH,
            value=self.detail_search_value,
            width=280,
            text_size=13,
            on_change=lambda e: self._on_detail_search_change(e.control.value),
            on_submit=lambda e: self._trigger_detail_search(),
        )
        
        # Dropdown avec hauteur de menu limitée (même que dans le formulaire)
        nc_dropdown = ft.Dropdown(
            label="Ou sélectionner une NC",
            hint_text="Choisissez dans la liste",
            options=[DropdownOption(r) for r in refs],
            value=self.detail_selected_ref if self.detail_selected_ref in refs else None,
            width=280,
            on_change=self._on_detail_dropdown_change,
            text_size=13,
            menu_height=240,  # Limite à 5 items visibles (48px par item x 5 = 240px)
        )
        
        # Boutons d'action
        search_button = create_button(
            "Rechercher",
            icon=ft.Icons.SEARCH,
            on_click=lambda e: self._trigger_detail_search(),
            style="primary",
        )
        
        reset_button = create_button(
            "Réinitialiser",
            icon=ft.Icons.REFRESH,
            on_click=lambda e: self._reset_detail_search(),
            style="secondary",
        )
        
        return ft.Container(
            padding=ft.Padding(left=12, right=12, top=8, bottom=8),
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.FILTER_ALT, size=18, color=Theme.TEXT_MUTED),
                            ft.Text("Filtrer par statut:", size=13, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                        ],
                    ),
                    filter_chips,
                    ft.Divider(height=1, color=Theme.BG_TERTIARY),
                    ft.Row(
                        spacing=10,
                        wrap=True,
                        controls=[
                            search_field,
                            nc_dropdown,
                            search_button,
                            reset_button,
                        ],
                    ),
                    ft.Text(
                        f"{len(refs)} NC disponible{'s' if len(refs) > 1 else ''}",
                        size=12,
                        color=Theme.TEXT_MUTED,
                        italic=True,
                    ),
                ],
            ),
        )
    
    def _on_detail_status_filter_change(self, new_filter: str):
        """Change le filtre de statut et rafraîchit la zone de recherche."""
        self.detail_status_filter = new_filter
        self.detail_selected_ref = ""  # Réinitialiser la sélection
        self.detail_search_value = ""  # Réinitialiser le champ de recherche
        self.current_nc_id = None  # Réinitialiser la NC sélectionnée
        self.tab_content.content = self._build_detail_tab()
        self.page.update()
    
    def _reset_detail_search(self):
        """Réinitialise tous les paramètres de recherche de l'onglet Détail."""
        self.detail_status_filter = "Tout"
        self.detail_selected_ref = ""
        self.detail_search_value = ""
        self.current_nc_id = None
        self.tab_content.content = self._build_detail_tab()
        self.page.update()

    def _on_detail_search_change(self, value: str):
        self.detail_search_value = value or ""

    def _on_detail_dropdown_change(self, e):
        self.detail_selected_ref = e.control.value or ""
        if self.detail_selected_ref:
            self._trigger_detail_search(from_dropdown=True)

    def _trigger_detail_search(self, from_dropdown: bool = False):
        """Recherche une NC et l'affiche dans l'onglet Détail."""
        query = self.detail_selected_ref if from_dropdown else (self.detail_search_value or self.detail_selected_ref)
        if not query:
            create_snackbar(self.page, "Saisissez ou choisissez une référence", "warning")
            return

        nc = self.db.find_nc(query)
        if not nc:
            create_snackbar(self.page, "Aucune NC trouvée pour cette référence", "error")
            return

        self.current_nc_id = nc['id']
        self.detail_search_value = query
        self.detail_selected_ref = nc.get('reference', '') or query
        self.tab_content.content = self._build_detail_tab()
        self.page.update()
    
    def _export_nc_to_pdf(self, nc: Dict):
        """Exporte la NC en PDF avec un rapport complet."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.units import cm
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            import os
            from datetime import datetime
            
            # Date et heure d'export
            now = datetime.now()
            export_datetime = now.strftime('%d/%m/%Y à %H:%M')
            
            # Nom de fichier par défaut
            reference = nc.get('reference', 'NC').replace('/', '_')
            default_filename = f"NC_{reference}_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Créer le FilePicker pour choisir l'emplacement
            def on_file_picker_result(e: ft.FilePickerResultEvent):
                if e.path:
                    # L'utilisateur a choisi un emplacement
                    try:
                        filepath = e.path
                        # S'assurer que l'extension .pdf est présente
                        if not filepath.lower().endswith('.pdf'):
                            filepath += '.pdf'
                        
                        print(f"[PDF] Génération du PDF vers: {filepath}")
                        self._generate_pdf_file(filepath, nc, now, export_datetime)
                        print(f"[PDF] PDF généré avec succès: {filepath}")
                    except Exception as ex:
                        print(f"[PDF] Erreur génération PDF: {ex}")
                        import traceback
                        traceback.print_exc()
                        create_snackbar(self.page, f"Erreur lors de la génération du PDF: {str(ex)}", "error")
            
            # Créer et configurer le FilePicker
            file_picker = ft.FilePicker(on_result=on_file_picker_result)
            self.page.overlay.append(file_picker)
            self.page.update()
            
            # Ouvrir le dialogue de sauvegarde
            file_picker.save_file(
                dialog_title="Enregistrer le PDF de la NC",
                file_name=default_filename,
                allowed_extensions=["pdf"],
                file_type=ft.FilePickerFileType.CUSTOM,
            )
            
        except Exception as e:
            print(f"Erreur export PDF: {e}")
            import traceback
            traceback.print_exc()
            create_snackbar(self.page, f"Erreur lors de l'export PDF: {str(e)}", "error")
    
    def _generate_pdf_file(self, filepath: str, nc: Dict, now, export_datetime: str):
        """Génère le fichier PDF à l'emplacement spécifié."""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.units import cm
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.platypus import PageBreak, Image
        from reportlab.lib.utils import ImageReader
        import os
        import html
        from PIL import Image as PILImage, ImageOps
        
        # Fonction pour échapper les caractères HTML spéciaux
        def escape_html(text):
            """Échappe les caractères HTML spéciaux pour ReportLab."""
            if text is None or text == '-':
                return text or '-'
            return html.escape(str(text))
        
        # Fonction pour créer l'en-tête et le pied de page
        def add_header_footer(canvas, doc):
            """Ajoute en-tête et pied de page à chaque page."""
            canvas.saveState()
            
            # En-tête
            # Logo entreprise (si existe)
            # Essayer plusieurs chemins possibles
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            
            possible_paths = [
                os.path.join(parent_dir, 'assets', 'logo_entreprise.png'),
                os.path.join(os.getcwd(), 'assets', 'logo_entreprise.png'),
                'assets/logo_entreprise.png',
            ]
            
            logo_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    logo_path = path
                    print(f"[PDF] Logo trouvé: {logo_path}")
                    break
                else:
                    print(f"[PDF] Logo non trouvé: {path}")
            
            if logo_path:
                try:
                    # Charger le PNG
                    pil_img = PILImage.open(logo_path)
                    print(f"[PDF] Image originale: mode={pil_img.mode}, taille={pil_img.size}")
                    
                    # Traitement spécial pour mode LA (gris + alpha)
                    if pil_img.mode == 'LA':
                        # Extraire le canal alpha
                        luminance, alpha = pil_img.split()
                        
                        # Vérifier si l'image est blanche avec alpha transparent
                        # Inverser le canal alpha pour en faire l'image (noir sur blanc)
                        from PIL import ImageOps
                        # Utiliser le canal alpha comme image (car le logo est probablement dans l'alpha)
                        gray_img = ImageOps.invert(alpha)  # Inverser l'alpha
                        pil_img = gray_img.convert('RGB')
                    elif pil_img.mode in ('RGBA', 'P'):
                        # Couleur avec alpha -> RGB avec fond blanc
                        background = PILImage.new('RGB', pil_img.size, (255, 255, 255))
                        if pil_img.mode == 'P':
                            pil_img = pil_img.convert('RGBA')
                        background.paste(pil_img, (0, 0), pil_img.split()[-1])
                        pil_img = background
                    elif pil_img.mode == 'L':
                        # Niveaux de gris sans alpha -> RGB
                        pil_img = pil_img.convert('RGB')
                    elif pil_img.mode != 'RGB':
                        pil_img = pil_img.convert('RGB')
                    
                    print(f"[PDF] Image convertie en: mode={pil_img.mode}")
                    
                    # Logo en haut à gauche (position ajustée pour ne pas chevaucher la ligne)
                    img_reader = ImageReader(pil_img)
                    canvas.drawImage(img_reader, 2*cm, A4[1] - 1.8*cm, width=3.5*cm, height=1.3*cm, preserveAspectRatio=True)
                    print(f"[PDF] Logo inséré avec succès")
                        
                except Exception as e:
                    print(f"[PDF] ERREUR affichage logo: {type(e).__name__}: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"[PDF] Aucun logo trouvé dans les chemins testés")
            
            # Titre document en haut à droite
            canvas.setFont('Helvetica-Bold', 12)
            canvas.setFillColor(colors.HexColor('#3B82F6'))
            canvas.drawRightString(A4[0] - 2*cm, A4[1] - 1.3*cm, "FICHE DE NON-CONFORMITÉ")
            
            # Mentions ISO sous le titre
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(colors.HexColor('#666666'))
            canvas.drawRightString(A4[0] - 2*cm, A4[1] - 1.6*cm, "Conforme ISO 9001:2015 / IATF 16949")
            
            # Ligne de séparation (sous le logo et le titre)
            canvas.setStrokeColor(colors.HexColor('#3B82F6'))
            canvas.setLineWidth(2)
            canvas.line(2*cm, A4[1] - 2.1*cm, A4[0] - 2*cm, A4[1] - 2.1*cm)
            
            # Pied de page
            # Ligne de séparation
            canvas.setStrokeColor(colors.HexColor('#CCCCCC'))
            canvas.setLineWidth(1)
            canvas.line(2*cm, 1.5*cm, A4[0] - 2*cm, 1.5*cm)
            
            # Informations à gauche
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(colors.grey)
            canvas.drawString(2*cm, 1.2*cm, f"Document généré le {export_datetime}")
            canvas.drawString(2*cm, 0.9*cm, f"Référence: NC-{nc.get('reference', '-')}")
            
            # Numéro de page à droite
            page_num = canvas.getPageNumber()
            canvas.drawRightString(A4[0] - 2*cm, 1.2*cm, f"Page {page_num}")
            canvas.drawRightString(A4[0] - 2*cm, 0.9*cm, "QualiManager ERP")
            
            canvas.restoreState()
        
        try:
            print(f"[PDF] Début génération PDF: {filepath}")
            
            # Vérifier que le dossier parent existe
            parent_dir = os.path.dirname(filepath)
            if parent_dir and not os.path.exists(parent_dir):
                print(f"[PDF] Création du dossier: {parent_dir}")
                os.makedirs(parent_dir, exist_ok=True)
            
            # Créer le document avec marges augmentées pour en-tête/pied de page
            doc = SimpleDocTemplate(
                filepath, 
                pagesize=A4, 
                topMargin=3*cm,  # Augmenté pour l'en-tête
                bottomMargin=2.5*cm,  # Augmenté pour le pied de page
                leftMargin=2*cm,
                rightMargin=2*cm
            )
            story = []
            styles = getSampleStyleSheet()
            
            print(f"[PDF] Document créé, construction du contenu...")
            
            # Style personnalisé
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#3B82F6'),
                spaceAfter=6,
                alignment=TA_CENTER,
            )
            
            export_date_style = ParagraphStyle(
                'ExportDate',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.grey,
                spaceAfter=12,
                alignment=TA_CENTER,
                italic=True,
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#1E40AF'),
                spaceAfter=10,
                spaceBefore=15,
            )
            
            wrapped_style = ParagraphStyle(
                'Wrapped',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_LEFT,
                wordWrap='CJK',
            )
            
            # Titre avec date/heure d'export
            story.append(Paragraph(f"<b>Non-Conformité {nc.get('reference', '-')}</b>", title_style))
            story.append(Paragraph(f"Exporté le {export_datetime}", export_date_style))
            story.append(Paragraph(f"{nc.get('designation', '-') or nc.get('description', '-')}", styles['Normal']))
            story.append(Spacer(1, 0.5*cm))
            
            # Section A - Identification avec wrapping
            story.append(Paragraph("<b>A. IDENTIFICATION</b>", heading_style))
            
            data_identification = [
                ['Référence', Paragraph(escape_html(nc.get('reference', '-')), wrapped_style)],
                ['Date détection', Paragraph(escape_html(nc.get('date_detection', '-')), wrapped_style)],
                ['Type de NC', Paragraph(escape_html(nc.get('type_nc', '-')), wrapped_style)],
                ['Origine', Paragraph(escape_html(nc.get('origine', '-')), wrapped_style)],
                ['Gravité', Paragraph(escape_html(nc.get('gravite', '-')), wrapped_style)],
                ['Statut', Paragraph(escape_html(nc.get('statut', '-')), wrapped_style)],
                ['Produit concerné', Paragraph(escape_html(nc.get('produit_concerne', '-') or '-'), wrapped_style)],
                ['Lot/Série', Paragraph(escape_html(nc.get('lot_serie', '-') or '-'), wrapped_style)],
                ['Quantité affectée', Paragraph(escape_html(str(nc.get('quantite_affectee', '-'))), wrapped_style)],
            ]
        
            table_id = Table(data_identification, colWidths=[5*cm, 11*cm])
            table_id.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E0E7FF')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(table_id)
            story.append(Spacer(1, 0.5*cm))
        
            # Description
            story.append(Paragraph("<b>Description du problème:</b>", styles['Heading3']))
            story.append(Paragraph(escape_html(nc.get('description', 'Non renseignée')), wrapped_style))
            story.append(Spacer(1, 0.5*cm))
        
            # Section B - Analyse causale
            story.append(Paragraph("<b>B. ANALYSE CAUSALE</b>", heading_style))
            methode_analyse = nc.get('methode_analyse', '') or ''
            story.append(Paragraph(f"<b>Méthode(s) d'analyse:</b> {escape_html(methode_analyse if methode_analyse else '-')}", styles['Normal']))
            
            # Déterminer quelles analyses afficher
            use_ishikawa = 'Ishikawa' in methode_analyse or '5M' in methode_analyse
            use_5why = '5 Pourquoi' in methode_analyse or '5 Why' in methode_analyse or '5Why' in methode_analyse
            
            # Afficher cause racine seulement si aucune méthode n'est cochée
            if not use_ishikawa and not use_5why:
                story.append(Paragraph(f"<b>Cause racine:</b> {escape_html(nc.get('cause_racine', 'Non identifiée'))}", wrapped_style))
        
            # Analyse 5M si activée
        
            if use_ishikawa:
                analyse_details = self._safe_json(nc.get('analyse_details'), {})
                ishikawa_data = analyse_details.get('ishikawa', {}) if isinstance(analyse_details, dict) else {}
                ishikawa_categories = ishikawa_data.get('categories', {}) if isinstance(ishikawa_data, dict) else {}
            
                if ishikawa_categories:
                    has_causes = any(causes and any(c.strip() for c in causes if c) for causes in ishikawa_categories.values())
                    if has_causes:
                        story.append(Spacer(1, 0.3*cm))
                        story.append(Paragraph("<b>Analyse 5M (Ishikawa):</b>", styles['Heading3']))
                    
                        for m_name, causes in ishikawa_categories.items():
                            valid_causes = [c.strip() for c in causes if c and c.strip()]
                            if valid_causes:
                                story.append(Paragraph(f"<b>{escape_html(m_name)}:</b>", styles['Normal']))
                                for cause in valid_causes:
                                    story.append(Paragraph(f"  * {escape_html(cause)}", wrapped_style))
                                story.append(Spacer(1, 0.2*cm))
                    
                    # Afficher cause racine après 5M
                    if nc.get('cause_racine'):
                        story.append(Spacer(1, 0.2*cm))
                        story.append(Paragraph(f"<b>Cause racine identifiée:</b> {escape_html(nc.get('cause_racine'))}", wrapped_style))
        
            # Analyse 5Why si activée
        
            if use_5why:
                if not 'analyse_details' in locals():
                    analyse_details = self._safe_json(nc.get('analyse_details'), {})
                fivewhy_data = analyse_details.get('5why', {}) if isinstance(analyse_details, dict) else {}
                if fivewhy_data and fivewhy_data.get('whys'):
                    story.append(Spacer(1, 0.3*cm))
                    story.append(Paragraph("<b>Analyse 5 Pourquoi:</b>", styles['Heading3']))
                    for i, why in enumerate(fivewhy_data.get('whys', []), 1):
                        if why and why.strip():
                            story.append(Paragraph(f"{i}. {escape_html(why)}", wrapped_style))
                    # Afficher cause racine (soit de 5Why soit du champ général)
                    root_cause = fivewhy_data.get('root_cause') or nc.get('cause_racine')
                    if root_cause:
                        story.append(Paragraph(f"<b>Cause racine identifiée:</b> {escape_html(root_cause)}", wrapped_style))
        
            story.append(Paragraph(f"<b>Portée de la NC:</b> {escape_html(nc.get('analyse_portee', 'Non analysée'))}", wrapped_style))
            story.append(Spacer(1, 0.5*cm))
        
            # Section C - Actions immédiates (Corrections)
            immediate_actions = self._safe_json(nc.get('actions_immediates_table'), [])
            if immediate_actions and any(a.get('correction') for a in immediate_actions):
                story.append(Paragraph("<b>C. CORRECTIONS (Actions immédiates)</b>", heading_style))
                data_corrections = [['Correction', 'Responsable', 'Date', 'Coût (EUR)']]
                for action in immediate_actions:
                    if action.get('correction'):
                        data_corrections.append([
                            Paragraph(escape_html(action.get('correction', '-')), wrapped_style),
                            Paragraph(escape_html(action.get('responsable', '-')), wrapped_style),
                            Paragraph(escape_html(action.get('date', '-')), wrapped_style),
                            Paragraph(escape_html(str(action.get('cost', '0'))), wrapped_style),
                        ])
            
                table_corrections = Table(data_corrections, colWidths=[7*cm, 4*cm, 3*cm, 2*cm])
                table_corrections.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                story.append(table_corrections)
                story.append(Spacer(1, 0.5*cm))
        
            # Section C - Actions correctives
            corrective_actions = self._safe_json(nc.get('actions_correctives_table'), [])
            if corrective_actions and any(a.get('desc') for a in corrective_actions):
                story.append(Paragraph("<b>C. ACTIONS CORRECTIVES</b>", heading_style))
                data_actions = [['Action', 'Responsable', 'Échéance', 'Statut', 'Coût (EUR)']]
                for action in corrective_actions:
                    if action.get('desc'):
                        data_actions.append([
                            Paragraph(escape_html(action.get('desc', '-')), wrapped_style),
                            Paragraph(escape_html(action.get('responsable', '-')), wrapped_style),
                            Paragraph(escape_html(action.get('date_echeance', '-') or action.get('date_fin', '-')), wrapped_style),
                            Paragraph(escape_html(action.get('statut', '-')), wrapped_style),
                            Paragraph(escape_html(str(action.get('cost', '0'))), wrapped_style),
                        ])
            
                table_actions = Table(data_actions, colWidths=[6*cm, 3.5*cm, 2.5*cm, 2.5*cm, 1.5*cm])
                table_actions.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                story.append(table_actions)
                story.append(Spacer(1, 0.5*cm))
        
            # Section Coûts
            story.append(Paragraph("<b>COÛTS CNQ</b>", heading_style))
        
            # Calculer les coûts depuis les tableaux
            cout_corrections = sum(float(str(a.get('cost', 0)).replace(',', '.')) if str(a.get('cost', 0)) else 0 for a in immediate_actions)
            cout_actions = sum(float(str(a.get('cost', 0)).replace(',', '.')) if str(a.get('cost', 0)) else 0 for a in corrective_actions)
            cout_total = cout_corrections + cout_actions
        
            data_couts = [
                ['Type de coût', 'Montant'],
                ['Coût Corrections', f"{cout_corrections:,.2f} EUR"],
                ['Coût Actions correctives', f"{cout_actions:,.2f} EUR"],
                ['TOTAL', f"{cout_total:,.2f} EUR"],
            ]
        
            table_couts = Table(data_couts, colWidths=[10*cm, 6*cm])
            table_couts.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FEE2E2')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(table_couts)
            story.append(Spacer(1, 0.5*cm))
        
            # Section D - Clôture
            story.append(Paragraph("<b>D. CLÔTURE</b>", heading_style))
            story.append(Paragraph(f"<b>Date de clôture:</b> {escape_html(nc.get('date_cloture', 'Non clôturée'))}", styles['Normal']))
            story.append(Paragraph(f"<b>Vérificateur:</b> {escape_html(nc.get('verificateur', 'Non assigné'))}", styles['Normal']))
            story.append(Paragraph(f"<b>Efficacité:</b> {escape_html(nc.get('efficacite', 'Non évaluée'))}", styles['Normal']))
        
            # Générer le PDF avec en-tête et pied de page
            print(f"[PDF] Construction du document PDF...")
            doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
            print(f"[PDF] Document PDF construit avec succès")
        
            # Vérifier que le fichier existe
            if not os.path.exists(filepath):
                raise Exception(f"Le fichier PDF n'a pas été créé: {filepath}")
            
            file_size = os.path.getsize(filepath)
            print(f"[PDF] Fichier créé: {filepath} ({file_size} octets)")
        
            # Extraire le nom de fichier et le dossier
            filename = os.path.basename(filepath)
            folder_path = os.path.dirname(filepath)
        
            # Ouvrir automatiquement le dossier contenant le PDF
            import subprocess
            try:
                print(f"[PDF] Ouverture de l'explorateur...")
                subprocess.Popen(f'explorer /select,"{filepath}"')
            except Exception as ex:
                print(f"[PDF] Erreur ouverture explorateur: {ex}")
        
            # Afficher un snackbar de confirmation
            create_snackbar(self.page, f"[OK] PDF généré avec succès : {filename} ({file_size} octets)", "success")
            self.page.update()
        
        except Exception as e:
            print(f"[PDF] ERREUR lors de la génération: {e}")
            import traceback
            traceback.print_exc()
            create_snackbar(self.page, f"[Erreur] Erreur lors de l'export PDF: {str(e)}", "error")
            raise
    
    def _navigate_to_previous_nc(self, e=None):
        """Navigue vers la NC précédente dans la liste."""
        if not self.current_nc_id:
            create_snackbar(self.page, "Aucune NC sélectionnée", "warning")
            return
        
        # Récupérer toutes les NC triées par référence
        all_ncs = self.db.get_all_nc()
        if not all_ncs:
            return
        
        # Trier par ID pour respecter l'ordre chronologique
        sorted_ncs = sorted(all_ncs, key=lambda x: x.get('id', 0))
        
        # Trouver l'index actuel
        current_index = next((i for i, nc in enumerate(sorted_ncs) if nc.get('id') == self.current_nc_id), None)
        
        if current_index is None:
            create_snackbar(self.page, "NC actuelle introuvable", "error")
            return
        
        # Si première NC, boucler vers la dernière
        if current_index == 0:
            previous_nc = sorted_ncs[-1]
            create_snackbar(self.page, "Retour à la dernière NC", "info")
        else:
            previous_nc = sorted_ncs[current_index - 1]
        
        # Naviguer vers la NC précédente
        self.current_nc_id = previous_nc['id']
        self.detail_selected_ref = previous_nc.get('reference', '')
        self.tab_content.content = self._build_detail_tab()
        if self.page:
            self.page.update()

    def _navigate_to_next_nc(self, e=None):
        """Navigue vers la NC suivante dans la liste."""
        if not self.current_nc_id:
            create_snackbar(self.page, "Aucune NC sélectionnée", "warning")
            return
        
        # Récupérer toutes les NC triées par référence
        all_ncs = self.db.get_all_nc()
        if not all_ncs:
            return
        
        # Trier par ID pour respecter l'ordre chronologique
        sorted_ncs = sorted(all_ncs, key=lambda x: x.get('id', 0))
        
        # Trouver l'index actuel
        current_index = next((i for i, nc in enumerate(sorted_ncs) if nc.get('id') == self.current_nc_id), None)
        
        if current_index is None:
            create_snackbar(self.page, "NC actuelle introuvable", "error")
            return
        
        # Si dernière NC, boucler vers la première
        if current_index == len(sorted_ncs) - 1:
            next_nc = sorted_ncs[0]
            create_snackbar(self.page, "Retour à la première NC", "info")
        else:
            next_nc = sorted_ncs[current_index + 1]
        
        # Naviguer vers la NC suivante
        self.current_nc_id = next_nc['id']
        self.detail_selected_ref = next_nc.get('reference', '')
        self.tab_content.content = self._build_detail_tab()
        if self.page:
            self.page.update()
    
    def _build_costs_card(self, nc: Dict) -> ft.Container:
        """Construit la carte des coûts CNQ."""
        cout_matiere = nc.get('cout_matiere', 0)
        qte_nc = nc.get('quantite_nc', 0)
        heures_mo = nc.get('heures_mo', 0)
        taux_horaire = nc.get('taux_horaire', 35)  # Par défaut 35EUR/h
        cout_destruction = nc.get('cout_destruction', 0)
        
        # Calcul
        cout_matiere_total = cout_matiere * qte_nc
        cout_mo = heures_mo * taux_horaire
        cout_total = cout_matiere_total + cout_mo + cout_destruction
        
        return ft.Container(
            padding=20,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Text("Détail des coûts CNQ", size=14, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    # Formule
                    ft.Container(
                        padding=10,
                        border_radius=8,
                        bgcolor=Theme.BG_TERTIARY,
                        content=ft.Text(
                            "(Coût matière x Qté) + (Heures MO x Taux) + Destruction",
                            size=11,
                            color=Theme.TEXT_MUTED,
                            italic=True,
                        ),
                    ),
                    # Détails
                    self._create_cost_line("Coût matière", f"{cout_matiere:,.2f} EUR/u x {qte_nc} u", cout_matiere_total),
                    self._create_cost_line("Main d'oeuvre", f"{heures_mo:.1f} h x {taux_horaire:,.0f} EUR/h", cout_mo),
                    self._create_cost_line("Destruction", "", cout_destruction),
                    ft.Divider(color=Theme.BG_TERTIARY),
                    # Total
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("TOTAL", size=14, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                            ft.Text(f"{cout_total:,.2f} EUR", size=18, weight=ft.FontWeight.BOLD, color=Theme.DANGER),
                        ]
                    ),
                ]
            ),
        )
    
    def _create_cost_line(self, label: str, detail: str, value: float) -> ft.Row:
        """Crée une ligne de coût."""
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=0,
                    controls=[
                        ft.Text(label, size=12, color=Theme.TEXT_SECONDARY),
                        ft.Text(detail, size=10, color=Theme.TEXT_MUTED) if detail else ft.Container(),
                    ]
                ),
                ft.Text(f"{value:,.2f} EUR", size=13, color=Theme.TEXT_PRIMARY),
            ]
        )
    
    def _build_timeline_card(self, nc: Dict) -> ft.Container:
        """Construit la timeline du lot."""
        lot = nc.get('lot_serie', nc.get('numero_lot', ''))
        
        # Récupérer les événements du lot
        events = self.db.get_lot_timeline(lot) if lot else []
        
        if not events:
            # Timeline par défaut basée sur la NC
            events = [
                {'date': nc.get('date_production', nc.get('date_detection')), 'type': 'Production', 'icon': '[Production]'},
                {'date': nc.get('date_analyse_labo'), 'type': 'Analyse Labo', 'icon': '[Analyse]'},
                {'date': nc.get('date_inspection'), 'type': 'Inspection', 'icon': '[Recherche]'},
                {'date': nc.get('date_detection'), 'type': 'Création NC', 'icon': '[Attention]'},
                {'date': nc.get('date_action_corrective'), 'type': 'Actions Correctives', 'icon': '[Outil]'},
                {'date': nc.get('date_cloture'), 'type': 'Clôture', 'icon': '[OK]'},
            ]
        
        return ft.Container(
            padding=20,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Text(f"Timeline Lot {lot}", size=14, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    TimelineWidget(events=events),
                ]
            ),
        )
    
    def _build_actions_card(self, nc: Dict) -> ft.Container:
        """Construit la carte des actions."""
        actions = nc.get('actions', [])
        
        action_rows = []
        for action in actions:
            action_rows.append(
                ft.Container(
                    padding=10,
                    border_radius=8,
                    bgcolor=Theme.BG_TERTIARY,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(action.get('description', '-'), size=13, color=Theme.TEXT_PRIMARY),
                                    ft.Text(
                                        f"Responsable: {action.get('responsable', '-')} | Échéance: {action.get('date_echeance', '-')}",
                                        size=11,
                                        color=Theme.TEXT_MUTED,
                                    ),
                                ]
                            ),
                            StatusBadge(action.get('statut', 'En cours')),
                        ]
                    ),
                )
            )
        
        return ft.Container(
            padding=20,
            border_radius=12,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Actions correctives", size=14, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                            create_button(
                                "Ajouter",
                                icon=ft.Icons.ADD,
                                on_click=lambda e: self._add_action(),
                                style="secondary",
                            ),
                        ]
                    ),
                    *(action_rows if action_rows else [
                        ft.Text("Aucune action définie", size=12, color=Theme.TEXT_MUTED, italic=True)
                    ]),
                ]
            ),
        )
    
    # ========================================================================
    # TAB 3: ANALYSE / FICHE NC
    # ========================================================================
    
    def _build_analysis_tab(self):
        """Onglet Analyse avec 4 sous-onglets : Par Imputation, Anomalie, Catégorie, Matières."""
        # Variables d'état pour le sous-onglet actif
        if not hasattr(self, 'analysis_sub_tab'):
            self.analysis_sub_tab = 0  # Par Imputation par défaut
        if not hasattr(self, 'analysis_filter_value'):
            self.analysis_filter_value = "Tous"
        if not hasattr(self, 'analysis_date_start'):
            self.analysis_date_start = ""
        if not hasattr(self, 'analysis_date_end'):
            self.analysis_date_end = ""
        
        # Sous-onglets avec design amélioré et haute visibilité
        sub_tabs = ft.Tabs(
            selected_index=self.analysis_sub_tab,
            animation_duration=300,
            on_change=self._on_analysis_sub_tab_change,
            scrollable=True,
            tab_alignment=ft.TabAlignment.START,
            label_color=ft.Colors.WHITE,
            unselected_label_color=ft.Colors.BLUE_GREY_800,
            indicator_color=ft.Colors.BLUE_600,
            indicator_tab_size=True,
            indicator_border_radius=3,
            indicator_padding=0,
            divider_color=ft.Colors.BLUE_300,
            tabs=[
                ft.Tab(
                    text="Par Imputation",
                    icon=ft.Icons.PERSON_ROUNDED,
                ),
                ft.Tab(
                    text="Par Anomalie",
                    icon=ft.Icons.WARNING_ROUNDED,
                ),
                ft.Tab(
                    text="Par Catégorie",
                    icon=ft.Icons.FOLDER_ROUNDED,
                ),
                ft.Tab(
                    text="Par Matières",
                    icon=ft.Icons.INVENTORY_2_ROUNDED,
                ),
                ft.Tab(
                    text="Par Type",
                    icon=ft.Icons.LABEL_ROUNDED,
                ),
                ft.Tab(
                    text="Par Origine",
                    icon=ft.Icons.PUBLIC_ROUNDED,
                ),
            ],
        )
        
        # Contenu du sous-onglet actif
        content = self._build_analysis_sub_tab_content()
        
        return ft.Column(
            expand=True,
            spacing=0,
            controls=[
                # Conteneur des sous-onglets avec fond
                ft.Container(
                    padding=ft.Padding(left=20, right=20, top=8, bottom=8),
                    bgcolor=ft.Colors.BLUE_600,
                    border=ft.Border(
                        bottom=ft.BorderSide(3, ft.Colors.BLUE_800),
                    ),
                    content=sub_tabs,
                ),
                ft.Container(
                    expand=True,
                    content=content,
                ),
            ],
        )
    
    def _on_analysis_sub_tab_change(self, e):
        """Change le sous-onglet d'analyse."""
        self.analysis_sub_tab = e.control.selected_index
        # Reset les filtres
        self.analysis_filter_value = "Tous"
        self.analysis_date_start = ""
        self.analysis_date_end = ""
        # Reconstruire uniquement le contenu, pas tout l'onglet
        new_content = self._build_analysis_sub_tab_content()
        # Trouver le container de contenu dans l'onglet actuel et le remplacer (index 3 = Analyse)
        if 3 in self._tabs_cache:
            analysis_tab = self._tabs_cache[3]
            # Le container de contenu est le deuxième élément (index 1) après les sous-onglets
            if isinstance(analysis_tab, ft.Column) and len(analysis_tab.controls) >= 2:
                analysis_tab.controls[1].content = new_content
                # Mettre à jour aussi le contenu affiché si on est sur l'onglet Analyse
                if self.current_tab == 3:
                    self.tab_content.content = analysis_tab
                if self.page:
                    self.page.update()
        else:
            # Si le cache n'existe pas encore, reconstruire complètement
            self._tabs_cache[3] = self._build_analysis_tab()
            if self.current_tab == 3:
                self.tab_content.content = self._tabs_cache[3]
            if self.page:
                self.page.update()
    
    def _build_analysis_sub_tab_content(self):
        """Construit le contenu du sous-onglet actif."""
        # Utiliser le cache pour éviter les requêtes répétées
        if not hasattr(self, '_analysis_nc_cache') or not self._analysis_nc_cache:
            self._analysis_nc_cache = self.db.get_all_nc()
        all_ncs = self._analysis_nc_cache
        
        # Configuration des sous-onglets (pour éviter code dupliqué)
        tab_config = {
            0: {  # Par Imputation
                'filter_label': "Choisir l'imputation",
                'filter_field': 'imputation',
                'var1': ('type_anomalie', 'Anomalie'),
                'var2': ('categorie_nc', 'Catégorie'),
                'var3': ('type_nc', 'Type NC'),
            },
            1: {  # Par Anomalie
                'filter_label': "Choisir l'anomalie",
                'filter_field': 'type_anomalie',
                'var1': ('imputation', 'Imputation'),
                'var2': ('categorie_nc', 'Catégorie'),
                'var3': ('type_nc', 'Type NC'),
            },
            2: {  # Par Catégorie
                'filter_label': "Choisir la catégorie",
                'filter_field': 'categorie_nc',
                'var1': ('type_anomalie', 'Anomalie'),
                'var2': ('imputation', 'Imputation'),
                'var3': ('type_nc', 'Type NC'),
            },
            3: {  # Par Matières Réclamées
                'filter_label': "Choisir la matière réclamée",
                'filter_field': 'matieres_reclames',
                'var1': ('imputation', 'Imputation'),
                'var2': ('type_anomalie', 'Anomalie'),
                'var3': ('type_nc', 'Type NC'),
            },
            4: {  # Par Type
                'filter_label': "Choisir le type",
                'filter_field': 'type_nc',
                'var1': ('imputation', 'Imputation'),
                'var2': ('type_anomalie', 'Anomalie'),
                'var3': ('categorie_nc', 'Catégorie'),
            },
            5: {  # Par Origine
                'filter_label': "Choisir l'origine",
                'filter_field': 'origine',
                'var1': ('imputation', 'Imputation'),
                'var2': ('type_anomalie', 'Anomalie'),
                'var3': ('categorie_nc', 'Catégorie'),
            },
        }
        
        # Récupérer config du sous-onglet actuel
        config = tab_config[self.analysis_sub_tab]
        filter_label = config['filter_label']
        filter_field = config['filter_field']
        var1_field, var1_label = config['var1']
        var2_field, var2_label = config['var2']
        var3_field, var3_label = config['var3']
        
        # Options du filtre (extraire valeurs uniques)
        options = ["Tous"] + sorted(set(nc.get(filter_field, '') for nc in all_ncs if nc.get(filter_field)))
        
        # Filtrage optimisé en une seule passe
        filtered_ncs = [
            nc for nc in all_ncs
            if (self.analysis_filter_value == "Tous" or nc.get(filter_field) == self.analysis_filter_value)
            and (not self.analysis_date_start or nc.get('date_detection', '') >= self.analysis_date_start)
            and (not self.analysis_date_end or nc.get('date_detection', '') <= self.analysis_date_end)
        ]
        
        nc_count = len(filtered_ncs)
        
        # Filtres dans une carte stylisée
        filters_card = ft.Container(
            padding=20,
            margin=ft.Margin(20, 15, 20, 15),
            bgcolor=Theme.BG_SECONDARY,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                offset=ft.Offset(0, 3),
            ),
            content=ft.Column(
                spacing=15,
                controls=[
                    # Titre section filtres
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Icon(ft.Icons.TUNE_ROUNDED, size=24, color=ft.Colors.BLUE_700),
                                    ft.Text(
                                        "Filtres d'analyse",
                                        size=17,
                                        weight=ft.FontWeight.BOLD,
                                        color=Theme.TEXT_PRIMARY,
                                    ),
                                ],
                            ),
                            # Compteur de NC en haut à droite
                            ft.Container(
                                padding=ft.Padding(left=15, right=15, top=8, bottom=8),
                                bgcolor=ft.Colors.BLUE_700,
                                border_radius=20,
                                shadow=ft.BoxShadow(
                                    spread_radius=0,
                                    blur_radius=4,
                                    color=ft.Colors.with_opacity(0.3, ft.Colors.BLUE),
                                    offset=ft.Offset(0, 2),
                                ),
                                content=ft.Row(
                                    spacing=8,
                                    controls=[
                                        ft.Icon(ft.Icons.ANALYTICS_ROUNDED, color=ft.Colors.WHITE, size=20),
                                        ft.Text(
                                            f"{nc_count} NC",
                                            color=ft.Colors.WHITE,
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color=ft.Colors.BLUE_100),
                    # Ligne de filtres
                    ft.Row(
                        spacing=15,
                        wrap=True,
                        controls=[
                            create_dropdown(
                                filter_label,
                                options,
                                value=self.analysis_filter_value if self.analysis_filter_value in options else "Tous",
                                on_change=lambda e: self._apply_analysis_filter(e.control.value),
                                width=220,
                            ),
                            create_text_field(
                                "Date début",
                                read_only=True,
                                value=self.analysis_date_start,
                                suffix=ft.IconButton(
                                    ft.Icons.CALENDAR_MONTH_ROUNDED,
                                    icon_size=18,
                                    on_click=lambda e: self._open_analysis_date_picker('start'),
                                ),
                                width=150,
                            ),
                            create_text_field(
                                "Date fin",
                                read_only=True,
                                value=self.analysis_date_end,
                                suffix=ft.IconButton(
                                    ft.Icons.CALENDAR_MONTH_ROUNDED,
                                    icon_size=18,
                                    on_click=lambda e: self._open_analysis_date_picker('end'),
                                ),
                                width=150,
                            ),
                            ft.ElevatedButton(
                                "[Actualiser] Réinitialiser",
                                icon=ft.Icons.REFRESH_ROUNDED,
                                on_click=lambda e: self._reset_analysis_filters(),
                                bgcolor=ft.Colors.BLUE_50,
                                color=ft.Colors.BLUE_700,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )
        
        # Trier par date
        filtered_ncs = sorted(filtered_ncs, key=lambda x: x.get('date_detection', ''))
        
        if not filtered_ncs:
            return ft.Column(
                controls=[
                    filters_card,
                    ft.Container(height=20),
                    create_empty_state(
                        ft.Icons.ANALYTICS,
                        "Aucune NC trouvée",
                        "Modifiez vos filtres pour afficher des résultats",
                    ),
                ],
            )
        
        # Section 1 : Timeline Interactive
        timeline = self._build_timeline(filtered_ncs, var1_field, var2_field, var3_field, var1_label, var2_label, var3_label)
        
        # Section 2 : Tableau de Détail
        detail_table = self._build_analysis_table(filtered_ncs, var1_field, var2_field, var3_field, var1_label, var2_label, var3_label)
        
        return ft.Column(
            expand=True,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                filters_card,
                # Timeline dans une carte stylisée
                ft.Container(
                    padding=20,
                    margin=ft.Margin(20, 10, 20, 10),
                    bgcolor=Theme.BG_SECONDARY,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=8,
                        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                        offset=ft.Offset(0, 2),
                    ),
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.TIMELINE_ROUNDED, size=24, color=ft.Colors.BLUE_700),
                                    ft.Text(
                                        "Timeline Chronologique",
                                        size=17,
                                        weight=ft.FontWeight.BOLD,
                                        color=Theme.TEXT_PRIMARY,
                                    ),
                                ],
                            ),
                            ft.Divider(height=1, color=ft.Colors.BLUE_100),
                            timeline,
                        ],
                    ),
                ),
                # Tableau de détail dans une carte stylisée
                ft.Container(
                    padding=20,
                    margin=ft.Margin(20, 10, 20, 10),
                    bgcolor=Theme.BG_SECONDARY,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=8,
                        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                        offset=ft.Offset(0, 2),
                    ),
                    expand=True,
                    content=ft.Column(
                        spacing=15,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.TABLE_CHART_ROUNDED, size=24, color=ft.Colors.BLUE_700),
                                    ft.Text(
                                        "Tableau de Détail",
                                        size=17,
                                        weight=ft.FontWeight.BOLD,
                                        color=Theme.TEXT_PRIMARY,
                                    ),
                                ],
                            ),
                            ft.Divider(height=1, color=ft.Colors.BLUE_100),
                            detail_table,
                        ],
                    ),
                ),
            ],
        )
    
    def _build_timeline(self, ncs: List[Dict], var1_field: str, var2_field: str, var3_field: str, var1_label: str, var2_label: str, var3_label: str):
        """Construit la timeline interactive (limite 50 items)."""
        if not ncs:
            return ft.Text("Aucune donnée", color=Theme.TEXT_MUTED)
        
        # Limiter à 50 NC pour la performance
        display_ncs = ncs[:50]
        has_more = len(ncs) > 50
        
        timeline_items = []
        for nc in display_ncs:
            nc_num = nc.get('reference') or nc.get('id', 'N/A')
            nc_date = nc.get('date_detection', '')
            gravite = nc.get('gravite', '')
            
            # Déterminer la couleur selon la gravité
            if gravite == 'Critique':
                badge_color = ft.Colors.RED_700
            elif gravite == 'Majeur':
                badge_color = ft.Colors.ORANGE_700
            elif gravite == 'Mineur':
                badge_color = ft.Colors.YELLOW_800
            else:
                badge_color = Theme.PRIMARY
            
            # Créer un item cliquable
            item = ft.Container(
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                    controls=[
                        ft.Container(
                            padding=ft.Padding(8, 8, 8, 8),
                            bgcolor=badge_color,
                            border_radius=20,
                            content=ft.Text(
                                f"NC {nc_num}",
                                color="#FFFFFF",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                            ),
                            on_click=lambda e, n=nc, v1=var1_field, v2=var2_field, v3=var3_field, l1=var1_label, l2=var2_label, l3=var3_label: self._show_nc_popup(n, v1, v2, v3, l1, l2, l3),
                            ink=True,
                            tooltip=f"Gravité: {gravite}",
                        ),
                        ft.Container(
                            width=2,
                            height=20,
                            bgcolor=badge_color,
                        ),
                        ft.Text(
                            nc_date,
                            size=10,
                            color=Theme.TEXT_MUTED,
                        ),
                    ],
                ),
            )
            timeline_items.append(item)
        
        # Ajouter indicateur si plus de données
        if has_more:
            timeline_items.append(
                ft.Container(
                    padding=ft.Padding(8, 8, 8, 8),
                    bgcolor=Theme.BG_TERTIARY,
                    border_radius=20,
                    content=ft.Text(
                        f"+{len(ncs) - 50} NC",
                        color=Theme.TEXT_MUTED,
                        weight=ft.FontWeight.BOLD,
                        size=12,
                    ),
                    tooltip="Affinez les filtres pour voir plus de détails",
                )
            )
        
        return ft.Container(
            content=ft.Row(
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
                controls=timeline_items,
            ),
        )
    
    def _build_analysis_table(self, ncs: List[Dict], var1_field: str, var2_field: str, var3_field: str, var1_label: str, var2_label: str, var3_label: str):
        """Construit le tableau de détail avec pagination."""
        total_count = len(ncs)
        
        # Variables pour la pagination
        if not hasattr(self, '_analysis_table_page'):
            self._analysis_table_page = 1
        if not hasattr(self, '_analysis_items_per_page'):
            self._analysis_items_per_page = 50
        
        # Calculer les indices
        start_idx = (self._analysis_table_page - 1) * self._analysis_items_per_page
        end_idx = start_idx + self._analysis_items_per_page
        display_ncs = ncs[start_idx:end_idx]
        
        total_pages = max(1, (total_count + self._analysis_items_per_page - 1) // self._analysis_items_per_page)
        
        # En-têtes avec colonnes fixes sauf Description (adaptative)
        header_cells = [
            ft.DataColumn(ft.Text("No NC", weight=ft.FontWeight.BOLD, size=13), numeric=True),
            ft.DataColumn(ft.Text("Date", weight=ft.FontWeight.BOLD, size=13)),
            ft.DataColumn(ft.Container(width=100, content=ft.Text("Origine", weight=ft.FontWeight.BOLD, size=13))),
            ft.DataColumn(ft.Container(width=110, content=ft.Text(var1_label, weight=ft.FontWeight.BOLD, size=13))),
            ft.DataColumn(ft.Container(width=120, content=ft.Text("Produit", weight=ft.FontWeight.BOLD, size=13))),
            ft.DataColumn(ft.Text("Description", weight=ft.FontWeight.BOLD, size=13)),  # Sans width fixe pour s'adapter
            ft.DataColumn(ft.Container(width=110, content=ft.Text(var2_label, weight=ft.FontWeight.BOLD, size=13))),
            ft.DataColumn(ft.Container(width=100, content=ft.Text(var3_label, weight=ft.FontWeight.BOLD, size=13))),
            ft.DataColumn(ft.Container(width=250, content=ft.Text("Cause Racine", weight=ft.FontWeight.BOLD, size=13))),
        ]
        
        # Lignes avec hauteur automatique adaptée au contenu
        rows = []
        for nc in display_ncs:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(nc.get('reference') or nc.get('id', '')), size=12)),
                    ft.DataCell(ft.Text(nc.get('date_detection', '-'), size=12)),
                    ft.DataCell(
                        ft.Container(
                            padding=5,
                            width=100,
                            content=ft.Text(nc.get('origine', '-') or '-', size=12, max_lines=None, no_wrap=False)
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            padding=5,
                            width=110,
                            content=ft.Text(nc.get(var1_field, '-') or '-', size=12, max_lines=None, no_wrap=False)
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            padding=5,
                            width=120,
                            content=ft.Text(nc.get('produit_concerne', '-') or '-', size=12, max_lines=None, no_wrap=False)
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            padding=5,
                            # Pas de width fixe - la colonne Description s'adapte
                            content=ft.Text(nc.get('description', '-') or '-', size=12, max_lines=None, no_wrap=False)
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            padding=5,
                            width=110,
                            content=ft.Text(nc.get(var2_field, '-') or '-', size=12, max_lines=None, no_wrap=False)
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            padding=5,
                            width=100,
                            content=ft.Text(nc.get(var3_field, '-') or '-', size=12, max_lines=None, no_wrap=False)
                        )
                    ),
                    ft.DataCell(
                        ft.Container(
                            padding=5,
                            width=250,
                            content=ft.Text(nc.get('cause_racine', '-') or '-', size=12, max_lines=None, no_wrap=False)
                        )
                    ),
                ],
                on_select_changed=lambda e, n=nc: self._open_form(n),
            )
            rows.append(row)
        
        # Tableau avec hauteur de ligne dynamique adaptée au contenu
        data_table = ft.DataTable(
            columns=header_cells,
            rows=rows,
            column_spacing=10,
            horizontal_margin=10,
            heading_row_color=Theme.BG_TERTIARY,
            data_row_min_height=60,  # Hauteur minimum plus grande
            data_row_max_height=float('inf'),  # Hauteur illimitée (infinity)
            expand=True,
        )
        
        # Contrôles de pagination
        pagination_controls = ft.Container(
            padding=10,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(
                        f"Affichage de {start_idx + 1} à {min(end_idx, total_count)} sur {total_count} NC",
                        size=13,
                        color=Theme.TEXT_MUTED,
                    ),
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.ElevatedButton(
                                "< Précédent",
                                on_click=lambda e: self._change_analysis_page(self._analysis_table_page - 1, ncs, var1_field, var2_field, var3_field, var1_label, var2_label, var3_label),
                                disabled=self._analysis_table_page <= 1,
                                style=ft.ButtonStyle(
                                    bgcolor={ft.ControlState.DEFAULT: Theme.PRIMARY, ft.ControlState.DISABLED: Theme.BG_TERTIARY},
                                    color=ft.Colors.WHITE,
                                ),
                            ),
                            ft.Text(
                                f"Page {self._analysis_table_page} / {total_pages}",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.TEXT_PRIMARY,
                            ),
                            ft.ElevatedButton(
                                "Suivant >",
                                on_click=lambda e: self._change_analysis_page(self._analysis_table_page + 1, ncs, var1_field, var2_field, var3_field, var1_label, var2_label, var3_label),
                                disabled=self._analysis_table_page >= total_pages,
                                style=ft.ButtonStyle(
                                    bgcolor={ft.ControlState.DEFAULT: Theme.PRIMARY, ft.ControlState.DISABLED: Theme.BG_TERTIARY},
                                    color=ft.Colors.WHITE,
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )
        
        return ft.Container(
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            scroll=ft.ScrollMode.AUTO,
                            controls=[data_table],
                            expand=True,
                        ),
                    ),
                    pagination_controls,
                ],
                expand=True,
            ),
        )
    
    def _change_analysis_page(self, new_page, ncs, var1_field, var2_field, var3_field, var1_label, var2_label, var3_label):
        """Change la page du tableau d'analyse."""
        self._analysis_table_page = new_page
        
        # Reconstruire le tableau avec la nouvelle page
        new_table = self._build_analysis_table(ncs, var1_field, var2_field, var3_field, var1_label, var2_label, var3_label)
        
        # Mettre à jour le contenu du tableau dans l'onglet
        # Il faut retrouver le container qui contient le tableau et le remplacer
        # Pour l'instant, invalidons le cache pour forcer la reconstruction
        if 3 in self._tabs_cache:
            del self._tabs_cache[3]
        
        # Reconstruire l'onglet analyse complet
        self.tab_content.content = self._build_analysis_tab()
        self._tabs_cache[3] = self.tab_content.content
        self.page.update()
    
    def _show_nc_popup(self, nc: Dict, var1_field: str, var2_field: str, var3_field: str, var1_label: str, var2_label: str, var3_label: str):
        """Affiche une modale avec les détails de la NC en haut à droite."""
        # Fermer la popup précédente si elle existe
        if self._current_popup and self._current_popup in self.page.overlay:
            self.page.overlay.remove(self._current_popup)
        
        # Créer un conteneur positionné en haut à droite avec animation
        popup_content = ft.Container(
            right=20,
            top=80,
            width=500,
            bgcolor=Theme.BG_PRIMARY,
            border=ft.Border(
                top=ft.BorderSide(2, Theme.OUTLINE),
                right=ft.BorderSide(2, Theme.OUTLINE),
                bottom=ft.BorderSide(2, Theme.OUTLINE),
                left=ft.BorderSide(2, Theme.OUTLINE),
            ),
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
            ),
            padding=20,
            opacity=0,
            animate_opacity=300,
            content=ft.Column(
                spacing=12,
                tight=True,
                controls=[
                    # En-tête
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.INFO, color=Theme.PRIMARY, size=24),
                                    ft.Text(
                                        f"NC {nc.get('reference') or nc.get('id', '')}",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=Theme.TEXT_PRIMARY,
                                    ),
                                ],
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                on_click=lambda e: self._close_positioned_popup(),
                                icon_color=Theme.TEXT_PRIMARY,
                                tooltip="Fermer",
                            ),
                        ],
                    ),
                    ft.Divider(color=Theme.OUTLINE),
                    # Contenu scrollable
                    ft.Container(
                        height=450,
                        content=ft.Column(
                            spacing=10,
                            scroll=ft.ScrollMode.AUTO,
                            controls=[
                                self._info_row("Date de détection", nc.get('date_detection', '-'), ft.Icons.CALENDAR_TODAY),
                                self._info_row("No NC", nc.get('reference') or nc.get('id', '-'), ft.Icons.TAG),
                                self._info_row("Origine", nc.get('origine', '-'), ft.Icons.PLACE),
                                self._info_row(var1_label, nc.get(var1_field, '-'), multiline=True),
                                self._info_row("Produits concernés", nc.get('produit_concerne', '-'), ft.Icons.INVENTORY, multiline=True),
                                self._info_row("Quantité", str(nc.get('quantite_affectee', '-') or '-')),
                                self._info_row("Lot", nc.get('lot_serie', '-'), ft.Icons.QR_CODE),
                                self._info_row("Description", nc.get('description', '-'), multiline=True),
                                self._info_row(var2_label, nc.get(var2_field, '-'), multiline=True),
                                self._info_row(var3_label, nc.get(var3_field, '-'), multiline=True),
                                self._info_row("Cause racine", nc.get('cause_racine', '-'), multiline=True),
                            ],
                        ),
                    ),
                    # Bouton Fermer
                    ft.Container(
                        alignment=ft.Alignment(0, 0),
                        content=ft.ElevatedButton(
                            "Fermer",
                            on_click=lambda e: self._close_positioned_popup(),
                            bgcolor=Theme.PRIMARY,
                            color="#FFFFFF",
                        ),
                    ),
                ],
            ),
        )
        
        # Créer un fond transparent qui ferme la popup quand on clique dessus
        backdrop_container = ft.Container(
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.01, ft.Colors.BLACK),
            opacity=0,
            animate_opacity=300,
        )
        
        backdrop = ft.GestureDetector(
            on_tap=lambda e: self._close_positioned_popup(),
            content=backdrop_container,
        )
        
        # Stack avec le backdrop en bas et la popup au-dessus
        popup_stack = ft.Stack(
            controls=[
                backdrop,
                popup_content,
            ],
        )
        
        # Sauvegarder la référence et ajouter à l'overlay
        self._current_popup = popup_stack
        self.page.overlay.append(popup_stack)
        self.page.update()
        
        # Déclencher l'animation fade-in
        popup_content.opacity = 1
        backdrop_container.opacity = 1
        self.page.update()
    
    def _open_nc_directly(self, nc: Dict):
        """Ouvre directement le formulaire de la NC sans popup intermédiaire."""
        # Change vers l'onglet Détails NC
        self.tabs.selected_index = 1
        self.current_tab = 1
        # Ouvre le formulaire
        self._open_form(nc)
    
    def _close_positioned_popup(self):
        """Ferme la popup positionnée."""
        if self._current_popup and self._current_popup in self.page.overlay:
            self.page.overlay.remove(self._current_popup)
            self._current_popup = None
            self.page.update()
    
    def _close_simple_dialog(self, dialog):
        """Ferme le dialog de manière simple et propre."""
        dialog.open = False
        self.page.update()
    
    def _close_bottom_sheet(self, bottom_sheet):
        """Ferme le BottomSheet proprement."""
        bottom_sheet.open = False
        if hasattr(self, 'page') and self.page:
            self.page.update()
            # Nettoie l'overlay après la fermeture
            if bottom_sheet in self.page.overlay:
                self.page.overlay.remove(bottom_sheet)
    
    def _close_nc_dialog(self, dialog):
        """Ferme la modale spécifique."""
        dialog.open = False
        if hasattr(self, 'page') and self.page:
            if dialog in self.page.overlay:
                self.page.overlay.remove(dialog)
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    def _open_nc_from_dialog(self, dialog, nc: Dict):
        """Ouvre le détail de la NC dans l'onglet Détails NC."""
        if hasattr(self, 'page') and self.page:
            # Ferme le dialog
            dialog.open = False
            if dialog in self.page.overlay:
                self.page.overlay.remove(dialog)
            self.page.update()
            
            # Change vers l'onglet Détails NC (onglet 1) et ouvre le formulaire
            self.tabs.selected_index = 1
            self.current_tab = 1
            
            # Ouvre le formulaire de cette NC
            self._open_form(nc)
    
    def _apply_analysis_filter(self, value: str):
        """Applique le filtre principal de l'analyse."""
        self.analysis_filter_value = value
        if 2 in self._tabs_cache:
            del self._tabs_cache[2]
        # Pas besoin d'invalider le cache NC ici, juste reconstruire la vue
        self._tabs_cache[2] = self._build_analysis_tab()
        self.tab_content.content = self._tabs_cache[2]
        self.page.update()
    
    def _open_analysis_date_picker(self, picker_type: str):
        """Ouvre le calendrier personnalisé pour les filtres d'analyse."""
        # Date initiale
        initial_date = None
        current_value = self.analysis_date_start if picker_type == 'start' else self.analysis_date_end
        if current_value:
            try:
                initial_date = datetime.strptime(current_value, "%Y-%m-%d").date()
            except:
                initial_date = None
        
        # Callback quand une date est sélectionnée
        def on_date_selected(selected_date):
            self._on_analysis_date_selected(selected_date, picker_type)
        
        # Créer et ouvrir le calendrier
        calendar_dialog = CustomCalendar(on_date_selected, initial_date)
        
        # Ajouter à l'overlay de la page
        if self.page:
            self.page.overlay.append(calendar_dialog)
            calendar_dialog.open = True
            self.page.update()
    
    def _on_analysis_date_selected(self, date_value, picker_type: str):
        """Traite la sélection de date."""
        if date_value:
            date_str = date_value.strftime("%Y-%m-%d")
            if picker_type == 'start':
                self.analysis_date_start = date_str
            else:
                self.analysis_date_end = date_str
            
            if 2 in self._tabs_cache:
                del self._tabs_cache[2]
            self._tabs_cache[2] = self._build_analysis_tab()
            self.tab_content.content = self._tabs_cache[2]
            self.page.update()
    
    def _reset_analysis_filters(self):
        """Réinitialise tous les filtres de l'analyse."""
        self.analysis_filter_value = "Tous"
        self.analysis_date_start = ""
        self.analysis_date_end = ""
        if 2 in self._tabs_cache:
            del self._tabs_cache[2]
        # Pas besoin d'invalider le cache NC ici, juste reconstruire la vue
        self._tabs_cache[2] = self._build_analysis_tab()
        self.tab_content.content = self._tabs_cache[2]
        self.page.update()

    def _info_row(self, label: str, value: str, icon=None, multiline: bool = False) -> ft.Row:
        """Affiche une ligne label/valeur avec option icône."""
        icon_control = ft.Icon(icon, size=14, color=Theme.TEXT_MUTED) if icon else None
        label_controls = [icon_control] if icon_control else []
        label_controls.append(ft.Text(f"{label}:", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY, size=13))

        return ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Container(
                    width=200,
                    content=ft.Row(spacing=6, controls=label_controls),
                ),
                ft.Container(
                    expand=True,
                    content=ft.Text(
                        str(value) if value else "-",
                        color=Theme.TEXT_SECONDARY,
                        size=13,
                        max_lines=None if multiline else 1,
                        no_wrap=False,  # Permet le retour à la ligne automatique
                    ),
                ),
            ],
        )

    def _pill(self, text: str) -> ft.Container:
        """Petit badge arrondi pour listes (5M, tags)."""
        return ft.Container(
            padding=ft.Padding(left=10, right=10, top=6, bottom=6),
            border_radius=20,
            bgcolor=Theme.BG_TERTIARY,
            content=ft.Text(text, size=12, color=Theme.TEXT_PRIMARY),
        )

    def _build_actions_table(self, actions: List[Dict], is_immediate: bool) -> ft.DataTable:
        """Construit un tableau d'actions aligné sur le formulaire (toutes colonnes utiles)."""
        if is_immediate:
            rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(a.get('correction', '-') or a.get('desc', '-') or a.get('description', '-'), size=11)),
                        ft.DataCell(ft.Text(a.get('responsable', '-'), size=11)),
                        ft.DataCell(ft.Text(a.get('date', '-') or a.get('date_echeance', '-'), size=11)),
                        ft.DataCell(ft.Text(str(a.get('cost', a.get('cout', '-'))), size=11)),
                    ]
                )
                for a in actions
            ]
            columns = [
                ft.DataColumn(ft.Text("Correction", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Responsable", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Date", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Coût", size=12, weight=ft.FontWeight.BOLD)),
            ]
        else:
            rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(a.get('desc', '-') or a.get('description', '-'), size=11)),
                        ft.DataCell(ft.Text(a.get('responsable', '-'), size=11)),
                        ft.DataCell(ft.Text(a.get('date_debut', '-') or a.get('date', '-'), size=11)),
                        ft.DataCell(ft.Text(a.get('date_fin', '-') or a.get('echeance', '-') or a.get('date_echeance', '-'), size=11)),
                        ft.DataCell(ft.Text(str(a.get('cost', a.get('cout', '-'))), size=11)),
                        ft.DataCell(ft.Text(a.get('verification', '-') or a.get('verif', '-') or '-', size=11)),
                        ft.DataCell(ft.Text(a.get('statut', '-'), size=11)),
                    ]
                )
                for a in actions
            ]
            columns = [
                ft.DataColumn(ft.Text("Action", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Responsable", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Début", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fin", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Coût", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Vérification", size=12, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Statut", size=12, weight=ft.FontWeight.BOLD)),
            ]

        return ft.DataTable(columns=columns, rows=rows, column_spacing=10)

    def _build_attachments_viewer(self, attachments: List[Dict]) -> ft.Column:
        """Affiche les pièces jointes avec ouverture contextualisée."""
        import os

        attachment_controls = []
        for att in attachments:
            file_name = att.get('name', 'Fichier')
            file_path = att.get('path', '')
            file_ext = os.path.splitext(file_name)[1].lower()

            is_image = file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
            is_pdf = file_ext == '.pdf'
            is_office = file_ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
            is_email = file_ext in ['.msg', '.eml']

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

            attachment_controls.append(
                ft.Container(
                    padding=8,
                    border=ft.Border(
                top=ft.BorderSide(1, Theme.BG_TERTIARY),
                right=ft.BorderSide(1, Theme.BG_TERTIARY),
                bottom=ft.BorderSide(1, Theme.BG_TERTIARY),
                left=ft.BorderSide(1, Theme.BG_TERTIARY),
            ),
                    border_radius=8,
                    bgcolor=Theme.BG_SECONDARY,
                    content=ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(icon, color=color, size=18),
                            ft.Text(file_name, size=13, color=Theme.TEXT_PRIMARY),
                            ft.IconButton(
                                icon=ft.Icons.OPEN_IN_NEW if not (is_image or is_pdf) else ft.Icons.VISIBILITY,
                                icon_size=16,
                                tooltip="Ouvrir" if not (is_image or is_pdf) else "Visualiser",
                                on_click=lambda e, path=file_path, name=file_name, img=is_image, pdf=is_pdf: self._open_attachment(path, name, img, pdf),
                            ),
                        ],
                    ),
                )
            )

        return ft.Column(spacing=6, controls=attachment_controls)

    def _open_attachment(self, file_path: str, file_name: str, is_image: bool, is_pdf: bool):
        """Ouvre une pièce jointe en interne pour images/PDF, sinon externe."""
        import os
        if not file_path or not os.path.exists(file_path):
            create_snackbar(self.page, "[Attention] Fichier introuvable", "error")
            return

        if is_image:
            self._show_image_viewer(file_path, file_name)
        elif is_pdf:
            self._show_pdf_viewer(file_path, file_name)
        else:
            self._open_external(file_path, file_name)

    def _show_image_viewer(self, file_path: str, file_name: str):
        """Affiche une image dans un dialog Flet."""
        import base64
        try:
            with open(file_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')

            img = ft.Image(src_base64=img_data, fit=ft.ImageFit.CONTAIN)
            dialog = ft.AlertDialog(
                title=ft.Text(file_name),
                content=ft.Container(width=800, height=600, content=img),
                actions=[
                    ft.TextButton("Fermer", on_click=lambda e: self.page.close(dialog)),
                    ft.TextButton("Ouvrir en externe", on_click=lambda e: self._open_external(file_path, file_name)),
                ],
            )
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
        except Exception as ex:
            create_snackbar(self.page, f"[Erreur] Erreur: {str(ex)}", "error")

    def _show_pdf_viewer(self, file_path: str, file_name: str):
        """Ouvre un PDF via l'application système par défaut."""
        self._open_external(file_path, file_name)

    def _open_external(self, file_path: str, file_name: str):
        """Ouvre un fichier avec l'application par défaut selon l'OS."""
        import os
        import subprocess
        import platform

        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':
                subprocess.call(['open', file_path])
            else:
                subprocess.call(['xdg-open', file_path])
            create_snackbar(self.page, f"[OK] Ouverture de {file_name}", "success")
        except Exception as ex:
            create_snackbar(self.page, f"[Erreur] Erreur: {str(ex)}", "error")

    def _safe_json(self, value: Any, default):
        """Décode une valeur JSON ou renvoie la valeur par défaut."""
        import json

        try:
            if value is None:
                return default
            data = json.loads(value) if isinstance(value, str) else value
            if isinstance(default, list) and isinstance(data, list):
                return data
            if isinstance(default, dict) and isinstance(data, dict):
                return data
        except Exception:
            pass
        return default
    
    # ========================================================================
    # FORMULAIRE NC PLEINE PAGE
    # ========================================================================
    
    def _init_form_fields(self):
        """Initialise les champs du formulaire de manière optimisée."""
        import json
        nc = self.editing_nc or {}
        
        # Section A - Identification (champs simples d'abord)
        self.ref_field = create_text_field("Référence", prefix_icon=ft.Icons.TAG)
        self.ref_field.value = nc.get('reference', '')
        
        # Champ date avec DatePicker (ouverture via l'icône seulement)
        self.date_field = create_text_field(
            "Date de détection", 
            hint_text="Cliquez sur l'icône",
            read_only=True,
            cursor_height=0,
        )
        self.date_field.value = nc.get('date_detection', datetime.now().strftime("%Y-%m-%d"))
        self.date_picker = None  # Créé à la demande

        # Ligne avec icône cliquable
        self.date_icon_btn = ft.IconButton(
            icon=ft.Icons.CALENDAR_TODAY,
            icon_color=Theme.TEXT_MUTED,
            on_click=lambda e: self._open_date_picker(),
            style=ft.ButtonStyle(padding=0),
        )
        self.date_input_row = ft.Container(
            expand=True,
            content=ft.Row(
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[self.date_icon_btn, self.date_field],
            ),
        )
        
        # Dropdowns avec icônes et possibilité d'ajout
        self.type_dropdown = create_dropdown(
            "Type de NC", 
            self.type_nc_choices, 
            value=nc.get('type_nc'), 
            prefix_icon=ft.Icons.CATEGORY,
            enable_add_new=True,
            on_change=lambda e: self._handle_dropdown_change(e, 'type')
        )
        
        # Gravité - sélecteur coloré (pas de dropdown, juste des boutons)
        self.current_severity = nc.get('gravite', 'Mineure')
        
        self.imputation_dropdown = create_dropdown(
            "Imputation", 
            self.imputation_choices, 
            value=nc.get('imputation'), 
            prefix_icon=ft.Icons.ACCOUNT_TREE,
            enable_add_new=True,
            on_change=lambda e: self._handle_dropdown_change(e, 'imputation')
        )
        
        self.origin_field = create_text_field("Origine", prefix_icon=ft.Icons.TRAVEL_EXPLORE)
        self.origin_field.value = nc.get('origine', '')
        
        self.anomaly_dropdown = create_dropdown(
            "Type d'anomalie", 
            self.anomaly_choices, 
            value=nc.get('type_anomalie'), 
            prefix_icon=ft.Icons.BUG_REPORT,
            enable_add_new=True,
            on_change=lambda e: self._handle_dropdown_change(e, 'anomaly')
        )
        
        self.category_field = create_text_field("Catégorie de la NC", prefix_icon=ft.Icons.FOLDER)
        self.category_field.value = nc.get('categorie_nc', '')
        
        self.location_field = create_text_field("Lieu de détection", prefix_icon=ft.Icons.LOCATION_ON)
        self.location_field.value = nc.get('lieu_detection', '')
        
        self.description_field = create_text_field("Description du problème", multiline=True, min_lines=3, prefix_icon=ft.Icons.DESCRIPTION)
        self.description_field.value = nc.get('description', '')
        
        self.product_field = create_text_field("Produit concerné", prefix_icon=ft.Icons.INVENTORY)
        self.product_field.value = nc.get('produit_concerne', '')
        
        self.lot_field = create_text_field("Lot / Série", prefix_icon=ft.Icons.QR_CODE)
        self.lot_field.value = nc.get('lot_serie', '')
        
        # Champ quantité avec clavier numérique
        self.qty_field = create_text_field(
            "Quantité affectée", 
            prefix_icon=ft.Icons.NUMBERS,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.NumbersOnlyInputFilter()
        )
        self.qty_field.value = str(nc.get('quantite_affectee', '') or '')
        
        # Matières réclamées
        self.matieres_dropdown = create_dropdown(
            "Matières réclamées",
            self.matieres_choices,
            value=nc.get('matieres_reclames'),
            prefix_icon=ft.Icons.CATEGORY,
            enable_add_new=True,
            on_change=lambda e: self._handle_dropdown_change(e, 'matieres')
        )
        
        # Pièces jointes
        try:
            existing_pj = json.loads(nc.get('pieces_jointes', '[]') or '[]')
            if isinstance(existing_pj, list):
                self.attachments = existing_pj
            else:
                self.attachments = []
        except Exception:
            self.attachments = []
        self.file_picker = ft.FilePicker(on_result=self._on_files_chosen)
        self.attachments_container = ft.Container(content=self._render_attachments())
        
        # Section B - Analyse
        saved_method = nc.get('methode_analyse') or ''
        use_5why = '5' in saved_method or saved_method.lower().startswith('5') or saved_method == ''
        use_ishikawa = 'ishi' in saved_method.lower() or 'm' in saved_method.lower()
        self.method_5why = ft.Checkbox(label="5 Pourquoi", value=use_5why, on_change=self._on_method_toggle)
        self.method_ishikawa = ft.Checkbox(label="Ishikawa (5M)", value=use_ishikawa, on_change=self._on_method_toggle)
        
        self.root_cause_field = create_text_field("Cause racine", multiline=True, min_lines=2)
        self.root_cause_field.value = nc.get('cause_racine', '')
        
        self.portee_field = create_text_field("Portée de la NC", multiline=True, min_lines=2)
        self.portee_field.value = nc.get('analyse_portee', '')
        
        # 5 Pourquoi
        try:
            self.analysis_details = json.loads(nc.get('analyse_details', '{}') or '{}')
            if not isinstance(self.analysis_details, dict):
                self.analysis_details = {}
        except Exception:
            self.analysis_details = {}
        
        fivewhy_data = self.analysis_details.get('5why', {}) if isinstance(self.analysis_details.get('5why', {}), dict) else {}
        fivewhy_whys = fivewhy_data.get('whys', []) if isinstance(fivewhy_data, dict) else []
        self.fivewhy_fields = []
        for i in range(5):
            self.fivewhy_fields.append(create_text_field(f"Pourquoi {i+1}?", value=fivewhy_whys[i] if i < len(fivewhy_whys) else "", multiline=True, min_lines=1, hint_text="Parce que..."))
        
        # Ishikawa
        ishikawa_data = self.analysis_details.get('ishikawa', {}) if isinstance(self.analysis_details.get('ishikawa', {}), dict) else {}
        default_cats = ["Main d'oeuvre", "Matériel", "Matière", "Méthode", "Milieu", "Mesure"]
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
            self.selected_ishikawa_cats.add(default_cats[0])
        self.ishikawa_synth_field = create_text_field("Synthèse Ishikawa", multiline=True, min_lines=2, value=ishikawa_data.get('synthesis', ""))
        
        # Section C - Actions immédiates
        try:
            immediate_data = json.loads(nc.get('actions_immediates_table', '[]') or '[]')
            if not isinstance(immediate_data, list):
                immediate_data = []
        except Exception:
            immediate_data = []
        if not immediate_data:
            immediate_data = [{}]
        self.immediate_rows = [self._build_immediate_row(row_data) for row_data in immediate_data]
        
        # Section C - Actions correctives
        try:
            corrective_data = json.loads(nc.get('actions_correctives_table', '[]') or '[]')
            if not isinstance(corrective_data, list):
                corrective_data = []
        except Exception:
            corrective_data = []
        if not corrective_data:
            corrective_data = [{}]
        self.corrective_rows = [self._build_corrective_row(row_data) for row_data in corrective_data]
        
        # Section D - Clôture
        self.status_dropdown = create_dropdown("Statut", ["En cours", "Clôturée"], value=nc.get('statut', 'En cours'), prefix_icon=ft.Icons.FLAG)
        self.closure_date_field = create_text_field(
            "Date de clôture", 
            hint_text="Cliquez sur l'icône",
            read_only=True,
            cursor_height=0,
        )
        self.closure_date_field.value = nc.get('date_cloture', '')
        self.closure_date_picker = None  # Créé à la demande
        self.closure_date_icon_btn = ft.IconButton(
            icon=ft.Icons.EVENT_AVAILABLE,
            icon_color=Theme.TEXT_MUTED,
            on_click=lambda e: self._open_closure_date_picker(),
            style=ft.ButtonStyle(padding=0),
        )
        self.closure_date_icon_btn.on_hover = lambda e, btn=self.closure_date_icon_btn: self._toggle_icon_color(btn, e)
        self.closure_date_input_row = ft.Container(
            expand=True,
            content=ft.Row(
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[self.closure_date_icon_btn, self.closure_date_field],
            ),
        )
        self.verifier_field = create_text_field("Vérificateur", prefix_icon=ft.Icons.PERSON)
        self.verifier_field.value = nc.get('verificateur', '')
        self.efficacy_dropdown = create_dropdown("Efficacité des actions", ["Non évaluée", "Efficace", "Partiellement efficace", "Non efficace"], value=nc.get('efficacite', 'Non évaluée'), prefix_icon=ft.Icons.VERIFIED)
        self.closure_comments_field = create_text_field("Commentaires de clôture", multiline=True, min_lines=2, value=nc.get('commentaires_cloture', ''), prefix_icon=ft.Icons.COMMENT)
        
        self.form_error_text = ft.Text("", color=Theme.DANGER, size=12)
    
    def _build_immediate_row(self, row_data=None):
        row_data = row_data or {}
        date_field = create_text_field("Quand (date)", value=row_data.get('date', ''), hint_text="Cliquez sur l'icône", read_only=True, cursor_height=0)
        date_field.width = 140
        date_icon_btn = ft.IconButton(
            icon=ft.Icons.CALENDAR_TODAY,
            icon_color=Theme.TEXT_MUTED,
            on_click=lambda e, f=date_field: self._open_action_date_picker(f, e),
            style=ft.ButtonStyle(padding=0),
        )
        date_icon_btn.on_hover = lambda e, btn=date_icon_btn: self._toggle_icon_color(btn, e)
        date_click_row = ft.Container(
            content=ft.Row(
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[date_icon_btn, date_field],
            ),
        )
        return {
            'correction': create_text_field("Correction effectuée", value=row_data.get('correction', ''), prefix_icon=ft.Icons.BUILD),
            'responsable': create_text_field("Responsable / Qui", value=row_data.get('responsable', ''), prefix_icon=ft.Icons.PERSON),
            'date': date_field,
            'date_container': date_click_row,
            'cost': create_text_field("Coût (EUR)", value=row_data.get('cost', ''), prefix_icon=ft.Icons.EURO, keyboard_type=ft.KeyboardType.NUMBER, input_filter=ft.InputFilter(regex_string=r"[0-9.,]")),
        }
    
    def _build_corrective_row(self, row_data=None):
        row_data = row_data or {}
        # 3 dates : début, échéance, et clôture
        date_debut_field = create_text_field("Date de début", value=row_data.get('date_debut', ''), hint_text="Cliquez sur l'icône", read_only=True, cursor_height=0)
        date_echeance_field = create_text_field("Date d'échéance", value=row_data.get('date_echeance', '') or row_data.get('date_fin', ''), hint_text="Cliquez sur l'icône", read_only=True, cursor_height=0)
        date_cloture_action_field = create_text_field("Date de clôture", value=row_data.get('date_cloture_action', ''), hint_text="Cliquez sur l'icône", read_only=True, cursor_height=0)
        date_debut_field.width = 140
        date_echeance_field.width = 140
        date_cloture_action_field.width = 140

        # Créer les boutons de date (les callbacks seront définis après avoir créé row_dict)
        date_debut_icon_btn = ft.IconButton(
            icon=ft.Icons.CALENDAR_TODAY,
            icon_color=Theme.TEXT_MUTED,
            style=ft.ButtonStyle(padding=0),
        )
        date_debut_icon_btn.on_hover = lambda e, btn=date_debut_icon_btn: self._toggle_icon_color(btn, e)
        date_debut_click_zone = ft.Container(
            content=ft.Row(
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[date_debut_icon_btn, date_debut_field],
            ),
        )

        date_echeance_icon_btn = ft.IconButton(
            icon=ft.Icons.EVENT_AVAILABLE,
            icon_color=Theme.TEXT_MUTED,
            style=ft.ButtonStyle(padding=0),
        )
        date_echeance_icon_btn.on_hover = lambda e, btn=date_echeance_icon_btn: self._toggle_icon_color(btn, e)
        date_echeance_click_zone = ft.Container(
            content=ft.Row(
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[date_echeance_icon_btn, date_echeance_field],
            ),
        )

        date_cloture_action_icon_btn = ft.IconButton(
            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
            icon_color=Theme.TEXT_MUTED,
            style=ft.ButtonStyle(padding=0),
        )
        date_cloture_action_icon_btn.on_hover = lambda e, btn=date_cloture_action_icon_btn: self._toggle_icon_color(btn, e)
        date_cloture_action_click_zone = ft.Container(
            content=ft.Row(
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[date_cloture_action_icon_btn, date_cloture_action_field],
            ),
        )
        
        # ========== RAPPEL AUTOMATIQUE ==========
        # Type de rappel : Unique (date+heure) ou Récurrent (fréquence+heure)
        type_rappel_dropdown = create_dropdown(
            "Type de rappel",
            ["Aucun", "Unique", "Récurrent"],
            value=row_data.get('type_rappel', 'Aucun'),
            prefix_icon=ft.Icons.NOTIFICATIONS
        )
        
        # Date unique pour rappel ponctuel
        date_rappel_unique_field = create_text_field(
            "Date du rappel",
            value=row_data.get('date_rappel_unique', ''),
            hint_text="Cliquez sur l'icône",
            read_only=True,
            cursor_height=0
        )
        date_rappel_unique_field.width = 140
        date_rappel_unique_icon = ft.IconButton(
            icon=ft.Icons.CALENDAR_TODAY,
            icon_color=Theme.TEXT_MUTED,
            on_click=lambda e, f=date_rappel_unique_field: self._open_action_date_picker(f, e),
            style=ft.ButtonStyle(padding=0),
        )
        date_rappel_unique_icon.on_hover = lambda e, btn=date_rappel_unique_icon: self._toggle_icon_color(btn, e)
        date_rappel_unique_container = ft.Container(
            content=ft.Row(
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[date_rappel_unique_icon, date_rappel_unique_field],
            ),
        )
        
        # Fréquence pour rappel récurrent
        frequence_rappel_dropdown = create_dropdown(
            "Fréquence",
            ["Tous les jours", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche", "Toutes les semaines", "Tous les mois"],
            value=row_data.get('frequence_rappel', 'Lundi'),
            prefix_icon=ft.Icons.REPEAT
        )
        
        # Heure du rappel avec dropdowns pour heures et minutes
        current_time = row_data.get('heure_rappel', '08:00').split(':')
        current_heure = current_time[0] if len(current_time) > 0 else '08'
        current_minute = current_time[1] if len(current_time) > 1 else '00'
        
        heures_dropdown = ft.Dropdown(
            label="Heure",
            options=[DropdownOption(f"{h:02d}") for h in range(24)],
            value=current_heure,
            width=80,
            text_size=13,
            filled=True,
            bgcolor=Theme.BG_SECONDARY,
            border_color=Theme.TEXT_MUTED,
        )
        
        minutes_dropdown = ft.Dropdown(
            label="Min",
            options=[DropdownOption(f"{m:02d}") for m in [0, 15, 30, 45]],
            value=current_minute if current_minute in ['00', '15', '30', '45'] else '00',
            width=80,
            text_size=13,
            filled=True,
            bgcolor=Theme.BG_SECONDARY,
            border_color=Theme.TEXT_MUTED,
        )
        
        # Switch activation rappel avec style amélioré
        rappel_active_switch = ft.Switch(
            label="Activer le rappel",
            value=row_data.get('rappel_actif', False),
            active_color=Theme.SUCCESS,
            label_style=ft.TextStyle(size=13, weight=ft.FontWeight.BOLD),
        )
        
        # Conteneurs conditionnels pour date unique et fréquence avec meilleure présentation
        date_unique_row = ft.Container(
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.EVENT, size=20, color=Theme.PRIMARY),
                            ft.Text("Date du rappel :", size=13, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                        ]
                    ),
                    ft.Container(
                        padding=10,
                        border_radius=8,
                        bgcolor=Theme.BG_TERTIARY,
                        content=ft.Row(
                            spacing=12,
                            controls=[
                                date_rappel_unique_container,
                                ft.Icon(ft.Icons.ACCESS_TIME, size=20, color=Theme.PRIMARY),
                                heures_dropdown,
                                ft.Text(":", size=16, color=Theme.TEXT_PRIMARY),
                                minutes_dropdown,
                            ]
                        )
                    )
                ]
            )
        )
        
        frequence_row = ft.Container(
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.REPEAT, size=20, color=Theme.SUCCESS),
                            ft.Text("Fréquence de répétition :", size=13, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                        ]
                    ),
                    ft.Container(
                        padding=10,
                        border_radius=8,
                        bgcolor=Theme.BG_TERTIARY,
                        content=ft.Column(
                            spacing=10,
                            controls=[
                                frequence_rappel_dropdown,
                                ft.Row(
                                    spacing=12,
                                    controls=[
                                        ft.Icon(ft.Icons.ACCESS_TIME, size=20, color=Theme.SUCCESS),
                                        ft.Text("à", size=13, color=Theme.TEXT_MUTED),
                                        heures_dropdown,
                                        ft.Text(":", size=16, color=Theme.TEXT_PRIMARY),
                                        minutes_dropdown,
                                    ]
                                )
                            ]
                        )
                    )
                ]
            )
        )
        
        # Déterminer le contenu initial selon le type
        initial_type = row_data.get('type_rappel', 'Aucun')
        initial_controls = []
        if initial_type == "Unique":
            initial_controls = [date_unique_row]
        elif initial_type == "Récurrent":
            initial_controls = [frequence_row]
        
        # Conteneur parent pour les options de rappel conditionnelles
        rappel_options_container = ft.Column(
            spacing=8,
            controls=initial_controls
        )
        
        # Stocker une référence à self pour le callback
        page_instance = self
        
        # Callback pour changer l'affichage selon le type de rappel
        def on_type_rappel_change(e):
            type_value = e.control.value if hasattr(e.control, 'value') else e.data
            
            # Reconstruire le contenu du conteneur selon le type
            if type_value == "Unique":
                rappel_options_container.controls = [date_unique_row]
            elif type_value == "Récurrent":
                rappel_options_container.controls = [frequence_row]
            else:
                rappel_options_container.controls = []
            
            # Update toute la page au lieu du conteneur seul
            try:
                if page_instance.page:
                    page_instance.page.update()
                elif rappel_options_container.page:
                    rappel_options_container.update()
            except Exception as ex:
                print(f"Erreur update rappel: {ex}")
        
        type_rappel_dropdown.on_change = on_type_rappel_change
        
        # Callback pour désactiver le rappel si action clôturée
        def on_statut_change(e):
            statut_value = e.control.value if hasattr(e.control, 'value') else e.data
            if statut_value == "Clôturée":
                rappel_active_switch.value = False
                try:
                    rappel_active_switch.update()
                except:
                    pass
        
        # Créer le statut dropdown avec callback
        statut_dropdown = create_dropdown("Statut", ["En cours", "Clôturée"], value=row_data.get('statut', 'En cours'), prefix_icon=ft.Icons.FLAG)
        statut_dropdown.on_change = on_statut_change
        
        # Créer un conteneur pour l'indicateur d'échéance et urgence
        echeance_urgence_container = ft.Container(
            padding=12,
            border_radius=8,
            bgcolor=Theme.BG_TERTIARY,
            border=ft.Border(
                top=ft.BorderSide(2, Theme.OUTLINE),
                right=ft.BorderSide(2, Theme.OUTLINE),
                bottom=ft.BorderSide(2, Theme.OUTLINE),
                left=ft.BorderSide(2, Theme.OUTLINE),
            ),
            content=ft.Text("", size=13),
        )
        
        # Fonction pour mettre à jour l'indicateur d'échéance
        def update_echeance_indicator():
            date_echeance_str = date_echeance_field.value.strip()
            if not date_echeance_str:
                echeance_urgence_container.content = ft.Text(
                    "Aucune échéance définie",
                    size=12,
                    color=Theme.TEXT_MUTED,
                    italic=True,
                )
                echeance_urgence_container.bgcolor = Theme.BG_TERTIARY
                try:
                    echeance_urgence_container.update()
                except:
                    pass
                return
            
            try:
                from datetime import datetime
                date_echeance = datetime.strptime(date_echeance_str, "%d/%m/%Y")
                today = datetime.now()
                delta = (date_echeance - today).days
                
                # Déterminer le niveau d'urgence
                if delta < 0:
                    urgence_text = f"RETARD de {abs(delta)} jour(s)"
                    urgence_label = "[Attention] RETARD"
                    urgence_color = ft.Colors.WHITE
                    bg_color = ft.Colors.RED_700
                    icon = ft.Icons.ERROR
                elif delta == 0:
                    urgence_text = "L'échéance est aujourd'hui"
                    urgence_label = "[Urgent] AUJOURD'HUI"
                    urgence_color = ft.Colors.WHITE
                    bg_color = ft.Colors.RED_700
                    icon = ft.Icons.WARNING_AMBER
                elif delta <= 3:
                    urgence_text = f"{delta} jour(s) restant(s)"
                    urgence_label = "[Critique] CRITIQUE"
                    urgence_color = ft.Colors.WHITE
                    bg_color = ft.Colors.RED_600
                    icon = ft.Icons.PRIORITY_HIGH
                elif delta <= 7:
                    urgence_text = f"{delta} jours restants"
                    urgence_label = "[Urgent] URGENT"
                    urgence_color = ft.Colors.WHITE
                    bg_color = ft.Colors.ORANGE_700
                    icon = ft.Icons.TIMER
                elif delta <= 14:
                    urgence_text = f"{delta} jours restants"
                    urgence_label = "[Attention] ATTENTION"
                    urgence_color = ft.Colors.BLACK
                    bg_color = ft.Colors.YELLOW_700
                    icon = ft.Icons.ACCESS_TIME
                else:
                    urgence_text = f"{delta} jours restants"
                    urgence_label = "[Normal] NORMAL"
                    urgence_color = ft.Colors.WHITE
                    bg_color = ft.Colors.GREEN_700
                    icon = ft.Icons.CHECK_CIRCLE
                
                echeance_urgence_container.content = ft.Column(
                    spacing=5,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=10,
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(icon, size=24, color=urgence_color),
                                ft.Text(
                                    urgence_label,
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=urgence_color,
                                ),
                            ],
                        ),
                        ft.Text(
                            urgence_text,
                            size=13,
                            color=urgence_color,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                )
                echeance_urgence_container.bgcolor = bg_color
                echeance_urgence_container.border = ft.Border(
                top=ft.BorderSide(2, bg_color),
                right=ft.BorderSide(2, bg_color),
                bottom=ft.BorderSide(2, bg_color),
                left=ft.BorderSide(2, bg_color),
            )
                try:
                    echeance_urgence_container.update()
                except:
                    pass
            except ValueError:
                echeance_urgence_container.content = ft.Text(
                    "Format de date invalide",
                    size=13,
                    color=Theme.DANGER,
                    weight=ft.FontWeight.BOLD,
                )
                echeance_urgence_container.bgcolor = ft.Colors.RED_100
                echeance_urgence_container.border = ft.Border(
                top=ft.BorderSide(2, Theme.DANGER),
                right=ft.BorderSide(2, Theme.DANGER),
                bottom=ft.BorderSide(2, Theme.DANGER),
                left=ft.BorderSide(2, Theme.DANGER),
            )
                try:
                    echeance_urgence_container.update()
                except:
                    pass
        
        # Callback pour mettre à jour l'indicateur quand la date change
        def on_date_fin_change(e):
            update_echeance_indicator()
        
        # Créer un dictionnaire de retour qui sera la référence
        row_dict = {
            'desc': create_text_field("Action corrective", value=row_data.get('desc', ''), prefix_icon=ft.Icons.CHECKLIST),
            'responsable': create_text_field("Responsable", value=row_data.get('responsable', ''), prefix_icon=ft.Icons.PERSON),
            'date_debut': date_debut_field,
            'date_debut_container': date_debut_click_zone,
            'date_echeance': date_echeance_field,
            'date_echeance_container': date_echeance_click_zone,
            'date_cloture_action': date_cloture_action_field,
            'date_cloture_action_container': date_cloture_action_click_zone,
            'cost': create_text_field("Coût (EUR)", value=row_data.get('cost', ''), prefix_icon=ft.Icons.EURO, keyboard_type=ft.KeyboardType.NUMBER, input_filter=ft.InputFilter(regex_string=r"[0-9.,]")),
            'verification': create_dropdown("Vérification de l'efficacité", ["Non évaluée", "Efficace", "Partiellement efficace", "Non efficace"], value=row_data.get('verification'), prefix_icon=ft.Icons.VERIFIED),
            'preuve_efficacite': create_text_field("Preuve d'efficacité", value=row_data.get('preuve_efficacite', ''), multiline=True, min_lines=2, prefix_icon=ft.Icons.VERIFIED_USER),
            'statut': statut_dropdown,
            'echeance_urgence_container': echeance_urgence_container,
            'update_echeance_indicator': update_echeance_indicator,
            'type_rappel': type_rappel_dropdown,
            'date_rappel_unique': date_rappel_unique_field,
            'date_rappel_unique_container': date_rappel_unique_container,
            'date_unique_row': date_unique_row,
            'frequence_rappel': frequence_rappel_dropdown,
            'frequence_row': frequence_row,
            'rappel_options_container': rappel_options_container,
            'heures_dropdown': heures_dropdown,
            'minutes_dropdown': minutes_dropdown,
            'rappel_actif': rappel_active_switch,
            'fichiers': row_data.get('fichiers', []) if isinstance(row_data.get('fichiers'), list) else ([{'nom': row_data.get('fichier_nom', ''), 'path': row_data.get('fichier_path', '')}] if row_data.get('fichier_nom') else []),
        }
        
        # Conteneur pour afficher les fichiers attachés avec possibilité de suppression
        attached_files_display = ft.Container(
            content=self._render_action_files_with_delete(row_dict)
        )
        
        # FilePicker pour pièces jointes - utilise row_dict comme référence
        action_file_picker = ft.FilePicker(
            on_result=lambda e, r=row_dict: self._on_action_file_chosen(e, r)
        )
        
        attach_btn = ft.ElevatedButton(
            text="Joindre fichier(s)",
            icon=ft.Icons.ATTACH_FILE,
            on_click=lambda e, fp=action_file_picker: self._open_action_file_picker(fp),
            bgcolor=Theme.BG_TERTIARY,
            color=Theme.TEXT_PRIMARY,
            height=40,
        )
        
        # Ajouter les références au dictionnaire
        row_dict['file_picker'] = action_file_picker
        row_dict['attach_button'] = attach_btn
        row_dict['files_display'] = attached_files_display
        
        # Définir les callbacks des boutons de date maintenant qu'on a row_dict
        date_debut_icon_btn.on_click = lambda e, f=date_debut_field, r=row_dict: self._open_action_date_picker(f, e, r)
        date_echeance_icon_btn.on_click = lambda e, f=date_echeance_field, r=row_dict: self._open_action_date_picker(f, e, r)
        date_cloture_action_icon_btn.on_click = lambda e, f=date_cloture_action_field, r=row_dict: self._open_action_date_picker(f, e, r)
        
        # Initialiser l'indicateur d'échéance
        update_echeance_indicator()
        
        return row_dict
    
    def _on_files_chosen(self, e):
        if e.files:
            for f in e.files:
                self.attachments.append({"name": f.name, "path": f.path, "size": f.size})
            self._refresh_attachments()
    
    def _refresh_attachments(self):
        try:
            self.attachments_container.content = self._render_attachments()
            if hasattr(self.attachments_container, 'update'):
                self.attachments_container.update()
        except Exception as ex:
            print(f"[ERREUR] _refresh_attachments: {ex}")
    
    def _remove_attachment(self, name):
        self.attachments = [a for a in self.attachments if a['name'] != name]
        self._refresh_attachments()
    
    def _render_attachments(self):
        if not self.attachments:
            return ft.Text("Aucune pièce jointe", color=Theme.TEXT_MUTED)
        chips = [
            ft.Chip(
                label=ft.Text(a['name'], size=12),
                leading=ft.Icon(ft.Icons.ATTACH_FILE, size=16),
                delete_icon=ft.Icon(ft.Icons.CLOSE, size=14),
                on_delete=lambda e, name=a['name']: self._remove_attachment(name)
            ) for a in self.attachments
        ]
        return ft.Row(wrap=True, spacing=6, controls=chips)
    
    def _open_file_picker(self, e=None):
        try:
            if not hasattr(self, 'page') or not self.page:
                print("[AVERTISSEMENT] Page non attachée, impossible d'ouvrir le file picker")
                return
            if self.file_picker not in self.page.overlay:
                self.page.overlay.append(self.file_picker)
                self.page.update()
            self.file_picker.pick_files(allow_multiple=True)
        except Exception as ex:
            print(f"[ERREUR] _open_file_picker: {ex}")
            import traceback
            traceback.print_exc()
    
    def _open_action_file_picker(self, file_picker):
        """Ouvre le file picker pour une action corrective spécifique."""
        try:
            if self.page and file_picker not in self.page.overlay:
                self.page.overlay.append(file_picker)
                self.page.update()
            file_picker.pick_files(allow_multiple=True)  # Permettre plusieurs fichiers
        except Exception as ex:
            print(f"Erreur ouverture file picker: {ex}")
    
    def _on_action_file_chosen(self, e, row):
        """Callback quand des fichiers sont choisis pour une action corrective."""
        if e.files and len(e.files) > 0:
            # Initialiser la liste si elle n'existe pas
            if 'fichiers' not in row or not isinstance(row['fichiers'], list):
                row['fichiers'] = []
            
            # Ajouter les nouveaux fichiers
            for file in e.files:
                row['fichiers'].append({
                    'nom': file.name,
                    'path': file.path
                })
            
            # Mettre à jour l'affichage
            row['files_display'].content = self._render_action_files_with_delete(row)
            try:
                row['files_display'].update()
            except:
                pass
    
    def _render_action_files_with_delete(self, row):
        """Affiche la liste des fichiers avec possibilité de suppression."""
        fichiers = row.get('fichiers', [])
        
        if not fichiers or len(fichiers) == 0:
            return ft.Text("Aucun fichier", color=Theme.TEXT_MUTED, size=12)
        
        chips = []
        for i, fichier in enumerate(fichiers):
            if fichier.get('nom'):
                chips.append(
                    ft.Chip(
                        label=ft.Text(fichier['nom'], size=12),
                        leading=ft.Icon(ft.Icons.ATTACH_FILE, size=16),
                        delete_icon=ft.Icon(ft.Icons.CLOSE, size=14),
                        on_delete=lambda e, r=row, idx=i: self._remove_action_file_by_index(r, idx),
                    )
                )
        
        return ft.Row(wrap=True, spacing=6, run_spacing=6, controls=chips) if chips else ft.Text("Aucun fichier", color=Theme.TEXT_MUTED, size=12)
    
    def _remove_action_file_by_index(self, row, index):
        """Retire un fichier d'une action corrective par son index."""
        fichiers = row.get('fichiers', [])
        if 0 <= index < len(fichiers):
            fichiers.pop(index)
            row['fichiers'] = fichiers
            row['files_display'].content = self._render_action_files_with_delete(row)
            try:
                row['files_display'].update()
            except:
                pass
    
    # ========== Méthodes DatePicker ==========
    def _close_picker(self, picker_attr: str = None, picker: ft.DatePicker = None):
        """Ferme et supprime un picker donné ou par attribut."""
        try:
            target = picker if picker is not None else getattr(self, picker_attr, None)
            if not target:
                return
            target.open = False
            if self.page and target in self.page.overlay:
                self.page.overlay.remove(target)
            if picker_attr:
                setattr(self, picker_attr, None)
            if self.page:
                self.page.update()
        except Exception as ex:
            print(f"Erreur fermeture picker {picker_attr}: {ex}")

    def _toggle_icon_color(self, icon_btn: ft.IconButton, e):
        """Colore l'icône au survol pour indiquer le clic possible."""
        try:
            icon_btn.icon_color = Theme.PRIMARY if str(e.data).lower() == "true" else Theme.TEXT_MUTED
            if icon_btn.page:
                icon_btn.update()
        except Exception:
            pass

    def _open_generic_date_picker(self, field: ft.TextField, picker_attr: str = None):
        """Ouvre le calendrier personnalisé hors ligne pour un champ de date."""
        try:
            if not self.page:
                return

            # Parser la date actuelle si elle existe
            initial_date = None
            if field.value:
                try:
                    initial_date = datetime.strptime(field.value, "%Y-%m-%d").date()
                except:
                    initial_date = None
            
            # Callback quand une date est sélectionnée
            def on_date_selected(selected_date):
                field.value = selected_date.strftime('%Y-%m-%d')
                if field.page:
                    field.update()
            
            # Créer et ouvrir le calendrier
            calendar_dialog = CustomCalendar(on_date_selected, initial_date)
            
            # Ajouter à l'overlay de la page
            if self.page:
                self.page.overlay.append(calendar_dialog)
                calendar_dialog.open = True
                self.page.update()
        except Exception as ex:
            print(f"Erreur ouverture calendrier: {ex}")

    def _open_date_picker(self, e=None):
        """Ouvre le calendrier pour la date de détection."""
        self._open_generic_date_picker(self.date_field, "date_picker")

    def _open_closure_date_picker(self, e=None):
        """Ouvre le calendrier pour la date de clôture."""
        self._open_generic_date_picker(self.closure_date_field, "closure_date_picker")
    
    def _open_action_date_picker(self, field, e=None, row_dict=None):
        """Ouvre le calendrier personnalisé hors ligne pour un champ de date d'action."""
        try:
            if not self.page:
                return

            # Parser la date actuelle si elle existe
            initial_date = None
            if field.value:
                try:
                    # Parser le format DD/MM/YYYY
                    initial_date = datetime.strptime(field.value, "%d/%m/%Y").date()
                except:
                    initial_date = None
            
            # Callback quand une date est sélectionnée
            def on_date_selected(selected_date):
                # Convertir au format DD/MM/YYYY pour l'affichage
                field.value = selected_date.strftime("%d/%m/%Y")
                if field.page:
                    field.update()
                
                # Si c'est un champ date_echeance et qu'on a la référence row_dict, mettre à jour l'indicateur
                if row_dict and 'update_echeance_indicator' in row_dict:
                    if field == row_dict.get('date_echeance'):
                        row_dict['update_echeance_indicator']()
            
            # Créer et ouvrir le calendrier
            calendar_dialog = CustomCalendar(on_date_selected, initial_date)
            
            # Ajouter à l'overlay de la page
            if self.page:
                self.page.overlay.append(calendar_dialog)
                calendar_dialog.open = True
                self.page.update()
        except Exception as ex:
            print(f"Erreur ouverture calendrier action: {ex}")
    
    # ========== Méthodes Gravité avec couleurs ==========
    def _build_severity_selector(self):
        """Construit le sélecteur de gravité avec boutons colorés."""
        severities = [
            ("Mineure", Theme.SUCCESS, ft.Icons.CHECK_CIRCLE),
            ("Majeure", Theme.WARNING, ft.Icons.WARNING),
            ("Critique", Theme.DANGER, ft.Icons.ERROR),
        ]
        
        buttons = []
        for severity, color, icon in severities:
            is_selected = self.current_severity == severity
            buttons.append(
                ft.Container(
                    content=ft.Row(
                        spacing=5,
                        controls=[
                            ft.Icon(icon, color=color if is_selected else Theme.TEXT_MUTED, size=20),
                            ft.Text(
                                severity, 
                                color=color if is_selected else Theme.TEXT_MUTED, 
                                weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                                size=13
                            ),
                        ]
                    ),
                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.2, color) if is_selected else Theme.BG_TERTIARY,
                    border=ft.Border(
                top=ft.BorderSide(2, color),
                right=ft.BorderSide(2, color),
                bottom=ft.BorderSide(2, color),
                left=ft.BorderSide(2, color),
            ) if is_selected else ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                    on_click=lambda e, s=severity: self._select_severity(s),
                    ink=True,
                )
            )
        
        return ft.Column(
            spacing=5,
            controls=[
                ft.Text("Gravité", size=12, color=Theme.TEXT_MUTED),
                ft.Row(spacing=10, controls=buttons),
            ]
        )
    
    def _select_severity(self, severity: str):
        """Sélectionne une gravité."""
        self.current_severity = severity
        # Rafraîchir la section A
        if self.form_tab_index == 0:
            self.form_content.content = ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[self._build_form_section_a()]
            )
            self.form_content.update()
    
    # ========== Méthodes Suppression Actions ==========
    def _remove_immediate_row(self, index: int):
        """Supprime une action immédiate."""
        if len(self.immediate_rows) > 1:
            self.immediate_rows.pop(index)
            self.form_content.content = ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[self._build_form_section_c()]
            )
            self.form_content.update()
    
    def _remove_corrective_row(self, index: int):
        """Supprime une action corrective."""
        if len(self.corrective_rows) > 1:
            self.corrective_rows.pop(index)
            self.form_content.content = ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[self._build_form_section_c()]
            )
            self.form_content.update()
    
    def _on_method_toggle(self, e=None):
        if self.form_tab_index == 1:
            self.form_content.content = ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[self._build_form_section_b()]
            )
            self.form_content.update()
    
    def _toggle_ishikawa_cat(self, cat, selected):
        if selected:
            self.selected_ishikawa_cats.add(cat)
        else:
            self.selected_ishikawa_cats.discard(cat)
        if self.form_tab_index == 1:
            self.form_content.content = ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[self._build_form_section_b()]
            )
            self.form_content.update()
    
    def _add_ishikawa_cause(self, cat):
        fields = self.ishikawa_categories.get(cat, [])
        fields.append(create_text_field(f"{cat} - cause {len(fields)+1}", multiline=True, min_lines=1, hint_text="Cause..."))
        self.ishikawa_categories[cat] = fields
        if self.form_tab_index == 1:
            self.form_content.content = ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[self._build_form_section_b()]
            )
            self.form_content.update()
    
    def _add_immediate_row(self):
        self.immediate_rows.append(self._build_immediate_row())
        self.form_content.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[self._build_form_section_c()]
        )
        self.form_content.update()
    
    def _add_corrective_row(self):
        self.corrective_rows.append(self._build_corrective_row())
        self.form_content.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[self._build_form_section_c()]
        )
        self.form_content.update()
    
    def _build_form_page(self):
        """Construit le formulaire NC en pleine page avec onglets."""
        is_edit = self.editing_nc is not None
        
        # Header
        header = ft.Container(
            padding=ft.Padding(left=20, right=20, top=15, bottom=15),
            content=ft.Row(
                controls=[
                    ft.IconButton(ft.Icons.ARROW_BACK, icon_color=Theme.TEXT_MUTED, on_click=lambda e: self._close_form()),
                    ft.Text(
                        f"[Note] {'Modifier' if is_edit else 'Nouvelle'} NC",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=Theme.TEXT_PRIMARY,
                    ),
                ]
            ),
        )
        
        # Tabs du formulaire avec design amélioré
        self.form_tabs = ft.Tabs(
            selected_index=self.form_tab_index,
            animation_duration=300,
            scrollable=False,
            tab_alignment=ft.TabAlignment.START,
            indicator_color=Theme.PRIMARY,
            indicator_tab_size=True,
            indicator_border_radius=3,
            label_color=Theme.PRIMARY,
            unselected_label_color=Theme.TEXT_MUTED,
            divider_color=Theme.OUTLINE,
            on_change=self._on_form_tab_change,
            expand=False,
            tabs=[
                ft.Tab(
                    text="Identification",
                    icon=ft.Icons.INFO_ROUNDED,
                ),
                ft.Tab(
                    text="Analyse",
                    icon=ft.Icons.SEARCH_ROUNDED,
                ),
                ft.Tab(
                    text="Actions",
                    icon=ft.Icons.BUILD_ROUNDED,
                ),
                ft.Tab(
                    text="Clôture",
                    icon=ft.Icons.CHECK_CIRCLE_ROUNDED,
                ),
            ],
        )
        
        # Contenu avec scroll - utilise l'index actuel
        sections = [self._build_form_section_a, self._build_form_section_b, self._build_form_section_c, self._build_form_section_d]
        self.form_content = ft.Container(
            expand=True, 
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[sections[self.form_tab_index]()]
            )
        )
        
        # Boutons de navigation entre onglets
        prev_btn = ft.ElevatedButton(
            text="< Précédent",
            icon=ft.Icons.ARROW_BACK,
            on_click=self._go_prev_tab,
            bgcolor=Theme.PRIMARY,
            color=ft.Colors.WHITE,
            visible=self.form_tab_index > 0,
        )
        next_btn = ft.ElevatedButton(
            text="Suivant >",
            icon=ft.Icons.ARROW_FORWARD,
            on_click=self._go_next_tab,
            bgcolor=Theme.SUCCESS,
            color=ft.Colors.WHITE,
            visible=self.form_tab_index < 3,
        )
        
        # Footer avec navigation ET actions
        # Boutons d'action (avec suppression si en mode édition)
        action_buttons = [
            self.form_error_text,
            create_button("Annuler", style="secondary", on_click=lambda e: self._close_form()),
        ]
        
        # Ajouter le bouton Supprimer uniquement en mode édition
        if self.editing_nc:
            action_buttons.append(
                create_button(
                    "Supprimer",
                    icon=ft.Icons.DELETE_FOREVER,
                    style="danger",
                    on_click=self._confirm_delete_nc
                )
            )
        
        action_buttons.append(
            create_button("Enregistrer", icon=ft.Icons.SAVE, style="success", on_click=self._save_form)
        )
        
        footer = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(controls=[prev_btn, next_btn], spacing=10),
                ft.Row(controls=action_buttons, spacing=10),
            ]
        )
        
        return ft.Container(
            expand=True,
            padding=20,
            content=ft.Column(
                expand=True,
                spacing=10,
                controls=[
                    header,
                    self.form_tabs,
                    self.form_content,
                    footer,
                ]
            )
        )
    
    def _on_form_tab_change(self, e):
        """Change l'onglet du formulaire avec animation."""
        sections = [self._build_form_section_a, self._build_form_section_b, self._build_form_section_c, self._build_form_section_d]
        self.form_tab_index = e.control.selected_index
        # Recréer le conteneur avec scroll
        self.form_content.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[sections[self.form_tab_index]()]
        )
        self.form_content.update()
        # NE PAS reconstruire le formulaire complet ici - sinon on perd self.editing_nc
        # et le bouton Supprimer disparaît !
        # Juste mettre à jour les boutons de navigation
        self._update_form_navigation_buttons()
        self.page.update()
    
    def _go_prev_tab(self, e):
        """Aller à l'onglet précédent."""
        if self.form_tab_index > 0:
            self.form_tab_index -= 1
            # Ne pas reconstruire tout le formulaire - mettre à jour seulement le contenu et la navigation
            sections = [self._build_form_section_a, self._build_form_section_b, self._build_form_section_c, self._build_form_section_d]
            self.form_content.content = ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[sections[self.form_tab_index]()]
            )
            self.form_content.update()
            self._update_form_navigation_buttons()
            self.page.update()
    
    def _go_next_tab(self, e):
        """Aller à l'onglet suivant."""
        if self.form_tab_index < 3:
            self.form_tab_index += 1
            # Ne pas reconstruire tout le formulaire - mettre à jour seulement le contenu et la navigation
            sections = [self._build_form_section_a, self._build_form_section_b, self._build_form_section_c, self._build_form_section_d]
            self.form_content.content = ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[sections[self.form_tab_index]()]
            )
            self.form_content.update()
            self._update_form_navigation_buttons()
            self.page.update()
    
    def _update_form_navigation_buttons(self):
        """Met à jour la visibilité des boutons de navigation sans reconstruire tout le formulaire."""
        # Cette fonction est appelée pour éviter de perdre self.editing_nc
        # lors des changements d'onglets du formulaire
        pass  # Les boutons sont déjà gérés dans _build_form_page via form_tab_index
    
    def _build_form_section_a(self):
        """Section A - Identification."""
        try:
            severity_selector = self._build_severity_selector()
        except Exception as ex:
            print(f"[ERREUR] _build_severity_selector: {ex}")
            severity_selector = ft.Text("Erreur chargement gravité", color=Theme.DANGER)
        
        return create_card(content=ft.Column(spacing=10, controls=[
            ft.Text("Identification", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
            ft.Row(controls=[
                ft.Container(expand=1, content=self.ref_field),
                self.date_input_row,
            ]),
            ft.Row(controls=[
                ft.Container(expand=1, content=self.type_dropdown),
                ft.Container(expand=1, content=severity_selector),
                ft.Container(expand=1, content=self.imputation_dropdown),
            ]),
            ft.Row(controls=[
                ft.Container(expand=1, content=self.origin_field),
                ft.Container(expand=1, content=self.anomaly_dropdown),
            ]),
            ft.Row(controls=[
                ft.Container(expand=1, content=self.category_field),
                ft.Container(expand=1, content=self.location_field),
            ]),
            self.description_field,
            ft.Row(controls=[
                ft.Container(expand=1, content=self.product_field),
                ft.Container(expand=1, content=self.lot_field),
                ft.Container(expand=1, content=self.qty_field),
            ]),
            self.matieres_dropdown,
            ft.Text("Pièces jointes", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
            ft.Row(controls=[
                create_button("Ajouter des fichiers", icon=ft.Icons.ATTACH_FILE, style="secondary", on_click=self._open_file_picker),
                self.attachments_container,
            ]),
        ]))
    
    def _build_form_section_b(self):
        """Section B - Analyse."""
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
            sections.append(create_card(content=ft.Column(spacing=8, controls=[
                ft.Text("5 Pourquoi", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)
            ] + self.fivewhy_fields), padding=10, bgcolor=Theme.BG_TERTIARY))
        if self.method_ishikawa.value:
            sections.append(self._render_ishikawa())
        if not sections:
            return ft.Text("Sélectionnez au moins une méthodologie", color=Theme.TEXT_MUTED)
        return ft.Column(spacing=12, controls=sections)
    
    def _render_ishikawa(self):
        cat_checks = []
        for cat in self.ishikawa_categories.keys():
            cat_checks.append(ft.Checkbox(label=cat, value=cat in self.selected_ishikawa_cats, on_change=lambda e, c=cat: self._toggle_ishikawa_cat(c, e.control.value)))
        
        rows = []
        active = [c for c in self.ishikawa_categories.keys() if c in self.selected_ishikawa_cats]
        if not active:
            return ft.Column(spacing=8, controls=[
                ft.Text("Ishikawa", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                ft.Text("Choisir au moins un axe 5M", color=Theme.TEXT_MUTED),
                ft.Row(wrap=True, spacing=10, controls=cat_checks)
            ])
        
        for cat in active:
            fields = self.ishikawa_categories[cat]
            add_btn = create_button("Ajouter une cause", icon=ft.Icons.ADD, style="secondary", on_click=lambda e, c=cat: self._add_ishikawa_cause(c))
            card = create_card(content=ft.Column(spacing=6, controls=[
                ft.Text(cat, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY)
            ] + fields + [add_btn]), padding=10, bgcolor=Theme.BG_TERTIARY, expand=True)
            rows.append(card)
        
        return ft.Column(spacing=10, controls=[
            ft.Text("Ishikawa (5M)", weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
            ft.Row(wrap=True, spacing=10, controls=cat_checks)
        ] + rows + [self.ishikawa_synth_field])
    
    def _build_immediate_table(self):
        rows = []
        for idx, row in enumerate(self.immediate_rows):
            rows.append(create_card(content=ft.Row(spacing=8, controls=[
                ft.Text(f"{idx+1}.", color=Theme.TEXT_MUTED, width=20),
                ft.Container(expand=3, content=row['correction']),
                ft.Container(width=220, content=row['responsable']),
                ft.Container(width=300, content=row['date_container']),
                ft.Container(width=100, content=row['cost']),
                ft.IconButton(
                    ft.Icons.DELETE_OUTLINE,
                    icon_color=Theme.DANGER,
                    icon_size=20,
                    tooltip="Supprimer",
                    on_click=lambda e, i=idx: self._remove_immediate_row(i)
                ) if len(self.immediate_rows) > 1 else ft.Container(width=40),
            ]), padding=12, bgcolor=Theme.BG_TERTIARY))
        add_btn = create_button("Ajouter une action immédiate", icon=ft.Icons.ADD, style="secondary", on_click=lambda e: self._add_immediate_row())
        rows.append(add_btn)
        return ft.Column(spacing=10, controls=rows)
    
    def _build_corrective_table(self):
        rows = []
        for idx, row in enumerate(self.corrective_rows):
            # Ajouter le file_picker à la page si nécessaire
            if self.page and row['file_picker'] not in self.page.overlay:
                self.page.overlay.append(row['file_picker'])
            
            rows.append(create_card(content=ft.Column(spacing=6, controls=[
                ft.Row(spacing=8, controls=[
                    ft.Container(expand=True, content=row['desc']),
                    ft.IconButton(
                        ft.Icons.DELETE_OUTLINE,
                        icon_color=Theme.DANGER,
                        icon_size=20,
                        tooltip="Supprimer",
                        on_click=lambda e, i=idx: self._remove_corrective_row(i)
                    ) if len(self.corrective_rows) > 1 else ft.Container(width=40),
                ]),
                ft.Row(spacing=8, controls=[
                    ft.Container(width=200, content=row['responsable']),
                    ft.Container(width=300, content=row['date_debut_container']),
                    ft.Container(width=140, content=row['cost']),
                ]),
                ft.Row(spacing=8, controls=[
                    ft.Container(expand=1, content=row['verification']),
                    ft.Container(expand=1, content=row['preuve_efficacite']),
                ]),
                ft.Row(spacing=8, controls=[
                    ft.Container(width=180, content=row['statut']),
                    ft.Container(width=300, content=row['date_echeance_container']),
                    ft.Container(width=300, content=row['date_cloture_action_container']),
                ]),
                # Indicateur d'échéance et urgence
                ft.Container(
                    padding=ft.Padding(left=8, right=8, top=4, bottom=0),
                    content=row['echeance_urgence_container'],
                ),
                ft.Divider(height=1, color=Theme.TEXT_MUTED),
                ft.Container(
                    padding=15,
                    border_radius=10,
                    bgcolor=Theme.BG_SECONDARY,
                    border=ft.Border(
                top=ft.BorderSide(1, Theme.PRIMARY),
                right=ft.BorderSide(1, Theme.PRIMARY),
                bottom=ft.BorderSide(1, Theme.PRIMARY),
                left=ft.BorderSide(1, Theme.PRIMARY),
            ),
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, size=24, color=Theme.PRIMARY),
                                    ft.Text("Rappel automatique", size=15, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
                                ]
                            ),
                            ft.Row(
                                spacing=12,
                                controls=[
                                    ft.Container(width=200, content=row['type_rappel']),
                                    row['rappel_actif'],
                                ]
                            ),
                            # Utiliser le conteneur parent qui contient les options conditionnelles
                            row['rappel_options_container'],
                        ]
                    )
                ),
                ft.Divider(height=1, color=Theme.TEXT_MUTED),
                ft.Text("[PJ] Pièce jointe", size=13, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
                row['attach_button'],
                row['files_display'],
            ])))
        add_btn = create_button("Ajouter une action corrective", icon=ft.Icons.ADD, style="secondary", on_click=lambda e: self._add_corrective_row())
        rows.append(add_btn)
        return ft.Column(spacing=10, controls=rows)
    
    def _build_form_section_c(self):
        """Section C - Actions."""
        return create_card(content=ft.Column(spacing=12, controls=[
            ft.Text("Actions", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
            ft.Text("Actions immédiates (Corrections)", weight=ft.FontWeight.BOLD, color=Theme.DANGER),
            self._build_immediate_table(),
            ft.Text("Actions correctives", weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
            self._build_corrective_table(),
        ]))
    
    def _build_form_section_d(self):
        """Section D - Clôture."""
        return create_card(content=ft.Column(spacing=10, controls=[
            ft.Text("Clôture", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
            ft.Row(spacing=8, controls=[
                ft.Container(expand=1, content=self.status_dropdown),
                self.closure_date_input_row,
            ]),
            ft.Row(spacing=8, controls=[
                ft.Container(expand=1, content=self.verifier_field),
                ft.Container(expand=1, content=self.efficacy_dropdown),
            ]),
            self.closure_comments_field,
        ]))
    
    def _collect_actions(self):
        import json
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
            # Construire l'heure à partir des dropdowns
            heure = row['heures_dropdown'].value or '08'
            minute = row['minutes_dropdown'].value or '00'
            heure_rappel = f"{heure}:{minute}"
            
            corrective_data.append({
                'desc': row['desc'].value,
                'responsable': row['responsable'].value,
                'date_debut': row['date_debut'].value,
                'date_echeance': row['date_echeance'].value,
                'date_cloture_action': row['date_cloture_action'].value,
                'cost': row['cost'].value,
                'verification': row['verification'].value,
                'preuve_efficacite': row['preuve_efficacite'].value,
                'statut': row['statut'].value,
                # Pour compatibilité ascendante, garder date_fin qui pointe vers date_echeance
                'date_fin': row['date_echeance'].value,
                'type_rappel': row['type_rappel'].value,
                'date_rappel_unique': row['date_rappel_unique'].value,
                'frequence_rappel': row['frequence_rappel'].value,
                'heure_rappel': heure_rappel,
                'rappel_actif': row['rappel_actif'].value,
                'fichiers': row.get('fichiers', []),  # Liste de fichiers
                # Pour compatibilité ascendante avec anciennes NC
                'fichier_nom': row.get('fichiers', [{}])[0].get('nom', '') if row.get('fichiers') else '',
                'fichier_path': row.get('fichiers', [{}])[0].get('path', '') if row.get('fichiers') else '',
            })
        return immediate_data, corrective_data
    
    def _collect_analysis_details(self):
        details = {}
        details['5why'] = {
            'whys': [f.value for f in self.fivewhy_fields],
            'root_cause': self.root_cause_field.value,
        }
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
    
    def _save_form(self, e):
        """Sauvegarde le formulaire NC."""
        import json
        try:
            immediate_data, corrective_data = self._collect_actions()
            analysis_details = self._collect_analysis_details()
            selected_methods = analysis_details.get('method', '')
            
            # Valeurs par défaut
            if not self.date_field.value:
                self.date_field.value = datetime.now().strftime("%Y-%m-%d")
            if not self.type_dropdown.value:
                self.type_dropdown.value = "Interne"
            if not self.current_severity:
                self.current_severity = "Mineure"
            if not self.status_dropdown.value:
                self.status_dropdown.value = "Ouverte"
            
            # Parse quantité
            qty_val = None
            if self.qty_field.value:
                try:
                    qty_val = int(self.qty_field.value)
                except ValueError:
                    pass
            
            data = {
                'reference': self.ref_field.value or self.db.generate_nc_reference(),
                'date_detection': self.date_field.value,
                'type_nc': self.type_dropdown.value or "Interne",
                'gravite': self.current_severity or "Mineure",
                'origine': self.origin_field.value or '',
                'type_anomalie': self.anomaly_dropdown.value or '',
                'categorie_nc': self.category_field.value or '',
                'imputation': self.imputation_dropdown.value or '',
                'description': self.description_field.value or '',
                'produit_concerne': self.product_field.value or '',
                'lot_serie': self.lot_field.value or '',
                'quantite_affectee': qty_val,
                'matieres_reclames': self.matieres_dropdown.value or '',
                'lieu_detection': self.location_field.value or '',
                'pieces_jointes': json.dumps(self.attachments or []),
                'methode_analyse': selected_methods or '',
                'cause_racine': self.root_cause_field.value or '',
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
            
            # Nom de l'utilisateur pour l'historique
            user_name = self.user.get('username', 'Utilisateur')
            
            if self.editing_nc:
                # MODIFICATION - Comparer les champs et enregistrer les changements
                nc_id = self.editing_nc['id']
                old_nc = self.editing_nc
                
                # Liste des champs à surveiller avec leurs labels
                field_labels = {
                    'reference': 'Référence',
                    'date_detection': 'Date de détection',
                    'type_nc': 'Type de NC',
                    'gravite': 'Gravité',
                    'origine': 'Origine',
                    'type_anomalie': "Type d'anomalie",
                    'categorie_nc': 'Catégorie',
                    'imputation': 'Imputation',
                    'description': 'Description',
                    'produit_concerne': 'Produit concerné',
                    'lot_serie': 'Lot/Série',
                    'quantite_affectee': 'Quantité affectée',
                    'matieres_reclames': 'Matières réclamées',
                    'lieu_detection': 'Lieu de détection',
                    'methode_analyse': "Méthode d'analyse",
                    'cause_racine': 'Cause racine',
                    'analyse_portee': 'Analyse de la portée',
                    'statut': 'Statut',
                    'date_cloture': 'Date de clôture',
                    'efficacite': 'Efficacité',
                    'commentaires_cloture': 'Commentaires de clôture',
                }
                
                # Comparer et enregistrer chaque modification
                changes_count = 0
                for field_key, field_label in field_labels.items():
                    old_value = old_nc.get(field_key)
                    new_value = data.get(field_key)
                    
                    # Convertir en string pour comparaison
                    old_str = str(old_value) if old_value not in (None, '') else ''
                    new_str = str(new_value) if new_value not in (None, '') else ''
                    
                    if old_str != new_str:
                        # Détecter si c'est une clôture
                        if field_key == 'statut' and new_value == 'Clôturée' and old_value != 'Clôturée':
                            self.db.log_nc_change(
                                nc_id=nc_id,
                                user_name=user_name,
                                action='cloture',
                                field_changed='statut',
                                old_value=old_str,
                                new_value=new_str
                            )
                        else:
                            self.db.log_nc_change(
                                nc_id=nc_id,
                                user_name=user_name,
                                action='modification',
                                field_changed=field_label,
                                old_value=old_str,
                                new_value=new_str
                            )
                        changes_count += 1
                
                # Enregistrer aussi les modifications d'actions
                old_actions_imm = json.loads(old_nc.get('actions_immediates_table', '[]'))
                if json.dumps(old_actions_imm) != json.dumps(immediate_data):
                    self.db.log_nc_change(
                        nc_id=nc_id,
                        user_name=user_name,
                        action='modification',
                        field_changed='Actions immédiates',
                        old_value=f"{len(old_actions_imm)} action(s)",
                        new_value=f"{len(immediate_data)} action(s)"
                    )
                    changes_count += 1
                
                old_actions_corr = json.loads(old_nc.get('actions_correctives_table', '[]'))
                if json.dumps(old_actions_corr) != json.dumps(corrective_data):
                    self.db.log_nc_change(
                        nc_id=nc_id,
                        user_name=user_name,
                        action='modification',
                        field_changed='Actions correctives',
                        old_value=f"{len(old_actions_corr)} action(s)",
                        new_value=f"{len(corrective_data)} action(s)"
                    )
                    changes_count += 1
                
                success = self.db.update_nc(nc_id, data)
                if success:
                    # Fermer le formulaire D'ABORD
                    temp_ref = data['reference']
                    self._close_form()  # Ferme et reconstruit l'interface (show_form=False)
                    # Maintenant on peut rafraîchir en toute sécurité
                    self._refresh_nc_cache()  # Safe car show_form=False maintenant
                    self._refresh_actions_correctives()  # Rafraîchir le tableau de bord
                    # Invalider le cache des statistiques pour forcer la régénération
                    self._clear_chart_cache()
                    create_snackbar(self.page, f"[OK] NC {temp_ref} mise à jour ({changes_count} modification(s))", "success")
                else:
                    create_snackbar(self.page, "Erreur lors de la mise à jour", "error")
            else:
                # CRÉATION - Enregistrer l'événement de création
                nc_id = self.db.create_nc(data)
                if nc_id:
                    # Enregistrer la création dans l'historique
                    self.db.log_nc_change(
                        nc_id=nc_id,
                        user_name=user_name,
                        action='creation',
                        field_changed=None,
                        old_value=None,
                        new_value=f"NC {data['reference']} créée"
                    )
                    
                    # Fermer le formulaire D'ABORD
                    temp_ref = data['reference']
                    self._close_form()  # Ferme et reconstruit l'interface (show_form=False)
                    # Maintenant on peut rafraîchir en toute sécurité
                    self._refresh_nc_cache()  # Safe car show_form=False maintenant
                    self._refresh_actions_correctives()  # Rafraîchir le tableau de bord
                    # Invalider le cache des statistiques pour forcer la régénération
                    self._clear_chart_cache()
                    create_snackbar(self.page, f"[OK] NC {temp_ref} créée", "success")
                else:
                    create_snackbar(self.page, "Erreur lors de la création", "error")
        
        except Exception as ex:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Erreur sauvegarde: {error_detail}")
            # Ne mettre à jour form_error_text que si le formulaire est encore affiché
            if self.show_form and hasattr(self, 'form_error_text'):
                try:
                    if hasattr(self.form_error_text, 'page') and self.form_error_text.page:
                        self.form_error_text.value = f"[Erreur] Erreur: {str(ex)[:100]}"
                        self.form_error_text.update()
                except Exception:
                    pass
            # Afficher aussi dans snackbar si formulaire fermé
            if not self.show_form:
                create_snackbar(self.page, f"[Erreur] Erreur: {str(ex)[:100]}", "error")
    
    def _add_action(self):
        """Ajoute une action corrective."""
        pass
    
    def _close_dialog(self, dialog):
        """Ferme un dialogue."""
        dialog.open = False
        self.page.update()
    
    def _confirm_delete_nc(self, e):
        """Affiche une boîte de dialogue de confirmation avant suppression."""
        if not self.editing_nc:
            return
        
        nc_ref = self.editing_nc.get('reference', 'cette NC')
        
        def close_dlg(e):
            dlg.open = False
            self.page.update()
        
        def delete_confirmed(e):
            dlg.open = False
            self.page.update()
            self._delete_nc()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("[Attention] Confirmer la suppression", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                padding=10,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.Text(
                            f"Êtes-vous sûr de vouloir supprimer définitivement la NC {nc_ref} ?",
                            size=14,
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            "[Attention] Cette action est irréversible et supprimera :",
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ORANGE,
                            size=13,
                        ),
                        ft.Text("* Toutes les données de la NC", size=13),
                        ft.Text("* Les actions immédiates", size=13),
                        ft.Text("* Les actions correctives", size=13),
                        ft.Text("* Les analyses (5 Pourquoi, Ishikawa)", size=13),
                        ft.Text("* Les références aux pièces jointes", size=13),
                    ],
                ),
            ),
            actions=[
                ft.TextButton("Annuler", on_click=close_dlg),
                ft.TextButton(
                    "Supprimer définitivement",
                    on_click=delete_confirmed,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.RED_700,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()
    
    def _delete_nc(self):
        """Supprime la NC de la base de données et retourne au tableau de bord."""
        if not self.editing_nc:
            create_snackbar(self.page, "[Erreur] Aucune NC à supprimer", "error")
            return
        
        nc_id = self.editing_nc.get('id')
        nc_ref = self.editing_nc.get('reference', 'NC')
        
        try:
            # Enregistrer la suppression dans l'historique AVANT de supprimer
            user_name = self.user.get('username', 'Utilisateur')
            self.db.log_nc_change(
                nc_id=nc_id,
                user_name=user_name,
                action='suppression',
                field_changed=None,
                old_value=nc_ref,
                new_value=None
            )
            
            # Supprimer de la base de données
            success = self.db.delete_nc(nc_id)
            
            if success:
                # 1. Fermer le formulaire AVANT tout (pour éviter erreurs de bouton)
                self.show_form = False
                self.editing_nc = None
                self.form_tab_index = None
                
                # 2. Rafraîchir le cache (maintenant safe car show_form=False)
                self._refresh_nc_cache()
                
                # 3. Invalider tous les caches pour forcer le refresh
                self._tabs_cache.clear()  # Vider tous les caches
                self._clear_chart_cache()  # Invalider le cache des statistiques
                
                # 4. Retourner au tableau de bord (onglet 0)
                self.tabs.selected_index = 0
                self.current_tab = 0
                
                # 5. Reconstruire l'interface complète
                self.content = self._build_ui()
                
                # 6. Afficher la notification de succès
                if self.page:
                    create_snackbar(self.page, f"[OK] NC {nc_ref} supprimée avec succès", "success")
                    self.page.update()
            else:
                create_snackbar(self.page, f"[Erreur] Erreur lors de la suppression de la NC {nc_ref}", "error")
        
        except Exception as ex:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Erreur suppression NC: {error_detail}")
            if self.page:
                create_snackbar(self.page, f"[Erreur] Erreur: {str(ex)}", "error")
    
    def _toggle_nc_selection(self, nc_id: int, is_checked: bool):
        """Gère la sélection/désélection d'une NC."""
        if is_checked:
            self.selected_nc_ids.add(nc_id)
        else:
            self.selected_nc_ids.discard(nc_id)
        
        # Mettre à jour l'état du bouton de suppression multiple
        self._update_delete_multiple_button()
    
    def _update_delete_multiple_button(self):
        """Met à jour l'état du bouton de suppression multiple."""
        if hasattr(self, 'delete_multiple_btn'):
            try:
                # Vérifier que le bouton est attaché à la page avant de mettre à jour
                if hasattr(self.delete_multiple_btn, 'page') and self.delete_multiple_btn.page:
                    count = len(self.selected_nc_ids)
                    self.delete_multiple_btn.disabled = count == 0
                    if count > 0:
                        self.delete_multiple_btn.text = f"Supprimer sélection ({count})"
                    else:
                        self.delete_multiple_btn.text = "Supprimer sélection"
                    self.delete_multiple_btn.update()
            except Exception as ex:
                # Ignorer silencieusement si le bouton n'est pas dans la page
                pass

    
    def _confirm_delete_multiple(self, e):
        """Affiche une confirmation avant suppression multiple."""
        if not self.selected_nc_ids:
            return
        
        count = len(self.selected_nc_ids)
        
        def close_dlg(e):
            dlg.open = False
            self.page.update()
        
        def delete_confirmed(e):
            dlg.open = False
            self.page.update()
            self._delete_multiple_nc()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("[Attention] Confirmer la suppression multiple", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                padding=10,
                content=ft.Column(
                    tight=True,
                    controls=[
                        ft.Text(
                            f"Êtes-vous sûr de vouloir supprimer définitivement {count} NC ?",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(height=10),
                        ft.Text(
                            "[Attention] Cette action est irréversible et supprimera pour chaque NC :",
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ORANGE,
                            size=13,
                        ),
                        ft.Text("* Toutes les données de la NC", size=13),
                        ft.Text("* Les actions immédiates", size=13),
                        ft.Text("* Les actions correctives", size=13),
                        ft.Text("* Les analyses (5 Pourquoi, Ishikawa)", size=13),
                        ft.Text("* Les références aux pièces jointes", size=13),
                    ],
                ),
            ),
            actions=[
                ft.TextButton("Annuler", on_click=close_dlg),
                ft.TextButton(
                    f"Supprimer les {count} NC",
                    on_click=delete_confirmed,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.RED_700,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()
    
    def _delete_multiple_nc(self):
        """Supprime plusieurs NC de la base de données et rafraîchit le tableau."""
        if not self.selected_nc_ids:
            create_snackbar(self.page, "[Erreur] Aucune NC sélectionnée", "error")
            return
        
        deleted_count = 0
        failed_count = 0
        
        try:
            for nc_id in list(self.selected_nc_ids):
                try:
                    success = self.db.delete_nc(nc_id)
                    if success:
                        deleted_count += 1
                    else:
                        failed_count += 1
                except Exception as ex:
                    print(f"Erreur suppression NC {nc_id}: {ex}")
                    failed_count += 1
            
            # Vider la sélection
            self.selected_nc_ids.clear()
            
            # Rafraîchir le cache
            self._refresh_nc_cache()
            self._update_delete_multiple_button()
            
            # IMPORTANT: Invalider le cache de l'onglet Liste pour forcer la reconstruction
            if 1 in self._tabs_cache:
                del self._tabs_cache[1]
            
            # Reconstruire l'onglet Liste NC
            self.tab_content.content = self._build_list_tab()
            self._tabs_cache[1] = self.tab_content.content
            
            # Afficher le résultat
            if failed_count == 0:
                create_snackbar(
                    self.page,
                    f"[OK] {deleted_count} NC supprimée{'s' if deleted_count > 1 else ''} avec succès",
                    "success"
                )
            else:
                create_snackbar(
                    self.page,
                    f"[Attention] {deleted_count} NC supprimées, {failed_count} échecs",
                    "warning"
                )
            
            # Mettre à jour l'affichage
            self.page.update()
        
        except Exception as ex:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Erreur suppression multiple: {error_detail}")
            create_snackbar(self.page, f"[Erreur] Erreur: {str(ex)}", "error")
    
    def _handle_dropdown_change(self, e, dropdown_type: str):
        """Gère le changement de valeur d'un dropdown et détecte '[+] Ajouter...'."""
        if e.control.value == "[+] Ajouter...":
            # Ouvrir le dialog d'ajout
            self._show_add_item_dialog(dropdown_type, e.control)
        # Sinon, la valeur est sélectionnée normalement
    
    def _show_add_item_dialog(self, dropdown_type: str, dropdown_control):
        """Affiche un dialog pour ajouter un nouvel élément à un dropdown."""
        # Déterminer le label et la liste cible
        labels = {
            'type': ('Type de NC', self.type_nc_choices),
            'anomaly': ("Type d'anomalie", self.anomaly_choices),
            'imputation': ('Imputation', self.imputation_choices),
            'matieres': ('Matière réclamée', self.matieres_choices),
        }
        
        if dropdown_type not in labels:
            return
        
        label, target_list = labels[dropdown_type]
        
        # Champ de saisie
        new_item_field = ft.TextField(
            label=f"Nouveau {label.lower()}",
            autofocus=True,
            border_radius=8,
            filled=True,
            bgcolor=Theme.BG_TERTIARY,
        )
        
        def close_dlg(e):
            dlg.open = False
            dropdown_control.value = None  # Réinitialiser le dropdown
            dropdown_control.update()
            self.page.update()
        
        def add_item(e):
            new_value = new_item_field.value.strip()
            if not new_value:
                create_snackbar(self.page, "[Erreur] Veuillez saisir une valeur", "error")
                return
            
            if new_value in target_list:
                create_snackbar(self.page, f"[Info] '{new_value}' existe déjà", "info")
                dlg.open = False
                dropdown_control.value = new_value  # Sélectionner l'élément existant
                dropdown_control.update()
                self.page.update()
                return
            
            # Ajouter à la liste
            target_list.append(new_value)
            target_list.sort()  # Trier alphabétiquement
            
            # Mettre à jour le dropdown
            dropdown_control.options = []
            dropdown_control.options.append("[+] Ajouter...")
            dropdown_control.options.extend([opt for opt in target_list])
            dropdown_control.value = new_value
            
            dlg.open = False
            self.page.update()
            create_snackbar(self.page, f"[OK] '{new_value}' ajouté avec succès", "success")
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"[+] Ajouter {label}", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=400,
                padding=10,
                content=ft.Column(
                    tight=True,
                    controls=[
                        new_item_field,
                        ft.Container(height=10),
                        ft.Text(
                            f"L'élément sera ajouté à la liste '{label}' et sera disponible pour toutes les NC.",
                            size=12,
                            color=Theme.TEXT_MUTED,
                        ),
                    ],
                ),
            ),
            actions=[
                ft.TextButton("Annuler", on_click=close_dlg),
                ft.TextButton(
                    "Ajouter",
                    on_click=add_item,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=Theme.PRIMARY,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()
    
    # ========================================================================
    # TAB 4: SUIVI DES ACTIONS CORRECTIVES (CAPA COCKPIT)
    # ========================================================================
    
    def _build_suivi_actions_tab(self):
        """Construit le tableau de bord de suivi des actions correctives."""
        from datetime import datetime
        import json
        
        # Récupérer toutes les actions correctives de toutes les NC
        actions_data = self._get_all_actions_correctives()
        
        # Calculer les KPIs avancés
        total_actions = len(actions_data)
        actions_soldees = len([a for a in actions_data if a.get('statut') == 'Clôturée'])
        progress_value = (actions_soldees / total_actions) if total_actions > 0 else 0
        
        # Calcul actions en retard et urgentes
        now = datetime.now()
        actions_en_retard = 0
        actions_urgentes_7j = 0
        
        for action in actions_data:
            if action.get('statut') == 'Clôturée':
                continue
            date_ech = action.get('date_echeance', '') or action.get('date_fin', '')
            if date_ech:
                try:
                    try:
                        date_obj = datetime.strptime(date_ech, '%Y-%m-%d')
                    except:
                        date_obj = datetime.strptime(date_ech, '%d/%m/%Y')
                    
                    days_diff = (date_obj - now).days
                    if days_diff < 0:
                        actions_en_retard += 1
                    elif 0 <= days_diff <= 7:
                        actions_urgentes_7j += 1
                except:
                    pass
        
        # Initialiser les filtres si pas définis
        if not hasattr(self, 'filter_tout'):
            self.filter_tout = True
            self.filter_a_faire = False
            self.filter_en_cours = False
            self.filter_cloturee = False
            self.filter_annule = False
        
        # Initialiser l'état d'affichage des filtres (masqué par défaut)
        if not hasattr(self, '_actions_show_filters'):
            self._actions_show_filters = False
        
        # Filtres on/off pour les statuts + bouton export
        filter_controls = ft.Container(
            padding=10,
            border_radius=8,
            bgcolor=Theme.BG_SECONDARY,
            content=ft.Row(
                spacing=15,
                controls=[
                    ft.Text("[Stats] Statut :", size=14, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    ft.Switch(
                        label="TOUT",
                        value=self.filter_tout,
                        active_color=Theme.PRIMARY,
                        on_change=lambda e: self._toggle_filter('tout', e.control.value),
                    ),
                    ft.Switch(
                        label="À faire",
                        value=self.filter_a_faire,
                        active_color=ft.Colors.RED_400,
                        on_change=lambda e: self._toggle_filter('a_faire', e.control.value),
                    ),
                    ft.Switch(
                        label="En cours",
                        value=self.filter_en_cours,
                        active_color=ft.Colors.ORANGE_400,
                        on_change=lambda e: self._toggle_filter('en_cours', e.control.value),
                    ),
                    ft.Switch(
                        label="Clôturée",
                        value=self.filter_cloturee,
                        active_color=ft.Colors.GREEN_400,
                        on_change=lambda e: self._toggle_filter('cloturee', e.control.value),
                    ),
                    ft.Switch(
                        label="Annulé",
                        value=self.filter_annule,
                        active_color=ft.Colors.GREY_400,
                        on_change=lambda e: self._toggle_filter('annule', e.control.value),
                    ),
                    ft.Container(width=20),  # Espacement
                    ft.IconButton(
                        icon=ft.Icons.FILE_DOWNLOAD,
                        tooltip="Exporter vers Excel",
                        icon_color=Theme.PRIMARY,
                        on_click=lambda e: self._export_actions_excel(),
                    ),
                ]
            )
        )
        
        # Barre de progression globale avec KPIs détaillés
        progress_bar = ft.Container(
            padding=20,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=5,
                                controls=[
                                    ft.Text(
                                        f"[Stats] Avancement Global : {actions_soldees}/{total_actions} actions soldées",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=Theme.TEXT_PRIMARY,
                                    ),
                                    ft.Row(
                                        spacing=20,
                                        controls=[
                                            ft.Text(
                                                f"[Attention] En retard : {actions_en_retard}",
                                                size=13,
                                                color=ft.Colors.RED_400 if actions_en_retard > 0 else Theme.TEXT_SECONDARY,
                                                weight=ft.FontWeight.BOLD if actions_en_retard > 0 else None,
                                            ),
                                            ft.Text(
                                                f"[Alerte] Échéance < 7j : {actions_urgentes_7j}",
                                                size=13,
                                                color=ft.Colors.ORANGE_400 if actions_urgentes_7j > 0 else Theme.TEXT_SECONDARY,
                                                weight=ft.FontWeight.BOLD if actions_urgentes_7j > 0 else None,
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            ft.Text(
                                f"{int(progress_value * 100)}%",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.SUCCESS if progress_value >= 0.8 else Theme.WARNING if progress_value >= 0.5 else Theme.DANGER,
                            ),
                        ]
                    ),
                    ft.ProgressBar(
                        value=progress_value,
                        color=Theme.SUCCESS if progress_value >= 0.8 else Theme.WARNING if progress_value >= 0.5 else Theme.DANGER,
                        bgcolor=Theme.BG_TERTIARY,
                        height=10,
                    ),
                ]
            ),
            border=ft.Border(
                top=ft.BorderSide(1, Theme.PRIMARY),
                right=ft.BorderSide(1, Theme.PRIMARY),
                bottom=ft.BorderSide(1, Theme.PRIMARY),
                left=ft.BorderSide(1, Theme.PRIMARY),
            ),
            border_radius=10,
            bgcolor=Theme.BG_SECONDARY,
        )
        
        # Construction de la DataTable
        data_table = self._build_actions_datatable(actions_data)
        
        # Structure complète similaire à la liste NC
        table_container = ft.Container(
            content=data_table,
            border_radius=8,
            bgcolor=Theme.BG_SECONDARY,
            expand=True,
            padding=10,
        )
        
        # Stocker référence pour rebuild optimisé
        self._actions_table_container = table_container
        
        # Bouton pour afficher/masquer filtres et KPI
        toggle_filters_button = ft.Container(
            padding=ft.Padding(left=10, right=10, top=5, bottom=5),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.TextButton(
                        content=ft.Row(
                            spacing=5,
                            controls=[
                                ft.Icon(
                                    ft.Icons.VISIBILITY_OFF if self._actions_show_filters else ft.Icons.VISIBILITY,
                                    size=18,
                                    color=Theme.PRIMARY,
                                ),
                                ft.Text(
                                    "Masquer filtres" if self._actions_show_filters else "Afficher filtres",
                                    size=13,
                                    color=Theme.PRIMARY,
                                    weight=ft.FontWeight.W_500,
                                ),
                            ]
                        ),
                        on_click=lambda e: self._toggle_actions_filters_visibility(),
                    ),
                ]
            )
        )
        
        # Liste des contrôles à afficher
        controls = [toggle_filters_button]
        
        # Ajouter filtres et KPI seulement si visible
        if self._actions_show_filters:
            controls.extend([filter_controls, progress_bar])
        
        # Toujours afficher le tableau
        controls.append(table_container)
        
        return ft.Column(
            expand=True,
            spacing=15,
            controls=controls
        )
    
    def _get_all_actions_correctives(self):
        """Récupère toutes les actions correctives de toutes les NC."""
        import json
        from datetime import datetime, timedelta
        
        # Vérifier le cache (expiration 30 secondes)
        if self._actions_cache and self._actions_cache_time:
            elapsed = (datetime.now() - self._actions_cache_time).total_seconds()
            if elapsed < 30:
                print(f"[CACHE] Utilisation du cache actions ({elapsed:.1f}s)")
                return self._apply_actions_filters(self._actions_cache)
        
        print("[PERF] Rechargement actions depuis DB...")
        actions_list = []
        
        try:
            # Récupérer seulement les NC avec actions (optimisation SQL)
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, reference, categorie_nc, type_nc, actions_correctives_table
                    FROM nc_header
                    WHERE actions_correctives_table IS NOT NULL 
                      AND actions_correctives_table != '[]'
                      AND actions_correctives_table != 'null'
                      AND actions_correctives_table != ''
                    ORDER BY reference DESC
                """)
                all_nc = cursor.fetchall()
                
                for nc in all_nc:
                    nc_id = nc['id']
                    nc_ref = nc['reference']
                    nc_categorie = nc['categorie_nc']
                    nc_type = nc['type_nc']
                    actions_json = nc['actions_correctives_table']
                    
                    try:
                        actions = json.loads(actions_json)
                        if isinstance(actions, list) and len(actions) > 0:
                            for action in actions:
                                # Filtrer les actions vides (sans description)
                                if action.get('desc') and action['desc'].strip():
                                    action['nc_id'] = nc_id
                                    action['nc_ref'] = nc_ref
                                    action['nc_categorie'] = nc_categorie or 'Non définie'
                                    action['nc_type'] = nc_type
                                    actions_list.append(action)
                    except:
                        pass
        except Exception as ex:
            print(f"Erreur récupération actions: {ex}")
        
        # Mettre en cache
        self._actions_cache = actions_list
        self._actions_cache_time = datetime.now()
        print(f"[CACHE] {len(actions_list)} actions mises en cache")
        
        # Appliquer les filtres
        return self._apply_actions_filters(actions_list)
    
    def _apply_actions_filters(self, actions_list):
        """Applique tous les filtres actifs sur la liste d'actions."""
        from datetime import datetime
        
        filtered = actions_list.copy()
        
        # Filtre par statut
        if hasattr(self, 'filter_tout') and not self.filter_tout:
            filtered = [a for a in filtered if (
                (self.filter_a_faire and a.get('statut') == 'À faire') or
                (self.filter_en_cours and a.get('statut') == 'En cours') or
                (self.filter_cloturee and a.get('statut') == 'Clôturée') or
                (self.filter_annule and a.get('statut') == 'Annulé')
            )]
        
        # Filtre par catégorie
        if self._actions_filter_category != "Tout":
            filtered = [a for a in filtered if a.get('nc_categorie') == self._actions_filter_category]
        
        # Filtre par échéance
        if self._actions_filter_deadline != "Tout":
            now = datetime.now()
            deadline_filtered = []
            for a in filtered:
                date_ech = a.get('date_echeance', '') or a.get('date_fin', '')
                if not date_ech or a.get('statut') == 'Clôturée':
                    continue
                try:
                    try:
                        date_obj = datetime.strptime(date_ech, '%Y-%m-%d')
                    except:
                        date_obj = datetime.strptime(date_ech, '%d/%m/%Y')
                    
                    if self._actions_filter_deadline == "En retard" and date_obj < now:
                        deadline_filtered.append(a)
                    elif self._actions_filter_deadline == "< 7 jours" and 0 <= (date_obj - now).days <= 7:
                        deadline_filtered.append(a)
                    elif self._actions_filter_deadline == "< 30 jours" and 0 <= (date_obj - now).days <= 30:
                        deadline_filtered.append(a)
                except:
                    pass
            filtered = deadline_filtered
        
        # Recherche textuelle
        if self._actions_search and self._actions_search.strip():
            search_lower = self._actions_search.lower().strip()
            filtered = [a for a in filtered if (
                search_lower in str(a.get('nc_ref', '')).lower() or
                search_lower in str(a.get('desc', '')).lower() or
                search_lower in str(a.get('nc_categorie', '')).lower() or
                search_lower in str(a.get('responsable', '')).lower()
            )]
        
        # Tri
        reverse = (self._actions_sort_order == "desc")
        if self._actions_sort_field == "nc_ref":
            filtered.sort(key=lambda x: x.get('nc_ref', ''), reverse=reverse)
        elif self._actions_sort_field == "date_echeance":
            def get_date_key(a):
                date_str = a.get('date_echeance', '') or a.get('date_fin', '') or '9999-12-31'
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    try:
                        return datetime.strptime(date_str, '%d/%m/%Y')
                    except:
                        return datetime(9999, 12, 31)
            filtered.sort(key=get_date_key, reverse=reverse)
        elif self._actions_sort_field == "statut":
            filtered.sort(key=lambda x: x.get('statut', 'En cours'), reverse=reverse)
        elif self._actions_sort_field == "date_debut":
            filtered.sort(key=lambda x: x.get('date_debut', ''), reverse=reverse)
        
        print(f"[FILTRE] {len(filtered)} actions après filtres/tri")
        return filtered
    
    def _build_actions_datatable(self, actions_data):
        """Construit la DataTable des actions correctives avec pagination."""
        from datetime import datetime
        
        # Pagination: calculer index de début/fin
        total_actions = len(actions_data)
        total_pages = max(1, (total_actions + self._actions_per_page - 1) // self._actions_per_page)
        
        # S'assurer que la page actuelle est valide
        self._actions_page = max(1, min(self._actions_page, total_pages))
        
        start_idx = (self._actions_page - 1) * self._actions_per_page
        end_idx = min(start_idx + self._actions_per_page, total_actions)
        display_actions = actions_data[start_idx:end_idx]
        
        print(f"[PAGINATION] Page {self._actions_page}/{total_pages}, Affichage {start_idx+1}-{end_idx}/{total_actions}")
        
        # Détecter la largeur de l'écran pour mode responsive
        try:
            width_sources = []
            if self.page:
                if hasattr(self.page, 'window_width') and self.page.window_width:
                    width_sources.append(('window_width', self.page.window_width))
                if hasattr(self.page, 'width') and self.page.width:
                    width_sources.append(('width', self.page.width))
            
            screen_width = 1366 if not width_sources else width_sources[0][1]
            is_small_screen = screen_width < self._responsive_threshold
        except Exception as e:
            is_small_screen = False
        
        # Configuration des colonnes (nom, largeur, icône) - responsive
        columns_config = [
            ("No Réf. NC", 100, ft.Icons.TAG),
            ("Catégorie", 120, ft.Icons.CATEGORY),
            ("Action Corrective", None, ft.Icons.DESCRIPTION),  # expand avec min 200px
            ("Date Début", 100, ft.Icons.DATE_RANGE),
            ("Date Échéance", 120, ft.Icons.EVENT),
            # Masquer sur petits écrans
            ("Preuve Efficacité", 200, ft.Icons.VERIFIED) if not is_small_screen else None,
            ("Vérification", 200, ft.Icons.FACT_CHECK),
            # Masquer sur petits écrans
            ("Rappel", 100, ft.Icons.ALARM) if not is_small_screen else None,
            ("Statut", 160, ft.Icons.TRAFFIC),
            ("Date Clôture", 120, ft.Icons.CHECK_CIRCLE),
            ("Fichier", 80, ft.Icons.ATTACH_FILE),
        ]
        
        # Filtrer les colonnes None (masquées)
        columns_config = [col for col in columns_config if col is not None]
        
        # Créer colonnes pour l'en-tête
        columns = []
        for col_name, width, icon in columns_config:
            columns.append(
                ft.DataColumn(
                    label=ft.Row(
                        spacing=5,
                        controls=[
                            ft.Icon(icon, size=16, color=Theme.TEXT_PRIMARY),
                            ft.Text(col_name, color=Theme.TEXT_PRIMARY, weight=ft.FontWeight.BOLD, size=12)
                        ]
                    )
                )
            )
        
        # Lignes de données (seulement les actions de la page actuelle)
        data_rows = []
        for action in display_actions:
            # Déterminer si action en retard
            is_late = False
            date_echeance = action.get('date_echeance', '') or action.get('date_fin', '')
            if date_echeance and action.get('statut') != 'Clôturée':
                try:
                    # Essayer les deux formats
                    try:
                        date_echeance_obj = datetime.strptime(date_echeance, '%Y-%m-%d')
                    except:
                        date_echeance_obj = datetime.strptime(date_echeance, '%d/%m/%Y')
                    if datetime.now() > date_echeance_obj:
                        is_late = True
                except:
                    pass
            
            # Badge catégorie
            cat_color = self._get_category_color(action.get('nc_categorie', ''))
            category_badge = ft.Container(
                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                border_radius=5,
                bgcolor=cat_color,
                content=ft.Text(
                    action.get('nc_categorie', 'N/A')[:20],
                    size=11,
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                ),
            )
            
            # Description avec tooltip
            desc_text = action.get('desc', 'Sans description')
            desc_display = desc_text[:50] + ('...' if len(desc_text) > 50 else '')
            
            # Badge statut avec couleur
            statut = action.get('statut', 'En cours')
            statut_colors = {
                'En cours': ft.Colors.ORANGE_400,
                'Clôturée': ft.Colors.GREEN_400,
                'À faire': ft.Colors.RED_400,
                'Annulé': ft.Colors.GREY_400,
            }
            statut_badge = ft.Container(
                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                border_radius=5,
                bgcolor=statut_colors.get(statut, ft.Colors.BLUE_400),
                content=ft.Text(
                    statut,
                    size=11,
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                ),
            )
            
            # Indicateur de rappel
            rappel_info = ""
            rappel_color = Theme.TEXT_MUTED
            if action.get('type_rappel') == 'Unique':
                rappel_info = f"[Date] {action.get('date_rappel_unique', 'N/A')}"
                if is_late:
                    rappel_color = ft.Colors.RED
            elif action.get('type_rappel') == 'Récurrent':
                rappel_info = f"[Actualiser] {action.get('frequence_rappel', 'N/A')}"
            
            # Créer les cellules de la ligne
            row_cells = []
            for i, (col_name, width, icon) in enumerate(columns_config):
                is_last = i == len(columns_config) - 1
                
                # Déterminer le contenu de la cellule
                if col_name == "No Réf. NC":
                    cell_content = ft.TextButton(
                        text=action.get('nc_ref', 'N/A'),
                        on_click=lambda e, nc_id=action.get('nc_id'): self._go_to_nc_actions_tab(nc_id),
                    )
                elif col_name == "Catégorie":
                    cell_content = category_badge
                elif col_name == "Action Corrective":
                    cell_content = ft.Text(
                        desc_display, 
                        size=12, 
                        color=Theme.TEXT_SECONDARY,
                        tooltip=desc_text if len(desc_text) > 50 else None,
                        no_wrap=False,  # Permettre retour à la ligne
                    )
                elif col_name == "Date Début":
                    cell_content = ft.Text(
                        action.get('date_debut', 'N/A'),
                        size=12,
                        color=Theme.TEXT_SECONDARY,
                    )
                elif col_name == "Date Échéance":
                    date_ech = action.get('date_echeance', '') or action.get('date_fin', '')
                    cell_content = ft.Text(
                        date_ech if date_ech else 'N/A',
                        size=12,
                        color=ft.Colors.RED if is_late else Theme.TEXT_SECONDARY,
                        weight=ft.FontWeight.BOLD if is_late else None,
                    )
                elif col_name == "Preuve Efficacité":
                    preuve_text = action.get('preuve_efficacite', 'N/A')
                    preuve_display = preuve_text[:60] + ('...' if len(preuve_text) > 60 else '')
                    cell_content = ft.Text(
                        preuve_display, 
                        size=12, 
                        color=Theme.TEXT_SECONDARY, 
                        tooltip=preuve_text,
                        no_wrap=False,  # Permettre retour à la ligne
                    )
                elif col_name == "Vérification":
                    verif_value = action.get('verification', 'Non évaluée')
                    verif_colors_bg = {
                        'Efficace': ft.Colors.GREEN_100,
                        'Non efficace': ft.Colors.RED_100,
                        'Partiellement efficace': ft.Colors.ORANGE_100,
                        'Non évaluée': ft.Colors.GREY_200,
                    }
                    verif_colors_text = {
                        'Efficace': ft.Colors.GREEN_900,
                        'Non efficace': ft.Colors.RED_900,
                        'Partiellement efficace': ft.Colors.ORANGE_900,
                        'Non évaluée': ft.Colors.GREY_900,
                    }
                    cell_content = ft.Dropdown(
                        value=verif_value,
                        options=[
                            DropdownOption("Non évaluée"),
                            DropdownOption("Efficace"),
                            DropdownOption("Non efficace"),
                            DropdownOption("Partiellement efficace"),
                        ],
                        text_size=11,
                        dense=True,
                        width=185,
                        color=verif_colors_text.get(verif_value, ft.Colors.GREY_900),
                        filled=True,
                        fill_color=verif_colors_bg.get(verif_value, ft.Colors.GREY_200),
                        border_color=ft.Colors.TRANSPARENT,
                        border_radius=5,
                        on_change=lambda e, nc_id=action.get('nc_id'), act_desc=action.get('desc'): self._update_action_verification(nc_id, act_desc, e.control.value),
                    )
                elif col_name == "Rappel":
                    cell_content = ft.Text(rappel_info, size=11, color=rappel_color)
                elif col_name == "Statut":
                    statut_bg_colors = {
                        'En cours': ft.Colors.ORANGE_100,
                        'Clôturée': ft.Colors.GREEN_100,
                        'À faire': ft.Colors.RED_100,
                        'Annulé': ft.Colors.GREY_300,
                    }
                    statut_text_colors = {
                        'En cours': ft.Colors.ORANGE_900,
                        'Clôturée': ft.Colors.GREEN_900,
                        'À faire': ft.Colors.RED_900,
                        'Annulé': ft.Colors.GREY_900,
                    }
                    cell_content = ft.Dropdown(
                        value=statut,
                        options=[
                            DropdownOption("À faire"),
                            DropdownOption("En cours"),
                            DropdownOption("Clôturée"),
                            DropdownOption("Annulé"),
                        ],
                        text_size=11,
                        dense=True,
                        width=145,
                        color=statut_text_colors.get(statut, ft.Colors.BLUE_900),
                        filled=True,
                        fill_color=statut_bg_colors.get(statut, ft.Colors.BLUE_100),
                        border_color=ft.Colors.TRANSPARENT,
                        border_radius=5,
                        on_change=lambda e, nc_id=action.get('nc_id'), act_desc=action.get('desc'): self._update_action_status(nc_id, act_desc, e.control.value),
                    )
                elif col_name == "Date Clôture":
                    date_cloture = action.get('date_cloture_action', 'N/A')
                    cell_content = ft.Text(
                        date_cloture if date_cloture and date_cloture != 'N/A' else '-',
                        size=12,
                        color=Theme.SUCCESS if date_cloture and date_cloture != 'N/A' else Theme.TEXT_MUTED,
                        weight=ft.FontWeight.BOLD if date_cloture and date_cloture != 'N/A' else None,
                    )
                else:  # Fichier
                    fichiers = action.get('fichiers', [])
                    # Compatibilité avec ancien format (fichier_nom/fichier_path)
                    if not fichiers and action.get('fichier_nom'):
                        fichiers = [{'nom': action.get('fichier_nom', ''), 'path': action.get('fichier_path', '')}]
                    
                    has_files = len(fichiers) > 0 and any(f.get('nom') for f in fichiers)
                    
                    if not has_files:
                        # Aucun fichier
                        cell_content = ft.IconButton(
                            icon=ft.Icons.ATTACH_FILE_OUTLINED,
                            icon_color=ft.Colors.GREY_400,
                            tooltip='Aucun fichier',
                            disabled=True,
                        )
                    elif len(fichiers) == 1:
                        # Un seul fichier - clic direct
                        fichier = fichiers[0]
                        cell_content = ft.IconButton(
                            icon=ft.Icons.ATTACH_FILE,
                            icon_color=Theme.PRIMARY,
                            tooltip=fichier.get('nom', 'Fichier'),
                            on_click=lambda e, path=fichier.get('path'), nom=fichier.get('nom'): self._open_action_file(path, nom),
                        )
                    else:
                        # Plusieurs fichiers - menu popup
                        cell_content = ft.PopupMenuButton(
                            icon=ft.Icons.ATTACH_FILE,
                            icon_color=Theme.PRIMARY,
                            tooltip=f"{len(fichiers)} fichiers",
                            items=[
                                ft.PopupMenuItem(
                                    text=f.get('nom', 'Fichier sans nom'),
                                    on_click=lambda e, path=f.get('path'), nom=f.get('nom'): self._open_action_file(path, nom)
                                )
                                for f in fichiers if f.get('nom')
                            ]
                        )
                
                # Créer le conteneur de cellule
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
                    # Pour colonnes expand (None) : conteneur interne avec largeur minimale 200px
                    row_cells.append(
                        ft.Container(
                            expand=True,
                            padding=ft.Padding(left=6, right=6, top=10, bottom=10),
                            border=ft.Border(right=ft.BorderSide(1, Theme.BG_TERTIARY)) if not is_last else None,
                            content=ft.Container(
                                width=200,
                                content=cell_content,
                            ),
                        )
                    )
            
            # Créer le conteneur de ligne avec bordure rouge si en retard
            row_container = ft.Container(
                border=ft.Border(
                top=ft.BorderSide(2, ft.Colors.RED),
                right=ft.BorderSide(2, ft.Colors.RED),
                bottom=ft.BorderSide(2, ft.Colors.RED),
                left=ft.BorderSide(2, ft.Colors.RED),
            ) if is_late else ft.Border(bottom=ft.BorderSide(1, Theme.BG_TERTIARY)),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.RED) if is_late else None,
                content=ft.Row(controls=row_cells, spacing=0),
            )
            
            data_rows.append(row_container)
        
        # Créer le tableau scrollable avec colonne
        table_column = ft.Column(
            controls=data_rows,
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        
        # Créer l'en-tête aligné avec les colonnes (CLIQUABLE pour tri)
        header_cells = []
        sortable_columns = {
            "No Réf. NC": "nc_ref",
            "Date Début": "date_debut",
            "Date Échéance": "date_echeance",
            "Statut": "statut",
        }
        
        for i, (col_name, width, icon) in enumerate(columns_config):
            is_last = i == len(columns_config) - 1
            is_sortable = col_name in sortable_columns
            
            # Indicateur de tri
            sort_icon = ""
            if is_sortable and self._actions_sort_field == sortable_columns[col_name]:
                sort_icon = " v" if self._actions_sort_order == "desc" else " ^"
            
            header_content = ft.Row(
                spacing=5,
                controls=[
                    ft.Icon(icon, size=16, color=Theme.TEXT_PRIMARY),
                    ft.Text(
                        col_name + sort_icon, 
                        color=Theme.PRIMARY if is_sortable and self._actions_sort_field == sortable_columns.get(col_name) else Theme.TEXT_PRIMARY, 
                        weight=ft.FontWeight.BOLD, 
                        size=12
                    )
                ]
            )
            
            if width is not None:
                header_cell = ft.Container(
                    width=width,
                    padding=ft.Padding(left=8, right=8, top=14, bottom=14),
                    border=ft.Border(right=ft.BorderSide(1, Theme.BG_PRIMARY)) if not is_last else None,
                    content=header_content,
                )
                
                # Rendre cliquable si triable
                if is_sortable:
                    header_cell = ft.GestureDetector(
                        content=header_cell,
                        on_tap=lambda e, field=sortable_columns[col_name]: self._on_actions_sort(field),
                        mouse_cursor=ft.MouseCursor.CLICK,
                    )
                
                header_cells.append(header_cell)
            else:
                # Pour colonnes expand (None) : conteneur interne avec largeur minimale 200px
                header_cell = ft.Container(
                    expand=True,
                    padding=ft.Padding(left=8, right=8, top=14, bottom=14),
                    border=ft.Border(right=ft.BorderSide(1, Theme.BG_PRIMARY)) if not is_last else None,
                    content=ft.Container(
                        width=200,
                        content=header_content,
                    ),
                )
                
                # Rendre cliquable si triable
                if is_sortable:
                    header_cell = ft.GestureDetector(
                        content=header_cell,
                        on_tap=lambda e, field=sortable_columns[col_name]: self._on_actions_sort(field),
                        mouse_cursor=ft.MouseCursor.CLICK,
                    )
                
                header_cells.append(header_cell)
        
        header_row = ft.Container(
            bgcolor=Theme.BG_TERTIARY,
            border_radius=ft.BorderRadius(8, 8, 0, 0),
            content=ft.Row(controls=header_cells, spacing=0),
        )
        
        # Contrôles de pagination
        pagination_controls = ft.Container(
            padding=15,
            bgcolor=Theme.BG_SECONDARY,
            border_radius=ft.BorderRadius(0, 0, 8, 8),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.CHEVRON_LEFT,
                        icon_color=Theme.TEXT_PRIMARY if self._actions_page > 1 else Theme.TEXT_MUTED,
                        disabled=self._actions_page <= 1,
                        on_click=lambda e: self._actions_change_page(-1),
                        tooltip="Page précédente",
                    ),
                    ft.Text(
                        f"Page {self._actions_page} / {total_pages}  *  {start_idx+1}-{end_idx} sur {total_actions} actions",
                        size=13,
                        color=Theme.TEXT_SECONDARY,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CHEVRON_RIGHT,
                        icon_color=Theme.TEXT_PRIMARY if self._actions_page < total_pages else Theme.TEXT_MUTED,
                        disabled=self._actions_page >= total_pages,
                        on_click=lambda e: self._actions_change_page(1),
                        tooltip="Page suivante",
                    ),
                ]
            )
        )
        
        # Retourner la structure complète avec pagination
        data_table = ft.Column(
            controls=[header_row, table_column, pagination_controls],
            spacing=0,
            expand=True,
        )
        
        return data_table
    
    def _actions_change_page(self, delta):
        """Change de page dans le tableau des actions."""
        self._actions_page += delta
        # Reconstruire seulement le tableau
        self._rebuild_actions_table()
    
    def _on_actions_search(self, search_value):
        """Gère la recherche textuelle avec debouncing."""
        self._actions_search = search_value
        self._actions_page = 1  # Retour page 1
        
        # Debouncing : attendre 500ms avant de déclencher la recherche
        if hasattr(self, '_actions_search_timer') and self._actions_search_timer:
            self._actions_search_timer.cancel()
        
        import threading
        self._actions_search_timer = threading.Timer(0.5, self._rebuild_actions_table)
        self._actions_search_timer.start()
    
    def _on_actions_filter_change(self, filter_type, value):
        """Gère les changements de filtres additionnels."""
        if filter_type == 'category':
            self._actions_filter_category = value
        elif filter_type == 'deadline':
            self._actions_filter_deadline = value
        
        self._actions_page = 1  # Retour page 1
        self._rebuild_actions_table()
    
    def _on_actions_sort(self, field):
        """Gère le tri par colonne cliquable."""
        # Basculer l'ordre si même colonne, sinon DESC par défaut
        if self._actions_sort_field == field:
            self._actions_sort_order = "asc" if self._actions_sort_order == "desc" else "desc"
        else:
            self._actions_sort_field = field
            self._actions_sort_order = "desc"
        
        self._actions_page = 1  # Retour page 1
        self._rebuild_actions_table()
    
    def _export_actions_excel(self):
        """Exporte les actions filtrées vers Excel."""
        try:
            from datetime import datetime
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
            
            actions_data = self._get_all_actions_correctives()
            
            if not actions_data:
                create_snackbar(self.page, "[Attention] Aucune action à exporter", "warning")
                return
            
            def on_file_result(e: ft.FilePickerResultEvent):
                if e.path:
                    try:
                        filepath = e.path
                        if not filepath.endswith('.xlsx'):
                            filepath += '.xlsx'
                        
                        # Créer le workbook
                        wb = openpyxl.Workbook()
                        ws = wb.active
                        ws.title = "Actions Correctives"
                        
                        # Style d'en-tête
                        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                        header_font = Font(bold=True, color="FFFFFF")
                        
                        # En-têtes
                        headers = [
                            'No Réf. NC', 'Catégorie NC', 'Type NC', 'Action Corrective',
                            'Responsable', 'Date Début', 'Date Échéance', 'Statut',
                            'Vérification', 'Preuve Efficacité', 'Date Clôture', 
                            'Type Rappel', 'Fichier'
                        ]
                        
                        for col_num, header in enumerate(headers, 1):
                            cell = ws.cell(row=1, column=col_num, value=header)
                            cell.fill = header_fill
                            cell.font = header_font
                            cell.alignment = Alignment(horizontal='center', vertical='center')
                        
                        # Données
                        for row_num, action in enumerate(actions_data, 2):
                            ws.cell(row=row_num, column=1, value=action.get('nc_ref', ''))
                            ws.cell(row=row_num, column=2, value=action.get('nc_categorie', ''))
                            ws.cell(row=row_num, column=3, value=action.get('nc_type', ''))
                            ws.cell(row=row_num, column=4, value=action.get('desc', ''))
                            ws.cell(row=row_num, column=5, value=action.get('responsable', ''))
                            ws.cell(row=row_num, column=6, value=action.get('date_debut', ''))
                            ws.cell(row=row_num, column=7, value=action.get('date_echeance', '') or action.get('date_fin', ''))
                            ws.cell(row=row_num, column=8, value=action.get('statut', ''))
                            ws.cell(row=row_num, column=9, value=action.get('verification', ''))
                            ws.cell(row=row_num, column=10, value=action.get('preuve_efficacite', ''))
                            ws.cell(row=row_num, column=11, value=action.get('date_cloture_action', ''))
                            ws.cell(row=row_num, column=12, value=action.get('type_rappel', ''))
                            ws.cell(row=row_num, column=13, value=action.get('fichier_nom', ''))
                        
                        # Ajuster largeur colonnes
                        ws.column_dimensions['A'].width = 12
                        ws.column_dimensions['B'].width = 15
                        ws.column_dimensions['C'].width = 12
                        ws.column_dimensions['D'].width = 50
                        ws.column_dimensions['E'].width = 20
                        
                        wb.save(filepath)
                        create_snackbar(self.page, f"[OK] Fichier exporté : {filepath.split('/')[-1]} ({len(actions_data)} actions)", "success")
                    except Exception as ex:
                        print(f"Erreur export Excel: {ex}")
                        create_snackbar(self.page, f"[Erreur] Erreur : {str(ex)}", "error")
            
            # Créer le FilePicker
            file_picker = ft.FilePicker(on_result=on_file_result)
            self.page.overlay.append(file_picker)
            self.page.update()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_picker.save_file(
                dialog_title="Exporter les actions correctives",
                file_name=f"export_actions_{timestamp}.xlsx",
                allowed_extensions=["xlsx"]
            )
            
        except ImportError:
            create_snackbar(self.page, "[Attention] Bibliothèque openpyxl non disponible", "warning")
        except Exception as ex:
            print(f"Erreur export: {ex}")
            create_snackbar(self.page, f"[Erreur] Erreur : {str(ex)}", "error")
    
    def _rebuild_actions_table(self):
        """Reconstruit uniquement le tableau des actions (optimisation)."""
        try:
            actions_data = self._get_all_actions_correctives()
            new_table = self._build_actions_datatable(actions_data)
            
            # Remplacer le conteneur du tableau
            if self._actions_table_container:
                self._actions_table_container.content = new_table
                self._actions_table_container.update()
            else:
                # Fallback : reconstruction complète
                self.tab_content.content = self._build_suivi_actions_tab()
                self.page.update()
        except Exception as ex:
            print(f"[ERROR] Erreur reconstruction tableau: {ex}")
    
    def _get_category_color(self, category):
        """Retourne la couleur selon la catégorie."""
        category_colors = {
            'Qualité': ft.Colors.BLUE_600,
            'Sécurité': ft.Colors.RED_600,
            'Environnement': ft.Colors.GREEN_600,
            'Hygiène': ft.Colors.PURPLE_600,
            'Réglementaire': ft.Colors.ORANGE_600,
        }
        return category_colors.get(category, ft.Colors.GREY_600)
    
    def _toggle_actions_filters_visibility(self):
        """Bascule l'affichage des filtres et KPI dans l'onglet Suivi Actions."""
        self._actions_show_filters = not self._actions_show_filters
        # Reconstruire l'onglet complet
        self.tab_content.content = self._build_suivi_actions_tab()
        self.page.update()
    
    def _toggle_filter(self, filter_name: str, value: bool):
        """Active/désactive un filtre de statut (optimisé)."""
        if filter_name == 'tout':
            self.filter_tout = value
            # Si TOUT est activé, désactiver les autres
            if value:
                self.filter_a_faire = False
                self.filter_en_cours = False
                self.filter_cloturee = False
                self.filter_annule = False
        elif filter_name == 'a_faire':
            self.filter_a_faire = value
            if value:
                self.filter_tout = False
        elif filter_name == 'en_cours':
            self.filter_en_cours = value
            if value:
                self.filter_tout = False
        elif filter_name == 'cloturee':
            self.filter_cloturee = value
            if value:
                self.filter_tout = False
        elif filter_name == 'annule':
            self.filter_annule = value
            if value:
                self.filter_tout = False
        
        # Si aucun filtre spécifique n'est activé, réactiver TOUT
        if not any([self.filter_a_faire, self.filter_en_cours, self.filter_cloturee, self.filter_annule]):
            self.filter_tout = True
        
        # Réinitialiser la page à 1 lors du changement de filtre
        self._actions_page = 1
        
        # Reconstruire SEULEMENT le tableau (pas les KPI/filtres)
        self._rebuild_actions_table()
    
    def _go_to_nc_detail(self, nc_id):
        """Navigate vers le détail d'une NC."""
        # Charger la NC et aller sur l'onglet détail
        self.current_nc_id = nc_id
        self.tabs.selected_index = 1
        self.current_tab = 1
        self.tab_content.content = self._build_detail_tab()
        self.page.update()
    
    def _go_to_nc_actions_tab(self, nc_id):
        """Navigate vers l'onglet Actions Correctives d'une NC."""
        # Charger la NC et ouvrir le formulaire sur l'onglet Actions (tab 2)
        nc_data = self.db.get_nc(nc_id)
        if nc_data:
            # Forcer l'onglet Actions AVANT d'ouvrir le formulaire
            self.form_tab_index = 2
            self._open_form(nc_data)
    
    def _update_action_verification(self, nc_id, action_desc, new_verification):
        """Met à jour la vérification d'une action corrective."""
        import json
        try:
            nc_data = self.db.get_nc(nc_id)
            if nc_data and nc_data.get('actions_correctives_table'):
                actions = json.loads(nc_data['actions_correctives_table'])
                # Trouver l'action correspondante
                for action in actions:
                    if action.get('desc') == action_desc:
                        action['verification'] = new_verification
                        break
                
                # Sauvegarder
                self.db.update_nc(nc_id, {'actions_correctives_table': json.dumps(actions)})
                
                # Invalider le cache
                self._actions_cache = None
                self._actions_cache_time = None
                
                # Recharger le tableau pour mettre à jour les couleurs
                self._rebuild_actions_table()
                
                # Rafraîchir le tableau de bord instantanément
                self._refresh_actions_correctives()
                
                create_snackbar(self.page, "[OK] Vérification mise à jour", "success")
        except Exception as ex:
            print(f"Erreur mise à jour vérification: {ex}")
            create_snackbar(self.page, f"[Erreur] Erreur: {ex}", "error")
    
    def _update_action_status(self, nc_id, action_desc, new_status):
        """Met à jour le statut d'une action corrective."""
        import json
        try:
            nc_data = self.db.get_nc(nc_id)
            if nc_data and nc_data.get('actions_correctives_table'):
                actions = json.loads(nc_data['actions_correctives_table'])
                # Trouver l'action correspondante
                for action in actions:
                    if action.get('desc') == action_desc:
                        action['statut'] = new_status
                        # Auto-désactiver rappel si clôturée
                        if new_status == 'Clôturée':
                            action['rappel_actif'] = False
                        break
                
                # Sauvegarder
                self.db.update_nc(nc_id, {'actions_correctives_table': json.dumps(actions)})
                
                # Invalider le cache
                self._actions_cache = None
                self._actions_cache_time = None
                
                # Recharger le tableau pour mettre à jour les couleurs
                self._rebuild_actions_table()
                
                # Rafraîchir le tableau de bord instantanément
                self._refresh_actions_correctives()
                
                create_snackbar(self.page, "[OK] Statut mis à jour", "success")
        except Exception as ex:
            print(f"Erreur mise à jour statut: {ex}")
            create_snackbar(self.page, f"[Erreur] Erreur: {ex}", "error")
    
    def _open_action_file(self, file_path, file_name):
        """Ouvre le fichier attaché à l'action."""
        import os
        import subprocess
        try:
            if os.path.exists(file_path):
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                else:  # Linux/Mac
                    subprocess.run(['xdg-open', file_path])
                self.page.snack_bar = ft.SnackBar(content=ft.Text(f"[Fichier] Ouverture de {file_name}"), bgcolor=Theme.INFO)
                self.page.snack_bar.open = True
                self.page.update()
            else:
                self.page.snack_bar = ft.SnackBar(content=ft.Text("[Erreur] Fichier introuvable"), bgcolor=Theme.DANGER)
                self.page.snack_bar.open = True
                self.page.update()
        except Exception as ex:
            print(f"Erreur ouverture fichier: {ex}")
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f"[Erreur] Erreur: {ex}"), bgcolor=Theme.DANGER)
            self.page.snack_bar.open = True
            self.page.update()

    # ========================================================================
    # TAB 5: TABLEAU DE BORD KPI - PILOTAGE OPÉRATIONNEL
    # ========================================================================
    
    def _build_dashboard_tab(self):
        """Construit le tableau de bord orienté pilotage opérationnel temps réel."""
        try:
            from datetime import datetime, timedelta
            import json
            
            # Récupérer toutes les NC et actions
            all_ncs = self.db.get_all_nc()
            today = datetime.now().date()
            current_month = datetime.now().strftime('%Y-%m')
            
                # === 1. CALCUL KPI ALERTES & SANTÉ ===
        
            # KPI 1: Actions en Souffrance (Retard)
            actions_en_retard = 0
            for nc in all_ncs:
                actions_json = nc.get('actions_correctives_table', '[]')
                try:
                    actions = json.loads(actions_json) if actions_json else []
                    for action in actions:
                        # Utiliser date_echeance ou date_fin pour compatibilité
                        date_echeance = action.get('date_echeance') or action.get('date_fin')
                        if date_echeance and action.get('statut') != 'Clôturée':
                            try:
                                # Essayer les deux formats
                                try:
                                    deadline = datetime.strptime(date_echeance, '%Y-%m-%d').date()
                                except:
                                    deadline = datetime.strptime(date_echeance, '%d/%m/%Y').date()
                                if deadline < today:
                                    actions_en_retard += 1
                            except:
                                pass
                except:
                    pass
        
            # KPI 2: NC Critiques Ouvertes
            nc_critiques_ouvertes = len([
                nc for nc in all_ncs 
                if nc.get('gravite') == 'Critique' and nc.get('statut') == 'En cours'
            ])
        
            # KPI 3: Coût Non-Qualité Mois en Cours
            cout_cnq_mois = 0.0
            for nc in all_ncs:
                if nc.get('date_detection', '').startswith(current_month):
                    cout_cnq_mois += float(nc.get('cout_analyse', 0) or 0)
                    cout_cnq_mois += float(nc.get('cout_controle_supp', 0) or 0)
                    cout_cnq_mois += float(nc.get('cout_rebut', 0) or 0)
                    cout_cnq_mois += float(nc.get('cout_retouche', 0) or 0)
                    cout_cnq_mois += float(nc.get('cout_immobilisation', 0) or 0)
                    cout_cnq_mois += float(nc.get('cout_retour_client', 0) or 0)
                    cout_cnq_mois += float(nc.get('cout_avoir', 0) or 0)
                    cout_cnq_mois += float(nc.get('cout_geste_commercial', 0) or 0)
        
            # KPI 4: Taux d'Efficacité (Rolling 30 jours)
            date_30j = (today - timedelta(days=30)).strftime('%Y-%m-%d')
            actions_verifiees = 0
            actions_efficaces = 0
            for nc in all_ncs:
                if nc.get('date_detection', '') >= date_30j:
                    actions_json = nc.get('actions_correctives_table', '[]')
                    try:
                        actions = json.loads(actions_json) if actions_json else []
                        for action in actions:
                            verif = action.get('verif', '')
                            if verif in ['Efficace', 'Non efficace']:
                                actions_verifiees += 1
                                if verif == 'Efficace':
                                    actions_efficaces += 1
                    except:
                        pass
        
            taux_efficacite = (actions_efficaces / actions_verifiees * 100) if actions_verifiees > 0 else 0
        
            # === 1. BANDEAU KPI ALERTES (Top Row) ===
            kpi_alertes = ft.Row(
                spacing=15,
                wrap=True,
                controls=[
                    self._create_alert_kpi(
                        "[Retard] Actions en Retard",
                        str(actions_en_retard),
                        ft.Colors.RED_600 if actions_en_retard > 0 else ft.Colors.GREEN_600,
                        ft.Icons.ALARM,
                        actions_en_retard > 0
                    ),
                    self._create_alert_kpi(
                        "[Attention] NC Critiques Ouvertes",
                        str(nc_critiques_ouvertes),
                        ft.Colors.RED_700 if nc_critiques_ouvertes > 0 else ft.Colors.GREEN_600,
                        ft.Icons.GPP_BAD,
                        nc_critiques_ouvertes > 0
                    ),
                    self._create_alert_kpi(
                        "[Cout] CNQ Mois Actuel",
                        f"{cout_cnq_mois:,.2f} EUR",
                        ft.Colors.BLUE_700,
                        ft.Icons.EURO_SYMBOL,
                        False
                    ),
                    self._create_gauge_kpi(
                        "[OK] Taux d'Efficacité (30j)",
                        taux_efficacite,
                        ft.Icons.TRENDING_UP
                    ),
                ],
            )
        
            # === 2. MATRICE DE RISQUE ===
            matrice_risque = self._build_risk_matrix(all_ncs)
        
            # === 3. TOP 5 URGENCES (NC les plus anciennes non clôturées) ===
            top_urgences = self._build_top_urgences(all_ncs, today)
        
            # === 4. SUIVI OPÉRATIONNEL DES ACTIONS CORRECTIVES ===
            suivi_actions_content = self._build_actions_correctives_suivi(all_ncs)
        
            # Conteneur pour actualisation partielle
            self._actions_correctives_container = ft.Container(
                content=suivi_actions_content,
            )
        
            return ft.Column(
                expand=True,
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    kpi_alertes,
                    matrice_risque,
                    top_urgences,
                    self._actions_correctives_container,
                ],
            )

        except Exception as e:
            print(f"[NCPage._build_dashboard_tab] [Erreur] ERREUR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Text("[Erreur] Erreur lors du chargement du tableau de bord", size=20, weight=ft.FontWeight.BOLD, color="red"),
                        ft.Text(f"{type(e).__name__}: {str(e)}", size=14),
                    ]
                )
            )

    def _create_alert_kpi(self, title: str, value: str, color, icon, is_alert: bool):
        """Crée une carte KPI avec alerte."""
        return ft.Container(
            width=280,
            padding=20,
            bgcolor=Theme.BG_SECONDARY,
            border_radius=12,
            border=ft.Border(
                top=ft.BorderSide(3 if is_alert else 2, color),
                right=ft.BorderSide(3 if is_alert else 2, color),
                bottom=ft.BorderSide(3 if is_alert else 2, color),
                left=ft.BorderSide(3 if is_alert else 2, color),
            ),
            shadow=ft.BoxShadow(
                spread_radius=2 if is_alert else 1,
                blur_radius=15 if is_alert else 8,
                color=ft.Colors.with_opacity(0.3 if is_alert else 0.15, color),
                offset=ft.Offset(0, 4 if is_alert else 2),
            ),
            content=ft.Column(
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icon, size=48, color=color),
                    ft.Text(
                        title,
                        size=14,
                        color=Theme.TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Text(
                        value,
                        size=36,
                        weight=ft.FontWeight.BOLD,
                        color=color,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )
    
    def _create_gauge_kpi(self, title: str, percentage: float, icon):
        """Crée une carte KPI avec jauge circulaire."""
        color = ft.Colors.GREEN_600 if percentage >= 80 else ft.Colors.ORANGE_600
    
        return ft.Container(
            width=280,
            padding=20,
            bgcolor=Theme.BG_SECONDARY,
            border_radius=12,
            border=ft.Border(
                top=ft.BorderSide(2, color),
                right=ft.BorderSide(2, color),
                bottom=ft.BorderSide(2, color),
                left=ft.BorderSide(2, color),
            ),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.15, color),
                offset=ft.Offset(0, 2),
            ),
            content=ft.Column(
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icon, size=48, color=color),
                    ft.Text(
                        title,
                        size=14,
                        color=Theme.TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.W_500,
                    ),
                    # Jauge circulaire simulée avec ProgressRing + texte
                    ft.Stack(
                        width=120,
                        height=120,
                        controls=[
                            ft.ProgressRing(
                                width=120,
                                height=120,
                                value=percentage / 100,
                                color=color,
                                bgcolor=Theme.BG_TERTIARY,
                                stroke_width=12,
                            ),
                            ft.Container(
                                width=120,
                                height=120,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Text(
                                    f"{percentage:.1f}%",
                                    size=28,
                                    weight=ft.FontWeight.BOLD,
                                    color=color,
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )
    
    def _build_risk_matrix(self, all_ncs):
        """Construit la matrice de risque (Gravité x Statut)."""
        # Calcul de la matrice
        matrix = {
            'Critique': {'En cours': 0, 'Clôturée': 0},
            'Majeure': {'En cours': 0, 'Clôturée': 0},
            'Mineure': {'En cours': 0, 'Clôturée': 0},
        }
        
        for nc in all_ncs:
            gravite = nc.get('gravite', 'Mineure')
            statut = nc.get('statut', 'En cours')
            if gravite in matrix and statut in matrix[gravite]:
                matrix[gravite][statut] += 1
        
        # Construction visuelle
        def create_matrix_cell(gravite, statut, count):
            # Couleur selon gravité et nombre
            if gravite == 'Critique' and statut == 'En cours' and count > 0:
                bg_color = ft.Colors.RED_700
                text_color = ft.Colors.WHITE
            elif gravite == 'Majeure' and statut == 'En cours' and count > 0:
                bg_color = ft.Colors.ORANGE_600
                text_color = ft.Colors.WHITE
            elif count > 0:
                bg_color = ft.Colors.BLUE_600
                text_color = ft.Colors.WHITE
            else:
                bg_color = Theme.BG_TERTIARY
                text_color = Theme.TEXT_MUTED
            
            return ft.Container(
                width=140,
                height=100,
                bgcolor=bg_color,
                border_radius=8,
                padding=15,
                alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    spacing=5,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            f"{gravite}",
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=text_color,
                        ),
                        ft.Text(
                            statut,
                            size=11,
                            color=text_color,
                        ),
                        ft.Text(
                            str(count),
                            size=32,
                            weight=ft.FontWeight.BOLD,
                            color=text_color,
                        ),
                    ],
                ),
            )
        
        return ft.Container(
            padding=20,
            bgcolor=Theme.BG_SECONDARY,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.GRID_ON, size=24, color=ft.Colors.BLUE_700),
                            ft.Text(
                                "Matrice de Risque",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.TEXT_PRIMARY,
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color=ft.Colors.BLUE_100),
                    ft.Row(
                        spacing=15,
                        wrap=True,
                        controls=[
                            create_matrix_cell('Critique', 'En cours', matrix['Critique']['En cours']),
                            create_matrix_cell('Critique', 'Clôturée', matrix['Critique']['Clôturée']),
                            create_matrix_cell('Majeure', 'En cours', matrix['Majeure']['En cours']),
                            create_matrix_cell('Majeure', 'Clôturée', matrix['Majeure']['Clôturée']),
                            create_matrix_cell('Mineure', 'En cours', matrix['Mineure']['En cours']),
                            create_matrix_cell('Mineure', 'Clôturée', matrix['Mineure']['Clôturée']),
                        ],
                    ),
                ],
            ),
        )
    
    def _build_top_urgences(self, all_ncs, today):
        """Construit le tableau des 5 NC les plus anciennes non clôturées."""
        from datetime import datetime
        
        # Filtrer NC en cours
        nc_en_cours = [nc for nc in all_ncs if nc.get('statut') == 'En cours']
        
        # Trier par date (plus anciennes d'abord)
        nc_en_cours.sort(key=lambda x: x.get('date_detection', '9999-99-99'))
        
        # Top 5
        top_5 = nc_en_cours[:5]
        
        # Construire les lignes
        rows = []
        for nc in top_5:
            date_str = nc.get('date_detection', '')
            try:
                date_detection = datetime.strptime(date_str, '%Y-%m-%d').date()
                jours_ouverts = (today - date_detection).days
                jours_text = f"J+{jours_ouverts}"
                jours_color = ft.Colors.RED_600 if jours_ouverts > 30 else ft.Colors.ORANGE_600 if jours_ouverts > 14 else ft.Colors.BLUE_600
            except:
                jours_text = "N/A"
                jours_color = Theme.TEXT_MUTED
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(nc.get('reference', 'N/A'), size=13)),
                        ft.DataCell(ft.Text(date_str, size=13)),
                        ft.DataCell(
                            ft.Container(
                                padding=ft.Padding(left=10, right=10, top=5, bottom=5),
                                bgcolor=ft.Colors.with_opacity(0.2, jours_color),
                                border_radius=8,
                                content=ft.Text(
                                    jours_text,
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=jours_color,
                                ),
                            )
                        ),
                        ft.DataCell(ft.Container(width=120, content=ft.Text(nc.get('produit_concerne', 'N/A'), size=12, no_wrap=False))),
                        ft.DataCell(ft.Container(width=250, content=ft.Text((nc.get('description', 'N/A') or 'N/A')[:60] + ('...' if len(nc.get('description', '') or '') > 60 else ''), size=12))),
                        ft.DataCell(ft.Text(nc.get('imputation', 'N/A'), size=13)),
                        ft.DataCell(
                            self._create_severity_badge_inline(nc.get('gravite', 'Mineure'))
                        ),
                    ],
                    on_select_changed=lambda e, nc_id=nc.get('id'): self._open_nc_from_urgences(nc_id),
                )
            )
        
        return ft.Container(
            padding=20,
            bgcolor=Theme.BG_SECONDARY,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.PRIORITY_HIGH, size=24, color=ft.Colors.RED_700),
                            ft.Text(
                                "Top 5 Urgences (NC les plus anciennes non clôturées)",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.TEXT_PRIMARY,
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color=ft.Colors.BLUE_100),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Réf", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Date détection", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Âge", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Produit", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Description", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Imputation", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Gravité", weight=ft.FontWeight.BOLD)),
                        ],
                        rows=rows if rows else [
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("Aucune NC en cours", color=Theme.TEXT_MUTED)),
                                    ft.DataCell(ft.Text("")),
                                    ft.DataCell(ft.Text("")),
                                    ft.DataCell(ft.Text("")),
                                    ft.DataCell(ft.Text("")),
                                    ft.DataCell(ft.Text("")),
                                    ft.DataCell(ft.Text("")),
                                ]
                            )
                        ],
                        border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                        border_radius=8,
                        horizontal_lines=ft.BorderSide(1, Theme.OUTLINE),
                    ),
                ],
            ),
        )
    
    def _create_severity_badge_inline(self, gravite):
        """Crée un badge de gravité inline."""
        colors = {
            'Mineure': ft.Colors.GREEN_600,
            'Majeure': ft.Colors.ORANGE_600,
            'Critique': ft.Colors.RED_600,
        }
        return ft.Container(
            padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            bgcolor=ft.Colors.with_opacity(0.2, colors.get(gravite, ft.Colors.GREY_600)),
            border_radius=12,
            content=ft.Text(
                gravite,
                size=12,
                weight=ft.FontWeight.BOLD,
                color=colors.get(gravite, ft.Colors.GREY_600),
            ),
        )
    
    def _open_nc_from_urgences(self, nc_id):
        """Ouvre la NC depuis le tableau des urgences."""
        nc = self.db.get_nc(nc_id)
        if nc:
            self._open_form(nc)
    
    def _refresh_actions_correctives(self):
        """Rafraîchit le tableau des actions correctives instantanément."""
        # Invalider le cache du tableau de bord pour forcer la reconstruction
        # lors de la prochaine visite
        if 4 in self._tabs_cache:
            del self._tabs_cache[4]
        
        # Invalider également le cache des actions pour l'onglet Suivi Actions
        self._actions_cache = None
        self._actions_cache_time = None
        
        # Si le conteneur existe ET est attaché à la page, le mettre à jour
        if (self._actions_correctives_container is not None and 
            hasattr(self._actions_correctives_container, 'page') and 
            self._actions_correctives_container.page is not None):
            try:
                # Récupérer toutes les NC
                all_ncs = self.db.get_all_nc()
                
                # Reconstruire le contenu
                new_content = self._build_actions_correctives_suivi(all_ncs)
                
                # Mise à jour partielle du conteneur
                self._actions_correctives_container.content = new_content
                self._actions_correctives_container.update()
            except Exception as e:
                # Si erreur, simplement invalider le cache (déjà fait)
                print(f"Erreur lors du rafraîchissement des actions correctives: {e}")
    
    def _build_actions_correctives_suivi(self, all_ncs):
        """Construit le tableau de suivi des actions correctives en cours."""
        from datetime import datetime
        import json
        
        # Collecter toutes les actions en cours (non clôturées)
        actions_en_cours = []
        for nc in all_ncs:
            nc_ref = nc.get('reference', 'N/A')
            nc_statut = nc.get('statut', '')
            actions_json = nc.get('actions_correctives_table', '[]')
            try:
                actions = json.loads(actions_json) if actions_json else []
                for action in actions:
                    # Récupérer les champs des actions correctives
                    description = action.get('desc', '').strip()
                    statut_action = action.get('statut', 'En cours')
                    
                    # Afficher seulement les actions en cours avec description non vide
                    if description and statut_action != 'Clôturée':
                        # Dates - utiliser date_echeance en priorité, sinon date_fin pour compatibilité
                        date_debut = action.get('date_debut', '')
                        date_echeance = action.get('date_echeance', '') or action.get('date_fin', '')
                        date_cloture = action.get('date_cloture_action', '')
                        
                        # Responsable
                        responsable = action.get('responsable', 'Non assigné')
                        
                        # Coût
                        cost = action.get('cost', '')
                        try:
                            cost_float = float(cost) if cost else 0
                        except:
                            cost_float = 0
                        
                        actions_en_cours.append({
                            'nc_ref': nc_ref,
                            'nc_id': nc.get('id'),
                            'description': description,
                            'responsable': responsable,
                            'date_debut': date_debut,
                            'date_echeance': date_echeance,
                            'date_cloture': date_cloture,
                            'cost': cost_float,
                            'statut': statut_action,
                        })
            except Exception as ex:
                print(f"Erreur lecture actions NC {nc_ref}: {ex}")
                pass
        
        # Trier par date d'échéance (plus proche en premier), puis par date de début
        def sort_key(action):
            date_echeance = action['date_echeance']
            if date_echeance:
                try:
                    return (0, datetime.strptime(date_echeance, '%Y-%m-%d').date())
                except:
                    try:
                        # Essayer format DD/MM/YYYY
                        return (0, datetime.strptime(date_echeance, '%d/%m/%Y').date())
                    except:
                        pass
            # Si pas de date_echeance, utiliser date_debut
            date_debut = action['date_debut']
            if date_debut:
                try:
                    return (1, datetime.strptime(date_debut, '%Y-%m-%d').date())
                except:
                    try:
                        return (1, datetime.strptime(date_debut, '%d/%m/%Y').date())
                    except:
                        pass
            return (2, datetime.now().date())
        
        actions_en_cours.sort(key=sort_key)
        
        # Construire les lignes du tableau avec informations enrichies
        rows = []
        today = datetime.now().date()
        
        for action in actions_en_cours[:20]:  # Limite à 20 actions
            # Calculer l'urgence basée sur date_echeance
            date_echeance = action['date_echeance']
            if date_echeance:
                try:
                    # Essayer format YYYY-MM-DD puis DD/MM/YYYY
                    try:
                        deadline_date = datetime.strptime(date_echeance, '%Y-%m-%d').date()
                    except:
                        deadline_date = datetime.strptime(date_echeance, '%d/%m/%Y').date()
                    
                    deadline_display = deadline_date.strftime('%d/%m/%Y')
                    jours_restants = (deadline_date - today).days
                    
                    if jours_restants < 0:
                        urgence_color = ft.Colors.RED_600
                        urgence_text = f"RETARD {abs(jours_restants)}j"
                        urgence_icon = ft.Icons.ERROR
                    elif jours_restants <= 3:
                        urgence_color = ft.Colors.RED_400
                        urgence_text = f"Critique {jours_restants}j"
                        urgence_icon = ft.Icons.WARNING
                    elif jours_restants <= 7:
                        urgence_color = ft.Colors.ORANGE_600
                        urgence_text = f"Urgent {jours_restants}j"
                        urgence_icon = ft.Icons.NOTIFICATION_IMPORTANT
                    else:
                        urgence_color = ft.Colors.BLUE_600
                        urgence_text = f"{jours_restants} jours"
                        urgence_icon = ft.Icons.SCHEDULE
                except:
                    deadline_display = date_echeance
                    urgence_color = Theme.TEXT_MUTED
                    urgence_text = "Date invalide"
                    urgence_icon = ft.Icons.HELP_OUTLINE
            else:
                deadline_display = "Non définie"
                urgence_color = Theme.TEXT_MUTED
                urgence_text = "Aucune échéance"
                urgence_icon = ft.Icons.HELP_OUTLINE
            
            # Date de début
            date_debut_display = "N/A"
            if action['date_debut']:
                try:
                    # Essayer format YYYY-MM-DD puis DD/MM/YYYY
                    try:
                        date_debut_obj = datetime.strptime(action['date_debut'], '%Y-%m-%d').date()
                    except:
                        date_debut_obj = datetime.strptime(action['date_debut'], '%d/%m/%Y').date()
                    date_debut_display = date_debut_obj.strftime('%d/%m/%Y')
                except:
                    date_debut_display = action['date_debut']
            
            # Coût formaté
            cost_display = f"{action['cost']:.2f} EUR" if action['cost'] > 0 else "-"
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(action['nc_ref'], size=12, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY),
                                on_click=lambda e, nc_id=action['nc_id']: self._open_nc_from_urgences(nc_id),
                                ink=True,
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                width=280,
                                content=ft.Text(
                                    action['description'][:90] + ('...' if len(action['description']) > 90 else ''),
                                    size=12,
                                    no_wrap=False,
                                    max_lines=2,
                                ),
                            )
                        ),
                        ft.DataCell(
                            ft.Row(
                                spacing=5,
                                controls=[
                                    ft.Icon(ft.Icons.PERSON, size=14, color=Theme.PRIMARY),
                                    ft.Text(action['responsable'], size=12),
                                ],
                            )
                        ),
                        ft.DataCell(ft.Text(date_debut_display, size=11, color=Theme.TEXT_MUTED)),
                        ft.DataCell(
                            ft.Container(
                                padding=ft.Padding(left=10, right=10, top=6, bottom=6),
                                bgcolor=ft.Colors.with_opacity(0.15, urgence_color),
                                border=ft.Border(
                top=ft.BorderSide(1, urgence_color),
                right=ft.BorderSide(1, urgence_color),
                bottom=ft.BorderSide(1, urgence_color),
                left=ft.BorderSide(1, urgence_color),
            ),
                                border_radius=8,
                                content=ft.Row(
                                    spacing=6,
                                    controls=[
                                        ft.Icon(urgence_icon, size=16, color=urgence_color),
                                        ft.Column(
                                            spacing=2,
                                            controls=[
                                                ft.Text(deadline_display, size=11, weight=ft.FontWeight.BOLD, color=urgence_color),
                                                ft.Text(urgence_text, size=9, color=urgence_color),
                                            ],
                                        ),
                                    ],
                                ),
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                cost_display,
                                size=12,
                                weight=ft.FontWeight.BOLD if action['cost'] > 0 else ft.FontWeight.NORMAL,
                                color=ft.Colors.GREEN_700 if action['cost'] > 0 else Theme.TEXT_MUTED,
                            )
                        ),
                    ],
                )
            )
        
        return ft.Container(
            padding=20,
            bgcolor=Theme.BG_SECONDARY,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.ASSIGNMENT_TURNED_IN, size=28, color=ft.Colors.BLUE_700),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        "Suivi des Actions Correctives en Cours",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=Theme.TEXT_PRIMARY,
                                    ),
                                    ft.Text(
                                        f"{len(actions_en_cours)} action(s) en cours * Triées par échéance",
                                        size=12,
                                        color=Theme.TEXT_MUTED,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color=ft.Colors.BLUE_100),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("NC", weight=ft.FontWeight.BOLD, size=12)),
                            ft.DataColumn(ft.Text("Action Corrective", weight=ft.FontWeight.BOLD, size=12)),
                            ft.DataColumn(ft.Text("Responsable", weight=ft.FontWeight.BOLD, size=12)),
                            ft.DataColumn(ft.Text("Début", weight=ft.FontWeight.BOLD, size=12)),
                            ft.DataColumn(ft.Text("Échéance & Urgence", weight=ft.FontWeight.BOLD, size=12)),
                            ft.DataColumn(ft.Text("Coût", weight=ft.FontWeight.BOLD, size=12)),
                        ],
                        rows=rows if rows else [
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("Aucune action corrective en cours", color=Theme.TEXT_MUTED)),
                                    ft.DataCell(ft.Text("")),
                                    ft.DataCell(ft.Text("")),
                                    ft.DataCell(ft.Text("")),
                                    ft.DataCell(ft.Text("")),
                                    ft.DataCell(ft.Text("")),
                                ]
                            )
                        ],
                        border=ft.Border(
                top=ft.BorderSide(1, Theme.OUTLINE),
                right=ft.BorderSide(1, Theme.OUTLINE),
                bottom=ft.BorderSide(1, Theme.OUTLINE),
                left=ft.BorderSide(1, Theme.OUTLINE),
            ),
                        border_radius=8,
                        horizontal_lines=ft.BorderSide(1, Theme.OUTLINE),
                    ),
                ],
            ),
        )
    
    def _create_kpi_card(self, title: str, value: str, color, icon):
        """Crée une carte KPI."""
        return ft.Container(
            width=250,
            padding=20,
            bgcolor=Theme.BG_SECONDARY,
            border_radius=10,
            border=ft.Border(
                top=ft.BorderSide(2, color),
                right=ft.BorderSide(2, color),
                bottom=ft.BorderSide(2, color),
                left=ft.BorderSide(2, color),
            ),
            content=ft.Column(
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icon, size=40, color=color),
                    ft.Text(
                        title,
                        size=14,
                        color=Theme.TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        value,
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=color,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )
    
    def _create_stat_item(self, title: str, data: dict):
        """Crée un élément statistique avec liste."""
        items = []
        total = sum(data.values())
        
        for key, count in sorted(data.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            items.append(
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(
                            width=150,
                            content=ft.Text(key or "Non défini", size=13),
                        ),
                        ft.Container(
                            width=60,
                            content=ft.Text(
                                f"{count}",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.PRIMARY,
                            ),
                        ),
                        ft.Container(
                            width=80,
                            content=ft.ProgressBar(
                                value=percentage / 100,
                                color=Theme.PRIMARY,
                                bgcolor=Theme.BG_TERTIARY,
                            ),
                        ),
                        ft.Text(
                            f"{percentage:.1f}%",
                            size=12,
                            color=Theme.TEXT_MUTED,
                        ),
                    ],
                )
            )
        
        return ft.Container(
            width=400,
            padding=15,
            bgcolor=Theme.BG_PRIMARY,
            border_radius=8,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Text(
                        title,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=Theme.TEXT_PRIMARY,
                    ),
                    ft.Divider(height=1, color=Theme.OUTLINE),
                    ft.Column(spacing=8, controls=items),
                ],
            ),
        )
    
    # ========================================================================
    # HELPERS MATPLOTLIB POUR AFFICHAGE DANS L'APPLICATION
    # ========================================================================
    
    def _generate_chart_base64(self, chart_type, **kwargs):
        """Génère un graphique matplotlib et le retourne en base64 pour affichage avec cache."""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from io import BytesIO
            import base64
            import hashlib
            import json
            
            # Initialiser le cache si nécessaire
            if not hasattr(self, '_chart_cache'):
                self._chart_cache = {}
            
            # Créer une clé de cache basée sur les paramètres
            cache_params = {
                'type': chart_type,
                'selected_type': getattr(self, 'stats_selected_type', 'Tout'),
                'years': sorted(getattr(self, 'stats_years_selected', [])),
            }
            
            if chart_type == 'repartition':
                # Déterminer le repartition_type à partir du field_name
                field_to_type = {
                    'imputation': 'imputation',
                    'type_anomalie': 'anomalie',
                    'categorie_nc': 'categorie',
                    'gravite': 'gravite',
                    'matieres_reclames': 'matieres'
                }
                repartition_type_key = field_to_type.get(kwargs.get('field_name'), 'unknown')
                cache_params.update({
                    'field': kwargs.get('field_name'),
                    'date_debut': str(kwargs.get('date_debut')),
                    'date_fin': str(kwargs.get('date_fin')),
                    'top_limit': self.stats_zone_b_top_limit.get(repartition_type_key, "Tout"),
                })
            
            if chart_type == 'pareto':
                # Même paramètres que repartition mais pas de limite (toujours toutes les valeurs)
                cache_params.update({
                    'field': kwargs.get('field_name'),
                    'date_debut': str(kwargs.get('date_debut')),
                    'date_fin': str(kwargs.get('date_fin')),
                })
            
            cache_key = hashlib.md5(json.dumps(cache_params, sort_keys=True).encode()).hexdigest()
            
            # Vérifier le cache
            if cache_key in self._chart_cache:
                return self._chart_cache[cache_key]
            
            # Créer le graphique selon le type
            if chart_type == 'evolution':
                fig = self._create_evolution_chart_figure(kwargs.get('all_ncs'))
            elif chart_type == 'comparateur':
                fig = self._create_comparateur_chart_figure(kwargs.get('all_ncs'))
            elif chart_type == 'comparateur_type':
                fig = self._create_comparateur_type_chart_figure(kwargs.get('all_ncs'))
            elif chart_type == 'repartition':
                fig = self._create_repartition_chart_figure(
                    kwargs.get('all_ncs'),
                    kwargs.get('field_name'),
                    kwargs.get('title'),
                    kwargs.get('date_debut'),
                    kwargs.get('date_fin'),
                    kwargs.get('color')
                )
            elif chart_type == 'pareto':
                fig = self._create_pareto_chart_figure(
                    kwargs.get('all_ncs'),
                    kwargs.get('field_name'),
                    kwargs.get('title'),
                    kwargs.get('date_debut'),
                    kwargs.get('date_fin'),
                    kwargs.get('color')
                )
            else:
                return None
            
            # Vérifier que la figure a bien été créée
            if fig is None:
                print(f"[CHART ERROR] Figure None pour chart_type={chart_type}")
                return None
            
            # Déterminer le DPI selon le type de graphique
            # Zone B (répartition/pareto): Qualité optimisée pour chargement rapide
            # Zone A (évolution/comparateur): DPI réduit pour génération instantanée
            if chart_type in ['repartition', 'pareto']:
                dpi = 100  # Qualité optimisée (30% plus rapide qu'à 120)
            else:
                dpi = 80  # DPI réduit pour génération rapide (20% plus rapide qu'à 100)
            
            # Sauvegarder en mémoire
            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight', facecolor='#0F172A', edgecolor='none')
            plt.close(fig)
            buf.seek(0)
            
            # Convertir en base64
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()
            
            # Mettre en cache (limiter à 20 graphiques max)
            if len(self._chart_cache) > 20:
                # Supprimer les plus anciens
                self._chart_cache.pop(next(iter(self._chart_cache)))
            self._chart_cache[cache_key] = img_base64
            
            return img_base64
            
        except Exception as ex:
            print(f"Erreur génération graphique base64: {ex}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_evolution_chart_figure(self, all_ncs):
        """Crée la figure matplotlib pour l'évolution mensuelle."""
        import matplotlib.pyplot as plt
        from datetime import datetime
        from collections import defaultdict
        
        # Utiliser l'année sélectionnée au lieu de l'année courante
        selected_year = getattr(self, 'stats_evolution_year', datetime.now().year)
        
        # Collecter les données (optimisé avec compréhension de liste)
        monthly_data = defaultdict(lambda: defaultdict(int))
        monthly_global = defaultdict(int)
        
        # Filtrer d'abord par année pour réduire le traitement
        current_year_ncs = [nc for nc in all_ncs if nc.get('date_detection', '').startswith(str(selected_year))]
        
        for nc in current_year_ncs:
            date_str = nc.get('date_detection', '')
            type_nc = nc.get('type_nc', 'Non défini')
            if date_str:
                try:
                    month = int(date_str.split('-')[1])
                    monthly_data[type_nc][month] += 1
                    monthly_global[month] += 1
                except:
                    pass
        
        # Créer le graphique avec taille optimisée
        fig, ax = plt.subplots(figsize=(10, 4.5))
        fig.patch.set_facecolor('#0F172A')
        ax.set_facecolor('#1E293B')
        
        mois_labels = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jui', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        
        if self.stats_selected_type == "Tout":
            # Graphique empilé
            types_nc = list(monthly_data.keys())
            bottom = [0] * 12
            colors_map = {'Audit': '#9333EA', 'Client': '#1D4ED8', 'Fournisseur': '#EA580C', 
                         'Interne': '#16A34A', 'Prestataire': '#0D9488'}
            
            for type_nc in types_nc:
                values = [monthly_data[type_nc].get(m, 0) for m in range(1, 13)]
                ax.bar(mois_labels, values, bottom=bottom, label=type_nc, 
                      color=colors_map.get(type_nc, '#6B7280'))
                bottom = [b + v for b, v in zip(bottom, values)]
            
            # Légende horizontale sur une seule ligne en haut
            ax.legend(loc='upper center', ncol=5, bbox_to_anchor=(0.5, 1.12), 
                     facecolor='#1E293B', edgecolor='#475569', labelcolor='white', framealpha=0.9)
            
            # Afficher les totaux au-dessus de chaque barre
            for i, total in enumerate(bottom):
                if total > 0:
                    ax.text(i, total, str(int(total)), ha='center', va='bottom', 
                           color='white', fontsize=9, fontweight='bold')
        else:
            # Graphique simple
            values = [monthly_data[self.stats_selected_type].get(m, 0) for m in range(1, 13)]
            colors_map = {'Audit': '#9333EA', 'Client': '#1D4ED8', 'Fournisseur': '#EA580C', 
                         'Interne': '#16A34A', 'Prestataire': '#0D9488'}
            ax.bar(mois_labels, values, color=colors_map.get(self.stats_selected_type, '#2563EB'))
            
            # Afficher les valeurs au-dessus de chaque barre
            for i, value in enumerate(values):
                if value > 0:
                    ax.text(i, value, str(int(value)), ha='center', va='bottom', 
                           color='white', fontsize=9, fontweight='bold')
        
        ax.set_title(f'Évolution Mensuelle des NC - {selected_year}', 
                    fontsize=14, fontweight='bold', color='white', pad=30)
        ax.set_xlabel('Mois', color='white', fontsize=11)
        ax.set_ylabel('Nombre de NC', color='white', fontsize=11)
        ax.tick_params(colors='white')
        ax.grid(axis='y', alpha=0.2, color='#475569')
        ax.spines['bottom'].set_color('#475569')
        ax.spines['left'].set_color('#475569')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        return fig
    
    def _create_comparateur_chart_figure(self, all_ncs):
        """Crée la figure matplotlib pour le comparateur annuel."""
        import matplotlib.pyplot as plt
        from datetime import datetime
        from collections import defaultdict
        import numpy as np
        
        # Filtrer par années sélectionnées pour réduire le traitement
        selected_years = sorted(self.stats_years_selected) if hasattr(self, 'stats_years_selected') else []
        if not selected_years:
            # Retourner une figure vide avec un message
            fig, ax = plt.subplots(figsize=(12, 4))
            fig.patch.set_facecolor('#0F172A')
            ax.set_facecolor('#1E293B')
            ax.text(0.5, 0.5, 'Aucune année sélectionnée', 
                   ha='center', va='center', color='white', fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.tight_layout()
            return fig
        
        # Filtrer les NC par années sélectionnées avant traitement
        year_strs = [str(y) for y in selected_years]
        filtered_ncs = [nc for nc in all_ncs if any(nc.get('date_detection', '').startswith(y) for y in year_strs)]
        
        # Collecter les données par année (sur données filtrées)
        yearly_data = defaultdict(lambda: defaultdict(int))
        for nc in filtered_ncs:
            date_str = nc.get('date_detection', '')
            if date_str:
                try:
                    parts = date_str.split('-')
                    year = int(parts[0])
                    month = int(parts[1])
                    if year in selected_years:
                        yearly_data[year][month] += 1
                except:
                    pass
        
        # Créer le graphique avec taille optimisée
        fig, ax = plt.subplots(figsize=(12, 4))
        fig.patch.set_facecolor('#0F172A')
        ax.set_facecolor('#1E293B')
        
        mois_labels = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jui', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        x = np.arange(len(mois_labels))
        
        colors_map = {2025: '#1D4ED8', 2024: '#EA580C', 2023: '#16A34A', 
                     2022: '#9333EA', 2021: '#0D9488', 2020: '#DC2626'}
        
        width = 0.15
        offset = 0
        
        # Calculer la valeur maximale de TOUTES les barres pour dimensionner correctement
        all_bar_values = []
        for year in sorted(self.stats_years_selected):
            for m in range(1, 13):
                value = yearly_data[year].get(m, 0)
                all_bar_values.append(value)
        
        max_bar_value = max(all_bar_values) if all_bar_values else 0
        trend_space_ratio = 0.20
        trend_offset = max_bar_value * 0.10
        y_max_final = max_bar_value * (1 + trend_space_ratio + 0.10)
        
        # Appliquer les limites Y
        ax.set_ylim(0, y_max_final)
        
        for year in sorted(self.stats_years_selected):
            values = [yearly_data[year].get(m, 0) for m in range(1, 13)]
            bars = ax.bar(x + offset, values, width, label=str(year), 
                  color=colors_map.get(year, '#6B7280'))
            
            # Afficher les valeurs au-dessus de chaque barre
            for i, (bar, value) in enumerate(zip(bars, values)):
                if value > 0:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2, height, str(int(value)),
                           ha='center', va='bottom', color='white', fontsize=8, fontweight='bold')
            
            offset += width
        
        # Ajouter les courbes de tendance si activées
        if hasattr(self, 'show_comparateur_annuel_trends') and self.show_comparateur_annuel_trends:
            # Ajouter les courbes de tendance pour chaque mois
            month_colors = ['#EF4444', '#F59E0B', '#10B981', '#06B6D4', '#8B5CF6', '#EC4899',
                           '#F97316', '#84CC16', '#14B8A6', '#6366F1', '#A855F7', '#F43F5E']
            
            ax2 = ax.twinx()
            ax2.set_facecolor('none')
            ax2.set_ylabel('')
            ax2.spines['right'].set_visible(False)
            ax2.set_yticks([])
            ax2.set_ylim(0, y_max_final)
            
            # Tracer une tendance pour chaque mois (évolution entre première et dernière année)
            years_sorted = sorted(self.stats_years_selected)
            if len(years_sorted) >= 2:
                for month_idx in range(12):
                    first_year_value = yearly_data[years_sorted[0]].get(month_idx + 1, 0)
                    last_year_value = yearly_data[years_sorted[-1]].get(month_idx + 1, 0)
                    
                    # Tracer seulement si au moins une valeur existe
                    if first_year_value > 0 or last_year_value > 0:
                        color = month_colors[month_idx]
                        x_first = month_idx
                        x_last = month_idx + width * (len(years_sorted) - 1)
                        y_first = first_year_value + trend_offset
                        y_last = last_year_value + trend_offset
                        
                        if y_last > y_first:
                            trend_arrow = '^'
                        elif y_last < y_first:
                            trend_arrow = 'v'
                        else:
                            trend_arrow = '>'
                        
                        ax2.plot([x_first, x_last], [y_first, y_last],
                               linestyle='--', linewidth=1.5,
                               color=color, alpha=0.7, zorder=10)
                        
                        ax2.plot([x_first, x_last], [y_first, y_last],
                               marker='o', linestyle='none',
                               markersize=4, color=color, alpha=0.9,
                               markeredgecolor='white', markeredgewidth=1, zorder=11)
        
        ax.set_xticks(x + width * (len(self.stats_years_selected) - 1) / 2)
        ax.set_xticklabels(mois_labels)
        ax.set_title('Comparateur Annuel Multi-années avec Tendances', 
                    fontsize=14, fontweight='bold', color='white', pad=15)
        ax.set_xlabel('Mois', color='white', fontsize=11)
        ax.set_ylabel('Nombre de NC', color='white', fontsize=11)
        ax.tick_params(colors='white')
        ax.legend(facecolor='#1E293B', edgecolor='#475569', labelcolor='white', loc='upper left')
        ax.grid(axis='y', alpha=0.2, color='#475569')
        ax.spines['bottom'].set_color('#475569')
        ax.spines['left'].set_color('#475569')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        return fig
    
    def _create_comparateur_type_chart_figure(self, all_ncs):
        """Crée la figure matplotlib pour le comparateur par type NC multi-années."""
        import matplotlib.pyplot as plt
        from datetime import datetime
        from collections import defaultdict
        import numpy as np
        
        # Filtrer par années sélectionnées (utiliser stats_years_selected_type)
        selected_years = sorted(self.stats_years_selected_type) if hasattr(self, 'stats_years_selected_type') else []
        if not selected_years:
            # Retourner une figure vide avec un message
            fig, ax = plt.subplots(figsize=(12, 4))
            fig.patch.set_facecolor('#0F172A')
            ax.set_facecolor('#1E293B')
            ax.text(0.5, 0.5, 'Aucune année sélectionnée', 
                   ha='center', va='center', color='white', fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.tight_layout()
            return fig
        
        # Filtrer les NC par années sélectionnées
        year_strs = [str(y) for y in selected_years]
        filtered_ncs = [nc for nc in all_ncs if any(nc.get('date_detection', '').startswith(y) for y in year_strs)]
        
        # Types de NC possibles
        all_types_nc = ['Client', 'Fournisseur', 'Interne', 'Audit', 'Prestataire']
        
        # Collecter les données par année et par type
        yearly_type_data = defaultdict(lambda: defaultdict(int))
        for nc in filtered_ncs:
            date_str = nc.get('date_detection', '')
            type_nc = nc.get('type_nc', '')
            if date_str and type_nc in all_types_nc:
                try:
                    parts = date_str.split('-')
                    year = int(parts[0])
                    if year in selected_years:
                        yearly_type_data[year][type_nc] += 1
                except:
                    pass
        
        # Filtrer les types qui ont au moins une donnée sur toutes les années
        types_nc = []
        for type_nc in all_types_nc:
            has_data = any(yearly_type_data[year].get(type_nc, 0) > 0 for year in selected_years)
            if has_data:
                types_nc.append(type_nc)
        
        # Si aucun type n'a de données, afficher un message
        if not types_nc:
            fig, ax = plt.subplots(figsize=(12, 4))
            fig.patch.set_facecolor('#0F172A')
            ax.set_facecolor('#1E293B')
            ax.text(0.5, 0.5, 'Aucune donnée disponible pour les années sélectionnées', 
                   ha='center', va='center', color='white', fontsize=14)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.tight_layout()
            return fig
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(12, 4))
        fig.patch.set_facecolor('#0F172A')
        ax.set_facecolor('#1E293B')
        
        x = np.arange(len(types_nc))
        
        colors_map = {2025: '#1D4ED8', 2024: '#EA580C', 2023: '#16A34A', 
                     2022: '#9333EA', 2021: '#0D9488', 2020: '#DC2626'}
        
        width = 0.15
        offset = 0
        
        for year in sorted(selected_years):
            values = [yearly_type_data[year].get(type_nc, 0) for type_nc in types_nc]
            bars = ax.bar(x + offset, values, width, label=str(year), 
                  color=colors_map.get(year, '#6B7280'))
            
            # Afficher les valeurs au-dessus de chaque barre
            for i, (bar, value) in enumerate(zip(bars, values)):
                if value > 0:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2, height, str(int(value)),
                           ha='center', va='bottom', color='white', fontsize=8, fontweight='bold')
            
            offset += width
        
        # Calculer la valeur maximale de TOUTES les barres (tous types, toutes années)
        all_bar_values = []
        for type_nc in types_nc:
            for year in sorted(selected_years):
                value = yearly_type_data[year].get(type_nc, 0)
                all_bar_values.append(value)
        
        max_bar_value = max(all_bar_values) if all_bar_values else 0
        
        # Réserver 20% de l'espace total pour les tendances au-dessus des barres
        trend_space_ratio = 0.20
        trend_offset = max_bar_value * 0.10  # Offset entre barres et tendances
        
        # Calculer la limite Y finale pour tout contenir
        y_max_final = max_bar_value * (1 + trend_space_ratio + 0.10)  # +10% marge supplémentaire
        
        # Appliquer les limites Y AVANT de tracer les tendances
        ax.set_ylim(0, y_max_final)
        
        # Ajouter des courbes de tendance si activées
        if hasattr(self, 'show_comparateur_type_trends') and self.show_comparateur_type_trends:
            # Ajouter des courbes de tendance pour chaque type NC
            type_colors_map = {
                'Client': '#EF4444',
                'Fournisseur': '#F59E0B', 
                'Interne': '#10B981',
                'Audit': '#8B5CF6',
                'Prestataire': '#06B6D4'
            }
            
            # Créer un second axe pour les courbes de tendance avec la même échelle
            ax2 = ax.twinx()
            ax2.set_facecolor('none')
            ax2.set_ylabel('')
            ax2.spines['right'].set_visible(False)
            ax2.set_yticks([])
            ax2.set_ylim(0, y_max_final)
            
            for i, type_nc in enumerate(types_nc):
                # Calculer les valeurs pour la première et la dernière année
                years_sorted = sorted(selected_years)
                first_year_value = yearly_type_data[years_sorted[0]].get(type_nc, 0)
                last_year_value = yearly_type_data[years_sorted[-1]].get(type_nc, 0)
                
                # Tracer uniquement une ligne droite entre première et dernière année si au moins 2 années
                if len(selected_years) >= 2 and (first_year_value > 0 or last_year_value > 0):
                    color = type_colors_map.get(type_nc, '#6B7280')
                    
                    # Position X pour la première et dernière barre de ce type
                    x_first = i  # Première barre
                    x_last = i + width * (len(selected_years) - 1)  # Dernière barre
                    
                    # Valeurs Y avec offset pour être au-dessus de TOUTES les barres
                    y_first = first_year_value + trend_offset
                    y_last = last_year_value + trend_offset
                    
                    # Déterminer la flèche selon la tendance
                    if y_last > y_first:
                        trend_arrow = '^'  # Hausse
                    elif y_last < y_first:
                        trend_arrow = 'v'  # Baisse
                    else:
                        trend_arrow = '>'  # Stable
                    
                    # Tracer la ligne de tendance (uniquement début à fin)
                    ax2.plot([x_first, x_last], [y_first, y_last], 
                           linestyle='--', linewidth=2.5, 
                           color=color, alpha=0.85,
                           label=f'{trend_arrow} {type_nc}', zorder=10)
                    
                    # Ajouter des marqueurs au début et à la fin
                    ax2.plot([x_first, x_last], [y_first, y_last], 
                           marker='o', linestyle='none',
                           markersize=7, color=color, alpha=0.95,
                           markeredgecolor='white', markeredgewidth=1.5, zorder=11)
            
            # Combiner les légendes des deux axes
            handles1, labels1 = ax.get_legend_handles_labels()
            handles2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(handles1 + handles2, labels1 + labels2,
                     facecolor='#1E293B', edgecolor='#475569', 
                     labelcolor='white', fontsize=9, loc='upper left', ncol=2)
        else:
            # Pas de tendances, légende simple
            ax.legend(facecolor='#1E293B', edgecolor='#475569', 
                     labelcolor='white', fontsize=10, loc='upper left')
        
        ax.set_xticks(x + width * (len(selected_years) - 1) / 2)
        ax.set_xticklabels(types_nc, color='white', fontsize=10)
        ax.set_ylabel('Nombre de NC', color='white', fontsize=11)
        ax.set_xlabel('Types de NC', color='white', fontsize=11)
        ax.tick_params(colors='white')
        ax.set_title('Comparateur par Type NC Multi-années avec Tendances', 
                    fontsize=14, fontweight='bold', color='white', pad=15)
        
        ax.grid(axis='y', alpha=0.2, color='#475569')
        
        # Styliser les axes
        ax.spines['bottom'].set_color('#475569')
        ax.spines['left'].set_color('#475569')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        return fig
    
    def _create_pareto_chart_figure(self, all_ncs, field_name, title, date_debut, date_fin, color_hex):
        """Crée la figure matplotlib pour un diagramme de Pareto (analyse 80/20)."""
        import matplotlib.pyplot as plt
        from datetime import datetime
        from collections import defaultdict
        import numpy as np
        
        # Filtrer par date avec conversion optimisée
        date_debut_str = str(date_debut)
        date_fin_str = str(date_fin)
        
        filtered_ncs = []
        for nc in all_ncs:
            date_str = nc.get('date_detection', '')
            if date_str and date_debut_str <= date_str <= date_fin_str:
                filtered_ncs.append(nc)
        
        # Collecter les données
        data_dict = defaultdict(int)
        for nc in filtered_ncs:
            value = nc.get(field_name, 'Non défini')
            if value:
                data_dict[value] += 1
        
        # Trier par ordre décroissant
        sorted_data = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)
        
        # Prendre toutes les valeurs pour le Pareto (pas de limite)
        labels = [item[0][:25] for item in sorted_data]  # Tronquer les labels
        values = [item[1] for item in sorted_data]
        
        # Calculer les pourcentages cumulés
        total = sum(values)
        cumul_percent = np.cumsum([v/total*100 for v in values]) if total > 0 else []
        
        # Créer la figure avec hauteur augmentée pour accommoder la légende au-dessus
        fig, ax1 = plt.subplots(figsize=(7, 6.3))
        fig.patch.set_facecolor('#0F172A')
        ax1.set_facecolor('#1E293B')
        
        # Barres (axe gauche)
        x_pos = np.arange(len(labels))
        bars = ax1.bar(x_pos, values, color=color_hex, alpha=0.7, label='Nombre de NC')
        ax1.set_xlabel('Valeurs', color='white', fontsize=8)
        ax1.set_ylabel('Nombre de NC', color='white', fontsize=9)
        ax1.tick_params(axis='y', labelcolor='white', labelsize=8)
        ax1.tick_params(axis='x', labelcolor='white', labelsize=7, rotation=45)
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(labels, ha='right')
        
        # Ligne cumulative (axe droit)
        ax2 = ax1.twinx()
        line = ax2.plot(x_pos, cumul_percent, color='#FF4444', marker='o', 
                        linewidth=2, markersize=4, label='% Cumulé')
        ax2.set_ylabel('% Cumulé', color='white', fontsize=9)
        ax2.tick_params(axis='y', labelcolor='white', labelsize=8)
        ax2.set_ylim([0, 105])
        
        # Ligne horizontale à 80%
        ax2.axhline(y=80, color='#FFD700', linestyle='--', linewidth=2, 
                    alpha=0.9, zorder=10)
        
        # Zone ombrée pour la partie critique (<80%)
        idx_80 = None
        if len(cumul_percent) > 0:
            # Trouver l'index où on dépasse 80%
            idx_80 = next((i for i, cp in enumerate(cumul_percent) if cp >= 80), len(cumul_percent))
            total_values = len(labels)  # Nombre total de valeurs
            if idx_80 < len(cumul_percent):
                # Zone verte pour les éléments critiques (causent 80%)
                ax1.axvspan(-0.5, idx_80 + 0.5, alpha=0.2, color='#00FF00', zorder=0)
                # Zone rouge pour le reste
                ax1.axvspan(idx_80 + 0.5, len(labels) - 0.5, alpha=0.15, color='#FF6B6B', zorder=0)
                
                # Annoter la zone critique
                ax1.text(idx_80 / 2, max(values) * 0.95, 
                        f'< {idx_80 + 1} valeurs sur {total_values} = 80% des NC',
                        color='#00FF00', fontsize=9, fontweight='bold',
                        ha='center', bbox=dict(boxstyle='round,pad=0.4', 
                        facecolor='#1E293B', edgecolor='#00FF00', linewidth=2))
        
        # Titre (tout sur une ligne)
        ax1.set_title(f'Pareto: {title} ({date_debut} à {date_fin})', 
                     fontsize=10, fontweight='bold', color='white', pad=35)
        
        # Styliser les axes
        ax1.spines['bottom'].set_color('#475569')
        ax1.spines['left'].set_color('#475569')
        ax1.spines['top'].set_visible(False)
        ax2.spines['right'].set_color('#475569')
        ax2.spines['top'].set_visible(False)
        
        # Légende horizontale bien positionnée au-dessus du graphique
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        # Ajouter manuellement les labels pour les zones
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=color_hex, alpha=0.7, label='Nombre de NC'),
            plt.Line2D([0], [0], color='#FF4444', linewidth=2, marker='o', markersize=4, label='% Cumulé'),
            plt.Line2D([0], [0], color='#FFD700', linewidth=2, linestyle='--', label='Seuil 80%'),
            Patch(facecolor='#00FF00', alpha=0.2, label='Zone critique (80%)'),
        ]
        ax1.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 1.14), 
                  ncol=4, fontsize=9, facecolor='#1E293B', edgecolor='#475569', 
                  labelcolor='white', framealpha=0.9)
        
        # Marges: beaucoup d'espace en haut pour séparer légende du graphique
        plt.subplots_adjust(top=0.64, bottom=0.10, left=0.12, right=0.88)
        return fig
    
    def _create_repartition_chart_figure(self, all_ncs, field_name, title, date_debut, date_fin, color_hex):
        """Crée la figure matplotlib pour une répartition."""
        import matplotlib.pyplot as plt
        from datetime import datetime
        from collections import defaultdict
        
        # Filtrer par date avec conversion optimisée
        date_debut_str = str(date_debut)
        date_fin_str = str(date_fin)
        
        filtered_ncs = []
        for nc in all_ncs:
            date_str = nc.get('date_detection', '')
            if date_str and date_debut_str <= date_str <= date_fin_str:
                filtered_ncs.append(nc)
        
        # Collecter les données en une seule passe
        data_dict = defaultdict(int)
        for nc in filtered_ncs:
            value = nc.get(field_name, 'Non défini')
            if value:
                data_dict[value] += 1
        
        # Créer le graphique avec taille uniformisée
        fig, ax = plt.subplots(figsize=(7, 4.2))
        fig.patch.set_facecolor('#0F172A')
        ax.set_facecolor('#1E293B')
        
        # Trier et appliquer la limite configurée
        sorted_data = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)
        # Récupérer la limite pour ce type de graphique
        repartition_type_key = None
        if field_name == 'imputation':
            repartition_type_key = 'imputation'
        elif field_name == 'type_anomalie':
            repartition_type_key = 'anomalie'
        elif field_name == 'categorie_nc':
            repartition_type_key = 'categorie'
        elif field_name == 'gravite':
            repartition_type_key = 'gravite'
        elif field_name == 'matieres_reclames':
            repartition_type_key = 'matieres'
        
        if repartition_type_key:
            top_limit = self.stats_zone_b_top_limit.get(repartition_type_key, "Tout")
            if top_limit != "Tout":
                sorted_data = sorted_data[:int(top_limit)]
        
        labels = [item[0][:30] for item in sorted_data]  # Tronquer les labels longs
        values = [item[1] for item in sorted_data]
        
        # Créer les barres
        colors = plt.cm.Set3(range(len(labels)))
        bars = ax.barh(labels, values, color=colors)
        
        ax.set_title(f'{title}\n({date_debut} à {date_fin})', 
                    fontsize=11, fontweight='bold', color='white', pad=8)
        ax.set_xlabel('Nombre de NC', color='white', fontsize=10)
        ax.tick_params(colors='white', labelsize=8)
        ax.grid(axis='x', alpha=0.2, color='#475569')
        ax.spines['bottom'].set_color('#475569')
        ax.spines['left'].set_color('#475569')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Ajouter les valeurs
        for i, (bar, v) in enumerate(zip(bars, values)):
            ax.text(v, i, f' {v}', va='center', color='white', fontsize=8)
        
        # Ajuster les marges pour garantir que tout reste dans le container
        plt.subplots_adjust(top=0.90, bottom=0.15, left=0.28, right=0.95)
        return fig
    
    # ========================================================================
    # TAB 6: STATISTIQUES
    # ========================================================================
    
    def _build_statistics_tab(self):
        """Construit l'onglet des statistiques orienté analyse de fond et coûts CNQ avec lazy loading et cache persistant."""
        # NE PLUS vider le cache ici - il sera vidé uniquement lors d'ajout/modif/suppression de NC
        # Cela permet de réutiliser les graphiques déjà générés (gain de 8-9 secondes)
        
        # Lazy loading: ne charger qu'une fois
        if self._stats_loaded and self._stats_data_cache:
            return self._stats_data_cache
        
        # Afficher un indicateur de chargement pendant la génération
        loading_indicator = ft.Container(
            expand=True,
            padding=50,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.ProgressRing(width=60, height=60, color=ft.Colors.BLUE_700),
                    ft.Container(height=20),
                    ft.Text(
                        "[Config] Génération des statistiques en cours...",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=Theme.TEXT_PRIMARY,
                    ),
                    ft.Text(
                        "Analyse des données et création des graphiques",
                        size=14,
                        color=Theme.TEXT_MUTED,
                    ),
                ],
            ),
        )
        
        all_ncs = self.db.get_all_nc()
        
        # === ZONE A: ÉVOLUTION ET COMPARAISON TEMPORELLE ===
        evolution_mensuelle = self._build_evolution_mensuelle_par_type(all_ncs)
        # Stocker la référence du container pour actualisation partielle
        self._evolution_container = evolution_mensuelle
        
        comparateur_annuel = self._build_comparateur_annuel(all_ncs)
        # Stocker la référence du container pour actualisation partielle
        self._comparateur_container = comparateur_annuel
        
        # Nouveau: Comparateur par Type (Client, Fournisseur, etc.) multi-années
        comparateur_par_type = self._build_comparateur_par_type(all_ncs)
        self._comparateur_type_container = comparateur_par_type
        
        # === ZONE B: RÉPARTITIONS (chargement différé pour optimisation) ===
        # Créer un placeholder pour Zone B qui se chargera à la demande
        zone_b_placeholder = ft.Container(
            padding=20,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.GREEN_700),
                            ft.Text(
                                "[Info] Zone B : Chargement optimisé",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREEN_700,
                            ),
                        ],
                    ),
                    ft.Text(
                        "Les graphiques de répartition sont chargés à la demande pour des performances optimales.",
                        size=12,
                        color=Theme.TEXT_MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "[Stats] Charger les répartitions",
                        icon=ft.Icons.PIE_CHART,
                        on_click=lambda e: self._load_zone_b_on_demand(e, all_ncs),
                        bgcolor=ft.Colors.GREEN_700,
                        color=ft.Colors.WHITE,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
        
        # Stocker la référence pour le chargement différé
        self._zone_b_container = zone_b_placeholder
        
        # === ANALYSES EXISTANTES (plus légères, chargement immédiat) ===
        pareto_financier = self._build_pareto_cnq(all_ncs)
        analyse_5m = self._build_5m_analysis(all_ncs)
        performance_cloture = self._build_closure_performance(all_ncs)
        efficacite_capa = self._build_capa_efficiency(all_ncs)
        
        stats_content = ft.Column(
            expand=True,
            spacing=25,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                # ZONE A
                ft.Container(
                    padding=20,
                    bgcolor=Theme.BG_SECONDARY,
                    border_radius=12,
                    content=ft.Column(
                        spacing=20,
                        controls=[
                            ft.Text(
                                "[Stats] ZONE A : Évolution et Comparaison Temporelle",
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_700,
                            ),
                            ft.Divider(height=2, color=ft.Colors.BLUE_300),
                            evolution_mensuelle,
                            comparateur_annuel,
                            comparateur_par_type,
                        ],
                    ),
                ),
                # ZONE B (chargement différé)
                ft.Container(
                    padding=20,
                    bgcolor=Theme.BG_SECONDARY,
                    border_radius=12,
                    content=ft.Column(
                        spacing=20,
                        controls=[
                            ft.Text(
                                "[Graphique] ZONE B : Répartitions par Dimension",
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREEN_700,
                            ),
                            ft.Divider(height=2, color=ft.Colors.GREEN_300),
                            zone_b_placeholder,
                        ],
                    ),
                ),
            ],
        )
        
        # Mettre en cache et marquer comme chargé
        self._stats_data_cache = stats_content
        self._stats_loaded = True
        
        return stats_content
    
    def _clear_chart_cache(self):
        """Vide le cache des graphiques (à appeler après ajout/modification/suppression de NC)."""
        if hasattr(self, '_chart_cache'):
            self._chart_cache.clear()
        self._stats_loaded = False
        self._stats_data_cache = None
    
    def _load_zone_b_on_demand(self, e, all_ncs):
        """Charge Zone B à la demande pour optimiser les performances."""
        if not self.page or not hasattr(self, '_zone_b_container'):
            return
        
        # Afficher un loader pendant le chargement
        self._zone_b_container.content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.ProgressRing(width=40, height=40, color=ft.Colors.GREEN_700),
                ft.Container(height=10),
                ft.Text("Génération des répartitions...", size=14, color=Theme.TEXT_MUTED),
            ],
        )
        self.page.update()
        
        # Générer Zone B dans un thread pour ne pas bloquer l'UI
        import threading
        def load_zone_b():
            try:
                repartitions = self._build_repartitions_zone_b(all_ncs)
                if self.page and hasattr(self, '_zone_b_container'):
                    self._zone_b_container.content = repartitions
                    self.page.update()
            except Exception as ex:
                print(f"Erreur chargement Zone B: {ex}")
                if self.page and hasattr(self, '_zone_b_container'):
                    self._zone_b_container.content = ft.Text(
                        f"[Erreur] Erreur lors du chargement: {str(ex)}",
                        color=ft.Colors.RED,
                    )
                    self.page.update()
        
        threading.Thread(target=load_zone_b, daemon=True).start()
    
    def _build_evolution_mensuelle_par_type(self, all_ncs):
        """Construit le graphique d'évolution mensuelle avec matplotlib."""
        from datetime import datetime
        
        # Types disponibles
        types_disponibles = ["Tout", "Audit", "Client", "Fournisseur", "Interne", "Prestataire"]
        colors_types = {
            "Tout": ft.Colors.BLUE_600,
            "Audit": ft.Colors.PURPLE_600,
            "Client": ft.Colors.BLUE_700,
            "Fournisseur": ft.Colors.ORANGE_600,
            "Interne": ft.Colors.GREEN_600,
            "Prestataire": ft.Colors.TEAL_600,
        }
        
        # Générer la liste des années disponibles (dernières 10 années)
        current_year = datetime.now().year
        available_years = [str(y) for y in range(current_year, current_year - 10, -1)]
        
        # Stocker les références des switches pour les mettre à jour
        self._evolution_switches = {}
        self._evolution_title_text = None  # Référence au texte du titre pour mise à jour
        
        # Fonction pour changer l'année sélectionnée
        def change_evolution_year(e):
            self.stats_evolution_year = int(e.control.value)
            # Vider le cache pour forcer la regénération
            if hasattr(self, '_chart_cache'):
                self._chart_cache.clear()
            # Regénérer le graphique matplotlib
            img_base64 = self._generate_chart_base64('evolution', all_ncs=all_ncs)
            if img_base64 and self._evolution_chart_image:
                self._evolution_chart_image.src_base64 = img_base64
            # Mettre à jour le titre
            if self._evolution_title_text:
                self._evolution_title_text.value = f"[Graphique] Évolution Mensuelle (Année {self.stats_evolution_year})"
            # Mettre à jour la page
            if self.page:
                self.page.update()
        
        # Créer les boutons de filtre avec Switch (mode radio - un seul actif)
        def select_type_filter(type_name):
            def handler(e):
                if e.control.value:  # Si on active ce switch
                    self.stats_selected_type = type_name
                    # Désactiver tous les autres switches
                    for other_type, other_switch in self._evolution_switches.items():
                        if other_type != type_name and other_switch.value:
                            other_switch.value = False
                    # Vider le cache pour forcer la regénération
                    if hasattr(self, '_chart_cache'):
                        self._chart_cache.clear()
                    # Regénérer le graphique matplotlib
                    img_base64 = self._generate_chart_base64('evolution', all_ncs=all_ncs)
                    if img_base64 and self._evolution_chart_image:
                        self._evolution_chart_image.src_base64 = img_base64
                    # Mettre à jour la page pour rafraîchir tous les switches
                    if self.page:
                        self.page.update()
                else:  # Si on désactive, revenir à "Tout"
                    if self.stats_selected_type == type_name:
                        self.stats_selected_type = "Tout"
                        # Activer le switch "Tout"
                        if "Tout" in self._evolution_switches:
                            self._evolution_switches["Tout"].value = True
                        # Vider le cache pour forcer la regénération
                        if hasattr(self, '_chart_cache'):
                            self._chart_cache.clear()
                        img_base64 = self._generate_chart_base64('evolution', all_ncs=all_ncs)
                        if img_base64 and self._evolution_chart_image:
                            self._evolution_chart_image.src_base64 = img_base64
                        # Mettre à jour la page pour rafraîchir tous les switches
                        if self.page:
                            self.page.update()
            return handler
        
        filter_switches = [ft.Text("Filtrer par type :", size=13, weight=ft.FontWeight.BOLD)]
        for type_name in types_disponibles:
            switch = ft.Switch(
                label=type_name,
                value=(self.stats_selected_type == type_name),
                on_change=select_type_filter(type_name),
                active_color=colors_types.get(type_name, ft.Colors.GREY_600),
            )
            self._evolution_switches[type_name] = switch
            filter_switches.append(switch)
        
        # Générer le graphique matplotlib
        img_base64 = self._generate_chart_base64('evolution', all_ncs=all_ncs)
        
        # Créer l'image Flet
        self._evolution_chart_image = ft.Image(
            src_base64=img_base64,
            width=1200,
            fit=ft.ImageFit.CONTAIN,
        ) if img_base64 else ft.Text("Erreur génération graphique", color=ft.Colors.RED)
        
        # Créer le texte du titre (référence pour mise à jour)
        self._evolution_title_text = ft.Text(
            f"[Graphique] Évolution Mensuelle (Année {self.stats_evolution_year})",
            size=18,
            weight=ft.FontWeight.BOLD,
            color=Theme.TEXT_PRIMARY,
        )
        
        # Stocker la référence du container pour l'export
        chart_container = ft.Container(
            padding=20,
            bgcolor=Theme.BG_PRIMARY,
            border_radius=12,
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.SHOW_CHART, size=24, color=ft.Colors.BLUE_700),
                                    self._evolution_title_text,
                                ],
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DOWNLOAD,
                                tooltip="Exporter en image",
                                icon_color=ft.Colors.BLUE_700,
                                on_click=lambda e: self._export_chart_image(chart_container, f"evolution_mensuelle_{self.stats_evolution_year}"),
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color=ft.Colors.BLUE_100),
                    ft.Container(
                        padding=10,
                        bgcolor=Theme.BG_SECONDARY,
                        border_radius=8,
                        content=ft.Row(
                            spacing=15,
                            wrap=False,
                            scroll=ft.ScrollMode.AUTO,
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=15,
                                    controls=filter_switches,
                                ),
                                ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Text("Année :", size=13, weight=ft.FontWeight.BOLD),
                                        ft.Dropdown(
                                            width=120,
                                            value=str(self.stats_evolution_year),
                                            options=[DropdownOption(year) for year in available_years],
                                            on_change=change_evolution_year,
                                            bgcolor=Theme.BG_PRIMARY,
                                            border_color=ft.Colors.BLUE_700,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),
                    self._evolution_chart_image,
                ],
            ),
        )
        
        return chart_container
    
    def _build_comparateur_annuel(self, all_ncs):
        """Construit le comparateur annuel multi-années avec matplotlib."""
        from datetime import datetime
        
        # Récupérer années disponibles
        years_available = set()
        for nc in all_ncs:
            date_str = nc.get('date_detection', '')
            if date_str:
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    years_available.add(date.year)
                except:
                    pass
        
        years_all = sorted(years_available, reverse=True)
        
        # Initialiser années sélectionnées si nécessaire
        if not hasattr(self, 'stats_years_selected') or not self.stats_years_selected:
            self.stats_years_selected = years_all[:3] if len(years_all) >= 3 else years_all
        
        # Initialiser état affichage tendances
        if not hasattr(self, 'show_comparateur_annuel_trends'):
            self.show_comparateur_annuel_trends = True
        
        # Couleurs distinctes par année
        colors_map = {
            2025: ft.Colors.BLUE_700,
            2024: ft.Colors.ORANGE_700,
            2023: ft.Colors.GREEN_700,
            2022: ft.Colors.PURPLE_700,
            2021: ft.Colors.TEAL_700,
            2020: ft.Colors.RED_700,
        }
        
        # Créer switches pour sélectionner les années
        def toggle_year_filter(year):
            def handler(e):
                if e.control.value:
                    if year not in self.stats_years_selected:
                        self.stats_years_selected.append(year)
                else:
                    if year in self.stats_years_selected:
                        self.stats_years_selected.remove(year)
                
                # Vider le cache pour forcer la regénération
                if hasattr(self, '_chart_cache'):
                    self._chart_cache.clear()
                
                # Regénérer le graphique comparateur annuel
                img_base64 = self._generate_chart_base64('comparateur', all_ncs=all_ncs)
                if img_base64 and self._comparateur_chart_image:
                    self._comparateur_chart_image.src_base64 = img_base64
                
                # Mettre à jour toute la page
                if self.page:
                    self.page.update()
            return handler
        
        # Handler pour activer/désactiver les tendances
        def toggle_trends(e):
            self.show_comparateur_annuel_trends = e.control.value
            
            # Vider le cache
            if hasattr(self, '_chart_cache'):
                self._chart_cache.clear()
            
            # Regénérer le graphique
            img_base64 = self._generate_chart_base64('comparateur', all_ncs=all_ncs)
            if img_base64 and self._comparateur_chart_image:
                self._comparateur_chart_image.src_base64 = img_base64
            
            if self.page:
                self.page.update()
        
        # Stocker les switches pour synchronisation
        if not hasattr(self, '_comparateur_annuel_switches'):
            self._comparateur_annuel_switches = {}
        
        year_switches = [ft.Text("Sélectionner les années :", size=13, weight=ft.FontWeight.BOLD)]
        for year in years_all:
            switch = ft.Switch(
                label=str(year),
                value=year in self.stats_years_selected,
                on_change=toggle_year_filter(year),
                active_color=colors_map.get(year, ft.Colors.GREY_600),
            )
            self._comparateur_annuel_switches[year] = switch
            year_switches.append(switch)
        
        # Ajouter switch pour les tendances
        trends_switch = ft.Switch(
            label="Afficher les tendances",
            value=self.show_comparateur_annuel_trends,
            on_change=toggle_trends,
            active_color=ft.Colors.CYAN_700,
        )
        year_switches.append(ft.Container(width=20))  # Espacement
        year_switches.append(trends_switch)
        
        # Générer le graphique matplotlib
        img_base64 = self._generate_chart_base64('comparateur', all_ncs=all_ncs)
        
        # Créer l'image Flet
        self._comparateur_chart_image = ft.Image(
            src_base64=img_base64,
            width=1400,
            fit=ft.ImageFit.CONTAIN,
        ) if img_base64 else ft.Text("Erreur génération graphique", color=ft.Colors.RED)
        
        # Ajouter bouton export
        comparateur_container = ft.Container(
            padding=20,
            bgcolor=Theme.BG_PRIMARY,
            border_radius=12,
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.COMPARE_ARROWS, size=24, color=ft.Colors.ORANGE_700),
                                    ft.Text(
                                        f"[Stats] Comparateur Annuel Multi-années",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=Theme.TEXT_PRIMARY,
                                    ),
                                ],
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DOWNLOAD,
                                tooltip="Exporter en image",
                                icon_color=ft.Colors.ORANGE_700,
                                on_click=lambda e: self._export_chart_image(comparateur_container, "comparateur_annuel"),
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color=ft.Colors.BLUE_100),
                    ft.Container(
                        padding=10,
                        bgcolor=Theme.BG_SECONDARY,
                        border_radius=8,
                        content=ft.Row(
                            spacing=15,
                            wrap=False,
                            scroll=ft.ScrollMode.AUTO,
                            controls=year_switches,
                        ),
                    ),
                    self._comparateur_chart_image,
                ],
            ),
        )
        
        return comparateur_container
    
    def _build_comparateur_par_type(self, all_ncs):
        """Construit le comparateur par type NC multi-années avec matplotlib."""
        from datetime import datetime
        
        # Récupérer années disponibles
        years_available = set()
        for nc in all_ncs:
            date_str = nc.get('date_detection', '')
            if date_str:
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    years_available.add(date.year)
                except:
                    pass
        
        years_all = sorted(years_available, reverse=True)
        
        # Utiliser les mêmes années sélectionnées que le comparateur mensuel mais liste indépendante
        if not hasattr(self, 'stats_years_selected_type') or not self.stats_years_selected_type:
            self.stats_years_selected_type = years_all[:3] if len(years_all) >= 3 else years_all
        
        # Initialiser état affichage tendances
        if not hasattr(self, 'show_comparateur_type_trends'):
            self.show_comparateur_type_trends = True
        
        # Couleurs distinctes par année (mêmes que le comparateur mensuel)
        colors_map = {
            2025: ft.Colors.BLUE_700,
            2024: ft.Colors.ORANGE_700,
            2023: ft.Colors.GREEN_700,
            2022: ft.Colors.PURPLE_700,
            2021: ft.Colors.TEAL_700,
            2020: ft.Colors.RED_700,
        }
        
        # Créer switches pour sélectionner les années (indépendant du comparateur mensuel)
        def toggle_year_filter_type(year):
            def handler(e):
                if e.control.value:
                    if year not in self.stats_years_selected_type:
                        self.stats_years_selected_type.append(year)
                else:
                    if year in self.stats_years_selected_type:
                        self.stats_years_selected_type.remove(year)
                
                # Vider le cache pour forcer la regénération
                if hasattr(self, '_chart_cache'):
                    self._chart_cache.clear()
                
                # Regénérer le graphique type uniquement
                img_base64_type = self._generate_chart_base64('comparateur_type', all_ncs=all_ncs)
                if img_base64_type and self._comparateur_type_chart_image:
                    self._comparateur_type_chart_image.src_base64 = img_base64_type
                
                # Mettre à jour toute la page
                if self.page:
                    self.page.update()
            return handler
        
        # Handler pour activer/désactiver les tendances
        def toggle_trends_type(e):
            self.show_comparateur_type_trends = e.control.value
            
            # Vider le cache
            if hasattr(self, '_chart_cache'):
                self._chart_cache.clear()
            
            # Regénérer le graphique
            img_base64_type = self._generate_chart_base64('comparateur_type', all_ncs=all_ncs)
            if img_base64_type and self._comparateur_type_chart_image:
                self._comparateur_type_chart_image.src_base64 = img_base64_type
            
            if self.page:
                self.page.update()
        
        # Stocker les switches pour synchronisation
        if not hasattr(self, '_comparateur_type_switches'):
            self._comparateur_type_switches = {}
        
        # Générer les switches des années
        year_switches = []
        for year in years_all:
            switch = ft.Switch(
                label=str(year),
                value=year in self.stats_years_selected_type,
                active_color=colors_map.get(year, ft.Colors.GREY_700),
                on_change=toggle_year_filter_type(year),
            )
            self._comparateur_type_switches[year] = switch
            year_switches.append(switch)
        
        # Ajouter switch pour les tendances
        trends_switch_type = ft.Switch(
            label="Afficher les tendances",
            value=self.show_comparateur_type_trends,
            on_change=toggle_trends_type,
            active_color=ft.Colors.CYAN_700,
        )
        year_switches.append(ft.Container(width=20))  # Espacement
        year_switches.append(trends_switch_type)
        
        # Générer le graphique matplotlib
        img_base64 = self._generate_chart_base64('comparateur_type', all_ncs=all_ncs)
        
        # Créer l'image Flet
        self._comparateur_type_chart_image = ft.Image(
            src_base64=img_base64,
            width=1200,
            height=400,
            fit=ft.ImageFit.CONTAIN,
        ) if img_base64 else ft.Text("Erreur de génération du graphique", color=ft.Colors.RED)
        
        comparateur_container = ft.Container(
            padding=20,
            bgcolor=Theme.BG_PRIMARY,
            border_radius=12,
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Icon(ft.Icons.BAR_CHART, size=24, color=ft.Colors.ORANGE_700),
                                    ft.Text(
                                        f"[Stats] Comparateur par Type NC Multi-années",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=Theme.TEXT_PRIMARY,
                                    ),
                                ],
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DOWNLOAD,
                                tooltip="Exporter en image",
                                icon_color=ft.Colors.ORANGE_700,
                                on_click=lambda e: self._export_chart_image(comparateur_container, "comparateur_par_type"),
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color=ft.Colors.BLUE_100),
                    ft.Container(
                        padding=10,
                        bgcolor=Theme.BG_SECONDARY,
                        border_radius=8,
                        content=ft.Row(
                            spacing=15,
                            wrap=False,
                            scroll=ft.ScrollMode.AUTO,
                            controls=year_switches,
                        ),
                    ),
                    self._comparateur_type_chart_image,
                ],
            ),
        )
        
        return comparateur_container
    
    def _build_repartitions_zone_b(self, all_ncs):
        """Construit la Zone B avec filtres de date dynamiques pour chaque répartition."""
        from datetime import datetime, timedelta
        
        # Initialiser les filtres de dates si nécessaire
        if not hasattr(self, 'stats_zone_b_dates') or not self.stats_zone_b_dates:
            date_fin_default = datetime.now().date()
            date_debut_default = (date_fin_default - timedelta(days=30))
            self.stats_zone_b_dates = {
                'imputation': (date_debut_default, date_fin_default),
                'anomalie': (date_debut_default, date_fin_default),
                'categorie': (date_debut_default, date_fin_default),
                'gravite': (date_debut_default, date_fin_default),
                'matieres': (date_debut_default, date_fin_default),
            }
        
        # Initialiser les limites de valeurs si nécessaire
        if not hasattr(self, 'stats_zone_b_top_limit') or not self.stats_zone_b_top_limit:
            self.stats_zone_b_top_limit = {
                'imputation': "Tout",
                'anomalie': "Tout",
                'categorie': "Tout",
                'gravite': "Tout",
                'matieres': "Tout",
            }
        
        # Initialiser le stockage des images de graphiques
        if not hasattr(self, '_repartition_chart_images'):
            self._repartition_chart_images = {}
        
        # Fonction helper pour créer un graphique avec filtre
        def create_filtered_pie_chart(chart_id, title, field_name, icon, color):
            # Convertir la couleur Flet en hex pour matplotlib
            color_map = {
                ft.Colors.BLUE_700: '#1976D2',
                ft.Colors.ORANGE_700: '#F57C00',
                ft.Colors.GREEN_700: '#388E3C',
                ft.Colors.RED_700: '#D32F2F',
                ft.Colors.PURPLE_700: '#7B1FA2',
            }
            color_hex = color_map.get(color, '#1976D2')  # Default bleu si non trouvé
            
            # Récupérer les dates du filtre
            date_debut, date_fin = self.stats_zone_b_dates.get(chart_id, (datetime.now().date() - timedelta(days=30), datetime.now().date()))
            
            # Générer le graphique de répartition
            img_base64_repartition = self._generate_chart_base64(
                'repartition', 
                all_ncs=all_ncs,
                field_name=field_name,
                title=title,
                date_debut=date_debut,
                date_fin=date_fin,
                color=color_hex
            )
            
            # Générer le graphique de Pareto
            img_base64_pareto = self._generate_chart_base64(
                'pareto', 
                all_ncs=all_ncs,
                field_name=field_name,
                title=title,
                date_debut=date_debut,
                date_fin=date_fin,
                color=color_hex
            )
            
            # Créer les images Flet
            chart_image_repartition = ft.Image(
                src_base64=img_base64_repartition,
                width=650,
                fit=ft.ImageFit.CONTAIN,
            ) if img_base64_repartition else ft.Text("Erreur génération graphique", color=ft.Colors.RED)
            
            chart_image_pareto = ft.Image(
                src_base64=img_base64_pareto,
                width=650,
                fit=ft.ImageFit.CONTAIN,
            ) if img_base64_pareto else ft.Text("Erreur génération graphique", color=ft.Colors.RED)
            
            # Stocker les références des images
            self._repartition_chart_images[chart_id] = chart_image_repartition
            self._repartition_chart_images[f"{chart_id}_pareto"] = chart_image_pareto
            
            # Créer les champs de date avec bouton calendrier (fonctionne hors ligne)
            field_debut = ft.TextField(
                label="Date début",
                value=date_debut.strftime('%Y-%m-%d'),
                hint_text="AAAA-MM-JJ",
                width=140,
                text_size=12,
                height=40,
                read_only=True,
                bgcolor=Theme.BG_SECONDARY,
                border_color=color,
                focused_border_color=color,
                suffix=ft.IconButton(
                    icon=ft.Icons.CALENDAR_TODAY,
                    icon_size=16,
                    tooltip="Calendrier",
                ),
            )
            
            field_fin = ft.TextField(
                label="Date fin",
                value=date_fin.strftime('%Y-%m-%d'),
                hint_text="AAAA-MM-JJ",
                width=140,
                text_size=12,
                height=40,
                read_only=True,
                bgcolor=Theme.BG_SECONDARY,
                border_color=color,
                focused_border_color=color,
                suffix=ft.IconButton(
                    icon=ft.Icons.CALENDAR_TODAY,
                    icon_size=16,
                    tooltip="Calendrier",
                ),
            )
            
            # Lier les boutons calendrier à l'ouverture du calendrier personnalisé
            field_debut.suffix.on_click = lambda e: self._open_stats_custom_calendar(chart_id, 'debut', field_debut, field_debut.value)
            field_fin.suffix.on_click = lambda e: self._open_stats_custom_calendar(chart_id, 'fin', field_fin, field_fin.value)
            
            # Handler pour validation et mise à jour des dates
            def create_date_change_handler(cid, which, field_ref):
                def handler(e):
                    from datetime import datetime
                    try:
                        # Valider le format de la date
                        new_value = e.control.value.replace('/', '-')
                        if len(new_value) == 10 and new_value.count('-') == 2:
                            parsed_date = datetime.strptime(new_value, '%Y-%m-%d').date()
                            
                            # Mettre à jour la date dans le stockage
                            current_debut, current_fin = self.stats_zone_b_dates.get(cid, (date_debut, date_fin))
                            if which == 'debut':
                                self.stats_zone_b_dates[cid] = (parsed_date, current_fin)
                                new_date_debut, new_date_fin = parsed_date, current_fin
                            else:
                                self.stats_zone_b_dates[cid] = (current_debut, parsed_date)
                                new_date_debut, new_date_fin = current_debut, parsed_date
                            
                            # Normaliser la valeur affichée
                            field_ref.value = parsed_date.strftime('%Y-%m-%d')
                            field_ref.error_text = None
                            field_ref.update()
                            
                            # Regénérer les deux graphiques (répartition + Pareto)
                            new_img_base64_repartition = self._generate_chart_base64(
                                'repartition', 
                                all_ncs=all_ncs,
                                field_name=field_name,
                                title=title,
                                date_debut=new_date_debut,
                                date_fin=new_date_fin,
                                color=color_hex
                            )
                            new_img_base64_pareto = self._generate_chart_base64(
                                'pareto', 
                                all_ncs=all_ncs,
                                field_name=field_name,
                                title=title,
                                date_debut=new_date_debut,
                                date_fin=new_date_fin,
                                color=color_hex
                            )
                            if new_img_base64_repartition and cid in self._repartition_chart_images:
                                self._repartition_chart_images[cid].src_base64 = new_img_base64_repartition
                                self._repartition_chart_images[cid].update()
                            if new_img_base64_pareto and f"{cid}_pareto" in self._repartition_chart_images:
                                self._repartition_chart_images[f"{cid}_pareto"].src_base64 = new_img_base64_pareto
                                self._repartition_chart_images[f"{cid}_pareto"].update()
                        else:
                            # Format incomplet, ne pas afficher d'erreur (l'utilisateur tape encore)
                            pass
                    except ValueError:
                        # Date invalide
                        field_ref.error_text = "Format: AAAA-MM-JJ"
                        field_ref.update()
                return handler
            
            field_debut.on_blur = create_date_change_handler(chart_id, 'debut', field_debut)
            field_fin.on_blur = create_date_change_handler(chart_id, 'fin', field_fin)
            
            # Créer le Dropdown pour la limite de valeurs
            limit_dropdown = ft.Dropdown(
                label="Afficher",
                value=self.stats_zone_b_top_limit.get(chart_id, "Tout"),
                options=[
                    DropdownOption("Tout"),
                    DropdownOption("5"),
                    DropdownOption("10"),
                    DropdownOption("15"),
                    DropdownOption("20"),
                ],
                width=120,
                text_size=12,
                bgcolor=Theme.BG_SECONDARY,
                border_color=color,
            )
            
            # Handler pour le changement de limite
            def on_limit_change(e):
                self.stats_zone_b_top_limit[chart_id] = e.control.value
                # Regénérer le graphique de répartition
                new_date_debut, new_date_fin = self.stats_zone_b_dates.get(chart_id, (date_debut, date_fin))
                new_img_base64 = self._generate_chart_base64(
                    'repartition', 
                    all_ncs=all_ncs,
                    field_name=field_name,
                    title=title,
                    date_debut=new_date_debut,
                    date_fin=new_date_fin,
                    color=color_hex
                )
                if new_img_base64 and chart_id in self._repartition_chart_images:
                    self._repartition_chart_images[chart_id].src_base64 = new_img_base64
                    self._repartition_chart_images[chart_id].update()
            
            limit_dropdown.on_change = on_limit_change
            
            # Container pour le graphique de répartition (gauche)
            container_repartition = ft.Container(
                expand=True,
                height=700,
                padding=15,
                bgcolor=Theme.BG_PRIMARY,
                border_radius=10,
                border=ft.Border(
                top=ft.BorderSide(2, color),
                right=ft.BorderSide(2, color),
                bottom=ft.BorderSide(2, color),
                left=ft.BorderSide(2, color),
            ),
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=4,
                    color=ft.Colors.with_opacity(0.1, color),
                ),
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(icon, size=20, color=color),
                                        ft.Text(
                                            title,
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=Theme.TEXT_PRIMARY,
                                        ),
                                    ],
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DOWNLOAD,
                                    tooltip="Exporter en image",
                                    icon_color=color,
                                    icon_size=18,
                                    on_click=lambda e: self._export_chart_image(container_repartition, f"repartition_{chart_id}"),
                                ),
                            ],
                        ),
                        ft.Divider(height=1, color=color),
                        # Filtres de date éditables (fonctionne hors ligne) et limite d'affichage
                        ft.Container(
                            padding=8,
                            bgcolor=ft.Colors.with_opacity(0.05, color),
                            border_radius=6,
                            content=ft.Column(
                                spacing=8,
                                controls=[
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.Icon(ft.Icons.DATE_RANGE, size=16, color=color),
                                            field_debut,
                                            ft.Text(">", size=16, color=color),
                                            field_fin,
                                            ft.Container(width=20),  # Espacement
                                            limit_dropdown,
                                        ],
                                    ),
                                ],
                            ),
                        ),
                        chart_image_repartition,
                    ],
                ),
            )
            
            # Container pour le graphique Pareto (droite)
            container_pareto = ft.Container(
                expand=True,
                height=700,
                padding=15,
                bgcolor=Theme.BG_PRIMARY,
                border_radius=10,
                border=ft.Border(
                top=ft.BorderSide(2, color),
                right=ft.BorderSide(2, color),
                bottom=ft.BorderSide(2, color),
                left=ft.BorderSide(2, color),
            ),
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=4,
                    color=ft.Colors.with_opacity(0.1, color),
                ),
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.ANALYTICS, size=20, color=color),
                                        ft.Text(
                                            f"Pareto 80/20 - {title}",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=Theme.TEXT_PRIMARY,
                                        ),
                                    ],
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DOWNLOAD,
                                    tooltip="Exporter en image",
                                    icon_color=color,
                                    icon_size=18,
                                    on_click=lambda e: self._export_chart_image(container_pareto, f"pareto_{chart_id}"),
                                ),
                            ],
                        ),
                        ft.Divider(height=1, color=color),
                        ft.Container(
                            padding=8,
                            bgcolor=ft.Colors.with_opacity(0.05, color),
                            border_radius=6,
                            content=ft.Text(
                                "[Stats] Analyse Pareto : Quelles valeurs causent 80% des NC ?",
                                size=11,
                                color=Theme.TEXT_MUTED,
                                italic=True,
                            ),
                        ),
                        chart_image_pareto,
                    ],
                ),
            )
            
            # Retourner une Row avec les deux graphiques
            return ft.Row(
                spacing=15,
                controls=[
                    container_repartition,
                    container_pareto,
                ],
            )
        
        # Stocker les paramètres pour lazy loading
        chart_configs = [
            ('imputation', "Répartition par Imputation", 'imputation', ft.Icons.BUSINESS, ft.Colors.BLUE_700),
            ('anomalie', "Répartition par Anomalie", 'type_anomalie', ft.Icons.ERROR_OUTLINE, ft.Colors.ORANGE_700),
            ('categorie', "Répartition par Catégorie", 'categorie_nc', ft.Icons.CATEGORY, ft.Colors.GREEN_700),
            ('gravite', "Répartition par Gravité", 'gravite', ft.Icons.PRIORITY_HIGH, ft.Colors.RED_700),
            ('matieres', "Répartition par Matières Réclamées", 'matieres_reclames', ft.Icons.INVENTORY_2, ft.Colors.PURPLE_700),
        ]
        
        # Stocker les containers pour lazy loading
        if not hasattr(self, '_zone_b_chart_containers'):
            self._zone_b_chart_containers = {}
        
        # Créer les ExpansionPanels avec lazy loading
        expansion_panels = []
        
        for chart_id, title, field_name, icon, color in chart_configs:
            # Container vide au départ (lazy loading)
            chart_container = ft.Column(spacing=10)
            self._zone_b_chart_containers[chart_id] = {
                'container': chart_container,
                'loaded': False,
                'config': (chart_id, title, field_name, icon, color)
            }
            
            # Handler pour charger le graphique à l'ouverture
            def create_expansion_handler(cid):
                def handler(e):
                    # Charger uniquement si pas encore chargé et si le panel est ouvert
                    if e.data == "true" and not self._zone_b_chart_containers[cid]['loaded']:
                        config = self._zone_b_chart_containers[cid]['config']
                        chart_id, title, field_name, icon, color = config
                        
                        # Afficher un loader pendant la génération
                        loader = ft.Column(
                            spacing=10,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.ProgressRing(width=40, height=40, color=color),
                                ft.Text("Génération des graphiques...", size=12, color=Theme.TEXT_MUTED),
                            ],
                        )
                        self._zone_b_chart_containers[cid]['container'].controls = [loader]
                        if self.page:
                            self.page.update()
                        
                        # Générer le graphique (dans un thread pour ne pas bloquer l'UI)
                        import threading
                        def load_chart():
                            chart_row = create_filtered_pie_chart(chart_id, title, field_name, icon, color)
                            self._zone_b_chart_containers[cid]['container'].controls = [chart_row]
                            self._zone_b_chart_containers[cid]['loaded'] = True
                            if self.page:
                                self.page.update()
                        
                        threading.Thread(target=load_chart, daemon=True).start()
                return handler
            
            # Créer l'ExpansionPanel
            panel = ft.ExpansionTile(
                title=ft.Row(
                    controls=[
                        ft.Icon(icon, size=20, color=color),
                        ft.Text(title, size=14, weight=ft.FontWeight.BOLD),
                    ],
                ),
                subtitle=ft.Text("Cliquez pour afficher les graphiques", size=11, color=Theme.TEXT_MUTED),
                initially_expanded=False,  # Fermé par défaut
                on_change=create_expansion_handler(chart_id),
                bgcolor=Theme.BG_PRIMARY,
                collapsed_bgcolor=Theme.BG_SECONDARY,
                controls=[chart_container],
            )
            expansion_panels.append(panel)
        
        return ft.Column(
            spacing=20,
            controls=[
                ft.Container(
                    padding=15,
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=8,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.GREEN_700),
                                    ft.Text(
                                        "[Info] Les graphiques sont chargés à la demande pour optimiser les performances.",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.GREEN_900,
                                    ),
                                ],
                            ),
                            ft.Text(
                                "Cliquez sur une catégorie pour afficher ses graphiques. Chaque graphique possède son propre filtre de période.",
                                size=11,
                                color=ft.Colors.GREEN_800,
                            ),
                        ],
                    ),
                ),
                *expansion_panels,
            ],
        )
    
    def _build_pareto_cnq(self, all_ncs):
        """Construit l'analyse Pareto du Coût Non-Qualité par imputation."""
        from collections import defaultdict
        
        # Calcul des coûts par imputation
        imputation_costs = defaultdict(lambda: {'interne': 0, 'externe': 0, 'detection': 0})
        
        for nc in all_ncs:
            imputation = nc.get('imputation', 'Non défini')
            
            # Coûts internes
            cout_interne = (
                float(nc.get('cout_analyse', 0) or 0) +
                float(nc.get('cout_controle_supp', 0) or 0) +
                float(nc.get('cout_rebut', 0) or 0) +
                float(nc.get('cout_retouche', 0) or 0)
            )
            
            # Coûts externes
            cout_externe = (
                float(nc.get('cout_immobilisation', 0) or 0) +
                float(nc.get('cout_retour_client', 0) or 0) +
                float(nc.get('cout_avoir', 0) or 0) +
                float(nc.get('cout_geste_commercial', 0) or 0)
            )
            
            # Coût détection (analyse + contrôle)
            cout_detection = (
                float(nc.get('cout_analyse', 0) or 0) +
                float(nc.get('cout_controle_supp', 0) or 0)
            )
            
            imputation_costs[imputation]['interne'] += cout_interne
            imputation_costs[imputation]['externe'] += cout_externe
            imputation_costs[imputation]['detection'] += cout_detection
        
        # Trier par coût total décroissant
        sorted_imputations = sorted(
            imputation_costs.items(),
            key=lambda x: x[1]['interne'] + x[1]['externe'],
            reverse=True
        )[:10]  # Top 10
        
        # Calcul du total pour % cumulé
        total_cnq = sum(costs['interne'] + costs['externe'] for _, costs in sorted_imputations)
        cumul_percent = 0
        
        # Construction des barres horizontales empilées
        bars = []
        for imputation, costs in sorted_imputations:
            total_imputation = costs['interne'] + costs['externe']
            percent = (total_imputation / total_cnq * 100) if total_cnq > 0 else 0
            cumul_percent += percent
            
            bars.append(
                ft.Column(
                    spacing=5,
                    controls=[
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.Text(
                                    imputation[:25],
                                    size=13,
                                    width=180,
                                    color=Theme.TEXT_PRIMARY,
                                ),
                                ft.Container(
                                    width=400,
                                    height=30,
                                    border_radius=6,
                                    bgcolor=Theme.BG_TERTIARY,
                                    content=ft.Stack(
                                        controls=[
                                            # Barre externe (rouge)
                                            ft.Container(
                                                width=400 * (costs['externe'] / total_cnq) if total_cnq > 0 else 0,
                                                height=30,
                                                bgcolor=ft.Colors.RED_600,
                                                border_radius=ft.BorderRadius(6, 0, 6, 0),
                                            ),
                                            # Barre interne (orange) - décalée
                                            ft.Container(
                                                margin=ft.Margin(400 * (costs['externe'] / total_cnq) if total_cnq > 0 else 0, 0, 0, 0),
                                                width=400 * (costs['interne'] / total_cnq) if total_cnq > 0 else 0,
                                                height=30,
                                                bgcolor=ft.Colors.ORANGE_600,
                                                border_radius=ft.BorderRadius(0, 6, 0, 6),
                                            ),
                                        ],
                                    ),
                                ),
                                ft.Text(
                                    f"{total_imputation:,.0f} EUR",
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLUE_700,
                                    width=100,
                                ),
                                ft.Text(
                                    f"{cumul_percent:.1f}%",
                                    size=12,
                                    color=Theme.TEXT_MUTED,
                                ),
                            ],
                        ),
                    ],
                )
            )
        
        # Légende
        legende = ft.Row(
            spacing=20,
            controls=[
                ft.Row(
                    spacing=5,
                    controls=[
                        ft.Container(width=20, height=20, bgcolor=ft.Colors.RED_600, border_radius=4),
                        ft.Text("Coûts Externes", size=12),
                    ],
                ),
                ft.Row(
                    spacing=5,
                    controls=[
                        ft.Container(width=20, height=20, bgcolor=ft.Colors.ORANGE_600, border_radius=4),
                        ft.Text("Coûts Internes", size=12),
                    ],
                ),
            ],
        )
        
        return ft.Container(
            padding=20,
            bgcolor=Theme.BG_SECONDARY,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.EURO_SYMBOL, size=24, color=ft.Colors.RED_700),
                            ft.Text(
                                "[Cout] Pareto Financier CNQ par Imputation (Top 10)",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.TEXT_PRIMARY,
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color=ft.Colors.BLUE_100),
                    legende,
                    ft.Column(spacing=10, controls=bars if bars else [
                        ft.Text("Aucune donnée de coût disponible", color=Theme.TEXT_MUTED)
                    ]),
                ],
            ),
        )
    
    def _build_5m_analysis(self, all_ncs):
        """Construit l'analyse des causes racines selon la méthode 5M (Ishikawa)."""
        import json
        
        # Compteurs des 6 catégories 5M
        m_counts = {
            "Main d'oeuvre": 0,
            "Matériel": 0,
            "Matière": 0,
            "Méthode": 0,
            "Milieu": 0,
            "Mesure": 0,
        }
        
        # Parser les analyses Ishikawa
        for nc in all_ncs:
            analyse_json = nc.get('analyse_details', '')
            if analyse_json:
                try:
                    analyse = json.loads(analyse_json)
                    ishikawa = analyse.get('ishikawa', {})
                    
                    for categorie in m_counts.keys():
                        causes = ishikawa.get(categorie, [])
                        if isinstance(causes, list):
                            # Compter les causes non vides
                            m_counts[categorie] += len([c for c in causes if c and c.strip()])
                except:
                    pass
        
        total_causes = sum(m_counts.values())
        
        # Construction des barres
        bars = []
        colors = [
            ft.Colors.BLUE_600,
            ft.Colors.ORANGE_600,
            ft.Colors.GREEN_600,
            ft.Colors.PURPLE_600,
            ft.Colors.RED_600,
            ft.Colors.TEAL_600,
        ]
        
        for idx, (categorie, count) in enumerate(sorted(m_counts.items(), key=lambda x: x[1], reverse=True)):
            percentage = (count / total_causes * 100) if total_causes > 0 else 0
            color = colors[idx % len(colors)]
            
            bars.append(
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Text(
                            categorie,
                            size=13,
                            width=120,
                            color=Theme.TEXT_PRIMARY,
                        ),
                        ft.Container(
                            width=300,
                            content=ft.ProgressBar(
                                value=percentage / 100,
                                color=color,
                                bgcolor=Theme.BG_TERTIARY,
                                bar_height=20,
                            ),
                        ),
                        ft.Text(
                            f"{count} ({percentage:.1f}%)",
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=color,
                            width=100,
                        ),
                    ],
                )
            )
        
        return ft.Container(
            padding=20,
            bgcolor=Theme.BG_SECONDARY,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ACCOUNT_TREE, size=24, color=ft.Colors.PURPLE_700),
                            ft.Text(
                                "[Recherche] Distribution des Causes Racines (5M Ishikawa)",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.TEXT_PRIMARY,
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color=ft.Colors.BLUE_100),
                    ft.Column(spacing=12, controls=bars if total_causes > 0 else [
                        ft.Text("Aucune analyse 5M disponible", color=Theme.TEXT_MUTED)
                    ]),
                    ft.Text(
                        f"Total causes identifiées : {total_causes}",
                        size=12,
                        color=Theme.TEXT_MUTED,
                        italic=True,
                    ),
                ],
            ),
        )
    
    def _build_closure_performance(self, all_ncs):
        """Construit l'analyse de performance de clôture (délai moyen + nombre clôturées)."""
        from datetime import datetime
        from collections import defaultdict
        
        # Groupement par mois
        monthly_stats = defaultdict(lambda: {'count': 0, 'total_days': 0})
        
        for nc in all_ncs:
            if nc.get('statut') == 'Clôturée':
                date_cloture = nc.get('date_cloture', '')
                date_detection = nc.get('date_detection', '')
                
                if date_cloture and date_detection:
                    try:
                        d_cloture = datetime.strptime(date_cloture, '%Y-%m-%d')
                        d_detection = datetime.strptime(date_detection, '%Y-%m-%d')
                        days = (d_cloture - d_detection).days
                        
                        if days >= 0:
                            month_key = d_cloture.strftime('%Y-%m')
                            monthly_stats[month_key]['count'] += 1
                            monthly_stats[month_key]['total_days'] += days
                    except:
                        pass
        
        # Prendre les 6 derniers mois
        sorted_months = sorted(monthly_stats.items(), reverse=True)[:6]
        sorted_months.reverse()  # Chronologique
        
        # Construction du graphique combo
        rows = []
        for month, stats in sorted_months:
            avg_days = stats['total_days'] / stats['count'] if stats['count'] > 0 else 0
            count = stats['count']
            
            rows.append(
                ft.Column(
                    spacing=5,
                    controls=[
                        ft.Text(month, size=11, color=Theme.TEXT_MUTED),
                        ft.Row(
                            spacing=10,
                            controls=[
                                # Barre délai moyen
                                ft.Container(
                                    width=max(avg_days * 2, 20),
                                    height=20,
                                    bgcolor=ft.Colors.BLUE_600,
                                    border_radius=4,
                                    tooltip=f"Délai moyen: {avg_days:.1f} jours",
                                ),
                                # Indicateur nombre
                                ft.Container(
                                    padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                                    bgcolor=ft.Colors.GREEN_600,
                                    border_radius=12,
                                    content=ft.Text(
                                        f"{count}",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE,
                                    ),
                                ),
                            ],
                        ),
                    ],
                )
            )
        
        # Légende
        legende = ft.Row(
            spacing=20,
            controls=[
                ft.Row(
                    spacing=5,
                    controls=[
                        ft.Container(width=20, height=15, bgcolor=ft.Colors.BLUE_600, border_radius=4),
                        ft.Text("Délai moyen (j)", size=11),
                    ],
                ),
                ft.Row(
                    spacing=5,
                    controls=[
                        ft.Container(width=20, height=15, bgcolor=ft.Colors.GREEN_600, border_radius=4),
                        ft.Text("Nombre clôturées", size=11),
                    ],
                ),
            ],
        )
        
        return ft.Container(
            width=500,
            padding=20,
            bgcolor=Theme.BG_SECONDARY,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.TIMELINE, size=22, color=ft.Colors.BLUE_700),
                            ft.Text(
                                "[Performance] Performance Clôture (6 mois)",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.TEXT_PRIMARY,
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color=ft.Colors.BLUE_100),
                    legende,
                    ft.Column(spacing=10, controls=rows if rows else [
                        ft.Text("Aucune NC clôturée", color=Theme.TEXT_MUTED)
                    ]),
                ],
            ),
        )
    
    def _build_capa_efficiency(self, all_ncs):
        """Construit l'analyse d'efficacité des actions CAPA (vérification)."""
        import json
        
        # Compteurs des statuts de vérification
        verif_counts = {
            'Non vérifié': 0,
            'Vérifié': 0,
            'Efficace': 0,
            'Non efficace': 0,
        }
        
        for nc in all_ncs:
            actions_json = nc.get('actions_correctives_table', '')
            if actions_json:
                try:
                    actions = json.loads(actions_json) if actions_json else []
                    for action in actions:
                        verif = action.get('verif', 'Non vérifié')
                        if verif in verif_counts:
                            verif_counts[verif] += 1
                        else:
                            verif_counts['Non vérifié'] += 1
                except:
                    pass
        
        total_actions = sum(verif_counts.values())
        
        # Construction du graphique donut (segments)
        segments = []
        colors_map = {
            'Non vérifié': ft.Colors.GREY_500,
            'Vérifié': ft.Colors.BLUE_600,
            'Efficace': ft.Colors.GREEN_600,
            'Non efficace': ft.Colors.RED_600,
        }
        
        for status, count in verif_counts.items():
            if count > 0:
                percentage = (count / total_actions * 100) if total_actions > 0 else 0
                segments.append(
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Container(
                                width=30,
                                height=30,
                                bgcolor=colors_map[status],
                                border_radius=15,
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        status,
                                        size=13,
                                        color=Theme.TEXT_PRIMARY,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"{count} actions ({percentage:.1f}%)",
                                        size=11,
                                        color=Theme.TEXT_MUTED,
                                    ),
                                ],
                            ),
                        ],
                    )
                )
        
        # Calcul taux efficacité
        actions_evaluees = verif_counts['Efficace'] + verif_counts['Non efficace']
        taux_efficacite = (verif_counts['Efficace'] / actions_evaluees * 100) if actions_evaluees > 0 else 0
        
        return ft.Container(
            width=500,
            padding=20,
            bgcolor=Theme.BG_SECONDARY,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            content=ft.Column(
                spacing=15,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=22, color=ft.Colors.GREEN_700),
                            ft.Text(
                                "[OK] Efficacité CAPA",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=Theme.TEXT_PRIMARY,
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color=ft.Colors.BLUE_100),
                    ft.Container(
                        padding=15,
                        bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.GREEN_100),
                        border_radius=8,
                        content=ft.Column(
                            spacing=5,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    "Taux d'Efficacité",
                                    size=13,
                                    color=Theme.TEXT_MUTED,
                                ),
                                ft.Text(
                                    f"{taux_efficacite:.1f}%",
                                    size=36,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.GREEN_700,
                                ),
                                ft.Text(
                                    f"({verif_counts['Efficace']}/{actions_evaluees} évaluées)",
                                    size=11,
                                    color=Theme.TEXT_MUTED,
                                ),
                            ],
                        ),
                    ),
                    ft.Column(spacing=10, controls=segments if total_actions > 0 else [
                        ft.Text("Aucune action CAPA", color=Theme.TEXT_MUTED)
                    ]),
                ],
            ),
        )

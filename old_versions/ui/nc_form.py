# -*- coding: utf-8 -*-
"""
Formulaire d'enregistrement des Non-Conformités
Chargement instantané - pas de délais
"""

import customtkinter as ctk
from datetime import datetime
from typing import Callable, Dict, Any
from .utils import ModernTheme


class NCForm(ctk.CTkFrame):
    """Formulaire NC avec chargement instantané."""
    
    def __init__(self, parent, on_save: Callable, on_cancel: Callable, user_info: dict = None, **kwargs):
        super().__init__(parent, fg_color=ModernTheme.BG_PRIMARY, **kwargs)
        
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.user_info = user_info or {}
        self.widgets: Dict[str, Any] = {}
        
        # Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Construction immédiate
        self._build_header()
        self._build_form()
        self._build_footer()
    
    def _build_header(self):
        """En-tête du formulaire."""
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        header.grid_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="📋 Enregistrement Non-Conformité",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=ModernTheme.TEXT_PRIMARY
        )
        title.pack(side="left")
        
        date_label = ctk.CTkLabel(
            header,
            text=f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            font=ctk.CTkFont(size=12),
            text_color=ModernTheme.TEXT_MUTED
        )
        date_label.pack(side="right")
    
    def _build_form(self):
        """Corps du formulaire."""
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Section A - Identification
        self._build_section_a(scroll)
        
        # Section B - Description
        self._build_section_b(scroll)
        
        # Section C - Analyse
        self._build_section_c(scroll)
        
        # Section D - Clôture
        self._build_section_d(scroll)
    
    def _build_section_a(self, parent):
        """Section A - Identification."""
        section = self._create_section(parent, "🔖 Section A - Identification")
        
        # Ligne 1
        row1 = ctk.CTkFrame(section, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        nc_num = f"NC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self._add_field(row1, "Numéro NC *", nc_num, "numero_nc", readonly=True, side="left")
        self._add_field(row1, "Date de détection *", datetime.now().strftime("%d/%m/%Y"), "date_detection", side="right")
        
        # Ligne 2
        row2 = ctk.CTkFrame(section, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        self._add_field(row2, "Détecté par *", self.user_info.get("nom", ""), "detecte_par", side="left")
        self._add_combo(row2, "Service *", ["Production", "Qualité", "Logistique", "Maintenance", "R&D", "Commercial", "Autre"], "service", side="right")
        
        # Ligne 3
        row3 = ctk.CTkFrame(section, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        
        self._add_combo(row3, "Type de NC *", ["Produit non-conforme", "Process non-conforme", "Réclamation client", "Audit interne", "Autre"], "type_nc", side="left")
        self._add_combo(row3, "Gravité *", ["🟢 Mineure", "🟡 Majeure", "🔴 Critique"], "gravite", side="right")
    
    def _build_section_b(self, parent):
        """Section B - Description."""
        section = self._create_section(parent, "📝 Section B - Description")
        
        lbl = ctk.CTkLabel(section, text="Description détaillée *", font=ctk.CTkFont(size=12, weight="bold"), text_color=ModernTheme.TEXT_PRIMARY)
        lbl.pack(anchor="w", pady=(5, 2))
        
        self.widgets["description"] = ctk.CTkTextbox(section, height=120, corner_radius=10, border_width=1, border_color=ModernTheme.BORDER)
        self.widgets["description"].pack(fill="x", pady=(0, 10))
        
        row = ctk.CTkFrame(section, fg_color="transparent")
        row.pack(fill="x", pady=5)
        
        self._add_field(row, "Référence produit/lot", "", "reference", side="left")
        self._add_field(row, "Quantité affectée", "", "quantite", side="right")
    
    def _build_section_c(self, parent):
        """Section C - Analyse."""
        section = self._create_section(parent, "🔍 Section C - Analyse des causes")
        
        lbl1 = ctk.CTkLabel(section, text="Méthode d'analyse", font=ctk.CTkFont(size=12, weight="bold"), text_color=ModernTheme.TEXT_PRIMARY)
        lbl1.pack(anchor="w", pady=(5, 2))
        
        self.widgets["methode_analyse"] = ctk.CTkComboBox(section, values=["5 Pourquoi", "Ishikawa", "AMDEC", "8D", "Autre"], corner_radius=10)
        self.widgets["methode_analyse"].pack(fill="x", pady=(0, 10))
        
        lbl2 = ctk.CTkLabel(section, text="Causes identifiées", font=ctk.CTkFont(size=12, weight="bold"), text_color=ModernTheme.TEXT_PRIMARY)
        lbl2.pack(anchor="w", pady=(5, 2))
        
        self.widgets["causes"] = ctk.CTkTextbox(section, height=80, corner_radius=10, border_width=1, border_color=ModernTheme.BORDER)
        self.widgets["causes"].pack(fill="x", pady=(0, 10))
        
        lbl3 = ctk.CTkLabel(section, text="Actions correctives", font=ctk.CTkFont(size=12, weight="bold"), text_color=ModernTheme.TEXT_PRIMARY)
        lbl3.pack(anchor="w", pady=(5, 2))
        
        self.widgets["actions_correctives"] = ctk.CTkTextbox(section, height=80, corner_radius=10, border_width=1, border_color=ModernTheme.BORDER)
        self.widgets["actions_correctives"].pack(fill="x", pady=(0, 10))
        
        row = ctk.CTkFrame(section, fg_color="transparent")
        row.pack(fill="x", pady=5)
        
        self._add_field(row, "Responsable des actions", "", "responsable_actions", side="left")
        self._add_field(row, "Délai de mise en œuvre", "", "delai_actions", side="right")
    
    def _build_section_d(self, parent):
        """Section D - Clôture."""
        section = self._create_section(parent, "✅ Section D - Clôture")
        
        lbl1 = ctk.CTkLabel(section, text="Statut", font=ctk.CTkFont(size=12, weight="bold"), text_color=ModernTheme.TEXT_PRIMARY)
        lbl1.pack(anchor="w", pady=(5, 2))
        
        self.widgets["statut"] = ctk.CTkComboBox(section, values=["� En cours", "🟢 Clôturée"], corner_radius=10)
        self.widgets["statut"].set("🟡 En cours")
        self.widgets["statut"].pack(fill="x", pady=(0, 10))
        
        lbl2 = ctk.CTkLabel(section, text="Vérification efficacité", font=ctk.CTkFont(size=12, weight="bold"), text_color=ModernTheme.TEXT_PRIMARY)
        lbl2.pack(anchor="w", pady=(5, 2))
        
        self.widgets["verification"] = ctk.CTkTextbox(section, height=60, corner_radius=10, border_width=1, border_color=ModernTheme.BORDER)
        self.widgets["verification"].pack(fill="x", pady=(0, 10))
        
        row = ctk.CTkFrame(section, fg_color="transparent")
        row.pack(fill="x", pady=5)
        
        self._add_field(row, "Date clôture prévue", "", "date_cloture_prevue", side="left")
        self._add_field(row, "Date clôture effective", "", "date_cloture_effective", side="right")
        
        # Spacer
        ctk.CTkFrame(parent, fg_color="transparent", height=20).pack()
    
    def _build_footer(self):
        """Pied de page."""
        footer = ctk.CTkFrame(self, fg_color=ModernTheme.BG_TERTIARY, height=70)
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_propagate(False)
        
        btn_frame = ctk.CTkFrame(footer, fg_color="transparent")
        btn_frame.pack(expand=True)
        
        ctk.CTkButton(
            btn_frame, text="❌ Annuler", fg_color=ModernTheme.TEXT_MUTED,
            hover_color="#6B7280", width=140, height=40, corner_radius=10,
            command=self.on_cancel
        ).pack(side="left", padx=10, pady=15)
        
        ctk.CTkButton(
            btn_frame, text="✅ Enregistrer", fg_color=ModernTheme.SUCCESS,
            hover_color="#059669", width=160, height=40, corner_radius=10,
            command=self._save
        ).pack(side="left", padx=10, pady=15)
    
    def _create_section(self, parent, title: str):
        """Crée une section de formulaire."""
        frame = ctk.CTkFrame(parent, fg_color=ModernTheme.BG_SECONDARY, corner_radius=12)
        frame.pack(fill="x", padx=10, pady=8)
        
        header = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color=ModernTheme.PRIMARY)
        header.pack(anchor="w", padx=15, pady=(12, 5))
        
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=(0, 15))
        
        return content
    
    def _add_field(self, parent, label: str, default: str, key: str, readonly: bool = False, side: str = "left"):
        """Ajoute un champ."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side=side, fill="x", expand=True, padx=5)
        
        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11, weight="bold"), text_color=ModernTheme.TEXT_SECONDARY).pack(anchor="w")
        
        entry = ctk.CTkEntry(frame, corner_radius=8, border_width=1, border_color=ModernTheme.BORDER)
        if default:
            entry.insert(0, default)
        if readonly:
            entry.configure(state="disabled")
        entry.pack(fill="x", pady=(2, 0))
        
        self.widgets[key] = entry
    
    def _add_combo(self, parent, label: str, values: list, key: str, side: str = "left"):
        """Ajoute un combo."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(side=side, fill="x", expand=True, padx=5)
        
        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11, weight="bold"), text_color=ModernTheme.TEXT_SECONDARY).pack(anchor="w")
        
        combo = ctk.CTkComboBox(frame, values=values, corner_radius=8)
        combo.pack(fill="x", pady=(2, 0))
        
        self.widgets[key] = combo
    
    def _get_value(self, key: str) -> str:
        """Récupère une valeur."""
        w = self.widgets.get(key)
        if w is None:
            return ""
        if isinstance(w, ctk.CTkEntry):
            return w.get()
        elif isinstance(w, ctk.CTkComboBox):
            return w.get()
        elif isinstance(w, ctk.CTkTextbox):
            return w.get("1.0", "end-1c")
        return ""
    
    def _save(self):
        """Sauvegarde."""
        # Validation
        required = ["numero_nc", "date_detection", "detecte_par", "service", "type_nc", "gravite", "description"]
        for key in required:
            if not self._get_value(key).strip():
                self._show_error(f"Le champ est requis")
                return
        
        data = {k: self._get_value(k) for k in self.widgets.keys()}
        self.on_save(data)
    
    def _show_error(self, msg: str):
        """Affiche une erreur."""
        popup = ctk.CTkToplevel(self)
        popup.title("Erreur")
        popup.geometry("300x120")
        popup.transient(self)
        popup.grab_set()
        
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() - 300) // 2
        y = (popup.winfo_screenheight() - 120) // 2
        popup.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(popup, text="⚠️", font=ctk.CTkFont(size=30)).pack(pady=(15, 5))
        ctk.CTkLabel(popup, text=msg, font=ctk.CTkFont(size=12)).pack()
        ctk.CTkButton(popup, text="OK", width=80, command=popup.destroy).pack(pady=10)

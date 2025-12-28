# -*- coding: utf-8 -*-
"""
Formulaire de Signalement simplifié
Chargement instantané
"""

import customtkinter as ctk
from datetime import datetime
from typing import Callable, Dict, Any
from .utils import ModernTheme


class SignalementForm(ctk.CTkFrame):
    """Formulaire de signalement simplifié."""
    
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
        """En-tête."""
        header = ctk.CTkFrame(self, fg_color="transparent", height=80)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        header.grid_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="🚨 Signalement Rapide",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=ModernTheme.TEXT_PRIMARY
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            header,
            text="Signalez un problème qualité en quelques clics",
            font=ctk.CTkFont(size=13),
            text_color=ModernTheme.TEXT_MUTED
        )
        subtitle.pack(anchor="w", pady=(5, 0))
    
    def _build_form(self):
        """Corps du formulaire."""
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)
        
        # Bannière info
        banner = ctk.CTkFrame(scroll, fg_color=ModernTheme.INFO_LIGHT, corner_radius=10)
        banner.pack(fill="x", padx=10, pady=(0, 15))
        
        banner_content = ctk.CTkFrame(banner, fg_color="transparent")
        banner_content.pack(fill="x", padx=15, pady=12)
        
        ctk.CTkLabel(banner_content, text="💡", font=ctk.CTkFont(size=18)).pack(side="left")
        ctk.CTkLabel(
            banner_content,
            text="  Ce formulaire simplifié permet de signaler rapidement un problème.\n  Un responsable qualité complétera l'analyse.",
            font=ctk.CTkFont(size=11),
            text_color=ModernTheme.INFO,
            justify="left"
        ).pack(side="left")
        
        # Section Identification
        section1 = self._create_section(scroll, "🔖 Identification")
        
        row1 = ctk.CTkFrame(section1, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        nc_num = f"SIG-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self._add_field(row1, "Numéro *", nc_num, "numero_nc", readonly=True, side="left")
        self._add_field(row1, "Date *", datetime.now().strftime("%d/%m/%Y"), "date_detection", readonly=True, side="right")
        
        row2 = ctk.CTkFrame(section1, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        self._add_field(row2, "Signalé par *", self.user_info.get("nom", ""), "detecte_par", readonly=True, side="left")
        self._add_combo(row2, "Service *", ["Production", "Qualité", "Logistique", "Maintenance", "R&D", "Commercial", "Autre"], "service", side="right")
        
        row3 = ctk.CTkFrame(section1, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        
        self._add_combo(row3, "Type de problème *", ["Produit défectueux", "Problème process", "Réclamation client", "Anomalie détectée", "Autre"], "type_nc", side="left")
        self._add_combo(row3, "Urgence *", ["🟢 Faible", "🟡 Moyenne", "🔴 Haute"], "gravite", side="right")
        
        # Section Description
        section2 = self._create_section(scroll, "📝 Description du problème")
        
        lbl = ctk.CTkLabel(section2, text="Décrivez le problème *", font=ctk.CTkFont(size=12, weight="bold"), text_color=ModernTheme.TEXT_PRIMARY)
        lbl.pack(anchor="w", pady=(5, 2))
        
        hint = ctk.CTkLabel(section2, text="Soyez le plus précis possible : quoi, où, quand, comment ?", font=ctk.CTkFont(size=10), text_color=ModernTheme.TEXT_MUTED)
        hint.pack(anchor="w", pady=(0, 5))
        
        self.widgets["description"] = ctk.CTkTextbox(section2, height=150, corner_radius=10, border_width=1, border_color=ModernTheme.BORDER)
        self.widgets["description"].pack(fill="x", pady=(0, 10))
        
        row4 = ctk.CTkFrame(section2, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        
        self._add_field(row4, "Référence produit/lot (optionnel)", "", "reference", side="left")
        self._add_field(row4, "Quantité concernée (optionnel)", "", "quantite", side="right")
        
        # Spacer
        ctk.CTkFrame(scroll, fg_color="transparent", height=20).pack()
    
    def _build_footer(self):
        """Pied de page."""
        footer = ctk.CTkFrame(self, fg_color=ModernTheme.BG_TERTIARY, height=80)
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_propagate(False)
        
        btn_frame = ctk.CTkFrame(footer, fg_color="transparent")
        btn_frame.pack(expand=True)
        
        ctk.CTkButton(
            btn_frame, text="❌ Annuler", fg_color=ModernTheme.TEXT_MUTED,
            hover_color="#6B7280", width=150, height=45, corner_radius=10,
            command=self.on_cancel
        ).pack(side="left", padx=15, pady=18)
        
        ctk.CTkButton(
            btn_frame, text="📤 Envoyer le signalement", fg_color=ModernTheme.PRIMARY,
            hover_color="#2563EB", width=200, height=45, corner_radius=10,
            command=self._save
        ).pack(side="left", padx=15, pady=18)
    
    def _create_section(self, parent, title: str):
        """Crée une section."""
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
        required = ["service", "type_nc", "gravite", "description"]
        for key in required:
            if not self._get_value(key).strip():
                self._show_error("Veuillez remplir tous les champs obligatoires")
                return
        
        data = {
            "numero_nc": self._get_value("numero_nc"),
            "date_detection": self._get_value("date_detection"),
            "detecte_par": self._get_value("detecte_par"),
            "service": self._get_value("service"),
            "type_nc": self._get_value("type_nc"),
            "gravite": self._get_value("gravite"),
            "description": self._get_value("description"),
            "reference": self._get_value("reference"),
            "quantite": self._get_value("quantite"),
            "statut": "� En cours",
            "is_signalement": True
        }
        
        self.on_save(data)
    
    def _show_error(self, msg: str):
        """Affiche une erreur."""
        popup = ctk.CTkToplevel(self)
        popup.title("Attention")
        popup.geometry("320x130")
        popup.transient(self)
        popup.grab_set()
        
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() - 320) // 2
        y = (popup.winfo_screenheight() - 130) // 2
        popup.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(popup, text="⚠️", font=ctk.CTkFont(size=30)).pack(pady=(15, 5))
        ctk.CTkLabel(popup, text=msg, font=ctk.CTkFont(size=12)).pack()
        ctk.CTkButton(popup, text="OK", width=80, command=popup.destroy).pack(pady=10)

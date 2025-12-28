# -*- coding: utf-8 -*-
"""
QualiManager - Page d'accueil
Dashboard avec chargement instantané
"""

import customtkinter as ctk
from typing import Callable, Dict, Any
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import get_statistics
from .utils import ModernTheme


class HomePage(ctk.CTkFrame):
    """Page d'accueil avec affichage instantané."""
    
    def __init__(self, parent, user_info: Dict[str, Any] = None, on_navigate: Callable = None, **kwargs):
        # Nettoyer les kwargs pour éviter les conflits
        kwargs.pop('current_user', None)
        super().__init__(parent, fg_color=ModernTheme.BG_PRIMARY, **kwargs)
        
        self.user_info = user_info or {}
        self.on_navigate = on_navigate
        
        # Charger les stats immédiatement
        try:
            self.stats = get_statistics()
        except:
            self.stats = {'total': 0, 'ouvertes': 0, 'soldees': 0}
        
        # Configuration du layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Construction immédiate de l'UI
        self._build_header()
        self._build_content()
    
    def _build_header(self):
        """Construit l'en-tête."""
        header = ctk.CTkFrame(self, fg_color="transparent", height=100)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 15))
        header.grid_propagate(False)
        
        # Salutation
        hour = datetime.now().hour
        if hour < 12:
            greeting = "🌅 Bonjour"
        elif hour < 18:
            greeting = "☀️ Bon après-midi"
        else:
            greeting = "🌙 Bonsoir"
        
        prenom = self.user_info.get('nom', 'Utilisateur').split()[0] if self.user_info.get('nom') else 'Utilisateur'
        
        title = ctk.CTkLabel(
            header,
            text=f"{greeting}, {prenom} !",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=ModernTheme.TEXT_PRIMARY
        )
        title.pack(anchor="w")
        
        # Rôle et date
        info_frame = ctk.CTkFrame(header, fg_color="transparent")
        info_frame.pack(anchor="w", pady=(8, 0))
        
        role = self.user_info.get('role', 'Utilisateur')
        role_colors = {
            "Administrateur": ModernTheme.DANGER,
            "Responsable": ModernTheme.WARNING,
            "Utilisateur": ModernTheme.INFO
        }
        
        role_badge = ctk.CTkLabel(
            info_frame,
            text=f"  {role}  ",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=role_colors.get(role, ModernTheme.PRIMARY),
            corner_radius=5,
            text_color="white"
        )
        role_badge.pack(side="left")
        
        date_label = ctk.CTkLabel(
            info_frame,
            text=f"   📅 {datetime.now().strftime('%d/%m/%Y')}",
            font=ctk.CTkFont(size=12),
            text_color=ModernTheme.TEXT_MUTED
        )
        date_label.pack(side="left")
    
    def _build_content(self):
        """Construit le contenu principal."""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 25))
        content.grid_columnconfigure((0, 1, 2, 3), weight=1)
        content.grid_rowconfigure(1, weight=1)
        
        # === CARTES STATISTIQUES ===
        stats_data = [
            ("📊", "Total NC", str(self.stats.get('total', 0)), ModernTheme.PRIMARY),
            ("�", "En cours", str(self.stats.get('en_cours', 0)), ModernTheme.WARNING),
            ("🟡", "En cours", str(self.stats.get('en_cours', 0)), ModernTheme.WARNING),
            ("🟢", "Clôturées", str(self.stats.get('soldees', 0)), ModernTheme.SUCCESS),
        ]
        
        for i, (icon, title, value, color) in enumerate(stats_data):
            card = self._create_stat_card(content, icon, title, value, color)
            card.grid(row=0, column=i, padx=8, pady=(0, 20), sticky="nsew")
        
        # === SECTION INFÉRIEURE ===
        bottom_frame = ctk.CTkFrame(content, fg_color="transparent")
        bottom_frame.grid(row=1, column=0, columnspan=4, sticky="nsew")
        bottom_frame.grid_columnconfigure(0, weight=2)
        bottom_frame.grid_columnconfigure(1, weight=1)
        bottom_frame.grid_rowconfigure(0, weight=1)
        
        # Actions rapides
        self._build_quick_actions(bottom_frame)
        
        # Infos système
        self._build_system_info(bottom_frame)
    
    def _create_stat_card(self, parent, icon: str, title: str, value: str, color: str):
        """Crée une carte de statistique."""
        card = ctk.CTkFrame(
            parent,
            fg_color=ModernTheme.BG_SECONDARY,
            corner_radius=15,
            border_width=1,
            border_color=ModernTheme.BORDER
        )
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Icône
        icon_lbl = ctk.CTkLabel(inner, text=icon, font=ctk.CTkFont(size=32))
        icon_lbl.pack()
        
        # Valeur
        value_lbl = ctk.CTkLabel(
            inner,
            text=value,
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=color
        )
        value_lbl.pack(pady=(5, 0))
        
        # Titre
        title_lbl = ctk.CTkLabel(
            inner,
            text=title,
            font=ctk.CTkFont(size=13),
            text_color=ModernTheme.TEXT_MUTED
        )
        title_lbl.pack()
        
        # Effet hover
        def on_enter(e):
            card.configure(border_color=color)
        def on_leave(e):
            card.configure(border_color=ModernTheme.BORDER)
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        for child in [inner, icon_lbl, value_lbl, title_lbl]:
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)
        
        return card
    
    def _build_quick_actions(self, parent):
        """Construit les actions rapides."""
        frame = ctk.CTkFrame(
            parent,
            fg_color=ModernTheme.BG_SECONDARY,
            corner_radius=15
        )
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        
        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Titre
        title = ctk.CTkLabel(
            inner,
            text="⚡ Actions rapides",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ModernTheme.TEXT_PRIMARY
        )
        title.pack(anchor="w", pady=(0, 15))
        
        role = self.user_info.get('role', 'Utilisateur')
        
        # Boutons d'action selon le rôle
        actions = []
        
        if role in ["Administrateur", "Responsable"]:
            actions.append(("➕ Nouvelle NC", "nouvelle_nc", ModernTheme.PRIMARY))
        
        actions.append(("🚨 Signaler un problème", "signalement", ModernTheme.WARNING))
        actions.append(("📋 Voir les NC", "liste_nc", ModernTheme.INFO))
        
        if role == "Administrateur":
            actions.append(("👥 Gérer les utilisateurs", "admin_users", ModernTheme.SECONDARY))
        
        for text, page_id, color in actions:
            btn = ctk.CTkButton(
                inner,
                text=text,
                font=ctk.CTkFont(size=14),
                fg_color=color,
                hover_color=self._darken(color),
                height=45,
                corner_radius=10,
                anchor="w",
                command=lambda p=page_id: self.on_navigate(p) if self.on_navigate else None
            )
            btn.pack(fill="x", pady=5)
    
    def _build_system_info(self, parent):
        """Construit les infos système."""
        frame = ctk.CTkFrame(
            parent,
            fg_color=ModernTheme.BG_SECONDARY,
            corner_radius=15
        )
        frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        
        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Titre
        title = ctk.CTkLabel(
            inner,
            text="ℹ️ Informations",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ModernTheme.TEXT_PRIMARY
        )
        title.pack(anchor="w", pady=(0, 15))
        
        # Infos
        infos = [
            ("🏭", "QualiManager v1.1"),
            ("💾", "Base locale SQLite"),
            ("🔐", "Session active"),
            ("📧", self.user_info.get('email', 'N/A')[:25]),
        ]
        
        for icon, text in infos:
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(fill="x", pady=4)
            
            ctk.CTkLabel(
                row,
                text=icon,
                font=ctk.CTkFont(size=14)
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=f"  {text}",
                font=ctk.CTkFont(size=12),
                text_color=ModernTheme.TEXT_SECONDARY
            ).pack(side="left")
    
    def _darken(self, color: str) -> str:
        """Assombrit une couleur."""
        darken_map = {
            ModernTheme.PRIMARY: "#2563EB",
            ModernTheme.SUCCESS: "#059669",
            ModernTheme.WARNING: "#D97706",
            ModernTheme.DANGER: "#DC2626",
            ModernTheme.INFO: "#0891B2",
            ModernTheme.SECONDARY: "#4F46E5"
        }
        return darken_map.get(color, color)

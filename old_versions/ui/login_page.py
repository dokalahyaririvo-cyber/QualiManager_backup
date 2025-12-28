# -*- coding: utf-8 -*-
"""
Page de connexion - Version Optimisée
Interface moderne avec animations fluides
"""

import customtkinter as ctk
from typing import Callable
from .utils import ModernTheme, ModernButton, ModernEntry


class LoginPage(ctk.CTkFrame):
    """Page de connexion moderne et animée"""
    
    def __init__(self, parent, on_login_success: Callable):
        super().__init__(parent, fg_color=ModernTheme.BG_PRIMARY)
        self.on_login_success = on_login_success
        self.auth_manager = None
        
        # Construction immédiate (page légère)
        self._create_ui()
        
        # Animation d'entrée
        self.after(50, self._animate_in)
    
    def set_auth_manager(self, auth_manager):
        """Configure le gestionnaire d'authentification"""
        self.auth_manager = auth_manager
    
    def _create_ui(self):
        """Crée l'interface de connexion"""
        # Conteneur principal centré
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Carte de connexion avec ombre visuelle
        self.card = ctk.CTkFrame(
            self.main_container,
            fg_color=ModernTheme.BG_SECONDARY,
            corner_radius=20,
            border_width=1,
            border_color=ModernTheme.BG_TERTIARY
        )
        self.card.pack(padx=40, pady=40)
        
        # Contenu de la carte
        content = ctk.CTkFrame(self.card, fg_color="transparent")
        content.pack(padx=50, pady=40)
        
        # Logo / Icône
        logo_frame = ctk.CTkFrame(content, fg_color="transparent")
        logo_frame.pack(pady=(0, 20))
        
        logo = ctk.CTkLabel(
            logo_frame,
            text="🏭",
            font=ctk.CTkFont(size=60)
        )
        logo.pack()
        
        # Titre de l'application
        title = ctk.CTkLabel(
            content,
            text="QualiManager",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=ModernTheme.PRIMARY
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            content,
            text="Système de Management de la Qualité",
            font=ctk.CTkFont(size=13),
            text_color=ModernTheme.TEXT_MUTED
        )
        subtitle.pack(pady=(5, 30))
        
        # Séparateur
        separator = ctk.CTkFrame(content, fg_color=ModernTheme.BG_TERTIARY, height=1)
        separator.pack(fill="x", pady=10)
        
        # Titre connexion
        login_title = ctk.CTkLabel(
            content,
            text="Connexion",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ModernTheme.TEXT_PRIMARY
        )
        login_title.pack(pady=(20, 15))
        
        # Champ Email
        email_label = ctk.CTkLabel(
            content,
            text="📧 Adresse email",
            font=ctk.CTkFont(size=12),
            text_color=ModernTheme.TEXT_SECONDARY,
            anchor="w"
        )
        email_label.pack(fill="x", pady=(0, 5))
        
        self.email_entry = ModernEntry(
            content,
            placeholder_text="votre@email.com",
            width=320,
            height=45
        )
        self.email_entry.pack(fill="x")
        
        # Champ Mot de passe
        pwd_label = ctk.CTkLabel(
            content,
            text="🔒 Mot de passe",
            font=ctk.CTkFont(size=12),
            text_color=ModernTheme.TEXT_SECONDARY,
            anchor="w"
        )
        pwd_label.pack(fill="x", pady=(20, 5))
        
        self.password_entry = ModernEntry(
            content,
            placeholder_text="••••••••",
            show="•",
            width=320,
            height=45
        )
        self.password_entry.pack(fill="x")
        
        # Message d'erreur (caché par défaut)
        self.error_label = ctk.CTkLabel(
            content,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=ModernTheme.DANGER,
            height=25
        )
        self.error_label.pack(pady=(15, 0))
        
        # Bouton de connexion
        self.login_btn = ModernButton(
            content,
            text="Se connecter",
            style="primary",
            command=self._handle_login,
            width=320,
            height=50
        )
        self.login_btn.pack(pady=(10, 0))
        
        # Indicateur de chargement (caché)
        self.loading_label = ctk.CTkLabel(
            content,
            text="⏳ Connexion en cours...",
            font=ctk.CTkFont(size=12),
            text_color=ModernTheme.INFO
        )
        
        # Info admin par défaut
        info_frame = ctk.CTkFrame(
            content,
            fg_color=ModernTheme.INFO_LIGHT,
            corner_radius=8
        )
        info_frame.pack(fill="x", pady=(25, 0))
        
        info_content = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_content.pack(padx=15, pady=12)
        
        info_icon = ctk.CTkLabel(
            info_content,
            text="💡",
            font=ctk.CTkFont(size=14)
        )
        info_icon.pack(side="left", padx=(0, 8))
        
        info_text = ctk.CTkLabel(
            info_content,
            text="Compte admin par défaut :\nadmin@qualimanager.local / Admin@2024!",
            font=ctk.CTkFont(size=11),
            text_color=ModernTheme.INFO,
            justify="left"
        )
        info_text.pack(side="left")
        
        # Bind Enter pour valider
        self.email_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self._handle_login())
        
        # Footer
        footer = ctk.CTkLabel(
            self,
            text="© 2024 QualiManager - Version 1.0",
            font=ctk.CTkFont(size=10),
            text_color=ModernTheme.TEXT_MUTED
        )
        footer.pack(side="bottom", pady=15)
    
    def _animate_in(self):
        """Animation d'entrée"""
        # Focus sur le champ email
        self.email_entry.focus()
    
    def _handle_login(self):
        """Gère la tentative de connexion"""
        if not self.auth_manager:
            self.error_label.configure(text="Erreur de configuration")
            return
        
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        
        # Validation basique
        if not email:
            self._show_error("Veuillez saisir votre email")
            self.email_entry.focus()
            return
        
        if not password:
            self._show_error("Veuillez saisir votre mot de passe")
            self.password_entry.focus()
            return
        
        # Afficher le chargement
        self._show_loading(True)
        
        # Authentification (avec délai simulé pour l'UX)
        self.after(300, lambda: self._do_login(email, password))
    
    def _do_login(self, email: str, password: str):
        """Effectue l'authentification"""
        success, result = self.auth_manager.authentifier(email, password)
        
        self._show_loading(False)
        
        if success:
            # Animation de succès rapide
            self.login_btn.configure(text="✅ Connecté !")
            self.after(500, lambda: self.on_login_success(result))
        else:
            self._show_error(result)
            self.password_entry.delete(0, "end")
            self.password_entry.focus()
            self._shake_animation()
    
    def _show_error(self, message: str):
        """Affiche un message d'erreur"""
        self.error_label.configure(text=f"❌ {message}")
    
    def _show_loading(self, show: bool):
        """Affiche/masque l'indicateur de chargement"""
        if show:
            self.login_btn.configure(state="disabled", text="⏳ Connexion...")
        else:
            self.login_btn.configure(state="normal", text="Se connecter")
    
    def _shake_animation(self):
        """Animation de secousse en cas d'erreur"""
        original_x = self.card.winfo_x()
        
        def shake(offset, count):
            if count > 0:
                self.card.place(x=original_x + offset)
                self.after(50, lambda: shake(-offset, count - 1))
            else:
                self.card.place(x=original_x)
        
        # Animation simple de décalage
        shake(5, 6)
    
    def reset(self):
        """Réinitialise le formulaire"""
        self.email_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.error_label.configure(text="")
        self.login_btn.configure(text="Se connecter", state="normal")
        self.email_entry.focus()

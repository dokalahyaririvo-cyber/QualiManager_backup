# -*- coding: utf-8 -*-
"""
QualiManager - Application principale optimisée
Système de Management de la Qualité (SMQ) On-Premise
Version: 1.1.0 - Interface moderne et fluide

Système d'authentification avec 3 niveaux d'accès:
- Administrateur: Gestion complète + comptes utilisateurs
- Responsable: Gestion complète des NC
- Utilisateur: Lecture + Signalement simplifié
"""

import customtkinter as ctk
from tkinter import messagebox
import os
import sys
from typing import Optional, Dict, Any

# Ajout du chemin pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import init_database, get_statistics, insert_non_conformite
from database.auth_manager import AuthManager
from ui.utils import ModernTheme
from ui.login_page import LoginPage
from ui.home_page import HomePage
from ui.nc_form import NCForm
from ui.admin_users_page import AdminUsersPage
from ui.signalement_form import SignalementForm


class QualiManagerApp(ctk.CTk):
    """Application principale QualiManager avec UI moderne et fluide."""
    
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre
        self.title("QualiManager - Système de Management de la Qualité")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Centrer la fenêtre
        self._center_window()
        
        # Initialiser les bases de données
        init_database()
        
        # Gestionnaire d'authentification
        self.auth_manager = AuthManager()
        
        # Configuration de l'apparence
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Variables d'état
        self.current_user: Optional[Dict[str, Any]] = None
        self.current_frame = None
        self.sidebar = None
        self.main_container = None
        self.nav_buttons = {}
        
        # Optimisation: désactiver le redraw pendant le chargement
        self.update_idletasks()
        
        # Afficher la page de connexion
        self.after(100, self._show_login)
    
    def _center_window(self):
        """Centre la fenêtre sur l'écran."""
        self.update_idletasks()
        width = 1400
        height = 900
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _show_login(self):
        """Affiche la page de connexion."""
        # Nettoyer
        for widget in self.winfo_children():
            widget.destroy()
        
        self.sidebar = None
        self.main_container = None
        self.current_frame = None
        self.nav_buttons = {}
        
        # Grid simple pour centrage
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Page de connexion
        login_page = LoginPage(self, on_login_success=self._on_login_success)
        login_page.set_auth_manager(self.auth_manager)
        login_page.grid(row=0, column=0, sticky="nsew")
    
    def _on_login_success(self, user: Dict[str, Any]):
        """Callback après connexion réussie."""
        self.current_user = user
        print(f"✅ Connexion: {user.get('nom', '')} ({user.get('role', '')})")
        
        # Transition fluide
        self.after(100, self._show_main_interface)
    
    def _show_main_interface(self):
        """Affiche l'interface principale."""
        # Nettoyer
        for widget in self.winfo_children():
            widget.destroy()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Créer la sidebar en premier (elle est légère)
        self._create_sidebar()
        
        # Conteneur principal
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Navigation vers l'accueil
        self.after(50, lambda: self._navigate_to("accueil"))
    
    def _create_sidebar(self):
        """Crée la sidebar moderne."""
        self.sidebar = ctk.CTkFrame(
            self, 
            width=270, 
            corner_radius=0, 
            fg_color=ModernTheme.SIDEBAR_BG
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(10, weight=1)
        
        # Header
        self._create_sidebar_header()
        
        # User info
        self._create_user_section()
        
        # Navigation
        self._create_navigation()
        
        # Footer
        self._create_sidebar_footer()
    
    def _create_sidebar_header(self):
        """En-tête sidebar."""
        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.grid(row=0, column=0, pady=(25, 15), padx=20, sticky="ew")
        
        # Logo
        logo = ctk.CTkLabel(header, text="🏭", font=ctk.CTkFont(size=50))
        logo.pack()
        
        # Titre
        title = ctk.CTkLabel(
            header,
            text="QualiManager",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        title.pack(pady=(5, 0))
        
        version = ctk.CTkLabel(
            header,
            text="v1.1.0 • SMQ On-Premise",
            font=ctk.CTkFont(size=10),
            text_color=ModernTheme.SIDEBAR_TEXT_MUTED
        )
        version.pack()
    
    def _create_user_section(self):
        """Section utilisateur."""
        # Séparateur
        ctk.CTkFrame(
            self.sidebar, 
            height=1, 
            fg_color=ModernTheme.SIDEBAR_SEPARATOR
        ).grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        # Cadre utilisateur
        user_frame = ctk.CTkFrame(
            self.sidebar, 
            fg_color=ModernTheme.SIDEBAR_HOVER,
            corner_radius=12
        )
        user_frame.grid(row=2, column=0, padx=15, pady=5, sticky="ew")
        
        content = ctk.CTkFrame(user_frame, fg_color="transparent")
        content.pack(padx=15, pady=12, fill="x")
        
        # Avatar
        avatar = ctk.CTkLabel(
            content,
            text="👤",
            font=ctk.CTkFont(size=28)
        )
        avatar.pack(side="left", padx=(0, 10))
        
        # Info
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        name = self.current_user.get('nom', 'Utilisateur')
        name_label = ctk.CTkLabel(
            info_frame,
            text=name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white",
            anchor="w"
        )
        name_label.pack(fill="x")
        
        role = self.current_user.get('role', 'Utilisateur')
        role_colors = {
            "Administrateur": ModernTheme.DANGER,
            "Responsable": ModernTheme.WARNING,
            "Utilisateur": ModernTheme.INFO
        }
        
        role_label = ctk.CTkLabel(
            info_frame,
            text=f"🔑 {role}",
            font=ctk.CTkFont(size=11),
            text_color=role_colors.get(role, ModernTheme.INFO),
            anchor="w"
        )
        role_label.pack(fill="x")
        
        # Séparateur
        ctk.CTkFrame(
            self.sidebar, 
            height=1, 
            fg_color=ModernTheme.SIDEBAR_SEPARATOR
        ).grid(row=3, column=0, sticky="ew", padx=20, pady=10)
    
    def _create_navigation(self):
        """Crée les boutons de navigation."""
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.grid(row=4, column=0, sticky="ew", padx=10)
        
        self.nav_buttons = {}
        role = self.current_user.get('role', 'Utilisateur')
        
        # Accueil (tous)
        self.nav_buttons['accueil'] = self._create_nav_btn(nav_frame, "🏠", "Accueil", "accueil")
        
        if role == "Administrateur":
            self._create_section_label(nav_frame, "ADMINISTRATION")
            self.nav_buttons['admin_users'] = self._create_nav_btn(nav_frame, "👥", "Gestion des comptes", "admin_users")
            
            self._create_section_label(nav_frame, "QUALITÉ")
            self.nav_buttons['nouvelle_nc'] = self._create_nav_btn(nav_frame, "➕", "Nouvelle NC", "nouvelle_nc")
            self.nav_buttons['liste_nc'] = self._create_nav_btn(nav_frame, "📋", "Liste des NC", "liste_nc")
        
        elif role == "Responsable":
            self._create_section_label(nav_frame, "QUALITÉ")
            self.nav_buttons['nouvelle_nc'] = self._create_nav_btn(nav_frame, "➕", "Nouvelle NC", "nouvelle_nc")
            self.nav_buttons['signalement'] = self._create_nav_btn(nav_frame, "🚨", "Signalement rapide", "signalement")
            self.nav_buttons['liste_nc'] = self._create_nav_btn(nav_frame, "📋", "Liste des NC", "liste_nc")
        
        else:  # Utilisateur
            self._create_section_label(nav_frame, "SIGNALEMENT")
            self.nav_buttons['signalement'] = self._create_nav_btn(nav_frame, "🚨", "Signaler une NC", "signalement")
            
            self._create_section_label(nav_frame, "CONSULTATION")
            self.nav_buttons['liste_nc'] = self._create_nav_btn(nav_frame, "📋", "Voir les NC", "liste_nc")
    
    def _create_section_label(self, parent, text: str):
        """Label de section."""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=ModernTheme.SIDEBAR_TEXT_MUTED
        )
        label.pack(anchor="w", padx=15, pady=(18, 5))
    
    def _create_nav_btn(self, parent, icon: str, text: str, page_id: str) -> ctk.CTkButton:
        """Crée un bouton de navigation moderne."""
        btn = ctk.CTkButton(
            parent,
            text=f"{icon}  {text}",
            command=lambda: self._navigate_to(page_id),
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color=ModernTheme.SIDEBAR_HOVER,
            text_color="white",
            anchor="w",
            height=44,
            corner_radius=10
        )
        btn.pack(fill="x", pady=2, padx=5)
        return btn
    
    def _create_sidebar_footer(self):
        """Footer sidebar."""
        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.grid(row=11, column=0, pady=15, padx=10, sticky="sew")
        
        # Thème
        theme_frame = ctk.CTkFrame(footer, fg_color="transparent")
        theme_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="🎨 Thème",
            font=ctk.CTkFont(size=11),
            text_color=ModernTheme.SIDEBAR_TEXT_MUTED
        )
        theme_label.pack(anchor="w")
        
        self.theme_menu = ctk.CTkSegmentedButton(
            theme_frame,
            values=["☀️", "🌙", "💻"],
            command=self._change_theme,
            font=ctk.CTkFont(size=14),
            fg_color=ModernTheme.SIDEBAR_HOVER,
            selected_color=ModernTheme.PRIMARY,
            selected_hover_color=ModernTheme.PRIMARY_HOVER,
            unselected_color=ModernTheme.SIDEBAR_HOVER,
            unselected_hover_color=ModernTheme.SIDEBAR_SEPARATOR
        )
        self.theme_menu.pack(fill="x", pady=5)
        self.theme_menu.set("☀️")
        
        # Déconnexion
        logout_btn = ctk.CTkButton(
            footer,
            text="🚪 Déconnexion",
            command=self._logout,
            fg_color=ModernTheme.DANGER,
            hover_color="#c0392b",
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        logout_btn.pack(fill="x", padx=10, pady=(10, 5))
    
    def _change_theme(self, value: str):
        """Change le thème."""
        themes = {"☀️": "light", "🌙": "dark", "💻": "system"}
        ctk.set_appearance_mode(themes.get(value, "light"))
    
    def _logout(self):
        """Déconnexion."""
        if messagebox.askyesno("Déconnexion", "Voulez-vous vraiment vous déconnecter ?"):
            self.current_user = None
            self._show_login()
    
    def _navigate_to(self, page_id: str):
        """Navigation vers une page."""
        # Highlight bouton actif
        for pid, btn in self.nav_buttons.items():
            if pid == page_id:
                btn.configure(fg_color=ModernTheme.SIDEBAR_HOVER)
            else:
                btn.configure(fg_color="transparent")
        
        # Détruire page actuelle
        if self.current_frame:
            self.current_frame.destroy()
        
        # Créer nouvelle page
        if page_id == "accueil":
            self._show_home()
        elif page_id == "admin_users":
            self._show_admin_users()
        elif page_id == "nouvelle_nc":
            self._show_nc_form()
        elif page_id == "signalement":
            self._show_signalement()
        elif page_id == "liste_nc":
            self._show_nc_list()
    
    def _show_home(self):
        """Page d'accueil."""
        self.current_frame = HomePage(
            self.main_container,
            user_info=self.current_user,
            on_navigate=self._navigate_to
        )
        self.current_frame.grid(row=0, column=0, sticky="nsew")
    
    def _show_admin_users(self):
        """Page admin utilisateurs."""
        role = self.current_user.get('role', '')
        if role != "Administrateur":
            messagebox.showerror("Accès refusé", "Réservé aux administrateurs")
            self._navigate_to("accueil")
            return
        
        self.current_frame = AdminUsersPage(
            self.main_container,
            auth_manager=self.auth_manager,
            on_back=lambda: self._navigate_to("accueil")
        )
        self.current_frame.grid(row=0, column=0, sticky="nsew")
    
    def _show_nc_form(self):
        """Formulaire NC complet."""
        role = self.current_user.get('role', '')
        if role not in ["Administrateur", "Responsable"]:
            messagebox.showerror("Accès refusé", "Utilisez le signalement rapide")
            self._navigate_to("signalement")
            return
        
        self.current_frame = NCForm(
            self.main_container,
            on_save=self._on_nc_saved,
            on_cancel=lambda: self._navigate_to("accueil"),
            user_info=self.current_user
        )
        self.current_frame.grid(row=0, column=0, sticky="nsew")
    
    def _show_signalement(self):
        """Formulaire signalement."""
        self.current_frame = SignalementForm(
            self.main_container,
            on_save=self._on_nc_saved,
            on_cancel=lambda: self._navigate_to("accueil"),
            user_info=self.current_user
        )
        self.current_frame.grid(row=0, column=0, sticky="nsew")
    
    def _show_nc_list(self):
        """Liste des NC (placeholder)."""
        self.current_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.current_frame.grid(row=0, column=0, sticky="nsew")
        
        # Card placeholder
        card = ctk.CTkFrame(
            self.current_frame,
            fg_color=ModernTheme.BG_SECONDARY,
            corner_radius=15
        )
        card.pack(expand=True, padx=50, pady=50)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(padx=60, pady=60)
        
        icon = ctk.CTkLabel(content, text="🚧", font=ctk.CTkFont(size=60))
        icon.pack(pady=(0, 20))
        
        title = ctk.CTkLabel(
            content,
            text="Liste des Non-Conformités",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=ModernTheme.TEXT_PRIMARY
        )
        title.pack()
        
        msg = ctk.CTkLabel(
            content,
            text="Ce module est en cours de développement.\n\n"
                 "Il permettra de consulter, filtrer et exporter\n"
                 "toutes les non-conformités enregistrées.",
            font=ctk.CTkFont(size=14),
            text_color=ModernTheme.TEXT_MUTED,
            justify="center"
        )
        msg.pack(pady=20)
        
        back_btn = ctk.CTkButton(
            content,
            text="← Retour à l'accueil",
            command=lambda: self._navigate_to("accueil"),
            fg_color=ModernTheme.PRIMARY,
            hover_color=ModernTheme.PRIMARY_HOVER,
            height=40,
            corner_radius=10
        )
        back_btn.pack(pady=10)
    
    def _on_nc_saved(self, data: dict):
        """Callback sauvegarde NC."""
        try:
            nc_id = insert_non_conformite(data)
            print(f"✅ NC #{nc_id} enregistrée")
            
            # Message de succès
            self._show_success_message(f"NC #{data.get('numero_nc', nc_id)} enregistrée avec succès !")
            
            # Retour à l'accueil
            self.after(1500, lambda: self._navigate_to("accueil"))
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement:\n{str(e)}")
    
    def _show_success_message(self, message: str):
        """Affiche un toast de succès."""
        toast = ctk.CTkToplevel(self)
        toast.title("")
        toast.geometry("400x100")
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        
        # Position en haut au centre
        toast.update_idletasks()
        x = (toast.winfo_screenwidth() - 400) // 2
        toast.geometry(f"+{x}+50")
        
        # Contenu
        frame = ctk.CTkFrame(
            toast,
            fg_color=ModernTheme.SUCCESS,
            corner_radius=12
        )
        frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(expand=True)
        
        icon = ctk.CTkLabel(content, text="✅", font=ctk.CTkFont(size=24))
        icon.pack(side="left", padx=10)
        
        text = ctk.CTkLabel(
            content,
            text=message,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        text.pack(side="left", padx=10)
        
        # Auto-fermeture
        toast.after(2000, toast.destroy)


def main():
    """Point d'entrée de l'application."""
    app = QualiManagerApp()
    app.mainloop()


if __name__ == "__main__":
    main()

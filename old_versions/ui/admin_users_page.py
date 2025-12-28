# -*- coding: utf-8 -*-
"""Page d'administration des utilisateurs - Chargement instantané."""

import customtkinter as ctk
from typing import Callable, Optional, List, Dict, Any
from ui.utils import ModernTheme


class AdminUsersPage(ctk.CTkFrame):
    """Page de gestion des utilisateurs."""
    
    def __init__(self, parent, auth_manager, on_back: Callable, **kwargs):
        super().__init__(parent, fg_color=ModernTheme.BG_PRIMARY, **kwargs)
        
        self.auth_manager = auth_manager
        self.on_back = on_back
        self.users_data = []
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self._build_header()
        self._build_toolbar()
        self._build_table()
        self._load_users()
    
    def _build_header(self):
        """En-tête."""
        header = ctk.CTkFrame(self, fg_color="transparent", height=70)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        header.grid_propagate(False)
        
        ctk.CTkButton(
            header, text="← Retour", fg_color=ModernTheme.TEXT_MUTED,
            hover_color="#6B7280", width=100, height=35, corner_radius=8,
            command=self.on_back
        ).pack(side="left")
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=20)
        
        ctk.CTkLabel(title_frame, text="👥 Gestion des Utilisateurs", font=ctk.CTkFont(size=22, weight="bold"), text_color=ModernTheme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Créez, modifiez et gérez les comptes", font=ctk.CTkFont(size=11), text_color=ModernTheme.TEXT_MUTED).pack(anchor="w")
    
    def _build_toolbar(self):
        """Barre d'outils."""
        toolbar = ctk.CTkFrame(self, fg_color=ModernTheme.BG_TERTIARY, corner_radius=10, height=55)
        toolbar.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        toolbar.grid_propagate(False)
        
        inner = ctk.CTkFrame(toolbar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=10)
        
        ctk.CTkLabel(inner, text="🔍", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))
        self.search_entry = ctk.CTkEntry(inner, placeholder_text="Rechercher...", width=220, corner_radius=8)
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", lambda e: self.after(200, self._load_users))
        
        ctk.CTkLabel(inner, text="  Rôle :", font=ctk.CTkFont(size=12), text_color=ModernTheme.TEXT_SECONDARY).pack(side="left", padx=(20, 5))
        self.role_filter = ctk.CTkComboBox(inner, values=["Tous", "Administrateur", "Responsable", "Utilisateur"], width=140, corner_radius=8, command=lambda v: self._load_users())
        self.role_filter.set("Tous")
        self.role_filter.pack(side="left")
        
        ctk.CTkButton(inner, text="➕ Nouvel utilisateur", fg_color=ModernTheme.SUCCESS, hover_color="#059669", width=160, height=35, corner_radius=8, command=self._show_add_dialog).pack(side="right")
        ctk.CTkButton(inner, text="🔄", fg_color=ModernTheme.PRIMARY, hover_color="#2563EB", width=40, height=35, corner_radius=8, command=self._load_users).pack(side="right", padx=10)
    
    def _build_table(self):
        """Table des utilisateurs."""
        container = ctk.CTkFrame(self, fg_color=ModernTheme.BG_SECONDARY, corner_radius=12)
        container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        header = ctk.CTkFrame(container, fg_color=ModernTheme.BG_TERTIARY, corner_radius=8, height=45)
        header.pack(fill="x", padx=10, pady=(10, 5))
        header.pack_propagate(False)
        
        for col in ["Nom", "Email", "Rôle", "Statut", "Actions"]:
            ctk.CTkLabel(header, text=col, font=ctk.CTkFont(size=12, weight="bold"), text_color=ModernTheme.TEXT_PRIMARY).pack(side="left", fill="x", expand=True, padx=10)
        
        self.table_scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.table_scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.empty_label = ctk.CTkLabel(self.table_scroll, text="Chargement...", font=ctk.CTkFont(size=14), text_color=ModernTheme.TEXT_MUTED)
        self.empty_label.pack(pady=50)
    
    def _load_users(self):
        """Charge les utilisateurs."""
        for widget in self.table_scroll.winfo_children():
            widget.destroy()
        
        try:
            users = self.auth_manager.get_all_users()
            search = self.search_entry.get().lower()
            role_filter = self.role_filter.get()
            
            filtered = []
            for u in users:
                if search and search not in u.get('nom', '').lower() and search not in u.get('email', '').lower():
                    continue
                if role_filter != "Tous" and u.get('role') != role_filter:
                    continue
                filtered.append(u)
            
            self.users_data = filtered
            
            if not filtered:
                ctk.CTkLabel(self.table_scroll, text="Aucun utilisateur", font=ctk.CTkFont(size=14), text_color=ModernTheme.TEXT_MUTED).pack(pady=50)
            else:
                for user in filtered:
                    self._create_user_row(user)
        except Exception as e:
            ctk.CTkLabel(self.table_scroll, text=f"Erreur: {e}", font=ctk.CTkFont(size=14), text_color=ModernTheme.DANGER).pack(pady=50)
    
    def _create_user_row(self, user: Dict[str, Any]):
        """Crée une ligne utilisateur."""
        row = ctk.CTkFrame(self.table_scroll, fg_color=ModernTheme.BG_TERTIARY, corner_radius=8, height=50)
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)
        
        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Nom
        ctk.CTkLabel(inner, text=user.get('nom', 'N/A'), font=ctk.CTkFont(size=12), text_color=ModernTheme.TEXT_PRIMARY, anchor="w").pack(side="left", fill="x", expand=True, padx=5)
        
        # Email
        ctk.CTkLabel(inner, text=user.get('email', 'N/A'), font=ctk.CTkFont(size=12), text_color=ModernTheme.TEXT_SECONDARY, anchor="w").pack(side="left", fill="x", expand=True, padx=5)
        
        # Rôle
        role = user.get('role', 'N/A')
        role_colors = {"Administrateur": ModernTheme.DANGER, "Responsable": ModernTheme.WARNING, "Utilisateur": ModernTheme.PRIMARY}
        badge = ctk.CTkFrame(inner, fg_color=role_colors.get(role, ModernTheme.TEXT_MUTED), corner_radius=5)
        badge.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(badge, text=role, font=ctk.CTkFont(size=10), text_color="white").pack(padx=8, pady=2)
        
        # Statut
        is_active = user.get('actif', True)
        status_frame = ctk.CTkFrame(inner, fg_color="transparent")
        status_frame.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(status_frame, text="● Actif" if is_active else "○ Inactif", font=ctk.CTkFont(size=11), text_color=ModernTheme.SUCCESS if is_active else ModernTheme.TEXT_MUTED).pack()
        
        # Actions
        actions = ctk.CTkFrame(inner, fg_color="transparent")
        actions.pack(side="left", fill="x", expand=True, padx=5)
        
        user_id = user.get('id')
        ctk.CTkButton(actions, text="✏️", fg_color=ModernTheme.PRIMARY, width=30, height=26, corner_radius=5, command=lambda uid=user_id: self._show_edit_dialog(uid)).pack(side="left", padx=2)
        ctk.CTkButton(actions, text="🗑️", fg_color=ModernTheme.DANGER, width=30, height=26, corner_radius=5, command=lambda uid=user_id: self._confirm_delete(uid)).pack(side="left", padx=2)
    
    def _show_add_dialog(self):
        """Dialogue d'ajout."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nouvel utilisateur")
        dialog.geometry("450x500")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.configure(fg_color=ModernTheme.BG_PRIMARY)
        
        # Centrer
        dialog.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() - 450) // 2
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() - 500) // 2
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(dialog, text="➕ Nouvel Utilisateur", font=ctk.CTkFont(size=18, weight="bold"), text_color=ModernTheme.TEXT_PRIMARY).pack(pady=20)
        
        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30, pady=10)
        
        fields = {}
        for label, key, placeholder in [("Nom complet", "nom", "Prénom Nom"), ("Email", "email", "email@example.com"), ("Mot de passe", "password", "Min. 8 caractères")]:
            ctk.CTkLabel(form, text=label, font=ctk.CTkFont(size=12), text_color=ModernTheme.TEXT_SECONDARY).pack(anchor="w", pady=(10, 3))
            entry = ctk.CTkEntry(form, placeholder_text=placeholder, height=38, corner_radius=8, show="*" if "password" in key else "")
            entry.pack(fill="x")
            fields[key] = entry
        
        ctk.CTkLabel(form, text="Rôle", font=ctk.CTkFont(size=12), text_color=ModernTheme.TEXT_SECONDARY).pack(anchor="w", pady=(10, 3))
        role_combo = ctk.CTkComboBox(form, values=["Utilisateur", "Responsable", "Administrateur"], height=38, corner_radius=8)
        role_combo.set("Utilisateur")
        role_combo.pack(fill="x")
        fields["role"] = role_combo
        
        msg_label = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=11), text_color=ModernTheme.DANGER)
        msg_label.pack(pady=10)
        
        def save():
            nom = fields["nom"].get().strip()
            email = fields["email"].get().strip()
            password = fields["password"].get()
            role = fields["role"].get()
            
            if not all([nom, email, password]):
                msg_label.configure(text="Tous les champs sont requis")
                return
            if len(password) < 8:
                msg_label.configure(text="Mot de passe trop court (min 8)")
                return
            
            try:
                self.auth_manager.create_user(nom, email, password, role)
                dialog.destroy()
                self._load_users()
            except Exception as e:
                msg_label.configure(text=str(e))
        
        btns = ctk.CTkFrame(form, fg_color="transparent")
        btns.pack(pady=20)
        ctk.CTkButton(btns, text="Annuler", fg_color=ModernTheme.TEXT_MUTED, width=100, height=38, command=dialog.destroy).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="Créer", fg_color=ModernTheme.SUCCESS, width=100, height=38, command=save).pack(side="left", padx=5)
    
    def _show_edit_dialog(self, user_id: int):
        """Dialogue de modification."""
        user = None
        for u in self.users_data:
            if u.get('id') == user_id:
                user = u
                break
        if not user:
            return
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Modifier utilisateur")
        dialog.geometry("450x550")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.configure(fg_color=ModernTheme.BG_PRIMARY)
        
        dialog.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() - 450) // 2
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() - 550) // 2
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(dialog, text="✏️ Modifier Utilisateur", font=ctk.CTkFont(size=18, weight="bold"), text_color=ModernTheme.TEXT_PRIMARY).pack(pady=20)
        
        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30, pady=10)
        
        fields = {}
        
        ctk.CTkLabel(form, text="Nom complet", font=ctk.CTkFont(size=12), text_color=ModernTheme.TEXT_SECONDARY).pack(anchor="w", pady=(10, 3))
        nom_entry = ctk.CTkEntry(form, height=38, corner_radius=8)
        nom_entry.insert(0, user.get('nom', ''))
        nom_entry.pack(fill="x")
        fields["nom"] = nom_entry
        
        ctk.CTkLabel(form, text="Email", font=ctk.CTkFont(size=12), text_color=ModernTheme.TEXT_SECONDARY).pack(anchor="w", pady=(10, 3))
        email_entry = ctk.CTkEntry(form, height=38, corner_radius=8)
        email_entry.insert(0, user.get('email', ''))
        email_entry.pack(fill="x")
        fields["email"] = email_entry
        
        ctk.CTkLabel(form, text="Nouveau mot de passe (laisser vide pour conserver)", font=ctk.CTkFont(size=12), text_color=ModernTheme.TEXT_SECONDARY).pack(anchor="w", pady=(10, 3))
        pwd_entry = ctk.CTkEntry(form, placeholder_text="Nouveau mot de passe", height=38, corner_radius=8, show="*")
        pwd_entry.pack(fill="x")
        fields["password"] = pwd_entry
        
        ctk.CTkLabel(form, text="Rôle", font=ctk.CTkFont(size=12), text_color=ModernTheme.TEXT_SECONDARY).pack(anchor="w", pady=(10, 3))
        role_combo = ctk.CTkComboBox(form, values=["Utilisateur", "Responsable", "Administrateur"], height=38, corner_radius=8)
        role_combo.set(user.get('role', 'Utilisateur'))
        role_combo.pack(fill="x")
        fields["role"] = role_combo
        
        ctk.CTkLabel(form, text="Statut", font=ctk.CTkFont(size=12), text_color=ModernTheme.TEXT_SECONDARY).pack(anchor="w", pady=(10, 3))
        status_var = ctk.BooleanVar(value=user.get('actif', True))
        ctk.CTkCheckBox(form, text="Compte actif", variable=status_var, font=ctk.CTkFont(size=12)).pack(anchor="w")
        
        msg_label = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=11), text_color=ModernTheme.DANGER)
        msg_label.pack(pady=10)
        
        def save():
            nom = fields["nom"].get().strip()
            email = fields["email"].get().strip()
            password = fields["password"].get()
            role = fields["role"].get()
            actif = status_var.get()
            
            if not all([nom, email]):
                msg_label.configure(text="Nom et email requis")
                return
            if password and len(password) < 8:
                msg_label.configure(text="Mot de passe trop court (min 8)")
                return
            
            try:
                self.auth_manager.update_user(user_id, nom=nom, email=email, role=role, actif=actif, password=password if password else None)
                dialog.destroy()
                self._load_users()
            except Exception as e:
                msg_label.configure(text=str(e))
        
        btns = ctk.CTkFrame(form, fg_color="transparent")
        btns.pack(pady=20)
        ctk.CTkButton(btns, text="Annuler", fg_color=ModernTheme.TEXT_MUTED, width=100, height=38, command=dialog.destroy).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="Enregistrer", fg_color=ModernTheme.PRIMARY, width=120, height=38, command=save).pack(side="left", padx=5)
    
    def _confirm_delete(self, user_id: int):
        """Confirmation de suppression."""
        user = None
        for u in self.users_data:
            if u.get('id') == user_id:
                user = u
                break
        if not user:
            return
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmer suppression")
        dialog.geometry("400x200")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.configure(fg_color=ModernTheme.BG_PRIMARY)
        
        dialog.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() - 400) // 2
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() - 200) // 2
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(dialog, text="⚠️ Confirmation", font=ctk.CTkFont(size=18, weight="bold"), text_color=ModernTheme.WARNING).pack(pady=20)
        ctk.CTkLabel(dialog, text=f"Supprimer l'utilisateur '{user.get('nom', '')}'?", font=ctk.CTkFont(size=13), text_color=ModernTheme.TEXT_SECONDARY).pack(pady=10)
        
        btns = ctk.CTkFrame(dialog, fg_color="transparent")
        btns.pack(pady=20)
        ctk.CTkButton(btns, text="Annuler", fg_color=ModernTheme.TEXT_MUTED, width=100, height=38, command=dialog.destroy).pack(side="left", padx=10)
        
        def delete():
            try:
                self.auth_manager.delete_user(user_id)
                dialog.destroy()
                self._load_users()
            except Exception as e:
                print(f"Erreur suppression: {e}")
        
        ctk.CTkButton(btns, text="Supprimer", fg_color=ModernTheme.DANGER, width=100, height=38, command=delete).pack(side="left", padx=10)

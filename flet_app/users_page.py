# -*- coding: utf-8 -*-
"""
QualiManager - Page gestion des utilisateurs
"""

import flet as ft
from typing import Dict, Any, Callable, List

from .theme import Theme, Styles
from .components import (
    create_card, create_text_field, create_dropdown,
    create_button, create_badge, create_snackbar,
    create_confirm_dialog, create_empty_state
)


class UsersPage(ft.Container):
    """Page de gestion des utilisateurs."""
    
    def __init__(self, user: Dict, db, navigate: Callable):
        self.user = user
        self.db = db
        self.navigate = navigate
        
        self.search_field = create_text_field(
            label="Rechercher",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search,
            width=250,
        )
        
        self.role_filter = create_dropdown(
            "Rôle",
            ["Tous", "Administrateur", "Responsable", "Utilisateur"],
            on_change=self._on_filter,
            width=150,
        )
        
        # Références pour le rafraîchissement
        self.table_container = ft.Container(expand=True)
        self.main_column = None
        
        super().__init__(
            expand=True,
            padding=30,
            content=None,
        )
        self.content = self._build_ui()
    
    def _build_ui(self) -> ft.Control:
        # Initialiser le contenu du tableau
        self.table_container.content = self._build_table()
        
        self.main_column = ft.Column(
            expand=True,
            controls=[
                # Header
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.IconButton(
                                    ft.Icons.ARROW_BACK,
                                    icon_color=Theme.TEXT_MUTED,
                                    on_click=lambda e: self.navigate("/home"),
                                ),
                                ft.Column(
                                    spacing=0,
                                    controls=[
                                        ft.Text(
                                            "👥 Gestion des Utilisateurs",
                                            size=24,
                                            weight=ft.FontWeight.BOLD,
                                            color=Theme.TEXT_PRIMARY
                                        ),
                                        ft.Text(
                                            "Créez, modifiez et gérez les comptes",
                                            size=13,
                                            color=Theme.TEXT_MUTED
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        create_button(
                            "Nouvel utilisateur",
                            icon=ft.Icons.PERSON_ADD,
                            style="success",
                            on_click=self._show_add_dialog,
                        ),
                    ],
                ),
                
                ft.Container(height=20),
                
                # Toolbar
                create_card(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                controls=[
                                    self.search_field,
                                    self.role_filter,
                                ],
                            ),
                            ft.IconButton(
                                ft.Icons.REFRESH,
                                icon_color=Theme.PRIMARY,
                                tooltip="Actualiser",
                                on_click=self._refresh,
                            ),
                        ],
                    ),
                    padding=15,
                ),
                
                ft.Container(height=20),
                
                # Table
                self.table_container,
            ],
        )
        return self.main_column
    
    def _build_table(self) -> ft.Control:
        users = self.db.get_all_users()
        search = self.search_field.value.lower() if self.search_field.value else ""
        role_filter = self.role_filter.value if self.role_filter.value else "Tous"
        
        # Filtrage
        filtered = []
        for u in users:
            if search and search not in u['nom'].lower() and search not in u['email'].lower():
                continue
            if role_filter != "Tous" and u['role'] != role_filter:
                continue
            filtered.append(u)
        
        if not filtered:
            return create_card(
                content=create_empty_state(
                    ft.Icons.PEOPLE_OUTLINE,
                    "Aucun utilisateur trouvé",
                    "Modifiez vos filtres ou créez un nouvel utilisateur",
                ),
            )
        
        rows = []
        for u in filtered:
            role_colors = {
                "Administrateur": Theme.DANGER,
                "Responsable": Theme.WARNING,
                "Utilisateur": Theme.PRIMARY,
            }
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    ft.CircleAvatar(
                                        content=ft.Text(u['nom'][0].upper()),
                                        bgcolor=role_colors.get(u['role'], Theme.TEXT_MUTED),
                                        radius=15,
                                    ),
                                    ft.Text(u['nom'], color=Theme.TEXT_PRIMARY),
                                ],
                            )
                        ),
                        ft.DataCell(ft.Text(u['email'], color=Theme.TEXT_SECONDARY)),
                        ft.DataCell(
                            ft.Text(
                                u.get('password_plain', 'N/A'),
                                color=Theme.INFO,
                                size=12,
                                weight=ft.FontWeight.BOLD,
                            )
                        ),
                        ft.DataCell(create_badge(u['role'], role_colors.get(u['role'], Theme.TEXT_MUTED))),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        width=8,
                                        height=8,
                                        border_radius=4,
                                        bgcolor=Theme.SUCCESS if u['actif'] else Theme.TEXT_MUTED,
                                    ),
                                    ft.Text(
                                        "Actif" if u['actif'] else "Inactif",
                                        color=Theme.SUCCESS if u['actif'] else Theme.TEXT_MUTED,
                                        size=12
                                    ),
                                ],
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                u['last_login'][:10] if u.get('last_login') else "Jamais",
                                color=Theme.TEXT_MUTED,
                                size=12
                            )
                        ),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        ft.Icons.EDIT,
                                        icon_color=Theme.PRIMARY,
                                        icon_size=18,
                                        tooltip="Modifier",
                                        on_click=lambda e, uid=u['id']: self._show_edit_dialog(uid),
                                    ),
                                    ft.IconButton(
                                        ft.Icons.DELETE,
                                        icon_color=Theme.DANGER,
                                        icon_size=18,
                                        tooltip="Supprimer",
                                        on_click=lambda e, uid=u['id'], name=u['nom']: self._confirm_delete(uid, name),
                                    ),
                                ],
                            )
                        ),
                    ],
                )
            )
        
        return create_card(
            content=ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(f"{len(filtered)} utilisateur(s)", color=Theme.TEXT_MUTED),
                        ],
                    ),
                    ft.Divider(color=Theme.BG_TERTIARY),
                    ft.Container(
                        expand=True,
                        bgcolor=Theme.BG_SECONDARY,
                        border_radius=8,
                        padding=5,
                        content=ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("Nom", color=Theme.TEXT_MUTED)),
                                ft.DataColumn(ft.Text("Email", color=Theme.TEXT_MUTED)),
                                ft.DataColumn(ft.Text("Mot de passe", color=Theme.TEXT_MUTED)),
                                ft.DataColumn(ft.Text("Rôle", color=Theme.TEXT_MUTED)),
                                ft.DataColumn(ft.Text("Statut", color=Theme.TEXT_MUTED)),
                                ft.DataColumn(ft.Text("Dernière connexion", color=Theme.TEXT_MUTED)),
                                ft.DataColumn(ft.Text("Actions", color=Theme.TEXT_MUTED)),
                            ],
                            rows=rows,
                            horizontal_lines=ft.BorderSide(1, Theme.BG_TERTIARY),
                            column_spacing=30,
                            heading_row_height=50,
                            data_row_min_height=60,
                        ),
                    ),
                ],
            ),
        )
    
    def _on_search(self, e):
        self._refresh(e)
    
    def _on_filter(self, e):
        self._refresh(e)
    
    def _refresh(self, e):
        if self.table_container:
            self.table_container.content = self._build_table()
            self.update()
    
    def _show_add_dialog(self, e):
        nom_field = create_text_field("Nom complet", prefix_icon=ft.Icons.PERSON)
        email_field = create_text_field("Email", prefix_icon=ft.Icons.EMAIL)
        password_field = create_text_field("Mot de passe", prefix_icon=ft.Icons.LOCK, password=True)
        role_dropdown = create_dropdown("Rôle", ["Utilisateur", "Responsable", "Administrateur"])
        error_text = ft.Text("", color=Theme.DANGER, size=12)
        
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        def save_user(e):
            nom = nom_field.value
            email = email_field.value
            password = password_field.value
            role = role_dropdown.value or "Utilisateur"
            
            if not all([nom, email, password]):
                error_text.value = "Tous les champs sont requis"
                error_text.update()
                return
            
            if len(password) < 8:
                error_text.value = "Mot de passe trop court (min 8 caractères)"
                error_text.update()
                return
            
            try:
                self.db.create_user(nom, email, password, role)
                dialog.open = False
                self.page.update()
                self._refresh(e)
                create_snackbar(self.page, "✅ Utilisateur créé avec succès", "success")
            except Exception as ex:
                error_text.value = str(ex)
                error_text.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("➕ Nouvel Utilisateur"),
            content=ft.Container(
                width=400,
                content=ft.Column(
                    tight=True,
                    controls=[
                        nom_field,
                        ft.Container(height=10),
                        email_field,
                        ft.Container(height=10),
                        password_field,
                        ft.Container(height=10),
                        role_dropdown,
                        error_text,
                    ],
                ),
            ),
            actions=[
                ft.TextButton("Annuler", on_click=close_dialog),
                create_button("Créer", style="success", on_click=save_user),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def _show_edit_dialog(self, user_id: int):
        user = self.db.get_user(user_id)
        if not user:
            return
        
        nom_field = create_text_field("Nom complet", prefix_icon=ft.Icons.PERSON, value=user['nom'])
        email_field = create_text_field("Email", prefix_icon=ft.Icons.EMAIL, value=user['email'])
        password_field = create_text_field("Nouveau mot de passe (optionnel)", prefix_icon=ft.Icons.LOCK, password=True)
        role_dropdown = create_dropdown("Rôle", ["Utilisateur", "Responsable", "Administrateur"], value=user['role'])
        actif_switch = ft.Switch(label="Compte actif", value=bool(user['actif']))
        error_text = ft.Text("", color=Theme.DANGER, size=12)
        
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        def save_user(e):
            nom = nom_field.value
            email = email_field.value
            password = password_field.value
            role = role_dropdown.value
            actif = actif_switch.value
            
            if not all([nom, email]):
                error_text.value = "Nom et email requis"
                error_text.update()
                return
            
            if password and len(password) < 8:
                error_text.value = "Mot de passe trop court (min 8 caractères)"
                error_text.update()
                return
            
            try:
                update_data = {'nom': nom, 'email': email, 'role': role, 'actif': actif}
                if password:
                    update_data['password'] = password
                self.db.update_user(user_id, **update_data)
                dialog.open = False
                self.page.update()
                self._refresh(e)
                create_snackbar(self.page, "✅ Utilisateur modifié", "success")
            except Exception as ex:
                error_text.value = str(ex)
                error_text.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("✏️ Modifier Utilisateur"),
            content=ft.Container(
                width=400,
                content=ft.Column(
                    tight=True,
                    controls=[
                        nom_field,
                        ft.Container(height=10),
                        email_field,
                        ft.Container(height=10),
                        password_field,
                        ft.Container(height=10),
                        role_dropdown,
                        ft.Container(height=10),
                        actif_switch,
                        error_text,
                    ],
                ),
            ),
            actions=[
                ft.TextButton("Annuler", on_click=close_dialog),
                create_button("Enregistrer", style="primary", on_click=save_user),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def _confirm_delete(self, user_id: int, user_name: str):
        def do_delete():
            try:
                self.db.delete_user(user_id)
                self._refresh(None)
                create_snackbar(self.page, "✅ Utilisateur supprimé", "success")
            except Exception as ex:
                create_snackbar(self.page, f"Erreur: {ex}", "error")
        
        create_confirm_dialog(
            self.page,
            "⚠️ Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer l'utilisateur '{user_name}' ?",
            do_delete,
            "Supprimer",
            danger=True
        )

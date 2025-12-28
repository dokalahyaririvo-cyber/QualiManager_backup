# -*- coding: utf-8 -*-
"""
QualiManager - Composants UI réutilisables
"""

import flet as ft
from typing import Optional, Callable, List
from .theme import Theme, Styles


def create_card(
    content: ft.Control,
    padding: int = Styles.PADDING_LG,
    border_radius: int = Styles.RADIUS_LG,
    bgcolor: str = Theme.BG_SECONDARY,
    **kwargs
) -> ft.Container:
    """Crée une carte avec style."""
    return ft.Container(
        content=content,
        padding=padding,
        border_radius=border_radius,
        bgcolor=bgcolor,
        animate=ft.Animation(Styles.ANIMATION_NORMAL, ft.AnimationCurve.EASE_OUT),
        **kwargs
    )


def create_stat_card(
    icon: str,
    title: str,
    value: str,
    color: str,
    trend: str = None,
    trend_positive: bool = True
) -> ft.Container:
    """Crée une carte de statistique."""
    return ft.Container(
        expand=1,
        padding=20,
        border_radius=Styles.RADIUS_LG,
        bgcolor=Theme.BG_SECONDARY,
        animate=ft.Animation(Styles.ANIMATION_NORMAL, ft.AnimationCurve.EASE_OUT),
        on_hover=lambda e: _card_hover(e),
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Container(
                            padding=12,
                            border_radius=Styles.RADIUS_MD,
                            bgcolor=Theme.BG_TERTIARY,
                            content=ft.Icon(icon, color=color, size=24),
                        ),
                        ft.Text(
                            trend or "",
                            color=Theme.SUCCESS if trend_positive else Theme.DANGER,
                            size=12,
                            weight=ft.FontWeight.W_500
                        ) if trend else ft.Container(),
                    ],
                ),
                ft.Text(
                    value,
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=Theme.TEXT_PRIMARY
                ),
                ft.Text(
                    title,
                    size=14,
                    color=Theme.TEXT_MUTED
                ),
            ],
        ),
    )


def _card_hover(e):
    """Animation de survol."""
    e.control.bgcolor = Theme.BG_TERTIARY if e.data == "true" else Theme.BG_SECONDARY
    e.control.update()


def create_action_card(
    icon: str,
    text: str,
    color: str,
    on_click: Callable = None
) -> ft.Container:
    """Crée une carte d'action cliquable."""
    return ft.Container(
        expand=1,
        padding=25,
        border_radius=Styles.RADIUS_LG,
        bgcolor=color,
        ink=True,
        on_click=on_click,
        animate=ft.Animation(Styles.ANIMATION_FAST, ft.AnimationCurve.EASE_OUT),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(icon, color=ft.Colors.WHITE, size=36),
                ft.Container(height=10),
                ft.Text(
                    text,
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.CENTER
                ),
            ],
        ),
    )


def create_text_field(
    label: str,
    prefix_icon: str = None,
    password: bool = False,
    multiline: bool = False,
    min_lines: int = 1,
    hint_text: str = None,
    on_change: Callable = None,
    expand: bool = False,
    keyboard_type: ft.KeyboardType = None,
    input_filter: ft.InputFilter = None,
    **kwargs
) -> ft.TextField:
    """Crée un champ de texte stylisé avec support clavier spécifique."""
    return ft.TextField(
        label=label,
        prefix_icon=prefix_icon,
        password=password,
        can_reveal_password=password,
        multiline=multiline,
        min_lines=min_lines if multiline else None,
        hint_text=hint_text,
        border_radius=Styles.RADIUS_MD,
        filled=True,
        bgcolor=Theme.BG_TERTIARY,
        border_color=Theme.OUTLINE,
        focused_border_color=Theme.PRIMARY,
        cursor_color=Theme.PRIMARY,
        on_change=on_change,
        expand=expand,
        keyboard_type=keyboard_type,
        input_filter=input_filter,
        **kwargs
    )


def create_dropdown(
    label: str,
    options: List[str],
    value: str = None,
    on_change: Callable = None,
    expand: bool = False,
    prefix_icon: str = None,
    enable_add_new: bool = False,
    on_add_new: Callable = None,
    **kwargs
) -> ft.Dropdown:
    """Crée une liste déroulante stylisée avec icône et animation.
    
    Args:
        enable_add_new: Si True, ajoute une option "➕ Ajouter..." au début
        on_add_new: Callback appelé quand l'utilisateur sélectionne "➕ Ajouter..."
    """
    # Ajouter l'option "➕ Ajouter..." au début si demandé
    dropdown_options = []
    if enable_add_new:
        dropdown_options.append(ft.dropdown.Option("➕ Ajouter..."))
    dropdown_options.extend([ft.dropdown.Option(opt) for opt in options])
    
    return ft.Dropdown(
        label=label,
        options=dropdown_options,
        value=value,
        border_radius=Styles.RADIUS_MD,
        filled=True,
        bgcolor=Theme.BG_TERTIARY,
        border_color=Theme.OUTLINE,
        focused_border_color=Theme.PRIMARY,
        on_change=on_change,
        expand=expand,
        prefix_icon=prefix_icon,
        menu_height=240,  # Limite à 5 items visibles (48px par item × 5 = 240px)
        **kwargs
    )


def create_button(
    text: str,
    icon: str = None,
    style: str = "primary",
    on_click: Callable = None,
    width: int = None,
    disabled: bool = False,
    **kwargs
) -> ft.ElevatedButton:
    """Crée un bouton stylisé."""
    colors = {
        "primary": (Theme.PRIMARY, ft.Colors.WHITE),
        "secondary": (Theme.BG_TERTIARY, Theme.TEXT_PRIMARY),
        "success": (Theme.SUCCESS, ft.Colors.WHITE),
        "danger": (Theme.DANGER, ft.Colors.WHITE),
        "warning": (Theme.WARNING, Theme.TEXT_INVERSE),
        "outline": ("transparent", Theme.PRIMARY),
    }
    
    bgcolor, textcolor = colors.get(style, colors["primary"])
    
    return ft.ElevatedButton(
        text=text,
        icon=icon,
        style=ft.ButtonStyle(
            bgcolor=bgcolor,
            color=textcolor,
            padding=ft.padding.symmetric(15, 20),
            shape=ft.RoundedRectangleBorder(radius=Styles.RADIUS_MD),
        ),
        on_click=on_click,
        width=width,
        disabled=disabled,
        **kwargs
    )


def create_icon_button(
    icon: str,
    tooltip: str = None,
    on_click: Callable = None,
    color: str = Theme.TEXT_MUTED,
    size: int = 24,
    **kwargs
) -> ft.IconButton:
    """Crée un bouton icône."""
    return ft.IconButton(
        icon=icon,
        tooltip=tooltip,
        icon_color=color,
        icon_size=size,
        on_click=on_click,
        **kwargs
    )


def create_badge(
    text: str,
    color: str,
    text_color: str = ft.Colors.WHITE
) -> ft.Container:
    """Crée un badge coloré."""
    return ft.Container(
        padding=ft.padding.symmetric(6, 10),
        border_radius=Styles.RADIUS_SM,
        bgcolor=Theme.BG_TERTIARY,
        content=ft.Text(
            text,
            color=color,
            size=11,
            weight=ft.FontWeight.W_500,
            no_wrap=True,  # JAMAIS de retour à la ligne
        ),
    )


def create_status_badge(status: str) -> ft.Container:
    """Crée un badge de statut."""
    colors = {
        "En cours": Theme.WARNING,
        "Clôturée": Theme.SUCCESS,
    }
    return create_badge(status, colors.get(status, Theme.TEXT_MUTED))


def create_severity_badge(severity: str) -> ft.Container:
    """Crée un badge de gravité."""
    colors = {
        "Mineure": Theme.INFO,
        "Majeure": Theme.WARNING,
        "Critique": Theme.DANGER,
    }
    return create_badge(severity, colors.get(severity, Theme.TEXT_MUTED))


def create_snackbar(
    page: ft.Page,
    message: str,
    type: str = "info"
) -> None:
    """Affiche une notification."""
    colors = {
        "success": Theme.SUCCESS,
        "error": Theme.DANGER,
        "warning": Theme.WARNING,
        "info": Theme.INFO,
    }
    icons = {
        "success": ft.Icons.CHECK_CIRCLE,
        "error": ft.Icons.ERROR,
        "warning": ft.Icons.WARNING,
        "info": ft.Icons.INFO,
    }
    
    page.snack_bar = ft.SnackBar(
        content=ft.Row(
            controls=[
                ft.Icon(icons.get(type, ft.Icons.INFO), color=ft.Colors.WHITE),
                ft.Text(message, color=ft.Colors.WHITE),
            ],
        ),
        bgcolor=colors.get(type, Theme.INFO),
        duration=3000,
    )
    page.snack_bar.open = True
    page.update()


def create_confirm_dialog(
    page: ft.Page,
    title: str,
    content: str,
    on_confirm: Callable,
    confirm_text: str = "Confirmer",
    danger: bool = False
) -> ft.AlertDialog:
    """Crée une boîte de dialogue de confirmation."""
    def close_dialog(e):
        dialog.open = False
        page.update()
    
    def confirm_action(e):
        dialog.open = False
        page.update()
        on_confirm()
    
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title),
        content=ft.Text(content),
        actions=[
            ft.TextButton("Annuler", on_click=close_dialog),
            ft.ElevatedButton(
                confirm_text,
                style=ft.ButtonStyle(
                    bgcolor=Theme.DANGER if danger else Theme.PRIMARY,
                    color=ft.Colors.WHITE,
                ),
                on_click=confirm_action,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    page.overlay.append(dialog)
    dialog.open = True
    page.update()
    return dialog


def create_loading_indicator() -> ft.Container:
    """Crée un indicateur de chargement."""
    return ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.ProgressRing(color=Theme.PRIMARY),
                ft.Container(height=20),
                ft.Text("Chargement...", color=Theme.TEXT_MUTED),
            ],
        ),
    )


def create_empty_state(
    icon: str,
    title: str,
    subtitle: str = None,
    action_text: str = None,
    on_action: Callable = None
) -> ft.Container:
    """Crée un état vide."""
    controls = [
        ft.Icon(icon, size=64, color=Theme.TEXT_MUTED),
        ft.Container(height=20),
        ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_SECONDARY),
    ]
    
    if subtitle:
        controls.append(
            ft.Text(subtitle, size=14, color=Theme.TEXT_MUTED, text_align=ft.TextAlign.CENTER)
        )
    
    if action_text and on_action:
        controls.append(ft.Container(height=20))
        controls.append(create_button(action_text, on_click=on_action))
    
    return ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=controls,
        ),
    )

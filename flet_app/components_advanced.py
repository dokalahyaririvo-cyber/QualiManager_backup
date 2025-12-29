# -*- coding: utf-8 -*-
"""
QualiManager ERP QHSE - Composants UI avancés réutilisables
StandardTable, KPICard, TileCard, TimelineWidget, RACIMatrix, ScoringIndicator, IshikawaChart
"""

import flet as ft
from typing import Optional, Callable, List, Dict, Any
from datetime import datetime
from .theme import Theme


# ============================================================================
# STANDARD TABLE - Avec scroll H/V automatique
# ============================================================================

def StandardTable(
    columns: List[Dict[str, Any]],  # [{"name": str, "width": int/None, "key": str}]
    rows: List[Dict[str, Any]],
    on_row_click: Callable = None,
    on_edit: Callable = None,
    on_delete: Callable = None,
    row_height: int = 48,
    header_bgcolor: str = None,
    stripe_rows: bool = True,
) -> ft.Container:
    """
    Table standard avec scroll horizontal et vertical automatique.
    Critical Requirement: Ne jamais casser la mise en page.
    """
    header_bgcolor = header_bgcolor or Theme.BG_TERTIARY
    
    if not rows:
        return ft.Container(
            padding=40,
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.SEARCH_OFF, size=48, color=Theme.TEXT_MUTED),
                    ft.Text("Aucune donnée", size=16, color=Theme.TEXT_MUTED),
                ]
            )
        )
    
    # Construire l'en-tête
    header_cells = []
    for col in columns:
        cell = ft.Container(
            width=col.get('width'),
            expand=col.get('width') is None,
            padding=ft.Padding(left=8, right=8, top=12, bottom=12),
            content=ft.Text(
                col['name'],
                weight=ft.FontWeight.BOLD,
                size=12,
                color=Theme.TEXT_PRIMARY,
                no_wrap=True,
            ),
        )
        header_cells.append(cell)
    
    header_row = ft.Container(
        bgcolor=header_bgcolor,
        border_radius=ft.BorderRadius(8, 8, 0, 0),
        content=ft.Row(controls=header_cells, spacing=0),
    )
    
    # Construire les lignes
    data_rows = []
    for idx, row_data in enumerate(rows):
        row_cells = []
        row_id = row_data.get('id')
        
        for col in columns:
            key = col.get('key')
            
            # Gestion des colonnes spéciales
            if key == '_actions':
                cell_content = ft.Row(
                    spacing=4,
                    controls=[
                        ft.IconButton(
                            ft.Icons.EDIT, 
                            icon_size=16, 
                            icon_color=Theme.WARNING,
                            tooltip="Modifier",
                            on_click=lambda e, rid=row_id: on_edit(rid) if on_edit else None,
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE, 
                            icon_size=16, 
                            icon_color=Theme.DANGER,
                            tooltip="Supprimer",
                            on_click=lambda e, rid=row_id: on_delete(rid) if on_delete else None,
                        ),
                    ]
                )
            elif key == '_status':
                status = row_data.get('statut', '')
                cell_content = StatusBadge(status)
            elif key == '_severity':
                severity = row_data.get('gravite', '')
                cell_content = SeverityBadge(severity)
            else:
                value = row_data.get(key, '-') if key else '-'
                if value is None:
                    value = '-'
                
                # Scroll horizontal pour texte long si width fixe et texte > 30 chars
                if col.get('scroll_horizontal') and len(str(value)) > 30:
                    cell_content = ft.Container(
                        width=col.get('width', 180) - 16,
                        content=ft.Row(
                            scroll=ft.ScrollMode.AUTO,
                            controls=[
                                ft.Text(
                                    str(value),
                                    size=12,
                                    color=Theme.TEXT_SECONDARY,
                                    no_wrap=True,
                                )
                            ]
                        )
                    )
                else:
                    cell_content = ft.Text(
                        str(value),
                        size=12,
                        color=Theme.TEXT_SECONDARY,
                        no_wrap=col.get('no_wrap', False),
                    )
            
            cell = ft.Container(
                width=col.get('width'),
                expand=col.get('width') is None,
                padding=ft.Padding(left=8, right=8, top=8, bottom=8),
                content=cell_content,
            )
            row_cells.append(cell)
        
        # Couleur alternée
        row_bgcolor = Theme.BG_SECONDARY if idx % 2 == 0 else Theme.BG_TERTIARY if stripe_rows else Theme.BG_SECONDARY
        
        row_container = ft.Container(
            bgcolor=row_bgcolor,
            border=ft.Border(bottom=ft.BorderSide(1, Theme.BG_TERTIARY)),
            content=ft.Row(controls=row_cells, spacing=0),
            on_click=lambda e, rid=row_id: on_row_click(rid) if on_row_click else None,
            ink=True if on_row_click else False,
        )
        data_rows.append(row_container)
    
    # Container scrollable
    return ft.Container(
        border_radius=8,
        bgcolor=Theme.BG_SECONDARY,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        expand=True,
        content=ft.Column(
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                # Header fixe avec scroll horizontal
                ft.Row(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[header_row],
                ),
                # Body avec scroll vertical
                ft.Column(
                    spacing=0,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Row(scroll=ft.ScrollMode.AUTO, controls=[row])
                        for row in data_rows
                    ]
                )
            ]
        )
    )


# ============================================================================
# BADGES
# ============================================================================

def StatusBadge(status: str) -> ft.Container:
    """Badge de statut coloré avec icône."""
    status_config = {
        "En cours": (Theme.WARNING, ft.Icons.HOURGLASS_EMPTY),
        "Clôturée": (Theme.SUCCESS, ft.Icons.CHECK_CIRCLE),
        "À analyser": (Theme.WARNING, ft.Icons.SEARCH),
        "Traité": (Theme.SUCCESS, ft.Icons.DONE_ALL),
        "Non applicable": (Theme.TEXT_MUTED, ft.Icons.BLOCK),
        "Conforme": (Theme.SUCCESS, ft.Icons.VERIFIED),
        "Non conforme": (Theme.DANGER, ft.Icons.ERROR),
        "NA": (Theme.TEXT_MUTED, ft.Icons.REMOVE),
        "Validée": (Theme.SUCCESS, ft.Icons.DONE),
        "Terminée": (Theme.INFO, ft.Icons.TASK_ALT),
        "Bloquée": (Theme.DANGER, ft.Icons.DANGEROUS),
    }
    color, icon = status_config.get(status, (Theme.TEXT_MUTED, ft.Icons.CIRCLE))
    
    return ft.Container(
        padding=ft.Padding(left=10, right=10, top=5, bottom=5),
        border_radius=12,
        bgcolor=Theme.BG_TERTIARY,
        border=ft.Border(
                top=ft.BorderSide(1, color),
                right=ft.BorderSide(1, color),
                bottom=ft.BorderSide(1, color),
                left=ft.BorderSide(1, color),
            ),
        content=ft.Row(
            spacing=4,
            controls=[
                ft.Icon(icon, size=14, color=color),
                ft.Text(status or "-", size=11, color=color, weight=ft.FontWeight.W_600, no_wrap=True),
            ],
        ),
    )


def SeverityBadge(severity: str) -> ft.Container:
    """Badge de gravité avec icône."""
    severity_config = {
        "Mineure": (Theme.INFO, ft.Icons.INFO),
        "Majeure": (Theme.WARNING, ft.Icons.WARNING_AMBER),
        "Critique": (Theme.DANGER, ft.Icons.DANGEROUS),
    }
    color, icon = severity_config.get(severity, (Theme.TEXT_MUTED, ft.Icons.CIRCLE))
    
    return ft.Container(
        padding=ft.Padding(left=10, right=10, top=5, bottom=5),
        border_radius=12,
        bgcolor=Theme.BG_TERTIARY,
        border=ft.Border(
                top=ft.BorderSide(1, color),
                right=ft.BorderSide(1, color),
                bottom=ft.BorderSide(1, color),
                left=ft.BorderSide(1, color),
            ),
        content=ft.Row(
            spacing=4,
            controls=[
                ft.Icon(icon, size=14, color=color),
                ft.Text(severity or "-", size=11, color=color, weight=ft.FontWeight.W_600, no_wrap=True),
            ],
        ),
    )


def PriorityBadge(priority: str) -> ft.Container:
    """Badge de priorité."""
    colors = {
        "Basse": Theme.TEXT_MUTED,
        "Normale": Theme.INFO,
        "Haute": Theme.WARNING,
        "Critique": Theme.DANGER,
    }
    color = colors.get(priority, Theme.TEXT_MUTED)
    
    return ft.Container(
        padding=ft.Padding(left=8, right=8, top=4, bottom=4),
        border_radius=12,
        bgcolor=Theme.BG_TERTIARY,
        content=ft.Text(priority or "-", size=11, color=color, weight=ft.FontWeight.W_500, no_wrap=True),
    )


# ============================================================================
# KPI CARD - Carte de statistique unifiée
# ============================================================================

def KPICard(
    title: str,
    value: str,
    icon: str = None,
    color: str = None,
    trend: str = None,
    trend_positive: bool = True,
    subtitle: str = None,
    on_click: Callable = None,
) -> ft.Container:
    """Carte KPI pour dashboard."""
    color = color or Theme.PRIMARY
    
    trend_widget = None
    if trend:
        trend_color = Theme.SUCCESS if trend_positive else Theme.DANGER
        trend_icon = ft.Icons.TRENDING_UP if trend_positive else ft.Icons.TRENDING_DOWN
        trend_widget = ft.Row(
            spacing=2,
            controls=[
                ft.Icon(trend_icon, size=14, color=trend_color),
                ft.Text(trend, size=11, color=trend_color),
            ]
        )
    
    return ft.Container(
        expand=True,
        padding=20,
        border_radius=16,
        bgcolor=Theme.BG_SECONDARY,
        border=ft.Border(
                top=ft.BorderSide(1, Theme.BORDER),
                right=ft.BorderSide(1, Theme.BORDER),
                bottom=ft.BorderSide(1, Theme.BORDER),
                left=ft.BorderSide(1, Theme.BORDER),
            ),
        ink=True if on_click else False,
        on_click=on_click,
        on_hover=lambda e: _card_hover(e),
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Container(
                            padding=10,
                            border_radius=10,
                            bgcolor=Theme.BG_TERTIARY,
                            content=ft.Icon(icon or ft.Icons.ANALYTICS, color=color, size=24),
                        ),
                        trend_widget or ft.Container(),
                    ]
                ),
                ft.Text(value, size=32, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                ft.Text(title, size=14, color=Theme.TEXT_MUTED),
                ft.Text(subtitle, size=11, color=Theme.TEXT_MUTED) if subtitle else ft.Container(),
            ]
        )
    )


def _card_hover(e):
    """Animation survol carte."""
    if e.data == "true":
        e.control.border = ft.Border(
                top=ft.BorderSide(1, Theme.PRIMARY),
                right=ft.BorderSide(1, Theme.PRIMARY),
                bottom=ft.BorderSide(1, Theme.PRIMARY),
                left=ft.BorderSide(1, Theme.PRIMARY),
            )
    else:
        e.control.border = ft.Border(
                top=ft.BorderSide(1, Theme.BORDER),
                right=ft.BorderSide(1, Theme.BORDER),
                bottom=ft.BorderSide(1, Theme.BORDER),
                left=ft.BorderSide(1, Theme.BORDER),
            )
    e.control.update()


# ============================================================================
# TILE CARD - Tuile pour Hub
# ============================================================================

def TileCard(
    title: str,
    icon: str,
    color: str,
    badge_count: int = None,
    badge_color: str = None,
    subtitle: str = None,
    on_click: Callable = None,
) -> ft.Container:
    """Tuile active pour le Hub de démarrage."""
    badge_color = badge_color or Theme.DANGER
    
    badge = None
    if badge_count is not None and badge_count > 0:
        badge = ft.Container(
            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
            border_radius=12,
            bgcolor=badge_color,
            content=ft.Text(str(badge_count), size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        )
    
    return ft.Container(
        width=200,
        height=180,
        padding=20,
        border_radius=16,
        bgcolor=Theme.BG_SECONDARY,
        border=ft.Border(
                top=ft.BorderSide(1, Theme.BORDER),
                right=ft.BorderSide(1, Theme.BORDER),
                bottom=ft.BorderSide(1, Theme.BORDER),
                left=ft.BorderSide(1, Theme.BORDER),
            ),
        ink=True,
        on_click=on_click,
        on_hover=lambda e: _tile_hover(e, color),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Container(
                            padding=12,
                            border_radius=12,
                            bgcolor=color,
                            content=ft.Icon(icon, color=ft.Colors.WHITE, size=28),
                        ),
                        badge or ft.Container(),
                    ]
                ),
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                        ft.Text(subtitle or "", size=12, color=Theme.TEXT_MUTED),
                    ]
                )
            ]
        )
    )


def _tile_hover(e, color):
    """Animation survol tuile."""
    if e.data == "true":
        e.control.border = ft.Border(
                top=ft.BorderSide(2, color),
                right=ft.BorderSide(2, color),
                bottom=ft.BorderSide(2, color),
                left=ft.BorderSide(2, color),
            )
        e.control.bgcolor = Theme.BG_TERTIARY
    else:
        e.control.border = ft.Border(
                top=ft.BorderSide(1, Theme.BORDER),
                right=ft.BorderSide(1, Theme.BORDER),
                bottom=ft.BorderSide(1, Theme.BORDER),
                left=ft.BorderSide(1, Theme.BORDER),
            )
        e.control.bgcolor = Theme.BG_SECONDARY
    e.control.update()


# ============================================================================
# TIMELINE WIDGET - Frise chronologique horizontale
# ============================================================================

def TimelineWidget(
    events: List[Dict[str, Any]],  # [{"date": str, "title": str, "type": str, "status": str}]
    height: int = 120,
) -> ft.Container:
    """Widget de timeline horizontale pour traçabilité lot."""
    
    if not events:
        return ft.Container(
            height=height,
            alignment=ft.Alignment(0, 0),
            content=ft.Text("Aucun événement", color=Theme.TEXT_MUTED),
        )
    
    # Couleurs par type d'événement
    type_colors = {
        "Production": Theme.PRIMARY,
        "Analyse": Theme.INFO,
        "Inspection": Theme.WARNING,
        "NC": Theme.DANGER,
        "Action": Theme.SECONDARY,
        "Liberation": Theme.SUCCESS,
    }
    
    timeline_items = []
    for i, event in enumerate(events):
        color = type_colors.get(event.get('type_event', ''), Theme.TEXT_MUTED)
        is_last = i == len(events) - 1
        
        # Point + Ligne
        point = ft.Container(
            width=16,
            height=16,
            border_radius=8,
            bgcolor=color,
            border=ft.Border(
                top=ft.BorderSide(3, Theme.BG_SECONDARY),
                right=ft.BorderSide(3, Theme.BG_SECONDARY),
                bottom=ft.BorderSide(3, Theme.BG_SECONDARY),
                left=ft.BorderSide(3, Theme.BG_SECONDARY),
            ),
        )
        
        line = ft.Container(
            width=60,
            height=2,
            bgcolor=Theme.BORDER if not is_last else "transparent",
        )
        
        # Info
        info = ft.Column(
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    event.get('date_event', '')[:10] if event.get('date_event') else '',
                    size=10,
                    color=Theme.TEXT_MUTED,
                ),
                ft.Text(
                    event.get('type_event', ''),
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    color=color,
                ),
                ft.Text(
                    event.get('titre', '')[:20] + '...' if len(event.get('titre', '')) > 20 else event.get('titre', ''),
                    size=10,
                    color=Theme.TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
            ]
        )
        
        item = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[point, line] if not is_last else [point],
                ),
                info,
            ]
        )
        
        timeline_items.append(item)
    
    return ft.Container(
        height=height,
        padding=10,
        border_radius=8,
        bgcolor=Theme.BG_SECONDARY,
        content=ft.Row(
            scroll=ft.ScrollMode.AUTO,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=timeline_items,
        )
    )


# ============================================================================
# SCORING INDICATOR - Indicateur de score avec couleur
# ============================================================================

def ScoringIndicator(
    score: float,
    max_score: float = 100,
    threshold_warning: float = 80,
    threshold_danger: float = 60,
    size: str = "normal",  # "small", "normal", "large"
) -> ft.Container:
    """Indicateur de score avec feedback visuel."""
    
    percentage = (score / max_score * 100) if max_score > 0 else 0
    
    if percentage >= threshold_warning:
        color = Theme.SUCCESS
        status = "Excellent"
    elif percentage >= threshold_danger:
        color = Theme.WARNING
        status = "À améliorer"
    else:
        color = Theme.DANGER
        status = "Critique"
    
    sizes = {
        "small": {"text": 24, "status": 10, "padding": 10},
        "normal": {"text": 36, "status": 12, "padding": 15},
        "large": {"text": 48, "status": 14, "padding": 20},
    }
    s = sizes.get(size, sizes["normal"])
    
    return ft.Container(
        padding=s["padding"],
        border_radius=12,
        bgcolor=Theme.BG_SECONDARY,
        border=ft.Border(
                top=ft.BorderSide(2, color),
                right=ft.BorderSide(2, color),
                bottom=ft.BorderSide(2, color),
                left=ft.BorderSide(2, color),
            ),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[
                ft.Text(
                    f"{percentage:.0f}%",
                    size=s["text"],
                    weight=ft.FontWeight.BOLD,
                    color=color,
                ),
                ft.Text(
                    f"{score:.0f}/{max_score:.0f}",
                    size=s["status"],
                    color=Theme.TEXT_MUTED,
                ),
                ft.Text(
                    status,
                    size=s["status"],
                    color=color,
                    weight=ft.FontWeight.W_500,
                ),
            ]
        )
    )


# ============================================================================
# COST INDICATOR - Grand indicateur de coût
# ============================================================================

def CostIndicator(
    total_cost: float,
    breakdown: Dict[str, float] = None,
    currency: str = "EUR",
) -> ft.Container:
    """Grand indicateur de coût de non-qualité."""
    
    breakdown_items = []
    if breakdown:
        for label, value in breakdown.items():
            if value > 0:
                breakdown_items.append(
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(label, size=12, color=Theme.TEXT_MUTED),
                            ft.Text(f"{value:,.2f} {currency}", size=12, color=Theme.TEXT_SECONDARY),
                        ]
                    )
                )
    
    # Couleur selon montant
    if total_cost > 5000:
        color = Theme.DANGER
    elif total_cost > 1000:
        color = Theme.WARNING
    else:
        color = Theme.SUCCESS
    
    return ft.Container(
        padding=20,
        border_radius=16,
        bgcolor=Theme.BG_SECONDARY,
        border=ft.Border(
                top=ft.BorderSide(2, color),
                right=ft.BorderSide(2, color),
                bottom=ft.BorderSide(2, color),
                left=ft.BorderSide(2, color),
            ),
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.EURO, color=color, size=32),
                        ft.Text(
                            f"{total_cost:,.2f} {currency}",
                            size=36,
                            weight=ft.FontWeight.BOLD,
                            color=color,
                        ),
                    ]
                ),
                ft.Text(
                    "Coût Total de Non-Qualité",
                    size=14,
                    color=Theme.TEXT_MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(color=Theme.BORDER) if breakdown_items else ft.Container(),
                *breakdown_items,
            ]
        )
    )


# ============================================================================
# RACI MATRIX ROW - Ligne de matrice RACI
# ============================================================================

def RACIMatrixRow(
    action: Dict[str, Any],
    users: List[Dict[str, Any]],
    on_update: Callable = None,
) -> ft.Container:
    """Ligne de matrice RACI avec slider progression."""
    
    is_late = action.get('is_late', False)
    progression = action.get('progression', 0)
    
    # Couleur de fond si en retard
    bgcolor = Theme.DANGER if is_late else Theme.BG_SECONDARY
    if is_late:
        bgcolor = ft.Colors.with_opacity(0.1, Theme.DANGER)
    
    # Slider progression
    progress_slider = ft.Slider(
        value=progression,
        min=0,
        max=100,
        divisions=20,
        label="{value}%",
        active_color=Theme.SUCCESS if progression >= 100 else Theme.WARNING if progression > 50 else Theme.DANGER,
        on_change_end=lambda e: on_update(action['id'], {'progression': int(e.control.value)}) if on_update else None,
    )
    
    # Barre de progression visuelle
    progress_bar = ft.Container(
        height=8,
        border_radius=4,
        bgcolor=Theme.BG_TERTIARY,
        content=ft.Container(
            width=progression * 2,  # Largeur proportionnelle
            height=8,
            border_radius=4,
            bgcolor=Theme.SUCCESS if progression >= 100 else Theme.WARNING if progression > 50 else Theme.DANGER,
        )
    )
    
    return ft.Container(
        padding=15,
        margin=8,
        border_radius=8,
        bgcolor=bgcolor if not is_late else None,
        border=ft.Border(
                top=ft.BorderSide(2, Theme.DANGER),
                right=ft.BorderSide(2, Theme.DANGER),
                bottom=ft.BorderSide(2, Theme.DANGER),
                left=ft.BorderSide(2, Theme.DANGER),
            ) if is_late else ft.Border(
                top=ft.BorderSide(1, Theme.BORDER),
                right=ft.BorderSide(1, Theme.BORDER),
                bottom=ft.BorderSide(1, Theme.BORDER),
                left=ft.BorderSide(1, Theme.BORDER),
            ),
        content=ft.Column(
            spacing=10,
            controls=[
                # Titre et alerte retard
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            action.get('titre_action', ''),
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=Theme.TEXT_PRIMARY,
                        ),
                        ft.Container(
                            padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                            border_radius=8,
                            bgcolor=Theme.DANGER,
                            visible=is_late,
                            content=ft.Row(
                                spacing=4,
                                controls=[
                                    ft.Icon(ft.Icons.WARNING, size=14, color=ft.Colors.WHITE),
                                    ft.Text("EN RETARD", size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                ]
                            )
                        ) if is_late else ft.Container(),
                    ]
                ),
                # RACI
                ft.Row(
                    spacing=20,
                    controls=[
                        _raci_cell("R", action.get('responsible_nom', '-'), Theme.DANGER),
                        _raci_cell("A", action.get('accountable_nom', '-'), Theme.WARNING),
                        _raci_cell("C", "-", Theme.INFO),  # TODO: Afficher liste
                        _raci_cell("I", "-", Theme.SUCCESS),
                    ]
                ),
                # Progression
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Progression:", size=12, color=Theme.TEXT_MUTED),
                        ft.Container(width=200, content=progress_bar),
                        ft.Text(f"{progression}%", size=14, weight=ft.FontWeight.BOLD, 
                               color=Theme.SUCCESS if progression >= 100 else Theme.TEXT_PRIMARY),
                    ]
                ),
                # Dates
                ft.Row(
                    spacing=20,
                    controls=[
                        ft.Text(f"Échéance: {action.get('date_butoir', '-')}", size=11, color=Theme.DANGER if is_late else Theme.TEXT_MUTED),
                        ft.Text(f"Priorité: {action.get('priorite', '-')}", size=11, color=Theme.TEXT_MUTED),
                    ]
                ),
            ]
        )
    )


def _raci_cell(letter: str, name: str, color: str) -> ft.Container:
    """Cellule RACI."""
    return ft.Row(
        spacing=4,
        controls=[
            ft.Container(
                width=24,
                height=24,
                border_radius=12,
                bgcolor=color,
                alignment=ft.Alignment(0, 0),
                content=ft.Text(letter, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            ),
            ft.Text(name, size=12, color=Theme.TEXT_SECONDARY),
        ]
    )


# ============================================================================
# ISHIKAWA CHART - Diagramme en arêtes de poisson
# ============================================================================

def IshikawaChart(
    problem: str,
    categories: Dict[str, List[str]] = None,  # {"Matière": ["cause1", "cause2"], ...}
    on_add_cause: Callable = None,
) -> ft.Container:
    """Diagramme d'Ishikawa (5M) visuel."""
    
    # Catégories 5M par défaut
    default_categories = {
        "Matière": [],
        "Méthode": [],
        "Main d'oeuvre": [],
        "Milieu": [],
        "Matériel": [],
    }
    categories = categories or default_categories
    
    # Couleurs par catégorie
    colors = {
        "Matière": Theme.DANGER,
        "Méthode": Theme.WARNING,
        "Main d'oeuvre": Theme.INFO,
        "Milieu": Theme.SUCCESS,
        "Matériel": Theme.SECONDARY,
        "Management": Theme.PRIMARY,
        "Moyen": Theme.PRIMARY_LIGHT,
    }
    
    # Construire les branches
    top_branches = []
    bottom_branches = []
    
    for i, (cat, causes) in enumerate(categories.items()):
        color = colors.get(cat, Theme.TEXT_MUTED)
        
        # Causes sous forme d'étiquettes
        cause_chips = [
            ft.Container(
                padding=ft.Padding(left=8, right=8, top=4, bottom=4),
                margin=4,
                border_radius=8,
                bgcolor=ft.Colors.with_opacity(0.2, color),
                content=ft.Text(cause, size=10, color=color),
            )
            for cause in causes
        ]
        
        branch = ft.Container(
            width=150,
            padding=10,
            content=ft.Column(
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                        border_radius=8,
                        bgcolor=color,
                        content=ft.Text(cat, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    ),
                    *cause_chips,
                    ft.IconButton(
                        ft.Icons.ADD_CIRCLE_OUTLINE,
                        icon_size=20,
                        icon_color=color,
                        tooltip=f"Ajouter cause {cat}",
                        on_click=lambda e, c=cat: on_add_cause(c) if on_add_cause else None,
                    ),
                ]
            )
        )
        
        if i % 2 == 0:
            top_branches.append(branch)
        else:
            bottom_branches.append(branch)
    
    # Problème central (tête du poisson)
    problem_box = ft.Container(
        padding=20,
        border_radius=8,
        bgcolor=Theme.DANGER,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.ERROR, color=ft.Colors.WHITE, size=24),
                ft.Text("PROBLÈME", size=10, color=ft.Colors.WHITE),
                ft.Text(
                    problem[:50] + "..." if len(problem) > 50 else problem,
                    size=12,
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
            ]
        )
    )
    
    return ft.Container(
        padding=20,
        border_radius=12,
        bgcolor=Theme.BG_SECONDARY,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Diagramme d'Ishikawa (5M)", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                ft.Container(height=10),
                # Branches du haut
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    controls=top_branches,
                ),
                # Ligne centrale + Problème
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(width=300, height=4, bgcolor=Theme.BORDER),
                        problem_box,
                    ]
                ),
                # Branches du bas
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    controls=bottom_branches,
                ),
            ]
        )
    )


# ============================================================================
# PROGRESS STEPS - Étapes de progression
# ============================================================================

def ProgressSteps(
    steps: List[Dict[str, Any]],  # [{"label": str, "completed": bool, "current": bool}]
) -> ft.Container:
    """Indicateur d'étapes de progression."""
    
    step_controls = []
    for i, step in enumerate(steps):
        is_last = i == len(steps) - 1
        
        if step.get('completed'):
            color = Theme.SUCCESS
            icon = ft.Icons.CHECK_CIRCLE
        elif step.get('current'):
            color = Theme.PRIMARY
            icon = ft.Icons.RADIO_BUTTON_CHECKED
        else:
            color = Theme.TEXT_MUTED
            icon = ft.Icons.RADIO_BUTTON_UNCHECKED
        
        step_item = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[
                ft.Icon(icon, color=color, size=24),
                ft.Text(step['label'], size=11, color=color, text_align=ft.TextAlign.CENTER),
            ]
        )
        
        step_controls.append(step_item)
        
        if not is_last:
            line_color = Theme.SUCCESS if step.get('completed') else Theme.BORDER
            step_controls.append(
                ft.Container(width=40, height=2, bgcolor=line_color)
            )
    
    return ft.Container(
        padding=10,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=step_controls,
        )
    )


# ============================================================================
# ALERT BANNER - Bannière d'alerte
# ============================================================================

def AlertBanner(
    message: str,
    type: str = "info",  # "info", "success", "warning", "danger"
    dismissible: bool = True,
    on_dismiss: Callable = None,
) -> ft.Container:
    """Bannière d'alerte."""
    
    colors = {
        "info": Theme.INFO,
        "success": Theme.SUCCESS,
        "warning": Theme.WARNING,
        "danger": Theme.DANGER,
    }
    icons = {
        "info": ft.Icons.INFO,
        "success": ft.Icons.CHECK_CIRCLE,
        "warning": ft.Icons.WARNING,
        "danger": ft.Icons.ERROR,
    }
    
    color = colors.get(type, Theme.INFO)
    icon = icons.get(type, ft.Icons.INFO)
    
    return ft.Container(
        padding=12,
        border_radius=8,
        bgcolor=ft.Colors.with_opacity(0.1, color),
        border=ft.Border(
                top=ft.BorderSide(1, color),
                right=ft.BorderSide(1, color),
                bottom=ft.BorderSide(1, color),
                left=ft.BorderSide(1, color),
            ),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(icon, color=color, size=20),
                        ft.Text(message, color=color, size=13),
                    ]
                ),
                ft.IconButton(
                    ft.Icons.CLOSE,
                    icon_size=16,
                    icon_color=color,
                    on_click=on_dismiss,
                ) if dismissible else ft.Container(),
            ]
        )
    )


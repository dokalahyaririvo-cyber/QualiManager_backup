# -*- coding: utf-8 -*-
"""
Calendrier personnalisé hors ligne pour QualiManager
Fonctionne sans connexion Internet
"""

import flet as ft
from datetime import datetime, timedelta
import calendar
from typing import Callable
from .theme import Theme


class CustomCalendar(ft.AlertDialog):
    """Calendrier personnalisé hors ligne pour sélection de date."""
    
    def __init__(self, on_date_selected: Callable, initial_date=None):
        self.on_date_selected = on_date_selected
        self.current_date = initial_date if initial_date else datetime.now().date()
        self.selected_year = self.current_date.year
        self.selected_month = self.current_date.month
        
        # Container pour le calendrier (sera mis à jour)
        self.calendar_grid = ft.Column(spacing=5)
        
        # Titre avec navigation mois/année
        self.month_year_text = ft.Text(
            self._get_month_year_text(),
            size=16,
            weight=ft.FontWeight.BOLD,
            color=Theme.TEXT_PRIMARY,
        )
        
        super().__init__(
            modal=True,
            title=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("[Date] Sélectionner une date", size=18, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        on_click=lambda e: self._close(),
                        icon_size=20,
                    ),
                ],
            ),
            content=ft.Container(
                width=350,
                padding=10,
                content=ft.Column(
                    spacing=15,
                    controls=[
                        # Navigation mois/année
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.CHEVRON_LEFT,
                                    on_click=lambda e: self._prev_month(),
                                    tooltip="Mois précédent",
                                ),
                                self.month_year_text,
                                ft.IconButton(
                                    icon=ft.Icons.CHEVRON_RIGHT,
                                    on_click=lambda e: self._next_month(),
                                    tooltip="Mois suivant",
                                ),
                            ],
                        ),
                        # Sélecteurs rapides
                        ft.Row(
                            spacing=5,
                            controls=[
                                ft.Dropdown(
                                    label="Année",
                                    value=str(self.selected_year),
                                    options=[str(y) for y in range(2020, 2031)],
                                    width=100,
                                    text_size=12,
                                    on_change=lambda e: self._change_year(int(e.control.value)),
                                ),
                                ft.Dropdown(
                                    label="Mois",
                                    value=str(self.selected_month),
                                    options=[str(m) for m in range(1, 13)],
                                    width=80,
                                    text_size=12,
                                    on_change=lambda e: self._change_month(int(e.control.value)),
                                ),
                                ft.TextButton(
                                    "Aujourd'hui",
                                    on_click=lambda e: self._select_today(),
                                ),
                            ],
                        ),
                        ft.Divider(height=1),
                        # Grille du calendrier
                        self.calendar_grid,
                    ],
                ),
            ),
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: self._close()),
            ],
        )
        
        self._build_calendar()
    
    def _get_month_year_text(self):
        """Retourne le texte du mois et année."""
        months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                  "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        return f"{months[self.selected_month - 1]} {self.selected_year}"
    
    def _build_calendar(self):
        """Construit la grille du calendrier."""
        # En-têtes des jours
        days_header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[
                ft.Container(
                    width=40,
                    content=ft.Text(day, size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                )
                for day in ["Lu", "Ma", "Me", "Je", "Ve", "Sa", "Di"]
            ],
        )
        
        # Obtenir le calendrier du mois
        cal = calendar.monthcalendar(self.selected_year, self.selected_month)
        
        # Créer les lignes de jours
        week_rows = []
        today = datetime.now().date()
        
        for week in cal:
            day_buttons = []
            for day in week:
                if day == 0:
                    # Jour vide
                    day_buttons.append(ft.Container(width=40, height=40))
                else:
                    day_date = datetime(self.selected_year, self.selected_month, day).date()
                    is_today = day_date == today
                    is_selected = day_date == self.current_date
                    
                    # Style du bouton
                    if is_selected:
                        bgcolor = Theme.PRIMARY
                        text_color = ft.Colors.WHITE
                    elif is_today:
                        bgcolor = ft.Colors.BLUE_50
                        text_color = Theme.PRIMARY
                    else:
                        bgcolor = Theme.BG_SECONDARY
                        text_color = Theme.TEXT_PRIMARY
                    
                    day_button = ft.Container(
                        width=40,
                        height=40,
                        border_radius=20,
                        bgcolor=bgcolor,
                        content=ft.Text(
                            str(day),
                            size=13,
                            color=text_color,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        alignment=ft.Alignment(0, 0),
                        on_click=lambda e, d=day: self._select_day(d),
                        ink=True,
                    )
                    day_buttons.append(day_button)
            
            week_rows.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    controls=day_buttons,
                )
            )
        
        # Mettre à jour le calendrier
        self.calendar_grid.controls = [days_header] + week_rows
    
    def _prev_month(self):
        """Mois précédent."""
        if self.selected_month == 1:
            self.selected_month = 12
            self.selected_year -= 1
        else:
            self.selected_month -= 1
        self._update_calendar()
    
    def _next_month(self):
        """Mois suivant."""
        if self.selected_month == 12:
            self.selected_month = 1
            self.selected_year += 1
        else:
            self.selected_month += 1
        self._update_calendar()
    
    def _change_year(self, year: int):
        """Change l'année."""
        self.selected_year = year
        self._update_calendar()
    
    def _change_month(self, month: int):
        """Change le mois."""
        self.selected_month = month
        self._update_calendar()
    
    def _select_today(self):
        """Sélectionne aujourd'hui."""
        today = datetime.now().date()
        self.selected_year = today.year
        self.selected_month = today.month
        self.current_date = today
        self._update_calendar()
    
    def _select_day(self, day: int):
        """Sélectionne un jour."""
        selected_date = datetime(self.selected_year, self.selected_month, day).date()
        self.on_date_selected(selected_date)
        self._close()
    
    def _update_calendar(self):
        """Met à jour l'affichage du calendrier."""
        self.month_year_text.value = self._get_month_year_text()
        self.month_year_text.update()
        self._build_calendar()
        self.calendar_grid.update()
    
    def _close(self):
        """Ferme le calendrier."""
        self.open = False
        self.update()

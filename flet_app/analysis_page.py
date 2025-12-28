# -*- coding: utf-8 -*-
"""
QualiManager - Page des outils d'analyse
5 Pourquoi, Ishikawa, AMDEC, 8D, Pareto
"""

import flet as ft
from typing import Dict, Any, Callable, List
import json

from .theme import Theme, Styles
from .components import (
    create_card, create_text_field, create_button,
    create_snackbar
)


class AnalysisPage(ft.View):
    """Page d'analyse des causes."""
    
    def __init__(self, user: Dict, db, navigate: Callable, nc_id: int = None):
        self.user = user
        self.db = db
        self.navigate = navigate
        self.nc_id = nc_id
        self.nc_data = db.get_nc(nc_id) if nc_id else {}
        self.current_tab = 0
        
        super().__init__(
            route="/analysis" if not nc_id else f"/analysis/{nc_id}",
            bgcolor=Theme.BG_PRIMARY,
            padding=0,
            controls=[self._build_ui()],
        )
    
    def _build_ui(self) -> ft.Control:
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            on_change=self._on_tab_change,
            tabs=[
                ft.Tab(text="5 Pourquoi", icon=ft.Icons.HELP),
                ft.Tab(text="Ishikawa", icon=ft.Icons.ACCOUNT_TREE),
                ft.Tab(text="AMDEC", icon=ft.Icons.GRID_VIEW),
                ft.Tab(text="8D", icon=ft.Icons.FORMAT_LIST_NUMBERED),
                ft.Tab(text="Pareto", icon=ft.Icons.BAR_CHART),
            ],
        )
        
        self.content_container = ft.Container(
            expand=True,
            padding=20,
            content=self._build_5why(),
        )
        
        return ft.Column(
            expand=True,
            controls=[
                # Header
                ft.Container(
                    padding=20,
                    bgcolor=Theme.BG_SECONDARY,
                    content=ft.Row(
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
                                                "🔬 Analyse des Causes",
                                                size=22,
                                                weight=ft.FontWeight.BOLD,
                                                color=Theme.TEXT_PRIMARY
                                            ),
                                            ft.Text(
                                                f"NC: {self.nc_data.get('reference', 'Nouvelle analyse')}",
                                                size=12,
                                                color=Theme.TEXT_MUTED
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                
                # Tabs
                ft.Container(
                    padding=ft.padding.symmetric(20, 0),
                    content=self.tabs,
                ),
                
                # Content
                self.content_container,
            ],
        )
    
    def _on_tab_change(self, e):
        self.current_tab = e.control.selected_index
        methods = [
            self._build_5why,
            self._build_ishikawa,
            self._build_amdec,
            self._build_8d,
            self._build_pareto,
        ]
        self.content_container.content = methods[self.current_tab]()
        self.update()
    
    # ========== 5 POURQUOI ==========
    def _build_5why(self) -> ft.Control:
        colors = [Theme.DANGER, Theme.WARNING, Theme.SUCCESS, Theme.PRIMARY, Theme.SECONDARY]
        
        self.why_entries = []
        why_controls = []
        
        for i in range(5):
            why_q = create_text_field(f"Pourquoi {i+1} ?", expand=True)
            why_a = create_text_field("Réponse", expand=True)
            self.why_entries.append((why_q, why_a))
            
            why_controls.append(
                ft.Container(
                    margin=ft.margin.only(bottom=15),
                    padding=20,
                    border_radius=Styles.RADIUS_LG,
                    bgcolor=Theme.BG_SECONDARY,
                    border=ft.border.all(2, colors[i]),
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                width=50,
                                height=50,
                                border_radius=25,
                                bgcolor=colors[i],
                                alignment=ft.alignment.center,
                                content=ft.Text(
                                    f"P{i+1}",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE
                                ),
                            ),
                            ft.Container(width=15),
                            ft.Column(
                                expand=True,
                                controls=[why_q, why_a],
                            ),
                        ],
                    ),
                )
            )
        
        self.problem_field = create_text_field(
            "Problème à analyser",
            multiline=True,
            min_lines=2,
            value=self.nc_data.get('description', ''),
        )
        
        self.root_cause_field = create_text_field(
            "Cause racine identifiée",
        )
        
        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                # Problème
                create_card(
                    content=ft.Column(
                        controls=[
                            ft.Text("🎯 Problème initial", size=16, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                            self.problem_field,
                        ],
                    ),
                ),
                
                ft.Container(height=20),
                
                # Les 5 Pourquoi
                *why_controls,
                
                # Cause racine
                ft.Container(
                    padding=20,
                    border_radius=Styles.RADIUS_LG,
                    bgcolor=Theme.SECONDARY,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "🎯 CAUSE RACINE IDENTIFIÉE",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE
                            ),
                            self.root_cause_field,
                        ],
                    ),
                ),
                
                ft.Container(height=20),
                
                # Bouton sauvegarder
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        create_button(
                            "💾 Sauvegarder l'analyse",
                            style="success",
                            on_click=lambda e: self._save_analysis("5why"),
                        ),
                    ],
                ),
            ],
        )
    
    # ========== ISHIKAWA ==========
    def _build_ishikawa(self) -> ft.Control:
        categories = [
            ("👷 Main d'œuvre", "main_oeuvre", Theme.DANGER),
            ("⚙️ Matériel", "materiel", Theme.WARNING),
            ("📦 Matière", "matiere", Theme.SUCCESS),
            ("📋 Méthode", "methode", Theme.PRIMARY),
            ("🌍 Milieu", "milieu", Theme.SECONDARY),
            ("📏 Mesure", "mesure", "#EC4899"),
        ]
        
        self.ishikawa_entries = {}
        cat_controls = []
        
        for name, key, color in categories:
            entries = [create_text_field(f"Cause {i+1}", expand=True) for i in range(3)]
            self.ishikawa_entries[key] = entries
            
            cat_controls.append(
                ft.Container(
                    expand=1,
                    padding=15,
                    border_radius=Styles.RADIUS_MD,
                    bgcolor=Theme.BG_SECONDARY,
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                padding=10,
                                border_radius=Styles.RADIUS_SM,
                                bgcolor=color,
                                content=ft.Text(name, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ),
                            *entries,
                        ],
                    ),
                )
            )
        
        self.effect_field = create_text_field(
            "Effet / Problème",
            value=self.nc_data.get('description', '')[:100] if self.nc_data.get('description') else '',
        )
        
        self.ishikawa_synth = create_text_field(
            "Synthèse des causes principales",
            multiline=True,
            min_lines=2,
        )
        
        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                # Effet
                ft.Container(
                    padding=20,
                    border_radius=Styles.RADIUS_LG,
                    bgcolor=Theme.DANGER,
                    content=ft.Column(
                        controls=[
                            ft.Text("🎯 EFFET / PROBLÈME", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            self.effect_field,
                        ],
                    ),
                ),
                
                ft.Container(height=20),
                
                # 6M en grille 2x3
                ft.Row(controls=cat_controls[:3]),
                ft.Container(height=10),
                ft.Row(controls=cat_controls[3:]),
                
                ft.Container(height=20),
                
                # Synthèse
                ft.Container(
                    padding=20,
                    border_radius=Styles.RADIUS_LG,
                    bgcolor=Theme.INFO,
                    content=ft.Column(
                        controls=[
                            ft.Text("📊 SYNTHÈSE", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            self.ishikawa_synth,
                        ],
                    ),
                ),
                
                ft.Container(height=20),
                
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        create_button(
                            "💾 Sauvegarder le diagramme",
                            style="success",
                            on_click=lambda e: self._save_analysis("ishikawa"),
                        ),
                    ],
                ),
            ],
        )
    
    # ========== AMDEC ==========
    def _build_amdec(self) -> ft.Control:
        self.amdec_rows = []
        
        def create_amdec_row(index: int) -> ft.Container:
            entries = {
                'mode': create_text_field("Mode défaillance", width=150),
                'effet': create_text_field("Effet", width=120),
                'cause': create_text_field("Cause", width=120),
                'g': create_text_field("G", width=50),
                'o': create_text_field("O", width=50),
                'd': create_text_field("D", width=50),
                'ipr': ft.Container(
                    width=60,
                    height=40,
                    bgcolor=Theme.BG_TERTIARY,
                    border_radius=Styles.RADIUS_SM,
                    alignment=ft.alignment.center,
                    content=ft.Text("--", color=Theme.TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                ),
                'action': create_text_field("Action corrective", width=150),
            }
            self.amdec_rows.append(entries)
            
            return ft.Container(
                padding=10,
                border_radius=Styles.RADIUS_SM,
                bgcolor=Theme.BG_SECONDARY,
                margin=ft.margin.only(bottom=5),
                content=ft.Row(
                    controls=[
                        entries['mode'],
                        entries['effet'],
                        entries['cause'],
                        entries['g'],
                        entries['o'],
                        entries['d'],
                        entries['ipr'],
                        entries['action'],
                    ],
                ),
            )
        
        rows = [create_amdec_row(i) for i in range(5)]
        
        self.ipr_summary = ft.Text("IPR Max: -- | Critiques: 0", color=Theme.TEXT_PRIMARY)
        
        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                # Header info
                create_card(
                    content=ft.Column(
                        controls=[
                            ft.Text("📊 AMDEC - Analyse des Modes de Défaillance", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                            ft.Text("IPR = Gravité × Occurrence × Détection  |  Échelles 1-10  |  IPR critique > 100", size=12, color=Theme.TEXT_MUTED),
                        ],
                    ),
                    padding=15,
                ),
                
                ft.Container(height=20),
                
                # Table header
                ft.Container(
                    padding=10,
                    border_radius=Styles.RADIUS_SM,
                    bgcolor=Theme.SECONDARY,
                    content=ft.Row(
                        controls=[
                            ft.Text("Mode", width=150, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            ft.Text("Effet", width=120, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            ft.Text("Cause", width=120, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            ft.Text("G", width=50, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            ft.Text("O", width=50, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            ft.Text("D", width=50, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            ft.Text("IPR", width=60, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            ft.Text("Action", width=150, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                ),
                
                # Rows
                *rows,
                
                ft.Container(height=15),
                
                # Summary & Actions
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        self.ipr_summary,
                        ft.Row(
                            controls=[
                                create_button("🔄 Calculer IPR", style="secondary", on_click=self._calculate_ipr),
                                create_button("💾 Sauvegarder", style="success", on_click=lambda e: self._save_analysis("amdec")),
                            ],
                        ),
                    ],
                ),
            ],
        )
    
    def _calculate_ipr(self, e):
        max_ipr = 0
        critical = 0
        
        for row in self.amdec_rows:
            try:
                g = int(row['g'].value or 0)
                o = int(row['o'].value or 0)
                d = int(row['d'].value or 0)
                ipr = g * o * d
                
                row['ipr'].content.value = str(ipr) if ipr > 0 else "--"
                
                if ipr > 100:
                    row['ipr'].bgcolor = Theme.DANGER
                    critical += 1
                elif ipr > 50:
                    row['ipr'].bgcolor = Theme.WARNING
                else:
                    row['ipr'].bgcolor = Theme.BG_TERTIARY
                
                row['ipr'].update()
                max_ipr = max(max_ipr, ipr)
            except ValueError:
                pass
        
        self.ipr_summary.value = f"IPR Max: {max_ipr} | Critiques (>100): {critical}"
        self.ipr_summary.update()
    
    # ========== 8D ==========
    def _build_8d(self) -> ft.Control:
        disciplines = [
            ("D1", "🏢 Équipe", "Constitution de l'équipe", Theme.DANGER),
            ("D2", "📝 Problème", "Description QQOQCCP", Theme.WARNING),
            ("D3", "🛡️ Containment", "Actions immédiates", "#F97316"),
            ("D4", "🔍 Cause racine", "Identification", Theme.SUCCESS),
            ("D5", "✅ Actions correctives", "Choix et vérification", Theme.PRIMARY),
            ("D6", "🚀 Mise en œuvre", "Implémentation", "#6366F1"),
            ("D7", "🔒 Prévention", "Éviter récurrence", Theme.SECONDARY),
            ("D8", "🎉 Clôture", "Capitalisation", "#EC4899"),
        ]
        
        self.d8_entries = {}
        d_controls = []
        
        for d_id, title, desc, color in disciplines:
            entry = create_text_field(desc, multiline=True, min_lines=2)
            self.d8_entries[d_id] = entry
            
            d_controls.append(
                ft.Container(
                    padding=15,
                    border_radius=Styles.RADIUS_MD,
                    bgcolor=Theme.BG_SECONDARY,
                    margin=ft.margin.only(bottom=10),
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        padding=ft.padding.symmetric(5, 10),
                                        border_radius=Styles.RADIUS_SM,
                                        bgcolor=color,
                                        content=ft.Text(d_id, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                    ),
                                    ft.Text(title, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                                ],
                            ),
                            entry,
                        ],
                    ),
                )
            )
        
        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                create_card(
                    content=ft.Text("📋 Méthode 8D - Résolution de Problèmes", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                    padding=15,
                ),
                ft.Container(height=15),
                *d_controls,
                ft.Container(height=15),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        create_button("💾 Sauvegarder le rapport 8D", style="success", on_click=lambda e: self._save_analysis("8d")),
                    ],
                ),
            ],
        )
    
    # ========== PARETO ==========
    def _build_pareto(self) -> ft.Control:
        self.pareto_rows = []
        
        def create_pareto_row(index: int) -> ft.Container:
            entries = {
                'cause': create_text_field(f"Cause {index+1}", width=250),
                'freq': create_text_field("Fréq.", width=80),
                'cumul': ft.Container(
                    width=80,
                    height=40,
                    bgcolor=Theme.BG_TERTIARY,
                    border_radius=Styles.RADIUS_SM,
                    alignment=ft.alignment.center,
                    content=ft.Text("--%", color=Theme.TEXT_PRIMARY),
                ),
                'bar': ft.Container(
                    width=200,
                    height=25,
                    bgcolor=Theme.BG_TERTIARY,
                    border_radius=Styles.RADIUS_SM,
                    content=ft.Container(width=0, bgcolor=Theme.PRIMARY, border_radius=Styles.RADIUS_SM),
                ),
            }
            self.pareto_rows.append(entries)
            
            return ft.Container(
                padding=10,
                border_radius=Styles.RADIUS_SM,
                bgcolor=Theme.BG_SECONDARY,
                margin=ft.margin.only(bottom=5),
                content=ft.Row(
                    controls=[
                        entries['cause'],
                        entries['freq'],
                        entries['cumul'],
                        entries['bar'],
                    ],
                ),
            )
        
        rows = [create_pareto_row(i) for i in range(8)]
        
        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                create_card(
                    content=ft.Column(
                        controls=[
                            ft.Text("📊 Analyse Pareto (80/20)", size=18, weight=ft.FontWeight.BOLD, color=Theme.TEXT_PRIMARY),
                            ft.Text("💡 80% des effets proviennent de 20% des causes", size=12, color=Theme.TEXT_MUTED),
                        ],
                    ),
                    padding=15,
                ),
                
                ft.Container(height=20),
                
                # Header
                ft.Container(
                    padding=10,
                    border_radius=Styles.RADIUS_SM,
                    bgcolor=Theme.PRIMARY,
                    content=ft.Row(
                        controls=[
                            ft.Text("Cause", width=250, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            ft.Text("Fréq.", width=80, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            ft.Text("% Cum.", width=80, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            ft.Text("Barre", width=200, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                ),
                
                *rows,
                
                ft.Container(height=15),
                
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        create_button("🔄 Calculer Pareto", style="secondary", on_click=self._calculate_pareto),
                        create_button("💾 Sauvegarder", style="success", on_click=lambda e: self._save_analysis("pareto")),
                    ],
                ),
            ],
        )
    
    def _calculate_pareto(self, e):
        data = []
        for row in self.pareto_rows:
            cause = row['cause'].value
            try:
                freq = int(row['freq'].value or 0)
            except ValueError:
                freq = 0
            if cause and freq > 0:
                data.append((cause, freq, row))
        
        if not data:
            return
        
        data.sort(key=lambda x: x[1], reverse=True)
        total = sum(d[1] for d in data)
        max_freq = data[0][1]
        
        cumul = 0
        for cause, freq, row in data:
            cumul += freq
            pct = (cumul / total) * 100
            bar_width = int((freq / max_freq) * 190)
            
            row['cumul'].content.value = f"{pct:.0f}%"
            row['bar'].content.width = bar_width
            
            if pct <= 80:
                row['bar'].content.bgcolor = "#EC4899"
            else:
                row['bar'].content.bgcolor = Theme.TEXT_MUTED
            
            row['cumul'].update()
            row['bar'].update()
    
    # ========== SAVE ==========
    def _save_analysis(self, method: str):
        data = {"method": method}
        
        if method == "5why":
            data["problem"] = self.problem_field.value
            data["whys"] = [(q.value, a.value) for q, a in self.why_entries]
            data["root_cause"] = self.root_cause_field.value
        
        elif method == "ishikawa":
            data["effect"] = self.effect_field.value
            data["categories"] = {k: [e.value for e in v] for k, v in self.ishikawa_entries.items()}
            data["synthesis"] = self.ishikawa_synth.value
        
        elif method == "amdec":
            data["rows"] = []
            for row in self.amdec_rows:
                data["rows"].append({
                    'mode': row['mode'].value,
                    'effet': row['effet'].value,
                    'cause': row['cause'].value,
                    'g': row['g'].value,
                    'o': row['o'].value,
                    'd': row['d'].value,
                    'action': row['action'].value,
                })
        
        elif method == "8d":
            for d_id, entry in self.d8_entries.items():
                data[d_id] = entry.value
        
        elif method == "pareto":
            data["items"] = []
            for row in self.pareto_rows:
                if row['cause'].value:
                    data["items"].append({
                        'cause': row['cause'].value,
                        'frequency': row['freq'].value,
                    })
        
        try:
            if self.nc_id:
                self.db.save_analysis(self.nc_id, method, json.dumps(data), self.user['id'])
            create_snackbar(self.page, "✅ Analyse sauvegardée!", "success")
        except Exception as ex:
            create_snackbar(self.page, f"Erreur: {ex}", "error")

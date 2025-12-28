# -*- coding: utf-8 -*-
"""
Outils d'Analyse des Causes - Page interactive
Méthodes : 5 Pourquoi, Ishikawa, AMDEC, 8D, Pareto
"""

import customtkinter as ctk
from typing import Callable, Optional, Dict, List, Any
from ui.utils import ModernTheme
import json
from datetime import datetime


class AnalysisToolsPage(ctk.CTkFrame):
    """Page des outils d'analyse des causes."""
    
    def __init__(self, parent, nc_data: Optional[Dict] = None, on_back: Callable = None, on_save: Callable = None, **kwargs):
        super().__init__(parent, fg_color=ModernTheme.BG_PRIMARY, **kwargs)
        
        self.nc_data = nc_data or {}
        self.on_back = on_back
        self.on_save = on_save
        self.current_method = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._build_header()
        self._build_content()
    
    def _build_header(self):
        """En-tête avec sélection de méthode."""
        header = ctk.CTkFrame(self, fg_color=ModernTheme.BG_SECONDARY, corner_radius=0, height=80)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        
        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Retour
        if self.on_back:
            ctk.CTkButton(inner, text="← Retour", fg_color="transparent", hover_color=ModernTheme.BG_TERTIARY, 
                         text_color=ModernTheme.TEXT_SECONDARY, width=80, command=self.on_back).pack(side="left")
        
        # Titre
        title_frame = ctk.CTkFrame(inner, fg_color="transparent")
        title_frame.pack(side="left", padx=20)
        ctk.CTkLabel(title_frame, text="🔬 Analyse des Causes", font=ctk.CTkFont(size=20, weight="bold"),
                    text_color=ModernTheme.TEXT_PRIMARY).pack(anchor="w")
        
        nc_ref = self.nc_data.get('reference', 'Nouvelle analyse')
        ctk.CTkLabel(title_frame, text=f"NC: {nc_ref}", font=ctk.CTkFont(size=11),
                    text_color=ModernTheme.TEXT_MUTED).pack(anchor="w")
        
        # Sélecteur de méthode
        method_frame = ctk.CTkFrame(inner, fg_color="transparent")
        method_frame.pack(side="right")
        
        ctk.CTkLabel(method_frame, text="Méthode :", font=ctk.CTkFont(size=12),
                    text_color=ModernTheme.TEXT_SECONDARY).pack(side="left", padx=(0, 10))
        
        self.method_selector = ctk.CTkSegmentedButton(
            method_frame,
            values=["5 Pourquoi", "Ishikawa", "AMDEC", "8D", "Pareto"],
            command=self._on_method_change,
            font=ctk.CTkFont(size=12),
            selected_color=ModernTheme.PRIMARY,
            selected_hover_color="#2563EB"
        )
        self.method_selector.set("5 Pourquoi")
        self.method_selector.pack(side="left")
    
    def _build_content(self):
        """Zone de contenu principale."""
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Afficher la méthode par défaut
        self._show_5why()
    
    def _clear_content(self):
        """Nettoie la zone de contenu."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _on_method_change(self, method: str):
        """Change de méthode d'analyse."""
        self._clear_content()
        self.current_method = method
        
        methods = {
            "5 Pourquoi": self._show_5why,
            "Ishikawa": self._show_ishikawa,
            "AMDEC": self._show_amdec,
            "8D": self._show_8d,
            "Pareto": self._show_pareto
        }
        methods.get(method, self._show_5why)()
    
    # ========== 5 POURQUOI ==========
    def _show_5why(self):
        """Affiche l'outil 5 Pourquoi."""
        container = ctk.CTkFrame(self.content_frame, fg_color=ModernTheme.BG_SECONDARY, corner_radius=15)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        
        # Titre
        header = ctk.CTkFrame(container, fg_color=ModernTheme.PRIMARY, corner_radius=15, height=60)
        header.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        header.grid_propagate(False)
        
        ctk.CTkLabel(header, text="❓ Méthode des 5 Pourquoi", font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="white").pack(expand=True)
        
        # Description
        desc = ctk.CTkLabel(container, text="Identifiez la cause racine en posant 'Pourquoi ?' jusqu'à 5 fois",
                           font=ctk.CTkFont(size=12), text_color=ModernTheme.TEXT_MUTED)
        desc.grid(row=1, column=0, pady=10)
        
        # Problème initial
        prob_frame = ctk.CTkFrame(container, fg_color=ModernTheme.BG_TERTIARY, corner_radius=10)
        prob_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(prob_frame, text="🎯 Problème initial", font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=ModernTheme.TEXT_PRIMARY).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.problem_entry = ctk.CTkTextbox(prob_frame, height=60, corner_radius=8,
                                            fg_color=ModernTheme.BG_PRIMARY)
        self.problem_entry.pack(fill="x", padx=15, pady=(0, 15))
        if self.nc_data.get('description'):
            self.problem_entry.insert("1.0", self.nc_data['description'])
        
        # Les 5 Pourquoi
        why_container = ctk.CTkScrollableFrame(container, fg_color="transparent")
        why_container.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        container.grid_rowconfigure(3, weight=1)
        
        self.why_entries = []
        colors = ["#EF4444", "#F59E0B", "#10B981", "#3B82F6", "#8B5CF6"]
        
        for i in range(5):
            why_frame = ctk.CTkFrame(why_container, fg_color="transparent")
            why_frame.pack(fill="x", pady=8, padx=10)
            
            # Numéro
            num_frame = ctk.CTkFrame(why_frame, fg_color=colors[i], width=50, height=50, corner_radius=25)
            num_frame.pack(side="left")
            num_frame.pack_propagate(False)
            ctk.CTkLabel(num_frame, text=f"P{i+1}", font=ctk.CTkFont(size=16, weight="bold"),
                        text_color="white").pack(expand=True)
            
            # Flèche
            if i > 0:
                arrow = ctk.CTkLabel(why_frame, text="↓", font=ctk.CTkFont(size=20),
                                    text_color=ModernTheme.TEXT_MUTED)
                arrow.place(relx=0.03, y=-15)
            
            # Champs
            fields_frame = ctk.CTkFrame(why_frame, fg_color=ModernTheme.BG_TERTIARY, corner_radius=10)
            fields_frame.pack(side="left", fill="x", expand=True, padx=15)
            
            ctk.CTkLabel(fields_frame, text=f"Pourquoi {i+1} ?", font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=colors[i]).pack(anchor="w", padx=15, pady=(10, 3))
            
            why_entry = ctk.CTkEntry(fields_frame, placeholder_text=f"Pourquoi ce problème se produit-il ?",
                                     height=40, corner_radius=8, fg_color=ModernTheme.BG_PRIMARY)
            why_entry.pack(fill="x", padx=15, pady=(0, 5))
            
            ctk.CTkLabel(fields_frame, text="Réponse :", font=ctk.CTkFont(size=11),
                        text_color=ModernTheme.TEXT_MUTED).pack(anchor="w", padx=15)
            
            answer_entry = ctk.CTkEntry(fields_frame, placeholder_text="La réponse identifie la cause...",
                                        height=40, corner_radius=8, fg_color=ModernTheme.BG_PRIMARY)
            answer_entry.pack(fill="x", padx=15, pady=(0, 15))
            
            self.why_entries.append((why_entry, answer_entry))
        
        # Cause racine
        root_frame = ctk.CTkFrame(container, fg_color="#7C3AED", corner_radius=10)
        root_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=15)
        
        ctk.CTkLabel(root_frame, text="🎯 CAUSE RACINE IDENTIFIÉE", font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="white").pack(pady=(15, 5))
        
        self.root_cause_entry = ctk.CTkEntry(root_frame, placeholder_text="Synthèse de la cause racine...",
                                             height=45, corner_radius=8, fg_color="white", text_color="#1F2937")
        self.root_cause_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Bouton sauvegarder
        ctk.CTkButton(container, text="💾 Sauvegarder l'analyse", fg_color=ModernTheme.SUCCESS,
                     hover_color="#059669", height=45, corner_radius=10,
                     command=lambda: self._save_analysis("5why")).grid(row=5, column=0, pady=15)
    
    # ========== ISHIKAWA ==========
    def _show_ishikawa(self):
        """Affiche le diagramme d'Ishikawa (arêtes de poisson)."""
        container = ctk.CTkFrame(self.content_frame, fg_color=ModernTheme.BG_SECONDARY, corner_radius=15)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)
        
        # Titre
        header = ctk.CTkFrame(container, fg_color="#0891B2", corner_radius=15, height=60)
        header.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        header.grid_propagate(False)
        ctk.CTkLabel(header, text="🐟 Diagramme d'Ishikawa (Causes-Effet)", 
                    font=ctk.CTkFont(size=18, weight="bold"), text_color="white").pack(expand=True)
        
        # Effet (tête du poisson)
        effect_frame = ctk.CTkFrame(container, fg_color=ModernTheme.DANGER, corner_radius=10)
        effect_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=15)
        
        ctk.CTkLabel(effect_frame, text="🎯 EFFET / PROBLÈME", font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="white").pack(anchor="w", padx=15, pady=(10, 5))
        self.effect_entry = ctk.CTkEntry(effect_frame, placeholder_text="Décrivez le problème à analyser...",
                                         height=40, corner_radius=8, fg_color="white", text_color="#1F2937")
        self.effect_entry.pack(fill="x", padx=15, pady=(0, 15))
        if self.nc_data.get('description'):
            self.effect_entry.insert(0, self.nc_data['description'][:100])
        
        # Les 6M
        categories_frame = ctk.CTkScrollableFrame(container, fg_color="transparent")
        categories_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configuration 2 colonnes
        categories_frame.grid_columnconfigure((0, 1), weight=1)
        
        categories = [
            ("👷 Main d'œuvre", "Matiere", "#EF4444", "Compétences, formation, erreur humaine..."),
            ("⚙️ Matériel", "Materiel", "#F59E0B", "Machines, outils, équipements..."),
            ("📦 Matière", "Matiere", "#10B981", "Matières premières, composants..."),
            ("📋 Méthode", "Methode", "#3B82F6", "Procédures, instructions, processus..."),
            ("🌍 Milieu", "Milieu", "#8B5CF6", "Environnement, conditions de travail..."),
            ("📏 Mesure", "Mesure", "#EC4899", "Instruments, calibration, contrôle...")
        ]
        
        self.ishikawa_entries = {}
        
        for idx, (name, key, color, placeholder) in enumerate(categories):
            row = idx // 2
            col = idx % 2
            
            cat_frame = ctk.CTkFrame(categories_frame, fg_color=ModernTheme.BG_TERTIARY, corner_radius=12)
            cat_frame.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
            
            # Titre catégorie
            title_bar = ctk.CTkFrame(cat_frame, fg_color=color, corner_radius=8, height=40)
            title_bar.pack(fill="x", padx=5, pady=5)
            title_bar.pack_propagate(False)
            ctk.CTkLabel(title_bar, text=name, font=ctk.CTkFont(size=13, weight="bold"),
                        text_color="white").pack(expand=True)
            
            # Zone de causes (3 lignes)
            causes_entries = []
            for i in range(3):
                entry = ctk.CTkEntry(cat_frame, placeholder_text=f"Cause {i+1}: {placeholder}",
                                    height=35, corner_radius=6, fg_color=ModernTheme.BG_PRIMARY)
                entry.pack(fill="x", padx=10, pady=3)
                causes_entries.append(entry)
            
            # Bouton ajouter
            ctk.CTkButton(cat_frame, text="+ Ajouter cause", fg_color="transparent",
                         hover_color=color, text_color=color, height=28,
                         command=lambda f=cat_frame, c=color: self._add_ishikawa_cause(f, c)).pack(pady=5)
            
            self.ishikawa_entries[key] = causes_entries
        
        # Synthèse
        synth_frame = ctk.CTkFrame(container, fg_color="#0891B2", corner_radius=10)
        synth_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        ctk.CTkLabel(synth_frame, text="📊 SYNTHÈSE - Causes principales identifiées",
                    font=ctk.CTkFont(size=13, weight="bold"), text_color="white").pack(pady=(10, 5))
        self.ishikawa_synth = ctk.CTkTextbox(synth_frame, height=60, corner_radius=8,
                                             fg_color="white", text_color="#1F2937")
        self.ishikawa_synth.pack(fill="x", padx=15, pady=(0, 15))
        
        # Bouton sauvegarder
        ctk.CTkButton(container, text="💾 Sauvegarder le diagramme", fg_color=ModernTheme.SUCCESS,
                     hover_color="#059669", height=45, corner_radius=10,
                     command=lambda: self._save_analysis("ishikawa")).grid(row=4, column=0, pady=15)
    
    def _add_ishikawa_cause(self, parent_frame, color):
        """Ajoute une ligne de cause."""
        entry = ctk.CTkEntry(parent_frame, placeholder_text="Nouvelle cause...",
                            height=35, corner_radius=6, fg_color=ModernTheme.BG_PRIMARY)
        entry.pack(fill="x", padx=10, pady=3, before=parent_frame.winfo_children()[-1])
    
    # ========== AMDEC ==========
    def _show_amdec(self):
        """Affiche la grille AMDEC."""
        container = ctk.CTkFrame(self.content_frame, fg_color=ModernTheme.BG_SECONDARY, corner_radius=15)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)
        
        # Titre
        header = ctk.CTkFrame(container, fg_color="#7C3AED", corner_radius=15, height=60)
        header.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        header.grid_propagate(False)
        ctk.CTkLabel(header, text="📊 AMDEC - Analyse des Modes de Défaillance", 
                    font=ctk.CTkFont(size=18, weight="bold"), text_color="white").pack(expand=True)
        
        # Légende IPR
        legend = ctk.CTkFrame(container, fg_color=ModernTheme.BG_TERTIARY, corner_radius=10)
        legend.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        legend_inner = ctk.CTkFrame(legend, fg_color="transparent")
        legend_inner.pack(pady=10)
        
        ctk.CTkLabel(legend_inner, text="IPR = Gravité × Occurrence × Détection",
                    font=ctk.CTkFont(size=12, weight="bold"), text_color=ModernTheme.TEXT_PRIMARY).pack()
        ctk.CTkLabel(legend_inner, text="Échelles : 1 (faible) à 10 (élevé)  |  IPR critique > 100",
                    font=ctk.CTkFont(size=11), text_color=ModernTheme.TEXT_MUTED).pack()
        
        # Tableau AMDEC
        table_frame = ctk.CTkScrollableFrame(container, fg_color="transparent")
        table_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        # En-têtes
        headers_frame = ctk.CTkFrame(table_frame, fg_color="#7C3AED", corner_radius=8, height=45)
        headers_frame.pack(fill="x", padx=5, pady=(0, 10))
        headers_frame.pack_propagate(False)
        
        headers = ["Mode défaillance", "Effet", "Cause", "G", "O", "D", "IPR", "Action"]
        widths = [150, 120, 120, 40, 40, 40, 50, 150]
        
        for h, w in zip(headers, widths):
            ctk.CTkLabel(headers_frame, text=h, font=ctk.CTkFont(size=11, weight="bold"),
                        text_color="white", width=w).pack(side="left", padx=2, pady=10)
        
        # Lignes AMDEC
        self.amdec_rows = []
        for i in range(5):
            self._add_amdec_row(table_frame, i)
        
        # Bouton ajouter ligne
        ctk.CTkButton(table_frame, text="➕ Ajouter une ligne", fg_color=ModernTheme.BG_TERTIARY,
                     hover_color="#7C3AED", text_color=ModernTheme.TEXT_PRIMARY, height=35,
                     command=lambda: self._add_amdec_row(table_frame, len(self.amdec_rows))).pack(pady=10)
        
        # Résumé
        summary_frame = ctk.CTkFrame(container, fg_color=ModernTheme.BG_TERTIARY, corner_radius=10)
        summary_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        summary_inner = ctk.CTkFrame(summary_frame, fg_color="transparent")
        summary_inner.pack(pady=15, padx=15)
        
        self.ipr_max_label = ctk.CTkLabel(summary_inner, text="IPR Max: --",
                                          font=ctk.CTkFont(size=14, weight="bold"),
                                          text_color=ModernTheme.TEXT_PRIMARY)
        self.ipr_max_label.pack(side="left", padx=20)
        
        self.critical_count_label = ctk.CTkLabel(summary_inner, text="Critiques (>100): 0",
                                                  font=ctk.CTkFont(size=14),
                                                  text_color=ModernTheme.DANGER)
        self.critical_count_label.pack(side="left", padx=20)
        
        ctk.CTkButton(summary_inner, text="🔄 Calculer IPR", fg_color=ModernTheme.PRIMARY,
                     width=120, command=self._calculate_ipr).pack(side="left", padx=20)
        
        # Bouton sauvegarder
        ctk.CTkButton(container, text="💾 Sauvegarder l'AMDEC", fg_color=ModernTheme.SUCCESS,
                     hover_color="#059669", height=45, corner_radius=10,
                     command=lambda: self._save_analysis("amdec")).grid(row=4, column=0, pady=15)
    
    def _add_amdec_row(self, parent, index):
        """Ajoute une ligne au tableau AMDEC."""
        row_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.BG_TERTIARY, corner_radius=8, height=50)
        row_frame.pack(fill="x", padx=5, pady=2)
        row_frame.pack_propagate(False)
        
        entries = {}
        
        # Mode défaillance
        entries['mode'] = ctk.CTkEntry(row_frame, width=145, height=35, corner_radius=6,
                                       placeholder_text="Mode de défaillance")
        entries['mode'].pack(side="left", padx=3, pady=7)
        
        # Effet
        entries['effet'] = ctk.CTkEntry(row_frame, width=115, height=35, corner_radius=6,
                                        placeholder_text="Effet")
        entries['effet'].pack(side="left", padx=3)
        
        # Cause
        entries['cause'] = ctk.CTkEntry(row_frame, width=115, height=35, corner_radius=6,
                                        placeholder_text="Cause")
        entries['cause'].pack(side="left", padx=3)
        
        # G, O, D
        for key in ['g', 'o', 'd']:
            entries[key] = ctk.CTkEntry(row_frame, width=38, height=35, corner_radius=6,
                                        placeholder_text="1-10")
            entries[key].pack(side="left", padx=2)
        
        # IPR (calculé)
        entries['ipr'] = ctk.CTkLabel(row_frame, text="--", width=45, height=35,
                                      fg_color=ModernTheme.BG_PRIMARY, corner_radius=6,
                                      font=ctk.CTkFont(size=12, weight="bold"))
        entries['ipr'].pack(side="left", padx=3)
        
        # Action
        entries['action'] = ctk.CTkEntry(row_frame, width=145, height=35, corner_radius=6,
                                         placeholder_text="Action corrective")
        entries['action'].pack(side="left", padx=3)
        
        self.amdec_rows.append(entries)
    
    def _calculate_ipr(self):
        """Calcule les IPR."""
        max_ipr = 0
        critical = 0
        
        for row in self.amdec_rows:
            try:
                g = int(row['g'].get() or 0)
                o = int(row['o'].get() or 0)
                d = int(row['d'].get() or 0)
                ipr = g * o * d
                
                row['ipr'].configure(text=str(ipr) if ipr > 0 else "--")
                
                if ipr > 100:
                    row['ipr'].configure(fg_color=ModernTheme.DANGER, text_color="white")
                    critical += 1
                elif ipr > 50:
                    row['ipr'].configure(fg_color=ModernTheme.WARNING, text_color="white")
                else:
                    row['ipr'].configure(fg_color=ModernTheme.BG_PRIMARY, text_color=ModernTheme.TEXT_PRIMARY)
                
                max_ipr = max(max_ipr, ipr)
            except ValueError:
                pass
        
        self.ipr_max_label.configure(text=f"IPR Max: {max_ipr}")
        self.critical_count_label.configure(text=f"Critiques (>100): {critical}")
    
    # ========== 8D ==========
    def _show_8d(self):
        """Affiche la méthode 8D."""
        container = ctk.CTkFrame(self.content_frame, fg_color=ModernTheme.BG_SECONDARY, corner_radius=15)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        
        # Titre
        header = ctk.CTkFrame(container, fg_color="#059669", corner_radius=15, height=60)
        header.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        header.grid_propagate(False)
        ctk.CTkLabel(header, text="📋 Méthode 8D - Résolution de Problèmes", 
                    font=ctk.CTkFont(size=18, weight="bold"), text_color="white").pack(expand=True)
        
        # Les 8 disciplines
        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        disciplines = [
            ("D1", "🏢 Équipe", "Constitution de l'équipe pluridisciplinaire", "#EF4444"),
            ("D2", "📝 Problème", "Description détaillée du problème (QQOQCCP)", "#F59E0B"),
            ("D3", "🛡️ Containment", "Actions de containment immédiates", "#F97316"),
            ("D4", "🔍 Cause racine", "Identification et vérification de la cause racine", "#10B981"),
            ("D5", "✅ Actions correctives", "Choix et vérification des actions correctives", "#3B82F6"),
            ("D6", "🚀 Mise en œuvre", "Implémentation des actions permanentes", "#6366F1"),
            ("D7", "🔒 Prévention", "Actions préventives pour éviter récurrence", "#8B5CF6"),
            ("D8", "🎉 Clôture", "Félicitations de l'équipe et capitalisation", "#EC4899")
        ]
        
        self.d8_entries = {}
        
        for d_id, icon_title, description, color in disciplines:
            d_frame = ctk.CTkFrame(scroll, fg_color=ModernTheme.BG_TERTIARY, corner_radius=12)
            d_frame.pack(fill="x", pady=6, padx=5)
            
            # En-tête
            header_row = ctk.CTkFrame(d_frame, fg_color="transparent")
            header_row.pack(fill="x", padx=15, pady=(10, 5))
            
            badge = ctk.CTkFrame(header_row, fg_color=color, width=45, height=30, corner_radius=5)
            badge.pack(side="left")
            badge.pack_propagate(False)
            ctk.CTkLabel(badge, text=d_id, font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="white").pack(expand=True)
            
            ctk.CTkLabel(header_row, text=f"  {icon_title}", font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=ModernTheme.TEXT_PRIMARY).pack(side="left")
            
            ctk.CTkLabel(header_row, text=description, font=ctk.CTkFont(size=11),
                        text_color=ModernTheme.TEXT_MUTED).pack(side="right")
            
            # Zone de texte
            text_entry = ctk.CTkTextbox(d_frame, height=70, corner_radius=8,
                                        fg_color=ModernTheme.BG_PRIMARY)
            text_entry.pack(fill="x", padx=15, pady=(0, 15))
            
            self.d8_entries[d_id] = text_entry
        
        # Bouton sauvegarder
        ctk.CTkButton(container, text="💾 Sauvegarder le rapport 8D", fg_color=ModernTheme.SUCCESS,
                     hover_color="#059669", height=45, corner_radius=10,
                     command=lambda: self._save_analysis("8d")).grid(row=2, column=0, pady=15)
    
    # ========== PARETO ==========
    def _show_pareto(self):
        """Affiche l'analyse Pareto."""
        container = ctk.CTkFrame(self.content_frame, fg_color=ModernTheme.BG_SECONDARY, corner_radius=15)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)
        
        # Titre
        header = ctk.CTkFrame(container, fg_color="#EC4899", corner_radius=15, height=60)
        header.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        header.grid_propagate(False)
        ctk.CTkLabel(header, text="📊 Analyse Pareto (80/20)", 
                    font=ctk.CTkFont(size=18, weight="bold"), text_color="white").pack(expand=True)
        
        # Description
        desc_frame = ctk.CTkFrame(container, fg_color=ModernTheme.BG_TERTIARY, corner_radius=10)
        desc_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        ctk.CTkLabel(desc_frame, text="💡 Principe : 80% des effets proviennent de 20% des causes",
                    font=ctk.CTkFont(size=12), text_color=ModernTheme.TEXT_MUTED).pack(pady=10)
        
        # Tableau des causes
        table_frame = ctk.CTkScrollableFrame(container, fg_color="transparent")
        table_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        # En-têtes
        headers_row = ctk.CTkFrame(table_frame, fg_color="#EC4899", corner_radius=8, height=45)
        headers_row.pack(fill="x", padx=5, pady=(0, 10))
        headers_row.pack_propagate(False)
        
        for h, w in [("Cause / Catégorie", 250), ("Fréquence", 80), ("% Cumulé", 80), ("Barre", 200)]:
            ctk.CTkLabel(headers_row, text=h, font=ctk.CTkFont(size=11, weight="bold"),
                        text_color="white", width=w).pack(side="left", padx=5, pady=10)
        
        # Lignes
        self.pareto_rows = []
        for i in range(8):
            self._add_pareto_row(table_frame, i)
        
        # Boutons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.grid(row=3, column=0, pady=10)
        
        ctk.CTkButton(btn_frame, text="🔄 Calculer Pareto", fg_color=ModernTheme.PRIMARY,
                     width=150, command=self._calculate_pareto).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="➕ Ajouter ligne", fg_color=ModernTheme.BG_TERTIARY,
                     text_color=ModernTheme.TEXT_PRIMARY, width=120,
                     command=lambda: self._add_pareto_row(table_frame, len(self.pareto_rows))).pack(side="left")
        
        # Bouton sauvegarder
        ctk.CTkButton(container, text="💾 Sauvegarder l'analyse Pareto", fg_color=ModernTheme.SUCCESS,
                     hover_color="#059669", height=45, corner_radius=10,
                     command=lambda: self._save_analysis("pareto")).grid(row=4, column=0, pady=15)
    
    def _add_pareto_row(self, parent, index):
        """Ajoute une ligne Pareto."""
        row_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.BG_TERTIARY, corner_radius=8, height=45)
        row_frame.pack(fill="x", padx=5, pady=2)
        row_frame.pack_propagate(False)
        
        entries = {}
        
        # Cause
        entries['cause'] = ctk.CTkEntry(row_frame, width=245, height=35, corner_radius=6,
                                        placeholder_text=f"Cause {index + 1}")
        entries['cause'].pack(side="left", padx=5, pady=5)
        
        # Fréquence
        entries['freq'] = ctk.CTkEntry(row_frame, width=75, height=35, corner_radius=6,
                                       placeholder_text="0")
        entries['freq'].pack(side="left", padx=5)
        
        # % Cumulé
        entries['cumul'] = ctk.CTkLabel(row_frame, text="--", width=75, height=35,
                                        fg_color=ModernTheme.BG_PRIMARY, corner_radius=6)
        entries['cumul'].pack(side="left", padx=5)
        
        # Barre visuelle
        bar_container = ctk.CTkFrame(row_frame, fg_color=ModernTheme.BG_PRIMARY, 
                                     width=195, height=25, corner_radius=4)
        bar_container.pack(side="left", padx=5)
        bar_container.pack_propagate(False)
        
        entries['bar'] = ctk.CTkFrame(bar_container, fg_color="#EC4899", width=0, height=25, corner_radius=4)
        entries['bar'].place(x=0, y=0)
        
        self.pareto_rows.append(entries)
    
    def _calculate_pareto(self):
        """Calcule et affiche Pareto."""
        # Collecter les données
        data = []
        for row in self.pareto_rows:
            cause = row['cause'].get().strip()
            try:
                freq = int(row['freq'].get() or 0)
            except ValueError:
                freq = 0
            if cause and freq > 0:
                data.append((cause, freq, row))
        
        if not data:
            return
        
        # Trier par fréquence décroissante
        data.sort(key=lambda x: x[1], reverse=True)
        total = sum(d[1] for d in data)
        
        cumul = 0
        for cause, freq, row in data:
            cumul += freq
            pct = (cumul / total) * 100
            
            row['cumul'].configure(text=f"{pct:.1f}%")
            
            # Barre proportionnelle
            bar_width = int((freq / data[0][1]) * 190)
            
            # Couleur selon zone 80/20
            if pct <= 80:
                row['bar'].configure(fg_color="#EC4899", width=bar_width)
            else:
                row['bar'].configure(fg_color=ModernTheme.TEXT_MUTED, width=bar_width)
    
    # ========== SAUVEGARDE ==========
    def _save_analysis(self, method: str):
        """Sauvegarde l'analyse."""
        analysis_data = {
            "method": method,
            "nc_reference": self.nc_data.get('reference', ''),
            "date": datetime.now().isoformat(),
            "data": {}
        }
        
        if method == "5why":
            analysis_data["data"]["problem"] = self.problem_entry.get("1.0", "end-1c")
            analysis_data["data"]["whys"] = []
            for why, answer in self.why_entries:
                analysis_data["data"]["whys"].append({
                    "question": why.get(),
                    "answer": answer.get()
                })
            analysis_data["data"]["root_cause"] = self.root_cause_entry.get()
        
        elif method == "ishikawa":
            analysis_data["data"]["effect"] = self.effect_entry.get()
            analysis_data["data"]["categories"] = {}
            for key, entries in self.ishikawa_entries.items():
                analysis_data["data"]["categories"][key] = [e.get() for e in entries if e.get()]
            analysis_data["data"]["synthesis"] = self.ishikawa_synth.get("1.0", "end-1c")
        
        elif method == "amdec":
            analysis_data["data"]["rows"] = []
            for row in self.amdec_rows:
                row_data = {
                    "mode": row['mode'].get(),
                    "effet": row['effet'].get(),
                    "cause": row['cause'].get(),
                    "g": row['g'].get(),
                    "o": row['o'].get(),
                    "d": row['d'].get(),
                    "action": row['action'].get()
                }
                if any(row_data.values()):
                    analysis_data["data"]["rows"].append(row_data)
        
        elif method == "8d":
            for d_id, entry in self.d8_entries.items():
                analysis_data["data"][d_id] = entry.get("1.0", "end-1c")
        
        elif method == "pareto":
            analysis_data["data"]["items"] = []
            for row in self.pareto_rows:
                if row['cause'].get():
                    analysis_data["data"]["items"].append({
                        "cause": row['cause'].get(),
                        "frequency": row['freq'].get()
                    })
        
        # Callback de sauvegarde
        if self.on_save:
            self.on_save(analysis_data)
        
        # Notification
        self._show_notification("✅ Analyse sauvegardée avec succès!")
    
    def _show_notification(self, message: str):
        """Affiche une notification."""
        notif = ctk.CTkFrame(self, fg_color=ModernTheme.SUCCESS, corner_radius=10)
        notif.place(relx=0.5, rely=0.95, anchor="center")
        
        ctk.CTkLabel(notif, text=message, font=ctk.CTkFont(size=13),
                    text_color="white").pack(padx=20, pady=10)
        
        self.after(3000, notif.destroy)

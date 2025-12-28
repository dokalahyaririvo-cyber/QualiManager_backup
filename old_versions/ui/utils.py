# -*- coding: utf-8 -*-
"""
QualiManager - Module d'utilitaires UI
Animations, chargement différé, effets visuels modernes
"""

import customtkinter as ctk
from typing import Callable, Optional, List, Any
import threading
import time


class UIAnimator:
    """Gestionnaire d'animations pour une UI fluide."""
    
    @staticmethod
    def fade_in(widget: ctk.CTkBaseClass, duration: int = 200, steps: int = 10):
        """
        Animation de fondu à l'apparition.
        
        Args:
            widget: Widget à animer
            duration: Durée en ms
            steps: Nombre d'étapes
        """
        try:
            # Pour les widgets qui supportent fg_color avec alpha
            delay = duration // steps
            for i in range(steps + 1):
                alpha = i / steps
                widget.after(i * delay, lambda a=alpha: widget.configure(
                    fg_color=widget.cget("fg_color")
                ) if widget.winfo_exists() else None)
        except:
            pass
    
    @staticmethod
    def slide_in_left(widget: ctk.CTkBaseClass, duration: int = 150):
        """Animation de glissement depuis la gauche."""
        try:
            widget.update_idletasks()
        except:
            pass


class DeferredLoader:
    """Chargeur différé pour améliorer la réactivité."""
    
    def __init__(self, parent: ctk.CTkBaseClass):
        self.parent = parent
        self.queue: List[tuple] = []
        self.is_loading = False
    
    def add(self, create_func: Callable, delay: int = 5):
        """
        Ajoute un widget à créer de manière différée.
        
        Args:
            create_func: Fonction de création du widget
            delay: Délai en ms entre chaque widget
        """
        self.queue.append((create_func, delay))
    
    def add_task(self, create_func: Callable, delay: int = 5):
        """Alias pour add() - compatibilité."""
        self.add(create_func, delay)
    
    def execute(self, on_complete: Optional[Callable] = None):
        """Exécute la création des widgets de manière différée."""
        if self.is_loading or not self.queue:
            return
        
        self.is_loading = True
        self._process_queue(0, on_complete)
    
    def _process_queue(self, index: int, on_complete: Optional[Callable]):
        """Traite la queue de manière récursive."""
        if index >= len(self.queue):
            self.is_loading = False
            self.queue.clear()
            if on_complete:
                on_complete()
            return
        
        create_func, delay = self.queue[index]
        try:
            create_func()
        except Exception as e:
            print(f"Erreur création widget: {e}")
        
        self.parent.after(delay, lambda: self._process_queue(index + 1, on_complete))


class ModernCard(ctk.CTkFrame):
    """Carte moderne avec effets de survol."""
    
    def __init__(
        self,
        parent,
        title: str = "",
        value: str = "",
        icon: str = "",
        color: str = "#3B82F6",
        subtitle: str = "",
        **kwargs
    ):
        # Couleurs par défaut
        self.default_bg = ("white", "#1E1E1E")
        self.hover_bg = ("#F8FAFC", "#2D2D2D")
        self.color = color
        self._content_frame = None
        
        super().__init__(
            parent,
            corner_radius=16,
            fg_color=self.default_bg,
            border_width=1,
            border_color=("#E2E8F0", "#333333"),
            **kwargs
        )
        
        # Bind pour les effets de survol
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        # Créer le contenu
        self._create_content(icon, title, value, subtitle)
    
    def _create_content(self, icon: str, title: str, value: str, subtitle: str):
        """Crée le contenu de la carte."""
        # Si un titre de section est fourni (mode formulaire)
        if title and not value and not icon:
            # En-tête de section
            header = ctk.CTkFrame(self, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=(12, 5))
            
            title_label = ctk.CTkLabel(
                header,
                text=title,
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=self.color
            )
            title_label.pack(anchor="w")
            
            # Cadre de contenu pour les formulaires
            self._content_frame = ctk.CTkFrame(self, fg_color="transparent")
            self._content_frame.pack(fill="both", expand=True, padx=5, pady=(0, 10))
        else:
            # Mode carte statistique
            content = ctk.CTkFrame(self, fg_color="transparent")
            content.pack(expand=True, fill="both", padx=20, pady=20)
            content.bind("<Enter>", self._on_enter)
            content.bind("<Leave>", self._on_leave)
            self._content_frame = content
            
            if icon:
                icon_label = ctk.CTkLabel(
                    content,
                    text=icon,
                    font=ctk.CTkFont(size=36)
                )
                icon_label.pack(pady=(0, 8))
                icon_label.bind("<Enter>", self._on_enter)
                icon_label.bind("<Leave>", self._on_leave)
            
            if value:
                value_label = ctk.CTkLabel(
                    content,
                    text=value,
                    font=ctk.CTkFont(size=38, weight="bold"),
                    text_color=self.color
                )
                value_label.pack()
                value_label.bind("<Enter>", self._on_enter)
                value_label.bind("<Leave>", self._on_leave)
            
            if title:
                title_label = ctk.CTkLabel(
                    content,
                    text=title,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=("#64748B", "#94A3B8")
                )
                title_label.pack(pady=(4, 0))
                title_label.bind("<Enter>", self._on_enter)
                title_label.bind("<Leave>", self._on_leave)
            
            if subtitle:
                sub_label = ctk.CTkLabel(
                    content,
                    text=subtitle,
                    font=ctk.CTkFont(size=11),
                    text_color=("#94A3B8", "#64748B")
                )
                sub_label.pack(pady=(2, 0))
                sub_label.bind("<Enter>", self._on_enter)
                sub_label.bind("<Leave>", self._on_leave)
    
    def get_content_frame(self) -> ctk.CTkFrame:
        """Retourne le frame de contenu pour y ajouter des widgets."""
        return self._content_frame
    
    def _on_enter(self, event):
        """Effet au survol."""
        self.configure(
            fg_color=self.hover_bg,
            border_color=(self.color, self.color)
        )
    
    def _on_leave(self, event):
        """Effet à la sortie."""
        self.configure(
            fg_color=self.default_bg,
            border_color=("#E2E8F0", "#333333")
        )


class ModernButton(ctk.CTkButton):
    """Bouton moderne avec animation de survol et styles prédéfinis."""
    
    # Styles prédéfinis
    STYLES = {
        "primary": {"fg_color": "#3B82F6", "hover_color": "#2563EB", "text_color": "white"},
        "secondary": {"fg_color": "#64748B", "hover_color": "#475569", "text_color": "white"},
        "success": {"fg_color": "#10B981", "hover_color": "#059669", "text_color": "white"},
        "danger": {"fg_color": "#EF4444", "hover_color": "#DC2626", "text_color": "white"},
        "warning": {"fg_color": "#F59E0B", "hover_color": "#D97706", "text_color": "white"},
        "info": {"fg_color": "#06B6D4", "hover_color": "#0891B2", "text_color": "white"},
    }
    
    def __init__(
        self,
        parent,
        text: str = "",
        icon: str = "",
        style: str = "primary",
        color: str = None,
        hover_color: str = None,
        **kwargs
    ):
        # Récupérer les couleurs du style ou utiliser les paramètres personnalisés
        style_config = self.STYLES.get(style, self.STYLES["primary"])
        
        fg_color = color or style_config["fg_color"]
        hover = hover_color or style_config["hover_color"]
        text_color = kwargs.pop("text_color", style_config["text_color"])
        
        display_text = f"{icon}  {text}" if icon else text
        
        super().__init__(
            parent,
            text=display_text,
            fg_color=fg_color,
            hover_color=hover,
            text_color=text_color,
            corner_radius=12,
            font=ctk.CTkFont(size=14, weight="bold"),
            **kwargs
        )


class ModernEntry(ctk.CTkEntry):
    """Champ de saisie moderne avec animation de focus."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            corner_radius=10,
            border_width=2,
            border_color=("#E2E8F0", "#333333"),
            fg_color=("white", "#1E1E1E"),
            **kwargs
        )
        
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, event):
        """Animation au focus."""
        self.configure(border_color=("#3B82F6", "#60A5FA"))
    
    def _on_focus_out(self, event):
        """Animation à la perte de focus."""
        self.configure(border_color=("#E2E8F0", "#333333"))


class ModernComboBox(ctk.CTkComboBox):
    """ComboBox moderne avec style amélioré."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            corner_radius=10,
            border_width=2,
            border_color=("#E2E8F0", "#333333"),
            button_color=("#3B82F6", "#2563EB"),
            button_hover_color=("#2563EB", "#1D4ED8"),
            dropdown_fg_color=("white", "#1E1E1E"),
            dropdown_hover_color=("#F1F5F9", "#2D2D2D"),
            **kwargs
        )


class ModernTextbox(ctk.CTkTextbox):
    """Zone de texte moderne."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            corner_radius=10,
            border_width=2,
            border_color=("#E2E8F0", "#333333"),
            fg_color=("white", "#1E1E1E"),
            **kwargs
        )
        
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
    
    def _on_focus_in(self, event):
        self.configure(border_color=("#3B82F6", "#60A5FA"))
    
    def _on_focus_out(self, event):
        self.configure(border_color=("#E2E8F0", "#333333"))


class LoadingSpinner(ctk.CTkFrame):
    """Indicateur de chargement animé."""
    
    def __init__(self, parent, size: int = 40, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.size = size
        self.angle = 0
        self.is_spinning = False
        
        self.canvas = ctk.CTkCanvas(
            self,
            width=size,
            height=size,
            bg=self._apply_appearance_mode(("white", "#1E1E1E")),
            highlightthickness=0
        )
        self.canvas.pack()
        
        self._draw_spinner()
    
    def _apply_appearance_mode(self, colors):
        """Applique le mode d'apparence."""
        mode = ctk.get_appearance_mode()
        if isinstance(colors, tuple):
            return colors[0] if mode == "Light" else colors[1]
        return colors
    
    def _draw_spinner(self):
        """Dessine le spinner."""
        self.canvas.delete("all")
        cx, cy = self.size // 2, self.size // 2
        r = self.size // 2 - 4
        
        # Arc de cercle
        import math
        start = self.angle
        extent = 270
        
        self.canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=start, extent=extent,
            style="arc", width=3,
            outline="#3B82F6"
        )
    
    def start(self):
        """Démarre l'animation."""
        self.is_spinning = True
        self._animate()
    
    def stop(self):
        """Arrête l'animation."""
        self.is_spinning = False
    
    def _animate(self):
        """Animation du spinner."""
        if not self.is_spinning:
            return
        
        self.angle = (self.angle + 15) % 360
        self._draw_spinner()
        self.after(30, self._animate)


class ProgressLoader(ctk.CTkFrame):
    """Barre de progression avec texte."""
    
    def __init__(self, parent, text: str = "Chargement...", **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=13),
            text_color=("#64748B", "#94A3B8")
        )
        self.label.pack(pady=(0, 8))
        
        self.progress = ctk.CTkProgressBar(
            self,
            width=300,
            height=6,
            corner_radius=3,
            fg_color=("#E2E8F0", "#333333"),
            progress_color="#3B82F6"
        )
        self.progress.pack()
        self.progress.set(0)
    
    def set_progress(self, value: float, text: str = None):
        """Met à jour la progression."""
        self.progress.set(value)
        if text:
            self.label.configure(text=text)
    
    def start_indeterminate(self):
        """Mode indéterminé."""
        self.progress.configure(mode="indeterminate")
        self.progress.start()
    
    def stop(self):
        """Arrête la progression."""
        self.progress.stop()
        self.progress.configure(mode="determinate")


class AsyncLoader:
    """Chargeur asynchrone pour opérations lourdes."""
    
    @staticmethod
    def run_async(func: Callable, callback: Callable, error_callback: Callable = None):
        """
        Exécute une fonction dans un thread séparé.
        
        Args:
            func: Fonction à exécuter
            callback: Callback avec le résultat
            error_callback: Callback en cas d'erreur
        """
        def wrapper():
            try:
                result = func()
                # Utiliser after pour revenir au thread principal
                callback(result)
            except Exception as e:
                if error_callback:
                    error_callback(e)
        
        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()


# Thèmes de couleurs modernes
class ModernTheme:
    """Thèmes de couleurs modernes."""
    
    # Couleurs principales
    PRIMARY = "#3B82F6"
    PRIMARY_HOVER = "#2563EB"
    PRIMARY_LIGHT = "#DBEAFE"
    
    SECONDARY = "#6366F1"
    SECONDARY_HOVER = "#4F46E5"
    
    SUCCESS = "#10B981"
    SUCCESS_HOVER = "#059669"
    SUCCESS_LIGHT = "#D1FAE5"
    
    WARNING = "#F59E0B"
    WARNING_HOVER = "#D97706"
    WARNING_LIGHT = "#FEF3C7"
    
    DANGER = "#EF4444"
    DANGER_HOVER = "#DC2626"
    DANGER_LIGHT = "#FEE2E2"
    
    INFO = "#06B6D4"
    INFO_HOVER = "#0891B2"
    INFO_LIGHT = "#CFFAFE"
    
    # Couleurs de texte
    TEXT_PRIMARY = "#1E293B"
    TEXT_SECONDARY = "#64748B"
    TEXT_MUTED = "#94A3B8"
    
    # Couleurs de fond
    BG_PRIMARY = "#FFFFFF"
    BG_SECONDARY = "#F8FAFC"
    BG_TERTIARY = "#F1F5F9"
    
    # Bordures
    BORDER = "#E2E8F0"
    BORDER_FOCUS = "#3B82F6"
    
    # Sidebar
    SIDEBAR_BG = "#0F172A"
    SIDEBAR_HOVER = "#1E293B"
    SIDEBAR_TEXT = "#F8FAFC"
    SIDEBAR_TEXT_MUTED = "#94A3B8"
    SIDEBAR_SEPARATOR = "#334155"
    SIDEBAR_HOVER = "#1E293B"
    SIDEBAR_ACTIVE = "#334155"

# -*- coding: utf-8 -*-
"""
QualiManager ERP QHSE - Thème et styles Material Design 3
Support Mode Sombre / Mode Clair
"""


class ThemeMode:
    """Mode du thème."""
    DARK = "dark"
    LIGHT = "light"


class Theme:
    """Thème moderne Material Design 3 avec support Dark/Light mode."""
    
    # Mode actuel (modifiable)
    _mode = ThemeMode.DARK
    
    # Couleurs primaires (fixes)
    PRIMARY = "#3B82F6"
    PRIMARY_LIGHT = "#60A5FA"
    PRIMARY_DARK = "#1D4ED8"
    
    SECONDARY = "#8B5CF6"
    SECONDARY_LIGHT = "#A78BFA"
    
    # Couleurs sémantiques (fixes)
    SUCCESS = "#10B981"
    SUCCESS_LIGHT = "#34D399"
    DANGER = "#EF4444"
    DANGER_LIGHT = "#F87171"
    WARNING = "#F59E0B"
    WARNING_LIGHT = "#FBBF24"
    INFO = "#06B6D4"
    INFO_LIGHT = "#22D3EE"
    
    # ========== MODE SOMBRE ==========
    # Fonds Dark
    BG_PRIMARY_DARK = "#0F172A"
    BG_SECONDARY_DARK = "#1E293B"
    BG_TERTIARY_DARK = "#334155"
    BG_CARD_DARK = "#1E293B"
    
    # Textes Dark
    TEXT_PRIMARY_DARK = "#F8FAFC"
    TEXT_SECONDARY_DARK = "#CBD5E1"
    TEXT_MUTED_DARK = "#64748B"
    
    # Surfaces Dark
    SURFACE_DARK = "#1E293B"
    SURFACE_VARIANT_DARK = "#334155"
    OUTLINE_DARK = "#475569"
    BORDER_DARK = "#475569"
    
    # ========== MODE CLAIR ==========
    # Fonds Light
    BG_PRIMARY_LIGHT = "#F8FAFC"
    BG_SECONDARY_LIGHT = "#FFFFFF"
    BG_TERTIARY_LIGHT = "#E2E8F0"
    BG_CARD_LIGHT = "#FFFFFF"
    
    # Textes Light
    TEXT_PRIMARY_LIGHT = "#0F172A"
    TEXT_SECONDARY_LIGHT = "#475569"
    TEXT_MUTED_LIGHT = "#94A3B8"
    
    # Surfaces Light
    SURFACE_LIGHT = "#FFFFFF"
    SURFACE_VARIANT_LIGHT = "#F1F5F9"
    OUTLINE_LIGHT = "#CBD5E1"
    BORDER_LIGHT = "#E2E8F0"
    
    # ========== PROPRIÉTÉS DYNAMIQUES ==========
    @classmethod
    def set_mode(cls, mode: str):
        """Change le mode du thème."""
        cls._mode = mode
    
    @classmethod
    def is_dark(cls) -> bool:
        """Vérifie si le mode sombre est actif."""
        return cls._mode == ThemeMode.DARK
    
    @classmethod
    def toggle(cls):
        """Bascule entre les modes."""
        cls._mode = ThemeMode.LIGHT if cls._mode == ThemeMode.DARK else ThemeMode.DARK
        # Mettre à jour toutes les propriétés de classe
        cls._update_theme_properties()
        return cls._mode
    
    @classmethod
    def init(cls):
        """Force l'initialisation des propriétés au démarrage."""
        cls._update_theme_properties()
    
    @classmethod
    def _update_theme_properties(cls):
        """Met à jour les propriétés de classe selon le mode actuel."""
        if cls._mode == ThemeMode.DARK:
            cls.BG_PRIMARY = cls.BG_PRIMARY_DARK
            cls.BG_SECONDARY = cls.BG_SECONDARY_DARK
            cls.BG_TERTIARY = cls.BG_TERTIARY_DARK
            cls.BG_CARD = cls.BG_CARD_DARK
            cls.TEXT_PRIMARY = cls.TEXT_PRIMARY_DARK
            cls.TEXT_SECONDARY = cls.TEXT_SECONDARY_DARK
            cls.TEXT_MUTED = cls.TEXT_MUTED_DARK
            cls.SURFACE = cls.SURFACE_DARK
            cls.SURFACE_VARIANT = cls.SURFACE_VARIANT_DARK
            cls.OUTLINE = cls.OUTLINE_DARK
            cls.BORDER = cls.BORDER_DARK
            cls.TEXT_INVERSE = "#F8FAFC"
            print(f"   ✅ Mode DARK appliqué - BG_PRIMARY={cls.BG_PRIMARY}")
        else:
            cls.BG_PRIMARY = cls.BG_PRIMARY_LIGHT
            cls.BG_SECONDARY = cls.BG_SECONDARY_LIGHT
            cls.BG_TERTIARY = cls.BG_TERTIARY_LIGHT
            cls.BG_CARD = cls.BG_CARD_LIGHT
            cls.TEXT_PRIMARY = cls.TEXT_PRIMARY_LIGHT
            cls.TEXT_SECONDARY = cls.TEXT_SECONDARY_LIGHT
            cls.TEXT_MUTED = cls.TEXT_MUTED_LIGHT
            cls.SURFACE = cls.SURFACE_LIGHT
            cls.SURFACE_VARIANT = cls.SURFACE_VARIANT_LIGHT
            cls.OUTLINE = cls.OUTLINE_LIGHT
            cls.BORDER = cls.BORDER_LIGHT
            cls.TEXT_INVERSE = "#0F172A"
            print(f"   ✅ Mode LIGHT appliqué - BG_PRIMARY={cls.BG_PRIMARY}")
    
    # Propriétés de compatibilité - INITIALISÉES EN DARK PAR DÉFAUT
    # Ces variables DOIVENT être mises à jour via _update_theme_properties()
    BG_PRIMARY = BG_PRIMARY_DARK
    BG_SECONDARY = BG_SECONDARY_DARK
    BG_TERTIARY = BG_TERTIARY_DARK
    BG_CARD = BG_CARD_DARK
    
    TEXT_PRIMARY = TEXT_PRIMARY_DARK
    TEXT_SECONDARY = TEXT_SECONDARY_DARK
    TEXT_MUTED = TEXT_MUTED_DARK
    TEXT_INVERSE = "#0F172A"
    
    SURFACE = SURFACE_DARK
    SURFACE_VARIANT = SURFACE_VARIANT_DARK
    OUTLINE = OUTLINE_DARK
    BORDER = BORDER_DARK
    
    # Gradients (pour les cartes)
    GRADIENT_PRIMARY = ["#3B82F6", "#1D4ED8"]
    GRADIENT_SUCCESS = ["#10B981", "#059669"]
    GRADIENT_DANGER = ["#EF4444", "#DC2626"]
    GRADIENT_WARNING = ["#F59E0B", "#D97706"]
    
    @classmethod
    def get_colors(cls) -> dict:
        """Retourne les couleurs selon le mode actuel."""
        if cls._mode == ThemeMode.DARK:
            return {
                'bg_primary': cls.BG_PRIMARY_DARK,
                'bg_secondary': cls.BG_SECONDARY_DARK,
                'bg_tertiary': cls.BG_TERTIARY_DARK,
                'bg_card': cls.BG_CARD_DARK,
                'text_primary': cls.TEXT_PRIMARY_DARK,
                'text_secondary': cls.TEXT_SECONDARY_DARK,
                'text_muted': cls.TEXT_MUTED_DARK,
                'surface': cls.SURFACE_DARK,
                'surface_variant': cls.SURFACE_VARIANT_DARK,
                'outline': cls.OUTLINE_DARK,
                'border': cls.BORDER_DARK,
            }
        else:
            return {
                'bg_primary': cls.BG_PRIMARY_LIGHT,
                'bg_secondary': cls.BG_SECONDARY_LIGHT,
                'bg_tertiary': cls.BG_TERTIARY_LIGHT,
                'bg_card': cls.BG_CARD_LIGHT,
                'text_primary': cls.TEXT_PRIMARY_LIGHT,
                'text_secondary': cls.TEXT_SECONDARY_LIGHT,
                'text_muted': cls.TEXT_MUTED_LIGHT,
                'surface': cls.SURFACE_LIGHT,
                'surface_variant': cls.SURFACE_VARIANT_LIGHT,
                'outline': cls.OUTLINE_LIGHT,
                'border': cls.BORDER_LIGHT,
            }


class Styles:
    """Styles réutilisables."""
    
    # Border radius
    RADIUS_SM = 8
    RADIUS_MD = 12
    RADIUS_LG = 16
    RADIUS_XL = 20
    RADIUS_FULL = 50
    
    # Padding
    PADDING_XS = 5
    PADDING_SM = 10
    PADDING_MD = 15
    PADDING_LG = 20
    PADDING_XL = 30
    
    # Animations
    ANIMATION_FAST = 150
    ANIMATION_NORMAL = 300
    ANIMATION_SLOW = 500
    
    # Shadows
    SHADOW_SM = 4
    SHADOW_MD = 8
    SHADOW_LG = 16
    SHADOW_XL = 24


# Icônes utilisées dans l'application
class Icons:
    """Mapping des icônes."""
    
    # Navigation
    DASHBOARD = "dashboard"
    NC = "warning_amber"
    ANALYSIS = "analytics"
    USERS = "people"
    SETTINGS = "settings"
    REPORTS = "assessment"
    AUDITS = "inventory"
    
    # Actions
    ADD = "add"
    EDIT = "edit"
    DELETE = "delete"
    SAVE = "save"
    CANCEL = "close"
    SEARCH = "search"
    FILTER = "filter_list"
    REFRESH = "refresh"
    BACK = "arrow_back"
    
    # Status
    CHECK = "check_circle"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    PENDING = "pending"
    
    # Auth
    LOGIN = "login"
    LOGOUT = "logout"
    USER = "person"
    LOCK = "lock"
    EMAIL = "email"
    
    # NC
    SEVERITY_LOW = "arrow_downward"
    SEVERITY_MEDIUM = "remove"
    SEVERITY_HIGH = "arrow_upward"
    SEVERITY_CRITICAL = "priority_high"

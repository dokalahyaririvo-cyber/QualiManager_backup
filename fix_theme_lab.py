# -*- coding: utf-8 -*-
"""Conversion complète vers Theme pour lab_page_new.py"""

filepath = r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Remplacement des couleurs par les constantes Theme
replacements = [
    # Backgrounds
    ('ft.Colors.WHITE', 'Theme.BG_CARD'),
    ('ft.Colors.BLUE_50', 'Theme.SURFACE_VARIANT'),
    ('ft.Colors.ORANGE_50', 'Theme.SURFACE_VARIANT'),
    ('ft.Colors.GREEN_50', 'Theme.SURFACE_VARIANT'),
    ('ft.Colors.RED_50', 'Theme.SURFACE_VARIANT'),
    
    # Borders
    ('ft.Colors.GREY_300', 'Theme.BORDER'),
    ('ft.Colors.GREY_200', 'Theme.BORDER'),
    ('ft.Colors.BLUE_200', 'Theme.BORDER'),
    ('ft.Colors.ORANGE_200', 'Theme.WARNING'),
    
    # Textes
    ('ft.Colors.GREY_900', 'Theme.TEXT_PRIMARY'),
    ('ft.Colors.GREY_700', 'Theme.TEXT_SECONDARY'),
    ('ft.Colors.GREY_600', 'Theme.TEXT_SECONDARY'),
    ('ft.Colors.GREY_400', 'Theme.TEXT_MUTED'),
    
    # Boutons primaires
    ('bgcolor=ft.Colors.BLUE_700', 'bgcolor=Theme.PRIMARY'),
    ('color=ft.Colors.BLUE_600', 'color=Theme.PRIMARY'),
    ('color=ft.Colors.BLUE_700', 'color=Theme.PRIMARY'),
    ('color=ft.Colors.BLUE_500', 'color=Theme.PRIMARY'),
    
    # Boutons success
    ('bgcolor=ft.Colors.GREEN_700', 'bgcolor=Theme.SUCCESS'),
    ('color=ft.Colors.GREEN_700', 'color=Theme.SUCCESS'),
    ('color=ft.Colors.GREEN_600', 'color=Theme.SUCCESS'),
    ('color=ft.Colors.GREEN_500', 'color=Theme.SUCCESS'),
    
    # Alertes danger
    ('color=ft.Colors.RED_700', 'color=Theme.DANGER'),
    ('color=ft.Colors.RED_600', 'color=Theme.DANGER'),
    ('color=ft.Colors.RED_500', 'color=Theme.DANGER'),
    ('icon_color=ft.Colors.RED_400', 'icon_color=Theme.DANGER'),
    
    # Alertes warning
    ('color=ft.Colors.ORANGE_700', 'color=Theme.WARNING'),
    ('color=ft.Colors.ORANGE_600', 'color=Theme.WARNING'),
    ('color=ft.Colors.ORANGE_500', 'color=Theme.WARNING'),
    
    # Info
    ('color=ft.Colors.TEAL_500', 'color=Theme.INFO'),
    
    # Graphiques - garder les couleurs vives pour distinction
    ('bgcolor=ft.Colors.BLUE_400', 'bgcolor=Theme.PRIMARY_LIGHT'),
    
    # Ombres
    ('color=ft.Colors.BLACK12', 'color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)'),
    
    # Conclusion badges - garder les couleurs sémantiques existantes
    ('ConclusionAnalyse.CONFORME: Theme.TEXT_SECONDARY', 'ConclusionAnalyse.CONFORME: Theme.SUCCESS'),
    ('ConclusionAnalyse.NON_CONFORME: Theme.TEXT_SECONDARY', 'ConclusionAnalyse.NON_CONFORME: Theme.DANGER'),
    ('ConclusionAnalyse.ALERTE: Theme.TEXT_SECONDARY', 'ConclusionAnalyse.ALERTE: Theme.WARNING'),
    ('ConclusionAnalyse.EN_ATTENTE: Theme.TEXT_SECONDARY', 'ConclusionAnalyse.EN_ATTENTE: Theme.TEXT_MUTED'),
]

count = 0
for old, new in replacements:
    occurrences = content.count(old)
    if occurrences > 0:
        content = content.replace(old, new)
        count += occurrences
        print(f"  ✓ {occurrences}x: {old} → {new}")

print(f"\n✅ Total: {count} remplacements effectués")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fichier lab_page_new.py mis à jour avec Theme")

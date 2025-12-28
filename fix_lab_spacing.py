# -*- coding: utf-8 -*-
"""Correction de l'espacement et des symboles dans le module laboratoire"""

with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Réduire l'espacement entre titre et onglets
content = content.replace(
    '''                    padding=ft.padding.only(left=10, top=10, bottom=10),
                ),
                # Tabs
                tabs_bar,''',
    '''                    padding=ft.padding.only(left=10, top=5, bottom=0),
                ),
                # Tabs
                tabs_bar,'''
)

# 2. Réduire l'espacement dans le conteneur principal
content = content.replace(
    '''        # Conteneur principal
        self.main_content = ft.Container(
            content=self._build_dashboard(),
            expand=True,
            padding=20
        )''',
    '''        # Conteneur principal
        self.main_content = ft.Container(
            content=self._build_dashboard(),
            expand=True,
            padding=10
        )'''
)

# 3. Corriger "CoÃ»t Total" -> "Coût Total"
content = content.replace('title="CoÃ»t Total"', 'title="Coût Total"')

# 4. Corriger "ConformitÃ©" -> "Conformité"
content = content.replace('title="Taux ConformitÃ©"', 'title="Taux Conformité"')

# 5. Corriger "â‚¬" -> "€"
content = content.replace('â‚¬', '€')

# 6. Réduire spacing dans le layout principal
content = content.replace(
    '''            expand=True,
            spacing=0
        )''',
    '''            expand=True,
            spacing=5,
            tight=True
        )'''
)

with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Corrections appliquées:")
print("   - Espacement réduit entre titre et onglets")
print("   - Padding du contenu réduit")
print("   - Symboles corrigés (Coût, Conformité, €)")
print("   - Spacing général optimisé")

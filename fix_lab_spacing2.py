# -*- coding: utf-8 -*-
"""Optimisation supplémentaire de l'espacement"""

with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Réduire l'espacement entre les KPIs
content = content.replace(
    '            ], spacing=20),\n            \n            ft.Divider(height=20, thickness=2),',
    '            ], spacing=15),\n            \n            ft.Divider(height=10, thickness=1),')

# Réduire l'espacement entre les graphiques
content = content.replace(
    '            ], spacing=20, expand=True),',
    '            ], spacing=15, expand=True),')

# Réduire le padding des graphiques
content = content.replace(
    '                    padding=20,\n                    border_radius=10,',
    '                    padding=15,\n                    border_radius=10,')

with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Espacement optimisé:")
print("   - Espacement KPIs: 20 → 15")
print("   - Divider: 20 → 10")
print("   - Espacement graphiques: 20 → 15")
print("   - Padding graphiques: 20 → 15")

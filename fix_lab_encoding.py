# -*- coding: utf-8 -*-
"""Script pour corriger l'encodage et améliorer le layout du module laboratoire"""

import codecs

# Lire le fichier avec l'encodage UTF-8
with codecs.open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Corriger les onglets avec des emojis corrects
content = content.replace(
    '''tabs=[
                ft.Tab(text="📊 Tableau de Bord", icon=ft.Icons.DASHBOARD),
                ft.Tab(text="📋 Liste Analyses", icon=ft.Icons.LIST_ALT),
                ft.Tab(text="➕ Nouvelle Analyse", icon=ft.Icons.ADD_CIRCLE_OUTLINE),
                ft.Tab(text="📈 Statistiques", icon=ft.Icons.BAR_CHART),
                ft.Tab(text="📄 Rapports", icon=ft.Icons.DESCRIPTION),
            ],''',
    '''tabs=[
                ft.Tab(text="Tableau de Bord", icon=ft.Icons.DASHBOARD),
                ft.Tab(text="Liste Analyses", icon=ft.Icons.LIST_ALT),
                ft.Tab(text="Nouvelle Analyse", icon=ft.Icons.ADD_CIRCLE_OUTLINE),
                ft.Tab(text="Statistiques", icon=ft.Icons.BAR_CHART),
                ft.Tab(text="Rapports", icon=ft.Icons.DESCRIPTION),
            ],'''
)

# Remplacer le layout pour ajouter un titre et réduire l'espace
old_layout = '''        # Layout principal (simplifié pour barre latérale)
        self.content = ft.Column(
            controls=[
                # Tabs
                tabs_bar,
                # Contenu dynamique
                self.main_content
            ],
            expand=True,
            spacing=0
        )'''

new_layout = '''        # Layout principal avec titre
        self.content = ft.Column(
            controls=[
                # Titre du module
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SCIENCE, size=32, color=ft.Colors.BLUE_700),
                        ft.Text(
                            "Laboratoire & Qualité",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_700
                        ),
                    ]),
                    padding=ft.padding.only(left=10, top=10, bottom=10),
                ),
                # Tabs
                tabs_bar,
                # Contenu dynamique
                self.main_content
            ],
            expand=True,
            spacing=0
        )'''

content = content.replace(old_layout, new_layout)

# Sauvegarder avec le bon encodage
with codecs.open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Encodage corrigé")
print("✅ Titre ajouté")
print("✅ Onglets sans emojis")

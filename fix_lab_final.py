# -*- coding: utf-8 -*-
"""Correction complète du module laboratoire"""

# Lire le fichier
with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Créer le nouveau contenu
new_lines = []
in_tabs = False
tabs_replaced = False

for i, line in enumerate(lines):
    # Détecter le début des tabs
    if 'tabs=[' in line:
        in_tabs = True
        new_lines.append(line)
        continue
    
    # Remplacer les lignes des tabs
    if in_tabs and not tabs_replaced:
        if 'ft.Tab(text=' in line:
            # Remplacer par version sans emojis
            if 'Tableau de Bord' in line:
                new_lines.append('                ft.Tab(text="Tableau de Bord", icon=ft.Icons.DASHBOARD),\n')
            elif 'Liste Analyses' in line:
                new_lines.append('                ft.Tab(text="Liste Analyses", icon=ft.Icons.LIST_ALT),\n')
            elif 'Nouvelle Analyse' in line:
                new_lines.append('                ft.Tab(text="Nouvelle Analyse", icon=ft.Icons.ADD_CIRCLE_OUTLINE),\n')
            elif 'Statistiques' in line:
                new_lines.append('                ft.Tab(text="Statistiques", icon=ft.Icons.BAR_CHART),\n')
            elif 'Rapports' in line:
                new_lines.append('                ft.Tab(text="Rapports", icon=ft.Icons.DESCRIPTION),\n')
            else:
                new_lines.append(line)
        elif '],\n' in line:
            in_tabs = False
            tabs_replaced = True
            new_lines.append(line)
        else:
            new_lines.append(line)
    # Ajouter un titre avant les tabs
    elif '# Layout principal' in line and 'barre latérale' in line:
        new_lines.append('        # Layout principal avec titre\n')
    elif line.strip() == 'self.content = ft.Column(':
        new_lines.append(line)
        # Sauter à l'ajout du contenu
    elif 'controls=[' in line and i > 50:  # Dans le layout
        new_lines.append(line)
        # Ajouter le titre juste après controls=[
        new_lines.append('                # Titre du module\n')
        new_lines.append('                ft.Container(\n')
        new_lines.append('                    content=ft.Row([\n')
        new_lines.append('                        ft.Icon(ft.Icons.SCIENCE, size=32, color=ft.Colors.BLUE_700),\n')
        new_lines.append('                        ft.Text(\n')
        new_lines.append('                            "Laboratoire & Qualité",\n')
        new_lines.append('                            size=24,\n')
        new_lines.append('                            weight=ft.FontWeight.BOLD,\n')
        new_lines.append('                            color=ft.Colors.BLUE_700\n')
        new_lines.append('                        ),\n')
        new_lines.append('                    ]),\n')
        new_lines.append('                    padding=ft.padding.only(left=10, top=10, bottom=10),\n')
        new_lines.append('                ),\n')
    else:
        new_lines.append(line)

# Écrire le fichier corrigé
with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Fichier corrigé avec succès")
print("   - Emojis supprimés des onglets")
print("   - Titre ajouté au module")

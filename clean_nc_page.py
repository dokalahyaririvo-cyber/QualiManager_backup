# -*- coding: utf-8 -*-
"""
Script pour nettoyer le fichier nc_page.py et retirer les modifications de debug
"""

def clean_nc_page():
    file_path = "flet_app/nc_page.py"
    
    print("Lecture du fichier...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Nettoyage des modifications...")
    
    # 1. Retirer les prints de debug ajoutés
    lines_to_remove = [
        '            print("[NCPage] Début de l\'initialisation...")\n',
        '            print("[NCPage] UI construite avec succès")\n',
        '            print("[NCPage] NCPage initialisé avec succès")\n',
        '            print("[NCPage._build_ui] Début...")\n',
        '            print("[NCPage._build_ui] Construction du header...")\n',
        '            print("[NCPage._build_ui] Construction des tabs...")\n',
        '            print("[NCPage._build_ui] Appel à _build_dashboard_tab...")\n',
        '            print("[NCPage._build_ui] Construction de la colonne finale...")\n',
        '            print("[NCPage._build_ui] UI construite avec succès!")\n',
        '            print("[NCPage._build_dashboard_tab] Début...")\n',
        '            print("[NCPage._build_dashboard_tab] Imports OK...")\n',
        '        print("[NCPage._build_ui] Début...")\n',
        '        print("[NCPage._build_ui] Construction du header...")\n',
    ]
    
    for line in lines_to_remove:
        content = content.replace(line, '')
    
    # 2. Retirer les blocs try/except ajoutés dans __init__
    # Chercher et remplacer la structure try dans __init__
    old_init_try = """        try:
            content = self._build_ui()
            
            super().__init__(
                expand=True,
                bgcolor=Theme.BG_PRIMARY,
                padding=0,
                content=content,
            )
        except Exception as e:
            print(f"[NCPage] ❌ ERREUR lors de l'initialisation: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            # Créer une interface d'erreur minimale
            super().__init__(
                expand=True,
                bgcolor=Theme.BG_PRIMARY,
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "❌ Erreur lors du chargement du module NC",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="red"
                        ),
                        ft.Text(f"Type: {type(e).__name__}", size=14),
                        ft.Text(f"Message: {str(e)}", size=14),
                        ft.ElevatedButton(
                            "Retour au Hub",
                            on_click=lambda _: self.navigate("/hub")
                        )
                    ]
                )
            )"""
    
    new_init = """        super().__init__(
            expand=True,
            bgcolor=Theme.BG_PRIMARY,
            padding=0,
            content=self._build_ui(),
        )"""
    
    content = content.replace(old_init_try, new_init)
    
    print("Sauvegarde du fichier nettoyé...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fichier nettoyé avec succès!")
    print("   - Prints de debug retirés")
    print("   - Blocs try/except retirés")

if __name__ == '__main__':
    clean_nc_page()

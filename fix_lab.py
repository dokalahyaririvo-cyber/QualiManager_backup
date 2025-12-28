with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Corriger le layout
content = content.replace(
    '# Layout principal (simplifié)`r`n        self.content = ft.Column(`r`n            controls=[`r`n                # Tabs`r`n                tabs_bar,',
    '# Layout principal (simplifié pour barre latérale)\n        self.content = ft.Column(\n            controls=[\n                # Tabs\n                tabs_bar,'
)

with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fichier corrigé')

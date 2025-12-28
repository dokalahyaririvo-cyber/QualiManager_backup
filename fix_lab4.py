with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remplacer toute la fin du __init__
old_init_end = '''        # Initialiser la page
        self._build_ui()
        
        # Configurer le container
        self.content = self.build()
        self.expand = True'''

new_init_end = '''        # Initialiser la page
        self._build_ui()
        
        # Appeler le constructeur parent avec le contenu construit
        _content = self.build()
        super().__init__(content=_content, expand=True)'''

content = content.replace(old_init_end, new_init_end)

with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Init corrigé - super().__init__() appelé à la fin')

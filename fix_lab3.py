with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Déplacer super().__init__() après _build_ui()
old_pattern = '''    def __init__(self, user, db, navigate):
        super().__init__()
        self.user = user'''

new_pattern = '''    def __init__(self, user, db, navigate):
        self.user = user'''

content = content.replace(old_pattern, new_pattern)

# Ajouter super().__init__() juste avant content
old_pattern2 = '''        # Configurer le container
        self.content = self.build()
        self.expand = True'''

new_pattern2 = '''        # Configurer le container en appelant super après avoir construit le contenu
        _content = self.build()
        super().__init__(content=_content, expand=True)'''

content = content.replace(old_pattern2, new_pattern2)

with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Ordre d initialisation corrigé')

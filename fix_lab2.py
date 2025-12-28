with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Faire hériter LabPage de ft.Container
content = content.replace(
    'class LabPage:\n    """Page principale du module Laboratoire"""',
    'class LabPage(ft.Container):\n    """Page principale du module Laboratoire"""'
)

# Ajouter super().__init__() et configurer le container
old_init = '''    def __init__(self, user, db, navigate):
        self.user = user
        self.db_main = db
        self.navigate = navigate
        self.db = LabDBManager()
        
        # État actuel'''

new_init = '''    def __init__(self, user, db, navigate):
        super().__init__()
        self.user = user
        self.db_main = db
        self.navigate = navigate
        self.db = LabDBManager()
        
        # État actuel'''

content = content.replace(old_init, new_init)

# Ajouter la configuration du container après _build_ui()
old_build_call = '''        # Initialiser la page
        self._build_ui()
    
    def _build_ui(self):'''

new_build_call = '''        # Initialiser la page
        self._build_ui()
        
        # Configurer le container
        self.content = self.build()
        self.expand = True
    
    def _build_ui(self):'''

content = content.replace(old_build_call, new_build_call)

with open(r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('LabPage modifié pour hériter de ft.Container')

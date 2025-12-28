# 📦 Guide de Distribution - QualiManager

## 🎯 Deux Solutions de Distribution

QualiManager peut être distribué de **deux façons** :

### 1️⃣ **Version PORTABLE** (Recommandée pour tests et mobilité)
✅ **Aucune installation requise**  
✅ Un seul fichier `.exe`  
✅ Fonctionne depuis une clé USB  
✅ Aucun droit administrateur nécessaire  
✅ Suppression simple (supprimer le fichier)  

❌ Premier lancement plus lent (~10-15 secondes)  
❌ Fichier volumineux (~80-120 MB)  
❌ Peut être signalé par certains antivirus (faux positif)  

### 2️⃣ **Version INSTALLATEUR** (Recommandée pour déploiement entreprise)
✅ Installation Windows standard  
✅ Lancement rapide (~2-3 secondes)  
✅ Désinstallation propre via Windows  
✅ Raccourcis automatiques (Bureau, Menu Démarrer)  
✅ Association de fichiers  
✅ Moins de faux positifs antivirus  

❌ Nécessite une installation  
❌ Droits administrateur parfois requis  

---

## 🛠️ Compilation de l'Application

### Prérequis
```bash
# 1. Python 3.10+ installé
python --version

# 2. Environnement virtuel configuré
python -m venv venv
venv\Scripts\activate

# 3. Dépendances installées
pip install -r requirements.txt
pip install pyinstaller
```

### Méthode Rapide (Automatique)

**Option 1 : Double-clic**
```
1. Double-cliquez sur BUILD.bat
2. Attendez la compilation (~5-10 minutes)
3. Les fichiers sont dans le dossier "output"
```

**Option 2 : Ligne de commande**
```batch
BUILD.bat
```

### Méthode Manuelle (Contrôle total)

```batch
# Activer l'environnement
venv\Scripts\activate

# Lancer le build complet
python build_complete.py
```

---

## 📂 Structure des Fichiers Générés

Après compilation, voici la structure :

```
output/
├── Portable/
│   ├── QualiManager.exe              ← Version portable
│   ├── README.md
│   ├── LANCEMENT.txt
│   └── GUIDE_IMPORT_EXPORT_VEILLE.md
│
├── QualiManager_v2.0.0_Portable_*.zip  ← Package ZIP portable
│
└── Installer/
    ├── QualiManager/                   ← Dossier application
    │   ├── QualiManager_Dir.exe
    │   ├── _internal/                 (DLLs et ressources)
    │   └── ...
    ├── QualiManager_Setup.iss          ← Script Inno Setup
    ├── README.md
    └── GUIDE_IMPORT_EXPORT_VEILLE.md
```

---

## 🚀 Distribution aux Utilisateurs

### Version Portable

#### Étape 1 : Préparer le package
```
1. Naviguez vers: output/
2. Trouvez: QualiManager_v2.0.0_Portable_*.zip
3. Ce fichier contient tout le nécessaire
```

#### Étape 2 : Instructions pour l'utilisateur
**Envoyez ces instructions avec le ZIP :**

```
═══════════════════════════════════════════════════════════
  QualiManager - Installation Version Portable
═══════════════════════════════════════════════════════════

📥 INSTALLATION:
1. Extraire le fichier ZIP dans un dossier de votre choix
   Exemple: C:\QualiManager ou D:\Applications\QualiManager
   
2. Vous pouvez aussi l'extraire sur une clé USB pour le rendre portable

🚀 LANCEMENT:
• Double-cliquez sur QualiManager.exe
• Premier lancement: Patientez 10-15 secondes (extraction des ressources)
• Lancements suivants: Plus rapide (~3-5 secondes)

💾 DONNÉES:
• Les données sont enregistrées dans le dossier "data"
• Pour sauvegarder: Copiez tout le dossier QualiManager

⚠️ ANTIVIRUS:
Si votre antivirus bloque le fichier:
1. C'est un faux positif (fréquent avec PyInstaller)
2. Ajoutez QualiManager.exe aux exceptions
3. Ou contactez votre administrateur informatique

❓ AIDE:
• Consultez README.md pour plus d'informations
• Guide d'import/export: GUIDE_IMPORT_EXPORT_VEILLE.md
```

### Version Installateur

#### Étape 1 : Créer l'installateur avec Inno Setup

```
1. Téléchargez et installez Inno Setup:
   https://jrsoftware.org/isdl.php (gratuit, open-source)

2. Ouvrez le fichier:
   output/Installer/QualiManager_Setup.iss

3. Dans Inno Setup:
   • Menu: Build → Compile
   • Attendez la compilation (~1-2 minutes)

4. L'installateur est créé:
   output/Installer/QualiManager_v2.0.0_Setup.exe
```

#### Étape 2 : Distribuer l'installateur

**Envoyez cet installateur avec ces instructions :**

```
═══════════════════════════════════════════════════════════
  QualiManager - Installation Version Installateur
═══════════════════════════════════════════════════════════

📥 INSTALLATION:
1. Double-cliquez sur QualiManager_v2.0.0_Setup.exe
2. Suivez l'assistant d'installation
3. Acceptez l'emplacement par défaut ou choisissez un autre dossier
4. Créez les raccourcis (Bureau, Menu Démarrer)
5. Cliquez sur "Installer"

🚀 LANCEMENT:
• Double-cliquez sur l'icône du Bureau
• Ou: Menu Démarrer → QualiManager

💾 DONNÉES:
• Les données sont dans: C:\Program Files\QualiManager\data
• Sauvegardes automatiques recommandées

🗑️ DÉSINSTALLATION:
• Panneau de configuration → Programmes et fonctionnalités
• Sélectionnez QualiManager → Désinstaller
• Ou: Dossier d'installation → unins000.exe

❓ AIDE:
• Menu Démarrer → QualiManager → Guide d'utilisation
```

---

## 🔧 Configuration Avancée

### Personnaliser l'Icône

```python
# Dans build_complete.py, ligne 11:
ICON_FILE = "assets/icon.ico"

# Créez votre icône (.ico, 256x256 pixels)
# Placez-la dans assets/icon.ico
```

### Modifier les Métadonnées

```python
# Dans build_complete.py, lignes 8-11:
APP_NAME = "QualiManager"           # Nom de l'application
APP_VERSION = "2.0.0"               # Version
APP_AUTHOR = "Votre Entreprise"    # Auteur
APP_DESCRIPTION = "..."             # Description
```

### Ajouter des Fichiers à la Distribution

```python
# Dans build_complete.py, méthode create_portable_package():
files_to_copy = [
    'README.md',
    'LICENSE.txt',
    'VotreNouveauFichier.pdf',  # ← Ajoutez ici
]
```

---

## 🐛 Résolution de Problèmes

### Erreur: "PyInstaller not found"
```bash
pip install pyinstaller
```

### Erreur: "Module not found"
```bash
# Réinstallez toutes les dépendances
pip install -r requirements.txt --force-reinstall
```

### L'exe ne démarre pas
```bash
# Testez avec console pour voir les erreurs
pyinstaller --onefile --console app_erp.py
# Puis lancez: dist/app_erp.exe
```

### Antivirus bloque le fichier
- C'est un **faux positif** courant avec PyInstaller
- Solutions :
  1. Ajoutez aux exceptions de l'antivirus
  2. Signez le code avec un certificat (payant)
  3. Soumettez aux éditeurs d'antivirus (gratuit mais long)

### Fichier trop volumineux
```python
# Dans build_complete.py, ajoutez:
'--exclude-module', 'module_non_utilise',

# Modules souvent inutiles:
--exclude-module matplotlib.tests
--exclude-module pandas.tests
--exclude-module PIL
```

---

## 📊 Comparaison des Méthodes

| Critère | Portable | Installateur |
|---------|----------|--------------|
| **Taille** | 80-120 MB (1 fichier) | 60-80 MB (dispersé) |
| **Installation** | Aucune | 2-3 minutes |
| **Démarrage** | 10-15s (1er) / 3-5s | 2-3 secondes |
| **Mobilité** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Professionnel** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Droits admin** | Non | Parfois |
| **Désinstallation** | Supprimer dossier | Windows standard |

---

## 💡 Recommandations

### Pour Tests Internes
→ **Version Portable**
- Distribution rapide
- Aucune installation
- Facile à mettre à jour

### Pour Déploiement Entreprise
→ **Version Installateur**
- Installation centralisée (GPO)
- Désinstallation propre
- Plus professionnel

### Pour Clients Externes
→ **Les deux !**
- Installateur = Installation classique
- Portable = Tests sans engagement

---

## 🔐 Sécurité & Certification

### Signature de Code (Recommandé pour production)

```bash
# Obtenez un certificat de signature de code
# Coût: ~150-400€/an

# Signez l'exe:
signtool sign /f certificat.pfx /p motdepasse /t http://timestamp.digicert.com QualiManager.exe
```

**Avantages :**
- ✅ Pas d'avertissement Windows SmartScreen
- ✅ Confiance des utilisateurs
- ✅ Moins de blocages antivirus

---

## 📞 Support

Pour toute question sur la compilation ou distribution :
1. Vérifiez la section "Résolution de Problèmes"
2. Consultez la documentation PyInstaller: https://pyinstaller.org
3. Consultez la documentation Inno Setup: https://jrsoftware.org/ishelp/

---

## 🎯 Checklist Finale

Avant de distribuer :

**Tests**
- [ ] Tester sur Windows 10
- [ ] Tester sur Windows 11
- [ ] Tester premier lancement
- [ ] Tester avec antivirus activé
- [ ] Tester import/export
- [ ] Vérifier base de données se crée bien

**Documentation**
- [ ] README.md à jour
- [ ] GUIDE_IMPORT_EXPORT_VEILLE.md inclus
- [ ] Instructions d'installation claires
- [ ] Numéro de version correct

**Fichiers**
- [ ] Portable : ZIP complet
- [ ] Installateur : .exe fonctionnel
- [ ] Licence incluse
- [ ] Templates Excel inclus

---

**Prêt à compiler ?**
```batch
BUILD.bat
```

**Bonne distribution ! 🚀**

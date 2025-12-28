# Procédure Standard de Build - QualiManager

## 📋 Vue d'ensemble
Cette procédure est appliquée **systématiquement** à chaque demande de création de l'application.
Elle génère automatiquement **2 versions** :
1. **Version Portable** : Exécutable unique (onefile) - Données locales
2. **Version Installeur** : Setup professionnel avec Inno Setup - Données dans AppData

> ⚠️ **DERNIÈRE MISE À JOUR**: Décembre 2025 - Version 2.1.0
> **Corrections majeures appliquées** :
> - ✅ Import Excel NC corrigé (mapping automatique colonnes)
> - ✅ Support variations format (accents, abréviations)
> - ✅ Gestion automatique dates Excel
> - ✅ Messages d'import toujours affichés
> - ✅ Correction VeilleDBManager (base unifiée)
> - ✅ Vraie portabilité (données locales)
> - ✅ Icône et métadonnées Windows intégrées

---

## 🔧 Étape 1 : Préparation

### ⚠️ 1.0 VÉRIFICATIONS CRITIQUES PRÉALABLES

**AVANT TOUT BUILD, vérifier ces points pour éviter les erreurs connues :**

#### A. Fichier QualiManager_Setup.iss 
Le fichier `.iss` se trouve dans `output/Installer/` après le build Python :
```powershell
# Après build_complete.py, vérifier :
Test-Path "output\Installer\QualiManager_Setup.iss"  # Doit retourner True
```

**Points critiques dans le fichier .iss :**
- Ligne 9 : `#define MyAppExeName "QualiManager_Dir.exe"` (PAS "QualiManager.exe")
- Ligne 40-41 : Sources relatives au .iss :
  ```
  Source: "QualiManager\QualiManager_Dir.exe"; DestDir: "{app}"
  Source: "QualiManager\_internal\*"; DestDir: "{app}\_internal"
  ```
- Lignes 44-56 : Documentation avec chemins `..\..\` :
  ```
  Source: "..\..\GUIDE_*.md"; DestDir: "{app}\docs"
  Source: "..\..\README.md"; DestDir: "{app}\docs"
  ```

#### B. Base de données unifiée et nettoyée
Avant chaque build, nettoyer TOUTES les bases :
```powershell
# Script de nettoyage complet
cd 'f:\Applications\Gestion Qualité'
Remove-Item "$env:APPDATA\QualiManager\*.db" -Force -ErrorAction SilentlyContinue
# La base source sera copiée lors du build
```

#### C. Import Excel NC - Nouvelles fonctionnalités v2.1.0
Le système d'import a été complètement refondu :
- **Mapping automatique** : Lit les en-têtes Excel dynamiquement
- **Flexibilité** : Supporte "Référence", "Reference", "Ref", "N°"
- **Dates auto** : Convertit les dates Excel automatiquement
- **Messages** : Dialogue modal avec résumé détaillé TOUJOURS affiché

```python
# app_erp.py - Lignes ~14-44
def is_portable_mode():
    """Détecte si l'application est en mode portable (onefile)"""
    if not getattr(sys, 'frozen', False):
        return False
    internal_path = os.path.join(application_path, '_internal')
    return not os.path.exists(internal_path)

def get_user_data_path():
    """Retourne le chemin des données selon le mode"""
    if is_portable_mode():
        return application_path  # Données à côté de l'exe
    else:
        # Mode installeur : AppData
        return os.path.join(os.environ.get('APPDATA'), 'QualiManager')
```

### 1.1 Vérifier la version
- Fichier : `flet_app/db_manager.py`
- Ligne : `APP_VERSION = "X.X.X"`
- Fichier .iss : `QualiManager_Setup.iss` ligne 6
- **Action** : S'assurer que les versions correspondent

### 1.2 Vérifier les dépendances
```powershell
cd 'f:\Applications\Gestion Qualité'
.\venv\Scripts\python.exe -m pip list | Select-String "flet|pandas|openpyxl|reportlab|matplotlib|PyInstaller"
```

### 1.3 Nettoyer les builds précédents
```powershell
Remove-Item -Path "dist", "build" -Recurse -Force -ErrorAction SilentlyContinue
# NE PAS supprimer output\Installer\QualiManager_Setup.iss - Il est copié depuis la racine
```

**⚠️ Important** : Le fichier `QualiManager_Setup.iss` à la racine ne doit JAMAIS être supprimé. Il est la source de vérité et est copié automatiquement par le build.ove-Item -Path "output\Portable", "output\Installer\QualiManager" -Recurse -Force -ErrorAction SilentlyContinue
```

---

## 🚀 Étape 2 : Build Automatique

### 2.1 Exécuter le script de build complet
```powershell
cd 'f:\Applications\Gestion Qualité'
.\Ce script effectue automatiquement :**
1. ✅ Nettoyage des builds précédents
2. ✅ Création de la version Portable (PyInstaller --onefile)
   - Fichier unique : `QualiManager.exe`
   - Mode portable activé automatiquement
   - Données stockées localement (à côté de l'exe)
3. ✅ Création de la version Installeur (PyInstaller --onedir)
   - Fichier principal : `QualiManager_Dir.exe` (⚠️ noter le suffixe _Dir)
   - Dossier `_internal` avec toutes les dépendances
   - Données stockées dans AppData
4. ✅ Copie de la base de données template
5. ✅ Copie des fichiers de documentation
6. ✅ **Copie du script Inno Setup (.iss) depuis la racine** vers output/Installer
7. ✅ Compilation de l'installeur Windows avec Inno Setup

**⚠️ POINTS CRITIQUES :**
- Le fichier .iss est **copié** depuis la racine (ne sera plus jamais écrasé)
- Le nom du fichier exe est `QualiManager_Dir.exe` pour la version installeur
- La versiutilisée : **Inno Setup 6.6.1** (testé et validé)
- Version minimale : **Inno Setup 6.0+**

**Installation :**
1. Télécharger le fichier `innosetup-6.x.x.exe`
2. Installer dans `C:\Program Files (x86)\Inno Setup 6\`
3. Le compilateur sera à : `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`

**Si Inno Setup n'est pas installé :**
- Le build créera quand même les versions Portable et Installeur (dossier)
- Seul le fichier Setup.exe final ne sera pas généré
- Vous pouvez compiler manuellement plus tard :
  ```powershell
  & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" QualiManager_Setup.iss
  ```

**Installation :**
1. Télécharger le fichier `innosetup-6.x.x.exe`
2. Installer dans `C: (53 429 523 octets)
- **Type** : Exécutable unique (onefile)
- **Usage** : Clé USB, déploiement rapide, environnement sans installation
- **🆕 Données** : Stockées dans le même dossier que l'exe (vraie portabilité)
  - `qualimanager_erp.db` : Base de données locale
  - `backups/` : Sauvegardes automatiques

**⚠️ Architecture Portable (v2.1.0+) :**
```
Dossier_USB/
├── QualiManager.exe          (Application)
├── qualimanager_erp.db      (Base de données - créée au 1er lancement)
└── backups/                  (Sauvegardes automatiques)
```
**Avantages** : Tout le dossier peut être copié sur une clé USB ou transféré sur un autre PC. Les données suivent l'application.

### 3.2 Version Installeur
- **Emplacement** : `output\Installer\QualiManager_vX.X.X_Setup.exe`
- **Taille** : ~38 MB (40 058 880 octets)
- **Type** : Installeur Windows professionnel (Inno Setup)
- **Installation** : `C:\Program Files\QualiManager\`
- **Données** : `%APPDATA%\QualiManager\` (séparées des fichiers programme)

**⚠️ Architecture Installeur :**
```
C:\Program Files\QualiManager\
├── QualiManager_Dir.exe      (⚠️ Nom avec suffixe _Dir)
├── _internal\                (Dépendances)
├── qualimanager_erp.db      (Template - lecture seule)
└── docs\                     (Documentation)

C:\Users\[User]\AppData\Roaming\QualiManager\
├── qualimanager_erp.db      (Base active - lecture/écriture)
└── backups\                  (Sauvegardes automatiques)
``
## 📦 Étape 3 : Résultats Attendus

### 3.1 Version Portable
- **Emplacement** : `output\Portable\QualiManager.exe`
- **Taille** : ~51 MB
- **Type** : Exécutable unique (onefile)
- **Usage** : Clé USB, déploiement rapide

### 3.2 Version Installeur
- **Emplacement** : `output\Installer\QualiManager_vX.X.X_Setup.exe`
- **Taille** : ~38 MB
- **Type** : Installeur Windows professionnel (Inno Setup)
- **Installation** : `C:\Program Files\QualiManager\`
- **Données** : `%APPDATA%\QualiManager\`

**Contenu du Setup :**
- Programme complet avec toutes les dépendances
- Base de données template
- Documentation (README, guides)
- Création automatique des dossiers utilisateur
- Icônes menu démarrer et bureau (optionnel)
- Désinstalleur intégré

### 3.3 Fichiers inclus dans l'installeur
```
output\Installer\
├── **L'onglet Veille est accessible et fonctionnel** (bug corrigé v2.1.0)
- ✅ Les modules sont accessibles (NC, Veille, Inspections, etc.)
- ✅ **Un fichier `qualimanager_erp.db` est créé dans `output\Portable\`** (portabilité)
- ✅ Ajouter une donnée de test, fermer, relancer → donnée toujours présente

**Test de portabilité (NOUVEAU) :**
```powershell
# Copier tout le dossier Portable ailleurs
Copy-Item "output\Portable" -Destination "C:\Temp\TestPortable" -Recurse
# Lancer depuis le nouvel emplacement
Start-Process "C:\Temp\TestPortable\QualiManager.exe"
# Les données doivent être présentes (vraie portabilité)
```
├── QualiManager_Setup.iss          (Script Inno Setup)
├── README.md
├── LICENSE.txt
├── GUIDE_MISE_A_JOUR.md
├── GUIDE_IMPORT_EXPORT_VEILLE.md (v2.1.0+)

### 5.1 Version Portable - VRAIE PORTABILITÉ ✨
```
Emplacement_au_choix\       (Clé USB, réseau, disque local...)
├── QualiManager.exe        (Application)
├── qualimanager_erp.db    (Base de données - créée au 1er lancement)
└── backups\
    └── qualimanager_erp_YYYYMMDD_HHMMSS.db
```

**Détection automatique du mode :**
```python
# app_erp.py détecte le mode portable
is_portable = not os.path.exists(os.path.join(app_path, '_internal'))
if is_portable:
    data_path = app_path  # Données à côté de l'exe
```

**Avantages :**
- ✅ Tout est dans un seul dossier
- ✅ Copie/déplacement facile
- ✅ Aucune trace dans le système
- ✅ Multi-utilisateurs possible (chacun son dossier)

### 5.2 Version Installeur - SÉPARATION PROGRAMME/DONNÉES
```
Installation (Programme - lecture seule):
C:\Program Files\QualiManager\
├── QualiManager_Dir.exe         (⚠️ Suffixe _Dir obligatoire)
├── _internal\                   (Dépendances Python)
│   ├── database\
│   ├── flet_app\
│   ❌ Erreur : "Source file QualiManager.exe does not exist" (Inno Setup)
**Cause :** Le fichier installeur s'appelle `QualiManager_Dir.exe`, pas `QualiManager.exe`

**Solution :**
Vérifier dans `QualiManager_Setup.iss` (à la racine) :
```ini
; Ligne 9 - Nom correct du fichier
#define MyAppExeName "QualiManager_Dir.exe"

; Ligne 40 - Source correcte
Source: "output\Installer\QualiManager\QualiManager_Dir.exe"; DestDir: "{app}";
```

**Vérification rapide :**
```powershell
Get-ChildItem "output\Installer\QualiManager\" -Filter "*.exe" | Select-Object Name
# Doit afficher : QualiManager_Dir.exe
```

### ❌ Erreur : Inno Setup ne trouve pas le fichier .iss
**Cause :** Le fichier .iss était dans output/Installer et a été écrasé par le build

**Solution :** Depuis v2.1.0, le fichier .iss est à la racine :
```powershell
# Le fichier doit être ici (source de vérité)
Test-Path "QualiManager_Setup.iss"  # Doit retourner True
✅ VÉRIFICATIONS CRITIQUES AVANT LE BUILD (v2.1.0+)
- [ ] **Fichier .iss à la racine** : `QualiManager_Setup.iss` existe et est correct
- [ ] **Nom exe correct** : Ligne 9 du .iss = `"QualiManager_Dir.exe"`
- [ ] **Source exe correcte** : Ligne 40 du .iss pointe vers `QualiManager_Dir.exe`
- [ ] **VeilleDBManager** : Accepte le paramètre `db_path` (ligne ~11)
- [ ] **VeillePage** : Passe `db.db_path` au VeilleDBManager (ligne ~25)
- [ ] **Mode portable** : Fonction `is_portable_mode()` implémentée dans app_erp.py
- [ ] **Data path dynamique** : `get_user_data_path()` retourne le bon chemin selon le mode

### Avant le build
- [ ] Version mise à jour dans `db_manager.py` ET dans `QualiManager_Setup.iss`
- [ ] Changelog mis à jour si nécessaire
- [ ] Environnement virtuel activé
- [ ] Dépendances installées et à jour
- [ ] Inno Setup 6.6.1+ installé

### Pendant le build
- [ ] Exécuter `build_complete.py`
- [ ] Surveiller les messages d'erreur
- [ ] Vérifier que le fichier .iss est copié depuis la racine
- [ ] Attendre la compilation Inno Setup (~2-3 minutes)
- [ ] Vérifier aucune erreur "Source file does not exist"

### Après le build - Tests Obligatoires
- [ ] Vérifier création de `output\Portable\QualiManager.exe` (51 MB)
- [ ] Vérifier création de `output\Installer\QualiManager_vX.X.X_Setup.exe` (38 MB)
- [ ] **TEST PORTABLE** :
  - [ ] Lancer et vérifier connexion
  - [ ] **Onglet Veille accessible**
  - [ ] Ajouter donnée test, fermer, relancer → donnée présente
  - [ ] Fichier `qualimanager_erp.db` créé dans output\Portable\
  - [ ] Copier le dossier ailleurs et tester → données suivent
- [ ] **TEST INSTALLEUR** :
  - [ ] Installer et vérifier connexion
  - [ ] **Onglet Veille accessible**
  - [ ] Vérifier données dans %APPDATA%\QualiManager
  - [ ] Vérifier QualiManager_Dir.exe dans Program Files
self.db = VeilleDBManager(db.db_path if hasattr(db, 'db_path') else None)
```

### ❌ Erreur : Version portable perd les données après déplacement
**Cause :** Ancienne version stockait dans AppData au lieu du dossier local

**Solution :** Vérifier l'implémentation v2.1.0 :
```python
# app_erp.py
def is_portable_mode():
    if not getattr(sys, 'frozen', False):
        return False
    internal_path = os.path.join(application_path, '_internal')
    return not os.path.exists(internal_path)  # True si onefile

def get_user_data_path():
    if is_portable_mode():
        return application_path  # Données locales !
    else:
        return os.path.join(os.environ.get('APPDATA'), 'QualiManager')
```

### Erreur : PyInstaller échoue
**Solution :**
```powershell
.\venv\Scripts\python.exe -m pip install --upgrade pyinstaller
```

### Erreur : Inno Setup non trouvé
**Solution :**
- Installer Inno Setup 6.6.1+ depuis : https://jrsoftware.org/isdl.php
- Vérifier : `C:\Program Files (x86)\Inno Setup 6\ISCC.exe` existe

### Erreur : Module manquant
**Solution :**
```powershell
.\venv\Scripts\python.exe -m pip install pandas openpyxl reportlab matplotlib flet --upgrade
```e"
```
Fichier .iss à la racine** - Source de vérité, copié automatiquement par le build
3. **Nom de l'exe installeur** : `QualiManager_Dir.exe` (avec suffixe _Dir)
4. **Ne jamais modifier** les bases de données dans Program Files
5. **Sauvegardes automatiques** : Créées avant chaque migration de version
6. **Multi-utilisateurs** : Chaque utilisateur Windows a sa propre base AppData
7. **Mises à jour** : Les données utilisateur persistent entre les versions
8. **Portabilité vraie** : Version portable stocke TOUT localement (v2.1.0+)
9. **Base unifiée** : VeilleDBManager utilise la base principale (v2.1.0+)

---

## 🔗 Fichiers Associés

- **Script principal** : `build_complete.py`
- **Configuration PyInstaller** : 
  - `QualiManager.spec` (portable - généré)
  - `QualiManager_Dir.spec` (installeur - généré)
- **Configuration Inno Setup** : `QualiManager_Setup.iss` (à la RACINE, copié vers output/Installer)
- **Gestion version** : `flet_app\db_manager.py` (APP_VERSION)
- **Gestion portabilité** : `app_erp.py` (is_portable_mode, get_user_data_path)
- **Gestion Veille** : 
  - `database\veille_db_manager.py` (accepte db_path)
  - `flet_app\veille_page.py` (passe db_path)

---

## 🐛 Bugs Corrigés (v2.1.0 - Décembre 2025)

### Bug #1 : Onglet Veille non fonctionnel après installation
**Cause** : VeilleDBManager créait une base séparée `data/veille.db`  
**Solution** : Passage du chemin de la base principale en paramètre  
**Fichiers modifiés** :
- `database/veille_db_manager.py` (ligne 11) : Accepte `db_path=None`
- `flet_app/veille_page.py` (ligne 25) : Passe `db.db_path`

### Bug #2 : Version portable perd les données après déplacement  
**Cause** : Données stockées dans AppData au lieu du dossier local  
**Solution** : Détection du mode portable et stockage local  
**Fichiers modifiés** :
- `app_erp.py` (lignes 14-44) : 
  - `is_portable_mode()` : Détecte l'absence du dossier `_internal`
  - `get_user_data_path()` : Retourne le chemin local si portable

### Bug #3 : Erreur compilation Inno Setup "Source file does not exist"  
**Cause** : Fichier .iss cherchait `QualiManager.exe` au lieu de `QualiManager_Dir.exe`  
**Solution** : Correction du nom dans le fichier .iss  
**Fichier modifié** :
- `QualiManager_Setup.iss` (lignes 9 et 40) : Nom correct `QualiManager_Dir.exe`

### Bug #4 : Fichier .iss écrasé à chaque build  
**Cause** : Fichier .iss généré dans output/Installer et recréé à chaque build  
**Solution** : Fichier .iss source à la racine, copié par build_complete.py  
**Fichiers modifiés** :
- Création de `QualiManager_Setup.iss` à la racine (permanent)
- `build_complete.py` (lignes 289-297) : Copie depuis la racine

---

**Dernière mise à jour** : 22 décembre 2025 - 21h30  
**Version actuelle** : 2.1.0  
**Créé pour** : QualiManager ERP  
**Bugs corrigés** : 4 bugs majeurs (Veille, Portabilité, Compilation)
└── QualiManager.exe
    └── (données intégrées dans l'exe)
```
- Base de données : Créée dans `%APPDATA%\QualiManager\` au premier lancement

### 5.2 Version Installeur
```
Installation:
C:\Program Files\QualiManager\
├── QualiManager.exe
├── qualimanager_erp.db (template - lecture seule)
└── ...

Données utilisateur:
C:\Users\[User]\AppData\Roaming\QualiManager\
├── qualimanager_erp.db (copie active - lecture/écriture)
└── backups\
    └── qualimanager_erp_vX.X.X_YYYYMMDD_HHMMSS.db
```

---

## 🚨 Gestion des Erreurs

### Erreur : PyInstaller échoue
**Solution :**
```powershell
.\venv\Scripts\python.exe -m pip install --upgrade pyinstaller
```

### Erreur : Inno Setup non trouvé
**Solution :**
- Installer Inno Setup 6.3.3+ depuis : https://jrsoftware.org/isdl.php
- Ajouter au PATH : `C:\Program Files (x86)\Inno Setup 6\`

### Erreur : Module manquant
**Solution :**
```powershell
.\venv\Scripts\python.exe -m pip install pandas openpyxl reportlab matplotlib flet --upgrade
```

### Erreur : "readonly database"
**Solution :** Déjà implémentée dans v2.1.0
- Les données sont automatiquement copiées dans AppData
- Program Files contient seulement le template

---

## 📝 Checklist de Build Complète

### Avant le build
- [ ] Version mise à jour dans `db_manager.py`
- [ ] Changelog mis à jour si nécessaire
- [ ] Environnement virtuel activé
- [ ] Dépendances installées et à jour

### Pendant le build
- [ ] Exécuter `build_complete.py`
- [ ] Surveiller les messages d'erreur
- [ ] Attendre la compilation Inno Setup (~2-3 minutes)

### Après le build
- [ ] Vérifier création de `output\Portable\QualiManager.exe`
- [ ] Vérifier création de `output\Installer\QualiManager_vX.X.X_Setup.exe`
- [ ] Tester la version Portable
- [ ] Tester l'installeur (si déploiement imminent)
- [ ] Archiver les builds précédents si nécessaire

---

## 📤 Distribution

### Version Portable
- **Partage** : Copier `QualiManager.exe` directement
- **Mise à jour** : Remplacer l'exe existant

### Version Installeur
- **Partage** : Distribuer `QualiManager_vX.X.X_Setup.exe`
- **Mise à jour** : Installer la nouvelle version
  - L'ancien programme est remplacé
  - Les données utilisateur sont préservées

---

## 🎯 Résumé : Une Seule Commande

Pour générer **les deux versions** en une seule fois :

```powershell
cd 'f:\Applications\Gestion Qualité'
.\venv\Scripts\python.exe build_complete.py
```

**Temps estimé :** 3-5 minutes  
**Résultat :** 2 versions prêtes à distribuer

---

## 📌 Notes Importantes

1. **Toujours utiliser `build_complete.py`** - Ne pas lancer PyInstaller manuellement
2. **Ne jamais modifier** les bases de données dans Program Files
3. **Sauvegardes automatiques** : Créées avant chaque migration de version
4. **Multi-utilisateurs** : Chaque utilisateur Windows a sa propre base AppData
5. **Mises à jour** : Les données utilisateur persistent entre les versions

---

## 🔗 Fichiers Associés

- **Script principal** : `build_complete.py`
- **Configuration PyInstaller** : `QualiManager.spec` (portable) et `QualiManager_Dir.spec` (installeur)
- **Configuration Inno Setup** : `output\Installer\QualiManager_Setup.iss` (généré automatiquement)
- **Gestion version** : `flet_app\db_manager.py` (APP_VERSION)

---

**Dernière mise à jour** : 22 décembre 2025  
**Version actuelle** : 2.1.0  
**Créé pour** : QualiManager ERP

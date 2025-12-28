# 🏭 QualiManager - Système de Gestion Qualité (SMQ)

Application moderne de gestion qualité développée avec **Flet** (Flutter pour Python).

## 🚀 Fonctionnalités

| Module | Description | État |
|--------|-------------|------|
| 📋 **Non-Conformités** | Signalement, suivi et clôture des NC | ✅ Disponible |
| � **Export/Import NC** | Export Excel/PDF/CSV avec texte complet + Import depuis Excel | ✅ Disponible |
| �🔬 **Outils d'analyse** | 5 Pourquoi, Ishikawa, AMDEC, 8D, Pareto | ✅ Disponible |
| 👥 **Gestion utilisateurs** | Administration des comptes | ✅ Disponible |
| ✅ **Plans d'actions** | Suivi des actions correctives | 🚧 À venir |
| 👁️ **Veille réglementaire** | Surveillance normative | 🚧 À venir |
| 📝 **Inspections** | Planification et suivi | 🚧 À venir |
| 📊 **Rapports** | Tableaux de bord et KPIs | 🚧 À venir |

## 📦 Installation

### Méthode 1 : Installation automatique (Windows - Recommandée)

1. Double-cliquez sur **`install.bat`**
2. Attendez la fin de l'installation (~2-3 minutes)
3. Double-cliquez sur **`run.bat`** pour lancer l'application

### Méthode 2 : Installation manuelle

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
venv\Scripts\activate

# Activer l'environnement (Linux/Mac)
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python app.py
```

## 🔨 Compilation en Exécutable (.exe)

Pour distribuer l'application sans avoir besoin d'installer Python :

### Méthode automatique
```bash
build.bat
```

### Méthode manuelle
```bash
python build.py
```

**Fichiers générés dans `dist/` :**
- `QualiManager.exe` - Exécutable standalone
- `QualiManager_Portable_v1.0.0.zip` - Version portable (copier sur clé USB)

### Créer un Installeur Windows (optionnel)

1. Téléchargez et installez [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Ouvrez `QualiManager.iss` avec Inno Setup
3. Cliquez sur "Compile" pour créer `QualiManager_Setup_v1.0.0.exe`

## 🔐 Connexion

**Identifiants administrateur par défaut :**

| Champ | Valeur |
|-------|--------|
| Email | `admin@qualimanager.local` |
| Mot de passe | `Admin@2024!` |

## 📁 Structure du Projet

```
QualiManager/
├── 📄 app_erp.py           # Point d'entrée principal
├── 📁 flet_app/            # Modules de l'application
│   ├── theme.py            # Thème Material Design 3
│   ├── database.py         # Gestionnaire SQLite
│   ├── components.py       # Composants UI réutilisables
│   ├── nc_page.py          # Module NC complet avec export/import
│   ├── analysis_page.py    # 5 outils d'analyse qualité
│   └── users_page.py       # Gestion des utilisateurs
├── 📁 data/                # Base de données SQLite
├── 📁 assets/              # Icônes et ressources
├── 📄 install.bat          # 🚀 Script d'installation
├── 📄 run.bat              # ▶️ Lancer l'application
├── 📄 build.bat            # 🔨 Compiler en .exe
├── 📄 build.py             # Script de build avancé
├── 📄 requirements.txt     # Dépendances Python
├── 📄 GUIDE_IMPORT_EXPORT_NC.md  # 📚 Guide export/import
├── 📄 MODELE_IMPORT_NC.xlsx      # 📋 Modèle Excel import
├── 📄 create_import_template.py  # Script création modèle
└── 📄 README.md            # Ce fichier
```

## 🛠️ Technologies

| Technologie | Usage |
|-------------|-------|
| **Flet 0.28.3** | Framework UI basé sur Flutter |
| **SQLite** | Base de données embarquée |
| **openpyxl** | Gestion fichiers Excel |
| **reportlab** | Génération PDF |
| **PyInstaller** | Compilation en exécutable |
| **Material Design 3** | Interface moderne dark mode |

## ✨ Nouveautés Export/Import

### 📤 Améliorations des exports
- **Texte complet** : Plus de troncature, tout le texte avec retours à la ligne
- **Colonnes Lot et Quantité** : Ajoutées après la colonne Produit
- **Sélecteur de fichier** : Choisissez où sauvegarder vos exports
- **Confirmations** : Messages de confirmation avec nombre de NC exportées

### 📥 Import depuis Excel
- **Import en masse** : Ajoutez plusieurs NC en une fois depuis Excel
- **Validation automatique** : Vérification des données et rapport d'erreurs
- **Modèle fourni** : Utilisez `MODELE_IMPORT_NC.xlsx` comme référence
- **Gestion des erreurs** : Détails des lignes problématiques

📚 **Documentation complète** : Voir [GUIDE_IMPORT_EXPORT_NC.md](GUIDE_IMPORT_EXPORT_NC.md)

## 📸 Captures d'écran

### Tableau de bord
Interface moderne avec statistiques et graphiques en temps réel.

### Liste NC
- Actions rapides : Voir / Éditer / Dupliquer
- Recherche instantanée avec debouncing
- Export Excel/PDF/CSV avec texte complet
- Import depuis Excel avec validation

### Outils d'analyse
- **5 Pourquoi** - Recherche de cause racine
- **Ishikawa** - Diagramme causes-effet (6M)
- **AMDEC** - Analyse des modes de défaillance
- **8D** - Résolution de problèmes structurée
- **Pareto** - Analyse 80/20

## 🔧 Configuration

La base de données SQLite est créée automatiquement au premier lancement dans le dossier `data/`.

Pour réinitialiser l'application, supprimez le fichier `data/qualimanager.db`.

## 📚 Documentation

- **[GUIDE_IMPORT_EXPORT_NC.md](GUIDE_IMPORT_EXPORT_NC.md)** : Guide complet export/import
- **[DOCUMENTATION_MODULE_NC.md](DOCUMENTATION_MODULE_NC.md)** : Documentation module NC
- **[LIRE_MOI_CHANGEMENTS.md](LIRE_MOI_CHANGEMENTS.md)** : Historique des modifications

## 📞 Support

Pour toute question ou problème technique :
1. Consultez les guides de documentation
2. Vérifiez les logs dans la console
3. Utilisez le modèle Excel fourni pour les imports

---

**QualiManager v2.0.0** - Système de Gestion Qualité  
*© 2024 - Tous droits réservés*

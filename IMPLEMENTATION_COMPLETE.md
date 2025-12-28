# ✅ QualiManager - Système de Distribution et Mise à Jour

## 📦 Ce qui a été implémenté

### 1️⃣ Système de Versioning Automatique

**Fichier modifié** : `flet_app/models.py`
- ✅ Table `app_version` créée pour suivre la version de la DB
- ✅ Stocke la version actuelle et l'historique des migrations

**Fichier modifié** : `flet_app/db_manager.py`
- ✅ Constante `APP_VERSION = "2.1.0"` (à mettre à jour à chaque version)
- ✅ Fonction `_get_db_version()` : Lit la version actuelle de la DB
- ✅ Fonction `_set_db_version()` : Enregistre la nouvelle version
- ✅ Fonction `_backup_database()` : Sauvegarde auto avant migration
- ✅ Fonction `_check_and_migrate()` : Détecte et applique les migrations
- ✅ Fonctions `_migrate_to_X_X_X()` : Migrations spécifiques par version

### 2️⃣ Mode PORTABLE (Sans installation)

**Structure du package** :
```
QualiManager_Portable\
├── QualiManager.exe          (51 MB)
├── qualimanager_erp.db       (420 KB - VOS DONNÉES)
├── backups\                  (Sauvegardes automatiques)
├── README.md
├── LICENSE.txt
└── GUIDE_MISE_A_JOUR.md
```

**Avantages** :
- ✅ Aucune installation requise
- ✅ Portable (clé USB, réseau)
- ✅ Données dans le même dossier
- ✅ Mise à jour simple : remplacer l'EXE

**Emplacement actuel** : `f:\Applications\Gestion Qualité\output\Portable\`

### 3️⃣ Mode INSTALLEUR (Installation classique)

**Structure** :
- Programme dans `C:\Program Files\QualiManager\`
- Données dans `C:\Users\[Nom]\AppData\Local\QualiManager\`

**Script Inno Setup** créé : `output\Installer\QualiManager_Setup.iss`

**Pour créer l'installeur** :
1. Installer Inno Setup : https://jrsoftware.org/isdl.php
2. Ouvrir le fichier `.iss`
3. Cliquer sur Build → Compile

### 4️⃣ Processus de Migration Automatique

**Au démarrage de l'application** :
1. ✅ Lecture de la version DB actuelle
2. ✅ Comparaison avec la version de l'app
3. ✅ Si différent → Sauvegarde automatique
4. ✅ Application des migrations nécessaires
5. ✅ Mise à jour de la version DB
6. ✅ Message de confirmation

**Exemple de sortie console** :
```
🔄 Migration de la base de données v1.0.0 → v2.1.0
✓ Sauvegarde créée: backup_before_migration_20251222_185642.db
  → Application de la migration 2.0.0...
  → Application de la migration 2.1.0...
✅ Migration terminée avec succès !
```

---

## 🔄 Comment mettre à jour l'application (VOUS, développeur)

### Étape 1 : Incrémenter la version

Dans `flet_app/db_manager.py` :
```python
class DatabaseManager:
    APP_VERSION = "2.2.0"  # ← Changer ici
```

### Étape 2 : Ajouter la migration si nécessaire

Si vous ajoutez des colonnes/tables, créer une nouvelle fonction :
```python
def _migrate_to_2_2_0(self):
    """Migration vers la version 2.2.0."""
    print("  → Application de la migration 2.2.0...")
    with self.get_connection() as conn:
        # Exemple: Ajouter une colonne
        self._add_column_if_not_exists(
            conn, 'nc_header', 'nouvelle_colonne', 'TEXT'
        )
```

Et l'appeler dans `_check_and_migrate()` :
```python
if db_version < "2.2.0":
    self._migrate_to_2_2_0()
```

### Étape 3 : Reconstruire

```powershell
cd "f:\Applications\Gestion Qualité"
.\venv\Scripts\python.exe build_complete.py
```

Ou manuellement :
```powershell
# Version Portable
.\venv\Scripts\pyinstaller.exe --onefile --windowed --name QualiManager [options...] app_erp.py

# Copier les fichiers
Copy-Item dist\QualiManager.exe output\Portable\
Copy-Item qualimanager_erp.db output\Portable\
# etc.
```

### Étape 4 : Distribuer au client

**Mode Portable** :
- Envoyer seulement : `QualiManager.exe` (nouvelle version)
- Client remplace son ancien .exe
- Au lancement → Migration automatique

**Mode Installeur** :
- Créer l'installeur avec Inno Setup
- Envoyer : `QualiManager_Setup_v2.2.0.exe`
- Client lance l'installeur
- Données préservées automatiquement

---

## 📋 Instructions pour le CLIENT

### Mode PORTABLE - Mise à jour

**Ce qu'il reçoit** : `QualiManager.exe` (nouveau fichier)

**Ce qu'il fait** :
1. Fermer l'application
2. Remplacer `QualiManager.exe`
3. Relancer
4. ✅ Ses données sont préservées
5. ✅ Migration automatique

**⚠️ NE JAMAIS toucher** : `qualimanager_erp.db`

### Mode INSTALLEUR - Mise à jour

**Ce qu'il reçoit** : `QualiManager_Setup_v2.2.0.exe`

**Ce qu'il fait** :
1. Lancer l'installeur
2. Accepter la mise à jour
3. ✅ Ses données sont préservées
4. ✅ Migration automatique

---

## 🆘 En cas de problème

### Migration échouée

Les données sont protégées ! Une sauvegarde a été créée dans `backups/` avant la migration.

**Restauration** :
1. Aller dans `backups/`
2. Trouver `backup_before_migration_YYYYMMDD_HHMMSS.db`
3. Copier et renommer en `qualimanager_erp.db`
4. Relancer l'application

### Base corrompue

Même processus : utiliser la sauvegarde la plus récente.

---

## 📊 État actuel

### Version actuelle implémentée
- **Code** : v2.1.0
- **Localisation** : `f:\Applications\Gestion Qualité\output\Portable\`

### Fichiers créés
✅ `GUIDE_MISE_A_JOUR.md` - Instructions détaillées pour les clients
✅ `flet_app/models.py` - Table app_version ajoutée
✅ `flet_app/db_manager.py` - Système de migration complet
✅ `build_complete.py` - Script amélioré avec copie automatique de la DB

### Tests effectués
✅ Build portable réussi (51 MB)
✅ Base de données copiée (420 KB)
✅ Dossier backups créé
✅ Documentation incluse

### À tester
⏳ Lancer l'application et vérifier la migration
⏳ Créer l'installeur avec Inno Setup
⏳ Tester la mise à jour d'une v1.0 vers v2.1

---

## 🎯 Recommandations

### Pour VOUS (développeur)
1. **À chaque modification de schéma DB** :
   - Incrémenter `APP_VERSION`
   - Créer une fonction `_migrate_to_X_X_X()`
   - Tester la migration

2. **Avant distribution** :
   - Tester sur une copie de la DB d'un client
   - Vérifier que la migration fonctionne
   - Tester la restauration depuis backup

3. **Versioning sémantique** :
   - `2.0.0` → Changements majeurs (schéma DB)
   - `2.1.0` → Nouvelles fonctionnalités
   - `2.1.1` → Corrections de bugs

### Pour les CLIENTS
1. **Portable** recommandé pour :
   - ✅ Environnements sans admin
   - ✅ Tests/démonstrations
   - ✅ Réseau local/clé USB
   - ✅ Pas d'intégration Windows nécessaire

2. **Installeur** recommandé pour :
   - ✅ Utilisation professionnelle permanente
   - ✅ Multiple utilisateurs Windows
   - ✅ Intégration menu Démarrer
   - ✅ Données sécurisées dans AppData

---

**Date de création** : 22 décembre 2025  
**Version du système** : 2.1.0  
**Prochaine étape** : Tester la migration complète

# 🔄 Guide de Mise à Jour - QualiManager

## 📦 Deux modes de distribution

QualiManager est disponible en **deux modes** selon vos besoins :

### 1️⃣ Mode PORTABLE (Sans installation)
- ✅ Pas d'installation requise
- ✅ Fonctionne depuis n'importe quel dossier
- ✅ Idéal pour clé USB ou réseau local
- ✅ Données stockées dans le même dossier

### 2️⃣ Mode INSTALLEUR (Installation classique)
- ✅ Installation dans Program Files
- ✅ Raccourcis dans le menu Démarrer
- ✅ Données dans AppData (sécurisées)
- ✅ Désinstallation propre

---

## 🔄 MODE PORTABLE - Mise à jour

### Structure du dossier
```
QualiManager_Portable\
├── QualiManager.exe          ← L'application (à remplacer)
├── qualimanager_erp.db       ← VOS DONNÉES (ne jamais toucher!)
├── backups\                  ← Sauvegardes automatiques
├── README.md
├── LICENSE.txt
└── GUIDE_MISE_A_JOUR.md
```

### 📋 Procédure de mise à jour

#### Étape 1 : Sauvegarder (optionnel mais recommandé)
```
1. Copier TOUT le dossier QualiManager_Portable
2. Le renommer en QualiManager_Portable_BACKUP
```

#### Étape 2 : Mettre à jour
```
1. Fermer complètement QualiManager
2. Télécharger la nouvelle version (ex: QualiManager_v2.2.exe)
3. Remplacer UNIQUEMENT le fichier QualiManager.exe
4. Lancer la nouvelle version
```

#### Étape 3 : Vérification
```
1. L'application détecte automatiquement l'ancienne version de la DB
2. Une sauvegarde automatique est créée dans backups\
3. La migration s'effectue automatiquement
4. Vos données sont préservées !
```

### ⚠️ IMPORTANT - Ne JAMAIS supprimer ou remplacer :
- ❌ `qualimanager_erp.db` (VOS DONNÉES)
- ❌ Dossier `backups\` (vos sauvegardes)

### ✅ Vous pouvez remplacer :
- ✅ `QualiManager.exe` (le programme)
- ✅ Fichiers README, LICENSE, etc.

---

## 🏢 MODE INSTALLEUR - Mise à jour

### Structure d'installation
```
Programme:
C:\Program Files\QualiManager\
├── QualiManager.exe
├── _internal\              (bibliothèques)
└── Uninstall.exe

Données utilisateur:
C:\Users\[VotreNom]\AppData\Local\QualiManager\
├── qualimanager_erp.db   ← VOS DONNÉES
└── backups\              ← Sauvegardes
```

### 📋 Procédure de mise à jour

#### Méthode 1 : Réinstallation complète (Recommandé)
```
1. Télécharger le nouvel installeur (ex: QualiManager_Setup_v2.2.exe)
2. Lancer l'installeur
3. Il détecte automatiquement l'ancienne version
4. Accepter la mise à jour
5. L'installeur remplace les fichiers PROGRAMME
6. Vos DONNÉES sont automatiquement préservées
7. Lancer QualiManager
8. La migration automatique s'effectue
```

#### Méthode 2 : Désinstaller puis réinstaller
```
1. Menu Démarrer → Paramètres → Applications
2. Trouver QualiManager → Désinstaller
3. ⚠️ IMPORTANT: Vos données dans AppData sont préservées !
4. Installer la nouvelle version
5. Au lancement, vos données sont récupérées automatiquement
```

### 🔒 Sécurité des données
Lors de la désinstallation, l'installeur :
- ✅ Supprime les fichiers PROGRAMME
- ✅ **PRÉSERVE** vos données dans AppData
- ✅ **PRÉSERVE** vos sauvegardes

---

## 🆘 En cas de problème

### Si l'application ne démarre plus après mise à jour

#### Solution 1 : Restaurer une sauvegarde
```
Mode Portable:
1. Aller dans le dossier backups\
2. Trouver le fichier backup_before_migration_YYYYMMDD_HHMMSS.db
3. Copier ce fichier
4. Le renommer en qualimanager_erp.db
5. Remplacer l'ancien fichier
6. Relancer l'application
```

```
Mode Installeur:
1. Aller dans C:\Users\[VotreNom]\AppData\Local\QualiManager\backups\
2. Trouver le fichier backup_before_migration_YYYYMMDD_HHMMSS.db
3. Copier ce fichier dans le dossier parent
4. Le renommer en qualimanager_erp.db
5. Remplacer l'ancien fichier
6. Relancer l'application
```

#### Solution 2 : Utiliser votre sauvegarde manuelle
```
1. Retrouver votre copie de sauvegarde complète
2. Restaurer le fichier qualimanager_erp.db
3. Relancer l'application
```

#### Solution 3 : Contacter le support
```
Si le problème persiste:
- Conservez votre fichier qualimanager_erp.db
- Notez le message d'erreur exact
- Contactez le support technique
```

---

## 📊 Vérification de la version

### Dans l'application
```
1. Lancer QualiManager
2. Se connecter
3. Aller dans Menu → À propos
4. Vérifier la version affichée
```

### Dans la console (mode développeur)
```
Au lancement, l'application affiche:
================================================================================
🚀 DEMARRAGE QUALIMANAGER ERP QHSE - Version 2.1.0
================================================================================
```

---

## 🔐 Bonnes pratiques

### Avant chaque mise à jour majeure
1. ✅ Sauvegarder manuellement le dossier complet
2. ✅ Vérifier que vos sauvegardes automatiques existent
3. ✅ Fermer complètement l'application
4. ✅ Noter votre version actuelle

### Fréquence recommandée
- 🔄 Mises à jour mineures (2.1.x): Appliquer dès disponible
- 🔄 Mises à jour majeures (2.x.0): Planifier avec sauvegarde
- 🔄 Mises à jour critiques (sécurité): Appliquer immédiatement

### Sauvegarde automatique
L'application crée automatiquement une sauvegarde :
- ✅ Avant chaque migration
- ✅ Dans le dossier backups\
- ✅ Avec horodatage (backup_before_migration_20251222_170000.db)
- ✅ Conservées pendant 30 jours

---

## 📞 Support

En cas de question ou problème :
- 📧 Email: support@qualimanager.local
- 📱 Documentation complète dans README.md
- 🌐 Conserver TOUJOURS votre fichier qualimanager_erp.db

---

**Version du guide : 2.1.0**  
**Dernière mise à jour : 22/12/2025**

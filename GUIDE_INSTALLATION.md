# 🚀 Guide d'Installation - QualiManager ERP QHSE

## 📦 Versions Disponibles

Votre application QualiManager est disponible en **2 versions** :

### 1️⃣ VERSION PORTABLE (Recommandée pour démarrer)
**📍 Emplacement** : `output/QualiManager_v2.0.0_Portable_XXXXXXXX.zip`

**✨ Avantages** :
- ✅ **Aucune installation requise**
- ✅ Un seul fichier exécutable
- ✅ Portable (USB, réseau, cloud)
- ✅ Pas de droits administrateur nécessaires
- ✅ Plusieurs installations possibles

**❌ Inconvénients** :
- ⏱️ Premier démarrage un peu plus lent (15-30s)
- 💾 Fichier plus volumineux (~100 MB)

**📥 Installation** :
1. Décompressez le fichier ZIP
2. Double-cliquez sur `QualiManager.exe`
3. C'est tout ! 🎉

---

### 2️⃣ VERSION AVEC INSTALLATEUR (Recommandée pour usage permanent)
**📍 Emplacement** : `output/Installer/`

**✨ Avantages** :
- ⚡ Démarrage rapide (instantané)
- 🎯 Installation propre dans Program Files
- 🗑️ Désinstallation Windows standard
- 🔗 Raccourcis automatiques (Bureau + Menu Démarrer)
- 📊 Moins d'espace disque utilisé

**❌ Inconvénients** :
- 🔐 Requiert les droits administrateur
- 💿 Nécessite de créer l'installateur

**📥 Création de l'installateur** :

#### Étape 1 : Installer Inno Setup
1. Téléchargez **Inno Setup** (gratuit) : https://jrsoftware.org/isdl.php
2. Installez-le (suivez les instructions par défaut)

#### Étape 2 : Compiler l'installateur
1. Ouvrez le fichier `output/Installer/QualiManager_Setup.iss` avec Inno Setup
2. Cliquez sur **Build** → **Compile**
3. L'installateur sera créé : `QualiManager_Setup.exe`

#### Étape 3 : Distribuer
1. Distribuez le fichier `QualiManager_Setup.exe` à vos utilisateurs
2. Double-cliquez sur l'installateur
3. Suivez l'assistant d'installation
4. L'application sera installée dans `C:\Program Files\QualiManager\`

---

## 🎯 Quelle Version Choisir ?

### Utilisez la VERSION PORTABLE si :
- 🧪 Vous voulez **tester l'application rapidement**
- 💼 Vous travaillez sur **plusieurs ordinateurs**
- 🔒 Vous **n'avez pas les droits administrateur**
- 💾 Vous voulez l'installer sur **clé USB ou réseau**
- 👥 Vous voulez **plusieurs instances** (dev, test, prod)

### Utilisez la VERSION INSTALLATEUR si :
- 💻 **Installation permanente** sur un poste fixe
- ⚡ Vous voulez un **démarrage instantané**
- 🎨 Vous voulez une **intégration Windows complète**
- 👥 **Distribution en entreprise** (plusieurs utilisateurs)
- 📊 **Usage professionnel intensif**

---

## 🚀 Démarrage Rapide

### Version Portable
```batch
# Méthode 1 : Direct
Double-cliquez sur QualiManager.exe

# Méthode 2 : Avec le lanceur
Double-cliquez sur Lancer_Portable.bat
```

### Version Installée
```batch
# Menu Démarrer → QualiManager
# ou
# Double-cliquez sur le raccourci Bureau
```

---

## 🔧 Configuration Post-Installation

### 1. Premier Lancement
Au premier démarrage, l'application va :
1. ✅ Créer la base de données automatiquement
2. ✅ Initialiser les tables
3. ✅ Créer un compte administrateur par défaut

**🔐 Identifiants par défaut** :
- **Utilisateur** : `admin`
- **Mot de passe** : `admin123`

⚠️ **IMPORTANT** : Changez le mot de passe immédiatement après la première connexion !

### 2. Structure des Dossiers
L'application crée automatiquement :
```
📁 QualiManager/
├── 📄 QualiManager.exe          # Application principale
├── 📊 qualimanager_erp.db       # Base de données SQLite
├── 📁 database/                 # Modules BDD
├── 📁 flet_app/                 # Interface utilisateur
├── 📁 assets/                   # Ressources (icônes, etc.)
└── 📁 data/                     # Données et exports
```

### 3. Base de Données
- **Type** : SQLite (fichier unique)
- **Emplacement** : `qualimanager_erp.db` (même dossier que l'exe)
- **Sauvegarde** : Copiez simplement le fichier `.db`
- **Migration** : Copiez le fichier `.db` vers une autre installation

---

## 📦 Distribution Multi-Appareils

### 🖥️ Windows (7, 8, 10, 11)
✅ **Compatible** - Utilisez l'une des deux versions

### 🍎 macOS / 🐧 Linux
⚠️ L'application actuelle est compilée pour Windows uniquement.

**Pour compiler sur d'autres plateformes** :
```bash
# Sur macOS/Linux, exécutez :
python build_complete.py

# L'application sera compilée pour la plateforme actuelle
```

### 📱 Déploiement Réseau
Vous pouvez installer l'application de plusieurs façons :

#### Option 1 : Installation Locale (Recommandée)
- Chaque utilisateur installe l'application sur son poste
- Base de données partagée sur un lecteur réseau :
  ```batch
  # Créez un lien symbolique vers la BDD réseau
  mklink "qualimanager_erp.db" "Z:\Qualite\qualimanager_erp.db"
  ```

#### Option 2 : Exécution Réseau (Non recommandée)
- Installation sur un lecteur réseau partagé
- ⚠️ Performances réduites
- ⚠️ Risques de conflits multi-utilisateurs

#### Option 3 : Serveur Central (Avancé)
- Installation avec base de données centralisée (MySQL/PostgreSQL)
- Nécessite modification du code pour connexion distante

---

## 🛠️ Résolution de Problèmes

### ❌ L'application ne démarre pas
1. **Vérifiez les prérequis** :
   - Windows 7 ou supérieur
   - .NET Framework installé (inclus dans Windows 10/11)
   
2. **Lancez en mode console** :
   ```batch
   # Téléchargez la version console pour voir les erreurs
   QualiManager_Console.exe
   ```

3. **Vérifiez l'antivirus** :
   - Ajoutez une exception pour QualiManager.exe
   - Les applications PyInstaller sont parfois bloquées

### ⚠️ "Windows a protégé votre ordinateur"
1. Cliquez sur **"Informations complémentaires"**
2. Cliquez sur **"Exécuter quand même"**
3. C'est normal pour les applications non signées

### 🐌 L'application est lente au démarrage
- **Version Portable** : Premier démarrage ~15-30s (normal)
- **Solution** : Utilisez la version avec installateur

### 💾 Erreur "Base de données verrouillée"
- Fermez toutes les instances de l'application
- Redémarrez l'application
- Si persistant : supprimez les fichiers `.db-shm` et `.db-wal`

### 📊 Erreur d'import Excel
- Vérifiez que le fichier respecte le template
- Consultez : `GUIDE_IMPORT_EXPORT_VEILLE.md`

---

## 📋 Mise à Jour

### Version Portable
1. Téléchargez la nouvelle version
2. Remplacez l'ancien `QualiManager.exe`
3. **Conservez** votre fichier `qualimanager_erp.db`

### Version Installée
1. Lancez le nouvel installateur
2. Il détectera l'ancienne version et proposera une mise à jour
3. La base de données sera préservée automatiquement

---

## 🔒 Sécurité et Sauvegarde

### 💾 Sauvegardes Recommandées
1. **Quotidienne** : Copiez `qualimanager_erp.db`
2. **Hebdomadaire** : Archive complète du dossier
3. **Mensuelle** : Copie hors site (cloud, autre PC)

### 🔐 Sécurité
- Changez le mot de passe admin par défaut
- Créez des comptes utilisateurs individuels
- Limitez les droits selon les rôles
- Stockez les sauvegardes dans un emplacement sécurisé

---

## 📞 Support

### 📖 Documentation
- `README.md` - Présentation générale
- `GUIDE_IMPORT_EXPORT_VEILLE.md` - Import/Export de données
- `GUIDE_NOUVELLES_FONCTIONS_NC.md` - Fonctionnalités NC
- `CHANGELOG_v2.1.md` - Historique des versions

### 🛠️ Mode Développement
Pour les développeurs :
```batch
# Lancez en mode dev (avec console de debug)
Lancer_Dev.bat
```

---

## ✅ Checklist de Déploiement

### Pour l'Administrateur
- [ ] Choisir la version (Portable ou Installateur)
- [ ] Tester sur une machine de référence
- [ ] Configurer les sauvegardes automatiques
- [ ] Créer la documentation utilisateur spécifique
- [ ] Former les utilisateurs clés

### Pour les Utilisateurs
- [ ] Installer l'application
- [ ] Se connecter (admin/admin123)
- [ ] Changer son mot de passe
- [ ] Tester les fonctionnalités de base
- [ ] Signaler tout problème

---

## 🎉 Prêt à Commencer !

Votre application **QualiManager ERP QHSE** est maintenant prête à être déployée sur tous vos appareils !

**Recommandation finale** :
1. 🧪 Commencez avec la **version portable** pour tester
2. 💾 Une fois validée, créez l'**installateur** pour le déploiement
3. 📚 Consultez les guides pour exploiter toutes les fonctionnalités

---

**Version** : 2.0.0  
**Date** : 22 Décembre 2025  
**Système** : Windows 7/8/10/11 (64-bit)

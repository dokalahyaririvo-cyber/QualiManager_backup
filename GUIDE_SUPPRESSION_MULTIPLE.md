# 🎯 QualiManager v2.3.0 - Guide de Suppression Multiple

## ✨ Nouvelle Fonctionnalité : Suppression Multiple de NC

### 📋 Vue d'ensemble

La version 2.3.0 introduit la possibilité de supprimer plusieurs Non-Conformités (NC) en une seule opération, avec une interface intuitive et sécurisée.

---

## 🚀 Comment Utiliser

### Étape 1 : Accéder à la Liste des NC

1. Connectez-vous à QualiManager
2. Cliquez sur l'onglet **"Liste"** dans le module Non-Conformités

### Étape 2 : Sélectionner les NC

Dans le tableau, vous verrez maintenant une **nouvelle colonne de checkboxes** (☑) à gauche.

- **Cochez** les NC que vous souhaitez supprimer
- Le compteur sur le bouton se met à jour en temps réel

```
Exemple :
☑ NC-001 ✓ (cochée)
☑ NC-002 ✓ (cochée)
☑ NC-003 ☐ (non cochée)
```

### Étape 3 : Lancer la Suppression

1. **Localisez le bouton rouge** en haut à droite : **"Supprimer sélection (X)"**
   - X = nombre de NC sélectionnées
   - Le bouton est gris (désactivé) si aucune NC n'est cochée
   - Le bouton devient rouge quand au moins une NC est sélectionnée

2. **Cliquez** sur le bouton

### Étape 4 : Confirmer

Un dialogue de confirmation apparaît avec :
- Le nombre total de NC à supprimer
- Un avertissement ⚠️ sur le caractère irréversible
- La liste des données qui seront supprimées :
  * Toutes les données de la NC
  * Les actions immédiates
  * Les actions correctives
  * Les analyses (5 Pourquoi, Ishikawa)
  * Les références aux pièces jointes

**Options :**
- **"Annuler"** : Ferme le dialogue, rien n'est supprimé
- **"Supprimer les X NC"** : Lance la suppression définitive

### Étape 5 : Vérifier le Résultat

Un message s'affiche avec le résultat :
- ✅ **Succès total** : "X NC supprimées avec succès"
- ⚠️ **Succès partiel** : "X NC supprimées, Y échecs"
- ❌ **Erreur** : Message d'erreur détaillé

Les checkboxes sont automatiquement **décochées** après la suppression.

---

## 🎨 Interface

### Bouton "Supprimer sélection"

| État | Apparence | Description |
|------|-----------|-------------|
| **Désactivé** | Gris, texte "Supprimer sélection" | Aucune NC cochée |
| **Activé (1 NC)** | Rouge, texte "Supprimer sélection (1)" | 1 NC sélectionnée |
| **Activé (5 NC)** | Rouge, texte "Supprimer sélection (5)" | 5 NC sélectionnées |

### Colonne Checkbox

- **Position** : Première colonne du tableau (tout à gauche)
- **Largeur** : 45 pixels
- **Symbole** : ☑
- **Interaction** : Clic pour cocher/décocher

---

## 🛡️ Sécurité et Comportement

### ✅ Sécurités Mises en Place

1. **Confirmation obligatoire** : Impossible de supprimer sans confirmer
2. **Dialogue modal** : Bloque l'interface jusqu'à confirmation ou annulation
3. **Avertissement clair** : Indication du caractère irréversible
4. **Liste détaillée** : Affiche tout ce qui sera supprimé

### 🔄 Réinitialisations Automatiques

La sélection est **automatiquement effacée** dans les cas suivants :
- **Après suppression** : Les checkboxes se décochent
- **Changement d'onglet** : Passer de "Liste" à "Tableau de bord", etc.
- **Rafraîchissement** : Application de nouveaux filtres, actualisation

**Pourquoi ?** Pour éviter les suppressions accidentelles.

---

## 📊 Gestion des Erreurs

### Suppression Partielle

Si certaines NC ne peuvent pas être supprimées :
- Les NC valides sont quand même supprimées
- Un message indique le nombre de succès et d'échecs
- Les erreurs sont affichées dans la console (pour le support technique)

**Exemple de message :**
```
⚠️ 8 NC supprimées, 2 échecs
```

### Causes Possibles d'Échec

- NC déjà supprimée par un autre utilisateur
- Problème de connexion à la base de données
- NC verrouillée par un autre processus

---

## 💡 Conseils et Astuces

### ✅ Bonnes Pratiques

1. **Vérifiez deux fois** avant de confirmer la suppression
2. **Utilisez les filtres** pour isoler les NC à supprimer
3. **Commencez petit** : testez avec 1-2 NC avant une suppression massive
4. **Sauvegardez régulièrement** votre base de données

### ⚠️ À Éviter

- Ne cochez pas aveuglément toutes les NC
- N'utilisez pas cette fonction pour "nettoyer" rapidement sans vérifier
- Ne supprimez pas de NC qui pourraient être référencées ailleurs

### 🎯 Cas d'Usage Typiques

1. **Nettoyage de données de test** : Supprimer les NC créées pour tester l'application
2. **Suppression de doublons** : Éliminer les NC créées par erreur
3. **Purge périodique** : Supprimer les anciennes NC clôturées non archivées
4. **Correction d'import** : Supprimer des NC importées par erreur

---

## 🔧 Caractéristiques Techniques

### Performance

- **Optimisée pour grands volumes** : Peut gérer 100+ NC en une fois
- **Suppression séquentielle** : Une NC à la fois pour gérer les erreurs
- **Cache intelligent** : Rafraîchissement automatique après suppression

### Compatibilité

- **Bases de données** : SQLite (standard)
- **Versions** : QualiManager 2.3.0 et supérieures
- **Plateformes** : Windows 10/11

---

## 📞 Support

### En Cas de Problème

1. **Vérifiez** que vous utilisez la version 2.3.0 ou supérieure
2. **Consultez** les messages d'erreur dans l'application
3. **Contactez** le support technique avec :
   - Le nombre de NC tentées
   - Le message d'erreur exact
   - Les circonstances (filtres appliqués, etc.)

### Changelog Complet

Pour voir toutes les modifications de la version 2.3.0, consultez `CHANGELOG_v2.3.md`.

---

## 🎉 Conclusion

La suppression multiple est un outil puissant pour gérer efficacement vos NC. Utilisez-la avec précaution et profitez du gain de temps qu'elle apporte !

**N'oubliez pas : La suppression est définitive et irréversible !**

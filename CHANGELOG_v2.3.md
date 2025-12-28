# Changelog - QualiManager v2.3.0

## 🚀 Version 2.3.0 - Décembre 2025

### ✨ Nouvelles Fonctionnalités

#### Suppression Multiple de NC
- **Sélection par checkboxes** : Nouvelle colonne de checkboxes dans le tableau Liste des NC
- **Bouton dynamique** : Bouton "Supprimer sélection (X)" qui affiche le nombre de NC sélectionnées
- **Activation intelligente** : Le bouton se désactive automatiquement quand aucune NC n'est sélectionnée
- **Confirmation sécurisée** : Dialogue de confirmation détaillé avant suppression définitive
- **Rapport de résultats** : Message indiquant le nombre de NC supprimées avec succès et les éventuels échecs
- **Réinitialisation automatique** : La sélection est réinitialisée lors du changement d'onglet ou de rafraîchissement

#### Améliorations UX
- Compteur en temps réel du nombre de NC sélectionnées
- Interface intuitive avec icône "DELETE_SWEEP"
- Suppression par lot optimisée pour de grandes quantités

### 🔧 Améliorations Techniques

#### Gestion de l'état
- Nouvel attribut `selected_nc_ids` (Set) pour suivre les sélections
- Méthode `_toggle_nc_selection()` pour gérer les sélections/désélections
- Méthode `_update_delete_multiple_button()` pour mettre à jour l'interface

#### Performance
- Suppression groupée avec gestion d'erreurs individuelles
- Cache rafraîchi automatiquement après suppression
- Transactions optimisées en base de données

### 📝 Modifications de l'Interface

#### Tableau Liste NC
- **Nouvelle colonne** : Colonne "☑" en première position (45px de largeur)
- **Structure** : Configuration mise à jour dans `columns_config`
- **Cellules** : Gestion spéciale pour `col_name == "☑"`

#### Header
- **Nouveau bouton** : "Supprimer sélection" à côté de "Nouvelle NC"
- **Styles** : Rouge (#RED_700) actif, gris désactivé
- **Hauteur** : 40px pour cohérence visuelle

### 🛡️ Sécurité

- **Confirmation obligatoire** : Dialogue modal avant toute suppression
- **Avertissement clair** : Liste des données qui seront supprimées
- **Irréversibilité** : Indication claire que l'action ne peut être annulée
- **Gestion d'erreurs** : Try-catch sur chaque suppression individuelle

### 📊 Métriques

- **Lignes de code ajoutées** : ~150
- **Nouvelles méthodes** : 4 (`_toggle_nc_selection`, `_update_delete_multiple_button`, `_confirm_delete_multiple`, `_delete_multiple_nc`)
- **Fichiers modifiés** : 1 (`flet_app/nc_page.py`)

### 🐛 Corrections de Bugs

- Initialisation correcte de `selected_nc_ids` dans `__init__`
- Référence correcte au bouton dans la structure du header
- Réinitialisation de la sélection lors du rafraîchissement du cache

---

## 📖 Versions Précédentes

### Version 2.2.0
- Messages d'import Excel toujours visibles avec dialogue modal
- Affichage détaillé du nombre de NC importées
- Liste des erreurs scrollable en cas de problème

### Version 2.1.0
- Mapping automatique des colonnes Excel
- Support des variations (accents, abréviations)
- Gestion automatique des dates Excel
- Rafraîchissement automatique après import

### Version 2.0.0
- Interface utilisateur refaite avec Flet
- Système de gestion des NC complet
- Module d'analyse (5 Pourquoi, Ishikawa)
- Statistiques et rapports

---

## 🎯 Utilisation de la Suppression Multiple

### Étapes

1. **Ouvrir l'onglet Liste** des Non-Conformités
2. **Cocher les NC** à supprimer via les checkboxes
3. **Vérifier le compteur** sur le bouton (ex: "Supprimer sélection (3)")
4. **Cliquer** sur le bouton rouge
5. **Confirmer** dans le dialogue
6. **Vérifier le résultat** dans le message de confirmation

### Astuces

- Les checkboxes se décocher automatiquement après suppression
- Le bouton se grise quand aucune NC n'est sélectionnée
- La sélection est perdue lors du changement d'onglet (par sécurité)
- Les NC sont supprimées une par une pour gérer les erreurs

---

## 📞 Support

Pour toute question ou problème, consultez la documentation ou contactez l'équipe de support.

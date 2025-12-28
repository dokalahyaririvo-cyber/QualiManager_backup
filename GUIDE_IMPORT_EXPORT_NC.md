# Guide d'Import et Export des Non-Conformités

## 📤 Export des NC

### Formats disponibles
L'application permet d'exporter les NC dans 3 formats :

1. **Excel (.xlsx)** - Recommandé pour l'analyse et la réutilisation
2. **PDF (.pdf)** - Idéal pour l'archivage et les rapports
3. **CSV (.csv)** - Compatible avec tous les tableurs

### Fonctionnalités d'export

#### ✅ Texte complet avec retours à la ligne
- Tous les exports incluent désormais le **texte complet** des descriptions et actions
- Les retours à la ligne sont préservés
- Plus de troncature avec "..."

#### ✅ Colonnes Lot et Quantité
- Les colonnes **Lot** et **Quantité** sont incluses dans tous les exports
- Positionnées après la colonne **Produit** pour une meilleure traçabilité

#### ✅ Choix de l'emplacement
- Lors de l'export, vous pouvez **choisir** où sauvegarder le fichier
- Plus besoin de chercher dans le dossier Téléchargements

#### ✅ Confirmations
- Message de confirmation après chaque export
- Indication du nombre de NC exportées
- Nom du fichier créé

### Colonnes exportées

Les 15 colonnes suivantes sont exportées :

1. **Référence** - Identifiant unique de la NC
2. **Date** - Date de détection
3. **Statut** - En cours / Clôturée
4. **Type** - Interne / Client / Fournisseur / Prestataire / Audit
5. **Gravité** - Mineure / Majeure / Critique
6. **Origine** - Source de la non-conformité
7. **Produit** - Produit concerné
8. **Lot** - Numéro de lot ou série
9. **Quantité** - Quantité affectée
10. **Description** - Description complète (avec retours à la ligne)
11. **Catégorie** - Catégorie de NC
12. **Imputation** - Service responsable
13. **Responsable** - Personne en charge du traitement
14. **Actions** - Actions immédiates (avec retours à la ligne)
15. **Coût** - Coût estimé

### Spécificités par format

#### Excel
- Retour à la ligne automatique activé (wrap_text)
- Largeurs de colonnes optimisées
- En-têtes avec fond bleu et texte en gras
- Alignement vertical en haut pour meilleure lisibilité

#### PDF
- Format paysage (landscape) pour plus d'espace
- Paragraphes avec wrapping pour textes longs
- 9 colonnes optimisées pour la page
- Police réduite pour maximiser le contenu

#### CSV
- Délimiteur : point-virgule (;)
- Encodage : UTF-8 avec BOM (compatible Excel)
- Compatible avec tous les tableurs

---

## 📥 Import depuis Excel

### Format du fichier Excel requis

Pour importer des NC depuis Excel, votre fichier doit respecter le format suivant :

#### En-têtes obligatoires (ligne 1)
```
Référence | Date | Statut | Type | Gravité | Origine | Produit | Lot | Quantité | Description | Catégorie | Imputation | Responsable | Actions | Coût
```

#### Colonnes obligatoires
- **Référence** : Identifiant unique (ex: NC-2024-001)
- **Date** : Date de détection (format: AAAA-MM-JJ ou JJ/MM/AAAA)

#### Colonnes optionnelles
Toutes les autres colonnes peuvent être vides, mais il est recommandé de remplir :
- **Statut** : "En cours" ou "Clôturée" (par défaut: "En cours")
- **Gravité** : "Mineure", "Majeure" ou "Critique" (par défaut: "Mineure")
- **Type** : "Interne", "Client", "Fournisseur", "Prestataire" ou "Audit"

### Procédure d'import

1. **Préparer votre fichier Excel**
   - Utilisez le modèle exporté comme référence
   - Première ligne = en-têtes
   - Données à partir de la ligne 2

2. **Lancer l'import**
   - Allez dans l'onglet **Liste NC**
   - Section **Filtres**
   - Cliquez sur **"Depuis Excel"** dans la zone Import

3. **Sélectionner le fichier**
   - Une fenêtre de sélection s'ouvre
   - Choisissez votre fichier .xlsx ou .xls
   - Cliquez sur **Ouvrir**

4. **Vérifier le résultat**
   - Un message indique le nombre de NC importées
   - En cas d'erreurs, une boîte de dialogue détaille les lignes problématiques

### Validation des données

L'import effectue les validations suivantes :
- ✅ Référence et Date obligatoires
- ✅ Vérification du format de fichier
- ✅ Au minimum 10 colonnes requises
- ✅ Détection des doublons (si référence existe déjà)

### Gestion des erreurs

Si des erreurs surviennent :
- Les NC valides sont importées
- Les lignes avec erreurs sont ignorées
- Un rapport détaille les erreurs par numéro de ligne
- Maximum 10 premières erreurs affichées

### Conseils

#### ✅ À faire
- Exporter d'abord pour obtenir un modèle valide
- Vérifier les références uniques
- Respecter le format des dates
- Utiliser les valeurs autorisées (Statut, Gravité, etc.)

#### ❌ À éviter
- Modifier les en-têtes de colonnes
- Supprimer des colonnes essentielles
- Utiliser des formats de date non standards
- Laisser Référence ou Date vides

### Exemple de fichier valide

```
Référence    | Date       | Statut    | Type     | Gravité  | Origine | Produit  | Lot      | Quantité | Description
NC-2024-001 | 2024-01-15 | En cours  | Interne  | Majeure  | Production | VIN-A  | LOT-123 | 500     | Problème qualité
NC-2024-002 | 2024-01-16 | Clôturée | Client   | Mineure  | Expédition | VIN-B  | LOT-124 | 100     | Étiquetage incorrect
```

---

## 🔄 Workflow complet

### Scénario 1 : Export pour analyse
1. Appliquer les filtres souhaités
2. Cliquer sur **Excel** ou **CSV**
3. Choisir l'emplacement
4. Ouvrir le fichier pour analyse

### Scénario 2 : Export puis import modifié
1. Exporter les NC existantes
2. Modifier/Ajouter des lignes dans Excel
3. Importer le fichier modifié
4. Vérifier les nouvelles NC dans la liste

### Scénario 3 : Import en masse
1. Préparer un fichier Excel avec toutes les colonnes
2. Remplir les données (peut provenir d'un autre système)
3. Importer via le bouton "Depuis Excel"
4. Vérifier le rapport d'import

---

## ⚠️ Notes importantes

- **Encodage** : Les fichiers CSV utilisent UTF-8 avec BOM pour la compatibilité Excel
- **Délimiteur CSV** : Point-virgule (;) pour compatibilité française
- **Taille** : Pas de limite théorique, mais les très gros fichiers PDF peuvent être lents
- **Sécurité** : L'import ne supprime jamais de données existantes
- **Doublons** : Si une référence existe déjà, la ligne est ignorée lors de l'import

---

## 📞 Support

En cas de problème :
1. Vérifier le format du fichier Excel
2. S'assurer que openpyxl est installé (pour Excel)
3. Consulter la console pour les messages d'erreur détaillés
4. Vérifier que les données respectent les contraintes (statut, gravité, etc.)

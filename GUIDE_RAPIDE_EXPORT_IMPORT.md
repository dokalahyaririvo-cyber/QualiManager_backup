# 🚀 Guide Rapide - Export et Import de NC

## ⚡ Démarrage rapide

### 📤 Pour exporter des NC

1. **Ouvrez l'onglet "Liste NC"**
2. **(Optionnel)** Appliquez des filtres (statut, gravité, dates, etc.)
3. **Cliquez sur le bouton de votre choix :**
   - **Excel** (vert) → Meilleur pour l'analyse
   - **PDF** (rouge) → Meilleur pour l'archivage
   - **CSV** (bleu) → Compatible tous tableurs
4. **Choisissez où sauvegarder** le fichier
5. **Confirmez** → Message de succès s'affiche

✅ **Nouveauté** : Tout le texte est exporté (descriptions complètes avec retours à la ligne) + colonnes Lot et Quantité ajoutées !

---

### 📥 Pour importer des NC depuis Excel

#### Première fois ?
1. **Utilisez le modèle fourni** : `MODELE_IMPORT_NC.xlsx`
2. **Ouvrez-le dans Excel**
3. **Modifiez ou ajoutez** vos propres NC
4. **Suivez le format** (ne modifiez pas les en-têtes)

#### Import
1. **Ouvrez l'onglet "Liste NC"**
2. **Cliquez sur "Depuis Excel"** (bouton orange)
3. **Sélectionnez votre fichier** .xlsx
4. **Attendez la validation**
5. **Vérifiez le résumé** : X importées, Y erreurs

⚠️ **Important** : Les colonnes Référence et Date sont obligatoires !

---

## 📋 Format Excel requis

### Colonnes (dans cet ordre)
```
1.  Référence      → NC-2024-001 (obligatoire, unique)
2.  Date           → 2024-01-15 (obligatoire)
3.  Statut         → En cours / Clôturée
4.  Type           → Interne / Client / Fournisseur / Prestataire / Audit
5.  Gravité        → Mineure / Majeure / Critique
6.  Origine        → Production, Expédition, etc.
7.  Produit        → Nom du produit concerné
8.  Lot            → Numéro de lot
9.  Quantité       → Quantité affectée
10. Description    → Description complète (peut contenir plusieurs lignes)
11. Catégorie      → Type de problème
12. Imputation     → Service responsable
13. Responsable    → Nom de la personne
14. Actions        → Actions immédiates (peut contenir plusieurs lignes)
15. Coût           → Coût estimé en euros
```

### Exemple de ligne valide
```
NC-2024-001 | 2024-01-15 | En cours | Interne | Majeure | Production | VIN-ROUGE-A | LOT-001 | 500 | Problème qualité... | Qualité | Cuverie | Jean Dupont | Quarantaine | 1500
```

---

## ✅ Checklist avant import

- [ ] Fichier au format .xlsx ou .xls
- [ ] Première ligne = en-têtes (ne pas modifier)
- [ ] Colonne Référence remplie (unique)
- [ ] Colonne Date remplie (format AAAA-MM-JJ ou JJ/MM/AAAA)
- [ ] Les valeurs Statut/Gravité/Type respectent les options autorisées
- [ ] Pas de cellules fusionnées

---

## 🎯 Cas d'usage courants

### Cas 1 : Rapport mensuel
```
Filtres → Mois précédent → Export Excel → Analyse dans Excel
```

### Cas 2 : Archivage PDF
```
Filtres → Année complète → Export PDF → Sauvegarde archives
```

### Cas 3 : Import données externes
```
Modèle Excel → Remplir données → Import → Vérifier
```

### Cas 4 : Dupliquer/Modifier en masse
```
Export Excel → Modifier références/dates → Import → Nouvelles NC créées
```

---

## ❌ Erreurs courantes

| Erreur | Cause | Solution |
|--------|-------|----------|
| "Colonnes insuffisantes" | Moins de 10 colonnes | Utiliser le modèle fourni |
| "Référence obligatoire" | Cellule Référence vide | Remplir toutes les références |
| "Date obligatoire" | Cellule Date vide | Remplir toutes les dates |
| "Format invalide" | Fichier corrompu | Utiliser .xlsx valide |
| Import bloqué | openpyxl non installé | Vérifier requirements.txt |

---

## 💡 Astuces

### Export
- **Filtrez avant d'exporter** pour cibler les NC voulues
- **Excel** : Meilleur pour réutiliser les données
- **PDF** : Compact mais non modifiable
- **CSV** : Compatible avec tous les logiciels

### Import
- **Testez avec 1 ligne** avant d'importer 100 NC
- **Utilisez le modèle** comme base
- **Vérifiez le rapport** pour corriger les erreurs
- **Les erreurs n'annulent pas** les lignes valides

### Retours à la ligne
- **Dans Excel** : ALT + Entrée
- **Dans l'export** : Préservés automatiquement
- **Dans l'import** : Reconnus et conservés

---

## 📞 Besoin d'aide ?

1. **Guide complet** → [GUIDE_IMPORT_EXPORT_NC.md](GUIDE_IMPORT_EXPORT_NC.md)
2. **Modèle Excel** → `MODELE_IMPORT_NC.xlsx`
3. **Documentation NC** → [DOCUMENTATION_MODULE_NC.md](DOCUMENTATION_MODULE_NC.md)
4. **Résumé technique** → [RESUME_AMELIORATIONS_EXPORT_IMPORT.md](RESUME_AMELIORATIONS_EXPORT_IMPORT.md)

---

## 🎉 C'est tout !

Vous êtes maintenant prêt à :
- ✅ Exporter vos NC avec tout le contenu
- ✅ Choisir où sauvegarder vos fichiers
- ✅ Importer des NC en masse depuis Excel
- ✅ Gérer vos données de façon professionnelle

**Bonne gestion qualité ! 🏭**

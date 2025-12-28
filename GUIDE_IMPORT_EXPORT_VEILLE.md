# Guide d'utilisation - Import/Export Veille & Plans d'Actions

## 📥 Import Excel (Veilles uniquement)

### Format du fichier Excel

**Colonnes obligatoires :**
- `source` : Source de la veille (ex: ISO 9001, RGPD, etc.)
- `description` : Description complète de la veille

**Colonnes optionnelles :**
- `date_publication` : Date de publication (format: YYYY-MM-DD)
- `lien_url` : Lien web vers la source
- `commentaire_interne` : Commentaire interne
- `date_lecture` : Date de lecture (format: YYYY-MM-DD)
- `statut_veille` : Statut (Conforme | Concerné | À l'étude | Non concerné)
- `plan_action_numero` : Numéro du plan d'action associé

### Utilisation

1. Cliquez sur **"Importer Excel"** dans l'onglet "Registre des Veilles"
2. Sélectionnez votre fichier .xlsx ou .xls
3. Le système importe automatiquement les données
4. Un message de confirmation indique le nombre de veilles importées

### Template

Un fichier template est disponible : `Template_Import_Veilles.xlsx`
Pour le générer/régénérer : `python create_import_template.py`

---

## 📤 Export PDF & Excel

### Export des Veilles

**Depuis l'onglet "Registre des Veilles" :**
1. Cliquez sur l'icône 📥 "Exporter"
2. Choisissez le format :
   - 📄 **PDF** : Document formaté pour impression
   - 📊 **Excel** : Fichier modifiable avec toutes les colonnes

**Contenu exporté :**
- ID, Source, Dates, Description
- Lien URL, Commentaire, Statut
- N° Plan d'action associé

### Export des Plans d'Actions

**Depuis l'onglet "Plans d'Actions" :**
1. Cliquez sur l'icône 📥 "Exporter"
2. Choisissez le format :
   - 📄 **PDF** : Document formaté pour impression
   - 📊 **Excel** : Fichier modifiable avec toutes les colonnes

**Contenu exporté :**
- ID, Date de création, Origine
- Objectif, Priorité, Type
- Auteurs, Échéance, Date soldé
- Avancement (%)

---

## 📁 Emplacement des fichiers exportés

Les fichiers exportés sont créés dans le **répertoire de travail** de l'application avec le format de nom :
- Veilles : `Veilles_Export_YYYYMMDD_HHMMSS.xlsx` ou `.pdf`
- Plans : `Plans_Actions_Export_YYYYMMDD_HHMMSS.xlsx` ou `.pdf`

---

## 💡 Conseils

### Pour l'import Excel :
- ✅ Utilisez le template fourni pour éviter les erreurs
- ✅ Vérifiez que les dates sont au format YYYY-MM-DD
- ✅ Les statuts doivent correspondre exactement aux valeurs valides
- ⚠️ Seules les lignes avec `source` ET `description` sont importées

### Pour l'export :
- 📄 **PDF** : Idéal pour archivage et diffusion
- 📊 **Excel** : Idéal pour traitement ultérieur et analyse
- 🔄 Les exports sont horodatés pour éviter les écrasements

---

## 🛠️ Dépendances

Les fonctionnalités d'import/export nécessitent :
- `openpyxl` : Gestion Excel
- `pandas` : Import de données
- `reportlab` : Génération PDF

Ces bibliothèques sont incluses dans `requirements.txt`.

# 📥 Guide d'Import des NC depuis Excel

## Vue d'ensemble

Le script `import_nc_excel.py` permet d'importer en masse des NC depuis un fichier Excel vers QualiManager.

---

## 🔧 Installation des dépendances

Avant d'utiliser le script, installez les modules nécessaires :

```bash
cd "F:\Applications\Gestion Qualité"
.\venv\Scripts\pip.exe install pandas openpyxl
```

---

## 📋 Préparation du fichier Excel

### Colonnes reconnues automatiquement

Le script reconnaît automatiquement ces noms de colonnes (parmi d'autres variantes) :

| Colonne Excel | Champ BDD | Obligatoire |
|---------------|-----------|-------------|
| Référence / N° NC | reference | Non (auto-généré) |
| Date / Date détection | date_detection | Recommandé |
| Type / Type NC | type_nc | Non (défaut: Interne) |
| Gravité / Criticité | gravite | Non (défaut: Mineure) |
| Origine | origine | Non |
| Type anomalie / Anomalie | type_anomalie | Non |
| Catégorie / Catégorie NC | categorie_nc | Non |
| Imputation / Service | imputation | Non |
| Description / Problème | description | Recommandé |
| Produit / Produit concerné | produit_concerne | Non |
| Lot / N° Lot / Série | lot_serie | Non |
| Quantité / Qté affectée | quantite_affectee | Non |
| **Matières / Matières réclamées** | matieres_reclames | Non |
| Statut / État | statut | Non (défaut: En cours) |
| Cause racine / Cause | cause_racine | Non |
| Lieu / Lieu détection | lieu_detection | Non |

### Exemple de structure Excel

```
| Référence  | Date       | Type     | Gravité  | Description           | Produit  | Lot      | Matières réclamées |
|------------|------------|----------|----------|-----------------------|----------|----------|--------------------|
| NC-2024-001| 2024-01-15 | Client   | Majeure  | Bouchon défectueux    | Crémant  | LOT-123  | Bouchons           |
| NC-2024-002| 2024-01-20 | Interne  | Mineure  | Étiquette mal placée  | VMQ      | LOT-456  | Étiquettes         |
```

---

## 🚀 Utilisation

### 1️⃣ Mode TEST (simulation sans insertion)

**Recommandé pour la première utilisation !**

```bash
cd "F:\Applications\Gestion Qualité"
.\venv\Scripts\python.exe import_nc_excel.py chemin\vers\votre_fichier.xlsx --dry-run
```

Ce mode :
- ✅ Lit le fichier Excel
- ✅ Affiche les colonnes détectées
- ✅ Montre les 5 premières lignes transformées
- ❌ **N'insère RIEN dans la base**

### 2️⃣ Mode IMPORT (insertion réelle)

**Une fois le test validé :**

```bash
.\venv\Scripts\python.exe import_nc_excel.py chemin\vers\votre_fichier.xlsx --import
```

Ce mode insère réellement les données dans la base `qualimanager_erp.db`.

### 3️⃣ Spécifier une feuille particulière

Si votre Excel a plusieurs feuilles :

```bash
# Par nom
.\venv\Scripts\python.exe import_nc_excel.py mon_fichier.xlsx --import --sheet=Feuille1

# Par index (0 = première feuille)
.\venv\Scripts\python.exe import_nc_excel.py mon_fichier.xlsx --import --sheet=0
```

---

## 🎯 Exemples complets

### Exemple 1 : Test avec fichier sur le Bureau

```powershell
cd "F:\Applications\Gestion Qualité"
.\venv\Scripts\python.exe import_nc_excel.py "C:\Users\VotreNom\Desktop\nc_2024.xlsx" --dry-run
```

### Exemple 2 : Import réel depuis un dossier

```powershell
.\venv\Scripts\python.exe import_nc_excel.py "D:\Documents\NC_export.xlsx" --import
```

### Exemple 3 : Import d'une feuille spécifique

```powershell
.\venv\Scripts\python.exe import_nc_excel.py "mes_nc.xlsx" --import --sheet=NC_2024
```

---

## ⚙️ Personnalisation du mapping

Si vos colonnes Excel ont des noms différents, modifiez le dictionnaire `column_mapping` dans le script (ligne ~70) :

```python
column_mapping = {
    # Vos noms de colonnes → Noms BDD
    'NumeroNC': 'reference',
    'DateConstat': 'date_detection',
    'TypeDeNC': 'type_nc',
    # etc.
}
```

---

## 📊 Format des données

### Dates
- Formats acceptés : `2024-01-15`, `15/01/2024`, ou format Excel natif
- Convertis automatiquement en `YYYY-MM-DD`

### Type NC
Valeurs acceptées : `Interne`, `Client`, `Fournisseur`, `Prestataire`, `Audit`

### Gravité
Valeurs acceptées : `Mineure`, `Majeure`, `Critique`

### Statut
Valeurs acceptées : `En cours`, `Clôturée`

### Matières réclamées
Valeurs acceptées : `Crémants`, `VMQ`, `Vins tranquiles`, `Bouchons`, `Bouteilles`, `Muselets`, `Contre-étiquettes`, `Étiquettes`, `Collerettes`, `Coiffes`, `Cartons`, `Boxes`, `Machines`, `Capsules`, `Bidules`, `Cerises`, `Crèmes`, `Ratafia`, `Coffrets`

---

## ⚠️ Points d'attention

### Références NC
- Si la colonne "Référence" est vide, le script génère automatiquement : `NC-YYYY-NNNN`
- Les références existantes sont préservées (pas de duplication automatique)

### Doublons
- Le script n'effectue **pas** de détection de doublons
- Si une référence existe déjà, l'insertion échouera pour cette ligne

### Encodage
- Le fichier Excel doit être en format `.xlsx` (pas `.xls`)
- Les caractères spéciaux (accents) sont gérés automatiquement

---

## 🐛 Résolution de problèmes

### Erreur "Module pandas not found"
```bash
.\venv\Scripts\pip.exe install pandas openpyxl
```

### Erreur "No such table: nc_header"
Lancez l'application une fois pour créer les tables :
```bash
.\venv\Scripts\python.exe app_erp.py
# Fermez l'application, puis relancez l'import
```

### Colonnes non reconnues
- Vérifiez l'affichage "Colonnes détectées" en mode `--dry-run`
- Adaptez le `column_mapping` dans le script si nécessaire

### Erreur d'insertion
- Le script affiche la ligne problématique
- Corrigez dans Excel et relancez l'import

---

## 📈 Résultat attendu

Après un import réussi :

```
==================================================================
   IMPORT DE NC DEPUIS EXCEL VERS QUALIMANAGER
==================================================================

✅ Connexion à la base: qualimanager_erp.db

📂 Lecture du fichier: mes_nc.xlsx
✅ 150 lignes trouvées
📋 Colonnes détectées: Référence, Date, Type, Gravité, Description, ...

✅ Colonnes après mapping: reference, date_detection, type_nc, ...

🧹 Nettoyage des données...
✅ 150 lignes nettoyées

💾 IMPORT de 150 NC...
==================================================================
   ✅ 10/150 NC importées...
   ✅ 20/150 NC importées...
   ...
   ✅ 150/150 NC importées...

==================================================================
✅ Import terminé:
   - Succès: 150
   - Erreurs: 0

✅ Connexion fermée
✅ Script terminé
```

---

## 💡 Conseils

1. **Testez toujours avec `--dry-run` d'abord**
2. **Faites une sauvegarde** de `qualimanager_erp.db` avant l'import
3. **Importez par petits lots** (50-100 NC) pour faciliter le débogage
4. **Vérifiez les données** dans l'application après import

---

## 🆘 Support

En cas de problème, vérifiez :
1. Le format du fichier Excel (`.xlsx`)
2. Les noms des colonnes (majuscules/minuscules)
3. Les logs d'erreur du script
4. Que l'application n'est pas en cours d'exécution pendant l'import

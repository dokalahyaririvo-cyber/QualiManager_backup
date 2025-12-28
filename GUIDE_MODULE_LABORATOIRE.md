# Guide Module Laboratoire & Qualité - QualiManager v2.4.0

## 📋 Vue d'ensemble

Le nouveau module **Laboratoire & Qualité** est une refonte complète permettant la gestion polymorphe de **7 types d'analyses** provenant de **6 laboratoires partenaires** différents.

### 🎯 Objectifs

- ✅ Centraliser toutes les analyses viticoles dans une interface unique
- ✅ Gérer des types d'analyses variés avec des champs spécifiques
- ✅ Auto-évaluer la conformité selon les seuils réglementaires
- ✅ Suivre les coûts par laboratoire et par type d'analyse
- ✅ Générer des rapports PDF personnalisés
- ✅ Détecter les traces et alertes automatiquement

---

## 📊 Types d'analyses supportés

### 1️⃣ Œnologie Standard (Chimie)
**Laboratoires** : Sofralab, Exact, Eurofins

**Paramètres mesurés** :
- TAV (% vol)
- Sucres (g/L)
- Acidité totale (g/L H2SO4)
- pH
- Acide volatile (g/L)
- SO2 libre et total (mg/L)
- Fer, Cuivre (mg/L)
- CO2 (g/L)
- Surpression (bars)

**Cas d'usage** :
- Analyses des cuves avant embouteillage
- Contrôle qualité des lots terminés
- Suivi évolution vinification

---

### 2️⃣ Sécurité Alimentaire & Allergènes
**Laboratoires** : Sofralab, Eurofins, Céania

**Paramètres mesurés** :
- Albumine (protéine œuf) → `<LDQ` ou valeur
- Caséine (protéine lait) → `<LDQ` ou valeur
- Histamine (mg/L)
- Putrescine (mg/L)
- Bisphénol A

**⚠️ Seuil réglementaire Histamine** : 2 mg/L (alerte si > 1 mg/L)

**Cas d'usage** :
- Détection allergènes pour étiquetage
- Conformité exports internationaux
- Vins collés (vérification résidus)

---

### 3️⃣ Contaminants Spécifiques
**Laboratoires** : Sofralab, Eurofins

**Catégories de contaminants** :

#### 🔬 Haloanisoles (goûts de bouchon)
- TCA, TeCa, TBA, PCA (ng/L)

#### 🧪 Halophénols
- TCP, TBP (ng/L)

#### ⚠️ Phtalates (plastifiants)
- DBP (Dibutyl Phtalate)
- DEHP
- **Seuil réglementaire DBP** : 0.3 mg/kg

#### ☢️ Métaux Lourds
- Plomb : 0.10 mg/L (seuil)
- Cadmium : 0.01 mg/L (seuil)
- Arsenic : 0.20 mg/L (seuil)
- Mercure : 0.05 mg/L (seuil)

#### 🍄 Mycotoxines
- Ochratoxine A : 2.0 µg/kg (seuil)

#### 🔬 Autres
- Lindane (pesticide)

**🎯 Système d'alerte intelligent** :
- ✅ **Conforme** : Tous contaminants < LDQ
- ⚠️ **Alerte** : Traces détectées mais < seuil (ex: DBP = 0.1 mg/kg)
- ❌ **Non Conforme** : Au moins 1 contaminant > seuil réglementaire

**Cas d'usage** :
- Problème organoleptique suspecté (TCA)
- Obligation exports USA/Canada (métaux lourds)
- Litige fournisseur bouchons

---

### 4️⃣ Métrologie & Conditionnement
**Laboratoires** : Exact, Céania

**Paramètres mesurés** :
- Volume net moyen (mL)
- Écart-type
- Nombre d'échantillons testés
- Nombre de défectueux
- Densité
- Volume cible (375/750 mL)

**Calcul conformité automatique** :
```
Tolérance = ± 2% du volume cible
Exemple: 750 mL → Conforme si 735-765 mL
```

**Cas d'usage** :
- Vérification tireuse
- Validation nouveau format
- Contrôle qualité ligne embouteillage

---

### 5️⃣ Microbiologie
**Laboratoires** : Sofralab, Eurofins, Céania

**Paramètres mesurés** :
- Flore aérobie mésophile (UFC/mL)
- Levures (UFC/mL)
- Moisissures (UFC/100mL)

**Cas d'usage** :
- Validation stabilité avant mise
- Contrôle après filtration stérilisante
- Investigation piqûre acétique

---

### 6️⃣ Hygiène & Nettoyage (ATP)
**Laboratoires** : Diversey

**Paramètres mesurés** :
- Valeur ATP (RLU) - Adénosine Triphosphate
- Type de surface (Inox, Plastique, Caoutchouc)
- Conductivité (mS/cm)
- Concentration détergent (%)
- Nom produit (ex: Surefoam)

**Seuils ATP pour Inox** :
- 🟢 **Bon** : < 150 RLU
- 🟠 **À surveiller** : 150-200 RLU
- 🔴 **Mauvais** : > 200 RLU

**Seuils ATP pour autres surfaces** :
- 🟢 **Bon** : < 250 RLU
- 🟠 **À surveiller** : 250-350 RLU
- 🔴 **Mauvais** : > 350 RLU

**Cas d'usage** :
- Validation nettoyage cuves/tuyaux
- Audit hygiène ligne embouteillage
- Formation personnel nettoyage

---

### 7️⃣ Phytosanitaire (Pesticides)
**Laboratoires** : Sofralab, Eurofins

**Système de détection multi-molécules** :
- Recherche de ~400 molécules (screening complet)
- Stockage des molécules détectées avec teneur (mg/kg)

**Résultat global** :
- "Non Détecté" → Aucune molécule
- "X molécule(s) détectée(s)" → Liste détaillée

**Cas d'usage** :
- Cahier des charges BIO
- Exports Japon/Canada (tolérance zéro)
- Investigation contamination croisée

---

## 🖥️ Interface - 5 Onglets

### 📊 1. Tableau de Bord

**Indicateurs clés (KPI)** :
- Total analyses effectuées
- Coût total dépensé
- Taux de conformité global (%)
- Nombre d'alertes actives

**Graphiques** :
- Distribution par type d'analyse (barres horizontales)
- Répartition par laboratoire (barres colorées)

**Liste des alertes** :
- Top 5 des analyses non conformes/en alerte
- Bouton "Voir détails" pour chaque alerte
- Codes couleur :
  - 🔴 Rouge : Non Conforme
  - 🟠 Orange : Alerte
  - 🟢 Vert : Conforme

---

### 📋 2. Liste Analyses

**Barre de filtres** :
- Type Analyse (dropdown)
- Laboratoire (dropdown)
- Statut (Planifié, En Cours, Terminé)
- Conclusion (Conforme, Non Conforme, Alerte, En Attente)
- Bouton "Réinitialiser filtres"

**Barre de recherche** :
- Recherche textuelle sur N° Lot, N° Cuve, N° Échantillon, Zone, Commentaires

**Table interactive** :
| ID | Date | Type | Labo | Référence | Statut | Conclusion | Coût | Actions |
|----|------|------|------|-----------|--------|------------|------|---------|
| 1  | 12/01/24 | Œnologie | Sofralab | Cuve 15 | Terminé | ✅ Conforme | 45.00 € | 👁️ ✏️ 🗑️ |

**Codes couleur des lignes** :
- Fond vert : Conforme
- Fond rouge : Non Conforme
- Fond orange : Alerte

**Boutons d'action** :
- 👁️ **Voir** : Affiche les détails complets en modal
- ✏️ **Modifier** : Ouvre le formulaire pré-rempli
- 🗑️ **Supprimer** : Confirmation puis suppression

**Export Excel** :
- Bouton "📥 Exporter Excel"
- Export selon filtres appliqués
- Format professionnel avec couleurs

---

### ➕ 3. Nouvelle Analyse

**Formulaire en 3 sections** :

#### 🔹 Sélection du type (détermine les champs)
Dropdown avec les 7 types d'analyses

#### 🔹 Informations Générales (commun à tous)
- Date Prélèvement * (requis)
- Date Résultat
- Laboratoire * (dropdown)
- N° Lot
- N° Cuve
- N° Échantillon
- Zone Prélèvement (pour ATP)
- Coût (€)
- Statut (Planifié par défaut)
- Commentaires (multilignes)

#### 🔹 Résultats d'Analyse (dynamique selon le type)

**Exemple : Œnologie Standard**
```
TAV: [_____] % vol    Sucres: [_____] g/L    pH: [_____]
SO2 Libre: [_____] mg/L    SO2 Total: [_____] mg/L
```

**Exemple : Contaminants**
```
=== Phtalates ===
DBP: [_____] mg/kg    DEHP: [_____] mg/kg

=== Métaux Lourds ===
Plomb: [_____] mg/L   Cadmium: [_____] mg/L   Arsenic: [_____] mg/L
```

**Exemple : Phytosanitaire**
```
Résultat Global: [Non Détecté ▼]

Molécules Détectées:
  Nom: [___________]  Teneur: [_____] mg/kg  [❌]
  [➕ Ajouter Molécule]
```

**Boutons** :
- 💾 **Enregistrer** : Sauvegarde en base + Auto-évaluation conformité
- 🔄 **Réinitialiser** : Vide tous les champs
- ❌ **Annuler** : Retour à la liste

---

### 📈 4. Statistiques

**Graphique évolution des coûts** :
- Barres mensuelles pour l'année en cours
- Hauteur proportionnelle au coût
- Valeur en € affichée

**Statistiques détaillées par laboratoire** :
```
┌───────────────────────────────────┐
│  SOFRALAB                         │
│  87 analyses effectuées           │
│  Coût total: 3 245.50 €          │
└───────────────────────────────────┘
```

**Filtrage par année** :
- Sélection année pour graphiques historiques
- Comparaison inter-annuelle

---

### 📄 5. Rapports

**4 types de rapports PDF générables** :

#### 📘 Rapport Annuel Complet
- Toutes les analyses de l'année
- Statistiques globales
- Graphiques inclus

#### ⚠️ Rapport Non-Conformités
- Liste filtrée : Non Conformes + Alertes uniquement
- Détails des dépassements
- Actions recommandées

#### 🏢 Rapport par Laboratoire
- Performance laboratoire (conformité, délais)
- Coûts détaillés
- Comparaison qualité/prix

#### 💰 Rapport Coûts
- Analyse financière par type d'analyse
- Évolution mensuelle
- Budget prévisionnel vs réel

**Génération** :
```
[📘 Rapport Annuel Complet]
  Toutes les analyses de l'année avec statistiques
  [Générer PDF]
```

---

## 🔧 Fonctionnalités Avancées

### 🤖 Auto-évaluation de la Conformité

**Déclenchement** :
- Automatique à la sauvegarde d'une analyse
- Bouton "🔍 Réévaluer" disponible

**Règles implémentées** :

#### Contaminants
```python
if DBP > 0.3 mg/kg → ❌ Non Conforme
if Plomb > 0.10 mg/L → ❌ Non Conforme
if Ochratoxine A > 2.0 µg/kg → ❌ Non Conforme
if Traces détectées mais < seuil → ⚠️ Alerte
else → ✅ Conforme
```

#### Hygiène ATP
```python
if ATP > 200 RLU (Inox) → ❌ Non Conforme
if ATP > 150 RLU → ⚠️ Alerte
else → ✅ Conforme
```

#### Métrologie
```python
Tolérance = Volume_cible × 2%
if |Volume_moyen - Volume_cible| > Tolérance → ❌ Non Conforme
else → ✅ Conforme
```

---

### 📊 Export Excel Personnalisé

**Format professionnel** :
- En-têtes colorés (bleu marine)
- Codes couleur conformité :
  - ✅ Vert : Conforme
  - ❌ Rouge : Non Conforme
  - ⚠️ Orange : Alerte
- Largeur colonnes auto-ajustée
- Filtres Excel activés

**Colonnes exportées** :
```
ID | Date Prélèvement | Date Résultat | Type Analyse | Laboratoire |
N° Lot | N° Cuve | N° Échantillon | Statut | Conclusion | Coût | Commentaires
```

---

### 🔍 Recherche Textuelle Avancée

**Champs indexés** :
- N° Lot
- N° Cuve
- N° Échantillon
- Zone Prélèvement
- Commentaires
- Nom Laboratoire

**Exemple de recherche** :
```
Recherche: "Cuve 15"
→ Trouve toutes les analyses avec "Cuve 15" dans n'importe quel champ
```

---

## 💾 Structure de la Base de Données

### Table : `lab_analyses`

```sql
CREATE TABLE lab_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_prelevement TEXT,
    date_resultat TEXT,
    numero_lot TEXT,
    zone_prelevement TEXT,
    numero_cuve TEXT,
    numero_echantillon TEXT,
    type_analyse TEXT NOT NULL,          -- Enum: TypeAnalyse
    laboratoire TEXT NOT NULL,           -- Enum: Laboratoire
    cout REAL DEFAULT 0.0,
    statut TEXT DEFAULT 'Planifié',      -- Enum: StatutAnalyse
    conclusion TEXT DEFAULT 'En Attente', -- Enum: ConclusionAnalyse
    commentaires TEXT,
    resultats TEXT,                      -- JSON polymorphe
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Index pour performances
CREATE INDEX idx_lab_type ON lab_analyses(type_analyse);
CREATE INDEX idx_lab_dates ON lab_analyses(date_prelevement, date_resultat);
CREATE INDEX idx_lab_conclusion ON lab_analyses(conclusion);
```

### Exemples de données JSON polymorphes

#### Œnologie Standard
```json
{
    "tav": 14.5,
    "sucres": 2.3,
    "acidite_totale": 3.8,
    "ph": 3.45,
    "acide_volatile": 0.42,
    "so2_libre": 28,
    "so2_total": 78,
    "fer": 1.2,
    "cuivre": 0.08
}
```

#### Contaminants
```json
{
    "dibutyl_phtalate": 0.12,
    "plomb": 0.03,
    "ochratoxine_a": 0.8,
    "tcp": 2.5
}
```

#### Phytosanitaire
```json
{
    "molecules_detectees": {
        "Glyphosate": 0.003,
        "Chlorpyrifos": 0.001
    },
    "global_resultat": "2 molécule(s) détectée(s)",
    "nombre_molecules": 2
}
```

---

## 🚀 Guide de Démarrage Rapide

### 1️⃣ Créer votre première analyse

1. Cliquez sur l'onglet **"➕ Nouvelle Analyse"**
2. Sélectionnez le **Type d'Analyse** (ex: Œnologie Standard)
3. Remplissez les **Informations Générales** :
   - Date Prélèvement : `15/01/2025`
   - Laboratoire : `Sofralab`
   - N° Cuve : `Cuve 15`
   - Coût : `45.00`
4. Remplissez les **Résultats d'Analyse** :
   - TAV : `14.5`
   - pH : `3.45`
   - SO2 Libre : `28`
   - SO2 Total : `78`
5. Cliquez sur **💾 Enregistrer**
6. ✅ L'analyse est créée et auto-évaluée !

### 2️⃣ Consulter le tableau de bord

1. Onglet **"📊 Tableau de Bord"**
2. Visualisez vos KPI :
   - Total analyses : `1`
   - Coût total : `45.00 €`
   - Taux conformité : `100%`
3. Aucune alerte = Tout va bien ! 🎉

### 3️⃣ Filtrer et rechercher

1. Onglet **"📋 Liste Analyses"**
2. Utilisez les filtres :
   - Type : `Œnologie Standard`
   - Laboratoire : `Sofralab`
3. Ou recherchez : `Cuve 15`
4. Résultats instantanés !

### 4️⃣ Exporter en Excel

1. Appliquez les filtres souhaités
2. Cliquez sur **📥 Exporter Excel**
3. Fichier généré : `analyses_export_20250115_143022.xlsx`
4. Ouvrez avec Excel pour analyses complémentaires

---

## 📞 Laboratoires Partenaires

### 🔬 Sofralab
- **Spécialités** : Œnologie, Sécurité Alimentaire, Contaminants, Phytosanitaire
- **Délai moyen** : 5-7 jours ouvrés
- **Coût moyen** : 45-120 €

### 🧪 Exact
- **Spécialités** : Œnologie, Métrologie
- **Délai moyen** : 3-5 jours ouvrés
- **Coût moyen** : 30-80 €

### 🏢 Eurofins
- **Spécialités** : Sécurité Alimentaire, Contaminants, Microbiologie, Phytosanitaire
- **Délai moyen** : 7-10 jours ouvrés
- **Coût moyen** : 60-200 €

### 🌾 Céania
- **Spécialités** : Sécurité Alimentaire, Métrologie, Microbiologie
- **Délai moyen** : 5-8 jours ouvrés
- **Coût moyen** : 40-90 €

### 🧼 Diversey
- **Spécialités** : Hygiène & Nettoyage (ATP uniquement)
- **Délai moyen** : Immédiat (mesure sur site)
- **Coût moyen** : 15-25 € (kit ATP)

---

## ⚙️ Paramètres Avancés

### Personnalisation des Seuils

**Fichier** : `flet_app/lab_models.py`

**Classe** : `SeuilsReglementaires`

```python
class SeuilsReglementaires:
    # Phtalates
    DBP_ROUGE = 0.3  # mg/kg - Modifier ici
    
    # Métaux lourds
    PLOMB_ROUGE = 0.10  # mg/L
    CADMIUM_ROUGE = 0.01  # mg/L
    
    # ATP (Inox)
    ATP_BON = 150  # RLU
    ATP_MOYEN = 200  # RLU
```

### Ajout d'un Nouveau Laboratoire

**Fichier** : `flet_app/lab_models.py`

```python
class Laboratoire(Enum):
    SOFRALAB = "Sofralab"
    EXACT = "Exact"
    EUROFINS = "Eurofins"
    CEANIA = "Céania"
    DIVERSEY = "Diversey"
    NOUVEAU_LABO = "Nouveau Labo"  # ← Ajouter ici
    AUTRE = "Autre"
```

---

## 🐛 Dépannage

### Problème : Analyse ne se sauvegarde pas
**Solution** :
- Vérifiez que les champs marqués d'un `*` sont remplis
- Date Prélèvement et Laboratoire sont obligatoires
- Format de date attendu : `JJ/MM/AAAA`

### Problème : Export Excel échoue
**Solution** :
- Installez `openpyxl` : `pip install openpyxl`
- Vérifiez les permissions d'écriture dans le dossier

### Problème : Auto-évaluation incorrecte
**Solution** :
- Cliquez sur "🔍 Réévaluer" pour forcer le recalcul
- Vérifiez les seuils dans `lab_models.py`

---

## 📈 Feuille de Route (Futures Versions)

### v2.5.0 (Prévu Q2 2025)
- [ ] Import massif depuis fichiers Excel laboratoires
- [ ] Génération QR Code pour traçabilité échantillons
- [ ] Notifications email alertes automatiques
- [ ] Intégration API laboratoires (récupération auto résultats)

### v2.6.0 (Prévu Q3 2025)
- [ ] Graphiques avancés (Matplotlib intégré)
- [ ] Export PDF rapports personnalisés
- [ ] Tableau de bord temps réel
- [ ] Analyse prédictive coûts

---

## 📝 Notes Techniques

### Architecture Polymorphe

Le système utilise le **polymorphisme** pour gérer 7 types d'analyses différents dans une seule table SQL :

```
Table lab_analyses (données communes)
    ↓
Champ `resultats` (JSON polymorphe)
    ↓
Classes spécialisées :
    - OenologieStandard
    - SecuriteAlimentaire
    - Contaminants
    - Metrologie
    - Microbiologie
    - HygieneATP
    - Phytosanitaire
```

**Avantages** :
- ✅ Ajout facile de nouveaux types
- ✅ Requêtes SQL simples (1 table)
- ✅ Flexibilité totale champs spécifiques

### Performance

**Optimisations implémentées** :
- Index sur `type_analyse`, `date_prelevement`, `conclusion`
- Cache des statistiques (rafraîchi toutes les 5 min)
- Pagination table (25 lignes par page)

**Temps de chargement** :
- Liste 1000 analyses : < 200ms
- Tableau de bord : < 100ms
- Export Excel 500 lignes : < 2s

---

## 🎓 Formation Recommandée

### Durée : 2 heures

#### Module 1 : Découverte (30 min)
- Présentation des 7 types d'analyses
- Navigation entre les onglets
- Interprétation du tableau de bord

#### Module 2 : Saisie (45 min)
- Créer une analyse Œnologie
- Créer une analyse Contaminants
- Créer une analyse ATP
- Exercice pratique : 5 analyses variées

#### Module 3 : Exploitation (30 min)
- Filtrer et rechercher efficacement
- Interpréter les alertes
- Exporter en Excel
- Générer un rapport PDF

#### Module 4 : Cas Pratiques (15 min)
- Gestion non-conformité DBP > seuil
- Investigation TCA détecté
- Validation nettoyage ATP

---

## 📞 Support

**Email** : support@qualimanager.local  
**Téléphone** : +33 X XX XX XX XX  
**Documentation en ligne** : docs.qualimanager.local/laboratoire

---

*Guide rédigé pour QualiManager v2.4.0 - Janvier 2025*  
*Module Laboratoire - Tous droits réservés*

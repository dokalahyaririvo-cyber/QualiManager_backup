# 🔍 Audit de Performance - Onglet Statistiques

## 📊 Problème Identifié
**Temps de chargement: ~10 secondes** pour afficher l'onglet Statistiques

## 🐛 Causes Identifiées

### 1. Génération Synchrone de Multiples Graphiques
```python
# Dans _build_statistics_tab():
evolution_mensuelle = self._build_evolution_mensuelle_par_type(all_ncs)  # 1-2s
comparateur_annuel = self._build_comparateur_annuel(all_ncs)  # 1-2s
repartitions = self._build_repartitions_zone_b(all_ncs)  # 3-5s (5 graphiques)
```
**Impact**: 6-9 secondes pour générer tous les graphiques matplotlib

### 2. Zone B Génère 10 Graphiques d'un Coup
```python
# Pour chaque répartition (imputation, anomalie, catégorie, gravité, matières):
- 1 graphique de répartition (camembert)
- 1 graphique Pareto
= 5 × 2 = 10 graphiques générés immédiatement
```
**Impact**: 3-5 secondes supplémentaires

### 3. Pas de Lazy Loading
- Tous les graphiques sont générés même si non visibles à l'écran
- L'utilisateur doit scroller pour voir les graphiques du bas
- Génération anticipée = temps perdu

### 4. Cache Inefficace
```python
# Le cache est vidé trop souvent:
if hasattr(self, '_chart_cache'):
    self._chart_cache.clear()  # Vidé à chaque ouverture
```

### 5. Traitement des Données Non Optimisé
```python
all_ncs = self.db.get_all_nc()  # Récupère TOUTES les NC (pas de pagination)
# Puis filtrage en Python pour chaque graphique
```

## 💡 Solutions Proposées

### ✅ Solution 1: Lazy Loading des Graphiques (PRIORITAIRE)
**Impact estimé: -6 à -7 secondes**

**Implémentation:**
```python
# Afficher des placeholders au lieu des graphiques
# Générer les graphiques uniquement quand ils deviennent visibles (scroll)
# Utiliser IntersectionObserver ou générer au clic sur un ExpansionPanel
```

**Avantages:**
- Temps de chargement initial réduit de 10s à 3s
- Meilleure expérience utilisateur
- Graphiques générés à la demande

### ✅ Solution 2: Graphiques en Arrière-Plan (Threading)
**Impact estimé: -4 à -5 secondes**

**Implémentation:**
```python
import threading

def _build_statistics_tab_async(self):
    # Afficher des spinners/loaders
    # Générer les graphiques en threads séparés
    # Mettre à jour progressivement l'interface
```

**Avantages:**
- Interface réactive immédiatement
- Graphiques apparaissent progressivement
- Pas de blocage de l'UI

### ✅ Solution 3: Cache Persistant et Intelligent
**Impact estimé: -8 à -9 secondes (après 1er chargement)**

**Implémentation:**
```python
# Ne vider le cache que lors d'ajout/modification/suppression de NC
# Ajouter un timestamp pour invalidation automatique (ex: 5 minutes)
# Réutiliser les graphiques tant que les données n'ont pas changé
```

**Avantages:**
- Chargements suivants quasi-instantanés (< 1s)
- Pas de regénération inutile
- Meilleure utilisation mémoire

### ✅ Solution 4: Optimisation des Requêtes DB
**Impact estimé: -1 à -2 secondes**

**Implémentation:**
```python
# Au lieu de:
all_ncs = self.db.get_all_nc()

# Utiliser:
all_ncs = self.db.get_all_nc_light()  # Seulement les champs nécessaires
# Ou ajouter un index sur les champs fréquents (date_detection, imputation, etc.)
```

### ✅ Solution 5: Réduction de la Résolution des Graphiques
**Impact estimé: -0.5 à -1 seconde**

**Implémentation:**
```python
# Au lieu de dpi=100:
fig.savefig(buf, format='png', dpi=72, bbox_inches='tight')  # Résolution web standard
```

### ✅ Solution 6: Compression des Images
**Impact estimé: -0.3 à -0.5 seconde**

**Implémentation:**
```python
from PIL import Image

# Compresser les images PNG avant base64
img = Image.open(buf)
img.save(buf_compressed, format='PNG', optimize=True, compress_level=6)
```

### ✅ Solution 7: ExpansionPanels pour Zone B
**Impact estimé: -3 à -4 secondes**

**Implémentation:**
```python
# Au lieu d'afficher tous les graphiques:
# Mettre chaque répartition dans un ExpansionPanel fermé par défaut
# Générer le graphique uniquement à l'ouverture du panel
```

**Avantages:**
- Organisation plus claire
- Génération à la demande
- Moins de scrolling

## 🎯 Plan d'Action Recommandé

### Phase 1: Amélioration Immédiate (30 minutes)
1. **Lazy Loading Zone B** avec ExpansionPanels
2. **Cache persistant** (ne vider que si modif NC)
3. **DPI réduit** à 72 pour affichage web

**Résultat attendu: 10s → 3-4s**

### Phase 2: Optimisation Avancée (1-2 heures)
1. **Threading** pour génération asynchrone
2. **Optimisation requêtes DB**
3. **Compression images**

**Résultat attendu: 3-4s → 1-2s**

### Phase 3: Amélioration UX (30 minutes)
1. **Loaders/spinners** pour feedback visuel
2. **Barre de progression** pour génération graphiques
3. **Bouton "Actualiser"** manuel optionnel

**Résultat attendu: UX fluide, perception < 1s**

## 📈 Métriques de Succès
- ✅ Temps chargement initial < 3s
- ✅ Temps chargement avec cache < 1s
- ✅ Interface réactive (pas de freeze)
- ✅ Feedback visuel immédiat

## 🔧 Autres Pistes d'Amélioration

### A. Pagination des Données
- Limiter à 1000 NC max pour les graphiques
- Option "Tout afficher" si nécessaire

### B. WebWorkers (Flet PWA)
- Si déployé en web, utiliser WebWorkers
- Génération graphiques côté client

### C. Graphiques Interactifs Légers
- Remplacer matplotlib par Plotly (plus léger en web)
- Ou utiliser Chart.js via JavaScript

### D. Préchargement Intelligent
- Précharger uniquement si l'utilisateur accède souvent aux stats
- Analyser les patterns d'utilisation

### E. Mode "Aperçu Rapide"
- Version simplifiée des graphiques (moins de détails)
- Bouton "Vue détaillée" pour graphiques complets

## 📊 Comparaison des Solutions

| Solution | Impact | Complexité | Temps Implémentation |
|----------|--------|------------|---------------------|
| Lazy Loading Zone B | ⭐⭐⭐⭐⭐ | Faible | 30 min |
| Cache Persistant | ⭐⭐⭐⭐⭐ | Faible | 15 min |
| DPI Réduit | ⭐⭐ | Très faible | 5 min |
| Threading | ⭐⭐⭐⭐ | Moyenne | 1-2h |
| ExpansionPanels | ⭐⭐⭐⭐ | Faible | 30 min |
| Optimisation DB | ⭐⭐⭐ | Moyenne | 1h |
| Compression | ⭐⭐ | Faible | 20 min |

## 🚀 Recommandation Finale

**Commencer par les "Quick Wins":**
1. ExpansionPanels + Lazy Loading (30 min)
2. Cache persistant (15 min)
3. DPI réduit (5 min)

**Total: 50 minutes d'implémentation pour passer de 10s à 2-3s**

Ensuite, si nécessaire, ajouter le threading pour descendre à < 1s.

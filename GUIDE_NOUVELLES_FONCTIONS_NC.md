# 🚀 Guide d'Utilisation Rapide - Nouvelles Fonctionnalités Liste NC

## 📋 Actions Rapides par Ligne

### Comment utiliser
Dans le tableau "Liste NC", chaque ligne possède maintenant **3 boutons d'action** dans la dernière colonne :

| Bouton | Icône | Couleur | Action |
|--------|-------|---------|--------|
| **Voir** | 👁️ | Bleu info | Consulter la NC en lecture seule |
| **Éditer** | ✏️ | Bleu primaire | Modifier la NC |
| **Dupliquer** | 📋 | Vert | Créer une copie pour nouvelle NC |

### Astuce : Duplication rapide
1. Cliquez sur 📋 (Dupliquer)
2. Le formulaire s'ouvre pré-rempli avec :
   - ✅ Toutes les données copiées
   - 🔄 Statut réinitialisé à "En cours"
   - 📅 Date mise à aujourd'hui
   - 📝 "[COPIE]" ajouté au début de la description
3. Modifiez ce qui est nécessaire
4. Cliquez sur "Enregistrer"
5. ✅ Une nouvelle NC est créée avec une nouvelle référence

---

## 🔍 Recherche Instantanée Améliorée

### Nouvelles fonctionnalités

#### 1. Compteur de résultats
- **Toujours visible** dans le coin droit du champ de recherche
- Affiche : `X NC` (nombre de résultats)
- Couleur :
  - 🔵 Bleu vif si recherche active
  - ⚪ Gris si pas de recherche

#### 2. Bouton effacer
- Icône ❌ visible uniquement si vous avez tapé du texte
- **Un seul clic** pour effacer toute la recherche
- Retour instantané à la liste complète

### Mode d'emploi
```
1. Tapez n'importe quel mot dans le champ de recherche
   → Le compteur se met à jour en temps réel

2. Observez le nombre de résultats : "42 NC"
   
3. Pour tout effacer :
   → Cliquez sur ❌
   → Ou supprimez manuellement le texte
```

---

## 📊 Export de Données

### 3 formats disponibles

#### 📗 Excel (.xlsx) - Bouton VERT
**Quand l'utiliser ?**
- Analyse de données
- Tableaux croisés dynamiques
- Graphiques
- Partage avec équipe

**Avantages :**
- ✅ Colonnes ajustées automatiquement
- ✅ En-têtes stylisés (fond bleu)
- ✅ Facile à manipuler

**Clic sur bouton Excel** → Fichier dans `Téléchargements`

---

#### 📕 PDF (.pdf) - Bouton ROUGE
**Quand l'utiliser ?**
- Impression
- Archivage
- Envoi par email officiel
- Rapport figé dans le temps

**Avantages :**
- ✅ Format universel
- ✅ Mise en page professionnelle
- ✅ Ne peut pas être modifié facilement

**Clic sur bouton PDF** → Document prêt à imprimer

---

#### 📘 CSV (.csv) - Bouton BLEU
**Quand l'utiliser ?**
- Import dans autre logiciel
- Compatibilité maximale
- Traitement par script
- Base de données

**Avantages :**
- ✅ Format texte simple
- ✅ Ouvre dans n'importe quel tableur
- ✅ Pas de mise en forme (données brutes)

**Clic sur bouton CSV** → Fichier texte structuré

---

## 🎯 Workflows Typiques

### Workflow 1 : Export pour réunion qualité
```
1. Appliquer filtres :
   - Statut : "En cours"
   - Gravité : "Majeure"
   - Date : Dernier mois

2. Vérifier compteur : "15 NC"

3. Cliquer sur 📕 PDF

4. Ouvrir le fichier dans Downloads

5. Imprimer ou joindre à l'email
```

### Workflow 2 : Créer NC similaire
```
1. Trouver la NC de référence dans la liste

2. Cliquer sur 📋 Dupliquer

3. Le formulaire s'ouvre pré-rempli

4. Modifier :
   - Date de détection
   - Description (enlever [COPIE] si besoin)
   - Produit concerné

5. Enregistrer → Nouvelle référence générée
```

### Workflow 3 : Analyse Excel
```
1. Pas de filtre (toutes les NC)

2. Vérifier compteur : "247 NC"

3. Cliquer sur 📗 Excel

4. Ouvrir le fichier .xlsx

5. Créer tableaux croisés dynamiques

6. Analyser par origine, gravité, etc.
```

---

## ⚙️ Paramètres & Localisation

### Où sont enregistrés les exports ?
```
Windows : C:\Users\[VotreNom]\Downloads\
Nom : export_nc_20250121_143052.xlsx
      └─ Format : YYYYMMDD_HHMMSS
```

### Combien de temps ça prend ?
| Format | Vitesse | 100 NC | 1000 NC |
|--------|---------|--------|---------|
| CSV | ⚡ Très rapide | < 1s | 1-2s |
| Excel | 🚀 Rapide | 1s | 2-3s |
| PDF | 🐢 Moyen | 2s | 5-10s |

---

## ❓ FAQ

### Q : Que se passe-t-il si je duplique une NC clôturée ?
**R :** La copie aura automatiquement le statut "En cours", même si l'originale est clôturée.

### Q : Le compteur de résultats inclut-il les filtres ?
**R :** Oui ! Le compteur affiche le nombre de NC **après application de tous les filtres**.

### Q : Puis-je exporter seulement certaines NC ?
**R :** Oui, utilisez les filtres (statut, gravité, dates, etc.), puis exportez. Seules les NC affichées seront exportées.

### Q : Le bouton "Voir" permet-il vraiment de bloquer les modifications ?
**R :** Pour l'instant, c'est un placeholder. La fonctionnalité de lecture seule pure sera implémentée ultérieurement.

### Q : Les exports sont-ils horodatés ?
**R :** Oui, le nom du fichier contient toujours la date et l'heure : `export_nc_20250121_143052.xlsx`

### Q : Que faire si Excel ou PDF ne fonctionnent pas ?
**R :** Utilisez le bouton CSV qui fonctionne toujours (pas de dépendance externe).

---

## 🆘 Dépannage

### Problème : "Bibliothèque openpyxl non disponible"
**Solution :**
```powershell
pip install openpyxl
```

### Problème : "Bibliothèque reportlab non disponible"
**Solution :**
```powershell
pip install reportlab
```

### Problème : Le compteur affiche "0 NC" alors que j'ai des résultats
**Solution :**
- Vérifiez vos filtres
- Cliquez sur "Tous" pour réinitialiser
- Effacez la recherche avec ❌

### Problème : Fichier export introuvable
**Solution :**
- Ouvrez l'explorateur Windows
- Allez dans `Ce PC > Téléchargements`
- Triez par date (le plus récent en premier)

---

## 📞 Support

Si vous rencontrez un problème non listé ici :
1. Vérifiez la console pour messages d'erreur
2. Consultez AMELIORATIONS_LISTE_NC.md pour détails techniques
3. Contactez l'équipe de développement

---

**Version** : QualiManager ERP QHSE v2.0  
**Dernière mise à jour** : Janvier 2025

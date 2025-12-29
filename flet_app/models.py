# -*- coding: utf-8 -*-
"""
QualiManager ERP QHSE - Modèles de données SQLAlchemy
Architecture complète pour industrie agroalimentaire (IFS, BRC, ISO 22000)
"""

import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
import json


# ============================================================================
# SCHEMA SQL - Toutes les tables du système ERP QHSE
# ============================================================================

SCHEMA_SQL = """
-- ============================================================================
-- VERSIONING & MIGRATIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS app_version (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    version TEXT NOT NULL,
    last_migration TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- ============================================================================
-- UTILISATEURS & AUTHENTIFICATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    password_plain TEXT,
    role TEXT NOT NULL DEFAULT 'Utilisateur',
    service TEXT,
    taux_horaire REAL DEFAULT 35.0,
    actif INTEGER DEFAULT 1,
    preferences TEXT,  -- JSON: thème, favoris KPI, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- ============================================================================
-- MODULE 1: NON-CONFORMITÉS (NC) - CORE
-- ============================================================================

-- Table principale NC
CREATE TABLE IF NOT EXISTS nc_header (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT UNIQUE NOT NULL,
    date_detection DATE NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    detecteur_id INTEGER,
    type_nc TEXT NOT NULL,  -- Interne, Client, Fournisseur, Prestataire, Audit
    origine TEXT,
    gravite TEXT NOT NULL DEFAULT 'Mineure',  -- Mineure, Majeure, Critique
    statut TEXT DEFAULT 'Ouverte',
    
    -- Description
    description TEXT,
    produit_concerne TEXT,
    lot_serie TEXT,
    quantite_affectee INTEGER DEFAULT 0,
    lieu_detection TEXT,
    type_anomalie TEXT,
    categorie_nc TEXT,
    imputation TEXT,
    pieces_jointes TEXT,  -- JSON array de chemins
    
    -- Analyse
    causes_immediates TEXT,
    cause_racine TEXT,
    methode_analyse TEXT,  -- 5Pourquoi, Ishikawa, AMDEC, 8D
    analyse_5m TEXT,  -- JSON: {"Matière": [], "Méthode": [], ...}
    analyse_data TEXT,  -- JSON données analyse détaillée
    analyse_details TEXT,  -- JSON détails 5why/ishikawa
    analyse_portee TEXT,
    
    -- Actions (JSON tables)
    actions_immediates_table TEXT,  -- JSON array des actions immédiates
    actions_correctives_table TEXT, -- JSON array des actions correctives
    
    -- Coûts de Non-Qualité (CNQ)
    cout_matiere REAL DEFAULT 0,
    cout_mo_heures REAL DEFAULT 0,
    cout_mo_taux REAL DEFAULT 35.0,
    cout_destruction REAL DEFAULT 0,
    cout_autres REAL DEFAULT 0,
    cout_total REAL DEFAULT 0,
    
    -- Responsabilité & Échéances
    responsable_id INTEGER,
    date_echeance DATE,
    
    -- Clôture
    date_cloture DATE,
    verificateur_id INTEGER,
    efficacite TEXT,
    commentaires_cloture TEXT,
    
    FOREIGN KEY (detecteur_id) REFERENCES users(id),
    FOREIGN KEY (responsable_id) REFERENCES users(id),
    FOREIGN KEY (verificateur_id) REFERENCES users(id)
);

-- Actions immédiates NC
CREATE TABLE IF NOT EXISTS nc_actions_immediates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nc_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    responsable_id INTEGER,
    date_prevue DATE,
    date_realisation DATE,
    statut TEXT DEFAULT 'En attente',
    commentaires TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nc_id) REFERENCES nc_header(id) ON DELETE CASCADE,
    FOREIGN KEY (responsable_id) REFERENCES users(id)
);

-- Actions correctives NC
CREATE TABLE IF NOT EXISTS nc_actions_correctives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nc_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    responsable_id INTEGER,
    date_prevue DATE,
    date_realisation DATE,
    statut TEXT DEFAULT 'En attente',
    efficacite TEXT,
    verification TEXT,
    commentaires TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nc_id) REFERENCES nc_header(id) ON DELETE CASCADE,
    FOREIGN KEY (responsable_id) REFERENCES users(id)
);

-- Actions préventives NC
CREATE TABLE IF NOT EXISTS nc_actions_preventives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nc_id INTEGER,
    description TEXT NOT NULL,
    responsable_id INTEGER,
    date_prevue DATE,
    date_realisation DATE,
    statut TEXT DEFAULT 'En attente',
    commentaires TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nc_id) REFERENCES nc_header(id) ON DELETE SET NULL,
    FOREIGN KEY (responsable_id) REFERENCES users(id)
);

-- Historique des modifications NC
CREATE TABLE IF NOT EXISTS nc_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nc_id INTEGER NOT NULL,
    user_name TEXT NOT NULL,
    action TEXT NOT NULL,               -- 'creation', 'modification', 'cloture', 'suppression'
    field_changed TEXT,                 -- Nom du champ modifié (NULL pour création/suppression)
    old_value TEXT,                     -- Ancienne valeur
    new_value TEXT,                     -- Nouvelle valeur
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nc_id) REFERENCES nc_header(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_history_nc_id ON nc_history(nc_id);
CREATE INDEX IF NOT EXISTS idx_history_timestamp ON nc_history(timestamp);

-- Préférences utilisateur (filtres, vues, etc.)
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    module TEXT NOT NULL,               -- 'nc', 'veille', 'inspections', etc.
    preference_key TEXT NOT NULL,       -- 'filters', 'view_mode', 'columns', etc.
    preference_value TEXT NOT NULL,     -- JSON avec les valeurs
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, module, preference_key),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_prefs ON user_preferences(user_id, module);

-- ============================================================================
-- MODULE 2: VEILLE RÉGLEMENTAIRE & RACI
-- ============================================================================

-- Items de veille
CREATE TABLE IF NOT EXISTS veille_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT UNIQUE NOT NULL,
    type_veille TEXT NOT NULL,  -- Réglementaire, Normative, Client, Interne
    source TEXT,  -- Journal Officiel, Client X, Norme ISO...
    date_publication DATE,
    date_application DATE,
    titre TEXT NOT NULL,
    description TEXT,
    tags TEXT,  -- JSON array: ["Étiquetage", "Allergènes"]
    pieces_jointes TEXT,  -- JSON array
    impact_systeme INTEGER DEFAULT 0,  -- 0=Non, 1=Oui
    statut TEXT DEFAULT 'À analyser',  -- À analyser, En cours, Traité, Non applicable
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Matrice RACI pour plans d'action
CREATE TABLE IF NOT EXISTS raci_matrix (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    veille_id INTEGER NOT NULL,
    titre_action TEXT NOT NULL,
    description TEXT,
    responsible_id INTEGER,  -- R: Réalise
    accountable_id INTEGER,  -- A: Approuve
    consulted_ids TEXT,  -- C: JSON array d'IDs consultés
    informed_ids TEXT,  -- I: JSON array d'IDs informés
    progression INTEGER DEFAULT 0,  -- 0-100%
    date_debut DATE,
    date_butoir DATE,
    date_realisation DATE,
    statut TEXT DEFAULT 'Non démarré',
    priorite TEXT DEFAULT 'Normale',  -- Basse, Normale, Haute, Critique
    commentaires TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (veille_id) REFERENCES veille_items(id) ON DELETE CASCADE,
    FOREIGN KEY (responsible_id) REFERENCES users(id),
    FOREIGN KEY (accountable_id) REFERENCES users(id)
);

-- ============================================================================
-- MODULE 3: INSPECTIONS & AUDITS
-- ============================================================================

-- Ateliers / Zones de production
CREATE TABLE IF NOT EXISTS ateliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    nom TEXT NOT NULL,
    description TEXT,
    responsable_id INTEGER,
    actif INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (responsable_id) REFERENCES users(id)
);

-- Zones dans les ateliers
CREATE TABLE IF NOT EXISTS zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    atelier_id INTEGER NOT NULL,
    code TEXT NOT NULL,
    nom TEXT NOT NULL,
    description TEXT,
    actif INTEGER DEFAULT 1,
    FOREIGN KEY (atelier_id) REFERENCES ateliers(id) ON DELETE CASCADE
);

-- Points de contrôle (template)
CREATE TABLE IF NOT EXISTS points_controle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_id INTEGER NOT NULL,
    code TEXT NOT NULL,
    libelle TEXT NOT NULL,
    description TEXT,
    categorie TEXT,  -- Hygiène, Sécurité, Qualité, Environnement
    frequence TEXT,  -- Quotidien, Hebdomadaire, Mensuel
    criticite TEXT DEFAULT 'Standard',  -- Standard, Important, Critique
    ordre_affichage INTEGER DEFAULT 0,
    actif INTEGER DEFAULT 1,
    FOREIGN KEY (zone_id) REFERENCES zones(id) ON DELETE CASCADE
);

-- En-tête inspection
CREATE TABLE IF NOT EXISTS inspection_header (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT UNIQUE NOT NULL,
    atelier_id INTEGER NOT NULL,
    date_inspection DATE NOT NULL,
    heure_debut TIME,
    heure_fin TIME,
    inspecteur_id INTEGER NOT NULL,
    type_inspection TEXT DEFAULT 'Routine',  -- Routine, Inopinée, Audit
    score_total REAL,
    score_max REAL,
    pourcentage REAL,
    statut TEXT DEFAULT 'En cours',  -- En cours, Terminée, Validée
    observations_generales TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (atelier_id) REFERENCES ateliers(id),
    FOREIGN KEY (inspecteur_id) REFERENCES users(id)
);

-- Détail inspection (résultats par point)
CREATE TABLE IF NOT EXISTS inspection_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inspection_id INTEGER NOT NULL,
    point_controle_id INTEGER NOT NULL,
    resultat TEXT NOT NULL,  -- Conforme, Non conforme, NA
    description_ecart TEXT,
    photo_path TEXT,
    action_immediate TEXT,
    nc_generee_id INTEGER,
    commentaires TEXT,
    FOREIGN KEY (inspection_id) REFERENCES inspection_header(id) ON DELETE CASCADE,
    FOREIGN KEY (point_controle_id) REFERENCES points_controle(id),
    FOREIGN KEY (nc_generee_id) REFERENCES nc_header(id)
);

-- ============================================================================
-- MODULE 4: LABORATOIRE / MINI-LIMS
-- ============================================================================

-- Produits analysés
CREATE TABLE IF NOT EXISTS lab_produits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    nom TEXT NOT NULL,
    categorie TEXT,
    description TEXT,
    actif INTEGER DEFAULT 1
);

-- Paramètres d'analyse avec bornes
CREATE TABLE IF NOT EXISTS lab_parametres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    nom TEXT NOT NULL,
    unite TEXT,
    methode TEXT,
    valeur_min REAL,
    valeur_max REAL,
    valeur_cible REAL,
    categorie TEXT,  -- Physico-chimique, Microbiologique, Organoleptique
    actif INTEGER DEFAULT 1
);

-- Bornes spécifiques par produit
CREATE TABLE IF NOT EXISTS lab_bornes_produit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produit_id INTEGER NOT NULL,
    parametre_id INTEGER NOT NULL,
    valeur_min REAL,
    valeur_max REAL,
    valeur_cible REAL,
    FOREIGN KEY (produit_id) REFERENCES lab_produits(id) ON DELETE CASCADE,
    FOREIGN KEY (parametre_id) REFERENCES lab_parametres(id) ON DELETE CASCADE,
    UNIQUE(produit_id, parametre_id)
);

-- En-tête analyse labo
CREATE TABLE IF NOT EXISTS lab_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT UNIQUE NOT NULL,
    produit_id INTEGER NOT NULL,
    lot_numero TEXT NOT NULL,
    date_prelevement DATE NOT NULL,
    date_analyse DATE,
    analyste_id INTEGER,
    statut TEXT DEFAULT 'En cours',  -- En cours, Terminée, Validée, Bloquée
    conforme INTEGER,  -- 0=Non conforme, 1=Conforme, NULL=En attente
    observations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (produit_id) REFERENCES lab_produits(id),
    FOREIGN KEY (analyste_id) REFERENCES users(id)
);

-- Résultats d'analyse
CREATE TABLE IF NOT EXISTS lab_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    parametre_id INTEGER NOT NULL,
    valeur REAL,
    valeur_texte TEXT,  -- Pour résultats qualitatifs
    conforme INTEGER,  -- 0=Non, 1=Oui
    commentaires TEXT,
    FOREIGN KEY (analysis_id) REFERENCES lab_analysis(id) ON DELETE CASCADE,
    FOREIGN KEY (parametre_id) REFERENCES lab_parametres(id)
);

-- ============================================================================
-- MODULE 5: KPI & DATA INTELLIGENCE
-- ============================================================================

-- Dashboards personnalisés
CREATE TABLE IF NOT EXISTS kpi_dashboards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    nom TEXT NOT NULL,
    description TEXT,
    layout TEXT,  -- JSON: configuration du layout
    widgets TEXT,  -- JSON: liste des widgets épinglés
    is_default INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Coûts qualité (historique)
CREATE TABLE IF NOT EXISTS couts_qualite (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    annee INTEGER NOT NULL,
    mois INTEGER NOT NULL,
    cout_nc REAL DEFAULT 0,
    cout_analyses REAL DEFAULT 0,
    cout_audits REAL DEFAULT 0,
    cout_prevention REAL DEFAULT 0,
    cout_total REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(annee, mois)
);

-- ============================================================================
-- TRAÇABILITÉ & TIMELINE
-- ============================================================================

-- Événements lot (pour timeline)
CREATE TABLE IF NOT EXISTS lot_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_numero TEXT NOT NULL,
    type_event TEXT NOT NULL,  -- Production, Analyse, Inspection, NC, Action, Liberation
    date_event TIMESTAMP NOT NULL,
    titre TEXT NOT NULL,
    description TEXT,
    reference_table TEXT,  -- nc_header, lab_analysis, inspection_header
    reference_id INTEGER,
    statut TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Historique / Audit trail
CREATE TABLE IF NOT EXISTS historique (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id INTEGER NOT NULL,
    action TEXT NOT NULL,  -- CREATE, UPDATE, DELETE
    old_value TEXT,  -- JSON
    new_value TEXT,  -- JSON
    user_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ============================================================================
-- INDEXES POUR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_nc_statut ON nc_header(statut);
CREATE INDEX IF NOT EXISTS idx_nc_lot ON nc_header(lot_serie);
CREATE INDEX IF NOT EXISTS idx_nc_date ON nc_header(date_detection);
CREATE INDEX IF NOT EXISTS idx_nc_gravite ON nc_header(gravite);
CREATE INDEX IF NOT EXISTS idx_nc_type ON nc_header(type_nc);
CREATE INDEX IF NOT EXISTS idx_nc_origine ON nc_header(origine);
CREATE INDEX IF NOT EXISTS idx_nc_imputation ON nc_header(imputation);
CREATE INDEX IF NOT EXISTS idx_nc_categorie ON nc_header(categorie_nc);
CREATE INDEX IF NOT EXISTS idx_nc_date_creation ON nc_header(date_creation);
CREATE INDEX IF NOT EXISTS idx_veille_statut ON veille_items(statut);
CREATE INDEX IF NOT EXISTS idx_raci_date ON raci_matrix(date_butoir);
CREATE INDEX IF NOT EXISTS idx_inspection_date ON inspection_header(date_inspection);
CREATE INDEX IF NOT EXISTS idx_lab_lot ON lab_analysis(lot_numero);
CREATE INDEX IF NOT EXISTS idx_lot_events ON lot_events(lot_numero, date_event);
"""

# ============================================================================
# DONNÉES INITIALES
# ============================================================================

INITIAL_DATA_SQL = """
-- Ateliers par défaut (exemple cave viticole)
INSERT OR IGNORE INTO ateliers (code, nom, description) VALUES
('TIR', 'Tirage', 'Zone de mise en bouteille'),
('DEG', 'Dégorgement', 'Zone de dégorgement'),
('HAB', 'Habillage', 'Zone d''habillage et conditionnement'),
('CUV', 'Cuverie', 'Zone de vinification'),
('CAV', 'Caves', 'Stockage et vieillissement'),
('EXP', 'Expédition', 'Préparation commandes et expédition'),
('LAB', 'Laboratoire', 'Analyses et contrôles');

-- Zones exemple pour Tirage
INSERT OR IGNORE INTO zones (atelier_id, code, nom) VALUES
(1, 'TIR-L1', 'Ligne 1'),
(1, 'TIR-L2', 'Ligne 2'),
(1, 'TIR-STO', 'Zone stockage');

-- Points de contrôle exemple
INSERT OR IGNORE INTO points_controle (zone_id, code, libelle, categorie, criticite) VALUES
(1, 'TIR-L1-01', 'Propreté des surfaces', 'Hygiène', 'Important'),
(1, 'TIR-L1-02', 'État des équipements', 'Sécurité', 'Standard'),
(1, 'TIR-L1-03', 'Température ambiante', 'Qualité', 'Important'),
(1, 'TIR-L1-04', 'Conformité étiquetage', 'Qualité', 'Critique'),
(1, 'TIR-L1-05', 'Rangement zone', 'Hygiène', 'Standard');

-- Paramètres labo par défaut
INSERT OR IGNORE INTO lab_parametres (code, nom, unite, valeur_min, valeur_max, valeur_cible, categorie) VALUES
('PH', 'pH', '', 2.9, 3.5, 3.2, 'Physico-chimique'),
('TAV', 'Titre Alcoométrique', '% vol', 10.5, 13.5, 12.0, 'Physico-chimique'),
('AT', 'Acidité Totale', 'g/L H2SO4', 4.0, 7.0, 5.5, 'Physico-chimique'),
('SO2L', 'SO2 Libre', 'mg/L', 10, 50, 30, 'Physico-chimique'),
('SO2T', 'SO2 Total', 'mg/L', 50, 200, 120, 'Physico-chimique'),
('BRIX', 'Brix', 'oBx', 0, 5, 1, 'Physico-chimique'),
('TURB', 'Turbidité', 'NTU', 0, 2, 0.5, 'Physico-chimique');

-- Produits exemple
INSERT OR IGNORE INTO lab_produits (code, nom, categorie) VALUES
('BRUT', 'Brut Tradition', 'Champagne'),
('ROSE', 'Rosé', 'Champagne'),
('PREST', 'Cuvée Prestige', 'Champagne'),
('BLANC', 'Blanc de Blancs', 'Champagne');
"""


def init_database(db_path: str = "qualimanager.db") -> None:
    """Initialise la base de données avec le schéma complet."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Exécuter le schéma
    cursor.executescript(SCHEMA_SQL)
    
    # Migration: copier données de l'ancienne table si elle existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='non_conformites'")
    if cursor.fetchone():
        # Migrer les NC existantes vers nc_header
        cursor.execute("""
            INSERT OR IGNORE INTO nc_header (
                id, reference, date_detection, date_creation, detecteur_id, type_nc,
                origine, gravite, statut, description, produit_concerne, lot_serie,
                quantite_affectee, lieu_detection, type_anomalie, categorie_nc,
                imputation, pieces_jointes, causes_immediates, cause_racine,
                methode_analyse, analyse_5m, responsable_id, date_echeance,
                date_cloture, verificateur_id, efficacite, commentaires_cloture
            )
            SELECT 
                id, reference, date_detection, date_creation, detecteur_id, type_nc,
                origine, gravite, statut, description, produit_concerne, lot_serie,
                quantite_affectee, lieu_detection, type_anomalie, categorie_nc,
                imputation, pieces_jointes, causes_immediates, cause_racine,
                methode_analyse, analyse_5m, responsable_id, date_echeance,
                date_cloture, verificateur_id, efficacite, commentaires_cloture
            FROM non_conformites
            WHERE NOT EXISTS (SELECT 1 FROM nc_header WHERE nc_header.reference = non_conformites.reference)
        """)
    
    # Insérer données initiales
    cursor.executescript(INITIAL_DATA_SQL)
    
    conn.commit()
    conn.close()


# ============================================================================
# HELPER CLASSES POUR MANIPULATION DES DONNÉES
# ============================================================================

class NCModel:
    """Modèle pour les Non-Conformités."""
    
    @staticmethod
    def calculate_cost(cout_matiere: float, quantite: int, heures_mo: float, 
                       taux_horaire: float, cout_destruction: float, cout_autres: float = 0) -> float:
        """Calcule le coût total de la NC."""
        # Gérer les valeurs None
        cout_matiere = cout_matiere or 0
        quantite = quantite or 0
        heures_mo = heures_mo or 0
        taux_horaire = taux_horaire or 0
        cout_destruction = cout_destruction or 0
        cout_autres = cout_autres or 0
        return (cout_matiere * quantite) + (heures_mo * taux_horaire) + cout_destruction + cout_autres
    
    @staticmethod
    def to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        """Convertit une ligne DB en dictionnaire."""
        return dict(row) if row else None


class VeilleModel:
    """Modèle pour la Veille Réglementaire."""
    
    @staticmethod
    def is_late(date_butoir: str, progression: int) -> bool:
        """Vérifie si une action est en retard."""
        if not date_butoir or progression >= 100:
            return False
        return datetime.strptime(date_butoir, '%Y-%m-%d').date() < datetime.now().date()


class InspectionModel:
    """Modèle pour les Inspections."""
    
    @staticmethod
    def calculate_score(results: List[Dict]) -> Dict[str, float]:
        """Calcule le score d'une inspection."""
        if not results:
            return {'score': 0, 'max': 0, 'percentage': 0}
        
        conforme = sum(1 for r in results if r['resultat'] == 'Conforme')
        non_conforme = sum(1 for r in results if r['resultat'] == 'Non conforme')
        total = conforme + non_conforme  # NA non compté
        
        if total == 0:
            return {'score': 0, 'max': 0, 'percentage': 100}
        
        percentage = (conforme / total) * 100
        return {
            'score': conforme,
            'max': total,
            'percentage': round(percentage, 1)
        }


class LabModel:
    """Modèle pour le Laboratoire."""
    
    @staticmethod
    def check_conformity(valeur: float, valeur_min: float, valeur_max: float) -> bool:
        """Vérifie la conformité d'une valeur."""
        if valeur_min is not None and valeur < valeur_min:
            return False
        if valeur_max is not None and valeur > valeur_max:
            return False
        return True

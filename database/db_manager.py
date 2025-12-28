# -*- coding: utf-8 -*-
"""
QualiManager - Module de gestion de la base de données SQLite
Gestion des connexions et création des tables du SMQ
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

# Chemin de la base de données
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "qualimanager.db")


def get_connection() -> sqlite3.Connection:
    """
    Établit une connexion à la base de données SQLite.
    Crée le dossier data si nécessaire.
    
    Returns:
        sqlite3.Connection: Objet de connexion à la BDD
    """
    # Créer le dossier data s'il n'existe pas
    data_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
    return conn


def init_database():
    """
    Initialise la base de données en créant toutes les tables nécessaires.
    Cette fonction est idempotente (peut être appelée plusieurs fois sans problème).
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Création de la table des Non-Conformités
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS non_conformites (
            -- Clé primaire auto-incrémentée
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- SECTION A : IDENTIFICATION
            date_enregistrement DATE NOT NULL,
            type_nc TEXT NOT NULL,              -- Interne, Client, Fournisseur
            entite TEXT,                        -- Département concerné
            profil TEXT,                        -- Profil de l'émetteur
            emetteur TEXT NOT NULL,             -- Personne qui enregistre la NC
            nom_tiers TEXT,                     -- Nom du Client ou Fournisseur concerné
            
            -- SECTION B : DESCRIPTION DU PROBLÈME
            anomalie TEXT,                      -- Type d'anomalie
            designation_produit TEXT,           -- Produit concerné
            numero_lot_bl_facture TEXT,         -- Numéro de lot, BL ou Facture
            quantite_concernee INTEGER,         -- Quantité affectée
            detail_probleme TEXT,               -- Description détaillée du problème
            evaluation_risque TEXT,             -- Mineur, Majeur, Critique
            
            -- SECTION C : ANALYSE ET ACTIONS
            probleme_exact TEXT,                -- Description précise du problème
            correction_immediate TEXT,          -- Action corrective immédiate
            methode_5why TEXT,                  -- Analyse des 5 Pourquoi
            cause_racine TEXT,                  -- Cause racine identifiée
            etude_portee TEXT,                  -- Étude de la portée du problème
            action_corrective TEXT,             -- Action corrective planifiée
            responsable_action TEXT,            -- Responsable de l'action
            suivi_action TEXT,                  -- État du suivi
            imputation_nc TEXT,                 -- À qui est imputée la NC
            
            -- SECTION D : CLÔTURE ET PREUVES
            preuve_efficacite TEXT,             -- Preuve de l'efficacité de l'action
            chemin_fichier_joint TEXT,          -- Chemin vers fichier PDF/Photo
            est_solde INTEGER DEFAULT 0,        -- Booléen : 0=Ouverte, 1=Soldée
            solde_par TEXT,                     -- Personne ayant soldé la NC
            date_solde DATE,                    -- Date de clôture
            
            -- Métadonnées
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Création d'un index sur la date d'enregistrement pour optimiser les recherches
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_nc_date_enregistrement 
        ON non_conformites(date_enregistrement)
    """)
    
    # Création d'un index sur le statut de solde pour filtrer rapidement
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_nc_est_solde 
        ON non_conformites(est_solde)
    """)
    
    # Création d'un index sur le type de NC
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_nc_type 
        ON non_conformites(type_nc)
    """)
    
    # Création de la table d'historique des modifications NC
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nc_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nc_id INTEGER NOT NULL,
            user_name TEXT NOT NULL,
            action TEXT NOT NULL,               -- 'creation', 'modification', 'cloture', 'suppression'
            field_changed TEXT,                 -- Nom du champ modifié (NULL pour création/suppression)
            old_value TEXT,                     -- Ancienne valeur
            new_value TEXT,                     -- Nouvelle valeur
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (nc_id) REFERENCES non_conformites(id) ON DELETE CASCADE
        )
    """)
    
    # Index sur nc_id pour requêtes rapides de l'historique d'une NC
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_history_nc_id 
        ON nc_history(nc_id)
    """)
    
    # Index sur timestamp pour tri chronologique
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_history_timestamp 
        ON nc_history(timestamp)
    """)
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée avec succès.")


def insert_non_conformite(data: Dict[str, Any]) -> int:
    """
    Insère une nouvelle Non-Conformité dans la base de données.
    
    Args:
        data: Dictionnaire contenant les données de la NC
        
    Returns:
        int: L'ID de la NC créée
        
    Raises:
        ValueError: Si les champs obligatoires sont manquants
        sqlite3.Error: En cas d'erreur SQL
    """
    # Vérification des champs obligatoires
    champs_obligatoires = ['date_enregistrement', 'type_nc', 'emetteur']
    for champ in champs_obligatoires:
        if champ not in data or not data[champ]:
            raise ValueError(f"Le champ '{champ}' est obligatoire.")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Construction de la requête INSERT
    colonnes = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    valeurs = list(data.values())
    
    query = f"INSERT INTO non_conformites ({colonnes}) VALUES ({placeholders})"
    
    try:
        cursor.execute(query, valeurs)
        conn.commit()
        nc_id = cursor.lastrowid
        print(f"✅ Non-Conformité #{nc_id} enregistrée avec succès.")
        return nc_id
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_all_non_conformites(filtre_solde: Optional[bool] = None) -> List[Dict[str, Any]]:
    """
    Récupère toutes les Non-Conformités.
    
    Args:
        filtre_solde: None=Toutes, True=Soldées uniquement, False=Ouvertes uniquement
        
    Returns:
        Liste de dictionnaires représentant les NC
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM non_conformites"
    params = []
    
    if filtre_solde is not None:
        query += " WHERE est_solde = ?"
        params.append(1 if filtre_solde else 0)
    
    query += " ORDER BY date_enregistrement DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # Conversion en liste de dictionnaires
    return [dict(row) for row in rows]


def get_non_conformite_by_id(nc_id: int) -> Optional[Dict[str, Any]]:
    """
    Récupère une Non-Conformité par son ID.
    
    Args:
        nc_id: L'identifiant de la NC
        
    Returns:
        Dictionnaire représentant la NC ou None si non trouvée
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM non_conformites WHERE id = ?", (nc_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def update_non_conformite(nc_id: int, data: Dict[str, Any]) -> bool:
    """
    Met à jour une Non-Conformité existante.
    
    Args:
        nc_id: L'identifiant de la NC à modifier
        data: Dictionnaire des données à mettre à jour
        
    Returns:
        bool: True si la mise à jour a réussi
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Ajout de la date de modification
    data['date_modification'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Construction de la requête UPDATE
    set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
    valeurs = list(data.values()) + [nc_id]
    
    query = f"UPDATE non_conformites SET {set_clause} WHERE id = ?"
    
    try:
        cursor.execute(query, valeurs)
        conn.commit()
        success = cursor.rowcount > 0
        if success:
            print(f"✅ Non-Conformité #{nc_id} mise à jour.")
        return success
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def delete_non_conformite(nc_id: int) -> bool:
    """
    Supprime une Non-Conformité.
    
    Args:
        nc_id: L'identifiant de la NC à supprimer
        
    Returns:
        bool: True si la suppression a réussi
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM non_conformites WHERE id = ?", (nc_id,))
        conn.commit()
        success = cursor.rowcount > 0
        if success:
            print(f"✅ Non-Conformité #{nc_id} supprimée.")
        return success
    finally:
        conn.close()


def get_statistics() -> Dict[str, Any]:
    """
    Retourne des statistiques sur les Non-Conformités.
    
    Returns:
        Dictionnaire contenant les statistiques
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # Total des NC
    cursor.execute("SELECT COUNT(*) FROM non_conformites")
    stats['total'] = cursor.fetchone()[0]
    
    # NC ouvertes
    cursor.execute("SELECT COUNT(*) FROM non_conformites WHERE est_solde = 0")
    stats['ouvertes'] = cursor.fetchone()[0]
    
    # NC soldées
    cursor.execute("SELECT COUNT(*) FROM non_conformites WHERE est_solde = 1")
    stats['soldees'] = cursor.fetchone()[0]
    
    # Par type
    cursor.execute("""
        SELECT type_nc, COUNT(*) as count 
        FROM non_conformites 
        GROUP BY type_nc
    """)
    stats['par_type'] = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Par niveau de risque
    cursor.execute("""
        SELECT evaluation_risque, COUNT(*) as count 
        FROM non_conformites 
        WHERE evaluation_risque IS NOT NULL
        GROUP BY evaluation_risque
    """)
    stats['par_risque'] = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    return stats


def log_nc_change(nc_id: int, user_name: str, action: str, field_changed: str = None, old_value: str = None, new_value: str = None) -> bool:
    """
    Enregistre une modification dans l'historique d'une NC.
    
    Args:
        nc_id: ID de la NC
        user_name: Nom de l'utilisateur qui a fait la modification
        action: Type d'action ('creation', 'modification', 'cloture', 'suppression')
        field_changed: Nom du champ modifié (optionnel)
        old_value: Ancienne valeur (optionnel)
        new_value: Nouvelle valeur (optionnel)
    
    Returns:
        bool: True si l'enregistrement a réussi
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO nc_history (nc_id, user_name, action, field_changed, old_value, new_value)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nc_id, user_name, action, field_changed, old_value, new_value))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement de l'historique: {e}")
        return False
    finally:
        conn.close()


def get_nc_history(nc_id: int) -> List[Dict[str, Any]]:
    """
    Récupère l'historique complet des modifications d'une NC.
    
    Args:
        nc_id: ID de la NC
    
    Returns:
        Liste des modifications triées par date décroissante
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, nc_id, user_name, action, field_changed, old_value, new_value, timestamp
            FROM nc_history
            WHERE nc_id = ?
            ORDER BY timestamp DESC
        """, (nc_id,))
        
        rows = cursor.fetchall()
        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'nc_id': row[1],
                'user_name': row[2],
                'action': row[3],
                'field_changed': row[4],
                'old_value': row[5],
                'new_value': row[6],
                'timestamp': row[7]
            })
        return history
    except sqlite3.OperationalError as e:
        if 'no such table' in str(e):
            # La table n'existe pas encore, initialiser la base
            print("⚠️ Table nc_history manquante, création en cours...")
            conn.close()
            init_database()
            return []
        else:
            raise
    finally:
        if not conn:
            conn = get_connection()
        conn.close()


# Initialisation automatique de la BDD au chargement du module
if __name__ == "__main__":
    init_database()

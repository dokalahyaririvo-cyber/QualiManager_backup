"""
Gestionnaire de base de données pour le module Veille Réglementaire & Exigences.
"""
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime


class VeilleDBManager:
    """Gère la base de données SQLite pour les veilles réglementaires et plans d'actions."""
    
    def __init__(self, db_path: str = None):
        """Initialise la connexion à la base de données.
        
        Args:
            db_path: Chemin vers la base de données. Si None, utilise le chemin par défaut.
        """
        if db_path is None:
            # Mode développement - base locale
            db_path = "data/veille.db"
        self.db_path = db_path
        if not Path(db_path).exists():
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()
    
    def _get_connection(self):
        """Crée une connexion à la base de données."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_tables(self):
        """Crée les tables si elles n'existent pas."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Table veille_item
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS veille_item (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                annee INTEGER,
                date_publication TEXT,
                description TEXT,
                resume TEXT,
                lien_url TEXT,
                commentaire_interne TEXT,
                date_lecture TEXT,
                statut_veille TEXT DEFAULT 'Non concerné',
                fichier_joint TEXT,
                plan_action_id INTEGER,
                plan_action_numero TEXT,
                date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plan_action_id) REFERENCES veille_action_plan(id)
            )
        """)
        
        # Table veille_action_plan
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS veille_action_plan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                veille_id INTEGER NOT NULL,
                date_creation TEXT NOT NULL,
                resume_origine TEXT,
                origine TEXT,
                objectif TEXT,
                priorite TEXT DEFAULT 'Mineure',
                type_action TEXT DEFAULT 'Amélioration',
                auteurs TEXT,
                date_fin_prevue TEXT,
                moyen_controle TEXT,
                date_solde TEXT,
                remarques TEXT,
                taches_liste TEXT,
                statut_calcule REAL DEFAULT 0.0,
                FOREIGN KEY (veille_id) REFERENCES veille_item(id)
            )
        """)
        
        # Migration : Ajouter plan_action_numero si n'existe pas
        try:
            cursor.execute("SELECT plan_action_numero FROM veille_item LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE veille_item ADD COLUMN plan_action_numero TEXT")
        
        conn.commit()
        conn.close()
    
    # ============= VEILLE ITEMS =============
    
    def get_all_veilles(self) -> List[Dict]:
        """Récupère toutes les veilles."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.*, 
                   CASE WHEN v.plan_action_id IS NOT NULL THEN 'Oui' ELSE 'Non' END as a_plan_action
            FROM veille_item v
            ORDER BY v.date_publication DESC, v.id DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_veille_by_id(self, veille_id: int) -> Optional[Dict]:
        """Récupère une veille par son ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM veille_item WHERE id = ?", (veille_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def create_veille(self, data: Dict) -> int:
        """Crée une nouvelle veille et retourne son ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO veille_item 
            (source, annee, date_publication, description, resume, lien_url, 
             commentaire_interne, date_lecture, statut_veille, fichier_joint, plan_action_numero)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('source'),
            data.get('annee'),
            data.get('date_publication'),
            data.get('description'),
            data.get('resume'),
            data.get('lien_url'),
            data.get('commentaire_interne'),
            data.get('date_lecture'),
            data.get('statut_veille', 'Non concerné'),
            data.get('fichier_joint'),
            data.get('plan_action_numero'),
        ))
        
        veille_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return veille_id
    
    def update_veille(self, veille_id: int, data: Dict):
        """Met à jour une veille."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE veille_item SET
                source = ?,
                annee = ?,
                date_publication = ?,
                description = ?,
                resume = ?,
                lien_url = ?,
                commentaire_interne = ?,
                date_lecture = ?,
                statut_veille = ?,
                fichier_joint = ?,
                plan_action_id = ?,
                plan_action_numero = ?
            WHERE id = ?
        """, (
            data.get('source'),
            data.get('annee'),
            data.get('date_publication'),
            data.get('description'),
            data.get('resume'),
            data.get('lien_url'),
            data.get('commentaire_interne'),
            data.get('date_lecture'),
            data.get('statut_veille'),
            data.get('fichier_joint'),
            data.get('plan_action_id'),
            data.get('plan_action_numero'),
            veille_id
        ))
        
        conn.commit()
        conn.close()
    
    def link_plan_to_veille(self, veille_id: int, plan_action_id: int):
        """Lie un plan d'action à une veille (mise à jour partielle)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE veille_item SET
                plan_action_id = ?
            WHERE id = ?
        """, (plan_action_id, veille_id))
        
        conn.commit()
        conn.close()
    
    def delete_veille(self, veille_id: int):
        """Supprime une veille (et son plan d'action associé si existant)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Supprimer d'abord le plan d'action associé
        cursor.execute("DELETE FROM veille_action_plan WHERE veille_id = ?", (veille_id,))
        
        # Puis supprimer la veille
        cursor.execute("DELETE FROM veille_item WHERE id = ?", (veille_id,))
        
        conn.commit()
        conn.close()
    
    # ============= PLANS D'ACTIONS =============
    
    def get_all_action_plans(self) -> List[Dict]:
        """Récupère tous les plans d'actions."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ap.*, v.description as veille_description
            FROM veille_action_plan ap
            LEFT JOIN veille_item v ON ap.veille_id = v.id
            ORDER BY ap.date_creation DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        plans = []
        for row in rows:
            plan = dict(row)
            # Décoder la liste des tâches JSON
            if plan.get('taches_liste'):
                try:
                    plan['taches_liste'] = json.loads(plan['taches_liste'])
                except:
                    plan['taches_liste'] = []
            else:
                plan['taches_liste'] = []
            plans.append(plan)
        
        return plans
    
    def get_action_plan_by_id(self, plan_id: int) -> Optional[Dict]:
        """Récupère un plan d'action par son ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ap.*, v.description as veille_description, v.source, v.resume
            FROM veille_action_plan ap
            LEFT JOIN veille_item v ON ap.veille_id = v.id
            WHERE ap.id = ?
        """, (plan_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            plan = dict(row)
            if plan.get('taches_liste'):
                try:
                    plan['taches_liste'] = json.loads(plan['taches_liste'])
                except:
                    plan['taches_liste'] = []
            else:
                plan['taches_liste'] = []
            return plan
        return None
    
    def create_action_plan(self, data: Dict) -> int:
        """Crée un nouveau plan d'action et retourne son ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Encoder les tâches en JSON
        taches_json = json.dumps(data.get('taches_liste', []))
        
        cursor.execute("""
            INSERT INTO veille_action_plan
            (veille_id, date_creation, resume_origine, origine, objectif, priorite,
             type_action, auteurs, date_fin_prevue, moyen_controle, date_solde,
             remarques, taches_liste, statut_calcule)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('veille_id'),
            data.get('date_creation', datetime.now().strftime('%Y-%m-%d')),
            data.get('resume_origine'),
            data.get('origine'),
            data.get('objectif'),
            data.get('priorite', 'Mineure'),
            data.get('type_action', 'Amélioration'),
            data.get('auteurs'),
            data.get('date_fin_prevue'),
            data.get('moyen_controle'),
            data.get('date_solde'),
            data.get('remarques'),
            taches_json,
            data.get('statut_calcule', 0.0)
        ))
        
        plan_id = cursor.lastrowid
        
        # Mettre à jour la veille parente avec le lien vers le plan
        cursor.execute("""
            UPDATE veille_item SET plan_action_id = ? WHERE id = ?
        """, (plan_id, data.get('veille_id')))
        
        conn.commit()
        conn.close()
        return plan_id
    
    def update_action_plan(self, plan_id: int, data: Dict):
        """Met à jour un plan d'action."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Encoder les tâches en JSON
        taches_json = json.dumps(data.get('taches_liste', []))
        
        cursor.execute("""
            UPDATE veille_action_plan SET
                objectif = ?,
                priorite = ?,
                type_action = ?,
                auteurs = ?,
                date_fin_prevue = ?,
                moyen_controle = ?,
                date_solde = ?,
                remarques = ?,
                taches_liste = ?,
                statut_calcule = ?
            WHERE id = ?
        """, (
            data.get('objectif'),
            data.get('priorite'),
            data.get('type_action'),
            data.get('auteurs'),
            data.get('date_fin_prevue'),
            data.get('moyen_controle'),
            data.get('date_solde'),
            data.get('remarques'),
            taches_json,
            data.get('statut_calcule', 0.0),
            plan_id
        ))
        
        conn.commit()
        conn.close()
    
    def update_plan_taches(self, plan_id: int, taches_liste: str, statut_calcule: float):
        """Met à jour uniquement les tâches et l'avancement d'un plan."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE veille_action_plan SET
                taches_liste = ?,
                statut_calcule = ?
            WHERE id = ?
        """, (taches_liste, statut_calcule, plan_id))
        
        conn.commit()
        conn.close()
    
    def delete_action_plan(self, plan_id: int):
        """Supprime un plan d'action."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Récupérer la veille associée
        cursor.execute("SELECT veille_id FROM veille_action_plan WHERE id = ?", (plan_id,))
        row = cursor.fetchone()
        if row:
            veille_id = row['veille_id']
            # Retirer le lien dans la veille
            cursor.execute("UPDATE veille_item SET plan_action_id = NULL WHERE id = ?", (veille_id,))
        
        # Supprimer le plan
        cursor.execute("DELETE FROM veille_action_plan WHERE id = ?", (plan_id,))
        
        conn.commit()
        conn.close()
    
    # ============= STATISTIQUES =============
    
    def get_veilles_stats(self) -> Dict:
        """Récupère les statistiques des veilles."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Répartition par statut
        cursor.execute("""
            SELECT statut_veille, COUNT(*) as count
            FROM veille_item
            GROUP BY statut_veille
        """)
        statuts = {row['statut_veille']: row['count'] for row in cursor.fetchall()}
        
        # Répartition par source
        cursor.execute("""
            SELECT source, COUNT(*) as count
            FROM veille_item
            GROUP BY source
        """)
        sources = {row['source']: row['count'] for row in cursor.fetchall()}
        
        # Total cette année
        current_year = datetime.now().year
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM veille_item
            WHERE annee = ?
        """, (current_year,))
        total_annee = cursor.fetchone()['total']
        
        conn.close()
        
        return {
            'statuts': statuts,
            'sources': sources,
            'total_annee': total_annee
        }
    
    def get_action_plans_stats(self) -> Dict:
        """Récupère les statistiques des plans d'actions."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Actions soldées vs en cours
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN date_solde IS NOT NULL AND date_solde != '' THEN 1 END) as soldees,
                COUNT(CASE WHEN date_solde IS NULL OR date_solde = '' THEN 1 END) as en_cours
            FROM veille_action_plan
        """)
        row = cursor.fetchone()
        soldees = row['soldees']
        en_cours = row['en_cours']
        
        # Répartition par origine
        cursor.execute("""
            SELECT origine, COUNT(*) as count
            FROM veille_action_plan
            GROUP BY origine
        """)
        origines = {row['origine']: row['count'] for row in cursor.fetchall()}
        
        # Répartition par type
        cursor.execute("""
            SELECT type_action, COUNT(*) as count
            FROM veille_action_plan
            GROUP BY type_action
        """)
        types = {row['type_action']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'soldees': soldees,
            'en_cours': en_cours,
            'origines': origines,
            'types': types
        }
    
    def get_todo_items(self) -> Dict:
        """Récupère les éléments de la To-Do List."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Veilles à l'étude
        cursor.execute("""
            SELECT id, source, description, date_lecture
            FROM veille_item
            WHERE statut_veille = 'À l''étude'
            ORDER BY date_lecture DESC
        """)
        veilles_etude = [dict(row) for row in cursor.fetchall()]
        
        # Plans d'actions en retard (date_fin_prevue dépassée et non soldé)
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT ap.id, ap.objectif, ap.date_fin_prevue, v.source
            FROM veille_action_plan ap
            LEFT JOIN veille_item v ON ap.veille_id = v.id
            WHERE ap.date_fin_prevue < ?
            AND (ap.date_solde IS NULL OR ap.date_solde = '')
            ORDER BY ap.date_fin_prevue ASC
        """, (today,))
        plans_retard = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'veilles_etude': veilles_etude,
            'plans_retard': plans_retard
        }

# -*- coding: utf-8 -*-
"""
QualiManager - Gestionnaire de base de données SQLite
"""

import sqlite3
import hashlib
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class DatabaseManager:
    """Gestionnaire de base de données SQLite."""
    
    def __init__(self, db_path: str = "qualimanager.db"):
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager pour les connexions."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialise la base de données."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table utilisateurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    password_plain TEXT,
                    role TEXT NOT NULL DEFAULT 'Utilisateur',
                    actif INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Table non-conformités
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS non_conformites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reference TEXT UNIQUE NOT NULL,
                    date_detection DATE NOT NULL,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    detecteur_id INTEGER,
                    type_nc TEXT NOT NULL,
                    origine TEXT,
                    gravite TEXT NOT NULL,
                    statut TEXT DEFAULT 'Ouverte',
                    
                    -- Section A: Description
                    description TEXT,
                    produit_concerne TEXT,
                    lot_serie TEXT,
                    quantite_affectee INTEGER,
                    lieu_detection TEXT,
                    type_anomalie TEXT,
                    categorie_nc TEXT,
                    imputation TEXT,
                    pieces_jointes TEXT,
                    
                    -- Section B: Analyse
                    causes_immediates TEXT,
                    cause_racine TEXT,
                    methode_analyse TEXT,
                    analyse_5m TEXT,
                    analyse_portee TEXT,
                    
                    -- Section C: Actions
                    actions_immediates TEXT,
                    actions_correctives TEXT,
                    actions_preventives TEXT,
                    actions_immediates_table TEXT,
                    actions_correctives_table TEXT,
                    responsable_id INTEGER,
                    date_echeance DATE,
                    
                    -- Section D: Clôture
                    date_cloture DATE,
                    verificateur_id INTEGER,
                    efficacite TEXT,
                    commentaires_cloture TEXT,
                    
                    FOREIGN KEY (detecteur_id) REFERENCES users(id),
                    FOREIGN KEY (responsable_id) REFERENCES users(id),
                    FOREIGN KEY (verificateur_id) REFERENCES users(id)
                )
            ''')
            
            # Table analyses
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nc_id INTEGER,
                    methode TEXT NOT NULL,
                    data TEXT,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (nc_id) REFERENCES non_conformites(id),
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            ''')
            
            # Table actions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nc_id INTEGER NOT NULL,
                    type_action TEXT NOT NULL,
                    description TEXT NOT NULL,
                    responsable_id INTEGER,
                    date_echeance DATE,
                    date_realisation DATE,
                    statut TEXT DEFAULT 'En attente',
                    efficacite TEXT,
                    commentaires TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (nc_id) REFERENCES non_conformites(id),
                    FOREIGN KEY (responsable_id) REFERENCES users(id)
                )
            ''')
            
            # Table historique/audit trail
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historique (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    record_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    user_id INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Créer l'admin par défaut s'il n'existe pas
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Administrateur'")
            if cursor.fetchone()[0] == 0:
                self._create_default_admin(cursor)

            # Ajout des colonnes manquantes (migrations légères)
            self._ensure_columns(conn)

    def _ensure_columns(self, conn: sqlite3.Connection):
        """Ajoute les colonnes manquantes si la base existe déjà."""
        self._add_column(conn, 'users', 'password_plain', 'TEXT')
        self._add_column(conn, 'non_conformites', 'type_anomalie', 'TEXT')
        self._add_column(conn, 'non_conformites', 'categorie_nc', 'TEXT')
        self._add_column(conn, 'non_conformites', 'imputation', 'TEXT')
        self._add_column(conn, 'non_conformites', 'pieces_jointes', 'TEXT')
        self._add_column(conn, 'non_conformites', 'analyse_5m', 'TEXT')
        self._add_column(conn, 'non_conformites', 'analyse_portee', 'TEXT')
        self._add_column(conn, 'non_conformites', 'analyse_details', 'TEXT')
        self._add_column(conn, 'non_conformites', 'actions_immediates_table', 'TEXT')
        self._add_column(conn, 'non_conformites', 'actions_correctives_table', 'TEXT')
        self._add_column(conn, 'non_conformites', 'matieres_reclames', 'TEXT')

    def _add_column(self, conn: sqlite3.Connection, table: str, column: str, definition: str):
        """Ajoute une colonne si elle n'existe pas."""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        existing = [row[1] for row in cursor.fetchall()]
        if column not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
    
    def _create_default_admin(self, cursor):
        """Crée l'administrateur par défaut."""
        password_hash = hashlib.sha256("Admin@2024!".encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (nom, email, password_hash, password_plain, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ("Administrateur", "admin@qualimanager.local", password_hash, "Admin@2024!", "Administrateur"))
    
    # ========== USERS ==========
    
    def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authentifie un utilisateur."""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, nom, email, role, actif FROM users
                WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))
            
            row = cursor.fetchone()
            if row and row['actif']:
                # Mise à jour last_login
                cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                             (datetime.now(), row['id']))
                return dict(row)
            return None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Récupère tous les utilisateurs."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, nom, email, role, actif, created_at, last_login, password_plain FROM users ORDER BY nom')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def create_user(self, nom: str, email: str, password: str, role: str = "Utilisateur") -> int:
        """Crée un nouvel utilisateur."""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (nom, email, password_hash, password_plain, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (nom, email, password_hash, password, role))
            return cursor.lastrowid
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Met à jour un utilisateur."""
        allowed_fields = ['nom', 'email', 'role', 'actif', 'password_plain']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}
        
        if 'password' in kwargs and kwargs['password']:
            updates['password_hash'] = hashlib.sha256(kwargs['password'].encode()).hexdigest()
            updates['password_plain'] = kwargs['password']
        
        if not updates:
            return False
        
        set_clause = ', '.join(f'{k} = ?' for k in updates.keys())
        values = list(updates.values()) + [user_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE users SET {set_clause} WHERE id = ?', values)
            return cursor.rowcount > 0
    
    def delete_user(self, user_id: int) -> bool:
        """Supprime un utilisateur."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            return cursor.rowcount > 0
    
    # ========== NON-CONFORMITÉS ==========
    
    def generate_nc_reference(self) -> str:
        """Génère une référence NC unique."""
        year = datetime.now().year
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM non_conformites 
                WHERE reference LIKE ?
            ''', (f'NC-{year}-%',))
            count = cursor.fetchone()[0] + 1
            return f"NC-{year}-{count:04d}"
    
    def create_nc(self, data: Dict[str, Any]) -> int:
        """Crée une nouvelle NC."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f'INSERT INTO non_conformites ({columns}) VALUES ({placeholders})',
                list(data.values())
            )
            return cursor.lastrowid
    
    def get_all_nc(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Récupère toutes les NC avec filtres optionnels."""
        query = '''
            SELECT nc.*, u.nom as detecteur_nom
            FROM non_conformites nc
            LEFT JOIN users u ON nc.detecteur_id = u.id
            WHERE 1=1
        '''
        params = []
        
        if filters:
            if filters.get('statut'):
                query += ' AND nc.statut = ?'
                params.append(filters['statut'])
            if filters.get('gravite'):
                query += ' AND nc.gravite = ?'
                params.append(filters['gravite'])
            if filters.get('type_nc'):
                query += ' AND nc.type_nc = ?'
                params.append(filters['type_nc'])
            if filters.get('search'):
                query += ' AND (nc.reference LIKE ? OR nc.description LIKE ?)'
                search = f'%{filters["search"]}%'
                params.extend([search, search])
        
        query += ' ORDER BY nc.date_creation DESC'
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_nc(self, nc_id: int) -> Optional[Dict[str, Any]]:
        """Récupère une NC par ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM non_conformites WHERE id = ?', (nc_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def find_nc(self, query: str) -> Optional[Dict[str, Any]]:
        """Recherche une NC par référence ou n° de lot."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM non_conformites
                WHERE reference = ? OR lot_serie = ?
                ORDER BY date_creation DESC
                LIMIT 1
            ''', (query, query))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_nc(self, nc_id: int, data: Dict[str, Any]) -> bool:
        """Met à jour une NC."""
        if not data:
            return False
        
        set_clause = ', '.join(f'{k} = ?' for k in data.keys())
        values = list(data.values()) + [nc_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE non_conformites SET {set_clause} WHERE id = ?', values)
            return cursor.rowcount > 0
    
    def delete_nc(self, nc_id: int) -> bool:
        """Supprime une NC."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM non_conformites WHERE id = ?', (nc_id,))
            return cursor.rowcount > 0

    # ========== ANALYSES ==========

    def save_analysis(self, nc_id: int, methode: str, data: str, user_id: int) -> int:
        """Insère ou met à jour une analyse pour une NC et une méthode donnée."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM analyses WHERE nc_id = ? AND methode = ? ORDER BY id DESC LIMIT 1', (nc_id, methode))
            existing = cursor.fetchone()
            if existing:
                cursor.execute('UPDATE analyses SET data = ?, created_by = ? WHERE id = ?', (data, user_id, existing['id']))
                return existing['id']
            cursor.execute('INSERT INTO analyses (nc_id, methode, data, created_by) VALUES (?, ?, ?, ?)', (nc_id, methode, data, user_id))
            return cursor.lastrowid
    
    # ========== STATISTIQUES ==========
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques globales."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # NC par statut
            cursor.execute('''
                SELECT statut, COUNT(*) as count 
                FROM non_conformites 
                GROUP BY statut
            ''')
            stats['by_status'] = {row['statut']: row['count'] for row in cursor.fetchall()}
            
            # NC par gravité
            cursor.execute('''
                SELECT gravite, COUNT(*) as count 
                FROM non_conformites 
                GROUP BY gravite
            ''')
            stats['by_severity'] = {row['gravite']: row['count'] for row in cursor.fetchall()}
            
            # NC par type
            cursor.execute('''
                SELECT type_nc, COUNT(*) as count 
                FROM non_conformites 
                GROUP BY type_nc
            ''')
            stats['by_type'] = {row['type_nc']: row['count'] for row in cursor.fetchall()}
            
            # Total
            cursor.execute('SELECT COUNT(*) FROM non_conformites')
            stats['total'] = cursor.fetchone()[0]
            
            # Ouvertes
            cursor.execute("SELECT COUNT(*) FROM non_conformites WHERE statut = 'Ouverte'")
            stats['open'] = cursor.fetchone()[0]
            
            # En cours
            cursor.execute("SELECT COUNT(*) FROM non_conformites WHERE statut = 'En cours'")
            stats['in_progress'] = cursor.fetchone()[0]
            
            # Résolues
            cursor.execute("SELECT COUNT(*) FROM non_conformites WHERE statut = 'Clôturée'")
            stats['resolved'] = cursor.fetchone()[0]
            
            # Délai moyen de résolution
            cursor.execute('''
                SELECT AVG(julianday(date_cloture) - julianday(date_detection)) as avg_days
                FROM non_conformites 
                WHERE date_cloture IS NOT NULL
            ''')
            row = cursor.fetchone()
            stats['avg_resolution_days'] = round(row[0], 1) if row[0] else 0
            
            return stats
    
    # ========== ANALYSES ==========
    
    def save_analysis(self, nc_id: int, method: str, data: str, user_id: int) -> int:
        """Sauvegarde une analyse."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analyses (nc_id, methode, data, created_by)
                VALUES (?, ?, ?, ?)
            ''', (nc_id, method, data, user_id))
            return cursor.lastrowid
    
    def get_analyses(self, nc_id: int) -> List[Dict[str, Any]]:
        """Récupère les analyses d'une NC."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.*, u.nom as created_by_nom
                FROM analyses a
                LEFT JOIN users u ON a.created_by = u.id
                WHERE a.nc_id = ?
                ORDER BY a.created_at DESC
            ''', (nc_id,))
            return [dict(row) for row in cursor.fetchall()]

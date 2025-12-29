# -*- coding: utf-8 -*-
"""
QualiManager ERP QHSE - Gestionnaire de base de données étendu
Support complet: NC, Veille, Inspections, Laboratoire, KPI
"""

import sqlite3
import hashlib
import json
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from .models import init_database, NCModel, VeilleModel, InspectionModel, LabModel


class DatabaseManager:
    """Gestionnaire de base de données SQLite étendu pour ERP QHSE."""
    
    APP_VERSION = "2.1.0"  # Version actuelle de l'application
    
    def __init__(self, db_path: str = "qualimanager.db"):
        self.db_path = db_path
        # Initialiser avec le nouveau schéma
        init_database(db_path)
        # Vérifier et migrer si nécessaire
        self._check_and_migrate()
        self._ensure_admin()
        self._ensure_nc_columns()
    
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
    
    def _get_db_version(self) -> str:
        """Récupère la version actuelle de la base de données."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version FROM app_version WHERE id = 1")
                result = cursor.fetchone()
                return result[0] if result else "1.0.0"
        except:
            # Table app_version n'existe pas encore (ancienne version)
            return "1.0.0"
    
    def _set_db_version(self, version: str, description: str = ""):
        """Définit la version de la base de données."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO app_version (id, version, last_migration, description)
                VALUES (1, ?, CURRENT_TIMESTAMP, ?)
            """, (version, description))
    
    def _backup_database(self):
        """Crée une sauvegarde avant migration."""
        import shutil
        from pathlib import Path
        
        backup_dir = Path(self.db_path).parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"backup_before_migration_{timestamp}.db"
        
        shutil.copy2(self.db_path, backup_path)
        print(f"[OK] Sauvegarde créée: {backup_path.name}")
        return backup_path
    
    def _check_and_migrate(self):
        """Vérifie la version et effectue les migrations nécessaires."""
        db_version = self._get_db_version()
        
        if db_version == self.APP_VERSION:
            return  # Déjà à jour
        
        print(f"\n[Actualiser] Migration de la base de données v{db_version} > v{self.APP_VERSION}")
        
        # Sauvegarde avant migration
        self._backup_database()
        
        # Appliquer les migrations selon la version
        try:
            if db_version < "2.0.0":
                self._migrate_to_2_0_0()
            
            if db_version < "2.1.0":
                self._migrate_to_2_1_0()
            
            # Mettre à jour la version
            self._set_db_version(self.APP_VERSION, f"Migration depuis v{db_version}")
            print(f"[OK] Migration terminée avec succès !\n")
            
        except Exception as e:
            print(f"[Erreur] Erreur lors de la migration: {e}")
            print("[Attention] La sauvegarde a été créée dans le dossier backups/")
            raise
    
    def _migrate_to_2_0_0(self):
        """Migration vers la version 2.0.0."""
        print("  > Application de la migration 2.0.0...")
        # Ajouter les nouvelles fonctionnalités de la v2.0
        # (Cette migration est pour l'exemple, ajustez selon vos besoins)
    
    def _migrate_to_2_1_0(self):
        """Migration vers la version 2.1.0."""
        print("  > Application de la migration 2.1.0...")
        with self.get_connection() as conn:
            # Exemple: Ajouter des colonnes si nécessaire
            # self._add_column_if_not_exists(conn, 'nc_header', 'nouvelle_colonne', 'TEXT')
            pass
    
    def _add_column_if_not_exists(self, conn, table: str, column: str, col_type: str):
        """Ajoute une colonne si elle n'existe pas."""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        if column not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
    
    def _ensure_nc_columns(self):
        """S'assure que toutes les colonnes NC existent."""
        with self.get_connection() as conn:
            # Colonnes pour l'analyse détaillée
            self._add_column_if_not_exists(conn, 'nc_header', 'analyse_details', 'TEXT')
            self._add_column_if_not_exists(conn, 'nc_header', 'analyse_portee', 'TEXT')
            # Colonnes pour les actions en JSON
            self._add_column_if_not_exists(conn, 'nc_header', 'actions_immediates_table', 'TEXT')
            self._add_column_if_not_exists(conn, 'nc_header', 'actions_correctives_table', 'TEXT')
            # Colonne matières réclamées
            self._add_column_if_not_exists(conn, 'nc_header', 'matieres_reclames', 'TEXT')
    
    def _ensure_admin(self):
        """S'assure qu'un admin existe."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Administrateur'")
            if cursor.fetchone()[0] == 0:
                password_hash = hashlib.sha256("Admin@2024!".encode()).hexdigest()
                cursor.execute('''
                    INSERT INTO users (nom, email, password_hash, password_plain, role, taux_horaire)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', ("Administrateur", "admin@qualimanager.local", password_hash, "Admin@2024!", "Administrateur", 35.0))
    
    # ========================================================================
    # UTILISATEURS
    # ========================================================================
    
    def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authentifie un utilisateur."""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, nom, email, role, actif, service, taux_horaire, preferences
                FROM users WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))
            
            row = cursor.fetchone()
            if row and row['actif']:
                cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                             (datetime.now(), row['id']))
                return dict(row)
            return None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Récupère tous les utilisateurs."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, nom, email, role, service, actif, created_at, last_login, password_plain, taux_horaire
                FROM users ORDER BY nom
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_users_dropdown(self) -> List[Dict[str, Any]]:
        """Récupère les utilisateurs pour les dropdowns."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, nom FROM users WHERE actif = 1 ORDER BY nom')
            return [dict(row) for row in cursor.fetchall()]
    
    def create_user(self, nom: str, email: str, password: str, role: str = "Utilisateur", 
                    service: str = None, taux_horaire: float = 35.0) -> int:
        """Crée un nouvel utilisateur."""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (nom, email, password_hash, password_plain, role, service, taux_horaire)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nom, email, password_hash, password, role, service, taux_horaire))
            return cursor.lastrowid
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Met à jour un utilisateur."""
        allowed_fields = ['nom', 'email', 'role', 'actif', 'service', 'taux_horaire', 'preferences']
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
    
    def save_user_preferences(self, user_id: int, preferences: Dict) -> bool:
        """Sauvegarde les préférences utilisateur."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET preferences = ? WHERE id = ?', 
                          (json.dumps(preferences), user_id))
            return cursor.rowcount > 0
    
    # ========================================================================
    # NON-CONFORMITÉS (NC)
    # ========================================================================
    
    def generate_nc_reference(self) -> str:
        """Génère une référence NC unique."""
        year = datetime.now().year
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Chercher dans les deux tables pour compatibilité
            cursor.execute('''
                SELECT MAX(CAST(SUBSTR(reference, -4) AS INTEGER)) as max_num
                FROM nc_header WHERE reference LIKE ?
            ''', (f'NC-{year}-%',))
            result = cursor.fetchone()
            count = (result['max_num'] or 0) + 1
            return f"NC-{year}-{count:04d}"
    
    def create_nc(self, data: Dict[str, Any]) -> int:
        """Crée une nouvelle NC."""
        # Calcul automatique du coût total
        if 'cout_matiere' in data:
            data['cout_total'] = NCModel.calculate_cost(
                data.get('cout_matiere', 0),
                data.get('quantite_affectee', 0),
                data.get('cout_mo_heures', 0),
                data.get('cout_mo_taux', 35.0),
                data.get('cout_destruction', 0),
                data.get('cout_autres', 0)
            )
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f'INSERT INTO nc_header ({columns}) VALUES ({placeholders})',
                list(data.values())
            )
            nc_id = cursor.lastrowid
            
            # Créer événement timeline
            if data.get('lot_serie'):
                self._create_lot_event(cursor, data['lot_serie'], 'NC', 
                                      f"NC créée: {data.get('reference', '')}", 
                                      'nc_header', nc_id)
            
            return nc_id
    
    def get_all_nc(self, filters: Dict[str, Any] = None, limit: int = None, offset: int = 0, count_only: bool = False) -> List[Dict[str, Any]]:
        """Récupère toutes les NC avec filtres optionnels, pagination et comptage optimisé.
        
        Args:
            filters: Dictionnaire de filtres (statut, gravite, type_nc, search, etc.)
            limit: Nombre maximum de résultats (None = tous)
            offset: Nombre de résultats à sauter
            count_only: Si True, retourne seulement le count total
        """
        # Construction de la clause WHERE
        where_clause = 'WHERE 1=1'
        params = []
        
        if filters:
            if filters.get('statut') and filters.get('statut') != 'Tous':
                where_clause += ' AND nc.statut = ?'
                params.append(filters['statut'])
            if filters.get('gravite') and filters.get('gravite') != 'Tous':
                where_clause += ' AND nc.gravite = ?'
                params.append(filters['gravite'])
            if filters.get('type_nc') and filters.get('type_nc') != 'Tous':
                where_clause += ' AND nc.type_nc = ?'
                params.append(filters['type_nc'])
            if filters.get('origine') and filters.get('origine') != 'Tous':
                where_clause += ' AND nc.origine = ?'
                params.append(filters['origine'])
            if filters.get('categorie_nc') and filters.get('categorie_nc') != 'Tous':
                where_clause += ' AND nc.categorie_nc = ?'
                params.append(filters['categorie_nc'])
            if filters.get('imputation') and filters.get('imputation') != 'Tous':
                where_clause += ' AND nc.imputation = ?'
                params.append(filters['imputation'])
            if filters.get('date_start'):
                where_clause += ' AND nc.date_detection >= ?'
                params.append(filters['date_start'])
            if filters.get('date_end'):
                where_clause += ' AND nc.date_detection <= ?'
                params.append(filters['date_end'])
            if filters.get('search'):
                where_clause += ' AND (nc.reference LIKE ? OR nc.description LIKE ? OR nc.lot_serie LIKE ? OR nc.produit_concerne LIKE ?)'
                search = f'%{filters["search"]}%'
                params.extend([search, search, search, search])
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Si comptage seulement
                if count_only:
                    count_query = f'SELECT COUNT(*) as total FROM nc_header nc {where_clause}'
                    cursor.execute(count_query, params)
                    return cursor.fetchone()['total']
                
                # Requête principale avec pagination
                query = f'''
                    SELECT nc.*, u.nom as detecteur_nom
                    FROM nc_header nc
                    LEFT JOIN users u ON nc.detecteur_id = u.id
                    {where_clause}
                    ORDER BY CAST(nc.reference AS INTEGER) DESC
                '''
                
                if limit is not None:
                    query += f' LIMIT {limit} OFFSET {offset}'
                
                cursor.execute(query, params)
                results = [dict(row) for row in cursor.fetchall()]
            except sqlite3.OperationalError:
                # Fallback sur ancienne table
                query = query.replace('nc_header', 'non_conformites')
                cursor.execute(query, params)
                results = [dict(row) for row in cursor.fetchall()]
            return results
    
    def get_nc(self, nc_id: int) -> Optional[Dict[str, Any]]:
        """Récupère une NC par ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT * FROM nc_header WHERE id = ?', (nc_id,))
                row = cursor.fetchone()
            except sqlite3.OperationalError:
                cursor.execute('SELECT * FROM non_conformites WHERE id = ?', (nc_id,))
                row = cursor.fetchone()
            return dict(row) if row else None
    
    def find_nc(self, query: str) -> Optional[Dict[str, Any]]:
        """Recherche une NC par référence ou no de lot."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    SELECT * FROM nc_header
                    WHERE reference = ? OR lot_serie = ?
                    ORDER BY date_creation DESC LIMIT 1
                ''', (query, query))
                row = cursor.fetchone()
            except sqlite3.OperationalError:
                cursor.execute('''
                    SELECT * FROM non_conformites
                    WHERE reference = ? OR lot_serie = ?
                    ORDER BY date_creation DESC LIMIT 1
                ''', (query, query))
                row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_nc(self, nc_id: int, data: Dict[str, Any]) -> bool:
        """Met à jour une NC."""
        if not data:
            return False
        
        # Recalculer le coût si des champs de coût sont modifiés
        if any(k in data for k in ['cout_matiere', 'quantite_affectee', 'cout_mo_heures', 'cout_destruction']):
            nc = self.get_nc(nc_id) or {}
            data['cout_total'] = NCModel.calculate_cost(
                data.get('cout_matiere', nc.get('cout_matiere', 0)),
                data.get('quantite_affectee', nc.get('quantite_affectee', 0)),
                data.get('cout_mo_heures', nc.get('cout_mo_heures', 0)),
                data.get('cout_mo_taux', nc.get('cout_mo_taux', 35.0)),
                data.get('cout_destruction', nc.get('cout_destruction', 0)),
                data.get('cout_autres', nc.get('cout_autres', 0))
            )
        
        set_clause = ', '.join(f'{k} = ?' for k in data.keys())
        values = list(data.values()) + [nc_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f'UPDATE nc_header SET {set_clause} WHERE id = ?', values)
            except sqlite3.OperationalError:
                cursor.execute(f'UPDATE non_conformites SET {set_clause} WHERE id = ?', values)
            return cursor.rowcount > 0
    
    def delete_nc(self, nc_id: int) -> bool:
        """Supprime une NC."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('DELETE FROM nc_header WHERE id = ?', (nc_id,))
            except sqlite3.OperationalError:
                cursor.execute('DELETE FROM non_conformites WHERE id = ?', (nc_id,))
            return cursor.rowcount > 0
    
    # Historique NC
    def log_nc_change(self, nc_id: int, user_name: str, action: str, field_changed: str = None, old_value: str = None, new_value: str = None) -> bool:
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
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO nc_history (nc_id, user_name, action, field_changed, old_value, new_value)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (nc_id, user_name, action, field_changed, old_value, new_value))
                return True
        except Exception as e:
            print(f"[Erreur] Erreur lors de l'enregistrement de l'historique: {e}")
            return False
    
    def get_nc_history(self, nc_id: int) -> List[Dict[str, Any]]:
        """
        Récupère l'historique complet des modifications d'une NC.
        
        Args:
            nc_id: ID de la NC
        
        Returns:
            Liste des modifications triées par date décroissante
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
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
                        'id': row['id'],
                        'nc_id': row['nc_id'],
                        'user_name': row['user_name'],
                        'action': row['action'],
                        'field_changed': row['field_changed'],
                        'old_value': row['old_value'],
                        'new_value': row['new_value'],
                        'timestamp': row['timestamp']
                    })
                return history
        except sqlite3.OperationalError as e:
            if 'no such table' in str(e):
                # La table n'existe pas encore, retourner liste vide
                print("[Attention] Table nc_history manquante")
                return []
            else:
                raise
    
    # ========================================================================
    # PRÉFÉRENCES UTILISATEUR
    # ========================================================================
    
    def save_user_preference(self, user_id: int, module: str, preference_key: str, preference_value: dict) -> bool:
        """
        Sauvegarde une préférence utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            module: Module concerné ('nc', 'veille', etc.)
            preference_key: Clé de la préférence ('filters', 'view_mode', etc.)
            preference_value: Valeur (dict qui sera converti en JSON)
        
        Returns:
            True si succès, False sinon
        """
        try:
            import json
            value_json = json.dumps(preference_value, ensure_ascii=False)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_preferences (user_id, module, preference_key, preference_value, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id, module, preference_key)
                    DO UPDATE SET preference_value = ?, updated_at = CURRENT_TIMESTAMP
                """, (user_id, module, preference_key, value_json, value_json))
                conn.commit()
                return True
        except Exception as e:
            print(f"[Erreur] Erreur sauvegarde préférence: {e}")
            return False
    
    def get_user_preference(self, user_id: int, module: str, preference_key: str, default=None):
        """
        Récupère une préférence utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            module: Module concerné
            preference_key: Clé de la préférence
            default: Valeur par défaut si non trouvée
        
        Returns:
            Valeur de la préférence (dict) ou default
        """
        try:
            import json
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT preference_value
                    FROM user_preferences
                    WHERE user_id = ? AND module = ? AND preference_key = ?
                """, (user_id, module, preference_key))
                
                row = cursor.fetchone()
                if row:
                    return json.loads(row['preference_value'])
                return default
        except sqlite3.OperationalError as e:
            if 'no such table' in str(e):
                print("[Attention] Table user_preferences manquante")
                return default
            else:
                raise
        except Exception as e:
            print(f"[Erreur] Erreur récupération préférence: {e}")
            return default
    
    # Actions NC
    def add_nc_action(self, nc_id: int, action_type: str, data: Dict[str, Any]) -> int:
        """Ajoute une action à une NC."""
        table = f'nc_actions_{action_type}'  # immediates, correctives, preventives
        data['nc_id'] = nc_id
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'INSERT INTO {table} ({columns}) VALUES ({placeholders})', list(data.values()))
            return cursor.lastrowid
    
    def get_nc_actions(self, nc_id: int, action_type: str = None) -> List[Dict[str, Any]]:
        """Récupère les actions d'une NC."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            results = []
            
            types = [action_type] if action_type else ['immediates', 'correctives', 'preventives']
            
            for t in types:
                cursor.execute(f'''
                    SELECT a.*, u.nom as responsable_nom, '{t}' as action_type
                    FROM nc_actions_{t} a
                    LEFT JOIN users u ON a.responsable_id = u.id
                    WHERE a.nc_id = ?
                    ORDER BY a.created_at
                ''', (nc_id,))
                results.extend([dict(row) for row in cursor.fetchall()])
            
            return results
    
    def update_nc_action(self, action_id: int, action_type: str, data: Dict[str, Any]) -> bool:
        """Met à jour une action."""
        table = f'nc_actions_{action_type}'
        set_clause = ', '.join(f'{k} = ?' for k in data.keys())
        values = list(data.values()) + [action_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE {table} SET {set_clause} WHERE id = ?', values)
            return cursor.rowcount > 0
    
    # ========================================================================
    # VEILLE RÉGLEMENTAIRE
    # ========================================================================
    
    def generate_veille_reference(self) -> str:
        """Génère une référence veille unique."""
        year = datetime.now().year
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT MAX(CAST(SUBSTR(reference, -4) AS INTEGER)) as max_num
                FROM veille_items WHERE reference LIKE ?
            ''', (f'VR-{year}-%',))
            result = cursor.fetchone()
            count = (result['max_num'] or 0) + 1
            return f"VR-{year}-{count:04d}"
    
    def create_veille(self, data: Dict[str, Any]) -> int:
        """Crée un nouvel item de veille."""
        if 'tags' in data and isinstance(data['tags'], list):
            data['tags'] = json.dumps(data['tags'])
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'INSERT INTO veille_items ({columns}) VALUES ({placeholders})', list(data.values()))
            return cursor.lastrowid
    
    def get_all_veille(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Récupère tous les items de veille."""
        query = '''
            SELECT v.*, u.nom as created_by_nom
            FROM veille_items v
            LEFT JOIN users u ON v.created_by = u.id
            WHERE 1=1
        '''
        params = []
        
        if filters:
            if filters.get('type_veille'):
                query += ' AND v.type_veille = ?'
                params.append(filters['type_veille'])
            if filters.get('statut'):
                query += ' AND v.statut = ?'
                params.append(filters['statut'])
            if filters.get('search'):
                query += ' AND (v.titre LIKE ? OR v.description LIKE ?)'
                search = f'%{filters["search"]}%'
                params.extend([search, search])
        
        query += ' ORDER BY v.date_publication DESC'
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = []
            for row in cursor.fetchall():
                item = dict(row)
                if item.get('tags'):
                    try:
                        item['tags'] = json.loads(item['tags'])
                    except:
                        item['tags'] = []
                results.append(item)
            return results
    
    def get_veille(self, veille_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un item de veille."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM veille_items WHERE id = ?', (veille_id,))
            row = cursor.fetchone()
            if row:
                item = dict(row)
                if item.get('tags'):
                    try:
                        item['tags'] = json.loads(item['tags'])
                    except:
                        item['tags'] = []
                return item
            return None
    
    def update_veille(self, veille_id: int, data: Dict[str, Any]) -> bool:
        """Met à jour un item de veille."""
        if 'tags' in data and isinstance(data['tags'], list):
            data['tags'] = json.dumps(data['tags'])
        
        set_clause = ', '.join(f'{k} = ?' for k in data.keys())
        values = list(data.values()) + [veille_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE veille_items SET {set_clause} WHERE id = ?', values)
            return cursor.rowcount > 0
    
    def delete_veille(self, veille_id: int) -> bool:
        """Supprime un item de veille."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM veille_items WHERE id = ?', (veille_id,))
            return cursor.rowcount > 0
    
    # RACI Matrix
    def create_raci(self, veille_id: int, data: Dict[str, Any]) -> int:
        """Crée une entrée RACI."""
        data['veille_id'] = veille_id
        if 'consulted_ids' in data and isinstance(data['consulted_ids'], list):
            data['consulted_ids'] = json.dumps(data['consulted_ids'])
        if 'informed_ids' in data and isinstance(data['informed_ids'], list):
            data['informed_ids'] = json.dumps(data['informed_ids'])
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'INSERT INTO raci_matrix ({columns}) VALUES ({placeholders})', list(data.values()))
            return cursor.lastrowid
    
    def get_raci_for_veille(self, veille_id: int) -> List[Dict[str, Any]]:
        """Récupère les RACI d'un item de veille."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.*, 
                       ur.nom as responsible_nom,
                       ua.nom as accountable_nom
                FROM raci_matrix r
                LEFT JOIN users ur ON r.responsible_id = ur.id
                LEFT JOIN users ua ON r.accountable_id = ua.id
                WHERE r.veille_id = ?
                ORDER BY r.date_butoir
            ''', (veille_id,))
            results = []
            for row in cursor.fetchall():
                item = dict(row)
                for field in ['consulted_ids', 'informed_ids']:
                    if item.get(field):
                        try:
                            item[field] = json.loads(item[field])
                        except:
                            item[field] = []
                # Vérifier le retard
                item['is_late'] = VeilleModel.is_late(item.get('date_butoir'), item.get('progression', 0))
                results.append(item)
            return results
    
    def get_late_raci(self) -> List[Dict[str, Any]]:
        """Récupère les actions RACI en retard."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.*, v.titre as veille_titre, ur.nom as responsible_nom
                FROM raci_matrix r
                JOIN veille_items v ON r.veille_id = v.id
                LEFT JOIN users ur ON r.responsible_id = ur.id
                WHERE r.progression < 100 AND r.date_butoir < date('now')
                ORDER BY r.date_butoir
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def update_raci(self, raci_id: int, data: Dict[str, Any]) -> bool:
        """Met à jour une entrée RACI."""
        if 'consulted_ids' in data and isinstance(data['consulted_ids'], list):
            data['consulted_ids'] = json.dumps(data['consulted_ids'])
        if 'informed_ids' in data and isinstance(data['informed_ids'], list):
            data['informed_ids'] = json.dumps(data['informed_ids'])
        
        set_clause = ', '.join(f'{k} = ?' for k in data.keys())
        values = list(data.values()) + [raci_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE raci_matrix SET {set_clause} WHERE id = ?', values)
            return cursor.rowcount > 0
    
    # ========================================================================
    # INSPECTIONS
    # ========================================================================
    
    def get_all_ateliers(self, actif_only: bool = True) -> List[Dict[str, Any]]:
        """Récupère tous les ateliers."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM ateliers'
            if actif_only:
                query += ' WHERE actif = 1'
            query += ' ORDER BY nom'
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_zones_for_atelier(self, atelier_id: int) -> List[Dict[str, Any]]:
        """Récupère les zones d'un atelier."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM zones WHERE atelier_id = ? AND actif = 1 ORDER BY nom
            ''', (atelier_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_points_controle(self, zone_id: int = None, atelier_id: int = None) -> List[Dict[str, Any]]:
        """Récupère les points de contrôle."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if zone_id:
                cursor.execute('''
                    SELECT pc.*, z.nom as zone_nom
                    FROM points_controle pc
                    JOIN zones z ON pc.zone_id = z.id
                    WHERE pc.zone_id = ? AND pc.actif = 1
                    ORDER BY pc.ordre_affichage, pc.libelle
                ''', (zone_id,))
            elif atelier_id:
                cursor.execute('''
                    SELECT pc.*, z.nom as zone_nom
                    FROM points_controle pc
                    JOIN zones z ON pc.zone_id = z.id
                    WHERE z.atelier_id = ? AND pc.actif = 1
                    ORDER BY z.nom, pc.ordre_affichage, pc.libelle
                ''', (atelier_id,))
            else:
                cursor.execute('''
                    SELECT pc.*, z.nom as zone_nom
                    FROM points_controle pc
                    JOIN zones z ON pc.zone_id = z.id
                    WHERE pc.actif = 1
                    ORDER BY pc.libelle
                ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def generate_inspection_reference(self) -> str:
        """Génère une référence inspection unique."""
        year = datetime.now().year
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT MAX(CAST(SUBSTR(reference, -4) AS INTEGER)) as max_num
                FROM inspection_header WHERE reference LIKE ?
            ''', (f'INS-{year}-%',))
            result = cursor.fetchone()
            count = (result['max_num'] or 0) + 1
            return f"INS-{year}-{count:04d}"
    
    def create_inspection(self, data: Dict[str, Any]) -> int:
        """Crée une nouvelle inspection."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'INSERT INTO inspection_header ({columns}) VALUES ({placeholders})', list(data.values()))
            return cursor.lastrowid
    
    def get_all_inspections(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Récupère toutes les inspections."""
        query = '''
            SELECT i.*, a.nom as atelier_nom, u.nom as inspecteur_nom
            FROM inspection_header i
            JOIN ateliers a ON i.atelier_id = a.id
            LEFT JOIN users u ON i.inspecteur_id = u.id
            WHERE 1=1
        '''
        params = []
        
        if filters:
            if filters.get('atelier_id'):
                query += ' AND i.atelier_id = ?'
                params.append(filters['atelier_id'])
            if filters.get('statut'):
                query += ' AND i.statut = ?'
                params.append(filters['statut'])
        
        query += ' ORDER BY i.date_inspection DESC'
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_inspection(self, inspection_id: int) -> Optional[Dict[str, Any]]:
        """Récupère une inspection."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT i.*, a.nom as atelier_nom
                FROM inspection_header i
                JOIN ateliers a ON i.atelier_id = a.id
                WHERE i.id = ?
            ''', (inspection_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def save_inspection_detail(self, inspection_id: int, point_id: int, data: Dict[str, Any]) -> int:
        """Sauvegarde un détail d'inspection."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Vérifier si existe déjà
            cursor.execute('''
                SELECT id FROM inspection_detail 
                WHERE inspection_id = ? AND point_controle_id = ?
            ''', (inspection_id, point_id))
            existing = cursor.fetchone()
            
            if existing:
                set_clause = ', '.join(f'{k} = ?' for k in data.keys())
                values = list(data.values()) + [existing['id']]
                cursor.execute(f'UPDATE inspection_detail SET {set_clause} WHERE id = ?', values)
                return existing['id']
            else:
                data['inspection_id'] = inspection_id
                data['point_controle_id'] = point_id
                columns = ', '.join(data.keys())
                placeholders = ', '.join('?' * len(data))
                cursor.execute(f'INSERT INTO inspection_detail ({columns}) VALUES ({placeholders})', list(data.values()))
                return cursor.lastrowid
    
    def get_inspection_details(self, inspection_id: int) -> List[Dict[str, Any]]:
        """Récupère les détails d'une inspection."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT d.*, pc.libelle as point_libelle, pc.categorie, pc.criticite
                FROM inspection_detail d
                JOIN points_controle pc ON d.point_controle_id = pc.id
                WHERE d.inspection_id = ?
                ORDER BY pc.ordre_affichage
            ''', (inspection_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_inspection_score(self, inspection_id: int) -> Dict[str, float]:
        """Met à jour et retourne le score d'une inspection."""
        details = self.get_inspection_details(inspection_id)
        score_data = InspectionModel.calculate_score(details)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE inspection_header 
                SET score_total = ?, score_max = ?, pourcentage = ?
                WHERE id = ?
            ''', (score_data['score'], score_data['max'], score_data['percentage'], inspection_id))
        
        return score_data
    
    def get_next_atelier_to_audit(self) -> Optional[Dict[str, Any]]:
        """Retourne le prochain atelier à auditer."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.*, MAX(i.date_inspection) as last_inspection
                FROM ateliers a
                LEFT JOIN inspection_header i ON a.id = i.atelier_id AND i.statut = 'Validée'
                WHERE a.actif = 1
                GROUP BY a.id
                ORDER BY last_inspection ASC NULLS FIRST
                LIMIT 1
            ''')
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ========================================================================
    # LABORATOIRE
    # ========================================================================
    
    def get_all_lab_produits(self) -> List[Dict[str, Any]]:
        """Récupère tous les produits labo."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM lab_produits WHERE actif = 1 ORDER BY nom')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_lab_parametres(self) -> List[Dict[str, Any]]:
        """Récupère tous les paramètres labo."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM lab_parametres WHERE actif = 1 ORDER BY nom')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_parametres_for_produit(self, produit_id: int) -> List[Dict[str, Any]]:
        """Récupère les paramètres avec bornes spécifiques pour un produit."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, 
                       COALESCE(bp.valeur_min, p.valeur_min) as valeur_min,
                       COALESCE(bp.valeur_max, p.valeur_max) as valeur_max,
                       COALESCE(bp.valeur_cible, p.valeur_cible) as valeur_cible
                FROM lab_parametres p
                LEFT JOIN lab_bornes_produit bp ON p.id = bp.parametre_id AND bp.produit_id = ?
                WHERE p.actif = 1
                ORDER BY p.nom
            ''', (produit_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def generate_analysis_reference(self) -> str:
        """Génère une référence analyse unique."""
        year = datetime.now().year
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT MAX(CAST(SUBSTR(reference, -4) AS INTEGER)) as max_num
                FROM lab_analysis WHERE reference LIKE ?
            ''', (f'ANA-{year}-%',))
            result = cursor.fetchone()
            count = (result['max_num'] or 0) + 1
            return f"ANA-{year}-{count:04d}"
    
    def create_lab_analysis(self, data: Dict[str, Any]) -> int:
        """Crée une nouvelle analyse labo."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'INSERT INTO lab_analysis ({columns}) VALUES ({placeholders})', list(data.values()))
            analysis_id = cursor.lastrowid
            
            # Créer événement timeline
            if data.get('lot_numero'):
                self._create_lot_event(cursor, data['lot_numero'], 'Analyse',
                                      f"Analyse créée: {data.get('reference', '')}",
                                      'lab_analysis', analysis_id)
            
            return analysis_id
    
    def get_all_lab_analyses(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Récupère toutes les analyses labo."""
        query = '''
            SELECT a.*, p.nom as produit_nom, u.nom as analyste_nom
            FROM lab_analysis a
            JOIN lab_produits p ON a.produit_id = p.id
            LEFT JOIN users u ON a.analyste_id = u.id
            WHERE 1=1
        '''
        params = []
        
        if filters:
            if filters.get('produit_id'):
                query += ' AND a.produit_id = ?'
                params.append(filters['produit_id'])
            if filters.get('statut'):
                query += ' AND a.statut = ?'
                params.append(filters['statut'])
            if filters.get('lot_numero'):
                query += ' AND a.lot_numero LIKE ?'
                params.append(f'%{filters["lot_numero"]}%')
        
        query += ' ORDER BY a.date_analyse DESC'
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_lab_analysis(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        """Récupère une analyse labo."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.*, p.nom as produit_nom
                FROM lab_analysis a
                JOIN lab_produits p ON a.produit_id = p.id
                WHERE a.id = ?
            ''', (analysis_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def save_lab_result(self, analysis_id: int, parametre_id: int, valeur: float, 
                        valeur_min: float, valeur_max: float) -> int:
        """Sauvegarde un résultat d'analyse."""
        conforme = 1 if LabModel.check_conformity(valeur, valeur_min, valeur_max) else 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Vérifier si existe
            cursor.execute('''
                SELECT id FROM lab_results WHERE analysis_id = ? AND parametre_id = ?
            ''', (analysis_id, parametre_id))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE lab_results SET valeur = ?, conforme = ? WHERE id = ?
                ''', (valeur, conforme, existing['id']))
                return existing['id']
            else:
                cursor.execute('''
                    INSERT INTO lab_results (analysis_id, parametre_id, valeur, conforme)
                    VALUES (?, ?, ?, ?)
                ''', (analysis_id, parametre_id, valeur, conforme))
                return cursor.lastrowid
    
    def get_lab_results(self, analysis_id: int) -> List[Dict[str, Any]]:
        """Récupère les résultats d'une analyse."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.*, p.nom as parametre_nom, p.unite, p.valeur_min, p.valeur_max, p.valeur_cible
                FROM lab_results r
                JOIN lab_parametres p ON r.parametre_id = p.id
                WHERE r.analysis_id = ?
                ORDER BY p.nom
            ''', (analysis_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_analysis_conformity(self, analysis_id: int) -> bool:
        """Met à jour la conformité globale d'une analyse."""
        results = self.get_lab_results(analysis_id)
        if not results:
            return True
        
        conforme = all(r['conforme'] for r in results)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE lab_analysis SET conforme = ? WHERE id = ?', (1 if conforme else 0, analysis_id))
            return conforme
    
    def get_spc_data(self, produit_id: int, parametre_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère les données pour carte de contrôle SPC."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.valeur, a.date_analyse, a.lot_numero,
                       p.valeur_min, p.valeur_max, p.valeur_cible
                FROM lab_results r
                JOIN lab_analysis a ON r.analysis_id = a.id
                JOIN lab_parametres p ON r.parametre_id = p.id
                WHERE a.produit_id = ? AND r.parametre_id = ?
                ORDER BY a.date_analyse DESC
                LIMIT ?
            ''', (produit_id, parametre_id, limit))
            return [dict(row) for row in cursor.fetchall()][::-1]  # Inverser pour ordre chronologique
    
    def get_last_lot_status(self) -> List[Dict[str, Any]]:
        """Récupère le statut des derniers lots analysés."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.lot_numero, a.statut, a.conforme, p.nom as produit_nom, a.date_analyse
                FROM lab_analysis a
                JOIN lab_produits p ON a.produit_id = p.id
                WHERE a.id IN (
                    SELECT MAX(id) FROM lab_analysis GROUP BY lot_numero
                )
                ORDER BY a.date_analyse DESC
                LIMIT 10
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    # ========================================================================
    # TIMELINE & TRAÇABILITÉ
    # ========================================================================
    
    def _create_lot_event(self, cursor, lot_numero: str, type_event: str, titre: str,
                          ref_table: str = None, ref_id: int = None, statut: str = None):
        """Crée un événement dans la timeline d'un lot."""
        cursor.execute('''
            INSERT INTO lot_events (lot_numero, type_event, date_event, titre, reference_table, reference_id, statut)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (lot_numero, type_event, datetime.now(), titre, ref_table, ref_id, statut))
    
    def get_lot_timeline(self, lot_numero: str) -> List[Dict[str, Any]]:
        """Récupère la timeline complète d'un lot."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM lot_events
                WHERE lot_numero = ?
                ORDER BY date_event ASC
            ''', (lot_numero,))
            return [dict(row) for row in cursor.fetchall()]
    
    def search_lot(self, lot_numero: str) -> Dict[str, Any]:
        """Recherche toutes les infos liées à un lot."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            result = {'lot_numero': lot_numero, 'nc': [], 'analyses': [], 'inspections': [], 'timeline': []}
            
            # NC liées
            try:
                cursor.execute('SELECT * FROM nc_header WHERE lot_serie = ?', (lot_numero,))
                result['nc'] = [dict(row) for row in cursor.fetchall()]
            except:
                cursor.execute('SELECT * FROM non_conformites WHERE lot_serie = ?', (lot_numero,))
                result['nc'] = [dict(row) for row in cursor.fetchall()]
            
            # Analyses liées
            cursor.execute('SELECT * FROM lab_analysis WHERE lot_numero = ?', (lot_numero,))
            result['analyses'] = [dict(row) for row in cursor.fetchall()]
            
            # Timeline
            result['timeline'] = self.get_lot_timeline(lot_numero)
            
            return result
    
    # ========================================================================
    # KPI & STATISTIQUES
    # ========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques globales."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            stats = {}
            
            # NC stats - essayer nc_header d'abord
            try:
                cursor.execute('SELECT statut, COUNT(*) as count FROM nc_header GROUP BY statut')
                stats['nc_by_status'] = {row['statut']: row['count'] for row in cursor.fetchall()}
                
                cursor.execute('SELECT COUNT(*) FROM nc_header')
                stats['total'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM nc_header WHERE statut = 'Ouverte'")
                stats['open'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM nc_header WHERE statut = 'En cours'")
                stats['in_progress'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM nc_header WHERE statut = 'Clôturée'")
                stats['resolved'] = cursor.fetchone()[0]
                
                cursor.execute('''
                    SELECT AVG(julianday(date_cloture) - julianday(date_detection)) as avg_days
                    FROM nc_header WHERE date_cloture IS NOT NULL
                ''')
                row = cursor.fetchone()
                stats['avg_resolution_days'] = round(row[0], 1) if row[0] else 0
                
                # Coût total NC
                cursor.execute('SELECT SUM(cout_total) FROM nc_header WHERE cout_total > 0')
                stats['total_nc_cost'] = cursor.fetchone()[0] or 0
                
            except sqlite3.OperationalError:
                # Fallback ancienne table
                cursor.execute('SELECT statut, COUNT(*) as count FROM non_conformites GROUP BY statut')
                stats['nc_by_status'] = {row['statut']: row['count'] for row in cursor.fetchall()}
                
                cursor.execute('SELECT COUNT(*) FROM non_conformites')
                stats['total'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM non_conformites WHERE statut = 'Ouverte'")
                stats['open'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM non_conformites WHERE statut = 'En cours'")
                stats['in_progress'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM non_conformites WHERE statut = 'Clôturée'")
                stats['resolved'] = cursor.fetchone()[0]
                
                stats['avg_resolution_days'] = 0
                stats['total_nc_cost'] = 0
            
            # Veille stats
            try:
                cursor.execute("SELECT COUNT(*) FROM veille_items WHERE statut = 'En cours'")
                stats['veille_en_cours'] = cursor.fetchone()[0]
                
                cursor.execute('''
                    SELECT COUNT(*) FROM raci_matrix 
                    WHERE progression < 100 AND date_butoir < date('now')
                ''')
                stats['raci_late'] = cursor.fetchone()[0]
            except:
                stats['veille_en_cours'] = 0
                stats['raci_late'] = 0
            
            # Inspection stats
            try:
                cursor.execute('''
                    SELECT AVG(pourcentage) FROM inspection_header 
                    WHERE statut = 'Validée' AND date_inspection > date('now', '-30 days')
                ''')
                row = cursor.fetchone()
                stats['avg_inspection_score'] = round(row[0], 1) if row[0] else 0
            except:
                stats['avg_inspection_score'] = 0
            
            # Lab stats
            try:
                cursor.execute('''
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN conforme = 1 THEN 1 ELSE 0 END) as conforme,
                           SUM(CASE WHEN conforme = 0 THEN 1 ELSE 0 END) as non_conforme
                    FROM lab_analysis WHERE date_analyse > date('now', '-30 days')
                ''')
                row = cursor.fetchone()
                stats['lab_total'] = row['total'] or 0
                stats['lab_conforme'] = row['conforme'] or 0
                stats['lab_non_conforme'] = row['non_conforme'] or 0
            except:
                stats['lab_total'] = 0
                stats['lab_conforme'] = 0
                stats['lab_non_conforme'] = 0
            
            return stats
    
    def get_nc_by_month(self, year: int = None) -> List[Dict[str, Any]]:
        """Récupère les NC par mois."""
        year = year or datetime.now().year
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    SELECT strftime('%m', date_detection) as month, COUNT(*) as count
                    FROM nc_header
                    WHERE strftime('%Y', date_detection) = ?
                    GROUP BY month ORDER BY month
                ''', (str(year),))
            except:
                cursor.execute('''
                    SELECT strftime('%m', date_detection) as month, COUNT(*) as count
                    FROM non_conformites
                    WHERE strftime('%Y', date_detection) = ?
                    GROUP BY month ORDER BY month
                ''', (str(year),))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_nc_by_type_and_month(self, year: int = None) -> List[Dict[str, Any]]:
        """Récupère les NC par type et mois (pour heatmap)."""
        year = year or datetime.now().year
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    SELECT type_anomalie, strftime('%m', date_detection) as month, COUNT(*) as count
                    FROM nc_header
                    WHERE strftime('%Y', date_detection) = ? AND type_anomalie IS NOT NULL
                    GROUP BY type_anomalie, month
                ''', (str(year),))
            except:
                cursor.execute('''
                    SELECT type_anomalie, strftime('%m', date_detection) as month, COUNT(*) as count
                    FROM non_conformites
                    WHERE strftime('%Y', date_detection) = ? AND type_anomalie IS NOT NULL
                    GROUP BY type_anomalie, month
                ''', (str(year),))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_quality_costs(self, year: int = None) -> Dict[str, float]:
        """Récupère les coûts qualité."""
        year = year or datetime.now().year
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            costs = {'nc': 0, 'analyses': 0, 'audits': 0, 'prevention': 0, 'total': 0}
            
            # Coût NC
            try:
                cursor.execute('''
                    SELECT SUM(cout_total) FROM nc_header 
                    WHERE strftime('%Y', date_detection) = ?
                ''', (str(year),))
                costs['nc'] = cursor.fetchone()[0] or 0
            except:
                pass
            
            # TODO: Ajouter coûts analyses et audits quand tables complétées
            
            costs['total'] = costs['nc'] + costs['analyses'] + costs['audits'] + costs['prevention']
            return costs
    
    def get_correlation_data(self, year: int = None) -> List[Dict[str, Any]]:
        """Récupère données de corrélation inspections/NC."""
        year = year or datetime.now().year
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            results = []
            for month in range(1, 13):
                month_str = f'{month:02d}'
                
                # Nombre d'inspections
                try:
                    cursor.execute('''
                        SELECT COUNT(*) FROM inspection_header
                        WHERE strftime('%Y', date_inspection) = ? AND strftime('%m', date_inspection) = ?
                    ''', (str(year), month_str))
                    inspections = cursor.fetchone()[0]
                except:
                    inspections = 0
                
                # Nombre de NC
                try:
                    cursor.execute('''
                        SELECT COUNT(*) FROM nc_header
                        WHERE strftime('%Y', date_detection) = ? AND strftime('%m', date_detection) = ?
                    ''', (str(year), month_str))
                    nc_count = cursor.fetchone()[0]
                except:
                    try:
                        cursor.execute('''
                            SELECT COUNT(*) FROM non_conformites
                            WHERE strftime('%Y', date_detection) = ? AND strftime('%m', date_detection) = ?
                        ''', (str(year), month_str))
                        nc_count = cursor.fetchone()[0]
                    except:
                        nc_count = 0
                
                results.append({'month': month, 'inspections': inspections, 'nc': nc_count})
            
            return results
    
    # ========================================================================
    # ANALYSES NC (méthodes existantes pour compatibilité)
    # ========================================================================
    
    def save_analysis(self, nc_id: int, method: str, data: str, user_id: int) -> int:
        """Sauvegarde une analyse NC."""
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
    
    # ========================================================================
    # ADMINISTRATION
    # ========================================================================
    
    def create_atelier(self, code: str, nom: str, description: str = None, responsable_id: int = None) -> int:
        """Crée un nouvel atelier."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ateliers (code, nom, description, responsable_id)
                VALUES (?, ?, ?, ?)
            ''', (code, nom, description, responsable_id))
            return cursor.lastrowid
    
    def create_zone(self, atelier_id: int, code: str, nom: str, description: str = None) -> int:
        """Crée une nouvelle zone."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO zones (atelier_id, code, nom, description)
                VALUES (?, ?, ?, ?)
            ''', (atelier_id, code, nom, description))
            return cursor.lastrowid
    
    def create_point_controle(self, zone_id: int, code: str, libelle: str, 
                               categorie: str = None, criticite: str = 'Standard') -> int:
        """Crée un nouveau point de contrôle."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO points_controle (zone_id, code, libelle, categorie, criticite)
                VALUES (?, ?, ?, ?, ?)
            ''', (zone_id, code, libelle, categorie, criticite))
            return cursor.lastrowid
    
    def create_lab_produit(self, code: str, nom: str, categorie: str = None) -> int:
        """Crée un nouveau produit labo."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO lab_produits (code, nom, categorie)
                VALUES (?, ?, ?)
            ''', (code, nom, categorie))
            return cursor.lastrowid
    
    def create_lab_parametre(self, code: str, nom: str, unite: str = None, 
                              valeur_min: float = None, valeur_max: float = None,
                              valeur_cible: float = None, categorie: str = None) -> int:
        """Crée un nouveau paramètre labo."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO lab_parametres (code, nom, unite, valeur_min, valeur_max, valeur_cible, categorie)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (code, nom, unite, valeur_min, valeur_max, valeur_cible, categorie))
            return cursor.lastrowid
    
    # ========================================================================
    # MÉTHODES SUPPLÉMENTAIRES POUR PAGES UI
    # ========================================================================
    
    def get_inspections_by_status(self, statuts: List[str]) -> List[Dict[str, Any]]:
        """Récupère les inspections par statut."""
        placeholders = ', '.join('?' * len(statuts))
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f'''
                    SELECT i.*, a.nom as atelier_nom, u.nom as inspecteur_nom
                    FROM inspection_header i
                    JOIN ateliers a ON i.atelier_id = a.id
                    LEFT JOIN users u ON i.inspecteur_id = u.id
                    WHERE i.statut IN ({placeholders})
                    ORDER BY i.date_inspection DESC
                ''', statuts)
                return [dict(row) for row in cursor.fetchall()]
            except Exception:
                # Si la table n'existe pas encore, retourner liste vide
                return []
    
    def get_points_controle_for_zone(self, zone_id: int) -> List[Dict[str, Any]]:
        """Récupère les points de contrôle pour une zone."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    SELECT * FROM points_controle 
                    WHERE zone_id = ? AND actif = 1
                    ORDER BY ordre_affichage, libelle
                ''', (zone_id,))
                return [dict(row) for row in cursor.fetchall()]
            except Exception:
                return []
    
    def update_inspection_status(self, inspection_id: int, status: str) -> bool:
        """Met à jour le statut d'une inspection."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('UPDATE inspection_header SET statut = ? WHERE id = ?', 
                              (status, inspection_id))
                return cursor.rowcount > 0
            except Exception:
                return False
    
    def get_analyses_by_status(self, statuts: List[str]) -> List[Dict[str, Any]]:
        """Récupère les analyses labo par statut."""
        placeholders = ', '.join('?' * len(statuts))
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f'''
                    SELECT a.*, p.nom as produit_nom, u.nom as analyste_nom
                    FROM lab_analysis a
                    JOIN lab_produits p ON a.produit_id = p.id
                    LEFT JOIN users u ON a.analyste_id = u.id
                    WHERE a.statut IN ({placeholders})
                    ORDER BY a.date_analyse DESC
                ''', statuts)
                return [dict(row) for row in cursor.fetchall()]
            except Exception:
                return []
    
    def get_analysis(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        """Récupère une analyse par ID."""
        return self.get_lab_analysis(analysis_id)
    
    def get_lab_produit(self, produit_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un produit labo par ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT * FROM lab_produits WHERE id = ?', (produit_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
            except Exception:
                return None
    
    def get_lab_parametre(self, parametre_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un paramètre labo par ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT * FROM lab_parametres WHERE id = ?', (parametre_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
            except Exception:
                return None
    
    def get_analysis_results(self, analysis_id: int) -> List[Dict[str, Any]]:
        """Récupère les résultats d'une analyse."""
        return self.get_lab_results(analysis_id)
    
    def update_lab_analysis(self, analysis_id: int, data: Dict[str, Any]) -> bool:
        """Met à jour une analyse labo."""
        if not data:
            return False
        set_clause = ', '.join(f'{k} = ?' for k in data.keys())
        values = list(data.values()) + [analysis_id]
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f'UPDATE lab_analysis SET {set_clause} WHERE id = ?', values)
                return cursor.rowcount > 0
            except Exception:
                return False
    
    def get_quality_costs_extended(self) -> Dict[str, Any]:
        """Récupère les coûts qualité étendus pour la pyramide."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            costs = {
                'prevention': 0,
                'evaluation': 0,
                'defaillance_interne': 0,
                'defaillance_externe': 0,
            }
            
            # Coûts de défaillance interne (NC internes)
            try:
                cursor.execute('''
                    SELECT SUM(cout_total) FROM nc_header 
                    WHERE source_detection NOT IN ('Client', 'Réclamation')
                    AND cout_total > 0
                ''')
                costs['defaillance_interne'] = cursor.fetchone()[0] or 0
            except:
                pass
            
            # Coûts de défaillance externe (réclamations)
            try:
                cursor.execute('''
                    SELECT SUM(cout_total) FROM nc_header 
                    WHERE source_detection IN ('Client', 'Réclamation')
                    AND cout_total > 0
                ''')
                costs['defaillance_externe'] = cursor.fetchone()[0] or 0
            except:
                pass
            
            # TODO: Ajouter coûts évaluation (analyses) et prévention
            
            return costs
    
    def get_nc_costs_detail(self) -> List[Dict[str, Any]]:
        """Récupère le détail des coûts NC."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    SELECT reference, designation, cout_matiere, heures_mo * 35 as cout_mo,
                           cout_destruction, cout_total
                    FROM nc_header
                    WHERE cout_total > 0
                    ORDER BY cout_total DESC
                    LIMIT 20
                ''')
                return [dict(row) for row in cursor.fetchall()]
            except:
                return []
    
    def get_nc_heatmap_data(self) -> List[List[int]]:
        """Récupère les données pour la heatmap NC."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Initialiser matrice 7 jours x 12 mois
            data = [[0 for _ in range(12)] for _ in range(7)]
            
            try:
                cursor.execute('''
                    SELECT strftime('%w', date_detection) as day_of_week,
                           strftime('%m', date_detection) as month,
                           COUNT(*) as count
                    FROM nc_header
                    WHERE strftime('%Y', date_detection) = strftime('%Y', 'now')
                    GROUP BY day_of_week, month
                ''')
                
                for row in cursor.fetchall():
                    dow = int(row['day_of_week'])  # 0=dimanche, 1=lundi...
                    # Convertir en 0=lundi, 6=dimanche
                    dow = (dow - 1) % 7
                    month = int(row['month']) - 1
                    data[dow][month] = row['count']
            except:
                pass
            
            return data

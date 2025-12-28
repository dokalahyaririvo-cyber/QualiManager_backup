# -*- coding: utf-8 -*-
"""
QualiManager - Module de gestion de l'authentification
Gestion des utilisateurs et des niveaux d'accès
"""

import sqlite3
import hashlib
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

from .db_manager import get_connection

# Niveaux d'accès
ROLE_ADMIN = "Administrateur"
ROLE_RESPONSABLE = "Responsable"
ROLE_UTILISATEUR = "Utilisateur"

# Compte administrateur par défaut
DEFAULT_ADMIN_EMAIL = "admin@qualimanager.local"
DEFAULT_ADMIN_PASSWORD = "Admin@2024!"


def hash_password(password: str) -> str:
    """
    Hash un mot de passe avec SHA-256 et un salt.
    
    Args:
        password: Mot de passe en clair
        
    Returns:
        Hash du mot de passe
    """
    # Utilisation d'un salt fixe pour simplifier (en production, utilisez un salt unique par utilisateur)
    salt = "QualiManager_Salt_2024"
    salted_password = f"{salt}{password}{salt}"
    return hashlib.sha256(salted_password.encode()).hexdigest()


def init_auth_tables():
    """
    Initialise les tables d'authentification.
    Crée la table utilisateurs et le compte admin par défaut.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Création de la table utilisateurs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            mot_de_passe TEXT NOT NULL,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Utilisateur',
            departement TEXT,
            actif INTEGER DEFAULT 1,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_derniere_connexion TIMESTAMP,
            cree_par INTEGER,
            FOREIGN KEY (cree_par) REFERENCES utilisateurs(id)
        )
    """)
    
    # Vérifier si l'admin par défaut existe
    cursor.execute("SELECT id FROM utilisateurs WHERE email = ?", (DEFAULT_ADMIN_EMAIL,))
    if not cursor.fetchone():
        # Créer le compte administrateur par défaut
        cursor.execute("""
            INSERT INTO utilisateurs (email, mot_de_passe, nom, prenom, role, actif)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            DEFAULT_ADMIN_EMAIL,
            hash_password(DEFAULT_ADMIN_PASSWORD),
            "Administrateur",
            "Système",
            ROLE_ADMIN,
            1
        ))
        print(f"✅ Compte administrateur créé : {DEFAULT_ADMIN_EMAIL}")
    
    conn.commit()
    conn.close()
    print("✅ Tables d'authentification initialisées.")


def authentifier(email: str, mot_de_passe: str) -> Optional[Dict[str, Any]]:
    """
    Authentifie un utilisateur.
    
    Args:
        email: Email de l'utilisateur
        mot_de_passe: Mot de passe en clair
        
    Returns:
        Dictionnaire avec les infos utilisateur si authentifié, None sinon
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    hashed = hash_password(mot_de_passe)
    
    cursor.execute("""
        SELECT id, email, nom, prenom, role, departement, actif
        FROM utilisateurs
        WHERE email = ? AND mot_de_passe = ? AND actif = 1
    """, (email, hashed))
    
    row = cursor.fetchone()
    
    if row:
        # Mettre à jour la date de dernière connexion
        cursor.execute("""
            UPDATE utilisateurs 
            SET date_derniere_connexion = ? 
            WHERE id = ?
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), row['id']))
        conn.commit()
        
        user = dict(row)
        conn.close()
        return user
    
    conn.close()
    return None


def creer_utilisateur(
    email: str,
    mot_de_passe: str,
    nom: str,
    prenom: str,
    role: str,
    departement: str = None,
    cree_par: int = None
) -> int:
    """
    Crée un nouvel utilisateur.
    
    Args:
        email: Email unique
        mot_de_passe: Mot de passe en clair
        nom: Nom de famille
        prenom: Prénom
        role: Rôle (Administrateur, Responsable, Utilisateur)
        departement: Département (optionnel)
        cree_par: ID de l'utilisateur créateur
        
    Returns:
        ID du nouvel utilisateur
        
    Raises:
        ValueError: Si l'email existe déjà
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Vérifier si l'email existe déjà
    cursor.execute("SELECT id FROM utilisateurs WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        raise ValueError("Un utilisateur avec cet email existe déjà.")
    
    try:
        cursor.execute("""
            INSERT INTO utilisateurs (email, mot_de_passe, nom, prenom, role, departement, cree_par)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            email,
            hash_password(mot_de_passe),
            nom,
            prenom,
            role,
            departement,
            cree_par
        ))
        conn.commit()
        user_id = cursor.lastrowid
        print(f"✅ Utilisateur {prenom} {nom} créé avec succès (ID: {user_id})")
        return user_id
    finally:
        conn.close()


def modifier_utilisateur(user_id: int, data: Dict[str, Any]) -> bool:
    """
    Modifie un utilisateur existant.
    
    Args:
        user_id: ID de l'utilisateur
        data: Dictionnaire des champs à modifier
        
    Returns:
        True si modifié avec succès
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Si mot de passe fourni, le hasher
    if 'mot_de_passe' in data and data['mot_de_passe']:
        data['mot_de_passe'] = hash_password(data['mot_de_passe'])
    else:
        data.pop('mot_de_passe', None)
    
    if not data:
        return False
    
    set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
    values = list(data.values()) + [user_id]
    
    try:
        cursor.execute(f"UPDATE utilisateurs SET {set_clause} WHERE id = ?", values)
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def supprimer_utilisateur(user_id: int) -> bool:
    """
    Désactive un utilisateur (soft delete).
    
    Args:
        user_id: ID de l'utilisateur
        
    Returns:
        True si désactivé avec succès
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE utilisateurs SET actif = 0 WHERE id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def reactiver_utilisateur(user_id: int) -> bool:
    """
    Réactive un utilisateur désactivé.
    
    Args:
        user_id: ID de l'utilisateur
        
    Returns:
        True si réactivé avec succès
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE utilisateurs SET actif = 1 WHERE id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_all_utilisateurs(include_inactive: bool = False) -> List[Dict[str, Any]]:
    """
    Récupère tous les utilisateurs.
    
    Args:
        include_inactive: Inclure les utilisateurs désactivés
        
    Returns:
        Liste des utilisateurs
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM utilisateurs"
    if not include_inactive:
        query += " WHERE actif = 1"
    query += " ORDER BY nom, prenom"
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_utilisateur_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Récupère un utilisateur par son ID.
    
    Args:
        user_id: ID de l'utilisateur
        
    Returns:
        Dictionnaire utilisateur ou None
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM utilisateurs WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def get_responsables() -> List[Dict[str, Any]]:
    """
    Récupère la liste des responsables (pour les notifications).
    
    Returns:
        Liste des responsables actifs
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, email, nom, prenom, departement
        FROM utilisateurs
        WHERE role IN (?, ?) AND actif = 1
        ORDER BY nom, prenom
    """, (ROLE_ADMIN, ROLE_RESPONSABLE))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def changer_mot_de_passe(user_id: int, ancien_mdp: str, nouveau_mdp: str) -> bool:
    """
    Change le mot de passe d'un utilisateur.
    
    Args:
        user_id: ID de l'utilisateur
        ancien_mdp: Ancien mot de passe
        nouveau_mdp: Nouveau mot de passe
        
    Returns:
        True si changé avec succès
        
    Raises:
        ValueError: Si l'ancien mot de passe est incorrect
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Vérifier l'ancien mot de passe
    cursor.execute(
        "SELECT id FROM utilisateurs WHERE id = ? AND mot_de_passe = ?",
        (user_id, hash_password(ancien_mdp))
    )
    
    if not cursor.fetchone():
        conn.close()
        raise ValueError("Ancien mot de passe incorrect.")
    
    try:
        cursor.execute(
            "UPDATE utilisateurs SET mot_de_passe = ? WHERE id = ?",
            (hash_password(nouveau_mdp), user_id)
        )
        conn.commit()
        return True
    finally:
        conn.close()


# Vérification des permissions
def peut_gerer_comptes(role: str) -> bool:
    """Vérifie si le rôle peut gérer les comptes utilisateurs."""
    return role == ROLE_ADMIN


def peut_enregistrer_nc(role: str) -> bool:
    """Vérifie si le rôle peut enregistrer des NC complètes."""
    return role in (ROLE_ADMIN, ROLE_RESPONSABLE)


def peut_signaler_nc(role: str) -> bool:
    """Vérifie si le rôle peut signaler des NC (formulaire simplifié)."""
    return True  # Tous les rôles peuvent signaler


def peut_voir_rapports(role: str) -> bool:
    """Vérifie si le rôle peut voir les rapports."""
    return True  # Tous les rôles peuvent voir


def peut_modifier_nc(role: str) -> bool:
    """Vérifie si le rôle peut modifier les NC."""
    return role in (ROLE_ADMIN, ROLE_RESPONSABLE)


def peut_solder_nc(role: str) -> bool:
    """Vérifie si le rôle peut solder les NC."""
    return role in (ROLE_ADMIN, ROLE_RESPONSABLE)


class AuthManager:
    """
    Classe de gestion de l'authentification.
    Encapsule les fonctions d'authentification pour une utilisation orientée objet.
    """
    
    def __init__(self):
        """Initialise le gestionnaire d'authentification."""
        init_auth_tables()
    
    def authentifier(self, email: str, mot_de_passe: str) -> tuple:
        """
        Authentifie un utilisateur.
        
        Returns:
            Tuple (success: bool, result: dict ou message d'erreur)
        """
        result = authentifier(email, mot_de_passe)
        if result:
            return True, result
        return False, "Email ou mot de passe incorrect"
    
    def creer_utilisateur(self, email: str, mot_de_passe: str, nom: str, role: str) -> tuple:
        """
        Crée un nouvel utilisateur.
        
        Returns:
            Tuple (success: bool, message)
        """
        try:
            user_id = creer_utilisateur(email, mot_de_passe, nom, "", role)
            return True, f"Utilisateur créé (ID: {user_id})"
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    
    def modifier_utilisateur(self, user_id: int, updates: dict) -> bool:
        """Modifie un utilisateur."""
        return modifier_utilisateur(user_id, updates)
    
    def supprimer_utilisateur(self, user_id: int) -> bool:
        """Supprime (désactive) un utilisateur."""
        return supprimer_utilisateur(user_id)
    
    def get_all_users(self, include_inactive: bool = True) -> list:
        """Récupère tous les utilisateurs."""
        return get_all_utilisateurs(include_inactive)
    
    def get_user_by_id(self, user_id: int) -> dict:
        """Récupère un utilisateur par ID."""
        return get_utilisateur_by_id(user_id)
    
    @staticmethod
    def peut_gerer_comptes(role: str) -> bool:
        """Vérifie si le rôle peut gérer les comptes."""
        return peut_gerer_comptes(role)
    
    @staticmethod
    def peut_enregistrer_nc(role: str) -> bool:
        """Vérifie si le rôle peut enregistrer des NC."""
        return peut_enregistrer_nc(role)

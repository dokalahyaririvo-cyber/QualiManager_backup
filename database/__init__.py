# -*- coding: utf-8 -*-
"""
QualiManager - Module Database
Package d'initialisation pour la gestion de la base de données
"""

from .db_manager import (
    init_database,
    get_connection,
    insert_non_conformite,
    get_all_non_conformites,
    get_non_conformite_by_id,
    update_non_conformite,
    delete_non_conformite,
    get_statistics
)

from .auth_manager import (
    init_auth_tables,
    authentifier,
    creer_utilisateur,
    modifier_utilisateur,
    supprimer_utilisateur,
    reactiver_utilisateur,
    get_all_utilisateurs,
    get_utilisateur_by_id,
    get_responsables,
    changer_mot_de_passe,
    peut_gerer_comptes,
    peut_enregistrer_nc,
    peut_signaler_nc,
    peut_voir_rapports,
    peut_modifier_nc,
    peut_solder_nc,
    ROLE_ADMIN,
    ROLE_RESPONSABLE,
    ROLE_UTILISATEUR,
    DEFAULT_ADMIN_EMAIL,
    DEFAULT_ADMIN_PASSWORD
)

__all__ = [
    # DB Manager
    'init_database',
    'get_connection',
    'insert_non_conformite',
    'get_all_non_conformites',
    'get_non_conformite_by_id',
    'update_non_conformite',
    'delete_non_conformite',
    'get_statistics',
    # Auth Manager
    'init_auth_tables',
    'authentifier',
    'creer_utilisateur',
    'modifier_utilisateur',
    'supprimer_utilisateur',
    'reactiver_utilisateur',
    'get_all_utilisateurs',
    'get_utilisateur_by_id',
    'get_responsables',
    'changer_mot_de_passe',
    'peut_gerer_comptes',
    'peut_enregistrer_nc',
    'peut_signaler_nc',
    'peut_voir_rapports',
    'peut_modifier_nc',
    'peut_solder_nc',
    'ROLE_ADMIN',
    'ROLE_RESPONSABLE',
    'ROLE_UTILISATEUR',
    'DEFAULT_ADMIN_EMAIL',
    'DEFAULT_ADMIN_PASSWORD'
]

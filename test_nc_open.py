"""
Script de test interne pour déboguer l'ouverture des NC
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test des imports
print("Test des imports...")
try:
    import flet as ft
    from flet_app.nc_page import NCPage
    from database.db_manager import get_connection
    print("✅ Tous les imports sont OK\n")
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test de récupération des NC depuis la base
print("Test de récupération des NC...")
try:
    conn = get_connection()
    cursor = conn.cursor()
    
    # D'abord, lister les tables disponibles
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"   Tables disponibles: {[t[0] for t in tables]}")
    
    # Essayer nc_header d'abord
    try:
        cursor.execute("SELECT * FROM nc_header LIMIT 1")
        nc = cursor.fetchone()
        table_name = "nc_header"
    except:
        # Sinon essayer non_conformites
        cursor.execute("SELECT * FROM non_conformites LIMIT 1")
        nc = cursor.fetchone()
        table_name = "non_conformites"
    
    conn.close()
    
    if nc:
        nc_dict = dict(nc)
        print(f"✅ NC trouvée dans la table '{table_name}'")
        print(f"   Colonnes disponibles: {len(nc_dict.keys())} colonnes")
        print(f"   Exemples: {list(nc_dict.keys())[:8]}\n")
    else:
        print("⚠️ Aucune NC dans la base de données\n")
        sys.exit(0)
except Exception as e:
    print(f"❌ ERREUR lors de la récupération: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 50)
print("✅ TESTS DE BASE RÉUSSIS!")
print("Les imports et la base de données fonctionnent.")
print("L'erreur de syntaxe a été corrigée.")
print("=" * 50)

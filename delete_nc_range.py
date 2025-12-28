"""Script pour supprimer les NC avec références de 1973 à 2700"""
import sqlite3
import os

# Chemin vers la base de données
db_path = os.path.join(os.getenv('APPDATA'), 'QualiManager', 'qualimanager_erp.db')

print(f"Connexion à la base de données: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Compter les NC à supprimer
    cursor.execute("""
        SELECT COUNT(*) FROM nc_header 
        WHERE CAST(reference AS INTEGER) >= 1973 
        AND CAST(reference AS INTEGER) <= 2700
    """)
    count = cursor.fetchone()[0]
    
    print(f"\n{count} NC trouvées avec des références entre 1973 et 2700")
    
    if count > 0:
        # Afficher quelques exemples
        cursor.execute("""
            SELECT id, reference, description 
            FROM nc_header 
            WHERE CAST(reference AS INTEGER) >= 1973 
            AND CAST(reference AS INTEGER) <= 2700
            ORDER BY reference
            LIMIT 5
        """)
        
        print("\nExemples de NC à supprimer:")
        for row in cursor.fetchall():
            desc = row[2][:50] if row[2] else "Sans description"
            print(f"  - NC {row[1]}: {desc}...")
        
        # Supprimer automatiquement sans confirmation
        print(f"\n🗑️  Suppression de {count} NC en cours...")
        
        # Supprimer les NC
        cursor.execute("""
            DELETE FROM nc_header 
            WHERE CAST(reference AS INTEGER) >= 1973 
            AND CAST(reference AS INTEGER) <= 2700
        """)
        
        conn.commit()
        print(f"\n✅ {cursor.rowcount} NC supprimées avec succès!")
    else:
        print("\nAucune NC à supprimer dans cette plage")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\nAppuyez sur Entrée pour fermer...")
input()

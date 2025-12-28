import sqlite3

conn = sqlite3.connect('qualimanager_erp.db')
cursor = conn.cursor()

print('\n=== Structure de la table veille_items ===')
cursor.execute('PRAGMA table_info(veille_items)')
columns = cursor.fetchall()
for col in columns:
    null_info = "NOT NULL" if col[3] else "NULL"
    default_info = f"DEFAULT: {col[4]}" if col[4] else ""
    print(f'{col[1]:25} {col[2]:10} {null_info:10} {default_info}')

print('\n\n=== Structure de la table nc_header ===')
cursor.execute('PRAGMA table_info(nc_header)')
columns = cursor.fetchall()
for col in columns:
    null_info = "NOT NULL" if col[3] else "NULL"
    default_info = f"DEFAULT: {col[4]}" if col[4] else ""
    print(f'{col[1]:25} {col[2]:10} {null_info:10} {default_info}')

conn.close()

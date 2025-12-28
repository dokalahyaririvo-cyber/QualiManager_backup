# -*- coding: utf-8 -*-
"""
Script d'import des NC depuis un fichier Excel vers QualiManager
Usage: python import_nc_excel.py chemin_vers_fichier.xlsx
"""

import sys
import sqlite3
import json
from datetime import datetime
from pathlib import Path

# Vérifier si pandas est installé
try:
    import pandas as pd
except ImportError:
    print("❌ Le module pandas n'est pas installé.")
    print("   Installez-le avec: pip install pandas openpyxl")
    sys.exit(1)


class NCImporter:
    """Importeur de NC depuis Excel vers SQLite."""
    
    def __init__(self, db_path: str = "qualimanager_erp.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connexion à la base de données."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        print(f"✅ Connexion à la base: {self.db_path}")
    
    def close(self):
        """Fermeture de la connexion."""
        if self.conn:
            self.conn.close()
            print("✅ Connexion fermée")
    
    def read_excel(self, excel_path: str, sheet_name: str = 0):
        """
        Lit le fichier Excel.
        
        Args:
            excel_path: Chemin vers le fichier Excel
            sheet_name: Nom ou index de la feuille (0 = première feuille)
        
        Returns:
            DataFrame pandas avec les données
        """
        print(f"\n📂 Lecture du fichier: {excel_path}")
        try:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            print(f"✅ {len(df)} lignes trouvées")
            print(f"📋 Colonnes détectées: {', '.join(df.columns)}")
            return df
        except Exception as e:
            print(f"❌ Erreur lecture Excel: {e}")
            sys.exit(1)
    
    def map_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Mappe les colonnes Excel vers les colonnes de la base de données.
        
        IMPORTANT: Adaptez ce mapping selon vos colonnes Excel !
        
        Colonnes possibles dans Excel → Colonnes BDD:
        - Référence / N° NC / Reference → reference
        - Date / Date détection / Date de détection → date_detection
        - Type / Type NC → type_nc
        - Gravité / Criticité → gravite
        - Origine → origine
        - Type anomalie / Anomalie → type_anomalie
        - Catégorie / Catégorie NC → categorie_nc
        - Imputation / Service → imputation
        - Description / Problème → description
        - Produit / Produit concerné → produit_concerne
        - Lot / N° Lot / Série → lot_serie
        - Quantité / Qté affectée → quantite_affectee
        - Matières / Matières réclamées → matieres_reclames
        - Statut / État → statut
        - Cause racine / Cause → cause_racine
        """
        
        # Dictionnaire de mapping (à adapter selon votre Excel)
        column_mapping = {
            # Vos colonnes Excel (à gauche) → Colonnes BDD (à droite)
            'Référence': 'reference',
            'N° NC': 'reference',
            'Reference': 'reference',
            
            'Date': 'date_detection',
            'Date détection': 'date_detection',
            'Date de détection': 'date_detection',
            
            'Type': 'type_nc',
            'Type NC': 'type_nc',
            
            'Gravité': 'gravite',
            'Criticité': 'gravite',
            
            'Origine': 'origine',
            
            'Type anomalie': 'type_anomalie',
            'Anomalie': 'type_anomalie',
            
            'Catégorie': 'categorie_nc',
            'Catégorie NC': 'categorie_nc',
            
            'Imputation': 'imputation',
            'Service': 'imputation',
            
            'Description': 'description',
            'Problème': 'description',
            
            'Produit': 'produit_concerne',
            'Produit concerné': 'produit_concerne',
            
            'Lot': 'lot_serie',
            'N° Lot': 'lot_serie',
            'Série': 'lot_serie',
            
            'Quantité': 'quantite_affectee',
            'Qté affectée': 'quantite_affectee',
            
            'Matières': 'matieres_reclames',
            'Matières réclamées': 'matieres_reclames',
            
            'Statut': 'statut',
            'État': 'statut',
            
            'Cause racine': 'cause_racine',
            'Cause': 'cause_racine',
            
            'Lieu': 'lieu_detection',
            'Lieu détection': 'lieu_detection',
        }
        
        # Renommer les colonnes
        df_renamed = df.rename(columns=column_mapping)
        
        print(f"\n✅ Colonnes après mapping: {', '.join(df_renamed.columns)}")
        
        return df_renamed
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie et formate les données.
        """
        print("\n🧹 Nettoyage des données...")
        
        # Remplacer les valeurs NaN par None ou chaînes vides
        df = df.where(pd.notnull(df), None)
        
        # Formater les dates au format ISO (YYYY-MM-DD)
        if 'date_detection' in df.columns:
            df['date_detection'] = pd.to_datetime(df['date_detection'], errors='coerce')
            df['date_detection'] = df['date_detection'].dt.strftime('%Y-%m-%d')
        
        # Ajouter la date de création
        df['date_creation'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Valeurs par défaut pour les champs obligatoires
        if 'statut' not in df.columns or df['statut'].isna().all():
            df['statut'] = 'En cours'
        
        if 'gravite' not in df.columns:
            df['gravite'] = 'Mineure'
        
        if 'type_nc' not in df.columns:
            df['type_nc'] = 'Interne'
        
        # Convertir quantité en entier
        if 'quantite_affectee' in df.columns:
            df['quantite_affectee'] = pd.to_numeric(df['quantite_affectee'], errors='coerce').fillna(0).astype(int)
        
        print(f"✅ {len(df)} lignes nettoyées")
        
        return df
    
    def generate_reference(self, year: int, count: int) -> str:
        """Génère une référence NC unique."""
        return f"NC-{year}-{count:04d}"
    
    def get_next_reference_number(self, year: int) -> int:
        """Récupère le prochain numéro de référence pour l'année."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT MAX(CAST(SUBSTR(reference, -4) AS INTEGER)) as max_num
            FROM nc_header WHERE reference LIKE ?
        ''', (f'NC-{year}-%',))
        result = cursor.fetchone()
        return (result['max_num'] or 0) + 1
    
    def insert_nc(self, row_data: dict) -> bool:
        """
        Insère une NC dans la base de données.
        
        Args:
            row_data: Dictionnaire avec les données de la ligne
        
        Returns:
            True si succès, False sinon
        """
        try:
            # Générer une référence si absente
            if not row_data.get('reference'):
                year = datetime.now().year
                count = self.get_next_reference_number(year)
                row_data['reference'] = self.generate_reference(year, count)
            
            # Colonnes autorisées (liste des colonnes de nc_header)
            allowed_columns = [
                'reference', 'date_detection', 'date_creation', 'type_nc', 'origine',
                'gravite', 'statut', 'description', 'produit_concerne', 'lot_serie',
                'quantite_affectee', 'lieu_detection', 'type_anomalie', 'categorie_nc',
                'imputation', 'pieces_jointes', 'cause_racine', 'methode_analyse',
                'analyse_5m', 'analyse_portee', 'analyse_details', 'actions_immediates_table',
                'actions_correctives_table', 'matieres_reclames', 'date_cloture',
                'efficacite', 'commentaires_cloture'
            ]
            
            # Filtrer uniquement les colonnes existantes
            filtered_data = {k: v for k, v in row_data.items() if k in allowed_columns and v is not None}
            
            # Construire la requête SQL
            columns = ', '.join(filtered_data.keys())
            placeholders = ', '.join('?' * len(filtered_data))
            values = list(filtered_data.values())
            
            cursor = self.conn.cursor()
            cursor.execute(
                f'INSERT INTO nc_header ({columns}) VALUES ({placeholders})',
                values
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur insertion ligne: {e}")
            print(f"   Données: {row_data}")
            return False
    
    def import_data(self, df: pd.DataFrame, dry_run: bool = False):
        """
        Importe les données dans la base.
        
        Args:
            df: DataFrame pandas avec les données
            dry_run: Si True, simule l'import sans insérer (test)
        """
        print(f"\n{'🔍 SIMULATION' if dry_run else '💾 IMPORT'} de {len(df)} NC...")
        print("=" * 70)
        
        success_count = 0
        error_count = 0
        
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            
            if dry_run:
                # Mode simulation: afficher les 5 premières lignes
                if idx < 5:
                    print(f"\n📋 Ligne {idx + 1}:")
                    for key, value in row_dict.items():
                        if value is not None and value != '':
                            print(f"   {key}: {value}")
            else:
                # Mode réel: insérer dans la BDD
                if self.insert_nc(row_dict):
                    success_count += 1
                    if (idx + 1) % 10 == 0:
                        print(f"   ✅ {idx + 1}/{len(df)} NC importées...")
                else:
                    error_count += 1
        
        if not dry_run:
            self.conn.commit()
            print("\n" + "=" * 70)
            print(f"✅ Import terminé:")
            print(f"   - Succès: {success_count}")
            print(f"   - Erreurs: {error_count}")
        else:
            print("\n" + "=" * 70)
            print(f"ℹ️  Mode simulation - Aucune donnée insérée")
            print(f"   Lancez avec --import pour insérer réellement")


def main():
    """Fonction principale."""
    print("=" * 70)
    print("   IMPORT DE NC DEPUIS EXCEL VERS QUALIMANAGER")
    print("=" * 70)
    
    # Vérifier les arguments
    if len(sys.argv) < 2:
        print("\n❌ Usage: python import_nc_excel.py <fichier.xlsx> [options]")
        print("\nOptions:")
        print("  --dry-run    Simulation sans insertion (test)")
        print("  --import     Import réel dans la base")
        print("  --sheet=X    Nom ou numéro de la feuille (défaut: 0)")
        print("\nExemple:")
        print("  python import_nc_excel.py mes_nc.xlsx --dry-run")
        print("  python import_nc_excel.py mes_nc.xlsx --import")
        print("  python import_nc_excel.py mes_nc.xlsx --import --sheet=Feuille1")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv or '--import' not in sys.argv
    
    # Récupérer le nom de la feuille si spécifié
    sheet_name = 0
    for arg in sys.argv:
        if arg.startswith('--sheet='):
            sheet_value = arg.split('=')[1]
            sheet_name = int(sheet_value) if sheet_value.isdigit() else sheet_value
    
    # Vérifier que le fichier existe
    if not Path(excel_path).exists():
        print(f"❌ Fichier introuvable: {excel_path}")
        sys.exit(1)
    
    # Créer l'importeur
    importer = NCImporter()
    
    try:
        # Connexion BDD
        importer.connect()
        
        # Lire Excel
        df = importer.read_excel(excel_path, sheet_name)
        
        # Mapper les colonnes
        df = importer.map_columns(df)
        
        # Nettoyer les données
        df = importer.clean_data(df)
        
        # Importer
        importer.import_data(df, dry_run=dry_run)
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        importer.close()
    
    print("\n✅ Script terminé")


if __name__ == "__main__":
    main()

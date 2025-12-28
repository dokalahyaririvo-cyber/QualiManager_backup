"""
Script pour créer un fichier Excel modèle pour l'import de NC.
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

def create_template():
    # Créer un nouveau workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Modele Import NC"
    
    # En-têtes
    headers = [
        'Référence', 'Date', 'Statut', 'Type', 'Gravité', 'Origine',
        'Produit', 'Lot', 'Quantité', 'Description', 'Catégorie', 
        'Imputation', 'Responsable', 'Actions', 'Coût'
    ]
    
    # Style d'en-tête
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    # Écrire les en-têtes avec style
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Exemples de données
    examples = [
        [
            'NC-2024-001', '2024-01-15', 'En cours', 'Interne', 'Majeure', 'Production',
            'VIN-ROUGE-A', 'LOT-2024-001', '500', 
            'Problème de qualité détecté sur le lot de production.\nAnalyse en cours pour déterminer la cause.',
            'Qualité produit', 'Cuverie', 'Jean Dupont', 
            'Mise en quarantaine du lot\nAnalyse microbiologique lancée', '1500'
        ],
        [
            'NC-2024-002', '2024-01-16', 'Clôturée', 'Client', 'Mineure', 'Expédition',
            'VIN-BLANC-B', 'LOT-2024-002', '100',
            'Étiquetage incorrect sur certaines bouteilles de la commande client.',
            'Étiquetage', 'Habillage', 'Marie Martin',
            'Ré-étiquetage effectué sur site client\nCompensation commerciale accordée', '300'
        ],
        [
            'NC-2024-003', '2024-01-17', 'En cours', 'Fournisseur', 'Critique', 'Réception',
            'BOUCHONS-LIEGE', 'FOURNISSEUR-BCH-456', '10000',
            'Lot de bouchons non conforme : présence de TCA détectée.\nRisque de goût de bouchon.',
            'Matières premières', 'QSE', 'Pierre Durand',
            'Retour fournisseur en cours\nAudit qualité fournisseur prévu', '5000'
        ]
    ]
    
    for example in examples:
        ws.append(example)
    
    # Appliquer wrap_text aux cellules de description et actions
    for row_num in range(2, len(examples) + 2):
        ws.cell(row=row_num, column=10).alignment = Alignment(wrap_text=True, vertical='top')  # Description
        ws.cell(row=row_num, column=14).alignment = Alignment(wrap_text=True, vertical='top')  # Actions
    
    # Ajuster largeur colonnes
    column_widths = [12, 12, 10, 12, 10, 15, 20, 15, 10, 50, 15, 15, 20, 40, 12]
    for i, width in enumerate(column_widths):
        ws.column_dimensions[chr(65 + i)].width = width
    
    # Ajuster hauteur des lignes avec du texte
    for row_num in range(2, len(examples) + 2):
        ws.row_dimensions[row_num].height = 40
    
    # Sauvegarder
    wb.save('MODELE_IMPORT_NC.xlsx')
    print("✅ Modèle créé avec succès : MODELE_IMPORT_NC.xlsx")
    print(f"   - {len(headers)} colonnes")
    print(f"   - {len(examples)} exemples de NC")
    print("\nVous pouvez maintenant :")
    print("  1. Ouvrir ce fichier dans Excel")
    print("  2. Modifier ou ajouter vos propres NC")
    print("  3. L'importer via l'application (onglet Liste NC > Import > Depuis Excel)")

if __name__ == "__main__":
    create_template()

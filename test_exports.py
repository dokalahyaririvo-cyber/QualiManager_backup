"""
Test des fonctions d'export - Simulation
Ne nécessite pas l'interface Flet complète
"""

import os
import csv
from datetime import datetime

# Données de test
test_ncs = [
    {
        'reference': 'NC-2025-001',
        'date_detection': '2025-01-15',
        'statut': 'En cours',
        'type_nc': 'Interne',
        'gravite': 'Majeure',
        'origine': 'Production',
        'produit_concerne': 'Champagne Brut',
        'description': 'Défaut d\'étiquetage sur lot 12345',
        'categorie_nc': 'Qualité',
        'imputation': 'Habillage',
        'responsable_traitement': 'Jean Dupont',
        'actions_immediates': 'Mise en quarantaine du lot',
        'cout_estime': '2500',
    },
    {
        'reference': 'NC-2025-002',
        'date_detection': '2025-01-18',
        'statut': 'Clôturée',
        'type_nc': 'Client',
        'gravite': 'Mineure',
        'origine': 'Réclamation',
        'produit_concerne': 'Rosé Prestige',
        'description': 'Bouchon défectueux signalé par client',
        'categorie_nc': 'Conditionnement',
        'imputation': 'Fournisseur',
        'responsable_traitement': 'Marie Martin',
        'actions_immediates': 'Remplacement bouteille',
        'cout_estime': '150',
    },
]

def test_csv_export():
    """Test de l'export CSV"""
    try:
        print("\n🔵 Test Export CSV...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_export_nc_{timestamp}.csv"
        filepath = os.path.join(os.path.expanduser('~'), 'Downloads', filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            
            headers = [
                'Référence', 'Date', 'Statut', 'Type', 'Gravité', 'Origine',
                'Produit', 'Description', 'Catégorie', 'Imputation',
                'Responsable', 'Actions', 'Coût'
            ]
            writer.writerow(headers)
            
            for nc in test_ncs:
                row = [
                    nc.get('reference', ''),
                    nc.get('date_detection', ''),
                    nc.get('statut', ''),
                    nc.get('type_nc', ''),
                    nc.get('gravite', ''),
                    nc.get('origine', ''),
                    nc.get('produit_concerne', ''),
                    nc.get('description', ''),
                    nc.get('categorie_nc', ''),
                    nc.get('imputation', ''),
                    nc.get('responsable_traitement', ''),
                    nc.get('actions_immediates', ''),
                    nc.get('cout_estime', ''),
                ]
                writer.writerow(row)
        
        print(f"  ✅ Fichier créé : {filename}")
        print(f"  📂 Emplacement : {filepath}")
        print(f"  📊 {len(test_ncs)} NC exportées")
        return True
        
    except Exception as ex:
        print(f"  ❌ Erreur : {ex}")
        return False

def test_excel_export():
    """Test de l'export Excel"""
    try:
        print("\n📗 Test Export Excel...")
        
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Non-Conformités"
        
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        headers = [
            'Référence', 'Date', 'Statut', 'Type', 'Gravité', 'Origine',
            'Produit', 'Description', 'Catégorie', 'Imputation',
            'Responsable', 'Actions', 'Coût'
        ]
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        for row_num, nc in enumerate(test_ncs, 2):
            ws.cell(row=row_num, column=1, value=nc.get('reference', ''))
            ws.cell(row=row_num, column=2, value=nc.get('date_detection', ''))
            ws.cell(row=row_num, column=3, value=nc.get('statut', ''))
            ws.cell(row=row_num, column=4, value=nc.get('type_nc', ''))
            ws.cell(row=row_num, column=5, value=nc.get('gravite', ''))
            ws.cell(row=row_num, column=6, value=nc.get('origine', ''))
            ws.cell(row=row_num, column=7, value=nc.get('produit_concerne', ''))
            ws.cell(row=row_num, column=8, value=nc.get('description', ''))
            ws.cell(row=row_num, column=9, value=nc.get('categorie_nc', ''))
            ws.cell(row=row_num, column=10, value=nc.get('imputation', ''))
            ws.cell(row=row_num, column=11, value=nc.get('responsable_traitement', ''))
            ws.cell(row=row_num, column=12, value=nc.get('actions_immediates', ''))
            ws.cell(row=row_num, column=13, value=nc.get('cout_estime', ''))
        
        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = min(max_length + 2, 50)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_export_nc_{timestamp}.xlsx"
        filepath = os.path.join(os.path.expanduser('~'), 'Downloads', filename)
        wb.save(filepath)
        
        print(f"  ✅ Fichier créé : {filename}")
        print(f"  📂 Emplacement : {filepath}")
        print(f"  📊 {len(test_ncs)} NC exportées")
        return True
        
    except ImportError:
        print("  ⚠️ openpyxl non disponible - export Excel désactivé")
        return False
    except Exception as ex:
        print(f"  ❌ Erreur : {ex}")
        return False

def test_pdf_export():
    """Test de l'export PDF"""
    try:
        print("\n📕 Test Export PDF...")
        
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_export_nc_{timestamp}.pdf"
        filepath = os.path.join(os.path.expanduser('~'), 'Downloads', filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=landscape(A4))
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#366092'),
            spaceAfter=30,
        )
        
        title = Paragraph(f"Export des Non-Conformités - {datetime.now().strftime('%d/%m/%Y %H:%M')}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        data = [['Réf', 'Date', 'Statut', 'Type', 'Gravité', 'Produit', 'Description']]
        
        for nc in test_ncs:
            desc = nc.get('description', '')
            if len(desc) > 50:
                desc = desc[:47] + '...'
            
            row = [
                nc.get('reference', ''),
                nc.get('date_detection', '')[:10] if nc.get('date_detection') else '',
                nc.get('statut', ''),
                nc.get('type_nc', ''),
                nc.get('gravite', ''),
                nc.get('produit_concerne', '')[:20] if nc.get('produit_concerne') else '',
                desc,
            ]
            data.append(row)
        
        table = Table(data, colWidths=[3*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 4*cm, 7*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        print(f"  ✅ Fichier créé : {filename}")
        print(f"  📂 Emplacement : {filepath}")
        print(f"  📊 {len(test_ncs)} NC exportées")
        return True
        
    except ImportError:
        print("  ⚠️ reportlab non disponible - export PDF désactivé")
        return False
    except Exception as ex:
        print(f"  ❌ Erreur : {ex}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DES EXPORTS - QualiManager NC")
    print("=" * 60)
    
    results = {
        'CSV': test_csv_export(),
        'Excel': test_excel_export(),
        'PDF': test_pdf_export(),
    }
    
    print("\n" + "=" * 60)
    print("RÉSULTATS")
    print("=" * 60)
    
    for format_name, success in results.items():
        status = "✅ OK" if success else "❌ ÉCHEC"
        print(f"{format_name:10} : {status}")
    
    print("\n📂 Vérifiez vos fichiers dans le dossier Téléchargements")
    print("=" * 60)

# -*- coding: utf-8 -*-
"""
Gestionnaire de base de données pour le module Laboratoire
Gestion polymorphe des analyses multi-types
"""

import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from .lab_models import (
    Analyse, TypeAnalyse, Laboratoire, StatutAnalyse, ConclusionAnalyse,
    OenologieStandard, SecuriteAlimentaire, Contaminants, Metrologie,
    Microbiologie, HygieneATP, Phytosanitaire, SeuilsReglementaires
)


class LabDBManager:
    """Gestionnaire de base de données pour les analyses de laboratoire"""
    
    def __init__(self, db_path: str = "qualimanager_erp.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialise les tables nécessaires"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table principale des analyses (polymorphe)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lab_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_prelevement TEXT,
                    date_resultat TEXT,
                    numero_lot TEXT,
                    zone_prelevement TEXT,
                    numero_cuve TEXT,
                    numero_echantillon TEXT,
                    type_analyse TEXT NOT NULL,
                    laboratoire TEXT NOT NULL,
                    cout REAL DEFAULT 0.0,
                    statut TEXT DEFAULT 'Planifié',
                    conclusion TEXT DEFAULT 'En Attente',
                    commentaires TEXT,
                    resultats TEXT,  -- JSON avec les résultats spécifiques
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index pour recherche rapide
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_lab_type 
                ON lab_analyses(type_analyse)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_lab_dates 
                ON lab_analyses(date_prelevement, date_resultat)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_lab_conclusion 
                ON lab_analyses(conclusion)
            """)
            
            conn.commit()
    
    def _serialize_date(self, dt: Optional[datetime]) -> Optional[str]:
        """Convertit datetime en ISO string"""
        return dt.isoformat() if dt else None
    
    def _deserialize_date(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Convertit ISO string en datetime"""
        try:
            return datetime.fromisoformat(dt_str) if dt_str else None
        except:
            return None
    
    def create_analyse(self, analyse: Analyse) -> int:
        """Crée une nouvelle analyse et retourne son ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO lab_analyses (
                    date_prelevement, date_resultat, numero_lot, zone_prelevement,
                    numero_cuve, numero_echantillon, type_analyse, laboratoire,
                    cout, statut, conclusion, commentaires, resultats
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self._serialize_date(analyse.date_prelevement),
                self._serialize_date(analyse.date_resultat),
                analyse.numero_lot,
                analyse.zone_prelevement,
                analyse.numero_cuve,
                analyse.numero_echantillon,
                analyse.type_analyse.value,
                analyse.laboratoire.value,
                analyse.cout,
                analyse.statut.value,
                analyse.conclusion.value,
                analyse.commentaires,
                json.dumps(analyse.resultats, ensure_ascii=False)
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def update_analyse(self, analyse_id: int, analyse: Analyse) -> bool:
        """Met à jour une analyse existante"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE lab_analyses SET
                    date_prelevement = ?,
                    date_resultat = ?,
                    numero_lot = ?,
                    zone_prelevement = ?,
                    numero_cuve = ?,
                    numero_echantillon = ?,
                    type_analyse = ?,
                    laboratoire = ?,
                    cout = ?,
                    statut = ?,
                    conclusion = ?,
                    commentaires = ?,
                    resultats = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                self._serialize_date(analyse.date_prelevement),
                self._serialize_date(analyse.date_resultat),
                analyse.numero_lot,
                analyse.zone_prelevement,
                analyse.numero_cuve,
                analyse.numero_echantillon,
                analyse.type_analyse.value,
                analyse.laboratoire.value,
                analyse.cout,
                analyse.statut.value,
                analyse.conclusion.value,
                analyse.commentaires,
                json.dumps(analyse.resultats, ensure_ascii=False),
                analyse_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_analyse(self, analyse_id: int) -> bool:
        """Supprime une analyse"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM lab_analyses WHERE id = ?", (analyse_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_analyse(self, analyse_id: int) -> Optional[Analyse]:
        """Récupère une analyse par son ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM lab_analyses WHERE id = ?
            """, (analyse_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return self._row_to_analyse(row)
    
    def get_all_analyses(self, 
                         type_analyse: Optional[TypeAnalyse] = None,
                         laboratoire: Optional[Laboratoire] = None,
                         statut: Optional[StatutAnalyse] = None,
                         conclusion: Optional[ConclusionAnalyse] = None,
                         date_debut: Optional[datetime] = None,
                         date_fin: Optional[datetime] = None) -> List[Analyse]:
        """Récupère toutes les analyses avec filtres optionnels"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM lab_analyses WHERE 1=1"
            params = []
            
            if type_analyse:
                query += " AND type_analyse = ?"
                params.append(type_analyse.value)
            
            if laboratoire:
                query += " AND laboratoire = ?"
                params.append(laboratoire.value)
            
            if statut:
                query += " AND statut = ?"
                params.append(statut.value)
            
            if conclusion:
                query += " AND conclusion = ?"
                params.append(conclusion.value)
            
            if date_debut:
                query += " AND date_prelevement >= ?"
                params.append(self._serialize_date(date_debut))
            
            if date_fin:
                query += " AND date_prelevement <= ?"
                params.append(self._serialize_date(date_fin))
            
            query += " ORDER BY date_prelevement DESC, created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [self._row_to_analyse(row) for row in rows]
    
    def _row_to_analyse(self, row: tuple) -> Analyse:
        """Convertit une ligne SQL en objet Analyse"""
        return Analyse(
            id=row[0],
            date_prelevement=self._deserialize_date(row[1]),
            date_resultat=self._deserialize_date(row[2]),
            numero_lot=row[3],
            zone_prelevement=row[4],
            numero_cuve=row[5],
            numero_echantillon=row[6],
            type_analyse=TypeAnalyse(row[7]),
            laboratoire=Laboratoire(row[8]),
            cout=row[9],
            statut=StatutAnalyse(row[10]),
            conclusion=ConclusionAnalyse(row[11]),
            commentaires=row[12],
            resultats=json.loads(row[13]) if row[13] else {},
            created_at=self._deserialize_date(row[14])
        )
    
    def get_statistiques(self) -> Dict[str, Any]:
        """Calcule les statistiques globales du laboratoire"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total analyses
            cursor.execute("SELECT COUNT(*) FROM lab_analyses")
            stats['total_analyses'] = cursor.fetchone()[0]
            
            # Analyses par type
            cursor.execute("""
                SELECT type_analyse, COUNT(*) 
                FROM lab_analyses 
                GROUP BY type_analyse
            """)
            stats['par_type'] = dict(cursor.fetchall())
            
            # Analyses par laboratoire
            cursor.execute("""
                SELECT laboratoire, COUNT(*) 
                FROM lab_analyses 
                GROUP BY laboratoire
            """)
            stats['par_laboratoire'] = dict(cursor.fetchall())
            
            # Analyses par conclusion
            cursor.execute("""
                SELECT conclusion, COUNT(*) 
                FROM lab_analyses 
                GROUP BY conclusion
            """)
            stats['par_conclusion'] = dict(cursor.fetchall())
            
            # Coût total
            cursor.execute("SELECT SUM(cout) FROM lab_analyses")
            stats['cout_total'] = cursor.fetchone()[0] or 0.0
            
            # Coût moyen
            if stats['total_analyses'] > 0:
                stats['cout_moyen'] = stats['cout_total'] / stats['total_analyses']
            else:
                stats['cout_moyen'] = 0.0
            
            # Taux de conformité
            total = stats['total_analyses']
            if total > 0:
                conformes = stats['par_conclusion'].get('Conforme', 0)
                stats['taux_conformite'] = (conformes / total) * 100
            else:
                stats['taux_conformite'] = 0.0
            
            return stats
    
    def get_cout_par_periode(self, annee: int) -> List[Dict[str, Any]]:
        """Récupère les coûts mensuels pour une année"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    strftime('%m', date_prelevement) as mois,
                    SUM(cout) as cout_total,
                    COUNT(*) as nombre_analyses
                FROM lab_analyses
                WHERE strftime('%Y', date_prelevement) = ?
                GROUP BY mois
                ORDER BY mois
            """, (str(annee),))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'mois': int(row[0]),
                    'cout_total': row[1],
                    'nombre_analyses': row[2]
                })
            
            return results
    
    def recherche_texte(self, texte: str) -> List[Analyse]:
        """Recherche textuelle dans tous les champs pertinents"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            recherche = f"%{texte}%"
            
            cursor.execute("""
                SELECT * FROM lab_analyses
                WHERE 
                    numero_lot LIKE ? OR
                    zone_prelevement LIKE ? OR
                    numero_cuve LIKE ? OR
                    numero_echantillon LIKE ? OR
                    commentaires LIKE ? OR
                    laboratoire LIKE ?
                ORDER BY date_prelevement DESC
            """, (recherche, recherche, recherche, recherche, recherche, recherche))
            
            rows = cursor.fetchall()
            return [self._row_to_analyse(row) for row in rows]
    
    def auto_evaluer_conformite(self, analyse_id: int) -> ConclusionAnalyse:
        """Auto-évalue la conformité d'une analyse selon les seuils réglementaires"""
        analyse = self.get_analyse(analyse_id)
        if not analyse:
            return ConclusionAnalyse.EN_ATTENTE
        
        nouvelle_conclusion = SeuilsReglementaires.evaluer_conformite(analyse)
        
        # Mettre à jour en base
        analyse.conclusion = nouvelle_conclusion
        self.update_analyse(analyse_id, analyse)
        
        return nouvelle_conclusion
    
    def get_alertes_actives(self) -> List[Analyse]:
        """Récupère toutes les analyses en alerte ou non conformes"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM lab_analyses
                WHERE conclusion IN ('Non Conforme', 'Alerte')
                ORDER BY date_prelevement DESC
            """)
            
            rows = cursor.fetchall()
            return [self._row_to_analyse(row) for row in rows]
    
    def export_to_excel(self, analyses: List[Analyse], filepath: str):
        """Exporte la liste d'analyses vers Excel"""
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
            
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Analyses Laboratoire"
            
            # En-têtes
            headers = [
                "ID", "Date Prélèvement", "Date Résultat", "Type Analyse",
                "Laboratoire", "No Lot", "No Cuve", "No Échantillon",
                "Statut", "Conclusion", "Coût", "Commentaires"
            ]
            
            # Style en-têtes
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            
            for col, header in enumerate(headers, start=1):
                cell = ws.cell(row=1, column=col)
                cell.value = header
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center")
            
            # Données
            for row_idx, analyse in enumerate(analyses, start=2):
                ws.cell(row=row_idx, column=1).value = analyse.id
                ws.cell(row=row_idx, column=2).value = analyse.date_prelevement.strftime("%d/%m/%Y") if analyse.date_prelevement else ""
                ws.cell(row=row_idx, column=3).value = analyse.date_resultat.strftime("%d/%m/%Y") if analyse.date_resultat else ""
                ws.cell(row=row_idx, column=4).value = analyse.type_analyse.value
                ws.cell(row=row_idx, column=5).value = analyse.laboratoire.value
                ws.cell(row=row_idx, column=6).value = analyse.numero_lot or ""
                ws.cell(row=row_idx, column=7).value = analyse.numero_cuve or ""
                ws.cell(row=row_idx, column=8).value = analyse.numero_echantillon or ""
                ws.cell(row=row_idx, column=9).value = analyse.statut.value
                ws.cell(row=row_idx, column=10).value = analyse.conclusion.value
                ws.cell(row=row_idx, column=11).value = analyse.cout
                ws.cell(row=row_idx, column=12).value = analyse.commentaires or ""
                
                # Couleur selon conclusion
                conclusion_cell = ws.cell(row=row_idx, column=10)
                if analyse.conclusion == ConclusionAnalyse.CONFORME:
                    conclusion_cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                elif analyse.conclusion == ConclusionAnalyse.NON_CONFORME:
                    conclusion_cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
                elif analyse.conclusion == ConclusionAnalyse.ALERTE:
                    conclusion_cell.fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
            
            # Ajuster largeur colonnes
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column].width = adjusted_width
            
            wb.save(filepath)
            return True
        
        except Exception as e:
            print(f"Erreur export Excel: {e}")
            return False

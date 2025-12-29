# -*- coding: utf-8 -*-
"""
Module Laboratoire & Qualité - QualiManager
Gestion des analyses viticoles multi-laboratoires avec polymorphisme
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TypeAnalyse(Enum):
    """Types d'analyses supportés"""
    OENOLOGIE = "Oenologie Standard"
    SECURITE_ALIMENTAIRE = "Sécurité Alimentaire & Allergènes"
    CONTAMINANTS = "Contaminants Spécifiques"
    METROLOGIE = "Métrologie & Conditionnement"
    MICROBIOLOGIE = "Microbiologie"
    HYGIENE_ATP = "Hygiène & Nettoyage (ATP)"
    PHYTOSANITAIRE = "Phytosanitaire (Pesticides)"


class Laboratoire(Enum):
    """Laboratoires partenaires"""
    SOFRALAB = "Sofralab"
    EXACT = "Exact"
    EUROFINS = "Eurofins"
    CEANIA = "Céania"
    DIVERSEY = "Diversey"
    AUTRE = "Autre"


class StatutAnalyse(Enum):
    """Statut de l'analyse"""
    PLANIFIE = "Planifié"
    EN_COURS = "En Cours"
    TERMINE = "Terminé"


class ConclusionAnalyse(Enum):
    """Conclusion de conformité"""
    CONFORME = "Conforme"
    NON_CONFORME = "Non Conforme"
    ALERTE = "Alerte"
    EN_ATTENTE = "En Attente"


@dataclass
class Analyse:
    """Entité mère - Données communes à toutes les analyses"""
    id: Optional[int] = None
    date_prelevement: Optional[datetime] = None
    date_resultat: Optional[datetime] = None
    numero_lot: Optional[str] = None  # Pour analyses sur lot
    zone_prelevement: Optional[str] = None  # Pour analyses d'hygiène
    numero_cuve: Optional[str] = None
    numero_echantillon: Optional[str] = None
    type_analyse: TypeAnalyse = TypeAnalyse.OENOLOGIE
    laboratoire: Laboratoire = Laboratoire.SOFRALAB
    cout: float = 0.0
    statut: StatutAnalyse = StatutAnalyse.PLANIFIE
    conclusion: ConclusionAnalyse = ConclusionAnalyse.EN_ATTENTE
    commentaires: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    # Données spécifiques stockées en JSON
    resultats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OenologieStandard:
    """Résultats d'analyse oenologique (Chimie)"""
    tav: Optional[float] = None  # % vol
    sucres: Optional[float] = None  # g/L
    acidite_totale: Optional[float] = None  # g/L H2SO4
    ph: Optional[float] = None
    acide_volatile: Optional[float] = None  # g/L
    so2_libre: Optional[float] = None  # mg/L
    so2_total: Optional[float] = None  # mg/L
    fer: Optional[float] = None  # mg/L
    cuivre: Optional[float] = None  # mg/L
    co2: Optional[float] = None  # g/L
    surpression: Optional[float] = None  # bars
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class SecuriteAlimentaire:
    """Résultats sécurité alimentaire & allergènes"""
    albumine: Optional[str] = None  # "<LDQ" ou valeur
    caseine: Optional[str] = None
    histamine: Optional[float] = None  # mg/L
    putrescine: Optional[float] = None  # mg/L
    bisphenol_a: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class Contaminants:
    """Résultats contaminants spécifiques (traces)"""
    ochratoxine_a: Optional[float] = None  # ug/kg
    tca: Optional[float] = None  # ng/L (haloanisole)
    teca: Optional[float] = None
    tba: Optional[float] = None
    pca: Optional[float] = None
    tcp: Optional[float] = None  # ng/L (halophénol)
    tbp: Optional[float] = None
    lindane: Optional[float] = None  # mg/kg
    dibutyl_phtalate: Optional[float] = None  # mg/kg
    dehp: Optional[float] = None
    plomb: Optional[float] = None  # mg/L
    cadmium: Optional[float] = None
    arsenic: Optional[float] = None
    mercure: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}
    
    def get_alerte_traces(self) -> List[str]:
        """Retourne la liste des traces détectées mais sous seuil"""
        alertes = []
        
        # Phtalates détectés mais < 0.3 mg/kg
        if self.dibutyl_phtalate and 0 < self.dibutyl_phtalate < 0.3:
            alertes.append(f"DBP détecté ({self.dibutyl_phtalate} mg/kg)")
        
        # TCP ou autres halophénols détectés
        if self.tcp and self.tcp > 0:
            alertes.append(f"TCP détecté ({self.tcp} ng/L)")
        
        return alertes


@dataclass
class Metrologie:
    """Résultats métrologie & conditionnement"""
    volume_net_moyen: Optional[float] = None  # mL
    ecart_type: Optional[float] = None
    nombre_defectueux: int = 0
    densite: Optional[float] = None
    volume_cible: float = 750.0  # mL (375 ou 750 généralement)
    nombre_echantillons: int = 0
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}
    
    def est_conforme(self) -> bool:
        """Évalue la conformité basée sur moyenne et écart-type"""
        if not self.volume_net_moyen or not self.ecart_type:
            return False
        
        # Tolérance : +/-2% du volume cible
        tolerance = self.volume_cible * 0.02
        return abs(self.volume_net_moyen - self.volume_cible) <= tolerance


@dataclass
class Microbiologie:
    """Résultats microbiologie"""
    flore_aerobie_mesophile: Optional[int] = None  # UFC/mL
    levures: Optional[int] = None  # UFC/mL
    moisissures: Optional[int] = None  # UFC/100mL
    unite: str = "UFC/mL"
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class HygieneATP:
    """Résultats hygiène & nettoyage (ATP)"""
    valeur_atp: Optional[float] = None  # RLU
    conductivite: Optional[float] = None  # mS/cm
    concentration_detergent: Optional[float] = None  # %
    nom_produit: Optional[str] = None  # ex: Surefoam
    surface_type: str = "Inox"  # Inox, Plastique, etc.
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}
    
    def get_evaluation_atp(self) -> tuple[str, str]:
        """Retourne (couleur, évaluation) basé sur RLU"""
        if not self.valeur_atp:
            return ("grey", "Non évalué")
        
        if self.surface_type == "Inox":
            if self.valeur_atp < 150:
                return ("green", "Bon")
            elif self.valeur_atp < 200:
                return ("orange", "À surveiller")
            else:
                return ("red", "Mauvais")
        else:
            # Seuils plus élevés pour autres surfaces
            if self.valeur_atp < 250:
                return ("green", "Bon")
            elif self.valeur_atp < 350:
                return ("orange", "À surveiller")
            else:
                return ("red", "Mauvais")


@dataclass
class Phytosanitaire:
    """Résultats phytosanitaire (pesticides)"""
    molecules_detectees: Dict[str, float] = field(default_factory=dict)  # {nom_molecule: teneur mg/kg}
    global_resultat: str = "Non Détecté"  # Si rien détecté
    
    def to_dict(self) -> Dict:
        return {
            "molecules_detectees": self.molecules_detectees,
            "global_resultat": self.global_resultat,
            "nombre_molecules": len(self.molecules_detectees)
        }
    
    def ajouter_molecule(self, nom: str, teneur: float):
        """Ajoute une molécule détectée"""
        self.molecules_detectees[nom] = teneur
        if self.molecules_detectees:
            self.global_resultat = f"{len(self.molecules_detectees)} molécule(s) détectée(s)"


# Seuils réglementaires (hardcoded rules)
class SeuilsReglementaires:
    """Seuils réglementaires pour auto-évaluation"""
    
    # Phtalates
    DBP_ROUGE = 0.3  # mg/kg
    
    # Métaux lourds
    PLOMB_ROUGE = 0.10  # mg/L
    CADMIUM_ROUGE = 0.01  # mg/L
    ARSENIC_ROUGE = 0.20  # mg/L
    MERCURE_ROUGE = 0.05  # mg/L
    
    # Ochratoxine A
    OCHRATOXINE_ROUGE = 2.0  # ug/kg
    
    # ATP (Inox)
    ATP_BON = 150  # RLU
    ATP_MOYEN = 200  # RLU
    
    @staticmethod
    def evaluer_conformite(analyse: Analyse) -> ConclusionAnalyse:
        """Évalue automatiquement la conformité selon le type d'analyse"""
        type_analyse = analyse.type_analyse
        resultats = analyse.resultats
        
        if type_analyse == TypeAnalyse.CONTAMINANTS:
            # Vérifier phtalates
            if resultats.get('dibutyl_phtalate', 0) > SeuilsReglementaires.DBP_ROUGE:
                return ConclusionAnalyse.NON_CONFORME
            
            # Vérifier métaux lourds
            if resultats.get('plomb', 0) > SeuilsReglementaires.PLOMB_ROUGE:
                return ConclusionAnalyse.NON_CONFORME
            
            # Vérifier ochratoxine
            if resultats.get('ochratoxine_a', 0) > SeuilsReglementaires.OCHRATOXINE_ROUGE:
                return ConclusionAnalyse.NON_CONFORME
            
            # Alertes traces
            if any(v > 0 for k, v in resultats.items() if isinstance(v, (int, float))):
                return ConclusionAnalyse.ALERTE
        
        elif type_analyse == TypeAnalyse.HYGIENE_ATP:
            atp = resultats.get('valeur_atp', 0)
            if atp > SeuilsReglementaires.ATP_MOYEN:
                return ConclusionAnalyse.NON_CONFORME
            elif atp > SeuilsReglementaires.ATP_BON:
                return ConclusionAnalyse.ALERTE
        
        elif type_analyse == TypeAnalyse.METROLOGIE:
            volume_moyen = resultats.get('volume_net_moyen', 0)
            volume_cible = resultats.get('volume_cible', 750)
            tolerance = volume_cible * 0.02
            
            if abs(volume_moyen - volume_cible) > tolerance:
                return ConclusionAnalyse.NON_CONFORME
        
        return ConclusionAnalyse.CONFORME

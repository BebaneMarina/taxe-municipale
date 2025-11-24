"""
Modèles SQLAlchemy pour la base de données PostgreSQL
Application de Collecte de Taxe Municipale - Mairie de Libreville
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, Text, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
from geoalchemy2 import Geometry

Base = declarative_base()


class TypeContribuableEnum(str, enum.Enum):
    """Types de contribuables"""
    PARTICULIER = "particulier"
    ENTREPRISE = "entreprise"
    COMMERCE = "commerce"
    AUTRE = "autre"


class StatutCollecteurEnum(str, enum.Enum):
    """Statut administratif du collecteur"""
    ACTIVE = "active"
    DESACTIVE = "desactive"


class EtatCollecteurEnum(str, enum.Enum):
    """État technique du collecteur"""
    CONNECTE = "connecte"
    DECONNECTE = "deconnecte"


class StatutCollecteEnum(str, enum.Enum):
    """Statut d'une collecte"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TypePaiementEnum(str, enum.Enum):
    """Type de paiement"""
    ESPECES = "especes"
    MOBILE_MONEY = "mobile_money"
    CARTE = "carte"


class PeriodiciteEnum(str, enum.Enum):
    """Périodicité de collecte"""
    JOURNALIERE = "journaliere"
    HEBDOMADAIRE = "hebdomadaire"
    MENSUELLE = "mensuelle"
    TRIMESTRIELLE = "trimestrielle"


# ==================== TABLE SERVICE ====================
class Service(Base):
    """Services de la mairie"""
    __tablename__ = "service"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    code = Column(String(20), unique=True, nullable=False)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    taxes = relationship("Taxe", back_populates="service")


# ==================== TABLE TYPE_TAXE ====================
class TypeTaxe(Base):
    """Types de taxes (ex: Taxe de marché, Taxe d'occupation, etc.)"""
    __tablename__ = "type_taxe"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False, unique=True)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    taxes = relationship("Taxe", back_populates="type_taxe")


# ==================== TABLE ZONE ====================
class Zone(Base):
    """Zones géographiques de Libreville"""
    __tablename__ = "zone"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    quartiers = relationship("Quartier", back_populates="zone")


# ==================== TABLE QUARTIER ====================
class Quartier(Base):
    """Quartiers de Libreville"""
    __tablename__ = "quartier"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    zone_id = Column(Integer, ForeignKey("zone.id"), nullable=False)
    description = Column(Text, nullable=True)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    zone = relationship("Zone", back_populates="quartiers")
    contribuables = relationship("Contribuable", back_populates="quartier")


# ==================== TABLE TYPE_CONTRIBUABLE ====================
class TypeContribuable(Base):
    """Types de contribuables"""
    __tablename__ = "type_contribuable"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(50), nullable=False, unique=True)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    contribuables = relationship("Contribuable", back_populates="type_contribuable")


# ==================== TABLE COLLECTEUR ====================
class Collecteur(Base):
    """Collecteurs de taxes"""
    __tablename__ = "collecteur"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    telephone = Column(String(20), unique=True, nullable=False)
    matricule = Column(String(50), unique=True, nullable=False, index=True)
    statut = Column(Enum(StatutCollecteurEnum, name='statut_collecteur_enum', create_type=False, values_callable=lambda x: [e.value for e in StatutCollecteurEnum]), default=StatutCollecteurEnum.ACTIVE)
    etat = Column(Enum(EtatCollecteurEnum, name='etat_collecteur_enum', create_type=False, values_callable=lambda x: [e.value for e in EtatCollecteurEnum]), default=EtatCollecteurEnum.DECONNECTE)
    zone_id = Column(Integer, ForeignKey("zone.id"), nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)  # Position GPS actuelle
    longitude = Column(Numeric(11, 8), nullable=True)  # Position GPS actuelle
    geom = Column(Geometry(geometry_type='POINT', srid=4326), nullable=True)
    date_derniere_connexion = Column(DateTime, nullable=True)
    date_derniere_deconnexion = Column(DateTime, nullable=True)
    heure_cloture = Column(String(5), nullable=True)  # Format HH:MM
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    zone = relationship("Zone")
    contribuables = relationship("Contribuable", back_populates="collecteur")
    collectes = relationship("InfoCollecte", back_populates="collecteur")
    dossiers_impayes = relationship("DossierImpaye", back_populates="collecteur")


# ==================== TABLE CONTRIBUABLE ====================
class Contribuable(Base):
    """Contribuables (clients)"""
    __tablename__ = "contribuable"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True, unique=True, index=True)
    telephone = Column(String(20), nullable=False, unique=True, index=True)
    type_contribuable_id = Column(Integer, ForeignKey("type_contribuable.id"), nullable=False)
    quartier_id = Column(Integer, ForeignKey("quartier.id"), nullable=False)
    collecteur_id = Column(Integer, ForeignKey("collecteur.id"), nullable=False)
    adresse = Column(Text, nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)  # Géolocalisation
    longitude = Column(Numeric(11, 8), nullable=True)  # Géolocalisation
    geom = Column(Geometry(geometry_type='POINT', srid=4326), nullable=True)
    nom_activite = Column(String(200), nullable=True)  # Nom de l'activité/commerce
    photo_url = Column(String(500), nullable=True)  # URL de la photo du lieu
    numero_identification = Column(String(50), unique=True, nullable=True, index=True)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    type_contribuable = relationship("TypeContribuable", back_populates="contribuables")
    quartier = relationship("Quartier", back_populates="contribuables")
    collecteur = relationship("Collecteur", back_populates="contribuables")
    affectations_taxes = relationship("AffectationTaxe", back_populates="contribuable")
    collectes = relationship("InfoCollecte", back_populates="contribuable")
    relances = relationship("Relance", back_populates="contribuable")
    dossiers_impayes = relationship("DossierImpaye", back_populates="contribuable")


# ==================== TABLE TAXE ====================
class Taxe(Base):
    """Taxes municipales"""
    __tablename__ = "taxe"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    montant = Column(Numeric(12, 2), nullable=False)
    montant_variable = Column(Boolean, default=False)  # True si montant peut varier
    periodicite = Column(Enum(PeriodiciteEnum, name='periodicite_enum', create_type=False, values_callable=lambda x: [e.value for e in PeriodiciteEnum]), nullable=False)
    type_taxe_id = Column(Integer, ForeignKey("type_taxe.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("service.id"), nullable=False)
    commission_pourcentage = Column(Numeric(5, 2), default=0.00)  # Commission sur collecte
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    type_taxe = relationship("TypeTaxe", back_populates="taxes")
    service = relationship("Service", back_populates="taxes")
    affectations_taxes = relationship("AffectationTaxe", back_populates="taxe")
    collectes = relationship("InfoCollecte", back_populates="taxe")


# ==================== TABLE AFFECTATION_TAXE ====================
class AffectationTaxe(Base):
    """Affectation d'une taxe à un contribuable"""
    __tablename__ = "affectation_taxe"
    
    id = Column(Integer, primary_key=True, index=True)
    contribuable_id = Column(Integer, ForeignKey("contribuable.id"), nullable=False)
    taxe_id = Column(Integer, ForeignKey("taxe.id"), nullable=False)
    date_debut = Column(DateTime, nullable=False)
    date_fin = Column(DateTime, nullable=True)  # NULL si toujours active
    montant_custom = Column(Numeric(12, 2), nullable=True)  # Montant personnalisé si variable
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    contribuable = relationship("Contribuable", back_populates="affectations_taxes")
    taxe = relationship("Taxe", back_populates="affectations_taxes")
    relances = relationship("Relance", back_populates="affectation_taxe")
    dossiers_impayes = relationship("DossierImpaye", back_populates="affectation_taxe")


# ==================== TABLE INFO_COLLECTE ====================
class InfoCollecte(Base):
    """Informations sur les collectes effectuées"""
    __tablename__ = "info_collecte"
    
    id = Column(Integer, primary_key=True, index=True)
    contribuable_id = Column(Integer, ForeignKey("contribuable.id"), nullable=False)
    taxe_id = Column(Integer, ForeignKey("taxe.id"), nullable=False)
    collecteur_id = Column(Integer, ForeignKey("collecteur.id"), nullable=False)
    montant = Column(Numeric(12, 2), nullable=False)
    commission = Column(Numeric(12, 2), default=0.00)
    type_paiement = Column(Enum(TypePaiementEnum, name='type_paiement_enum', create_type=False, values_callable=lambda x: [e.value for e in TypePaiementEnum]), nullable=False)
    statut = Column(Enum(StatutCollecteEnum, name='statut_collecte_enum', create_type=False, values_callable=lambda x: [e.value for e in StatutCollecteEnum]), default=StatutCollecteEnum.PENDING)
    reference = Column(String(50), unique=True, nullable=False, index=True)
    billetage = Column(Text, nullable=True)  # JSON: {"5000": 5, "1000": 10}
    date_collecte = Column(DateTime, nullable=False, default=datetime.utcnow)
    date_cloture = Column(DateTime, nullable=True)  # Date de clôture de journée
    sms_envoye = Column(Boolean, default=False)
    ticket_imprime = Column(Boolean, default=False)
    annule = Column(Boolean, default=False)
    raison_annulation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    contribuable = relationship("Contribuable", back_populates="collectes")
    taxe = relationship("Taxe", back_populates="collectes")
    collecteur = relationship("Collecteur", back_populates="collectes")


# ==================== TABLE ZONE_GEOGRAPHIQUE ====================
class ZoneGeographique(Base):
    """Zones géographiques fiscales (polygones GeoJSON)"""
    __tablename__ = "zone_geographique"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    type_zone = Column(String(50), nullable=False)  # 'quartier', 'arrondissement', 'secteur'
    code = Column(String(50), unique=True, nullable=True, index=True)
    geometry = Column(JSON, nullable=False)  # GeoJSON geometry (Polygon ou MultiPolygon)
    properties = Column(JSON, nullable=True)  # Propriétés additionnelles
    quartier_id = Column(Integer, ForeignKey("quartier.id"), nullable=True)
    geom = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=True)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    quartier = relationship("Quartier")


# ==================== TABLE UTILISATEUR ====================
class RoleEnum(str, enum.Enum):
    """Rôles utilisateurs"""
    ADMIN = "admin"
    AGENT_BACK_OFFICE = "agent_back_office"
    AGENT_FRONT_OFFICE = "agent_front_office"
    CONTROLEUR_INTERNE = "controleur_interne"
    COLLECTEUR = "collecteur"


class Utilisateur(Base):
    """Utilisateurs du système (authentification)"""
    __tablename__ = "utilisateur"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    telephone = Column(String(20), unique=True, nullable=True)
    mot_de_passe_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum, name='role_enum', create_type=False, values_callable=lambda x: [e.value for e in RoleEnum]), nullable=False, default=RoleEnum.AGENT_BACK_OFFICE)
    actif = Column(Boolean, default=True)
    derniere_connexion = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==================== ENUMS POUR RELANCES ====================
class TypeRelanceEnum(str, enum.Enum):
    """Types de relances"""
    SMS = "sms"
    EMAIL = "email"
    APPEL = "appel"
    COURRIER = "courrier"
    VISITE = "visite"


class StatutRelanceEnum(str, enum.Enum):
    """Statut d'une relance"""
    EN_ATTENTE = "en_attente"
    ENVOYEE = "envoyee"
    ECHEC = "echec"
    ANNULEE = "annulee"


# ==================== TABLE RELANCE ====================
class Relance(Base):
    """Historique des relances envoyées aux contribuables"""
    __tablename__ = "relance"
    
    id = Column(Integer, primary_key=True, index=True)
    contribuable_id = Column(Integer, ForeignKey("contribuable.id"), nullable=False)
    affectation_taxe_id = Column(Integer, ForeignKey("affectation_taxe.id"), nullable=True)
    type_relance = Column(Enum(TypeRelanceEnum, name='type_relance_enum', create_type=False, values_callable=lambda x: [e.value for e in TypeRelanceEnum]), nullable=False)
    statut = Column(Enum(StatutRelanceEnum, name='statut_relance_enum', create_type=False, values_callable=lambda x: [e.value for e in StatutRelanceEnum]), default=StatutRelanceEnum.EN_ATTENTE)
    message = Column(Text, nullable=True)
    montant_due = Column(Numeric(12, 2), nullable=False)
    date_echeance = Column(DateTime, nullable=True)
    date_envoi = Column(DateTime, nullable=True)
    date_planifiee = Column(DateTime, nullable=False)
    canal_envoi = Column(String(100), nullable=True)
    reponse_recue = Column(Boolean, default=False)
    date_reponse = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateur.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    contribuable = relationship("Contribuable", back_populates="relances")
    affectation_taxe = relationship("AffectationTaxe", back_populates="relances")
    utilisateur = relationship("Utilisateur")


# ==================== TABLE DOSSIER_IMPAYE ====================
class StatutTransactionEnum(str, enum.Enum):
    """Statut d'une transaction de paiement"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class TransactionBambooPay(Base):
    """Transactions de paiement via BambooPay"""
    __tablename__ = "transaction_bamboopay"
    
    id = Column(Integer, primary_key=True, index=True)
    contribuable_id = Column(Integer, ForeignKey("contribuable.id"), nullable=True)  # Optionnel si paiement sans compte
    affectation_taxe_id = Column(Integer, ForeignKey("affectation_taxe.id"), nullable=True)  # Optionnel
    taxe_id = Column(Integer, ForeignKey("taxe.id"), nullable=True)  # Pour paiement direct d'une taxe
    
    # Informations du payeur
    payer_name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False)
    matricule = Column(String(50), nullable=True)
    raison_sociale = Column(String(200), nullable=True)
    
    # Informations de transaction
    billing_id = Column(String(100), unique=True, nullable=False, index=True)  # ID facture côté marchand
    transaction_amount = Column(Numeric(12, 2), nullable=False)
    reference_bp = Column(String(100), nullable=True, index=True)  # Référence BambooPay
    transaction_id = Column(String(100), nullable=True, index=True)  # ID transaction BambooPay
    
    # Statut
    statut = Column(Enum(StatutTransactionEnum, name='statut_transaction_enum', create_type=False, values_callable=lambda x: [e.value for e in StatutTransactionEnum]), default=StatutTransactionEnum.PENDING)
    statut_message = Column(Text, nullable=True)
    
    # URLs
    return_url = Column(String(500), nullable=True)
    callback_url = Column(String(500), nullable=True)
    
    # Métadonnées
    operateur = Column(String(50), nullable=True)  # moov_money, airtel_money, etc.
    payment_method = Column(String(50), nullable=True)  # web, mobile_instant
    metadata_json = Column(JSON, nullable=True)  # Données additionnelles (renommé car 'metadata' est réservé dans SQLAlchemy)
    
    # Dates
    date_initiation = Column(DateTime, default=datetime.utcnow)
    date_paiement = Column(DateTime, nullable=True)
    date_callback = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    contribuable = relationship("Contribuable")
    affectation_taxe = relationship("AffectationTaxe")
    taxe = relationship("Taxe")


class DossierImpaye(Base):
    """Dossiers d'impayés pour suivi et recouvrement"""
    __tablename__ = "dossier_impaye"
    
    id = Column(Integer, primary_key=True, index=True)
    contribuable_id = Column(Integer, ForeignKey("contribuable.id"), nullable=False)
    affectation_taxe_id = Column(Integer, ForeignKey("affectation_taxe.id"), nullable=False)
    montant_initial = Column(Numeric(12, 2), nullable=False)
    montant_paye = Column(Numeric(12, 2), default=0.00)
    montant_restant = Column(Numeric(12, 2), nullable=False)
    penalites = Column(Numeric(12, 2), default=0.00)
    date_echeance = Column(DateTime, nullable=False)
    jours_retard = Column(Integer, default=0)
    statut = Column(String(50), default="en_cours")  # en_cours, partiellement_paye, paye, archive
    priorite = Column(String(20), default="normale")  # faible, normale, elevee, urgente
    dernier_contact = Column(DateTime, nullable=True)
    nombre_relances = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    assigne_a = Column(Integer, ForeignKey("collecteur.id"), nullable=True)
    date_assignation = Column(DateTime, nullable=True)
    date_cloture = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    contribuable = relationship("Contribuable", back_populates="dossiers_impayes")
    affectation_taxe = relationship("AffectationTaxe", back_populates="dossiers_impayes")
    collecteur = relationship("Collecteur", back_populates="dossiers_impayes")

"""
Modèles supplémentaires pour les relances et impayés
À ajouter dans models.py
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Numeric, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# Ajouter ces classes dans models.py après les autres modèles

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


class Relance(Base):
    """Historique des relances envoyées aux contribuables"""
    __tablename__ = "relance"
    
    id = Column(Integer, primary_key=True, index=True)
    contribuable_id = Column(Integer, ForeignKey("contribuable.id"), nullable=False)
    affectation_taxe_id = Column(Integer, ForeignKey("affectation_taxe.id"), nullable=True)  # NULL si relance générale
    type_relance = Column(Enum(TypeRelanceEnum, name='type_relance_enum', create_type=False, values_callable=lambda x: [e.value for e in TypeRelanceEnum]), nullable=False)
    statut = Column(Enum(StatutRelanceEnum, name='statut_relance_enum', create_type=False, values_callable=lambda x: [e.value for e in StatutRelanceEnum]), default=StatutRelanceEnum.EN_ATTENTE)
    message = Column(Text, nullable=True)  # Contenu du message envoyé
    montant_due = Column(Numeric(12, 2), nullable=False)  # Montant dû au moment de la relance
    date_echeance = Column(DateTime, nullable=True)  # Date d'échéance de la taxe
    date_envoi = Column(DateTime, nullable=True)  # Date d'envoi effectif
    date_planifiee = Column(DateTime, nullable=False)  # Date planifiée pour l'envoi
    canal_envoi = Column(String(100), nullable=True)  # Email, téléphone, etc.
    reponse_recue = Column(Boolean, default=False)  # Le contribuable a-t-il réagi ?
    date_reponse = Column(DateTime, nullable=True)  # Date de réponse/paiement après relance
    notes = Column(Text, nullable=True)  # Notes additionnelles
    utilisateur_id = Column(Integer, ForeignKey("utilisateur.id"), nullable=True)  # Qui a créé la relance
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    contribuable = relationship("Contribuable", back_populates="relances")
    affectation_taxe = relationship("AffectationTaxe", back_populates="relances")
    utilisateur = relationship("Utilisateur")


class DossierImpaye(Base):
    """Dossiers d'impayés pour suivi et recouvrement"""
    __tablename__ = "dossier_impaye"
    
    id = Column(Integer, primary_key=True, index=True)
    contribuable_id = Column(Integer, ForeignKey("contribuable.id"), nullable=False)
    affectation_taxe_id = Column(Integer, ForeignKey("affectation_taxe.id"), nullable=False)
    montant_initial = Column(Numeric(12, 2), nullable=False)  # Montant initial dû
    montant_paye = Column(Numeric(12, 2), default=0.00)  # Montant déjà payé
    montant_restant = Column(Numeric(12, 2), nullable=False)  # Montant restant à payer
    penalites = Column(Numeric(12, 2), default=0.00)  # Pénalités de retard
    date_echeance = Column(DateTime, nullable=False)  # Date d'échéance initiale
    jours_retard = Column(Integer, default=0)  # Nombre de jours de retard
    statut = Column(String(50), default="en_cours")  # en_cours, partiellement_paye, paye, archive
    priorite = Column(String(20), default="normale")  # faible, normale, elevee, urgente
    dernier_contact = Column(DateTime, nullable=True)  # Date du dernier contact
    nombre_relances = Column(Integer, default=0)  # Nombre de relances envoyées
    notes = Column(Text, nullable=True)  # Notes sur le dossier
    assigne_a = Column(Integer, ForeignKey("collecteur.id"), nullable=True)  # Collecteur assigné au recouvrement
    date_assignation = Column(DateTime, nullable=True)
    date_cloture = Column(DateTime, nullable=True)  # Date de clôture du dossier
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    contribuable = relationship("Contribuable", back_populates="dossiers_impayes")
    affectation_taxe = relationship("AffectationTaxe", back_populates="dossiers_impayes")
    collecteur = relationship("Collecteur", back_populates="dossiers_impayes")


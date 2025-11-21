"""
Router pour le paramétrage du système
Gestion des rôles, divisions administratives et secteurs d'activité
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db
from database.models import Utilisateur, RoleEnum
from auth.security import get_current_active_user, require_role
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from geoalchemy2 import Geometry

router = APIRouter(prefix="/api/parametrage", tags=["Paramétrage"])

# ==================== MODÈLES POUR PARAMÉTRAGE ====================
# Ces modèles seront ajoutés à database/models.py si nécessaire
# Pour l'instant, on utilise des modèles temporaires dans ce fichier

# Utiliser le Base de database.models pour éviter les conflits
from database.models import Base

# Modèles pour le paramétrage - À déplacer dans database/models.py pour production
class RoleParametrage(Base):
    """Rôles utilisateurs avec permissions"""
    __tablename__ = "role"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False, unique=True)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(Text, nullable=True)  # JSON string des permissions
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VilleParametrage(Base):
    """Villes du Gabon"""
    __tablename__ = "ville"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    pays = Column(String(50), default="Gabon")
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    communes = relationship("CommuneParametrage", back_populates="ville", cascade="all, delete-orphan")

class CommuneParametrage(Base):
    """Communes dans les villes"""
    __tablename__ = "commune"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    ville_id = Column(Integer, ForeignKey("ville.id"), nullable=False)
    description = Column(Text, nullable=True)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    ville = relationship("VilleParametrage", back_populates="communes")
    arrondissements = relationship("ArrondissementParametrage", back_populates="commune", cascade="all, delete-orphan")

class ArrondissementParametrage(Base):
    """Arrondissements dans les communes"""
    __tablename__ = "arrondissement"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    commune_id = Column(Integer, ForeignKey("commune.id"), nullable=False)
    description = Column(Text, nullable=True)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    commune = relationship("CommuneParametrage", back_populates="arrondissements")
    quartiers = relationship("QuartierParametrage", back_populates="arrondissement", cascade="all, delete-orphan")

class QuartierParametrage(Base):
    """Quartiers dans les arrondissements (extension du modèle Quartier existant)"""
    __tablename__ = "quartier_parametrage"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    arrondissement_id = Column(Integer, ForeignKey("arrondissement.id"), nullable=True)
    zone_id = Column(Integer, ForeignKey("zone.id"), nullable=True)  # Pour compatibilité
    description = Column(Text, nullable=True)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    arrondissement = relationship("ArrondissementParametrage", back_populates="quartiers")

class SecteurActiviteParametrage(Base):
    """Secteurs d'activité des contribuables"""
    __tablename__ = "secteur_activite"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False, unique=True)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==================== SCHÉMAS PYDANTIC ====================
from pydantic import BaseModel

class RoleBase(BaseModel):
    nom: str
    code: str
    description: Optional[str] = None
    permissions: List[str] = []
    actif: bool = True

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    nom: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    actif: Optional[bool] = None

class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class VilleBase(BaseModel):
    nom: str
    code: str
    description: Optional[str] = None
    pays: str = "Gabon"
    actif: bool = True

class VilleCreate(VilleBase):
    pass

class VilleUpdate(BaseModel):
    nom: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    pays: Optional[str] = None
    actif: Optional[bool] = None

class VilleResponse(VilleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CommuneBase(BaseModel):
    nom: str
    code: str
    ville_id: int
    description: Optional[str] = None
    actif: bool = True

class CommuneCreate(CommuneBase):
    pass

class CommuneUpdate(BaseModel):
    nom: Optional[str] = None
    code: Optional[str] = None
    ville_id: Optional[int] = None
    description: Optional[str] = None
    actif: Optional[bool] = None

class CommuneResponse(CommuneBase):
    id: int
    ville: Optional[VilleResponse] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ArrondissementBase(BaseModel):
    nom: str
    code: str
    commune_id: int
    description: Optional[str] = None
    actif: bool = True

class ArrondissementCreate(ArrondissementBase):
    pass

class ArrondissementUpdate(BaseModel):
    nom: Optional[str] = None
    code: Optional[str] = None
    commune_id: Optional[int] = None
    description: Optional[str] = None
    actif: Optional[bool] = None

class ArrondissementResponse(ArrondissementBase):
    id: int
    commune: Optional[CommuneResponse] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class QuartierParametrageBase(BaseModel):
    nom: str
    code: str
    arrondissement_id: Optional[int] = None
    zone_id: Optional[int] = None
    description: Optional[str] = None
    actif: bool = True

class QuartierParametrageCreate(QuartierParametrageBase):
    pass

class QuartierParametrageUpdate(BaseModel):
    nom: Optional[str] = None
    code: Optional[str] = None
    arrondissement_id: Optional[int] = None
    zone_id: Optional[int] = None
    description: Optional[str] = None
    actif: Optional[bool] = None

class QuartierParametrageResponse(QuartierParametrageBase):
    id: int
    arrondissement: Optional[ArrondissementResponse] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SecteurActiviteBase(BaseModel):
    nom: str
    code: str
    description: Optional[str] = None
    actif: bool = True

class SecteurActiviteCreate(SecteurActiviteBase):
    pass

class SecteurActiviteUpdate(BaseModel):
    nom: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    actif: Optional[bool] = None

class SecteurActiviteResponse(SecteurActiviteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ==================== ENDPOINTS RÔLES ====================
@router.get("/roles", response_model=List[dict])
def get_roles(
    actif: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user)
):
    """Récupère la liste des rôles"""
    try:
        # Pour l'instant, retourner les rôles existants du système
        roles = []
        for role_enum in RoleEnum:
            roles.append({
                "id": role_enum.value,
                "nom": role_enum.value.replace("_", " ").title(),
                "code": role_enum.value,
                "description": f"Rôle {role_enum.value}",
                "permissions": [],  # À implémenter selon les besoins
                "actif": True,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            })
        
        if actif is not None:
            # Filtrer si nécessaire
            pass
            
        return roles
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des rôles: {str(e)}")

@router.get("/roles/{role_id}")
def get_role(role_id: str, db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_active_user)):
    """Récupère un rôle par son ID"""
    try:
        role_enum = RoleEnum(role_id)
        return {
            "id": role_enum.value,
            "nom": role_enum.value.replace("_", " ").title(),
            "code": role_enum.value,
            "description": f"Rôle {role_enum.value}",
            "permissions": [],
            "actif": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="Rôle non trouvé")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@router.post("/roles")
def create_role(role: RoleCreate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Crée un nouveau rôle (admin uniquement)"""
    # Note: Dans la version actuelle, les rôles sont définis par enum
    # Cette fonctionnalité pourrait être étendue pour permettre des rôles personnalisés
    raise HTTPException(status_code=501, detail="Création de rôles personnalisés non encore implémentée")

@router.put("/roles/{role_id}")
def update_role(role_id: str, role: RoleUpdate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Met à jour un rôle (admin uniquement)"""
    raise HTTPException(status_code=501, detail="Modification de rôles non encore implémentée")

@router.delete("/roles/{role_id}")
def delete_role(role_id: str, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Supprime un rôle (admin uniquement)"""
    raise HTTPException(status_code=501, detail="Suppression de rôles non encore implémentée")

# ==================== ENDPOINTS VILLES ====================
@router.get("/villes", response_model=List[dict])
def get_villes(
    actif: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user)
):
    """Récupère la liste des villes"""
    try:
        # Vérifier si la table existe, sinon retourner les villes gabonaises par défaut
        from sqlalchemy import inspect, text
        
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        if "ville" in tables:
            query = db.query(VilleParametrage)
            if actif is not None:
                query = query.filter(VilleParametrage.actif == actif)
            villes = query.all()
            return [{
                "id": v.id,
                "nom": v.nom,
                "code": v.code,
                "description": v.description,
                "pays": v.pays,
                "actif": v.actif,
                "created_at": v.created_at.isoformat() if v.created_at else None,
                "updated_at": v.updated_at.isoformat() if v.updated_at else None
            } for v in villes]
        else:
            # Retourner les villes gabonaises par défaut
            villes_gabon = [
                {"nom": "Libreville", "code": "LBV", "description": "Capitale du Gabon"},
                {"nom": "Port-Gentil", "code": "POG", "description": "Ville économique"},
                {"nom": "Franceville", "code": "FRV", "description": "Ville du Haut-Ogooué"},
                {"nom": "Oyem", "code": "OYM", "description": "Ville du Woleu-Ntem"},
                {"nom": "Moanda", "code": "MND", "description": "Ville minière"},
                {"nom": "Mouila", "code": "MLA", "description": "Ville de la Ngounié"},
                {"nom": "Tchibanga", "code": "TCB", "description": "Ville de la Nyanga"},
                {"nom": "Koulamoutou", "code": "KLM", "description": "Ville de l'Ogooué-Lolo"},
                {"nom": "Makokou", "code": "MKK", "description": "Ville de l'Ogooué-Ivindo"},
                {"nom": "Lambaréné", "code": "LBR", "description": "Ville de Moyen-Ogooué"}
            ]
            return [{"id": i+1, "nom": v["nom"], "code": v["code"], "description": v["description"], "pays": "Gabon", "actif": True, "created_at": datetime.utcnow().isoformat(), "updated_at": datetime.utcnow().isoformat()} for i, v in enumerate(villes_gabon)]
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des villes: {str(e)}")

@router.post("/villes")
def create_ville(ville: VilleCreate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Crée une nouvelle ville"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        if "ville" not in tables:
            # Créer la table si elle n'existe pas
            Base.metadata.create_all(bind=db.bind, tables=[VilleParametrage.__table__])
        
        db_ville = VilleParametrage(**ville.dict())
        db.add(db_ville)
        db.commit()
        db.refresh(db_ville)
        
        return {
            "id": db_ville.id,
            "nom": db_ville.nom,
            "code": db_ville.code,
            "description": db_ville.description,
            "pays": db_ville.pays,
            "actif": db_ville.actif,
            "created_at": db_ville.created_at.isoformat() if db_ville.created_at else None,
            "updated_at": db_ville.updated_at.isoformat() if db_ville.updated_at else None
        }
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la ville: {str(e)}")

@router.put("/villes/{ville_id}")
def update_ville(ville_id: int, ville: VilleUpdate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Met à jour une ville"""
    try:
        db_ville = db.query(Ville).filter(Ville.id == ville_id).first()
        if not db_ville:
            raise HTTPException(status_code=404, detail="Ville non trouvée")
        
        update_data = ville.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_ville, key, value)
        
        db_ville.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_ville)
        
        return {
            "id": db_ville.id,
            "nom": db_ville.nom,
            "code": db_ville.code,
            "description": db_ville.description,
            "pays": db_ville.pays,
            "actif": db_ville.actif,
            "created_at": db_ville.created_at.isoformat() if db_ville.created_at else None,
            "updated_at": db_ville.updated_at.isoformat() if db_ville.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")

@router.delete("/villes/{ville_id}")
def delete_ville(ville_id: int, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Supprime une ville"""
    try:
        db_ville = db.query(Ville).filter(Ville.id == ville_id).first()
        if not db_ville:
            raise HTTPException(status_code=404, detail="Ville non trouvée")
        
        db.delete(db_ville)
        db.commit()
        return {"message": "Ville supprimée avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

# ==================== ENDPOINTS COMMUNES ====================
@router.get("/communes", response_model=List[dict])
def get_communes(
    ville_id: Optional[int] = Query(None),
    actif: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user)
):
    """Récupère la liste des communes"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        if "commune" in tables:
            query = db.query(CommuneParametrage)
            if ville_id:
                query = query.filter(CommuneParametrage.ville_id == ville_id)
            if actif is not None:
                query = query.filter(CommuneParametrage.actif == actif)
            communes = query.all()
            return [{
                "id": c.id,
                "nom": c.nom,
                "code": c.code,
                "ville_id": c.ville_id,
                "description": c.description,
                "actif": c.actif,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None
            } for c in communes]
        else:
            return []
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des communes: {str(e)}")

@router.post("/communes")
def create_commune(commune: CommuneCreate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Crée une nouvelle commune"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        if "commune" not in tables:
            Base.metadata.create_all(bind=db.bind, tables=[CommuneParametrage.__table__])
        
        db_commune = CommuneParametrage(**commune.dict())
        db.add(db_commune)
        db.commit()
        db.refresh(db_commune)
        
        return {
            "id": db_commune.id,
            "nom": db_commune.nom,
            "code": db_commune.code,
            "ville_id": db_commune.ville_id,
            "description": db_commune.description,
            "actif": db_commune.actif,
            "created_at": db_commune.created_at.isoformat() if db_commune.created_at else None,
            "updated_at": db_commune.updated_at.isoformat() if db_commune.updated_at else None
        }
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la commune: {str(e)}")

@router.put("/communes/{commune_id}")
def update_commune(commune_id: int, commune: CommuneUpdate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Met à jour une commune"""
    try:
        db_commune = db.query(Commune).filter(Commune.id == commune_id).first()
        if not db_commune:
            raise HTTPException(status_code=404, detail="Commune non trouvée")
        
        update_data = commune.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_commune, key, value)
        
        db_commune.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_commune)
        
        return {
            "id": db_commune.id,
            "nom": db_commune.nom,
            "code": db_commune.code,
            "ville_id": db_commune.ville_id,
            "description": db_commune.description,
            "actif": db_commune.actif,
            "created_at": db_commune.created_at.isoformat() if db_commune.created_at else None,
            "updated_at": db_commune.updated_at.isoformat() if db_commune.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")

@router.delete("/communes/{commune_id}")
def delete_commune(commune_id: int, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Supprime une commune"""
    try:
        db_commune = db.query(Commune).filter(Commune.id == commune_id).first()
        if not db_commune:
            raise HTTPException(status_code=404, detail="Commune non trouvée")
        
        db.delete(db_commune)
        db.commit()
        return {"message": "Commune supprimée avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

# ==================== ENDPOINTS ARRONDISSEMENTS ====================
@router.get("/arrondissements", response_model=List[dict])
def get_arrondissements(
    commune_id: Optional[int] = Query(None),
    actif: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user)
):
    """Récupère la liste des arrondissements"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        if "arrondissement" in tables:
            query = db.query(ArrondissementParametrage)
            if commune_id:
                query = query.filter(ArrondissementParametrage.commune_id == commune_id)
            if actif is not None:
                query = query.filter(ArrondissementParametrage.actif == actif)
            arrondissements = query.all()
            return [{
                "id": a.id,
                "nom": a.nom,
                "code": a.code,
                "commune_id": a.commune_id,
                "description": a.description,
                "actif": a.actif,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "updated_at": a.updated_at.isoformat() if a.updated_at else None
            } for a in arrondissements]
        else:
            return []
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des arrondissements: {str(e)}")

@router.post("/arrondissements")
def create_arrondissement(arrondissement: ArrondissementCreate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Crée un nouvel arrondissement"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        if "arrondissement" not in tables:
            Base.metadata.create_all(bind=db.bind, tables=[ArrondissementParametrage.__table__])
        
        db_arrondissement = ArrondissementParametrage(**arrondissement.dict())
        db.add(db_arrondissement)
        db.commit()
        db.refresh(db_arrondissement)
        
        return {
            "id": db_arrondissement.id,
            "nom": db_arrondissement.nom,
            "code": db_arrondissement.code,
            "commune_id": db_arrondissement.commune_id,
            "description": db_arrondissement.description,
            "actif": db_arrondissement.actif,
            "created_at": db_arrondissement.created_at.isoformat() if db_arrondissement.created_at else None,
            "updated_at": db_arrondissement.updated_at.isoformat() if db_arrondissement.updated_at else None
        }
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'arrondissement: {str(e)}")

@router.put("/arrondissements/{arrondissement_id}")
def update_arrondissement(arrondissement_id: int, arrondissement: ArrondissementUpdate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Met à jour un arrondissement"""
    try:
        db_arrondissement = db.query(ArrondissementParametrage).filter(ArrondissementParametrage.id == arrondissement_id).first()
        if not db_arrondissement:
            raise HTTPException(status_code=404, detail="Arrondissement non trouvé")
        
        update_data = arrondissement.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_arrondissement, key, value)
        
        db_arrondissement.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_arrondissement)
        
        return {
            "id": db_arrondissement.id,
            "nom": db_arrondissement.nom,
            "code": db_arrondissement.code,
            "commune_id": db_arrondissement.commune_id,
            "description": db_arrondissement.description,
            "actif": db_arrondissement.actif,
            "created_at": db_arrondissement.created_at.isoformat() if db_arrondissement.created_at else None,
            "updated_at": db_arrondissement.updated_at.isoformat() if db_arrondissement.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")

@router.delete("/arrondissements/{arrondissement_id}")
def delete_arrondissement(arrondissement_id: int, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Supprime un arrondissement"""
    try:
        db_arrondissement = db.query(ArrondissementParametrage).filter(ArrondissementParametrage.id == arrondissement_id).first()
        if not db_arrondissement:
            raise HTTPException(status_code=404, detail="Arrondissement non trouvé")
        
        db.delete(db_arrondissement)
        db.commit()
        return {"message": "Arrondissement supprimé avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

# ==================== ENDPOINTS QUARTIERS (EXTENSION) ====================
@router.post("/quartiers")
def create_quartier(quartier: QuartierParametrageCreate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Crée un nouveau quartier avec support pour arrondissement"""
    try:
        # Utiliser la table quartier existante et ajouter arrondissement_id si la colonne existe
        from database.models import Quartier
        from sqlalchemy import inspect, text
        
        inspector = inspect(db.bind)
        columns = [col['name'] for col in inspector.get_columns('quartier')]
        
        quartier_data = quartier.dict(exclude={'arrondissement_id'} if 'arrondissement_id' not in columns else set())
        
        if 'arrondissement_id' in columns and quartier.arrondissement_id:
            quartier_data['arrondissement_id'] = quartier.arrondissement_id
        
        db_quartier = Quartier(**quartier_data)
        db.add(db_quartier)
        db.commit()
        db.refresh(db_quartier)
        
        return {
            "id": db_quartier.id,
            "nom": db_quartier.nom,
            "code": db_quartier.code,
            "arrondissement_id": getattr(db_quartier, 'arrondissement_id', None),
            "zone_id": db_quartier.zone_id if hasattr(db_quartier, 'zone_id') else None,
            "description": db_quartier.description,
            "actif": db_quartier.actif,
            "created_at": db_quartier.created_at.isoformat() if db_quartier.created_at else None,
            "updated_at": db_quartier.updated_at.isoformat() if db_quartier.updated_at else None
        }
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du quartier: {str(e)}")

@router.put("/quartiers/{quartier_id}")
def update_quartier(quartier_id: int, quartier: QuartierParametrageUpdate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Met à jour un quartier"""
    try:
        from database.models import Quartier
        db_quartier = db.query(Quartier).filter(Quartier.id == quartier_id).first()
        if not db_quartier:
            raise HTTPException(status_code=404, detail="Quartier non trouvé")
        
        update_data = quartier.dict(exclude_unset=True)
        
        # Gérer arrondissement_id si la colonne existe
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        columns = [col['name'] for col in inspector.get_columns('quartier')]
        
        if 'arrondissement_id' not in columns and 'arrondissement_id' in update_data:
            del update_data['arrondissement_id']
        
        for key, value in update_data.items():
            if hasattr(db_quartier, key):
                setattr(db_quartier, key, value)
        
        db_quartier.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_quartier)
        
        return {
            "id": db_quartier.id,
            "nom": db_quartier.nom,
            "code": db_quartier.code,
            "arrondissement_id": getattr(db_quartier, 'arrondissement_id', None),
            "zone_id": db_quartier.zone_id if hasattr(db_quartier, 'zone_id') else None,
            "description": db_quartier.description,
            "actif": db_quartier.actif,
            "created_at": db_quartier.created_at.isoformat() if db_quartier.created_at else None,
            "updated_at": db_quartier.updated_at.isoformat() if db_quartier.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")

@router.delete("/quartiers/{quartier_id}")
def delete_quartier(quartier_id: int, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Supprime un quartier"""
    try:
        from database.models import Quartier
        db_quartier = db.query(Quartier).filter(Quartier.id == quartier_id).first()
        if not db_quartier:
            raise HTTPException(status_code=404, detail="Quartier non trouvé")
        
        db.delete(db_quartier)
        db.commit()
        return {"message": "Quartier supprimé avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

# ==================== ENDPOINTS SECTEURS D'ACTIVITÉ ====================
@router.get("/secteurs-activite", response_model=List[dict])
def get_secteurs_activite(
    actif: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_active_user)
):
    """Récupère la liste des secteurs d'activité"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        if "secteur_activite" in tables:
            query = db.query(SecteurActiviteParametrage)
            if actif is not None:
                query = query.filter(SecteurActiviteParametrage.actif == actif)
            secteurs = query.all()
            return [{
                "id": s.id,
                "nom": s.nom,
                "code": s.code,
                "description": s.description,
                "actif": s.actif,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None
            } for s in secteurs]
        else:
            return []
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des secteurs: {str(e)}")

@router.post("/secteurs-activite")
def create_secteur_activite(secteur: SecteurActiviteCreate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Crée un nouveau secteur d'activité"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        if "secteur_activite" not in tables:
            Base.metadata.create_all(bind=db.bind, tables=[SecteurActiviteParametrage.__table__])
        
        db_secteur = SecteurActiviteParametrage(**secteur.dict())
        db.add(db_secteur)
        db.commit()
        db.refresh(db_secteur)
        
        return {
            "id": db_secteur.id,
            "nom": db_secteur.nom,
            "code": db_secteur.code,
            "description": db_secteur.description,
            "actif": db_secteur.actif,
            "created_at": db_secteur.created_at.isoformat() if db_secteur.created_at else None,
            "updated_at": db_secteur.updated_at.isoformat() if db_secteur.updated_at else None
        }
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du secteur: {str(e)}")

@router.put("/secteurs-activite/{secteur_id}")
def update_secteur_activite(secteur_id: int, secteur: SecteurActiviteUpdate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Met à jour un secteur d'activité"""
    try:
        db_secteur = db.query(SecteurActiviteParametrage).filter(SecteurActiviteParametrage.id == secteur_id).first()
        if not db_secteur:
            raise HTTPException(status_code=404, detail="Secteur d'activité non trouvé")
        
        update_data = secteur.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_secteur, key, value)
        
        db_secteur.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_secteur)
        
        return {
            "id": db_secteur.id,
            "nom": db_secteur.nom,
            "code": db_secteur.code,
            "description": db_secteur.description,
            "actif": db_secteur.actif,
            "created_at": db_secteur.created_at.isoformat() if db_secteur.created_at else None,
            "updated_at": db_secteur.updated_at.isoformat() if db_secteur.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")

@router.delete("/secteurs-activite/{secteur_id}")
def delete_secteur_activite(secteur_id: int, db: Session = Depends(get_db), current_user: Utilisateur = Depends(require_role(["admin"]))):
    """Supprime un secteur d'activité"""
    try:
        db_secteur = db.query(SecteurActiviteParametrage).filter(SecteurActiviteParametrage.id == secteur_id).first()
        if not db_secteur:
            raise HTTPException(status_code=404, detail="Secteur d'activité non trouvé")
        
        db.delete(db_secteur)
        db.commit()
        return {"message": "Secteur d'activité supprimé avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


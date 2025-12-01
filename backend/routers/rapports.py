"""
Routes pour les rapports et statistiques
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional, List
from database.database import get_db
from database.models import InfoCollecte, Collecteur, Taxe, StatutCollecteEnum
from datetime import datetime, date, timedelta
from decimal import Decimal
from pydantic import BaseModel
from auth.security import get_current_active_user
from schemas.statistiques_collecteur import StatistiquesCollecteurResponse
from services.statistiques_collecteur import compute_statistiques_collecteur
from services.export_rapport import generate_csv_rapport, generate_pdf_rapport

router = APIRouter(
    prefix="/api/rapports",
    tags=["rapports"],
    dependencies=[Depends(get_current_active_user)],
)


# Schémas de réponse
class StatistiquesGenerales(BaseModel):
    total_collecte: Decimal
    nombre_transactions: int
    moyenne_par_transaction: Decimal
    nombre_collecteurs_actifs: int
    nombre_taxes_actives: int
    transactions_aujourd_hui: int
    collecte_aujourd_hui: Decimal
    transactions_ce_mois: int
    collecte_ce_mois: Decimal


class CollecteParMoyen(BaseModel):
    moyen_paiement: str
    montant_total: Decimal
    nombre_transactions: int
    pourcentage: float


class TopCollecteur(BaseModel):
    collecteur_id: int
    collecteur_nom: str
    collecteur_prenom: str
    montant_total: Decimal
    nombre_transactions: int


class TopTaxe(BaseModel):
    taxe_id: int
    taxe_nom: str
    taxe_code: str
    montant_total: Decimal
    nombre_transactions: int


class EvolutionTemporelle(BaseModel):
    periode: str
    montant_total: Decimal
    nombre_transactions: int


class RapportComplet(BaseModel):
    statistiques_generales: StatistiquesGenerales
    collecte_par_moyen: List[CollecteParMoyen]
    top_collecteurs: List[TopCollecteur]
    top_taxes: List[TopTaxe]
    evolution_temporelle: List[EvolutionTemporelle]


@router.get("/statistiques-generales")
def get_statistiques_generales(
    date_debut: Optional[date] = Query(None, description="Date de début du rapport"),
    date_fin: Optional[date] = Query(None, description="Date de fin du rapport"),
    collecteur_id: Optional[int] = Query(None, description="ID du collecteur pour filtrer"),
    taxe_id: Optional[int] = Query(None, description="ID de la taxe pour filtrer"),
    db: Session = Depends(get_db)
):
    """Récupère les statistiques générales des collectes"""
    try:
        # Query de base pour les collectes validées
        query = db.query(InfoCollecte).filter(
            InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
            InfoCollecte.annule == False
        )
        
        # Appliquer les filtres
        if date_debut:
            query = query.filter(InfoCollecte.date_collecte >= datetime.combine(date_debut, datetime.min.time()))
        if date_fin:
            query = query.filter(InfoCollecte.date_collecte <= datetime.combine(date_fin, datetime.max.time()))
        if collecteur_id:
            query = query.filter(InfoCollecte.collecteur_id == collecteur_id)
        if taxe_id:
            query = query.filter(InfoCollecte.taxe_id == taxe_id)
        
        # Statistiques globales
        total_collecte = query.with_entities(func.sum(InfoCollecte.montant)).scalar() or Decimal('0')
        nombre_transactions = query.count()
        moyenne_par_transaction = total_collecte / nombre_transactions if nombre_transactions > 0 else Decimal('0')
        
        # Statistiques pour aujourd'hui
        aujourd_hui = date.today()
        query_aujourd_hui = db.query(InfoCollecte).filter(
            InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
            InfoCollecte.annule == False,
            func.date(InfoCollecte.date_collecte) == aujourd_hui
        )
        if collecteur_id:
            query_aujourd_hui = query_aujourd_hui.filter(InfoCollecte.collecteur_id == collecteur_id)
        if taxe_id:
            query_aujourd_hui = query_aujourd_hui.filter(InfoCollecte.taxe_id == taxe_id)
        
        transactions_aujourd_hui = query_aujourd_hui.count()
        collecte_aujourd_hui = query_aujourd_hui.with_entities(func.sum(InfoCollecte.montant)).scalar() or Decimal('0')
        
        # Statistiques pour ce mois
        premier_jour_mois = date.today().replace(day=1)
        query_ce_mois = db.query(InfoCollecte).filter(
            InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
            InfoCollecte.annule == False,
            InfoCollecte.date_collecte >= datetime.combine(premier_jour_mois, datetime.min.time())
        )
        if collecteur_id:
            query_ce_mois = query_ce_mois.filter(InfoCollecte.collecteur_id == collecteur_id)
        if taxe_id:
            query_ce_mois = query_ce_mois.filter(InfoCollecte.taxe_id == taxe_id)
        
        transactions_ce_mois = query_ce_mois.count()
        collecte_ce_mois = query_ce_mois.with_entities(func.sum(InfoCollecte.montant)).scalar() or Decimal('0')
        
        # Nombre de collecteurs et taxes actifs
        nombre_collecteurs_actifs = db.query(Collecteur).filter(Collecteur.actif == True).count()
        nombre_taxes_actives = db.query(Taxe).filter(Taxe.actif == True).count()
        
        return StatistiquesGenerales(
            total_collecte=total_collecte,
            nombre_transactions=nombre_transactions,
            moyenne_par_transaction=moyenne_par_transaction,
            nombre_collecteurs_actifs=nombre_collecteurs_actifs,
            nombre_taxes_actives=nombre_taxes_actives,
            transactions_aujourd_hui=transactions_aujourd_hui,
            collecte_aujourd_hui=collecte_aujourd_hui,
            transactions_ce_mois=transactions_ce_mois,
            collecte_ce_mois=collecte_ce_mois
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul des statistiques: {str(e)}")


@router.get("/collecte-par-moyen")
def get_collecte_par_moyen(
    date_debut: Optional[date] = Query(None),
    date_fin: Optional[date] = Query(None),
    collecteur_id: Optional[int] = Query(None),
    taxe_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupère la répartition des collectes par moyen de paiement"""
    try:
        query = db.query(
            InfoCollecte.type_paiement,
            func.sum(InfoCollecte.montant).label('montant_total'),
            func.count(InfoCollecte.id).label('nombre_transactions')
        ).filter(
            InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
            InfoCollecte.annule == False
        )
        
        if date_debut:
            query = query.filter(InfoCollecte.date_collecte >= datetime.combine(date_debut, datetime.min.time()))
        if date_fin:
            query = query.filter(InfoCollecte.date_collecte <= datetime.combine(date_fin, datetime.max.time()))
        if collecteur_id:
            query = query.filter(InfoCollecte.collecteur_id == collecteur_id)
        if taxe_id:
            query = query.filter(InfoCollecte.taxe_id == taxe_id)
        
        results = query.group_by(InfoCollecte.type_paiement).all()
        
        # Calculer le total pour les pourcentages
        total = sum(row.montant_total for row in results) or Decimal('1')
        
        collecte_par_moyen = []
        for row in results:
            pourcentage = float((row.montant_total / total) * 100) if total > 0 else 0.0
            collecte_par_moyen.append(CollecteParMoyen(
                moyen_paiement=row.type_paiement or 'autre',
                montant_total=row.montant_total or Decimal('0'),
                nombre_transactions=row.nombre_transactions or 0,
                pourcentage=pourcentage
            ))
        
        return sorted(collecte_par_moyen, key=lambda x: x.montant_total, reverse=True)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul: {str(e)}")


@router.get("/top-collecteurs")
def get_top_collecteurs(
    limit: int = Query(10, ge=1, le=50, description="Nombre de collecteurs à retourner"),
    date_debut: Optional[date] = Query(None),
    date_fin: Optional[date] = Query(None),
    taxe_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupère les meilleurs collecteurs par montant collecté"""
    try:
        query = db.query(
            InfoCollecte.collecteur_id,
            Collecteur.nom,
            Collecteur.prenom,
            func.sum(InfoCollecte.montant).label('montant_total'),
            func.count(InfoCollecte.id).label('nombre_transactions')
        ).join(
            Collecteur, InfoCollecte.collecteur_id == Collecteur.id
        ).filter(
            InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
            InfoCollecte.annule == False,
            Collecteur.actif == True
        )
        
        if date_debut:
            query = query.filter(InfoCollecte.date_collecte >= datetime.combine(date_debut, datetime.min.time()))
        if date_fin:
            query = query.filter(InfoCollecte.date_collecte <= datetime.combine(date_fin, datetime.max.time()))
        if taxe_id:
            query = query.filter(InfoCollecte.taxe_id == taxe_id)
        
        results = query.group_by(
            InfoCollecte.collecteur_id,
            Collecteur.nom,
            Collecteur.prenom
        ).order_by(
            func.sum(InfoCollecte.montant).desc()
        ).limit(limit).all()
        
        return [
            TopCollecteur(
                collecteur_id=row.collecteur_id,
                collecteur_nom=row.nom or '',
                collecteur_prenom=row.prenom or '',
                montant_total=row.montant_total or Decimal('0'),
                nombre_transactions=row.nombre_transactions or 0
            )
            for row in results
        ]
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul: {str(e)}")


@router.get("/top-taxes")
def get_top_taxes(
    limit: int = Query(10, ge=1, le=50, description="Nombre de taxes à retourner"),
    date_debut: Optional[date] = Query(None),
    date_fin: Optional[date] = Query(None),
    collecteur_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupère les meilleures taxes par montant collecté"""
    try:
        query = db.query(
            InfoCollecte.taxe_id,
            Taxe.nom,
            Taxe.code,
            func.sum(InfoCollecte.montant).label('montant_total'),
            func.count(InfoCollecte.id).label('nombre_transactions')
        ).join(
            Taxe, InfoCollecte.taxe_id == Taxe.id
        ).filter(
            InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
            InfoCollecte.annule == False,
            Taxe.actif == True
        )
        
        if date_debut:
            query = query.filter(InfoCollecte.date_collecte >= datetime.combine(date_debut, datetime.min.time()))
        if date_fin:
            query = query.filter(InfoCollecte.date_collecte <= datetime.combine(date_fin, datetime.max.time()))
        if collecteur_id:
            query = query.filter(InfoCollecte.collecteur_id == collecteur_id)
        
        results = query.group_by(
            InfoCollecte.taxe_id,
            Taxe.nom,
            Taxe.code
        ).order_by(
            func.sum(InfoCollecte.montant).desc()
        ).limit(limit).all()
        
        return [
            TopTaxe(
                taxe_id=row.taxe_id,
                taxe_nom=row.nom or '',
                taxe_code=row.code or '',
                montant_total=row.montant_total or Decimal('0'),
                nombre_transactions=row.nombre_transactions or 0
            )
            for row in results
        ]
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul: {str(e)}")


@router.get("/evolution-temporelle")
def get_evolution_temporelle(
    date_debut: Optional[date] = Query(None),
    date_fin: Optional[date] = Query(None),
    collecteur_id: Optional[int] = Query(None),
    taxe_id: Optional[int] = Query(None),
    periode: str = Query('jour', regex='^(jour|semaine|mois)$', description="Période d'agrégation"),
    db: Session = Depends(get_db)
):
    """Récupère l'évolution temporelle des collectes"""
    try:
        # Par défaut, prendre le mois dernier si aucune date n'est spécifiée
        if not date_debut or not date_fin:
            date_fin = date.today()
            if periode == 'mois':
                date_debut = date_fin.replace(day=1) - timedelta(days=365)  # 12 mois
            elif periode == 'semaine':
                date_debut = date_fin - timedelta(days=84)  # 12 semaines
            else:
                date_debut = date_fin - timedelta(days=30)  # 30 jours
        
        query = db.query(
            func.date(InfoCollecte.date_collecte).label('date_collecte'),
            func.sum(InfoCollecte.montant).label('montant_total'),
            func.count(InfoCollecte.id).label('nombre_transactions')
        ).filter(
            InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
            InfoCollecte.annule == False,
            InfoCollecte.date_collecte >= datetime.combine(date_debut, datetime.min.time()),
            InfoCollecte.date_collecte <= datetime.combine(date_fin, datetime.max.time())
        )
        
        if collecteur_id:
            query = query.filter(InfoCollecte.collecteur_id == collecteur_id)
        if taxe_id:
            query = query.filter(InfoCollecte.taxe_id == taxe_id)
        
        if periode == 'mois':
            query = query.group_by(
                extract('year', InfoCollecte.date_collecte),
                extract('month', InfoCollecte.date_collecte)
            )
        elif periode == 'semaine':
            query = query.group_by(
                extract('year', InfoCollecte.date_collecte),
                extract('week', InfoCollecte.date_collecte)
            )
        else:  # jour
                query = query.group_by(func.date(InfoCollecte.date_collecte))
        
        results = query.all()
        
        evolution = []
        for row in results:
            # Format de sortie selon le type de requête
            date_collecte = row[0] if isinstance(row, tuple) else (row.date_collecte if hasattr(row, 'date_collecte') else None)
            montant_total = row[1] if isinstance(row, tuple) else (row.montant_total if hasattr(row, 'montant_total') else Decimal('0'))
            nb_transactions = row[2] if isinstance(row, tuple) else (row.nombre_transactions if hasattr(row, 'nombre_transactions') else 0)
            
            # Formater la période selon le type d'agrégation
            if periode == 'mois':
                if date_collecte:
                    if isinstance(date_collecte, date):
                        periode_str = f"{date_collecte.year}-{date_collecte.month:02d}"
                    else:
                        periode_str = str(date_collecte)[:7]  # Prendre YYYY-MM
                else:
                    periode_str = "N/A"
            elif periode == 'semaine':
                if date_collecte:
                    if isinstance(date_collecte, date):
                        year, week, _ = date_collecte.isocalendar()
                        periode_str = f"S{week:02d}-{year}"
                    else:
                        periode_str = str(date_collecte)
                else:
                    periode_str = "N/A"
            else:  # jour
                periode_str = str(date_collecte) if date_collecte else "N/A"
            
            evolution.append(EvolutionTemporelle(
                periode=periode_str,
                montant_total=montant_total or Decimal('0'),
                nombre_transactions=nb_transactions or 0
            ))
        
        return evolution
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul: {str(e)}")


@router.get("/complet")
def get_rapport_complet(
    date_debut: Optional[date] = Query(None),
    date_fin: Optional[date] = Query(None),
    collecteur_id: Optional[int] = Query(None),
    taxe_id: Optional[int] = Query(None),
    top_limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Récupère un rapport complet avec toutes les statistiques"""
    try:
        # Calculer toutes les statistiques en parallèle serait mieux, mais on fait séquentiel pour simplifier
        stats_gen = get_statistiques_generales(date_debut, date_fin, collecteur_id, taxe_id, db)
        collecte_moyen = get_collecte_par_moyen(date_debut, date_fin, collecteur_id, taxe_id, db)
        top_collecteurs = get_top_collecteurs(top_limit, date_debut, date_fin, taxe_id, db)
        top_taxes = get_top_taxes(top_limit, date_debut, date_fin, collecteur_id, db)
        evolution = get_evolution_temporelle(date_debut, date_fin, collecteur_id, taxe_id, 'jour', db)
        
        return RapportComplet(
            statistiques_generales=stats_gen,
            collecte_par_moyen=collecte_moyen,
            top_collecteurs=top_collecteurs,
            top_taxes=top_taxes,
            evolution_temporelle=evolution
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération du rapport: {str(e)}")


@router.get("/collecteur/{collecteur_id}", response_model=StatistiquesCollecteurResponse)
def get_collecteur_stats_via_rapports(collecteur_id: int, db: Session = Depends(get_db)):
    """Expose /api/rapports/collecteur/{collecteur_id} pour l'app mobile"""
    stats = compute_statistiques_collecteur(db, collecteur_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Collecteur non trouvé")
    return stats


@router.get("/export/csv")
def export_rapport_csv(
    date_debut: Optional[date] = Query(None, description="Date de début du rapport"),
    date_fin: Optional[date] = Query(None, description="Date de fin du rapport"),
    collecteur_id: Optional[int] = Query(None, description="ID du collecteur pour filtrer"),
    taxe_id: Optional[int] = Query(None, description="ID de la taxe pour filtrer"),
    top_limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Exporte le rapport complet en format CSV"""
    try:
        # Récupérer le rapport complet
        rapport_complet = get_rapport_complet(date_debut, date_fin, collecteur_id, taxe_id, top_limit, db)
        
        # Convertir en dictionnaire
        rapport_dict = rapport_complet.model_dump() if hasattr(rapport_complet, 'model_dump') else rapport_complet.dict()
        
        # Ajouter les dates de filtrage si disponibles
        if date_debut:
            rapport_dict['date_debut'] = date_debut.strftime('%d/%m/%Y') if isinstance(date_debut, date) else str(date_debut)
        if date_fin:
            rapport_dict['date_fin'] = date_fin.strftime('%d/%m/%Y') if isinstance(date_fin, date) else str(date_fin)
        
        # Générer le CSV
        csv_buffer = generate_csv_rapport(rapport_dict)
        
        # Générer le nom de fichier
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"rapport_collecte_{date_str}.csv"
        
        return StreamingResponse(
            csv_buffer,
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "text/csv; charset=utf-8"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'export CSV: {str(e)}")


@router.get("/export/pdf")
def export_rapport_pdf(
    date_debut: Optional[date] = Query(None, description="Date de début du rapport"),
    date_fin: Optional[date] = Query(None, description="Date de fin du rapport"),
    collecteur_id: Optional[int] = Query(None, description="ID du collecteur pour filtrer"),
    taxe_id: Optional[int] = Query(None, description="ID de la taxe pour filtrer"),
    top_limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Exporte le rapport complet en format PDF avec logo"""
    try:
        # Récupérer le rapport complet
        rapport_complet = get_rapport_complet(date_debut, date_fin, collecteur_id, taxe_id, top_limit, db)
        
        # Convertir en dictionnaire
        rapport_dict = rapport_complet.model_dump() if hasattr(rapport_complet, 'model_dump') else rapport_complet.dict()
        
        # Ajouter les dates de filtrage si disponibles
        if date_debut:
            rapport_dict['date_debut'] = date_debut.strftime('%d/%m/%Y') if isinstance(date_debut, date) else str(date_debut)
        if date_fin:
            rapport_dict['date_fin'] = date_fin.strftime('%d/%m/%Y') if isinstance(date_fin, date) else str(date_fin)
        
        # Générer le PDF
        pdf_buffer = generate_pdf_rapport(rapport_dict)
        
        # Générer le nom de fichier
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"rapport_collecte_{date_str}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/pdf"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'export PDF: {str(e)}")


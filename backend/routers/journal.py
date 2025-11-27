"""
Routes pour les journaux de travaux quotidiens et les commissions
"""

from datetime import date, datetime
from pathlib import Path
from typing import Optional
import csv
import json
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth.security import get_current_active_user
from database.database import get_db
from database.models import (
    JournalTravaux,
    Caisse,
    EtatCaisseEnum,
    InfoCollecte,
    StatutCollecteEnum,
    OperationCaisse,
    TypeOperationCaisseEnum,
    Relance,
    DossierImpaye,
    CommissionFichier,
    CommissionJournaliere,
    StatutJournalEnum,
    StatutCommissionEnum,
    Collecteur,
)
from schemas.journal import (
    JournalComputedResponse,
    JournalTravauxResponse,
    ClotureRequest,
    CommissionGenerationResponse,
    CommissionItem,
    CommissionFichierResponse,
    CommissionJournalResponse,
)
from schemas.info_collecte import InfoCollecteResponse
from schemas.caisse import OperationCaisseResponse

router = APIRouter(
    prefix="/api/journal",
    tags=["journal"],
    dependencies=[Depends(get_current_active_user)],
)


def _compute_decimal(value) -> Decimal:
    return Decimal(value or 0).quantize(Decimal("0.01"))


def _write_commissions_json(file_path: Path, commissions_items: list["CommissionItem"]) -> None:
    payload = [item.model_dump() for item in commissions_items]
    file_path.write_text(
        json.dumps(payload, default=str, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _write_commissions_csv(file_path: Path, commissions_items: list["CommissionItem"]) -> None:
    headers = [
        "collecteur_id",
        "collecteur_nom",
        "montant_collecte",
        "commission_montant",
        "commission_pourcentage",
        "statut_paiement",
    ]
    with file_path.open("w", newline="", encoding="utf-8") as buffer:
        writer = csv.writer(buffer, delimiter=";")
        writer.writerow(headers)
        for item in commissions_items:
            writer.writerow(
                [
                    item.collecteur_id,
                    item.collecteur_nom or "",
                    f"{item.montant_collecte:.2f}",
                    f"{item.commission_montant:.2f}",
                    f"{item.commission_pourcentage:.2f}",
                    item.statut_paiement,
                ]
            )


def _write_commissions_pdf(file_path: Path, commissions_items: list["CommissionItem"], jour: date) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(str(file_path), pagesize=A4)
    width, height = A4

    title = f"Fichier commissions - {jour.isoformat()}"
    c.setFont("Helvetica-Bold", 14)
    c.drawString(25 * mm, height - 30 * mm, title)
    c.setFont("Helvetica", 10)
    c.drawString(25 * mm, height - 35 * mm, f"Généré le {datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')}")

    y = height - 50 * mm
    line_height = 7 * mm

    headers = ["Collecteur", "Montant", "Commission", "%", "Statut"]
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, headers[0])
    c.drawString(70 * mm, y, headers[1])
    c.drawString(100 * mm, y, headers[2])
    c.drawString(130 * mm, y, headers[3])
    c.drawString(150 * mm, y, headers[4])
    y -= line_height

    c.setFont("Helvetica", 10)
    for item in commissions_items:
        if y < 30 * mm:
            c.showPage()
            y = height - 30 * mm
            c.setFont("Helvetica", 10)

        name = item.collecteur_nom or f"Collecteur #{item.collecteur_id}"
        c.drawString(20 * mm, y, name[:30])
        c.drawRightString(95 * mm, y, f"{item.montant_collecte:.2f} FCFA")
        c.drawRightString(125 * mm, y, f"{item.commission_montant:.2f}")
        c.drawRightString(140 * mm, y, f"{item.commission_pourcentage:.2f}%")
        c.drawString(150 * mm, y, item.statut_paiement.upper())
        y -= line_height

    c.showPage()
    c.save()


def compute_journal_stats(db: Session, target_date: date) -> dict:
    collectes_query = db.query(InfoCollecte).filter(
        func.date(InfoCollecte.date_collecte) == target_date,
        InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
        InfoCollecte.annule == False,
    )

    nb_collectes = collectes_query.count()
    montant_collectes = _compute_decimal(
        collectes_query.with_entities(func.coalesce(func.sum(InfoCollecte.montant), 0)).scalar()
    )

    operations_query = db.query(OperationCaisse).filter(
        func.date(OperationCaisse.date_operation) == target_date
    )
    nb_operations = operations_query.count()

    total_entrees = _compute_decimal(
        operations_query.filter(
            OperationCaisse.type_operation.in_(
                [TypeOperationCaisseEnum.ENTREE.value, TypeOperationCaisseEnum.OUVERTURE.value]
            )
        )
        .with_entities(func.coalesce(func.sum(OperationCaisse.montant), 0))
        .scalar()
    )
    total_sorties = _compute_decimal(
        operations_query.filter(
            OperationCaisse.type_operation.in_(
                [TypeOperationCaisseEnum.SORTIE.value, TypeOperationCaisseEnum.FERMETURE.value]
            )
        )
        .with_entities(func.coalesce(func.sum(OperationCaisse.montant), 0))
        .scalar()
    )

    relances_envoyees = db.query(func.count(Relance.id)).filter(
        func.date(Relance.created_at) == target_date
    ).scalar() or 0

    impayes_regles = db.query(func.count(DossierImpaye.id)).filter(
        func.date(DossierImpaye.date_cloture) == target_date
    ).scalar() or 0

    caisses_ouvertes = (
        db.query(func.count(Caisse.id))
        .filter(Caisse.etat == EtatCaisseEnum.OUVERTE.value)
        .scalar()
        or 0
    )

    return {
        "date_jour": target_date,
        "statut": StatutJournalEnum.EN_COURS.value,
        "nb_collectes": nb_collectes,
        "montant_collectes": montant_collectes,
        "nb_operations_caisse": nb_operations,
        "total_entrees_caisse": total_entrees,
        "total_sorties_caisse": total_sorties,
        "relances_envoyees": relances_envoyees,
        "impayes_regles": impayes_regles,
        "caisses_ouvertes": caisses_ouvertes,
        "toutes_caisses_fermees": caisses_ouvertes == 0,
    }


@router.get("/travaux/current", response_model=JournalComputedResponse)
def get_current_journal(
    jour: date = Query(default=date.today()),
    db: Session = Depends(get_db),
):
    stats = compute_journal_stats(db, jour)
    stored = db.query(JournalTravaux).filter(JournalTravaux.date_jour == jour).first()
    if stored:
        stats["statut"] = stored.statut.value
        stats["remarque"] = stored.remarque
    else:
        stats["remarque"] = None
    return JournalComputedResponse(**stats)


@router.get("/travaux/{jour}", response_model=JournalTravauxResponse)
def get_journal(jour: date, db: Session = Depends(get_db)):
    record = db.query(JournalTravaux).filter(JournalTravaux.date_jour == jour).first()
    if not record:
        raise HTTPException(status_code=404, detail="Journal introuvable pour cette date")
    return record


@router.post("/travaux/cloturer", response_model=JournalTravauxResponse)
def cloturer_journee(
    payload: ClotureRequest,
    jour: date = Query(default=date.today()),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    stats = compute_journal_stats(db, jour)

    if not stats["toutes_caisses_fermees"]:
        raise HTTPException(
            status_code=400,
            detail="Impossible de clôturer : certaines caisses sont encore ouvertes",
        )

    record = db.query(JournalTravaux).filter(JournalTravaux.date_jour == jour).first()
    if not record:
        record = JournalTravaux(date_jour=jour)
        db.add(record)

    record.nb_collectes = stats["nb_collectes"]
    record.montant_collectes = stats["montant_collectes"]
    record.nb_operations_caisse = stats["nb_operations_caisse"]
    record.total_entrees_caisse = stats["total_entrees_caisse"]
    record.total_sorties_caisse = stats["total_sorties_caisse"]
    record.relances_envoyees = stats["relances_envoyees"]
    record.impayes_regles = stats["impayes_regles"]
    record.remarque = payload.remarque
    record.statut = StatutJournalEnum.CLOTURE
    record.closed_at = datetime.utcnow()
    record.closed_by = getattr(current_user, "id", None)

    db.commit()
    db.refresh(record)
    return record


@router.get("/commissions/files", response_model=list[CommissionFichierResponse])
def list_commission_files(db: Session = Depends(get_db)):
    files = db.query(CommissionFichier).order_by(CommissionFichier.created_at.desc()).limit(50).all()
    return files


@router.post("/commissions/generer", response_model=CommissionGenerationResponse)
def generer_commissions(
    jour: date = Query(default=date.today()),
    format_fichier: str = Query(default="json", description="json, csv ou pdf"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    format_fichier = format_fichier.lower()
    if format_fichier not in {"json", "csv", "pdf"}:
        raise HTTPException(status_code=400, detail="Format de fichier non supporté (json, csv, pdf)")

    # Supprimer les commissions existantes pour cette date
    db.query(CommissionJournaliere).filter(CommissionJournaliere.date_jour == jour).delete()

    collectes = (
        db.query(
            InfoCollecte.collecteur_id,
            func.coalesce(func.sum(InfoCollecte.montant), 0).label("total_collecte"),
            func.coalesce(func.sum(InfoCollecte.commission), 0).label("commission"),
        )
        .filter(
            func.date(InfoCollecte.date_collecte) == jour,
            InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
            InfoCollecte.annule == False,
        )
        .group_by(InfoCollecte.collecteur_id)
        .all()
    )

    if not collectes:
        raise HTTPException(status_code=400, detail="Aucune collecte validée pour cette date")

    commissions_items: list[CommissionItem] = []
    for ligne in collectes:
        collecteur = db.query(Collecteur).filter(Collecteur.id == ligne.collecteur_id).first()
        commission_percent = (
            (Decimal(ligne.commission or 0) / Decimal(ligne.total_collecte or 1) * 100)
            if ligne.total_collecte
            else Decimal("0.00")
        )
        commissions_items.append(
            CommissionItem(
                collecteur_id=ligne.collecteur_id,
                collecteur_nom=f"{collecteur.nom} {collecteur.prenom}" if collecteur else None,
                montant_collecte=_compute_decimal(ligne.total_collecte),
                commission_montant=_compute_decimal(ligne.commission),
                commission_pourcentage=commission_percent.quantize(Decimal("0.01")),
                statut_paiement=StatutCommissionEnum.EN_ATTENTE.value,
            )
        )

    # Créer le fichier dans uploads/commissions
    uploads_dir = Path(__file__).resolve().parent.parent / "uploads" / "commissions"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    filename = f"commission_{jour.isoformat()}_{int(datetime.utcnow().timestamp())}.{format_fichier}"
    file_path = uploads_dir / filename
    if format_fichier == "json":
        _write_commissions_json(file_path, commissions_items)
    elif format_fichier == "csv":
        _write_commissions_csv(file_path, commissions_items)
    else:
        _write_commissions_pdf(file_path, commissions_items, jour)

    fichier = CommissionFichier(
        date_jour=jour,
        chemin=str(file_path.relative_to(Path(__file__).resolve().parent.parent / "uploads")),
        type_fichier=format_fichier,
        statut=StatutCommissionEnum.EN_ATTENTE,
        created_by=getattr(current_user, "id", None),
        file_metadata={
            "total_collecteurs": len(commissions_items),
            "format": format_fichier,
        },
    )
    db.add(fichier)
    db.commit()
    db.refresh(fichier)

    for item in commissions_items:
        db.add(
            CommissionJournaliere(
                date_jour=jour,
                collecteur_id=item.collecteur_id,
                montant_collecte=item.montant_collecte,
                commission_montant=item.commission_montant,
                commission_pourcentage=item.commission_pourcentage,
                statut_paiement=StatutCommissionEnum.EN_ATTENTE,
                fichier_id=fichier.id,
            )
        )

    db.commit()

    return CommissionGenerationResponse(
        fichier=fichier,
        commissions=commissions_items,
    )


@router.get("/commissions", response_model=list[CommissionJournalResponse])
def list_commissions(
    date_debut: Optional[date] = Query(default=None),
    date_fin: Optional[date] = Query(default=None),
    collecteur_id: Optional[int] = Query(default=None),
    statut: Optional[StatutCommissionEnum] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=500, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = (
        db.query(CommissionJournaliere, Collecteur)
        .join(Collecteur, CommissionJournaliere.collecteur_id == Collecteur.id, isouter=True)
    )

    if date_debut:
        query = query.filter(CommissionJournaliere.date_jour >= date_debut)
    if date_fin:
        query = query.filter(CommissionJournaliere.date_jour <= date_fin)
    if collecteur_id:
        query = query.filter(CommissionJournaliere.collecteur_id == collecteur_id)
    if statut:
        query = query.filter(CommissionJournaliere.statut_paiement == statut)

    records = (
        query.order_by(CommissionJournaliere.date_jour.desc(), CommissionJournaliere.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    response: list[CommissionJournalResponse] = []
    for commission, collecteur in records:
        if collecteur:
            collecteur_nom = f"{collecteur.nom or ''} {collecteur.prenom or ''}".strip() or None
            collecteur_matricule = collecteur.matricule
        else:
            collecteur_nom = None
            collecteur_matricule = None

        response.append(
            CommissionJournalResponse(
                id=commission.id,
                date_jour=commission.date_jour,
                collecteur_id=commission.collecteur_id,
                collecteur_nom=collecteur_nom,
                collecteur_matricule=collecteur_matricule,
                montant_collecte=commission.montant_collecte,
                commission_montant=commission.commission_montant,
                commission_pourcentage=commission.commission_pourcentage,
                statut_paiement=commission.statut_paiement.value
                if hasattr(commission.statut_paiement, "value")
                else commission.statut_paiement,
                fichier_id=commission.fichier_id,
                created_at=commission.created_at,
            )
        )

    return response


@router.get("/travaux/{jour}/collectes", response_model=list[InfoCollecteResponse])
def get_collectes_jour(
    jour: date,
    db: Session = Depends(get_db),
):
    """Récupère toutes les collectes validées pour une date donnée"""
    collectes = (
        db.query(InfoCollecte)
        .filter(
            func.date(InfoCollecte.date_collecte) == jour,
            InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
            InfoCollecte.annule == False,
        )
        .order_by(InfoCollecte.date_collecte.desc())
        .all()
    )
    return collectes


@router.get("/travaux/{jour}/operations", response_model=list[OperationCaisseResponse])
def get_operations_jour(
    jour: date,
    db: Session = Depends(get_db),
):
    """Récupère toutes les opérations de caisse pour une date donnée"""
    operations = (
        db.query(OperationCaisse)
        .filter(func.date(OperationCaisse.date_operation) == jour)
        .order_by(OperationCaisse.date_operation.desc())
        .all()
    )
    return operations


@router.get("/travaux/{jour}/relances", response_model=list)
def get_relances_jour(
    jour: date,
    db: Session = Depends(get_db),
):
    """Récupère toutes les relances envoyées pour une date donnée"""
    relances = (
        db.query(Relance)
        .filter(func.date(Relance.created_at) == jour)
        .order_by(Relance.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "contribuable_nom": f"{r.contribuable.nom} {r.contribuable.prenom}" if r.contribuable else None,
            "type_relance": r.type_relance.value,
            "statut": r.statut.value,
            "montant_due": float(r.montant_due),
            "date_envoi": r.date_envoi.isoformat() if r.date_envoi else None,
            "created_at": r.created_at.isoformat(),
        }
        for r in relances
    ]


@router.get("/commissions/{jour}/details", response_model=list[CommissionItem])
def get_commissions_details(
    jour: date,
    db: Session = Depends(get_db),
):
    """Récupère le détail des commissions journalières pour une date donnée"""
    commissions = (
        db.query(CommissionJournaliere)
        .filter(CommissionJournaliere.date_jour == jour)
        .order_by(CommissionJournaliere.commission_montant.desc())
        .all()
    )
    return [
        CommissionItem(
            collecteur_id=c.collecteur_id,
            collecteur_nom=f"{c.collecteur.nom} {c.collecteur.prenom}" if c.collecteur else None,
            montant_collecte=c.montant_collecte,
            commission_montant=c.commission_montant,
            commission_pourcentage=c.commission_pourcentage,
            statut_paiement=c.statut_paiement.value,
        )
        for c in commissions
    ]


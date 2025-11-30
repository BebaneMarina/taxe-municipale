"""
Seeders pour les nouvelles fonctionnalités : Caisses, Opérations, Journal, Commissions
Données de démonstration pour la présentation
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import (
    Caisse, OperationCaisse, JournalTravaux, CommissionFichier, CommissionJournaliere,
    Collecteur, InfoCollecte, Utilisateur, CoupureCaisse,
    TypeCaisseEnum, EtatCaisseEnum, TypeOperationCaisseEnum, TypeCoupureEnum,
    StatutJournalEnum, StatutCommissionEnum, StatutCollecteEnum
)
from datetime import datetime, date, timedelta
from decimal import Decimal
import random


def seed_coupures(db: Session):
    """Créer une base de coupures utilisées pour les caisses"""
    coupures_defaut = [
        {"valeur": Decimal("50"), "type_coupure": TypeCoupureEnum.PIECE, "ordre_affichage": 1},
        {"valeur": Decimal("100"), "type_coupure": TypeCoupureEnum.PIECE, "ordre_affichage": 2},
        {"valeur": Decimal("500"), "type_coupure": TypeCoupureEnum.BILLET, "ordre_affichage": 3},
        {"valeur": Decimal("1000"), "type_coupure": TypeCoupureEnum.BILLET, "ordre_affichage": 4},
        {"valeur": Decimal("2000"), "type_coupure": TypeCoupureEnum.BILLET, "ordre_affichage": 5},
        {"valeur": Decimal("5000"), "type_coupure": TypeCoupureEnum.BILLET, "ordre_affichage": 6},
        {"valeur": Decimal("10000"), "type_coupure": TypeCoupureEnum.BILLET, "ordre_affichage": 7},
    ]

    inserted = 0
    for coupure in coupures_defaut:
        existing = (
            db.query(CoupureCaisse)
            .filter(
                CoupureCaisse.valeur == coupure["valeur"],
                CoupureCaisse.type_coupure == coupure["type_coupure"].value,
                func.upper(CoupureCaisse.devise) == "XAF",
            )
            .first()
        )
        if existing:
            continue

        db_coupure = CoupureCaisse(
            valeur=coupure["valeur"],
            devise="XAF",
            type_coupure=coupure["type_coupure"],
            ordre_affichage=coupure["ordre_affichage"],
            actif=True,
        )
        db.add(db_coupure)
        inserted += 1

    if inserted:
        db.commit()
    print(f"✅ Coupures créées ({inserted})")


def seed_caisses(db: Session):
    """Créer des caisses de démonstration pour les collecteurs"""
    collecteurs = db.query(Collecteur).filter(Collecteur.actif == True).limit(5).all()
    
    if not collecteurs:
        print("⚠️ Aucun collecteur trouvé. Créez d'abord des collecteurs.")
        return
    
    caisses_data = []
    for i, collecteur in enumerate(collecteurs):
        # Caisse physique
        caisses_data.append({
            "collecteur_id": collecteur.id,
            "type_caisse": TypeCaisseEnum.PHYSIQUE,
            "code": f"CAISSE-PHYS-{collecteur.matricule}",
            "nom": f"Caisse physique {collecteur.nom}",
            "solde_initial": Decimal("50000.00"),
            "solde_actuel": Decimal("75000.00") if i % 2 == 0 else Decimal("45000.00"),
            "etat": EtatCaisseEnum.OUVERTE if i % 2 == 0 else EtatCaisseEnum.FERMEE,
            "date_ouverture": datetime.utcnow() - timedelta(hours=2) if i % 2 == 0 else None,
            "notes": f"Caisse principale pour {collecteur.nom} {collecteur.prenom}",
            "actif": True
        })
        
        # Caisse en ligne
        caisses_data.append({
            "collecteur_id": collecteur.id,
            "type_caisse": TypeCaisseEnum.EN_LIGNE,
            "code": f"CAISSE-ONLINE-{collecteur.matricule}",
            "nom": f"Caisse mobile {collecteur.nom}",
            "solde_initial": Decimal("0.00"),
            "solde_actuel": Decimal("25000.00") if i % 2 == 0 else Decimal("15000.00"),
            "etat": EtatCaisseEnum.OUVERTE if i % 2 == 0 else EtatCaisseEnum.FERMEE,
            "date_ouverture": datetime.utcnow() - timedelta(hours=1) if i % 2 == 0 else None,
            "notes": f"Caisse mobile money pour {collecteur.nom}",
            "actif": True
        })
    
    for caisse_data in caisses_data:
        existing = db.query(Caisse).filter(Caisse.code == caisse_data["code"]).first()
        if not existing:
            caisse = Caisse(**caisse_data)
            db.add(caisse)
    
    db.commit()
    print(f"✅ {len(caisses_data)} caisses créées")


def seed_operations_caisse(db: Session):
    """Créer des opérations de caisse de démonstration"""
    caisses = db.query(Caisse).filter(Caisse.actif == True).all()
    collecteurs = db.query(Collecteur).filter(Collecteur.actif == True).all()
    
    if not caisses or not collecteurs:
        print("⚠️ Aucune caisse ou collecteur trouvé")
        return
    
    operations = []
    today = datetime.utcnow().replace(hour=8, minute=0, second=0, microsecond=0)
    
    for caisse in caisses:
        collecteur = next((c for c in collecteurs if c.id == caisse.collecteur_id), None)
        if not collecteur:
            continue
        
        solde_actuel = caisse.solde_initial
        
        # Opération d'ouverture
        if caisse.etat == EtatCaisseEnum.OUVERTE:
            op_ouverture = OperationCaisse(
                caisse_id=caisse.id,
                collecteur_id=caisse.collecteur_id,
                type_operation=TypeOperationCaisseEnum.OUVERTURE,
                montant=caisse.solde_initial,
                libelle=f"Ouverture de caisse - Solde initial",
                solde_avant=Decimal("0.00"),
                solde_apres=caisse.solde_initial,
                date_operation=today - timedelta(hours=2),
                reference=f"OP-{caisse.code}-{int(today.timestamp())}"
            )
            operations.append(op_ouverture)
            solde_actuel = caisse.solde_initial
        
        # Opérations d'entrée (collectes)
        for i in range(random.randint(3, 8)):
            montant = Decimal(random.randint(5000, 50000))
            solde_avant = solde_actuel
            solde_actuel += montant
            
            op_entree = OperationCaisse(
                caisse_id=caisse.id,
                collecteur_id=caisse.collecteur_id,
                type_operation=TypeOperationCaisseEnum.ENTREE,
                montant=montant,
                libelle=f"Collecte #{i+1} - {collecteur.nom}",
                solde_avant=solde_avant,
                solde_apres=solde_actuel,
                date_operation=today - timedelta(hours=2-i*0.3),
                reference=f"ENT-{caisse.code}-{i+1}-{int(today.timestamp())}"
            )
            operations.append(op_entree)
        
        # Opération de sortie (remise)
        if random.random() > 0.5:
            montant_sortie = Decimal(random.randint(10000, 30000))
            solde_avant = solde_actuel
            solde_actuel -= montant_sortie
            
            op_sortie = OperationCaisse(
                caisse_id=caisse.id,
                collecteur_id=caisse.collecteur_id,
                type_operation=TypeOperationCaisseEnum.SORTIE,
                montant=montant_sortie,
                libelle="Remise en banque",
                solde_avant=solde_avant,
                solde_apres=solde_actuel,
                date_operation=today - timedelta(minutes=30),
                reference=f"SORT-{caisse.code}-{int(today.timestamp())}"
            )
            operations.append(op_sortie)
    
    for op in operations:
        existing = db.query(OperationCaisse).filter(OperationCaisse.reference == op.reference).first()
        if not existing:
            db.add(op)
    
    db.commit()
    print(f"✅ {len(operations)} opérations de caisse créées")


def seed_journal_travaux(db: Session):
    """Créer des journaux de travaux pour les derniers jours"""
    dates = [
        date.today() - timedelta(days=i) for i in range(7)
    ]
    
    collectes_query = db.query(InfoCollecte).filter(
        InfoCollecte.statut == StatutCollecteEnum.COMPLETED,
        InfoCollecte.annule == False
    )
    
    for jour in dates:
        existing = db.query(JournalTravaux).filter(JournalTravaux.date_jour == jour).first()
        if existing:
            continue
        
        # Compter les collectes du jour
        collectes_du_jour = collectes_query.filter(
            func.date(InfoCollecte.date_collecte) == jour
        ).all()
        
        nb_collectes = len(collectes_du_jour)
        montant_collectes = sum(Decimal(str(c.montant)) for c in collectes_du_jour)
        
        # Compter les opérations
        operations_du_jour = db.query(OperationCaisse).filter(
            func.date(OperationCaisse.date_operation) == jour
        ).all()
        
        nb_operations = len(operations_du_jour)
        total_entrees = sum(Decimal(str(op.montant)) for op in operations_du_jour 
                           if op.type_operation in [TypeOperationCaisseEnum.ENTREE.value, TypeOperationCaisseEnum.OUVERTURE.value])
        total_sorties = sum(Decimal(str(op.montant)) for op in operations_du_jour 
                           if op.type_operation in [TypeOperationCaisseEnum.SORTIE.value, TypeOperationCaisseEnum.FERMETURE.value])
        
        # Compter les relances (simulation)
        relances_envoyees = random.randint(0, 15) if jour < date.today() else 0
        
        # Compter les impayés réglés (simulation)
        impayes_regles = random.randint(0, 5) if jour < date.today() else 0
        
        statut = StatutJournalEnum.CLOTURE if jour < date.today() - timedelta(days=1) else StatutJournalEnum.EN_COURS
        
        journal = JournalTravaux(
            date_jour=jour,
            statut=statut,
            nb_collectes=nb_collectes,
            montant_collectes=montant_collectes,
            nb_operations_caisse=nb_operations,
            total_entrees_caisse=total_entrees,
            total_sorties_caisse=total_sorties,
            relances_envoyees=relances_envoyees,
            impayes_regles=impayes_regles,
            remarque=f"Journal automatique pour {jour}" if jour < date.today() else None,
            closed_at=datetime.utcnow() - timedelta(days=(date.today() - jour).days) if statut == StatutJournalEnum.CLOTURE else None
        )
        db.add(journal)
    
    db.commit()
    print(f"✅ {len(dates)} journaux de travaux créés")


def seed_commissions(db: Session):
    """Créer des fichiers de commissions et commissions journalières"""
    collecteurs = db.query(Collecteur).filter(Collecteur.actif == True).limit(5).all()
    
    if not collecteurs:
        print("⚠️ Aucun collecteur trouvé")
        return
    
    # Créer des fichiers de commissions pour les 3 derniers jours
    dates = [date.today() - timedelta(days=i) for i in range(1, 4)]
    utilisateurs = db.query(Utilisateur).limit(1).all()
    created_by = utilisateurs[0].id if utilisateurs else None
    
    for jour in dates:
        # Vérifier si fichier existe déjà
        existing_file = db.query(CommissionFichier).filter(
            CommissionFichier.date_jour == jour
        ).first()
        
        if existing_file:
            continue
        
        # Calculer les commissions pour chaque collecteur
        commissions_items = []
        total_collecte_global = Decimal("0.00")
        
        for collecteur in collecteurs:
            # Simuler des collectes pour ce collecteur ce jour-là
            montant_collecte = Decimal(random.randint(50000, 500000))
            commission_pourcentage = Decimal("5.00")  # 5% de commission
            commission_montant = (montant_collecte * commission_pourcentage / 100).quantize(Decimal("0.01"))
            
            total_collecte_global += montant_collecte
            
            commission_jour = CommissionJournaliere(
                date_jour=jour,
                collecteur_id=collecteur.id,
                montant_collecte=montant_collecte,
                commission_montant=commission_montant,
                commission_pourcentage=commission_pourcentage,
                statut_paiement=StatutCommissionEnum.EN_ATTENTE if jour == dates[0] else StatutCommissionEnum.PAYEE,
                fichier_id=None  # Sera mis à jour après création du fichier
            )
            commissions_items.append(commission_jour)
        
        # Créer le fichier de commission
        fichier = CommissionFichier(
            date_jour=jour,
            chemin=f"commissions/commission_{jour.isoformat()}_demo.json",
            type_fichier="json",
            statut=StatutCommissionEnum.EN_ATTENTE if jour == dates[0] else StatutCommissionEnum.ENVOYEE,
            created_by=created_by,
            file_metadata={
                "total_collecteurs": len(collecteurs),
                "format": "json",
                "montant_total_collecte": float(total_collecte_global)
            }
        )
        db.add(fichier)
        db.flush()  # Pour obtenir l'ID
        
        # Lier les commissions au fichier
        for comm in commissions_items:
            comm.fichier_id = fichier.id
            db.add(comm)
    
    db.commit()
    print(f"✅ Fichiers de commissions créés pour {len(dates)} jours")


def seed_all(db: Session):
    """Exécuter tous les seeders"""
    print("\n🌱 Démarrage des seeders pour caisses, journal et commissions...\n")
    
    seed_coupures(db)
    seed_caisses(db)
    seed_operations_caisse(db)
    seed_journal_travaux(db)
    seed_commissions(db)
    
    print("\n✅ Tous les seeders ont été exécutés avec succès!\n")


if __name__ == "__main__":
    from database.database import SessionLocal
    
    db = SessionLocal()
    try:
        seed_all(db)
    finally:
        db.close()


"""
Seeders avec données réelles du Gabon (Libreville)
"""

from sqlalchemy.orm import Session
from database.models import (
    Service, TypeTaxe, Zone, Quartier, TypeContribuable,
    Collecteur, Contribuable, Taxe, AffectationTaxe, InfoCollecte,
    StatutCollecteurEnum, EtatCollecteurEnum, PeriodiciteEnum,
    TypePaiementEnum, StatutCollecteEnum
)
from datetime import datetime, timedelta
import random
import json


# ==================== DONNÉES RÉELLES DU GABON ====================

# Zones de Libreville
ZONES_LIBREVILLE = [
    {"nom": "Centre-ville", "code": "ZONE-001", "description": "Zone centrale de Libreville"},
    {"nom": "Akanda", "code": "ZONE-002", "description": "Zone Akanda"},
    {"nom": "Ntoum", "code": "ZONE-003", "description": "Zone Ntoum"},
    {"nom": "Owendo", "code": "ZONE-004", "description": "Zone portuaire d'Owendo"},
]

# Quartiers de Libreville (réels)
QUARTIERS_LIBREVILLE = [
    # Centre-ville
    {"nom": "Mont-Bouët", "code": "Q-001", "zone": "ZONE-001"},
    {"nom": "Glass", "code": "Q-002", "zone": "ZONE-001"},
    {"nom": "Quartier Louis", "code": "Q-003", "zone": "ZONE-001"},
    {"nom": "Nombakélé", "code": "Q-004", "zone": "ZONE-001"},
    {"nom": "Akébé", "code": "Q-005", "zone": "ZONE-001"},
    {"nom": "Oloumi", "code": "Q-006", "zone": "ZONE-001"},
    
    # Akanda
    {"nom": "Cocotiers", "code": "Q-007", "zone": "ZONE-002"},
    {"nom": "Angondjé", "code": "Q-008", "zone": "ZONE-002"},
    {"nom": "Melen", "code": "Q-009", "zone": "ZONE-002"},
    
    # Ntoum
    {"nom": "Ntoum Centre", "code": "Q-010", "zone": "ZONE-003"},
    
    # Owendo
    {"nom": "Owendo Centre", "code": "Q-011", "zone": "ZONE-004"},
    {"nom": "PK8", "code": "Q-012", "zone": "ZONE-004"},
]

# Types de contribuables
TYPES_CONTRIBUABLES = [
    {"nom": "Particulier", "code": "TC-001"},
    {"nom": "Entreprise", "code": "TC-002"},
    {"nom": "Commerce", "code": "TC-003"},
    {"nom": "Marché", "code": "TC-004"},
    {"nom": "Transport", "code": "TC-005"},
]

# Services de la mairie
SERVICES_MAIRIE = [
    {"nom": "Service des Finances", "code": "SRV-001", "description": "Gestion financière"},
    {"nom": "Service des Marchés", "code": "SRV-002", "description": "Gestion des marchés"},
    {"nom": "Service de l'Urbanisme", "code": "SRV-003", "description": "Urbanisme et aménagement"},
    {"nom": "Service des Transports", "code": "SRV-004", "description": "Gestion des transports"},
    {"nom": "Service des Commerces", "code": "SRV-005", "description": "Gestion des commerces"},
]

# Types de taxes municipales (réelles au Gabon)
TYPES_TAXES = [
    {"nom": "Taxe de Marché", "code": "TT-001", "description": "Taxe sur les activités de marché"},
    {"nom": "Taxe d'Occupation du Domaine Public", "code": "TT-002", "description": "Taxe pour occupation de l'espace public"},
    {"nom": "Taxe sur les Activités Commerciales", "code": "TT-003", "description": "Taxe sur les activités commerciales"},
    {"nom": "Taxe de Stationnement", "code": "TT-004", "description": "Taxe de stationnement"},
    {"nom": "Taxe de Voirie", "code": "TT-005", "description": "Taxe de voirie"},
    {"nom": "Taxe d'Enlèvement des Ordures", "code": "TT-006", "description": "Taxe pour l'enlèvement des ordures"},
    {"nom": "Taxe sur les Transports", "code": "TT-007", "description": "Taxe sur les activités de transport"},
]


def seed_zones(db: Session):
    """Seed des zones"""
    for zone_data in ZONES_LIBREVILLE:
        zone = db.query(Zone).filter(Zone.code == zone_data["code"]).first()
        if not zone:
            zone = Zone(**zone_data)
            db.add(zone)
    db.commit()
    print("✅ Zones créées")


def seed_quartiers(db: Session):
    """Seed des quartiers"""
    for quartier_data in QUARTIERS_LIBREVILLE:
        quartier = db.query(Quartier).filter(Quartier.code == quartier_data["code"]).first()
        if not quartier:
            zone = db.query(Zone).filter(Zone.code == quartier_data["zone"]).first()
            if zone:
                quartier_data_copy = quartier_data.copy()
                quartier_data_copy["zone_id"] = zone.id
                del quartier_data_copy["zone"]
                quartier = Quartier(**quartier_data_copy)
                db.add(quartier)
    db.commit()
    print("✅ Quartiers créés")


def seed_types_contribuables(db: Session):
    """Seed des types de contribuables"""
    for type_data in TYPES_CONTRIBUABLES:
        type_contrib = db.query(TypeContribuable).filter(
            TypeContribuable.code == type_data["code"]
        ).first()
        if not type_contrib:
            type_contrib = TypeContribuable(**type_data)
            db.add(type_contrib)
    db.commit()
    print("✅ Types de contribuables créés")


def seed_services(db: Session):
    """Seed des services"""
    for service_data in SERVICES_MAIRIE:
        service = db.query(Service).filter(Service.code == service_data["code"]).first()
        if not service:
            service = Service(**service_data)
            db.add(service)
    db.commit()
    print("✅ Services créés")


def seed_types_taxes(db: Session):
    """Seed des types de taxes"""
    for type_data in TYPES_TAXES:
        type_taxe = db.query(TypeTaxe).filter(TypeTaxe.code == type_data["code"]).first()
        if not type_taxe:
            type_taxe = TypeTaxe(**type_data)
            db.add(type_taxe)
    db.commit()
    print("✅ Types de taxes créés")


def seed_taxes(db: Session):
    """Seed des taxes"""
    types_taxes = db.query(TypeTaxe).all()
    services = db.query(Service).all()
    
    if not types_taxes or not services:
        print("⚠️ Créez d'abord les types de taxes et services")
        return
    
    taxes_data = [
        {
            "nom": "Taxe de Marché Journalière",
            "code": "TAX-001",
            "description": "Taxe quotidienne pour les vendeurs de marché",
            "montant": 1000.00,
            "montant_variable": False,
            "periodicite": PeriodiciteEnum.JOURNALIERE,
            "type_taxe_id": types_taxes[0].id,
            "service_id": services[1].id,
            "commission_pourcentage": 5.00
        },
        {
            "nom": "Taxe de Marché Mensuelle",
            "code": "TAX-002",
            "description": "Taxe mensuelle pour les vendeurs de marché",
            "montant": 25000.00,
            "montant_variable": False,
            "periodicite": PeriodiciteEnum.MENSUELLE,
            "type_taxe_id": types_taxes[0].id,
            "service_id": services[1].id,
            "commission_pourcentage": 5.00
        },
        {
            "nom": "Taxe d'Occupation Domaine Public",
            "code": "TAX-003",
            "description": "Taxe pour occupation de l'espace public",
            "montant": 5000.00,
            "montant_variable": True,
            "periodicite": PeriodiciteEnum.MENSUELLE,
            "type_taxe_id": types_taxes[1].id,
            "service_id": services[2].id,
            "commission_pourcentage": 3.00
        },
        {
            "nom": "Taxe Commerciale Mensuelle",
            "code": "TAX-004",
            "description": "Taxe sur les activités commerciales",
            "montant": 15000.00,
            "montant_variable": False,
            "periodicite": PeriodiciteEnum.MENSUELLE,
            "type_taxe_id": types_taxes[2].id,
            "service_id": services[4].id,
            "commission_pourcentage": 4.00
        },
        {
            "nom": "Taxe de Stationnement",
            "code": "TAX-005",
            "description": "Taxe de stationnement journalière",
            "montant": 500.00,
            "montant_variable": False,
            "periodicite": PeriodiciteEnum.JOURNALIERE,
            "type_taxe_id": types_taxes[3].id,
            "service_id": services[3].id,
            "commission_pourcentage": 2.00
        },
        {
            "nom": "Taxe d'Enlèvement Ordures",
            "code": "TAX-006",
            "description": "Taxe pour l'enlèvement des ordures ménagères",
            "montant": 3000.00,
            "montant_variable": False,
            "periodicite": PeriodiciteEnum.MENSUELLE,
            "type_taxe_id": types_taxes[5].id,
            "service_id": services[0].id,
            "commission_pourcentage": 0.00
        },
    ]
    
    for taxe_data in taxes_data:
        taxe = db.query(Taxe).filter(Taxe.code == taxe_data["code"]).first()
        if not taxe:
            taxe = Taxe(**taxe_data)
            db.add(taxe)
    db.commit()
    print("✅ Taxes créées")


def seed_collecteurs(db: Session):
    """Seed des collecteurs"""
    zones = db.query(Zone).all()
    
    collecteurs_data = [
        {
            "nom": "MBOUMBA",
            "prenom": "Jean",
            "email": "jean.mboumba@mairie-libreville.ga",
            "telephone": "+241062345678",
            "matricule": "COL-001",
            "statut": StatutCollecteurEnum.ACTIVE,
            "etat": EtatCollecteurEnum.DECONNECTE,
            "zone_id": zones[0].id if zones else None,
            "heure_cloture": "18:00"
        },
        {
            "nom": "NDONG",
            "prenom": "Marie",
            "email": "marie.ndong@mairie-libreville.ga",
            "telephone": "+241062345679",
            "matricule": "COL-002",
            "statut": StatutCollecteurEnum.ACTIVE,
            "etat": EtatCollecteurEnum.CONNECTE,
            "zone_id": zones[1].id if len(zones) > 1 else None,
            "heure_cloture": "18:00"
        },
        {
            "nom": "OBAME",
            "prenom": "Pierre",
            "email": "pierre.obame@mairie-libreville.ga",
            "telephone": "+241062345680",
            "matricule": "COL-003",
            "statut": StatutCollecteurEnum.ACTIVE,
            "etat": EtatCollecteurEnum.DECONNECTE,
            "zone_id": zones[2].id if len(zones) > 2 else None,
            "heure_cloture": "18:00"
        },
    ]
    
    for collecteur_data in collecteurs_data:
        collecteur = db.query(Collecteur).filter(
            Collecteur.matricule == collecteur_data["matricule"]
        ).first()
        if not collecteur:
            collecteur = Collecteur(**collecteur_data)
            db.add(collecteur)
    db.commit()
    print("✅ Collecteurs créés")


def seed_contribuables(db: Session):
    """Seed des contribuables"""
    types_contrib = db.query(TypeContribuable).all()
    quartiers = db.query(Quartier).all()
    collecteurs = db.query(Collecteur).all()
    
    if not types_contrib or not quartiers or not collecteurs:
        print("⚠️ Créez d'abord les types, quartiers et collecteurs")
        return
    
    prenoms_gabonais = ["Jean", "Marie", "Pierre", "Paul", "Sophie", "Luc", "Anne", "David"]
    noms_gabonais = ["MBOUMBA", "NDONG", "OBAME", "BONGO", "MBOUMBA", "ESSONO", "MVE", "MINTSA"]
    
    contribuables_data = []
    for i in range(20):  # Créer 20 contribuables
        contribuables_data.append({
            "nom": random.choice(noms_gabonais),
            "prenom": random.choice(prenoms_gabonais),
            "email": f"contribuable{i+1}@example.ga",
            "telephone": f"+24106{random.randint(1000000, 9999999)}",
            "type_contribuable_id": random.choice(types_contrib).id,
            "quartier_id": random.choice(quartiers).id,
            "collecteur_id": random.choice(collecteurs).id,
            "adresse": f"Rue {random.choice(['Avenue', 'Boulevard', 'Rue'])} {random.randint(1, 100)}",
            "latitude": round(random.uniform(0.3, 0.5), 8),  # Coordonnées approximatives Libreville
            "longitude": round(random.uniform(9.3, 9.5), 8),
            "numero_identification": f"CTB-{str(i+1).zfill(4)}"
        })
    
    for contrib_data in contribuables_data:
        contrib = db.query(Contribuable).filter(
            Contribuable.numero_identification == contrib_data["numero_identification"]
        ).first()
        if not contrib:
            contrib = Contribuable(**contrib_data)
            db.add(contrib)
    db.commit()
    print("✅ Contribuables créés")


def seed_affectations_taxes(db: Session):
    """Seed des affectations de taxes"""
    contribuables = db.query(Contribuable).all()
    taxes = db.query(Taxe).all()
    
    if not contribuables or not taxes:
        print("⚠️ Créez d'abord les contribuables et taxes")
        return
    
    for contrib in contribuables[:15]:  # Affecter des taxes à 15 contribuables
        # Affecter 1-3 taxes par contribuable
        nb_taxes = random.randint(1, 3)
        taxes_selected = random.sample(taxes, min(nb_taxes, len(taxes)))
        
        for taxe in taxes_selected:
            affectation = db.query(AffectationTaxe).filter(
                AffectationTaxe.contribuable_id == contrib.id,
                AffectationTaxe.taxe_id == taxe.id,
                AffectationTaxe.actif == True
            ).first()
            
            if not affectation:
                affectation = AffectationTaxe(
                    contribuable_id=contrib.id,
                    taxe_id=taxe.id,
                    date_debut=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                    date_fin=None,
                    montant_custom=None if not taxe.montant_variable else float(taxe.montant) * random.uniform(0.8, 1.2),
                    actif=True
                )
                db.add(affectation)
    db.commit()
    print("✅ Affectations de taxes créées")


def seed_collectes(db: Session):
    """Seed des collectes"""
    affectations = db.query(AffectationTaxe).filter(AffectationTaxe.actif == True).all()
    collecteurs = db.query(Collecteur).all()
    
    if not affectations or not collecteurs:
        print("⚠️ Créez d'abord les affectations et collecteurs")
        return
    
    # Créer des collectes pour les 30 derniers jours
    for i in range(50):  # 50 collectes
        affectation = random.choice(affectations)
        contribuable = affectation.contribuable
        taxe = affectation.taxe
        collecteur = random.choice(collecteurs)
        
        montant = float(affectation.montant_custom) if affectation.montant_custom else float(taxe.montant)
        commission = montant * (float(taxe.commission_pourcentage) / 100)
        
        date_collecte = datetime.utcnow() - timedelta(days=random.randint(0, 30))
        
        reference = f"COL-{date_collecte.strftime('%Y%m%d')}-{str(i+1).zfill(4)}"
        
        collecte = InfoCollecte(
            contribuable_id=contribuable.id,
            taxe_id=taxe.id,
            collecteur_id=collecteur.id,
            montant=montant,
            commission=commission,
            type_paiement=random.choice(list(TypePaiementEnum)),
            statut=random.choice([StatutCollecteEnum.COMPLETED, StatutCollecteEnum.COMPLETED, StatutCollecteEnum.COMPLETED, StatutCollecteEnum.FAILED]),
            reference=reference,
            billetage=json.dumps({"5000": random.randint(0, 10), "1000": random.randint(0, 20)}) if random.choice([True, False]) else None,
            date_collecte=date_collecte,
            sms_envoye=random.choice([True, False]),
            ticket_imprime=random.choice([True, False]),
            annule=False
        )
        db.add(collecte)
    db.commit()
    print("✅ Collectes créées")


def seed_all(db: Session):
    """Exécute tous les seeders"""
    print("🌱 Début du seeding...")
    seed_zones(db)
    seed_quartiers(db)
    seed_types_contribuables(db)
    seed_services(db)
    seed_types_taxes(db)
    seed_taxes(db)
    seed_collecteurs(db)
    seed_contribuables(db)
    seed_affectations_taxes(db)
    seed_collectes(db)
    
    # Créer l'utilisateur admin
    from database.seeders_auth import seed_admin_user
    seed_admin_user(db)
    
    print("✅ Seeding terminé avec succès!")


if __name__ == "__main__":
    from database.database import SessionLocal
    import json
    
    db = SessionLocal()
    try:
        seed_all(db)
    finally:
        db.close()


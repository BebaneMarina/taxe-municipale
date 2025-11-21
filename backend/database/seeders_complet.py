"""
Script complet pour insérer des données dans la base de données
Au moins 50 entrées par table avec des données gabonaises réalistes
"""

from sqlalchemy.orm import Session
from database.models import (
    Service, TypeTaxe, Zone, Quartier, TypeContribuable,
    Collecteur, Contribuable, Taxe, AffectationTaxe, InfoCollecte, Utilisateur,
    StatutCollecteurEnum, EtatCollecteurEnum, PeriodiciteEnum,
    TypePaiementEnum, StatutCollecteEnum, RoleEnum
)
from datetime import datetime, timedelta
import random
import json
from auth.security import get_password_hash

# ==================== DONNÉES RÉELLES DU GABON ====================

# Noms gabonais courants
PRENOMS_GABONAIS = [
    "Jean", "Marie", "Pierre", "Paul", "Sophie", "Luc", "Anne", "David",
    "François", "Catherine", "Michel", "Isabelle", "André", "Christine",
    "Philippe", "Nathalie", "Laurent", "Valérie", "Olivier", "Sandrine",
    "Stéphane", "Céline", "Nicolas", "Julie", "Sébastien", "Caroline",
    "Julien", "Emilie", "Thomas", "Aurélie", "Antoine", "Marion",
    "Boris", "Camille", "Yannick", "Élodie", "Fabrice", "Amélie",
    "Romain", "Claire", "Vincent", "Laura", "Maxime", "Pauline",
    "Alexandre", "Manon", "Guillaume", "Émilie", "Jérôme", "Sarah"
]

NOMS_GABONAIS = [
    "MBOUMBA", "NDONG", "OBAME", "BONGO", "ESSONO", "MVE", "MINTSA",
    "MBOUMBA", "NDONG", "OBAME", "BONGO", "ESSONO", "MVE", "MINTSA",
    "MBOUMBA", "NDONG", "OBAME", "BONGO", "ESSONO", "MVE", "MINTSA",
    "MBOUMBA", "NDONG", "OBAME", "BONGO", "ESSONO", "MVE", "MINTSA",
    "MBOUMBA", "NDONG", "OBAME", "BONGO", "ESSONO", "MVE", "MINTSA",
    "MBOUMBA", "NDONG", "OBAME", "BONGO", "ESSONO", "MVE", "MINTSA",
    "MBOUMBA", "NDONG", "OBAME", "BONGO", "ESSONO", "MVE", "MINTSA",
    "MBOUMBA", "NDONG", "OBAME", "BONGO", "ESSONO", "MVE", "MINTSA"
]

# Zones de Libreville (réelles)
ZONES_LIBREVILLE = [
    {"nom": "Centre-ville", "code": "ZONE-001", "description": "Zone centrale de Libreville"},
    {"nom": "Akanda", "code": "ZONE-002", "description": "Zone Akanda"},
    {"nom": "Ntoum", "code": "ZONE-003", "description": "Zone Ntoum"},
    {"nom": "Owendo", "code": "ZONE-004", "description": "Zone portuaire d'Owendo"},
    {"nom": "Port-Gentil", "code": "ZONE-005", "description": "Zone Port-Gentil"},
    {"nom": "Franceville", "code": "ZONE-006", "description": "Zone Franceville"},
]

# Quartiers de Libreville (réels et étendus)
QUARTIERS_LIBREVILLE = [
    # Centre-ville
    {"nom": "Mont-Bouët", "code": "Q-001", "zone": "ZONE-001"},
    {"nom": "Glass", "code": "Q-002", "zone": "ZONE-001"},
    {"nom": "Quartier Louis", "code": "Q-003", "zone": "ZONE-001"},
    {"nom": "Nombakélé", "code": "Q-004", "zone": "ZONE-001"},
    {"nom": "Akébé", "code": "Q-005", "zone": "ZONE-001"},
    {"nom": "Oloumi", "code": "Q-006", "zone": "ZONE-001"},
    {"nom": "Batterie IV", "code": "Q-007", "zone": "ZONE-001"},
    {"nom": "Derrière la Prison", "code": "Q-008", "zone": "ZONE-001"},
    {"nom": "Charbonnages", "code": "Q-009", "zone": "ZONE-001"},
    {"nom": "Lalala", "code": "Q-010", "zone": "ZONE-001"},
    
    # Akanda
    {"nom": "Cocotiers", "code": "Q-011", "zone": "ZONE-002"},
    {"nom": "Angondjé", "code": "Q-012", "zone": "ZONE-002"},
    {"nom": "Melen", "code": "Q-013", "zone": "ZONE-002"},
    {"nom": "Nkoltang", "code": "Q-014", "zone": "ZONE-002"},
    {"nom": "Minko", "code": "Q-015", "zone": "ZONE-002"},
    
    # Ntoum
    {"nom": "Ntoum Centre", "code": "Q-016", "zone": "ZONE-003"},
    {"nom": "Mveng", "code": "Q-017", "zone": "ZONE-003"},
    {"nom": "Mvouli", "code": "Q-018", "zone": "ZONE-003"},
    
    # Owendo
    {"nom": "Owendo Centre", "code": "Q-019", "zone": "ZONE-004"},
    {"nom": "PK8", "code": "Q-020", "zone": "ZONE-004"},
    {"nom": "PK12", "code": "Q-021", "zone": "ZONE-004"},
    {"nom": "PK15", "code": "Q-022", "zone": "ZONE-004"},
    
    # Port-Gentil
    {"nom": "Port-Gentil Centre", "code": "Q-023", "zone": "ZONE-005"},
    {"nom": "Ivea", "code": "Q-024", "zone": "ZONE-005"},
    {"nom": "Nzeng-Ayong", "code": "Q-025", "zone": "ZONE-005"},
    
    # Franceville
    {"nom": "Franceville Centre", "code": "Q-026", "zone": "ZONE-006"},
    {"nom": "Mounana", "code": "Q-027", "zone": "ZONE-006"},
    {"nom": "Okondja", "code": "Q-028", "zone": "ZONE-006"},
]

# Types de contribuables
TYPES_CONTRIBUABLES = [
    {"nom": "Particulier", "code": "TC-001"},
    {"nom": "Entreprise", "code": "TC-002"},
    {"nom": "Commerce", "code": "TC-003"},
    {"nom": "Marché", "code": "TC-004"},
    {"nom": "Transport", "code": "TC-005"},
    {"nom": "Restaurant", "code": "TC-006"},
    {"nom": "Hôtel", "code": "TC-007"},
    {"nom": "Boutique", "code": "TC-008"},
]

# Services de la mairie
SERVICES_MAIRIE = [
    {"nom": "Service des Finances", "code": "SRV-001", "description": "Gestion financière"},
    {"nom": "Service des Marchés", "code": "SRV-002", "description": "Gestion des marchés"},
    {"nom": "Service de l'Urbanisme", "code": "SRV-003", "description": "Urbanisme et aménagement"},
    {"nom": "Service des Transports", "code": "SRV-004", "description": "Gestion des transports"},
    {"nom": "Service des Commerces", "code": "SRV-005", "description": "Gestion des commerces"},
    {"nom": "Service de l'Environnement", "code": "SRV-006", "description": "Environnement et propreté"},
    {"nom": "Service de la Voirie", "code": "SRV-007", "description": "Entretien de la voirie"},
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
    {"nom": "Taxe sur les Débits de Boissons", "code": "TT-008", "description": "Taxe sur les débits de boissons"},
    {"nom": "Taxe sur les Hôtels", "code": "TT-009", "description": "Taxe sur les établissements hôteliers"},
    {"nom": "Taxe sur les Publicités", "code": "TT-010", "description": "Taxe sur les publicités et enseignes"},
]


def seed_zones(db: Session, count=50):
    """Seed des zones"""
    zones_created = 0
    for zone_data in ZONES_LIBREVILLE:
        zone = db.query(Zone).filter(Zone.code == zone_data["code"]).first()
        if not zone:
            zone = Zone(**zone_data)
            db.add(zone)
            zones_created += 1
    
    # Créer des zones supplémentaires si nécessaire
    for i in range(len(ZONES_LIBREVILLE), count):
        code = f"ZONE-{str(i+1).zfill(3)}"
        # Vérifier si la zone existe déjà
        existing_zone = db.query(Zone).filter(Zone.code == code).first()
        if not existing_zone:
            zone = Zone(
                nom=f"Zone {i+1}",
                code=code,
                description=f"Zone géographique {i+1}",
                actif=True
            )
            db.add(zone)
            zones_created += 1
    
    db.commit()
    print(f"✅ {zones_created} zones créées")


def seed_quartiers(db: Session, count=50):
    """Seed des quartiers"""
    zones = db.query(Zone).all()
    if not zones:
        print("⚠️ Créez d'abord les zones")
        return
    
    quartiers_created = 0
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
                quartiers_created += 1
    
    # Créer des quartiers supplémentaires
    for i in range(len(QUARTIERS_LIBREVILLE), count):
        code = f"Q-{str(i+1).zfill(3)}"
        # Vérifier si le quartier existe déjà
        existing_quartier = db.query(Quartier).filter(Quartier.code == code).first()
        if not existing_quartier:
            zone = random.choice(zones)
            quartier = Quartier(
                nom=f"Quartier {i+1}",
                code=code,
                zone_id=zone.id,
                description=f"Quartier {i+1} de {zone.nom}",
                actif=True
            )
            db.add(quartier)
            quartiers_created += 1
    
    db.commit()
    print(f"✅ {quartiers_created} quartiers créés")


def seed_types_contribuables(db: Session, count=50):
    """Seed des types de contribuables"""
    types_created = 0
    for type_data in TYPES_CONTRIBUABLES:
        type_contrib = db.query(TypeContribuable).filter(
            TypeContribuable.code == type_data["code"]
        ).first()
        if not type_contrib:
            type_contrib = TypeContribuable(**type_data)
            db.add(type_contrib)
            types_created += 1
    
    # Créer des types supplémentaires
    types_supplementaires = [
        "Artisan", "Prestataire", "Vendeur ambulant", "Taxi", "Moto-taxi",
        "Garage", "Pharmacie", "Superette", "Boulangerie", "Coiffure",
        "Salon de beauté", "Cybercafé", "Imprimerie", "Photographe", "Bijoutier"
    ]
    
    for i, nom_type in enumerate(types_supplementaires[:count - len(TYPES_CONTRIBUABLES)]):
        type_contrib = TypeContribuable(
            nom=nom_type,
            code=f"TC-{str(len(TYPES_CONTRIBUABLES) + i + 1).zfill(3)}",
            description=f"Type de contribuable : {nom_type}",
            actif=True
        )
        db.add(type_contrib)
        types_created += 1
    
    db.commit()
    print(f"✅ {types_created} types de contribuables créés")


def seed_services(db: Session, count=50):
    """Seed des services"""
    services_created = 0
    for service_data in SERVICES_MAIRIE:
        service = db.query(Service).filter(Service.code == service_data["code"]).first()
        if not service:
            service = Service(**service_data)
            db.add(service)
            services_created += 1
    
    # Créer des services supplémentaires
    services_supplementaires = [
        "Service de la Propreté", "Service de l'Éclairage Public", "Service des Espaces Verts",
        "Service de la Sécurité", "Service de la Communication", "Service des Archives",
        "Service de l'État Civil", "Service de la Population", "Service de l'Action Sociale"
    ]
    
    for i, nom_service in enumerate(services_supplementaires[:count - len(SERVICES_MAIRIE)]):
        service = Service(
            nom=nom_service,
            code=f"SRV-{str(len(SERVICES_MAIRIE) + i + 1).zfill(3)}",
            description=f"Service : {nom_service}",
            actif=True
        )
        db.add(service)
        services_created += 1
    
    db.commit()
    print(f"✅ {services_created} services créés")


def seed_types_taxes(db: Session, count=50):
    """Seed des types de taxes"""
    types_created = 0
    for type_data in TYPES_TAXES:
        type_taxe = db.query(TypeTaxe).filter(TypeTaxe.code == type_data["code"]).first()
        if not type_taxe:
            type_taxe = TypeTaxe(**type_data)
            db.add(type_taxe)
            types_created += 1
    
    # Créer des types supplémentaires
    types_supplementaires = [
        "Taxe sur les Spectacles", "Taxe sur les Jeux", "Taxe sur les Locations",
        "Taxe sur les Terrains", "Taxe sur les Constructions", "Taxe sur les Véhicules",
        "Taxe sur les Animaux", "Taxe sur les Événements", "Taxe sur les Installations"
    ]
    
    for i, nom_type in enumerate(types_supplementaires[:count - len(TYPES_TAXES)]):
        type_taxe = TypeTaxe(
            nom=nom_type,
            code=f"TT-{str(len(TYPES_TAXES) + i + 1).zfill(3)}",
            description=f"Type de taxe : {nom_type}",
            actif=True
        )
        db.add(type_taxe)
        types_created += 1
    
    db.commit()
    print(f"✅ {types_created} types de taxes créés")


def seed_taxes(db: Session, count=50):
    """Seed des taxes"""
    types_taxes = db.query(TypeTaxe).all()
    services = db.query(Service).all()
    
    if not types_taxes or not services:
        print("⚠️ Créez d'abord les types de taxes et services")
        return
    
    taxes_created = 0
    
    # Taxes de base
    taxes_base = [
        {
            "nom": "Taxe de Marché Journalière",
            "code": "TAX-001",
            "description": "Taxe quotidienne pour les vendeurs de marché",
            "montant": 1000.00,
            "montant_variable": False,
            "periodicite": PeriodiciteEnum.JOURNALIERE,
            "commission_pourcentage": 5.00
        },
        {
            "nom": "Taxe de Marché Mensuelle",
            "code": "TAX-002",
            "description": "Taxe mensuelle pour les vendeurs de marché",
            "montant": 25000.00,
            "montant_variable": False,
            "periodicite": PeriodiciteEnum.MENSUELLE,
            "commission_pourcentage": 5.00
        },
        {
            "nom": "Taxe d'Occupation Domaine Public",
            "code": "TAX-003",
            "description": "Taxe pour occupation de l'espace public",
            "montant": 5000.00,
            "montant_variable": True,
            "periodicite": PeriodiciteEnum.MENSUELLE,
            "commission_pourcentage": 3.00
        },
        {
            "nom": "Taxe Commerciale Mensuelle",
            "code": "TAX-004",
            "description": "Taxe sur les activités commerciales",
            "montant": 15000.00,
            "montant_variable": False,
            "periodicite": PeriodiciteEnum.MENSUELLE,
            "commission_pourcentage": 4.00
        },
        {
            "nom": "Taxe de Stationnement",
            "code": "TAX-005",
            "description": "Taxe de stationnement journalière",
            "montant": 500.00,
            "montant_variable": False,
            "periodicite": PeriodiciteEnum.JOURNALIERE,
            "commission_pourcentage": 2.00
        },
        {
            "nom": "Taxe d'Enlèvement Ordures",
            "code": "TAX-006",
            "description": "Taxe pour l'enlèvement des ordures ménagères",
            "montant": 3000.00,
            "montant_variable": False,
            "periodicite": PeriodiciteEnum.MENSUELLE,
            "commission_pourcentage": 0.00
        },
    ]
    
    for taxe_data in taxes_base:
        taxe = db.query(Taxe).filter(Taxe.code == taxe_data["code"]).first()
        if not taxe:
            taxe_data["type_taxe_id"] = types_taxes[0].id
            taxe_data["service_id"] = services[1].id if len(services) > 1 else services[0].id
            taxe = Taxe(**taxe_data)
            db.add(taxe)
            taxes_created += 1
    
    # Créer des taxes supplémentaires
    periodicites = [PeriodiciteEnum.JOURNALIERE, PeriodiciteEnum.HEBDOMADAIRE, 
                    PeriodiciteEnum.MENSUELLE, PeriodiciteEnum.TRIMESTRIELLE]
    montants_base = [500, 1000, 2000, 3000, 5000, 10000, 15000, 20000, 25000, 30000]
    
    for i in range(len(taxes_base), count):
        taxe = Taxe(
            nom=f"Taxe {i+1}",
            code=f"TAX-{str(i+1).zfill(3)}",
            description=f"Description de la taxe {i+1}",
            montant=random.choice(montants_base),
            montant_variable=random.choice([True, False]),
            periodicite=random.choice(periodicites),
            type_taxe_id=random.choice(types_taxes).id,
            service_id=random.choice(services).id,
            commission_pourcentage=round(random.uniform(0, 10), 2),
            actif=True
        )
        db.add(taxe)
        taxes_created += 1
    
    db.commit()
    print(f"✅ {taxes_created} taxes créées")


def seed_collecteurs(db: Session, count=50):
    """Seed des collecteurs"""
    zones = db.query(Zone).all()
    
    collecteurs_created = 0
    
    for i in range(count):
        matricule = f"COL-{str(i+1).zfill(3)}"
        collecteur = db.query(Collecteur).filter(Collecteur.matricule == matricule).first()
        
        if not collecteur:
            collecteur = Collecteur(
                nom=random.choice(NOMS_GABONAIS),
                prenom=random.choice(PRENOMS_GABONAIS),
                email=f"collecteur{i+1}@mairie-libreville.ga",
                telephone=f"+24106{random.randint(1000000, 9999999)}",
                matricule=matricule,
                statut=random.choice([StatutCollecteurEnum.ACTIVE, StatutCollecteurEnum.ACTIVE, StatutCollecteurEnum.DESACTIVE]),
                etat=random.choice([EtatCollecteurEnum.CONNECTE, EtatCollecteurEnum.DECONNECTE]),
                zone_id=random.choice(zones).id if zones else None,
                heure_cloture=f"{random.randint(17, 19)}:00",
                actif=True
            )
            db.add(collecteur)
            collecteurs_created += 1
    
    db.commit()
    print(f"✅ {collecteurs_created} collecteurs créés")


def seed_contribuables(db: Session, count=50):
    """Seed des contribuables"""
    types_contrib = db.query(TypeContribuable).all()
    quartiers = db.query(Quartier).all()
    collecteurs = db.query(Collecteur).all()
    
    if not types_contrib or not quartiers or not collecteurs:
        print("⚠️ Créez d'abord les types, quartiers et collecteurs")
        return
    
    contribuables_created = 0
    
    for i in range(count):
        numero_id = f"CTB-{str(i+1).zfill(4)}"
        contribuable = db.query(Contribuable).filter(
            Contribuable.numero_identification == numero_id
        ).first()
        
        if not contribuable:
            telephone = f"+24106{random.randint(1000000, 9999999)}"
            # Vérifier que le téléphone n'existe pas déjà
            existing = db.query(Contribuable).filter(Contribuable.telephone == telephone).first()
            if existing:
                telephone = f"+24107{random.randint(1000000, 9999999)}"
            
            contribuable = Contribuable(
                nom=random.choice(NOMS_GABONAIS),
                prenom=random.choice(PRENOMS_GABONAIS),
                email=f"contribuable{i+1}@example.ga" if random.choice([True, False]) else None,
                telephone=telephone,
                type_contribuable_id=random.choice(types_contrib).id,
                quartier_id=random.choice(quartiers).id,
                collecteur_id=random.choice(collecteurs).id,
                adresse=f"Rue {random.choice(['Avenue', 'Boulevard', 'Rue', 'Impasse'])} {random.choice(['Indépendance', 'Léon Mba', 'Nkrumah', 'De Gaulle', 'Massenet'])} {random.randint(1, 200)}",
                latitude=round(random.uniform(0.3, 0.5), 8),  # Coordonnées approximatives Libreville
                longitude=round(random.uniform(9.3, 9.5), 8),
                numero_identification=numero_id,
                actif=True
            )
            db.add(contribuable)
            contribuables_created += 1
    
    db.commit()
    print(f"✅ {contribuables_created} contribuables créés")


def seed_affectations_taxes(db: Session, count=50):
    """Seed des affectations de taxes"""
    contribuables = db.query(Contribuable).all()
    taxes = db.query(Taxe).all()
    
    if not contribuables or not taxes:
        print("⚠️ Créez d'abord les contribuables et taxes")
        return
    
    affectations_created = 0
    
    # Affecter des taxes à chaque contribuable
    for contribuable in contribuables:
        # Chaque contribuable a 1-3 taxes
        nb_taxes = random.randint(1, 3)
        taxes_selected = random.sample(taxes, min(nb_taxes, len(taxes)))
        
        for taxe in taxes_selected:
            # Vérifier si l'affectation existe déjà
            affectation = db.query(AffectationTaxe).filter(
                AffectationTaxe.contribuable_id == contribuable.id,
                AffectationTaxe.taxe_id == taxe.id,
                AffectationTaxe.actif == True
            ).first()
            
            if not affectation:
                date_debut = datetime.utcnow() - timedelta(days=random.randint(1, 180))
                affectation = AffectationTaxe(
                    contribuable_id=contribuable.id,
                    taxe_id=taxe.id,
                    date_debut=date_debut,
                    date_fin=None if random.choice([True, False]) else date_debut + timedelta(days=365),
                    montant_custom=None if not taxe.montant_variable else float(taxe.montant) * random.uniform(0.8, 1.5),
                    actif=True
                )
                db.add(affectation)
                affectations_created += 1
    
    # Créer des affectations supplémentaires pour atteindre le count
    while affectations_created < count:
        contribuable = random.choice(contribuables)
        taxe = random.choice(taxes)
        
        affectation = db.query(AffectationTaxe).filter(
            AffectationTaxe.contribuable_id == contribuable.id,
            AffectationTaxe.taxe_id == taxe.id
        ).first()
        
        if not affectation:
            date_debut = datetime.utcnow() - timedelta(days=random.randint(1, 180))
            affectation = AffectationTaxe(
                contribuable_id=contribuable.id,
                taxe_id=taxe.id,
                date_debut=date_debut,
                date_fin=None,
                montant_custom=None if not taxe.montant_variable else float(taxe.montant) * random.uniform(0.8, 1.5),
                actif=True
            )
            db.add(affectation)
            affectations_created += 1
    
    db.commit()
    print(f"✅ {affectations_created} affectations de taxes créées")


def seed_collectes(db: Session, count=50):
    """Seed des collectes"""
    affectations = db.query(AffectationTaxe).filter(AffectationTaxe.actif == True).all()
    collecteurs = db.query(Collecteur).all()
    
    if not affectations or not collecteurs:
        print("⚠️ Créez d'abord les affectations et collecteurs")
        return
    
    collectes_created = 0
    
    # Créer des collectes pour les 90 derniers jours
    for i in range(count):
        affectation = random.choice(affectations)
        contribuable = affectation.contribuable
        taxe = affectation.taxe
        collecteur = random.choice(collecteurs)
        
        montant = float(affectation.montant_custom) if affectation.montant_custom else float(taxe.montant)
        commission = montant * (float(taxe.commission_pourcentage) / 100)
        
        date_collecte = datetime.utcnow() - timedelta(days=random.randint(0, 90))
        
        reference = f"COL-{date_collecte.strftime('%Y%m%d')}-{str(i+1).zfill(4)}"
        
        # Vérifier que la référence n'existe pas
        existing = db.query(InfoCollecte).filter(InfoCollecte.reference == reference).first()
        if existing:
            reference = f"COL-{date_collecte.strftime('%Y%m%d')}-{str(i+1).zfill(4)}-{random.randint(1, 999)}"
        
        # Générer un billetage aléatoire pour les paiements en espèces
        billetage = None
        if random.choice([True, False]):
            billetage_data = {}
            montant_restant = montant
            coupures = [10000, 5000, 2000, 1000, 500]
            for coupure in coupures:
                if montant_restant >= coupure:
                    nb = random.randint(0, int(montant_restant / coupure))
                    if nb > 0:
                        billetage_data[str(coupure)] = nb
                        montant_restant -= nb * coupure
            if billetage_data:
                billetage = json.dumps(billetage_data)
        
        collecte = InfoCollecte(
            contribuable_id=contribuable.id,
            taxe_id=taxe.id,
            collecteur_id=collecteur.id,
            montant=montant,
            commission=commission,
            type_paiement=random.choice(list(TypePaiementEnum)),
            statut=random.choice([
                StatutCollecteEnum.COMPLETED, StatutCollecteEnum.COMPLETED, 
                StatutCollecteEnum.COMPLETED, StatutCollecteEnum.PENDING, StatutCollecteEnum.FAILED
            ]),
            reference=reference,
            billetage=billetage,
            date_collecte=date_collecte,
            date_cloture=date_collecte + timedelta(hours=random.randint(1, 8)) if random.choice([True, False]) else None,
            sms_envoye=random.choice([True, False]),
            ticket_imprime=random.choice([True, False]),
            annule=False
        )
        db.add(collecte)
        collectes_created += 1
    
    db.commit()
    print(f"✅ {collectes_created} collectes créées")


def seed_utilisateurs(db: Session, count=50):
    """Seed des utilisateurs"""
    roles = list(RoleEnum)
    utilisateurs_created = 0
    
    # Créer l'admin si n'existe pas
    admin = db.query(Utilisateur).filter(Utilisateur.email == "admin@mairie-libreville.ga").first()
    if not admin:
        admin = Utilisateur(
            nom="Admin",
            prenom="Système",
            email="admin@mairie-libreville.ga",
            telephone="+241062345678",
            mot_de_passe_hash=get_password_hash("admin123"),
            role=RoleEnum.ADMIN,
            actif=True
        )
        db.add(admin)
        utilisateurs_created += 1
    
    # Créer des utilisateurs supplémentaires
    for i in range(1, count):
        email = f"user{i}@mairie-libreville.ga"
        existing = db.query(Utilisateur).filter(Utilisateur.email == email).first()
        
        if not existing:
            utilisateur = Utilisateur(
                nom=random.choice(NOMS_GABONAIS),
                prenom=random.choice(PRENOMS_GABONAIS),
                email=email,
                telephone=f"+24106{random.randint(1000000, 9999999)}",
                mot_de_passe_hash=get_password_hash("password123"),
                role=random.choice(roles),
                actif=random.choice([True, True, True, False]),  # 75% actifs
                derniere_connexion=datetime.utcnow() - timedelta(days=random.randint(0, 30)) if random.choice([True, False]) else None
            )
            db.add(utilisateur)
            utilisateurs_created += 1
    
    db.commit()
    print(f"✅ {utilisateurs_created} utilisateurs créés")


def seed_all(db: Session, count_per_table=50):
    """Exécute tous les seeders avec au moins count_per_table entrées par table"""
    print("🌱 Début du seeding complet...")
    print(f"📊 Objectif : {count_per_table} entrées minimum par table\n")
    
    seed_zones(db, count_per_table)
    seed_quartiers(db, count_per_table)
    seed_types_contribuables(db, count_per_table)
    seed_services(db, count_per_table)
    seed_types_taxes(db, count_per_table)
    seed_taxes(db, count_per_table)
    seed_collecteurs(db, count_per_table)
    seed_contribuables(db, count_per_table)
    seed_affectations_taxes(db, count_per_table)
    seed_collectes(db, count_per_table)
    seed_utilisateurs(db, count_per_table)
    
    print("\n✅ Seeding terminé avec succès!")
    print("\n📝 Utilisateur admin:")
    print("   Email: admin@mairie-libreville.ga")
    print("   Password: admin123")


if __name__ == "__main__":
    import sys
    from database.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Par défaut, 50 entrées par table, mais peut être modifié
        count = 50
        if len(sys.argv) > 1:
            count = int(sys.argv[1])
        
        seed_all(db, count)
    finally:
        db.close()


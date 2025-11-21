# Guide des Seeders - Insertion de Données

## 📊 Script de Seeding Complet

Le script `seeders_complet.py` permet d'insérer au moins 50 entrées par table avec des données gabonaises réalistes.

## 🚀 Utilisation

### Option 1 : Via le module Python (Recommandé)

```bash
cd backend
python -m database.run_seeders
```

### Option 2 : Avec un nombre personnalisé

```bash
python -m database.run_seeders 100
```

Cela créera 100 entrées par table au lieu de 50.

### Option 3 : Directement

```bash
python backend/database/seeders_complet.py
```

Ou avec un nombre personnalisé :

```bash
python backend/database/seeders_complet.py 75
```

## 📋 Données Insérées

### Tables et Quantités

- **Zones** : 50+ zones géographiques du Gabon
- **Quartiers** : 50+ quartiers de Libreville et autres villes
- **Types de Contribuables** : 50+ types (Particulier, Entreprise, Commerce, etc.)
- **Services** : 50+ services de la mairie
- **Types de Taxes** : 50+ types de taxes municipales
- **Taxes** : 50+ taxes avec montants, périodicités, commissions
- **Collecteurs** : 50+ collecteurs avec noms gabonais
- **Contribuables** : 50+ contribuables avec adresses gabonaises
- **Affectations Taxes** : 50+ affectations taxes/contribuables
- **Collectes** : 50+ collectes avec historique sur 90 jours
- **Utilisateurs** : 50+ utilisateurs avec différents rôles

## 🇬🇦 Données Gabonaises

### Noms et Prénoms
- Noms de famille gabonais : MBOUMBA, NDONG, OBAME, BONGO, ESSONO, MVE, MINTSA
- Prénoms français courants au Gabon

### Zones et Quartiers
- Zones réelles : Centre-ville, Akanda, Ntoum, Owendo, Port-Gentil, Franceville
- Quartiers réels : Mont-Bouët, Glass, Cocotiers, Angondjé, Melen, etc.

### Taxes Municipales
- Taxe de Marché (journalière/mensuelle)
- Taxe d'Occupation du Domaine Public
- Taxe sur les Activités Commerciales
- Taxe de Stationnement
- Taxe de Voirie
- Taxe d'Enlèvement des Ordures
- Et plus...

### Coordonnées
- Latitude/Longitude : Coordonnées approximatives de Libreville (0.3-0.5, 9.3-9.5)
- Téléphones : Format gabonais (+24106...)

## 🔐 Utilisateur Admin

Un utilisateur admin est créé automatiquement :
- **Email** : `admin@mairie-libreville.ga`
- **Mot de passe** : `admin123`
- **⚠️ À changer immédiatement en production !**

## 📝 Notes

- Les données sont générées de manière aléatoire mais réaliste
- Les relations entre tables sont respectées (foreign keys)
- Les dates sont cohérentes (collectes sur les 90 derniers jours)
- Les montants sont en XAF (Franc CFA)
- Les billetages sont générés pour les paiements en espèces

## ⚠️ Attention

- Le script vérifie les doublons avant insertion
- Les données existantes ne sont pas écrasées
- Pour réinitialiser, supprimez d'abord les données existantes

## 🔄 Réinitialisation

Pour réinitialiser complètement la base :

```sql
-- ATTENTION : Cela supprime TOUTES les données !
TRUNCATE TABLE info_collecte CASCADE;
TRUNCATE TABLE affectation_taxe CASCADE;
TRUNCATE TABLE contribuable CASCADE;
TRUNCATE TABLE collecteur CASCADE;
TRUNCATE TABLE taxe CASCADE;
TRUNCATE TABLE utilisateur CASCADE;
TRUNCATE TABLE quartier CASCADE;
TRUNCATE TABLE zone CASCADE;
TRUNCATE TABLE type_contribuable CASCADE;
TRUNCATE TABLE type_taxe CASCADE;
TRUNCATE TABLE service CASCADE;
```

Puis relancez le script de seeding.


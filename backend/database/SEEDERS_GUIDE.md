# Guide Complet des Seeders

## 🎯 Objectif

Insérer au moins **50 entrées par table** avec des **données gabonaises réalistes**.

## 📋 Deux Méthodes Disponibles

### Méthode 1 : Script Python (Recommandé) ⭐

**Avantages** :
- ✅ Gestion automatique des relations
- ✅ Vérification des doublons
- ✅ Génération de données cohérentes
- ✅ Plus facile à maintenir

**Utilisation** :
```bash
cd backend
python -m database.run_seeders
```

**Avec nombre personnalisé** :
```bash
python -m database.run_seeders 100
```

### Méthode 2 : Script SQL

**Avantages** :
- ✅ Exécution directe dans PostgreSQL
- ✅ Pas besoin de Python

**Utilisation** :
```bash
psql -U postgres -d taxe_municipale -f backend/database/insert_data.sql
```

## 📊 Données Insérées

### Tables et Quantités Minimum

| Table | Quantité | Description |
|-------|----------|-------------|
| Zone | 50+ | Zones géographiques du Gabon |
| Quartier | 50+ | Quartiers de Libreville et autres villes |
| Type Contribuable | 50+ | Types de contribuables |
| Service | 50+ | Services de la mairie |
| Type Taxe | 50+ | Types de taxes municipales |
| Taxe | 50+ | Taxes avec montants et périodicités |
| Collecteur | 50+ | Collecteurs avec noms gabonais |
| Contribuable | 50+ | Contribuables avec adresses gabonaises |
| Affectation Taxe | 50+ | Relations contribuables/taxes |
| Info Collecte | 50+ | Historique des collectes (90 jours) |
| Utilisateur | 50+ | Utilisateurs avec différents rôles |

## 🇬🇦 Données Gabonaises Réalistes

### Noms et Prénoms
- **Noms** : MBOUMBA, NDONG, OBAME, BONGO, ESSONO, MVE, MINTSA
- **Prénoms** : Jean, Marie, Pierre, Paul, Sophie, Luc, Anne, David, etc.

### Zones Réelles
- Centre-ville, Akanda, Ntoum, Owendo, Port-Gentil, Franceville

### Quartiers Réels
- Mont-Bouët, Glass, Quartier Louis, Nombakélé, Akébé, Oloumi
- Cocotiers, Angondjé, Melen (Akanda)
- PK8, PK12, PK15 (Owendo)

### Taxes Municipales
- Taxe de Marché (journalière/mensuelle)
- Taxe d'Occupation du Domaine Public
- Taxe sur les Activités Commerciales
- Taxe de Stationnement
- Taxe de Voirie
- Taxe d'Enlèvement des Ordures
- Et plus...

### Coordonnées
- **Téléphones** : Format gabonais (+24106...)
- **Latitude/Longitude** : Coordonnées de Libreville (0.3-0.5, 9.3-9.5)
- **Adresses** : Rues réelles (Avenue Indépendance, Boulevard Léon Mba, etc.)

## 🔐 Utilisateur Admin

Créé automatiquement :
- **Email** : `admin@mairie-libreville.ga`
- **Mot de passe** : `admin123`
- **⚠️ À changer en production !**

## ⚙️ Configuration

### Variables d'environnement

Assurez-vous que votre `.env` contient :
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/taxe_municipale
```

## 🔄 Réinitialisation

Pour réinitialiser complètement :

```sql
-- ATTENTION : Supprime TOUTES les données !
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

Puis relancez le script.

## 📝 Notes Importantes

1. **Doublons** : Les scripts vérifient les doublons avant insertion
2. **Relations** : Les foreign keys sont respectées
3. **Dates** : Les collectes sont sur les 90 derniers jours
4. **Montants** : En XAF (Franc CFA)
5. **Billetage** : Généré pour les paiements en espèces

## 🐛 Dépannage

### Erreur de connexion
- Vérifier que PostgreSQL est démarré
- Vérifier les credentials dans `.env`

### Erreur de foreign key
- Exécuter les seeders dans l'ordre
- Ou utiliser le script Python qui gère l'ordre automatiquement

### Données manquantes
- Vérifier les logs du script
- Relancer le script (les doublons sont ignorés)

## 📞 Support

Pour toute question, consulter :
- `README_SEEDERS.md` - Documentation détaillée
- `seeders_complet.py` - Code source du script Python


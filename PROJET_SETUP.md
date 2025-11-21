# Guide de Configuration du Projet - Collecte Taxe Municipale

## 📋 Vue d'ensemble

Ce projet comprend :
- **Backend FastAPI** : API REST pour la gestion de la collecte de taxes
- **Frontend Angular** : Interface d'administration
- **Base de données PostgreSQL** : Stockage des données

## 🗄️ Base de Données PostgreSQL

### Installation PostgreSQL

1. Installer PostgreSQL depuis https://www.postgresql.org/download/
2. Créer une base de données :
```sql
CREATE DATABASE taxe_municipale;
```

### Tables créées

- `service` : Services de la mairie
- `type_taxe` : Types de taxes (Taxe de marché, Taxe d'occupation, etc.)
- `zone` : Zones géographiques de Libreville
- `quartier` : Quartiers de Libreville
- `type_contribuable` : Types de contribuables (Particulier, Entreprise, etc.)
- `collecteur` : Collecteurs de taxes
- `contribuable` : Contribuables (clients)
- `taxe` : Taxes municipales
- `affectation_taxe` : Affectation d'une taxe à un contribuable
- `info_collecte` : Informations sur les collectes effectuées

## 🚀 Backend FastAPI

### Prérequis
- Python 3.9+
- PostgreSQL installé et configuré

### Installation

1. Aller dans le dossier backend :
```bash
cd backend
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
# Sur Windows
venv\Scripts\activate
# Sur Linux/Mac
source venv/bin/activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer l'environnement :
```bash
# Copier le fichier .env.example
cp .env.example .env
# Modifier DATABASE_URL si nécessaire
```

5. Initialiser la base de données :
```bash
python -m database.init_db
```

6. Démarrer le serveur :
```bash
uvicorn main:app --reload --port 8000
```

L'API sera accessible sur :
- API : http://localhost:8000
- Documentation : http://localhost:8000/docs
- Health check : http://localhost:8000/health

## 🎨 Frontend Angular

### Prérequis
- Node.js 18+
- npm ou yarn

### Installation

1. Aller dans le dossier frontend :
```bash
cd e_taxe_back_office
```

2. Installer les dépendances :
```bash
npm install
```

3. Installer HttpClient (si nécessaire) :
```bash
npm install @angular/common
```

4. Démarrer le serveur de développement :
```bash
ng serve
# ou
npm start
```

L'application sera accessible sur : http://localhost:4200

## 📝 Données réelles du Gabon

Le projet inclut des données réelles pour Libreville :

### Zones
- Centre-ville
- Akanda
- Ntoum
- Owendo

### Quartiers
- Mont-Bouët, Glass, Quartier Louis, Nombakélé, Akébé, Oloumi (Centre-ville)
- Cocotiers, Angondjé, Melen (Akanda)
- Ntoum Centre
- Owendo Centre, PK8

### Types de Taxes
- Taxe de Marché
- Taxe d'Occupation du Domaine Public
- Taxe sur les Activités Commerciales
- Taxe de Stationnement
- Taxe de Voirie
- Taxe d'Enlèvement des Ordures
- Taxe sur les Transports

## 🔌 Intégration Frontend-Backend

Le frontend est configuré pour communiquer avec le backend via :
- Service : `src/app/services/api.service.ts`
- URL API : `http://localhost:8000/api` (configurable dans `environment.ts`)

## 📚 Endpoints API

### Taxes
- `GET /api/taxes` : Liste des taxes
- `GET /api/taxes/{id}` : Détails d'une taxe
- `POST /api/taxes` : Créer une taxe
- `PUT /api/taxes/{id}` : Modifier une taxe
- `DELETE /api/taxes/{id}` : Supprimer une taxe

### Contribuables
- `GET /api/contribuables` : Liste des contribuables
- `GET /api/contribuables/{id}` : Détails d'un contribuable
- `POST /api/contribuables` : Créer un contribuable
- `PUT /api/contribuables/{id}` : Modifier un contribuable
- `PATCH /api/contribuables/{id}/transfert` : Transférer un contribuable
- `DELETE /api/contribuables/{id}` : Supprimer un contribuable

### Collecteurs
- `GET /api/collecteurs` : Liste des collecteurs
- `GET /api/collecteurs/{id}` : Détails d'un collecteur
- `POST /api/collecteurs` : Créer un collecteur
- `PUT /api/collecteurs/{id}` : Modifier un collecteur
- `PATCH /api/collecteurs/{id}/connexion` : Connecter un collecteur
- `PATCH /api/collecteurs/{id}/deconnexion` : Déconnecter un collecteur
- `DELETE /api/collecteurs/{id}` : Supprimer un collecteur

### Collectes
- `GET /api/collectes` : Liste des collectes
- `GET /api/collectes/{id}` : Détails d'une collecte
- `POST /api/collectes` : Créer une collecte
- `PUT /api/collectes/{id}` : Modifier une collecte
- `PATCH /api/collectes/{id}/annuler` : Annuler une collecte
- `DELETE /api/collectes/{id}` : Supprimer une collecte

### Références
- `GET /api/references/zones` : Liste des zones
- `GET /api/references/quartiers` : Liste des quartiers
- `GET /api/references/types-contribuables` : Types de contribuables
- `GET /api/references/types-taxes` : Types de taxes
- `GET /api/references/services` : Services de la mairie

## 🐛 Dépannage

### Erreur de connexion à la base de données
- Vérifier que PostgreSQL est démarré
- Vérifier les credentials dans `.env`
- Vérifier que la base de données `taxe_municipale` existe

### Erreur CORS
- Vérifier que le backend autorise les requêtes depuis `http://localhost:4200`
- Vérifier la configuration CORS dans `backend/main.py`

### Erreur d'import dans Angular
- Vérifier que `HttpClient` est bien importé dans `app.config.ts`
- Vérifier que les interfaces sont bien créées

## 📞 Support

Pour toute question ou problème, consulter :
- Documentation FastAPI : http://localhost:8000/docs
- Documentation Angular : https://angular.dev


# Guide d'importation du dump SQL

Ce guide explique comment importer les données gabonaises réelles depuis le fichier `dump_taxe.sql` dans votre base de données.

## Prérequis

1. PostgreSQL installé et en cours d'exécution
2. Base de données `taxe_municipale` créée
3. Extensions PostGIS activées (si nécessaire)
4. Python 3.8+ avec les dépendances installées

## Méthode 1 : Utilisation du script Python (Recommandé)

### Étape 1 : Activer l'environnement virtuel

```bash
cd backend
# Sur Windows
venv\Scripts\activate

# Sur Linux/Mac
source venv/bin/activate
```

### Étape 2 : Exécuter le script d'importation

```bash
python -m database.import_dump
```

Le script va :
- Détecter automatiquement le fichier `dump_taxe.sql`
- Utiliser la configuration de connexion depuis `.env` ou `database.py`
- Importer toutes les données
- Vérifier que l'importation a réussi

### Options disponibles

```bash
# Spécifier un fichier dump personnalisé
python -m database.import_dump --dump-file chemin/vers/dump.sql

# Spécifier une URL de base de données personnalisée
python -m database.import_dump --database-url postgresql://user:pass@host:port/dbname

# Vérifier uniquement les données importées (sans importer)
python -m database.import_dump --verify-only
```

## Méthode 2 : Utilisation directe de psql (Plus rapide)

Si vous avez `psql` installé, vous pouvez importer directement :

```bash
# Sur Windows (PowerShell)
$env:PGPASSWORD="votre_mot_de_passe"
psql -h localhost -U postgres -d taxe_municipale -f backend\dump_taxe.sql

# Sur Linux/Mac
PGPASSWORD=votre_mot_de_passe psql -h localhost -U postgres -d taxe_municipale -f backend/dump_taxe.sql
```

Ou en spécifiant le mot de passe dans la commande :

```bash
psql -h localhost -U postgres -d taxe_municipale -f backend/dump_taxe.sql
# Vous serez invité à entrer le mot de passe
```

## Vérification de l'importation

Après l'importation, le script vérifie automatiquement :

- Nombre de contribuables importés
- Nombre de collecteurs importés
- Nombre de taxes importées
- Nombre de collectes importées
- Nombre de contribuables avec coordonnées GPS

Vous pouvez aussi vérifier manuellement :

```sql
-- Se connecter à la base de données
psql -U postgres -d taxe_municipale

-- Vérifier les données
SELECT COUNT(*) FROM contribuable;
SELECT COUNT(*) FROM collecteur;
SELECT COUNT(*) FROM taxe;
SELECT COUNT(*) FROM info_collecte;

-- Vérifier les contribuables avec GPS
SELECT COUNT(*) FROM contribuable 
WHERE latitude IS NOT NULL AND longitude IS NOT NULL;
```

## Données incluses dans le dump

Le fichier `dump_taxe.sql` contient :

- ✅ **Contribuables** : Contribuables gabonais avec coordonnées GPS réelles
- ✅ **Collecteurs** : Collecteurs de taxes avec leurs informations
- ✅ **Taxes** : Types de taxes municipales gabonaises
- ✅ **Collectes** : Historique des collectes effectuées
- ✅ **Zones géographiques** : Zones, quartiers, arrondissements de Libreville
- ✅ **Services** : Services de la mairie
- ✅ **Types** : Types de contribuables et types de taxes

## Résolution des problèmes

### Erreur : "Le fichier dump_taxe.sql n'existe pas"

Vérifiez que le fichier existe dans `backend/dump_taxe.sql`. Si nécessaire, spécifiez le chemin complet avec `--dump-file`.

### Erreur : "psql n'est pas trouvé"

Installez PostgreSQL ou utilisez la méthode Python (méthode 1) qui ne nécessite pas psql.

### Erreur : "Permission denied" ou erreur de connexion

Vérifiez :
- Que PostgreSQL est en cours d'exécution
- Les identifiants dans votre fichier `.env`
- Les permissions de la base de données

### Erreur : "Extension postgis does not exist"

Activez PostGIS dans votre base de données :

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

### Importation partielle ou incomplète

Si l'importation échoue partiellement :
1. Videz la base de données (optionnel, attention aux données existantes)
2. Réessayez l'importation
3. Vérifiez les logs d'erreur pour identifier les problèmes spécifiques

## Notes importantes

⚠️ **Attention** : L'importation du dump va **écraser** les données existantes dans les tables concernées. Faites une sauvegarde si nécessaire.

💡 **Conseil** : Pour de meilleures performances, utilisez `psql` directement (méthode 2) pour les gros fichiers.

📊 **Performance** : L'importation peut prendre quelques minutes selon la taille du dump et les performances de votre système.

## Support

En cas de problème, vérifiez :
1. Les logs du script Python
2. Les logs PostgreSQL
3. La documentation PostgreSQL pour les erreurs spécifiques


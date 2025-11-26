# Seeders pour Caisses, Journal et Commissions

Ce guide explique comment ajouter des données de démonstration dans les nouvelles tables de l'application.

## 📋 Tables concernées

- `caisse` - Caisses des collecteurs (physiques et en ligne)
- `operation_caisse` - Opérations de caisse (ouvertures, entrées, sorties)
- `journal_travaux` - Journaux quotidiens de travaux
- `commission_fichier` - Fichiers de commissions générés
- `commission_journaliere` - Commissions par collecteur et par jour

## 🚀 Méthode 1 : Script Python (Recommandé)

### Prérequis
- Avoir des collecteurs actifs dans la base de données
- Avoir au moins un utilisateur dans la table `utilisateur`

### Exécution

```bash
cd backend
python -m database.seeders_caisses_journal
```

Le script va :
1. Créer 2 caisses par collecteur (1 physique + 1 en ligne) pour les 5 premiers collecteurs actifs
2. Générer des opérations de caisse (ouvertures, collectes, remises)
3. Créer des journaux de travaux pour les 7 derniers jours
4. Créer des fichiers de commissions pour les 3 derniers jours avec commissions par collecteur

## 🚀 Méthode 2 : Script SQL (Alternative)

### Exécution

```bash
psql -d taxe_municipale -U postgres -f backend/database/migrations/seed_caisses_journal_data.sql
```

### Avantages
- Plus rapide pour de grandes quantités de données
- Pas besoin d'environnement Python
- Transaction atomique (rollback en cas d'erreur)

## 📊 Données générées

### Caisses
- **2 caisses par collecteur** : 1 physique + 1 en ligne
- **États variés** : Ouvertes/Fermées alternées
- **Soldes réalistes** : Entre 15 000 et 75 000 FCFA

### Opérations de caisse
- **Ouvertures** : Pour les caisses ouvertes
- **Entrées** : 3 à 8 collectes par caisse (5 000 à 50 000 FCFA)
- **Sorties** : Remises en banque (50% de chance, 10 000 à 30 000 FCFA)

### Journaux de travaux
- **7 jours** : Du jour actuel jusqu'à 6 jours en arrière
- **Statuts** : Clôturés pour les jours passés, en cours pour aujourd'hui
- **Statistiques calculées** : Basées sur les collectes et opérations réelles

### Commissions
- **3 jours** : Les 3 derniers jours
- **5 collecteurs** : Commissions pour les 5 premiers collecteurs actifs
- **Commission** : 5% du montant collecté
- **Statuts** : En attente pour le dernier jour, payées pour les autres

## ✅ Vérification

Après exécution, vous pouvez vérifier les données :

```sql
-- Nombre de caisses
SELECT COUNT(*) FROM caisse;

-- Nombre d'opérations
SELECT COUNT(*) FROM operation_caisse;

-- Journaux créés
SELECT date_jour, statut, nb_collectes, montant_collectes 
FROM journal_travaux 
ORDER BY date_jour DESC;

-- Commissions
SELECT 
    cf.date_jour,
    COUNT(cj.id) as nb_collecteurs,
    SUM(cj.commission_montant) as total_commissions
FROM commission_fichier cf
LEFT JOIN commission_journaliere cj ON cj.fichier_id = cf.id
GROUP BY cf.date_jour
ORDER BY cf.date_jour DESC;
```

## 🔄 Réexécution

Les scripts sont idempotents : ils vérifient l'existence des données avant insertion.

Pour forcer la réinsertion, supprimez d'abord les données :

```sql
DELETE FROM commission_journaliere;
DELETE FROM commission_fichier;
DELETE FROM journal_travaux;
DELETE FROM operation_caisse;
DELETE FROM caisse;
```

Puis réexécutez le script.

## ⚠️ Notes importantes

1. **Collecteurs requis** : Assurez-vous d'avoir au moins 5 collecteurs actifs
2. **Utilisateurs requis** : Au moins 1 utilisateur pour `created_by` dans les commissions
3. **Dates** : Les données sont générées pour les jours récents (derniers 7 jours)
4. **Montants** : Les montants sont générés aléatoirement dans des plages réalistes

## 🐛 Dépannage

### Erreur : "Aucun collecteur trouvé"
```bash
# Vérifiez les collecteurs
psql -d taxe_municipale -c "SELECT id, nom, prenom, actif FROM collecteur LIMIT 10;"
```

### Erreur : "Aucun utilisateur trouvé"
```bash
# Créez un utilisateur si nécessaire
psql -d taxe_municipale -c "SELECT id, email FROM utilisateur LIMIT 1;"
```

### Erreur de contrainte unique
Les scripts vérifient l'existence avant insertion. Si vous avez des doublons, supprimez-les d'abord.


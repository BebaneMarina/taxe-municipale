# 🚀 Exécution du Script SQL de Seeding

## 📋 Utilisation

### Méthode 1 : Via psql (ligne de commande)

```bash
psql -U postgres -d taxe_municipale -f database/insert_all_data.sql
```

### Méthode 2 : Via pgAdmin

1. Ouvrez pgAdmin
2. Connectez-vous à votre serveur PostgreSQL
3. Sélectionnez la base de données `taxe_municipale`
4. Cliquez sur "Query Tool"
5. Ouvrez le fichier `backend/database/insert_all_data.sql`
6. Exécutez le script (F5)

## ✅ Résultat Attendu

Après exécution, vous devriez avoir :
- ✅ 50+ zones
- ✅ 50+ quartiers
- ✅ 50+ types de contribuables
- ✅ 50+ services
- ✅ 50+ types de taxes
- ✅ 50+ taxes
- ✅ 50+ collecteurs
- ✅ 50+ contribuables
- ✅ 50+ affectations
- ✅ 50+ collectes
- ✅ 50+ utilisateurs

## 🔐 Utilisateur Admin

Créé automatiquement :
- **Email** : `admin@mairie-libreville.ga`
- **Mot de passe** : `admin123`

⚠️ **À changer immédiatement en production !**

## 📊 Vérification

Le script affiche automatiquement les statistiques à la fin :
- Nombre d'entrées par table
- Vérification que toutes les données sont insérées

## 🔄 Réexécution

Le script utilise `ON CONFLICT DO NOTHING`, donc vous pouvez le réexécuter plusieurs fois sans problème. Les doublons seront ignorés.

## 🐛 En cas d'erreur

Si vous avez des erreurs :
1. Vérifiez que tous les types ENUM existent
2. Vérifiez que les tables existent
3. Exécutez d'abord `database/schema.sql` si nécessaire


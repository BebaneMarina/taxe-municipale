# 👥 Guide de Gestion des Utilisateurs

## 📋 Vue d'ensemble

Le système de gestion des utilisateurs permet de gérer complètement les utilisateurs du back-office avec attribution de rôles et contrôle des permissions.

## 🔐 Rôles disponibles

1. **`admin`** : Administrateur système
   - Accès complet à toutes les fonctionnalités
   - Peut créer, modifier, supprimer tous les utilisateurs
   - Peut activer/désactiver les comptes

2. **`agent_back_office`** : Agent back-office
   - Gestion des collecteurs, activation, transferts
   - Validation des collectes
   - Accès aux statistiques

3. **`agent_front_office`** : Agent front-office
   - Accès aux données clients
   - Modification des informations contribuables
   - Gestion des paiements

4. **`controleur_interne`** : Contrôleur interne
   - Lecture seule
   - Extraction de données
   - Génération de rapports

5. **`collecteur`** : Collecteur
   - Application mobile uniquement
   - Collecte de taxes sur le terrain

## 🛠️ Endpoints disponibles

### Authentification (`/api/auth`)

- `POST /api/auth/login` : Connexion et génération du token JWT
- `GET /api/auth/me` : Informations de l'utilisateur connecté
- `PUT /api/auth/me` : Mise à jour du profil personnel
- `POST /api/auth/change-password` : Changement de mot de passe

### Gestion des utilisateurs (`/api/utilisateurs`)

#### Liste des utilisateurs
```
GET /api/utilisateurs?skip=0&limit=100&search=nom&role=admin&actif=true
```

**Paramètres de requête :**
- `skip` : Nombre d'éléments à sauter (pagination)
- `limit` : Nombre d'éléments à retourner (max 1000)
- `search` : Recherche par nom, prénom ou email
- `role` : Filtrer par rôle
- `actif` : Filtrer par statut (true/false)

**Permissions :** Tous les utilisateurs authentifiés

#### Détails d'un utilisateur
```
GET /api/utilisateurs/{user_id}
```

**Permissions :** Tous les utilisateurs authentifiés

#### Créer un utilisateur
```
POST /api/utilisateurs
Content-Type: application/json

{
  "nom": "Dupont",
  "prenom": "Jean",
  "email": "jean.dupont@mairie.ga",
  "telephone": "+241 01 23 45 67",
  "password": "motdepasse123",
  "role": "agent_back_office"
}
```

**Permissions :** Administrateurs uniquement

#### Modifier un utilisateur
```
PUT /api/utilisateurs/{user_id}
Content-Type: application/json

{
  "nom": "Dupont",
  "prenom": "Jean",
  "email": "jean.dupont@mairie.ga",
  "telephone": "+241 01 23 45 67",
  "role": "agent_front_office",
  "actif": true
}
```

**Permissions :**
- Administrateurs : peuvent modifier tous les champs de tous les utilisateurs
- Utilisateurs : peuvent modifier leurs propres informations (sauf `role` et `actif`)

#### Supprimer un utilisateur
```
DELETE /api/utilisateurs/{user_id}
```

**Permissions :** Administrateurs uniquement
**Note :** Un administrateur ne peut pas supprimer son propre compte

#### Activer un utilisateur
```
PATCH /api/utilisateurs/{user_id}/activate
```

**Permissions :** Administrateurs uniquement

#### Désactiver un utilisateur
```
PATCH /api/utilisateurs/{user_id}/deactivate
```

**Permissions :** Administrateurs uniquement
**Note :** Un administrateur ne peut pas se désactiver lui-même

#### Liste des rôles disponibles
```
GET /api/utilisateurs/roles/list
```

**Permissions :** Tous les utilisateurs authentifiés

**Réponse :**
```json
[
  {
    "value": "admin",
    "label": "Admin"
  },
  {
    "value": "agent_back_office",
    "label": "Agent Back Office"
  },
  ...
]
```

## 🔒 Sécurité et Permissions

### Règles de sécurité

1. **Création d'utilisateurs** : Seuls les administrateurs peuvent créer de nouveaux utilisateurs
2. **Modification de rôle** : Seuls les administrateurs peuvent modifier les rôles
3. **Activation/Désactivation** : Seuls les administrateurs peuvent activer/désactiver des comptes
4. **Auto-modification** : Les utilisateurs peuvent modifier leurs propres informations (nom, prénom, email, téléphone) mais pas leur rôle ou statut
5. **Auto-suppression** : Un utilisateur ne peut pas supprimer ou désactiver son propre compte

### Validation des données

- **Email** : Doit être unique et valide
- **Téléphone** : Doit être unique si fourni
- **Mot de passe** : Minimum 6 caractères
- **Rôle** : Doit être l'un des rôles valides

## 📝 Exemples d'utilisation

### Exemple 1 : Créer un nouvel agent back-office

```bash
curl -X POST "http://localhost:8000/api/utilisateurs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Martin",
    "prenom": "Sophie",
    "email": "sophie.martin@mairie.ga",
    "telephone": "+241 01 23 45 68",
    "password": "securepass123",
    "role": "agent_back_office"
  }'
```

### Exemple 2 : Lister tous les utilisateurs actifs

```bash
curl -X GET "http://localhost:8000/api/utilisateurs?actif=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Exemple 3 : Modifier son propre profil

```bash
curl -X PUT "http://localhost:8000/api/utilisateurs/5" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Martin",
    "prenom": "Sophie",
    "telephone": "+241 01 23 45 69"
  }'
```

### Exemple 4 : Désactiver un utilisateur

```bash
curl -X PATCH "http://localhost:8000/api/utilisateurs/10/deactivate" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## ⚠️ Notes importantes

1. **Route `/api/auth/register`** : Cette route est toujours disponible mais est marquée comme DEPRECATED. Utilisez plutôt `POST /api/utilisateurs`

2. **Changement de mot de passe** : Utilisez `POST /api/auth/change-password` pour changer votre propre mot de passe

3. **Résiliation de mot de passe** : Actuellement, seuls les administrateurs peuvent réinitialiser les mots de passe en modifiant directement l'utilisateur (nécessite de connaître le nouveau mot de passe hash)

4. **Historique** : Les modifications sont tracées via les champs `created_at` et `updated_at`

## 🧪 Tests

Pour tester le système :

1. **Créer un utilisateur admin** (via script de seed ou directement en base)
2. **Se connecter** avec cet utilisateur
3. **Créer d'autres utilisateurs** avec différents rôles
4. **Tester les permissions** en essayant d'accéder aux endpoints avec différents rôles

## 📚 Documentation API

La documentation interactive est disponible sur :
- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`


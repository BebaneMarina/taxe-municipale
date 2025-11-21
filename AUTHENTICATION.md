# Authentification JWT - Guide

## Pourquoi JWT au lieu de Keycloak ?

JWT (JSON Web Token) a été choisi car :
- **Simplicité** : Pas besoin d'un serveur d'authentification séparé
- **Léger** : Solution intégrée directement dans l'API
- **Rapide** : Pas de dépendance externe
- **Suffisant** : Pour une application interne de la mairie
- **Contrôle total** : Gestion complète de l'authentification

## Architecture

### Backend (FastAPI)

1. **Table `utilisateur`** : Stocke les utilisateurs avec leurs rôles
2. **Routes d'authentification** (`/api/auth`) :
   - `POST /api/auth/login` : Connexion et génération du token
   - `GET /api/auth/me` : Informations de l'utilisateur connecté
   - `PUT /api/auth/me` : Mise à jour du profil
   - `POST /api/auth/change-password` : Changement de mot de passe
   - `POST /api/auth/register` : Création d'utilisateur (admin uniquement)

3. **Sécurité** :
   - Hashage des mots de passe avec bcrypt
   - Tokens JWT avec expiration (30 jours)
   - Protection des routes avec dépendances FastAPI

### Frontend (Angular)

1. **Service `AuthService`** : Gestion de l'authentification
2. **Interceptor HTTP** : Ajout automatique du token aux requêtes
3. **Stockage** : Token et utilisateur dans localStorage

## Rôles disponibles

- `admin` : Administrateur système
- `agent_back_office` : Agent back-office (activation collecteurs, transferts, validation)
- `agent_front_office` : Agent front-office (accès données client, modification)
- `controleur_interne` : Contrôleur interne (lecture seule, extraction données)
- `collecteur` : Collecteur (application mobile)

## Utilisation

### Backend

```python
from auth.security import get_current_active_user, require_role
from database.models import Utilisateur

# Route protégée (nécessite authentification)
@router.get("/protected")
def protected_route(current_user: Utilisateur = Depends(get_current_active_user)):
    return {"message": f"Bonjour {current_user.nom}"}

# Route avec contrôle de rôle
@router.get("/admin-only")
def admin_route(current_user: Utilisateur = Depends(require_role(["admin"]))):
    return {"message": "Accès admin"}
```

### Frontend

```typescript
// Connexion
this.authService.login({ email: 'user@example.com', password: 'password' })
  .subscribe(response => {
    console.log('Connecté !', response.user);
  });

// Vérifier l'authentification
if (this.authService.isAuthenticated()) {
  // Utilisateur connecté
}

// Vérifier le rôle
if (this.authService.hasRole('admin')) {
  // Utilisateur est admin
}

// Récupérer l'utilisateur actuel
const user = this.authService.getCurrentUserValue();
```

## Configuration

### Variables d'environnement

Dans `backend/.env` :
```env
SECRET_KEY=votre-secret-key-tres-securisee-changez-moi-en-production
ACCESS_TOKEN_EXPIRE_MINUTES=43200  # 30 jours
```

### Utilisateur admin par défaut

Lors de l'initialisation de la base de données, un utilisateur admin est créé :
- **Email** : `admin@mairie-libreville.ga`
- **Mot de passe** : `admin123`
- **⚠️ À changer immédiatement en production !**

## Sécurité

1. **Mots de passe** : Hashés avec bcrypt (10 rounds)
2. **Tokens JWT** : Signés avec HS256
3. **Expiration** : Tokens expirent après 30 jours
4. **HTTPS** : À utiliser en production
5. **Secret Key** : À changer en production et stocker de manière sécurisée

## Migration depuis Keycloak

Si vous aviez prévu Keycloak, voici les changements :

1. ✅ Suppression de la dépendance `keycloak-angular`
2. ✅ Création du système JWT
3. ✅ Service d'authentification Angular
4. ✅ Interceptor HTTP pour les tokens
5. ✅ Protection des routes backend

## Prochaines étapes

- [ ] Implémenter le refresh token
- [ ] Ajouter la gestion des sessions
- [ ] Implémenter la réinitialisation de mot de passe
- [ ] Ajouter la vérification d'email
- [ ] Implémenter les guards de route Angular


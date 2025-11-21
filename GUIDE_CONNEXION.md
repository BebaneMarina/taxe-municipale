# Guide de Connexion - Page de Connexion

## 🎨 Page de Connexion Créée

Une page de connexion moderne et élégante a été créée avec les fonctionnalités suivantes :

### Fonctionnalités

1. **Design moderne** :
   - Gradient de fond animé
   - Animations fluides
   - Design responsive
   - Logo/emblème de la mairie

2. **Validation des formulaires** :
   - Validation en temps réel
   - Messages d'erreur clairs
   - Indicateurs visuels

3. **Sécurité** :
   - Masquage/affichage du mot de passe
   - Gestion des erreurs d'authentification
   - Protection CSRF via tokens JWT

4. **Expérience utilisateur** :
   - Loading state pendant la connexion
   - Messages d'erreur contextuels
   - Redirection automatique après connexion

## 📁 Fichiers Créés

- `src/app/components/pages/login/login.component.ts`
- `src/app/components/pages/login/login.component.html`
- `src/app/components/pages/login/login.component.scss`
- `src/app/guards/auth.guard.ts` - Protection des routes
- `src/app/guards/role.guard.ts` - Protection par rôle
- `src/app/directives/click-outside.directive.ts` - Directive pour fermer les menus

## 🔐 Authentification

### Utilisateur Admin par Défaut

- **Email** : `admin@mairie-libreville.ga`
- **Mot de passe** : `admin123`

### Utilisation

1. Accéder à `/login`
2. Entrer les identifiants
3. Le token JWT est automatiquement stocké
4. Redirection vers le dashboard

## 🛡️ Protection des Routes

Toutes les routes (sauf `/login`) sont protégées par `AuthGuard` :

```typescript
{
  path: '',
  component: LayoutComponent,
  canActivate: [AuthGuard],  // Protection ici
  children: [...]
}
```

### Protection par Rôle

Certaines routes nécessitent des rôles spécifiques :

```typescript
{
  path: 'administration',
  canActivate: [RoleGuard],
  data: { roles: ['admin'] }  // Seuls les admins
}
```

## 🎯 Topbar Mis à Jour

Le topbar affiche maintenant :
- Nom de l'utilisateur connecté
- Menu déroulant avec :
  - Informations utilisateur
  - Rôle avec badge coloré
  - Lien vers le profil
  - Lien vers les paramètres
  - Bouton de déconnexion

## 🚀 Prochaines Étapes

1. **Page "Mot de passe oublié"** : À implémenter
2. **Changement de mot de passe** : Déjà disponible via API
3. **Gestion des sessions** : Refresh token (optionnel)
4. **2FA** : Authentification à deux facteurs (optionnel)

## 📝 Notes

- Le token est stocké dans `localStorage`
- Le token expire après 30 jours
- La déconnexion vide le localStorage
- Les routes sont automatiquement protégées


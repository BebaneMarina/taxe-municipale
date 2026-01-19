import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { catchError, map, of } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): boolean | Promise<boolean> {
    const currentUrl = state.url;
    
    // Si pas de token, rediriger immédiatement vers /login
    if (!this.authService.isAuthenticated()) {
      // Toujours rediriger vers /login si pas authentifié
      // Utiliser setTimeout pour éviter les conflits avec la navigation initiale
      setTimeout(() => {
        if (currentUrl !== '/login' && !currentUrl.startsWith('/login')) {
          this.router.navigate(['/login'], { 
            queryParams: { returnUrl: currentUrl },
            replaceUrl: true 
          }).catch(() => {
            // Ignorer les erreurs de navigation
          });
        }
      }, 0);
      return false;
    }

    // Vérifier que le token est valide en récupérant l'utilisateur courant
    const user = this.authService.getCurrentUserValue();
    
    // Si l'utilisateur est déjà en cache, laisser passer
    if (user) {
      return true;
    }

    // Sinon, vérifier le token en récupérant l'utilisateur de manière asynchrone
    return new Promise<boolean>((resolve) => {
      this.authService.getCurrentUser().subscribe({
        next: () => {
          resolve(true);
        },
        error: () => {
          // Token invalide ou expiré, déconnecter et rediriger
          this.authService.logout();
          // Rediriger vers /login
          setTimeout(() => {
            if (currentUrl !== '/login' && !currentUrl.startsWith('/login')) {
              this.router.navigate(['/login'], { 
                queryParams: { returnUrl: currentUrl },
                replaceUrl: true 
              }).catch(() => {
                // Ignorer les erreurs de navigation
              });
            }
          }, 0);
          resolve(false);
        }
      });
    });
  }
}


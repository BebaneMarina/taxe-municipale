import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(route: ActivatedRouteSnapshot): boolean {
    const requiredRoles = route.data['roles'] as Array<string>;
    
    if (!requiredRoles || requiredRoles.length === 0) {
      return true;
    }

    const user = this.authService.getCurrentUserValue();
    
    if (!user) {
      this.router.navigate(['/login']);
      return false;
    }

    if (this.authService.hasAnyRole(requiredRoles)) {
      return true;
    }

    // Rediriger vers le dashboard si pas les permissions
    this.router.navigate(['/']);
    return false;
  }
}


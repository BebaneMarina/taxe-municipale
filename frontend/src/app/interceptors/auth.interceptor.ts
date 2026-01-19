import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = this.authService.getToken();
    
    // Cloner la requête avec les headers nécessaires pour UTF-8
    let clonedReq = req.clone({
      setHeaders: {
        'Accept': 'application/json; charset=utf-8',
        'Accept-Charset': 'utf-8'
      }
    });
    
    if (token) {
      clonedReq = clonedReq.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`,
          'Accept': 'application/json; charset=utf-8',
          'Accept-Charset': 'utf-8'
        }
      });
    }
    
    return next.handle(clonedReq).pipe(
      catchError((error: HttpErrorResponse) => {
        // Si l'erreur est 401 (Unauthorized) ou 403 (Forbidden), déconnecter
        if (error.status === 401 || error.status === 403) {
          // Ne pas déconnecter si on est en train de faire une requête de login
          if (!req.url.includes('/auth/login')) {
            this.authService.logout();
            // Ne rediriger que si on n'est pas déjà sur la page de login
            if (!this.router.url.includes('/login')) {
              this.router.navigate(['/login']);
            }
          }
        }
        return throwError(() => error);
      })
    );
  }
}


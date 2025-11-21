import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user?: {
    id: number;
    nom: string;
    prenom: string;
    email: string;
    role: string;
  };
}

export interface User {
  id: number;
  nom: string;
  prenom: string;
  email: string;
  telephone?: string;
  role: string;
  actif: boolean;
  derniere_connexion?: string;
  created_at: string;
  updated_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl || 'http://localhost:8000/api';
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    // Vérifier si un token existe au démarrage
    const token = this.getToken();
    if (token) {
      this.getCurrentUser().subscribe();
    }
  }

  login(credentials: LoginCredentials): Observable<TokenResponse> {
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    return this.http.post<TokenResponse>(`${this.apiUrl}/auth/login`, formData).pipe(
      tap(response => {
        if (response.access_token) {
          localStorage.setItem('access_token', response.access_token);
          if (response.user) {
            localStorage.setItem('current_user', JSON.stringify(response.user));
            this.currentUserSubject.next(response.user as any);
          }
        }
      })
    );
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('current_user');
    this.currentUserSubject.next(null);
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/auth/me`).pipe(
      tap(user => {
        localStorage.setItem('current_user', JSON.stringify(user));
        this.currentUserSubject.next(user);
      })
    );
  }

  updateCurrentUser(userData: Partial<User>): Observable<User> {
    return this.http.put<User>(`${this.apiUrl}/auth/me`, userData).pipe(
      tap(user => {
        localStorage.setItem('current_user', JSON.stringify(user));
        this.currentUserSubject.next(user);
      })
    );
  }

  changePassword(currentPassword: string, newPassword: string): Observable<void> {
    return this.http.post<void>(`${this.apiUrl}/auth/change-password`, {
      current_password: currentPassword,
      new_password: newPassword
    });
  }

  getCurrentUserValue(): User | null {
    const stored = localStorage.getItem('current_user');
    if (stored) {
      return JSON.parse(stored);
    }
    return this.currentUserSubject.value;
  }

  hasRole(role: string): boolean {
    const user = this.getCurrentUserValue();
    return user?.role === role;
  }

  hasAnyRole(roles: string[]): boolean {
    const user = this.getCurrentUserValue();
    return user ? roles.includes(user.role) : false;
  }
}


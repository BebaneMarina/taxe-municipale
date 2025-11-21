import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NgOptimizedImage } from '@angular/common';
import { H1Component } from '../texts/h1/h1.component';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService, User } from '../../../services/auth.service';
import { ClickOutsideDirective } from '../../../directives/click-outside.directive';

@Component({
  selector: 'app-topbar',
  standalone: true,
  imports: [
    CommonModule,
    NgOptimizedImage,
    H1Component,
    ClickOutsideDirective
  ],
  templateUrl: './topbar.component.html',
  styleUrl: './topbar.component.scss'
})
export class TopbarComponent implements OnInit {
  route: ActivatedRoute = inject(ActivatedRoute);
  router: Router = inject(Router);
  authService: AuthService = inject(AuthService);
  
  title: string | undefined | any = "Dashboard";
  currentUser: User | null = null;
  showUserMenu = false;

  ngOnInit() {
    // Récupérer l'utilisateur actuel
    this.currentUser = this.authService.getCurrentUserValue();
    
    // S'abonner aux changements de l'utilisateur
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });

    // Écouter les changements de route pour mettre à jour le titre
    this.router.events.subscribe(event => {
      this.getTitle();
    });
  }

  getTitle() {
    if (this.route.firstChild) {
      this.title = this.route.firstChild.snapshot.routeConfig?.title || 'Dashboard';
    }
  }

  toggleUserMenu() {
    this.showUserMenu = !this.showUserMenu;
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
    this.showUserMenu = false;
  }

  getUserDisplayName(): string {
    if (this.currentUser) {
      return `${this.currentUser.prenom} ${this.currentUser.nom}`;
    }
    return 'Utilisateur';
  }

  getUserInitials(): string {
    if (this.currentUser) {
      const prenom = this.currentUser.prenom?.charAt(0) || '';
      const nom = this.currentUser.nom?.charAt(0) || '';
      return `${prenom}${nom}`.toUpperCase();
    }
    return 'U';
  }
}

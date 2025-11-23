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
      // S'assurer que les caractères sont correctement décodés
      let prenom = this.currentUser.prenom || '';
      let nom = this.currentUser.nom || '';
      
      // Fonction pour corriger l'encodage mal formé (double encodage UTF-8)
      const fixEncoding = (text: string): string => {
        if (!text || !text.includes('Ã')) {
          return text;
        }
        
        try {
          // Si le texte contient "Ã¨", c'est probablement "è" mal encodé
          // "SystÃ¨me" devrait être "Système"
          // On essaie de décoder comme si c'était du latin-1 interprété comme UTF-8
          const bytes = new Uint8Array(
            text.split('').map(c => {
              const code = c.charCodeAt(0);
              // Si c'est un caractère dans la plage UTF-8 mal encodé
              if (code >= 0xC0 && code <= 0xFF) {
                return code;
              }
              return code;
            })
          );
          
          // Essayer de décoder comme UTF-8
          const decoder = new TextDecoder('utf-8', { fatal: false });
          let decoded = decoder.decode(bytes);
          
          // Si ça n'a pas marché, essayer latin-1 puis re-encoder
          if (decoded.includes('Ã')) {
            const latin1Decoder = new TextDecoder('latin-1', { fatal: false });
            const latin1Bytes = new Uint8Array(text.split('').map(c => c.charCodeAt(0)));
            const latin1Text = latin1Decoder.decode(latin1Bytes);
            // Re-encoder en UTF-8
            const utf8Encoder = new TextEncoder();
            const utf8Bytes = utf8Encoder.encode(latin1Text);
            decoded = new TextDecoder('utf-8', { fatal: false }).decode(utf8Bytes);
          }
          
          return decoded;
        } catch (e) {
          // Si tout échoue, retourner le texte original
          return text;
        }
      };
      
      prenom = fixEncoding(prenom);
      nom = fixEncoding(nom);
      
      const displayName = `${prenom} ${nom}`.trim();
      return displayName || 'Utilisateur';
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

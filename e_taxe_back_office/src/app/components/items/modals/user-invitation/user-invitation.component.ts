import { Component, EventEmitter, Output, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../../services/api.service';

@Component({
  selector: 'app-user-invitation',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './user-invitation.component.html',
  styleUrl: './user-invitation.component.scss'
})
export class UserInvitationComponent implements OnInit {
  @Output() userCreated = new EventEmitter<void>();
  
  private apiService = inject(ApiService);
  
  loading = false;
  error = '';
  success = false;
  loadingRoles = false;
  
  // Liste des rôles disponibles
  availableRoles: any[] = [];
  rolesFromDB: any[] = [];
  
  // Formulaire
  userForm = {
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    password: '',
    role: ''
  };

  ngOnInit(): void {
    this.loadRoles();
  }

  loadRoles(): void {
    this.loadingRoles = true;
    // Charger les rôles depuis la base de données
    this.apiService.getRoles({ actif: true }).subscribe({
      next: (response: any) => {
        console.log('Réponse API rôles:', response);
        
        // Gérer différents formats de réponse
        let roles: any[] = [];
        if (Array.isArray(response)) {
          roles = response;
        } else if (response && Array.isArray(response.items)) {
          roles = response.items;
        } else if (response && response.data && Array.isArray(response.data)) {
          roles = response.data;
        }
        
        this.rolesFromDB = roles;
        
        // Mapper les rôles pour la liste déroulante
        if (roles && roles.length > 0) {
          this.availableRoles = roles.map(r => ({
            value: r.code || r.id,
            label: r.nom || (r.code ? r.code.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()) : String(r.id)),
            code: r.code || String(r.id)
          }));
          console.log('Rôles mappés:', this.availableRoles);
        } else {
          // Si aucun rôle n'est retourné, utiliser les rôles par défaut
          console.warn('Aucun rôle retourné par l\'API, utilisation des rôles par défaut');
          this.availableRoles = [
            { value: 'admin', label: 'Administrateur', code: 'admin' },
            { value: 'agent_back_office', label: 'Agent Back Office', code: 'agent_back_office' },
            { value: 'agent_front_office', label: 'Agent Front Office', code: 'agent_front_office' },
            { value: 'controleur_interne', label: 'Contrôleur Interne', code: 'controleur_interne' },
            { value: 'collecteur', label: 'Collecteur', code: 'collecteur' }
          ];
        }
        this.loadingRoles = false;
      },
      error: (err) => {
        console.error('Erreur chargement rôles:', err);
        this.loadingRoles = false;
        // Fallback sur les rôles par défaut
        this.availableRoles = [
          { value: 'admin', label: 'Administrateur', code: 'admin' },
          { value: 'agent_back_office', label: 'Agent Back Office', code: 'agent_back_office' },
          { value: 'agent_front_office', label: 'Agent Front Office', code: 'agent_front_office' },
          { value: 'controleur_interne', label: 'Contrôleur Interne', code: 'controleur_interne' },
          { value: 'collecteur', label: 'Collecteur', code: 'collecteur' }
        ];
      }
    });
  }

  async onSubmit(): Promise<void> {
    this.error = '';
    this.success = false;
    
    // Validation
    if (!this.userForm.nom || !this.userForm.email || !this.userForm.password || !this.userForm.role) {
      this.error = 'Veuillez remplir tous les champs obligatoires';
      return;
    }
    
    if (this.userForm.password.length < 6) {
      this.error = 'Le mot de passe doit contenir au moins 6 caractères';
      return;
    }

    this.loading = true;

    try {
      // Normaliser le format du rôle (minuscules, underscores)
      const normalizedRole = this.userForm.role.toLowerCase().trim().replace(/\s+/g, '_');
      
      // Créer l'utilisateur (le backend créera automatiquement le rôle s'il n'existe pas)
      this.apiService.createUtilisateur({
        nom: this.userForm.nom,
        prenom: this.userForm.prenom,
        email: this.userForm.email,
        telephone: this.userForm.telephone || undefined,
        password: this.userForm.password,
        role: normalizedRole
      }).subscribe({
        next: () => {
          this.success = true;
          this.resetForm();
          this.userCreated.emit();
          setTimeout(() => {
            this.success = false;
          }, 3000);
        },
        error: (err) => {
          this.error = err.error?.detail || 'Erreur lors de la création de l\'utilisateur';
          this.loading = false;
        }
      });
    } catch (error: any) {
      this.error = 'Erreur lors de la création';
      this.loading = false;
    }
  }

  resetForm(): void {
    this.userForm = {
      nom: '',
      prenom: '',
      email: '',
      telephone: '',
      password: '',
      role: ''
    };
    this.loading = false;
  }
}

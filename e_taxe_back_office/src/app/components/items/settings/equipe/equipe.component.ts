import { Component, OnInit, inject, model, ModelSignal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../../services/api.service';
import { ModalComponent } from '../../modal/modal.component';
import { UserInvitationComponent } from '../../modals/user-invitation/user-invitation.component';
import { UserDetailsComponent } from '../../modals/user-details/user-details.component';

interface Utilisateur {
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

@Component({
  selector: 'app-equipe',
  imports: [CommonModule, FormsModule, ModalComponent, UserInvitationComponent, UserDetailsComponent],
  standalone: true,
  templateUrl: './equipe.component.html',
  styleUrl: './equipe.component.scss'
})
export class EquipeComponent implements OnInit {
  private apiService = inject(ApiService);
  
  active: ModelSignal<boolean> = model<boolean>(true);
  activeModalUser: ModelSignal<boolean> = model<boolean>(false);
  activeModalDetails: ModelSignal<boolean> = model<boolean>(false);
  
  utilisateurs: Utilisateur[] = [];
  selectedUtilisateur: Utilisateur | null = null;
  loading = false;
  error = '';
  searchTerm = '';
  
  // Pagination
  currentPage = 1;
  pageSize = 10;
  totalItems = 0;
  totalPages = 1;

  ngOnInit(): void {
    this.loadUtilisateurs();
  }

  loadUtilisateurs(): void {
    this.loading = true;
    this.error = '';
    
    const params: any = {
      skip: (this.currentPage - 1) * this.pageSize,
      limit: this.pageSize
    };
    
    if (this.searchTerm) {
      params.search = this.searchTerm;
    }
    
    this.apiService.getUtilisateurs(params).subscribe({
      next: (response: any) => {
        // Gérer différents formats de réponse
        if (response && response.items) {
          this.utilisateurs = response.items;
          this.totalItems = response.total || response.items.length;
        } else if (Array.isArray(response)) {
          this.utilisateurs = response;
          this.totalItems = response.length;
        } else {
          this.utilisateurs = [];
          this.totalItems = 0;
        }
        
        this.totalPages = Math.ceil(this.totalItems / this.pageSize);
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des utilisateurs:', err);
        this.error = 'Erreur lors du chargement des utilisateurs';
        this.loading = false;
      }
    });
  }

  onSearch(): void {
    this.currentPage = 1;
    this.loadUtilisateurs();
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadUtilisateurs();
  }

  onActiveChange(): void {
    this.active.set(true);
  }

  onActiveModalUser(value: boolean): void {
    this.activeModalUser.set(value);
  }

  onUserCreated(): void {
    this.loadUtilisateurs();
    this.activeModalUser.set(false);
  }

  onUserClick(utilisateur: Utilisateur): void {
    this.selectedUtilisateur = utilisateur;
    this.activeModalDetails.set(true);
  }

  toggleActif(utilisateur: Utilisateur): void {
    if (utilisateur.actif) {
      this.apiService.deactivateUtilisateur(utilisateur.id).subscribe({
        next: () => {
          this.loadUtilisateurs();
        },
        error: (err) => {
          console.error('Erreur lors de la désactivation:', err);
          this.error = 'Erreur lors de la désactivation de l\'utilisateur';
        }
      });
    } else {
      this.apiService.activateUtilisateur(utilisateur.id).subscribe({
        next: () => {
          this.loadUtilisateurs();
        },
        error: (err) => {
          console.error('Erreur lors de l\'activation:', err);
          this.error = 'Erreur lors de l\'activation de l\'utilisateur';
        }
      });
    }
  }

  formatRole(role: string): string {
    return role.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
  }

  formatDate(date: string | undefined): string {
    if (!date) return 'Jamais';
    return new Date(date).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  // Exposer Math pour le template
  Math = Math;
}

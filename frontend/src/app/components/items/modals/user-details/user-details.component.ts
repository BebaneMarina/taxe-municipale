import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ContenerGrayComponent } from '../../contener-gray/contener-gray.component';

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
  selector: 'app-user-details',
  standalone: true,
  imports: [
    CommonModule,
    ContenerGrayComponent
  ],
  templateUrl: './user-details.component.html',
  styleUrl: './user-details.component.scss'
})
export class UserDetailsComponent {
  @Input() utilisateur!: Utilisateur | null;

  formatRole(role: string): string {
    return role.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
  }

  formatDate(date: string | undefined): string {
    if (!date) return 'Jamais';
    const dateObj = new Date(date);
    const now = new Date();
    const diffMs = now.getTime() - dateObj.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'À l\'instant';
    if (diffMins < 60) return `Il y a ${diffMins} minute${diffMins > 1 ? 's' : ''}`;
    if (diffHours < 24) return `Il y a ${diffHours} heure${diffHours > 1 ? 's' : ''}`;
    if (diffDays < 7) return `Il y a ${diffDays} jour${diffDays > 1 ? 's' : ''}`;
    
    return dateObj.toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  formatCreatedDate(date: string | undefined): string {
    if (!date) return '-';
    return new Date(date).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }
}

import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../services/api.service';

@Component({
  selector: 'app-impayes',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './impayes.component.html',
  styleUrl: './impayes.component.scss'
})
export class ImpayesComponent implements OnInit {
  private apiService = inject(ApiService);

  impayes: any[] = [];
  loading = false;
  error = '';
  
  // Filtres
  filters = {
    contribuable_id: null as number | null,
    collecteur_id: null as number | null,
    statut: '',
    priorite: '',
    jours_retard_min: null as number | null
  };

  // Pagination
  currentPage = 0;
  pageSize = 20;
  total = 0;

  // Statistiques
  stats: any = null;

  // Collecteurs pour assignation
  collecteurs: any[] = [];

  ngOnInit(): void {
    this.loadImpayes();
    this.loadStats();
    this.loadCollecteurs();
  }

  loadImpayes(): void {
    this.loading = true;
    this.error = '';

    const params: any = {
      skip: this.currentPage * this.pageSize,
      limit: this.pageSize
    };

    if (this.filters.contribuable_id) params.contribuable_id = this.filters.contribuable_id;
    if (this.filters.collecteur_id) params.collecteur_id = this.filters.collecteur_id;
    if (this.filters.statut) params.statut = this.filters.statut;
    if (this.filters.priorite) params.priorite = this.filters.priorite;
    if (this.filters.jours_retard_min) params.jours_retard_min = this.filters.jours_retard_min;

    this.apiService.getImpayes(params).subscribe({
      next: (response) => {
        if (response.items) {
          this.impayes = response.items;
          this.total = response.total;
        } else {
          this.impayes = response;
          this.total = response.length;
        }
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Erreur lors du chargement des impayés';
        this.loading = false;
      }
    });
  }

  loadStats(): void {
    this.apiService.getStatistiquesImpayes().subscribe({
      next: (data) => {
        this.stats = data;
      },
      error: (err) => {
        console.error('Erreur chargement stats:', err);
      }
    });
  }

  loadCollecteurs(): void {
    this.apiService.getCollecteurs({ actif: true, limit: 1000 }).subscribe({
      next: (data) => {
        this.collecteurs = data;
      },
      error: (err) => {
        console.error('Erreur chargement collecteurs:', err);
      }
    });
  }

  applyFilters(): void {
    this.currentPage = 0;
    this.loadImpayes();
  }

  resetFilters(): void {
    this.filters = {
      contribuable_id: null,
      collecteur_id: null,
      statut: '',
      priorite: '',
      jours_retard_min: null
    };
    this.applyFilters();
  }

  detecterImpayes(): void {
    if (!confirm('Voulez-vous détecter automatiquement les nouveaux impayés ?')) {
      return;
    }

    this.loading = true;
    this.apiService.detecterImpayes({
      jours_retard_min: 7,
      taux_penalite: 0.5
    }).subscribe({
      next: (dossiers) => {
        alert(`${dossiers.length} dossier(s) d'impayé(s) détecté(s) avec succès`);
        this.loadImpayes();
        this.loadStats();
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Erreur lors de la détection des impayés';
        this.loading = false;
      }
    });
  }

  assignerDossier(dossierId: number, collecteurId: number): void {
    if (!confirm('Assigner ce dossier au collecteur sélectionné ?')) {
      return;
    }

    this.apiService.assignerDossier(dossierId, collecteurId).subscribe({
      next: () => {
        this.loadImpayes();
        this.loadStats();
      },
      error: (err) => {
        this.error = err.error?.detail || 'Erreur lors de l\'assignation';
      }
    });
  }

  cloturerDossier(id: number): void {
    if (!confirm('Clôturer ce dossier d\'impayé ?')) {
      return;
    }

    this.apiService.cloturerDossier(id).subscribe({
      next: () => {
        this.loadImpayes();
        this.loadStats();
      },
      error: (err) => {
        this.error = err.error?.detail || 'Erreur lors de la clôture';
      }
    });
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadImpayes();
  }

  getTotalPages(): number {
    return Math.ceil(this.total / this.pageSize);
  }

  getStatutClass(statut: string): string {
    const classes: { [key: string]: string } = {
      'en_cours': 'bg-yellow-100 text-yellow-800',
      'partiellement_paye': 'bg-orange-100 text-orange-800',
      'paye': 'bg-green-100 text-green-800',
      'archive': 'bg-gray-100 text-gray-800'
    };
    return classes[statut] || 'bg-gray-100 text-gray-800';
  }

  getPrioriteClass(priorite: string): string {
    const classes: { [key: string]: string } = {
      'urgente': 'bg-red-100 text-red-800',
      'elevee': 'bg-orange-100 text-orange-800',
      'normale': 'bg-yellow-100 text-yellow-800',
      'faible': 'bg-green-100 text-green-800'
    };
    return classes[priorite] || 'bg-gray-100 text-gray-800';
  }
}


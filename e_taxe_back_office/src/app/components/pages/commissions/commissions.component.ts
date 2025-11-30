import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../services/api.service';

interface CommissionRecord {
  id: number;
  date_jour: string;
  collecteur_id: number;
  collecteur_nom?: string;
  collecteur_matricule?: string;
  montant_collecte: number;
  commission_montant: number;
  commission_pourcentage: number;
  statut_paiement: string;
  fichier_id?: number;
  created_at: string;
}

@Component({
  selector: 'app-commissions',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './commissions.component.html',
  styleUrl: './commissions.component.scss'
})
export class CommissionsComponent implements OnInit {
  private apiService = inject(ApiService);

  filters = {
    dateDebut: '',
    dateFin: ''
  };

  commissions = signal<CommissionRecord[]>([]);
  loadingCommissions = signal<boolean>(false);
  message = signal<string | null>(null);

  ngOnInit(): void {
    this.loadCommissions();
  }

  refreshCommissions(): void {
    this.message.set(null);
    this.loadCommissions();
  }

  resetFilters(): void {
    this.filters = {
      dateDebut: '',
      dateFin: ''
    };
    this.refreshCommissions();
  }

  private buildParams(): Record<string, string | number> {
    const params: Record<string, string | number> = { limit: 500 };
    if (this.filters.dateDebut) {
      params['date_debut'] = this.filters.dateDebut;
    }
    if (this.filters.dateFin) {
      params['date_fin'] = this.filters.dateFin;
    }
    return params;
  }

  private loadCommissions(): void {
    this.loadingCommissions.set(true);
    this.apiService.getCommissions(this.buildParams()).subscribe({
      next: (data: CommissionRecord[]) => {
        this.commissions.set(data || []);
        this.loadingCommissions.set(false);
        if (!data || !data.length) {
          this.message.set('Aucune commission enregistrée pour ces critères.');
        }
      },
      error: (err) => {
        this.commissions.set([]);
        this.loadingCommissions.set(false);
        this.message.set(err?.error?.detail || 'Impossible de charger les commissions');
      }
    });
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'XAF', maximumFractionDigits: 0 }).format(value || 0);
  }

}


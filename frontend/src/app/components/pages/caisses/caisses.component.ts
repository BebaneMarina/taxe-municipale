import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Component, inject, OnInit } from '@angular/core';
import { ApiService } from '../../../services/api.service';

@Component({
  selector: 'app-parametrage-caisse',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './caisses.component.html',
  styleUrl: './caisses.component.scss'
})
export class ParametrageCaisseComponent implements OnInit {
  private apiService = inject(ApiService);

  loading = true;
  caisses: any[] = [];
  selectedCaisse: any = null;
  etatCaisse: any = null;
  errorMessage: string | null = null;
  operationsLoading = false;
  filters = {
    type_caisse: 'all',
    etat: 'all'
  };

  ngOnInit(): void {
    this.loadCaisses();
  }

  loadCaisses(): void {
    this.loading = true;
    this.errorMessage = null;

    const params: any = { limit: 100 };
    if (this.filters.type_caisse !== 'all') {
      params.type_caisse = this.filters.type_caisse;
    }
    if (this.filters.etat !== 'all') {
      params.etat = this.filters.etat;
    }

    this.apiService.getCaisses(params).subscribe({
      next: (response) => {
        this.caisses = response?.items || [];
        this.loading = false;
        if (this.caisses.length > 0) {
          this.selectCaisse(this.caisses[0]);
        } else {
          this.selectedCaisse = null;
          this.etatCaisse = null;
        }
      },
      error: (err) => {
        this.loading = false;
        this.errorMessage = err?.error?.detail || 'Impossible de charger les caisses';
      }
    });
  }

  selectCaisse(caisse: any): void {
    this.selectedCaisse = caisse;
    this.operationsLoading = true;
    this.errorMessage = null;

    this.apiService.getEtatCaisse(caisse.id).subscribe({
      next: (etat) => {
        this.etatCaisse = etat;
        this.operationsLoading = false;
      },
      error: (err) => {
        this.operationsLoading = false;
        this.errorMessage = err?.error?.detail || 'Impossible de récupérer l’état de la caisse';
      }
    });
  }

  get totalActives(): number {
    return this.caisses.filter(c => c.actif).length;
  }

  get totalSolde(): number {
    return this.caisses.reduce((sum, caisse) => sum + Number(caisse.solde_actuel || 0), 0);
  }
}


import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../../services/api.service';

@Component({
  selector: 'app-affectation-caisse',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './affectation-caisse.component.html',
  styleUrl: './affectation-caisse.component.scss'
})
export class AffectationCaisseComponent implements OnInit {
  private apiService = inject(ApiService);

  caisses = signal<any[]>([]);
  collecteurs = signal<any[]>([]);
  loading = signal<boolean>(true);
  message = signal<string | null>(null);
  processingId: number | null = null;

  ngOnInit(): void {
    this.refresh();
  }

  rafraichir(): void {
    this.refresh();
  }

  refresh(): void {
    this.loading.set(true);
    this.message.set(null);
    this.apiService.getCaisses({ limit: 50 }).subscribe({
      next: (res) => {
        this.caisses.set(res?.items || []);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.message.set('Impossible de charger les caisses');
      }
    });

    this.apiService.getCollecteurs({ limit: 200 }).subscribe({
      next: (collecteurs) => this.collecteurs.set(collecteurs || []),
      error: () => this.message.set('Impossible de charger la liste des collecteurs'),
    });
  }

  affecter(caisse: any): void {
    if (!caisse.new_collecteur_id) {
      this.message.set('Merci de sélectionner un collecteur');
      return;
    }

    this.processingId = caisse.id;
    this.apiService.updateCaisse(caisse.id, { collecteur_id: caisse.new_collecteur_id }).subscribe({
      next: () => {
        this.message.set('Caisse affectée avec succès');
        this.processingId = null;
        this.refresh();
      },
      error: (err) => {
        this.message.set(err?.error?.detail || 'Erreur lors de l’affectation');
        this.processingId = null;
      }
    });
  }

  trackById(_: number, item: any): number {
    return item.id;
  }
}


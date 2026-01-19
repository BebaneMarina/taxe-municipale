import { CommonModule } from '@angular/common';
import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../../services/api.service';

interface Coupure {
  id: number;
  valeur: number;
  devise: string;
  type_coupure: 'billet' | 'piece';
  description?: string;
  ordre_affichage: number;
  actif: boolean;
}

interface CoupuresResponse {
  items: Coupure[];
  total: number;
}

@Component({
  selector: 'app-parametrage-coupures',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './parametrage-coupures.component.html',
  styleUrl: './parametrage-coupures.component.scss'
})
export class ParametrageCoupuresComponent {
  readonly typeOptions = [
    { value: 'billet', label: 'Billet' },
    { value: 'piece', label: 'Pièce' }
  ];

  loading = true;
  creating = false;
  processingId: number | null = null;
  errorMessage = signal<string | null>(null);
  coupures: Coupure[] = [];

  newCoupure = {
    valeur: null as number | null,
    type_coupure: 'billet' as 'billet' | 'piece',
    description: ''
  };

  constructor(private api: ApiService) {
    this.loadCoupures();
  }

  loadCoupures(): void {
    this.loading = true;
    this.errorMessage.set(null);
    this.api.getCoupures({ limit: 200, actif: undefined })
      .subscribe({
        next: (response: CoupuresResponse) => {
          this.coupures = (response?.items ?? []) as Coupure[];
          this.loading = false;
        },
        error: (err) => {
          console.error(err);
          this.errorMessage.set("Impossible de charger les coupures. Réessayez plus tard.");
          this.loading = false;
        }
      });
  }

  addCoupure(): void {
    if (!this.newCoupure.valeur || this.newCoupure.valeur <= 0) {
      this.errorMessage.set("La valeur doit être supérieure à 0.");
      return;
    }

    this.creating = true;
    this.errorMessage.set(null);

    const payload = {
      valeur: this.newCoupure.valeur,
      type_coupure: this.newCoupure.type_coupure,
      description: this.newCoupure.description?.trim() || null
    };

    this.api.createCoupure(payload).subscribe({
      next: (coupure: Coupure) => {
        this.coupures = [...this.coupures, coupure].sort((a, b) => a.ordre_affichage - b.ordre_affichage);
        this.newCoupure = { valeur: null, type_coupure: this.newCoupure.type_coupure, description: '' };
        this.creating = false;
      },
      error: (err) => {
        console.error(err);
        this.errorMessage.set(err?.error?.detail || "Impossible d'ajouter la coupure.");
        this.creating = false;
      }
    });
  }

  toggle(coupure: Coupure): void {
    if (this.processingId) return;
    this.processingId = coupure.id;
    this.api.toggleCoupure(coupure.id).subscribe({
      next: (updated: Coupure) => {
        this.coupures = this.coupures.map(c => c.id === updated.id ? updated : c);
        this.processingId = null;
      },
      error: (err) => {
        console.error(err);
        this.errorMessage.set("Impossible de mettre à jour cette coupure.");
        this.processingId = null;
      }
    });
  }

  move(coupure: Coupure, direction: 'up' | 'down'): void {
    const index = this.coupures.findIndex(c => c.id === coupure.id);
    if (index === -1) return;

    const neighborIndex = direction === 'up' ? index - 1 : index + 1;
    if (neighborIndex < 0 || neighborIndex >= this.coupures.length) return;

    const neighbor = this.coupures[neighborIndex];
    const payload = { ordre_affichage: neighbor.ordre_affichage };

    this.processingId = coupure.id;
    this.api.updateCoupure(coupure.id, payload).subscribe({
      next: () => {
        const neighborPayload = { ordre_affichage: coupure.ordre_affichage };
        this.api.updateCoupure(neighbor.id, neighborPayload).subscribe({
          next: () => {
            this.processingId = null;
            this.loadCoupures();
          },
          error: () => {
            this.processingId = null;
            this.loadCoupures();
          }
        });
      },
      error: (err) => {
        console.error(err);
        this.errorMessage.set("Impossible de réordonner les coupures.");
        this.processingId = null;
      }
    });
  }

  deleteCoupure(coupure: Coupure): void {
    if (this.processingId || !confirm(`Supprimer la coupure ${coupure.valeur} ${coupure.devise} ?`)) return;
    this.processingId = coupure.id;
    this.api.deleteCoupure(coupure.id).subscribe({
      next: () => {
        this.coupures = this.coupures.filter(c => c.id !== coupure.id);
        this.processingId = null;
      },
      error: (err) => {
        console.error(err);
        this.errorMessage.set("Impossible de supprimer cette coupure.");
        this.processingId = null;
      }
    });
  }

  trackById(_: number, item: Coupure): number {
    return item.id;
  }
}


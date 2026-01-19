import { CommonModule } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../../services/api.service';

@Component({
  selector: 'app-approvisionnement-caisse',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './approvisionnement-caisse.component.html',
  styleUrl: './approvisionnement-caisse.component.scss'
})
export class ApprovisionnementCaisseComponent implements OnInit {
  private apiService = inject(ApiService);

  caisses: any[] = [];
  form = {
    caisse_id: undefined as number | undefined,
    montant: 0,
    libelle: 'Approvisionnement manuel',
    notes: ''
  };
  message: string | null = null;

  ngOnInit(): void {
    this.apiService.getCaisses({ limit: 50 }).subscribe({
      next: (res) => this.caisses = res?.items || [],
      error: () => this.message = 'Impossible de charger les caisses'
    });
  }

  approvisionner(): void {
    this.message = null;
    if (!this.form.caisse_id || this.form.montant <= 0) {
      this.message = 'Merci de sélectionner une caisse et un montant';
      return;
    }

    const payload = {
      type_operation: 'entree',
      montant: this.form.montant,
      libelle: this.form.libelle,
      notes: this.form.notes,
    };

    this.apiService.createOperationCaisse(this.form.caisse_id, payload).subscribe({
      next: () => this.message = 'Approvisionnement enregistré',
      error: (err) => this.message = err?.error?.detail || 'Échec de l’opération'
    });
  }
}


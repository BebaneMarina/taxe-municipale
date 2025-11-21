import { Component, EventEmitter, Output, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../../services/api.service';
import { InfoCollecteCreate } from '../../../../interfaces/collecte.interface';

@Component({
  selector: 'app-create-collecte',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './create-collecte.component.html',
  styleUrl: './create-collecte.component.scss'
})
export class CreateCollecteComponent implements OnInit {
  @Output() collecteCreated = new EventEmitter<void>();
  
  private apiService = inject(ApiService);
  
  loading: boolean = false;
  error: string = '';
  
  // Listes pour les selects
  contribuables: any[] = [];
  taxes: any[] = [];
  collecteurs: any[] = [];
  
  loadingContribuables: boolean = false;
  loadingTaxes: boolean = false;
  loadingCollecteurs: boolean = false;
  
  // Form data
  formData: InfoCollecteCreate = {
    contribuable_id: 0,
    taxe_id: 0,
    collecteur_id: 0,
    montant: 0,
    type_paiement: 'especes',
    billetage: undefined,
    date_collecte: undefined
  };

  ngOnInit(): void {
    // Définir la date du jour par défaut
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    this.formData.date_collecte = today.toISOString().split('T')[0];
    
    // Charger les listes
    this.loadContribuables();
    this.loadTaxes();
    this.loadCollecteurs();
  }

  loadContribuables(): void {
    this.loadingContribuables = true;
    this.apiService.getContribuables({ actif: true, limit: 1000 }).subscribe({
      next: (data: any) => {
        this.contribuables = Array.isArray(data) ? data : (data.items || []);
        this.loadingContribuables = false;
      },
      error: (err) => {
        console.error('Erreur chargement contribuables:', err);
        this.loadingContribuables = false;
      }
    });
  }

  loadTaxes(): void {
    this.loadingTaxes = true;
    this.apiService.getTaxes({ actif: true, limit: 1000 }).subscribe({
      next: (data: any) => {
        this.taxes = Array.isArray(data) ? data : (data.items || []);
        this.loadingTaxes = false;
      },
      error: (err) => {
        console.error('Erreur chargement taxes:', err);
        this.loadingTaxes = false;
      }
    });
  }

  loadCollecteurs(): void {
    this.loadingCollecteurs = true;
    this.apiService.getCollecteurs({ actif: true, limit: 1000 }).subscribe({
      next: (data: any) => {
        this.collecteurs = Array.isArray(data) ? data : (data.items || []);
        this.loadingCollecteurs = false;
      },
      error: (err) => {
        console.error('Erreur chargement collecteurs:', err);
        this.loadingCollecteurs = false;
      }
    });
  }

  onSubmit(): void {
    this.error = '';
    
    // Validation
    if (!this.formData.contribuable_id || this.formData.contribuable_id === 0) {
      this.error = 'Le contribuable est obligatoire';
      return;
    }
    
    if (!this.formData.taxe_id || this.formData.taxe_id === 0) {
      this.error = 'La taxe est obligatoire';
      return;
    }
    
    if (!this.formData.collecteur_id || this.formData.collecteur_id === 0) {
      this.error = 'Le collecteur est obligatoire';
      return;
    }
    
    if (!this.formData.montant || this.formData.montant <= 0) {
      this.error = 'Le montant doit être supérieur à 0';
      return;
    }

    if (!this.formData.type_paiement) {
      this.error = 'Le type de paiement est obligatoire';
      return;
    }

    this.loading = true;
    
    // Préparer les données pour l'API
    const collecteData: InfoCollecteCreate = {
      contribuable_id: Number(this.formData.contribuable_id),
      taxe_id: Number(this.formData.taxe_id),
      collecteur_id: Number(this.formData.collecteur_id),
      montant: Number(this.formData.montant),
      type_paiement: this.formData.type_paiement,
      billetage: this.formData.billetage || undefined,
      date_collecte: this.formData.date_collecte ? new Date(this.formData.date_collecte).toISOString() : undefined
    };
    
    this.apiService.createCollecte(collecteData).subscribe({
      next: () => {
        this.loading = false;
        this.resetForm();
        this.collecteCreated.emit();
      },
      error: (err) => {
        this.loading = false;
        this.error = err.error?.detail || 'Erreur lors de la création de la collecte';
      }
    });
  }

  resetForm(): void {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    this.formData = {
      contribuable_id: 0,
      taxe_id: 0,
      collecteur_id: 0,
      montant: 0,
      type_paiement: 'especes',
      billetage: undefined,
      date_collecte: today.toISOString().split('T')[0]
    };
    this.error = '';
  }
}


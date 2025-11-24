import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../services/api.service';
import { Router } from '@angular/router';

interface Taxe {
  id: number;
  nom: string;
  description: string;
  montant: number;
  periodicite: string;
  service: string | null;
}

@Component({
  selector: 'app-paiement-client',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './paiement-client.component.html',
  styleUrl: './paiement-client.component.scss'
})
export class PaiementClientComponent implements OnInit {
  private apiService = inject(ApiService);
  private router = inject(Router);

  taxes: Taxe[] = [];
  loading: boolean = true;
  error: string = '';

  // Formulaire de paiement
  selectedTaxe: Taxe | null = null;
  showPaymentForm: boolean = false;
  paymentForm = {
    payer_name: '',
    phone: '',
    matricule: '',
    raison_sociale: '',
    payment_method: 'web', // 'web' ou 'mobile_instant'
    operateur: '' // 'moov_money' ou 'airtel_money'
  };

  // Statut de paiement
  processing: boolean = false;
  transactionBillingId: string = '';
  showStatus: boolean = false;
  transactionStatus: any = null;

  ngOnInit(): void {
    this.loadTaxes();
  }

  loadTaxes(): void {
    this.loading = true;
    this.apiService.getTaxesPubliques(true).subscribe({
      next: (data: Taxe[]) => {
        this.taxes = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Erreur lors du chargement des taxes';
        this.loading = false;
        console.error('Erreur:', err);
      }
    });
  }

  selectTaxe(taxe: Taxe): void {
    this.selectedTaxe = taxe;
    this.showPaymentForm = true;
    this.error = '';
  }

  backToTaxes(): void {
    this.selectedTaxe = null;
    this.showPaymentForm = false;
    this.showStatus = false;
    this.transactionBillingId = '';
    this.paymentForm = {
      payer_name: '',
      phone: '',
      matricule: '',
      raison_sociale: '',
      payment_method: 'web',
      operateur: ''
    };
  }

  async initierPaiement(): Promise<void> {
    if (!this.selectedTaxe) return;

    // Validation
    if (!this.paymentForm.payer_name || !this.paymentForm.phone) {
      this.error = 'Le nom et le téléphone sont obligatoires';
      return;
    }

    if (this.paymentForm.payment_method === 'mobile_instant' && !this.paymentForm.operateur) {
      this.error = 'Veuillez sélectionner un opérateur pour le paiement instantané';
      return;
    }

    this.processing = true;
    this.error = '';

    const transactionData = {
      taxe_id: this.selectedTaxe.id,
      payer_name: this.paymentForm.payer_name,
      phone: this.paymentForm.phone,
      matricule: this.paymentForm.matricule || undefined,
      raison_sociale: this.paymentForm.raison_sociale || undefined,
      payment_method: this.paymentForm.payment_method,
      operateur: this.paymentForm.operateur || undefined
    };

    try {
      const response = await this.apiService.initierPaiement(transactionData).toPromise();
      
      if (response) {
        this.transactionBillingId = response.billing_id;
        
        if (response.redirect_url) {
          // Redirection vers BambooPay pour paiement web
          window.location.href = response.redirect_url;
        } else if (response.reference_bp) {
          // Paiement instantané - afficher le statut
          this.showStatus = true;
          this.checkTransactionStatus();
        } else {
          this.error = 'Erreur: aucune URL de redirection ou référence reçue';
        }
      }
    } catch (err: any) {
      this.error = err.error?.detail || 'Erreur lors de l\'initiation du paiement';
      console.error('Erreur paiement:', err);
    } finally {
      this.processing = false;
    }
  }

  checkTransactionStatus(): void {
    if (!this.transactionBillingId) return;

    this.apiService.getStatutTransaction(this.transactionBillingId).subscribe({
      next: (status) => {
        this.transactionStatus = status;
        
        // Si le paiement est en attente, vérifier à nouveau après 3 secondes
        if (status.statut === 'pending') {
          setTimeout(() => this.checkTransactionStatus(), 3000);
        }
      },
      error: (err) => {
        console.error('Erreur vérification statut:', err);
      }
    });
  }

  verifierAvecBambooPay(): void {
    if (!this.transactionBillingId) return;

    this.processing = true;
    this.apiService.verifierStatutBambooPay(this.transactionBillingId).subscribe({
      next: (result) => {
        this.processing = false;
        alert(`Statut local: ${result.statut_local}\nStatut BambooPay: ${result.statut_bamboopay || 'N/A'}\nMessage: ${result.message || 'N/A'}`);
        this.checkTransactionStatus();
      },
      error: (err) => {
        this.processing = false;
        this.error = err.error?.detail || 'Erreur lors de la vérification';
      }
    });
  }

  formatMontant(montant: number): string {
    return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'XAF' }).format(montant);
  }

  getStatutClass(statut: string): string {
    switch (statut) {
      case 'success':
        return 'text-green-600 bg-green-50';
      case 'failed':
        return 'text-red-600 bg-red-50';
      case 'pending':
        return 'text-yellow-600 bg-yellow-50';
      case 'cancelled':
        return 'text-gray-600 bg-gray-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  }

  getStatutText(statut: string): string {
    switch (statut) {
      case 'success':
        return 'Paiement réussi';
      case 'failed':
        return 'Paiement échoué';
      case 'pending':
        return 'En attente';
      case 'cancelled':
        return 'Annulé';
      default:
        return statut;
    }
  }
}

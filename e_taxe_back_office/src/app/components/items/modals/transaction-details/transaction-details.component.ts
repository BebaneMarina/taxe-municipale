import { Component, inject, Input, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import {ContenerGrayComponent} from '../../contener-gray/contener-gray.component';
import {hiddenLetters, dateFormater, parseMount} from '../../../../utils/utils';
import {Collecte} from '../../../../interfaces/collecte.interface';
import {CommonModule} from '@angular/common';
import {paiementLogo} from '../../../../utils/seeder';
import QRCode from 'qrcode';

@Component({
  selector: 'app-transaction-details',
  standalone : true,
  imports: [
    ContenerGrayComponent,
    CommonModule
  ],
  templateUrl: './transaction-details.component.html',
  styleUrl: './transaction-details.component.scss'
})
export class TransactionDetailsComponent implements OnChanges {
  @Input() collecte: Collecte | null = null;

  protected readonly hiddenLetters = hiddenLetters;
  protected readonly dateFormater = dateFormater;
  protected readonly parseMount = parseMount;
  protected readonly paiementLogo = paiementLogo;
  
  qrCodeDataUrl: string = '';
  isLoadingQR: boolean = false;

  getMoyenPaiementLabel(type: string): string {
    const labels: { [key: string]: string } = {
      'especes': 'Espèces',
      'mobile_money': 'Mobile Money',
      'carte': 'Carte bancaire'
    };
    return labels[type] || type;
  }

  getStatutLabel(statut: string): string {
    const labels: { [key: string]: string } = {
      'completed': 'Succès',
      'validee': 'Succès', // Support de l'ancienne valeur
      'pending': 'En cours',
      'cancelled': 'Annulé',
      'failed': 'Échec'
    };
    return labels[statut] || statut;
  }

  getStatutColor(statut: string): string {
    const colors: { [key: string]: string } = {
      'completed': 'text-green-700',
      'validee': 'text-green-700', // Support de l'ancienne valeur
      'pending': 'text-yellow-700',
      'cancelled': 'text-red-700',
      'failed': 'text-red-700'
    };
    return colors[statut] || 'text-gray-700';
  }

  formatDateTime(dateStr: string): string {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return `${dateFormater(dateStr, '/')} à ${date.toLocaleTimeString('fr-FR', {hour: '2-digit', minute: '2-digit'})}`;
  }

  navigator = navigator;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['collecte'] && this.collecte) {
      this.generateQRCode();
    }
  }

  async generateQRCode(): Promise<void> {
    if (!this.collecte) {
      return;
    }

    this.isLoadingQR = true;
    
    try {
      // Créer un objet JSON structuré avec toutes les informations importantes
      const qrData = {
        type: "COLLECTE_TAXE",
        version: "1.0",
        transaction: {
          reference: this.collecte.reference,
          id: this.collecte.id,
          statut: this.collecte.statut,
          valide: this.collecte.statut === 'completed' && !this.collecte.annule,
          date_collecte: this.collecte.date_collecte,
          date_cloture: this.collecte.date_cloture || null
        },
        paiement: {
          montant: parseFloat(this.collecte.montant.toString()),
          commission: parseFloat(this.collecte.commission.toString()),
          montant_net: parseFloat(this.collecte.montant.toString()) - parseFloat(this.collecte.commission.toString()),
          type_paiement: this.collecte.type_paiement,
          devise: "XAF"
        },
        contribuable: {
          nom: this.collecte.contribuable?.nom || '',
          prenom: this.collecte.contribuable?.prenom || '',
          telephone: this.collecte.contribuable?.telephone || '',
          email: this.collecte.contribuable?.email || null
        },
        taxe: {
          nom: this.collecte.taxe?.nom || '',
          code: this.collecte.taxe?.code || ''
        },
        collecteur: {
          nom: this.collecte.collecteur?.nom || '',
          prenom: this.collecte.collecteur?.prenom || '',
          matricule: this.collecte.collecteur?.matricule || ''
        },
        verification: {
          sms_envoye: this.collecte.sms_envoye,
          ticket_imprime: this.collecte.ticket_imprime,
          annule: this.collecte.annule,
          raison_annulation: this.collecte.raison_annulation || null
        },
        message: this.collecte.statut === 'completed' && !this.collecte.annule 
          ? "✅ Paiement validé - Transaction approuvée" 
          : "❌ Paiement non validé - Transaction en attente ou annulée"
      };

      // Convertir en JSON formaté et lisible
      const qrText = JSON.stringify(qrData, null, 2);

      // Générer le QR code avec des paramètres optimisés pour la scannabilité
      const dataUrl: string = await QRCode.toDataURL(qrText, {
        errorCorrectionLevel: 'H', // Niveau de correction d'erreur élevé (30%)
        margin: 4, // Marge plus grande pour une meilleure détection
        color: {
          dark: '#000000', // Noir pur pour un meilleur contraste
          light: '#FFFFFF' // Blanc pur
        },
        width: 400 // Taille plus grande pour une meilleure résolution
      });
      this.qrCodeDataUrl = dataUrl;
    } catch (error) {
      console.error('Erreur lors de la génération du QR code:', error);
      this.qrCodeDataUrl = '';
    } finally {
      this.isLoadingQR = false;
    }
  }

  isPaymentValid(): boolean {
    if (!this.collecte) return false;
    return this.collecte.statut === 'completed' && !this.collecte.annule;
  }

  async copyQRData(): Promise<void> {
    if (!this.collecte) return;

    try {
      const qrData = {
        type: "COLLECTE_TAXE",
        version: "1.0",
        transaction: {
          reference: this.collecte.reference,
          id: this.collecte.id,
          statut: this.collecte.statut,
          valide: this.collecte.statut === 'completed' && !this.collecte.annule,
          date_collecte: this.collecte.date_collecte,
          date_cloture: this.collecte.date_cloture || null
        },
        paiement: {
          montant: parseFloat(this.collecte.montant.toString()),
          commission: parseFloat(this.collecte.commission.toString()),
          montant_net: parseFloat(this.collecte.montant.toString()) - parseFloat(this.collecte.commission.toString()),
          type_paiement: this.collecte.type_paiement,
          devise: "XAF"
        },
        contribuable: {
          nom: this.collecte.contribuable?.nom || '',
          prenom: this.collecte.contribuable?.prenom || '',
          telephone: this.collecte.contribuable?.telephone || '',
          email: this.collecte.contribuable?.email || null
        },
        taxe: {
          nom: this.collecte.taxe?.nom || '',
          code: this.collecte.taxe?.code || ''
        },
        collecteur: {
          nom: this.collecte.collecteur?.nom || '',
          prenom: this.collecte.collecteur?.prenom || '',
          matricule: this.collecte.collecteur?.matricule || ''
        },
        verification: {
          sms_envoye: this.collecte.sms_envoye,
          ticket_imprime: this.collecte.ticket_imprime,
          annule: this.collecte.annule,
          raison_annulation: this.collecte.raison_annulation || null
        },
        message: this.collecte.statut === 'completed' && !this.collecte.annule 
          ? "✅ Paiement validé - Transaction approuvée" 
          : "❌ Paiement non validé - Transaction en attente ou annulée"
      };

      const qrText = JSON.stringify(qrData, null, 2);
      await navigator.clipboard.writeText(qrText);
      alert('Données copiées dans le presse-papiers !');
    } catch (error) {
      console.error('Erreur lors de la copie:', error);
      alert('Erreur lors de la copie des données');
    }
  }
}

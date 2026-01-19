import { Component, inject, Input, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import {ContenerGrayComponent} from '../../contener-gray/contener-gray.component';
import {hiddenLetters, dateFormater, parseMount} from '../../../../utils/utils';
import {Collecte} from '../../../../interfaces/collecte.interface';
import {CommonModule} from '@angular/common';
import {paiementLogo} from '../../../../utils/seeder';
import QRCode from 'qrcode';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

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

  async loadImageAsBase64(url: string): Promise<string> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.drawImage(img, 0, 0);
          resolve(canvas.toDataURL('image/png'));
        } else {
          reject(new Error('Impossible de créer le contexte canvas'));
        }
      };
      img.onerror = reject;
      img.src = url;
    });
  }

  async downloadReceiptPDF(): Promise<void> {
    if (!this.collecte) {
      alert('Aucune collecte sélectionnée');
      return;
    }

    try {
      const pdf = new jsPDF();
      
      // Couleurs personnalisées - Palette moderne
      const primaryColor: [number, number, number] = [59, 130, 246]; // Bleu (#3b82f6)
      const primaryDark: [number, number, number] = [37, 99, 235]; // Bleu foncé (#2563eb)
      const successColor: [number, number, number] = [16, 185, 129]; // Vert (#10b981)
      const textColor: [number, number, number] = [31, 41, 55]; // Gris foncé (#1f2937)
      const textGray: [number, number, number] = [107, 114, 128]; // Gris moyen (#6b7280)
      const lightGray: [number, number, number] = [243, 244, 246]; // Gris clair (#f3f4f6)
      const borderGray: [number, number, number] = [229, 231, 235]; // Bordure grise (#e5e7eb)
      const white: [number, number, number] = [255, 255, 255]; // Blanc
      
      // Page width and margins
      const pageWidth = pdf.internal.pageSize.getWidth();
      const margin = 15;
      let yPosition = 10;
      
      // En-tête avec fond coloré
      pdf.setFillColor(primaryColor[0], primaryColor[1], primaryColor[2]);
      pdf.roundedRect(margin, yPosition, pageWidth - 2 * margin, 50, 3, 3, 'F');
      
      // Charger et ajouter le logo dans l'en-tête
      let logoHeight = 35;
      let logoWidth = 35;
      try {
        const logoUrl = '/assets/logo/logo_app.png';
        const logoData = await this.loadImageAsBase64(logoUrl);
        pdf.addImage(logoData, 'PNG', margin + 10, yPosition + 7.5, logoWidth, logoHeight);
      } catch (error) {
        console.warn('Logo non chargé, continuation sans logo:', error);
      }
      
      // Titre et sous-titre dans l'en-tête
      pdf.setTextColor(white[0], white[1], white[2]);
      pdf.setFontSize(22);
      pdf.setFont('helvetica', 'bold');
      pdf.text('REÇU DE COLLECTE', margin + 50, yPosition + 20);
      
      pdf.setFontSize(11);
      pdf.setFont('helvetica', 'normal');
      pdf.text('Mairie de Libreville - Gabon', margin + 50, yPosition + 30);
      
      // Référence dans le coin supérieur droit
      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'bold');
      pdf.text(`Réf: ${this.collecte.reference || 'N/A'}`, pageWidth - margin - 5, yPosition + 18, { align: 'right' });
      
      yPosition += 60;
      
      // Ligne de séparation décorative
      pdf.setDrawColor(primaryColor[0], primaryColor[1], primaryColor[2]);
      pdf.setLineWidth(2);
      pdf.line(margin, yPosition, pageWidth - margin, yPosition);
      yPosition += 10;
      
      // Section : Informations de la transaction avec box
      pdf.setFillColor(lightGray[0], lightGray[1], lightGray[2]);
      pdf.roundedRect(margin, yPosition, pageWidth - 2 * margin, 15, 3, 3, 'F');
      
      pdf.setFontSize(13);
      pdf.setTextColor(primaryDark[0], primaryDark[1], primaryDark[2]);
      pdf.setFont('helvetica', 'bold');
      pdf.text('📋 Détails de la transaction', margin + 5, yPosition + 11);
      
      yPosition += 20;
      
      // Tableau des détails avec style amélioré
      const statutLabel = this.getStatutLabel(this.collecte.statut);
      const statutColor = this.collecte.statut === 'completed' ? successColor : textGray;
      
      const details = [
        ['Date de collecte', this.formatDateTime(this.collecte.date_collecte)],
        ['Statut', statutLabel],
        ['Collecteur', `${this.collecte.collecteur?.nom || ''} ${this.collecte.collecteur?.prenom || ''}`.trim() || 'N/A'],
        ['Matricule', this.collecte.collecteur?.matricule || 'N/A'],
      ];
      
      autoTable(pdf, {
        startY: yPosition,
        head: [],
        body: details,
        theme: 'striped',
        margin: { left: margin, right: margin },
        styles: {
          fontSize: 10,
          cellPadding: { top: 6, bottom: 6, left: 5, right: 5 },
          lineColor: borderGray,
          lineWidth: 0.1,
        },
        headStyles: {
          fillColor: primaryColor,
          textColor: white,
          fontStyle: 'bold',
        },
        columnStyles: {
          0: { 
            fontStyle: 'bold', 
            cellWidth: 70,
            textColor: textColor,
          },
          1: { 
            cellWidth: 'auto',
            textColor: textGray,
          },
        },
        alternateRowStyles: {
          fillColor: [249, 250, 251],
        },
        didDrawCell: (data: any) => {
          // Colorier le statut
          if (data.column.index === 1 && data.row.index === 1) {
            pdf.setTextColor(statutColor[0], statutColor[1], statutColor[2]);
            pdf.setFont('helvetica', 'bold');
          }
        },
      });
      
      yPosition = (pdf as any).lastAutoTable?.finalY || yPosition + 35;
      yPosition += 5;
      
      // Section : Informations du contribuable avec box
      pdf.setFillColor(lightGray[0], lightGray[1], lightGray[2]);
      pdf.roundedRect(margin, yPosition, pageWidth - 2 * margin, 15, 3, 3, 'F');
      
      pdf.setFontSize(13);
      pdf.setTextColor(primaryDark[0], primaryDark[1], primaryDark[2]);
      pdf.setFont('helvetica', 'bold');
      pdf.text('👤 Contribuable', margin + 5, yPosition + 11);
      
      yPosition += 20;
      
      const contribuableDetails = [
        ['Nom complet', `${this.collecte.contribuable?.nom || ''} ${this.collecte.contribuable?.prenom || ''}`.trim() || 'N/A'],
        ['Téléphone', this.collecte.contribuable?.telephone || 'N/A'],
        ['Email', this.collecte.contribuable?.email || 'N/A'],
      ];
      
      autoTable(pdf, {
        startY: yPosition,
        head: [],
        body: contribuableDetails,
        theme: 'striped',
        margin: { left: margin, right: margin },
        styles: {
          fontSize: 10,
          cellPadding: { top: 6, bottom: 6, left: 5, right: 5 },
          lineColor: borderGray,
          lineWidth: 0.1,
        },
        columnStyles: {
          0: { 
            fontStyle: 'bold', 
            cellWidth: 70,
            textColor: textColor,
          },
          1: { 
            cellWidth: 'auto',
            textColor: textGray,
          },
        },
        alternateRowStyles: {
          fillColor: [249, 250, 251],
        },
      });
      
      yPosition = (pdf as any).lastAutoTable?.finalY || yPosition + 30;
      yPosition += 5;
      
      // Section : Détails de la taxe avec box
      pdf.setFillColor(lightGray[0], lightGray[1], lightGray[2]);
      pdf.roundedRect(margin, yPosition, pageWidth - 2 * margin, 15, 3, 3, 'F');
      
      pdf.setFontSize(13);
      pdf.setTextColor(primaryDark[0], primaryDark[1], primaryDark[2]);
      pdf.setFont('helvetica', 'bold');
      pdf.text('📄 Détails de la taxe', margin + 5, yPosition + 11);
      
      yPosition += 20;
      
      const taxeDetails = [
        ['Nom', this.collecte.taxe?.nom || 'N/A'],
        ['Code', this.collecte.taxe?.code || 'N/A'],
        ['Description', this.collecte.taxe?.description || 'N/A'],
      ];
      
      autoTable(pdf, {
        startY: yPosition,
        head: [],
        body: taxeDetails,
        theme: 'striped',
        margin: { left: margin, right: margin },
        styles: {
          fontSize: 10,
          cellPadding: { top: 6, bottom: 6, left: 5, right: 5 },
          lineColor: borderGray,
          lineWidth: 0.1,
        },
        columnStyles: {
          0: { 
            fontStyle: 'bold', 
            cellWidth: 70,
            textColor: textColor,
          },
          1: { 
            cellWidth: 'auto',
            textColor: textGray,
          },
        },
        alternateRowStyles: {
          fillColor: [249, 250, 251],
        },
      });
      
      yPosition = (pdf as any).lastAutoTable?.finalY || yPosition + 30;
      yPosition += 5;
      
      // Section : Informations de paiement avec box
      pdf.setFillColor(lightGray[0], lightGray[1], lightGray[2]);
      pdf.roundedRect(margin, yPosition, pageWidth - 2 * margin, 15, 3, 3, 'F');
      
      pdf.setFontSize(13);
      pdf.setTextColor(primaryDark[0], primaryDark[1], primaryDark[2]);
      pdf.setFont('helvetica', 'bold');
      pdf.text('💳 Informations de paiement', margin + 5, yPosition + 11);
      
      yPosition += 20;
      
      const montantTotal = parseFloat(this.collecte.montant.toString());
      const commission = parseFloat(this.collecte.commission.toString());
      const montantNet = montantTotal - commission;
      
      const paiementDetails = [
        ['Moyen de paiement', this.getMoyenPaiementLabel(this.collecte.type_paiement)],
        ['Montant total', `${parseMount(montantTotal.toString(), ',')} XAF`],
        ['Commission', `${parseMount(commission.toString(), ',')} XAF`],
        ['Montant net', `${parseMount(montantNet.toString(), ',')} XAF`],
      ];
      
      autoTable(pdf, {
        startY: yPosition,
        head: [],
        body: paiementDetails,
        theme: 'striped',
        margin: { left: margin, right: margin },
        styles: {
          fontSize: 10,
          cellPadding: { top: 6, bottom: 6, left: 5, right: 5 },
          lineColor: borderGray,
          lineWidth: 0.1,
        },
        columnStyles: {
          0: { 
            fontStyle: 'bold', 
            cellWidth: 70,
            textColor: textColor,
          },
          1: { 
            cellWidth: 'auto', 
            halign: 'right',
            textColor: textGray,
          },
        },
        alternateRowStyles: {
          fillColor: [249, 250, 251],
        },
      });
      
      yPosition = (pdf as any).lastAutoTable?.finalY || yPosition + 35;
      yPosition += 10;
      
      // Box élégante pour le montant total avec bordure
      pdf.setFillColor(primaryColor[0], primaryColor[1], primaryColor[2]);
      pdf.setDrawColor(primaryDark[0], primaryDark[1], primaryDark[2]);
      pdf.setLineWidth(0.5);
      pdf.roundedRect(margin, yPosition, pageWidth - 2 * margin, 20, 3, 3, 'FD');
      
      pdf.setFontSize(14);
      pdf.setTextColor(white[0], white[1], white[2]);
      pdf.setFont('helvetica', 'bold');
      pdf.text('TOTAL PAYÉ', margin + 10, yPosition + 12);
      
      pdf.setFontSize(18);
      pdf.text(`${parseMount(montantTotal.toString(), ',')} XAF`, pageWidth - margin - 10, yPosition + 12, { align: 'right' });
      
      yPosition += 30;
      
      // QR Code si disponible avec box
      if (this.qrCodeDataUrl) {
        try {
          const qrSize = 45;
          const qrX = pageWidth - margin - qrSize - 5; // Aligné à droite
          const qrY = yPosition;
          
          // Box autour du QR Code
          pdf.setFillColor(white[0], white[1], white[2]);
          pdf.setDrawColor(borderGray[0], borderGray[1], borderGray[2]);
          pdf.setLineWidth(0.5);
          pdf.roundedRect(qrX - 5, qrY, qrSize + 10, qrSize + 20, 3, 3, 'FD');
          
          const qrCodeImg = this.qrCodeDataUrl;
          pdf.addImage(qrCodeImg, 'PNG', qrX, qrY + 3, qrSize, qrSize);
          
          pdf.setFontSize(8);
          pdf.setTextColor(textGray[0], textGray[1], textGray[2]);
          pdf.setFont('helvetica', 'normal');
          pdf.text('Code QR', qrX + qrSize / 2, qrY + qrSize + 10, { align: 'center' });
          pdf.text('de validation', qrX + qrSize / 2, qrY + qrSize + 16, { align: 'center' });
        } catch (error) {
          console.warn('QR Code non ajouté au PDF:', error);
        }
      }
      
      // Ligne de séparation avant le pied de page
      const pageHeight = pdf.internal.pageSize.getHeight();
      pdf.setDrawColor(borderGray[0], borderGray[1], borderGray[2]);
      pdf.setLineWidth(0.5);
      pdf.line(margin, pageHeight - 25, pageWidth - margin, pageHeight - 25);
      
      // Pied de page amélioré
      pdf.setFontSize(8);
      pdf.setTextColor(textGray[0], textGray[1], textGray[2]);
      pdf.setFont('helvetica', 'italic');
      pdf.text(
        `Document généré le ${new Date().toLocaleDateString('fr-FR')} à ${new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}`,
        pageWidth / 2,
        pageHeight - 15,
        { align: 'center' }
      );
      
      pdf.setFontSize(7);
      pdf.text(
        'Ce document est généré électroniquement et est valable sans signature',
        pageWidth / 2,
        pageHeight - 10,
        { align: 'center' }
      );
      
      // Nom du fichier
      const fileName = `recu_collecte_${this.collecte.reference}_${new Date().toISOString().split('T')[0]}.pdf`;
      
      // Sauvegarder le PDF
      pdf.save(fileName);
      
    } catch (error) {
      console.error('Erreur lors de la génération du PDF:', error);
      alert('Erreur lors de la génération du reçu PDF. Veuillez réessayer.');
    }
  }

  printReceipt(): void {
    // Cette fonction peut ouvrir une fenêtre d'impression
    window.print();
  }
}

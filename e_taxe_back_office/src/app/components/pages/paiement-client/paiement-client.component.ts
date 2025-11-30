import { Component, OnInit, OnDestroy, inject } from '@angular/core';
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

interface FeaturedTax {
  categorie: string;
  description: string;
  periodicite: string;
  service_ref: string;
  mode_paiement: string;
  justificatifs: string;
  montant_base: string;
  tag?: string;
}

@Component({
  selector: 'app-paiement-client',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './paiement-client.component.html',
  styleUrl: './paiement-client.component.scss'
})
export class PaiementClientComponent implements OnInit, OnDestroy {
  private apiService = inject(ApiService);
  private router = inject(Router);

  taxes: Taxe[] = [];
  loading: boolean = true;
  error: string = '';
  featuredTaxes: FeaturedTax[] = [
    {
      categorie: 'Taxe Professionnelle Unique (TPU)',
      description: 'Due par toute activité commerciale, artisanale ou libérale exercée sur le territoire communal.',
      periodicite: 'Annuelle (déclaration au plus tard le 31 mars)',
      service_ref: 'Direction des affaires économiques',
      mode_paiement: 'Portail e-Taxe ou guichet municipal',
      justificatifs: 'RCCM, NIF, copie pièce d’identité, formulaire TPU',
      montant_base: 'Barème progressif par tranche de chiffre d’affaires (à partir de 50 000 FCFA)',
      tag: 'Prioritaire'
    },
    {
      categorie: 'Occupation Temporaire du Domaine Public (OTDP)',
      description: 'Autorisation de terrasse, kiosque, étalage, stationnement ou chantier sur domaine public.',
      periodicite: 'Hebdomadaire ou mensuelle selon l’autorisation',
      service_ref: 'Direction de l’urbanisme & du domaine',
      mode_paiement: 'Paiement immédiat avant délivrance du permis d’occupation',
      justificatifs: 'Demande écrite, plan de situation, agrément commercial',
      montant_base: 'Entre 2 000 et 15 000 FCFA / jour selon la zone',
      tag: 'Espaces publics'
    },
    {
      categorie: 'Droit de place – Marchés municipaux',
      description: 'Redevence pour l’occupation d’un emplacement dans les marchés et foires.',
      periodicite: 'Quotidienne ou mensuelle',
      service_ref: 'Gestion des marchés',
      mode_paiement: 'Collecte mobile ou guichet en début de période',
      justificatifs: 'Carte de commerçant, photo, quittance précédente',
      montant_base: '1 000 à 5 000 FCFA / jour en fonction du marché'
    },
    {
      categorie: 'Taxe d’Enseigne & Publicité',
      description: 'Autorisation pour panneaux, banderoles, totems ou dispositifs lumineux.',
      periodicite: 'Annuelle (renouvelable)',
      service_ref: 'Direction de la communication municipale',
      mode_paiement: 'Portail e-Taxe ou virement sur régie',
      justificatifs: 'Plan de l’enseigne, photo, autorisation d’implantation',
      montant_base: '10 000 à 150 000 FCFA selon la surface'
    },
    {
      categorie: 'Taxe d’Enlèvement des Ordures Ménagères (TEOM)',
      description: 'Participation aux services de propreté pour ménages et entreprises.',
      periodicite: 'Mensuelle ou incluse sur la facture d’eau/électricité',
      service_ref: 'Service hygiène & salubrité',
      mode_paiement: 'Prélèvement via factures SEEG / paiement régie',
      justificatifs: 'Numéro compteur ou attestation de domicile',
      montant_base: '3 000 à 12 000 FCFA selon la superficie'
    }
  ];

  // Filtres tableau
  taxSearch = '';
  periodiciteFilter = '';
  serviceFilter = '';
  filteredFeaturedTaxes: FeaturedTax[] = [...this.featuredTaxes];

  // FAQ
  faqItems = [
    {
      question: 'Qui doit s’acquitter de la Taxe Professionnelle Unique (TPU) ?',
      answer: 'Toute personne physique ou morale exerçant une activité commerciale, artisanale ou libérale sur le territoire communal, y compris les établissements secondaires.'
    },
    {
      question: 'Comment obtenir une autorisation d’occupation temporaire ?',
      answer: 'Déposez une demande écrite à la Direction de l’urbanisme avec le plan de situation et les justificatifs commerciaux. Le paiement doit être effectué avant la délivrance de l’autorisation.'
    },
    {
      question: 'Quels moyens de paiement sont acceptés sur le portail ?',
      answer: 'Vous pouvez payer par carte bancaire via BambooPay (paiement web) ou via Mobile Money (Moov Money / Airtel Money) en paiement instantané.'
    },
    {
      question: 'Comment recevoir une quittance officielle ?',
      answer: 'Après validation du paiement, la quittance est envoyée par email et reste accessible dans l’espace contribuable.'
    }
  ];

  activeSection: string = 'accueil';
  private scrollHandler?: () => void;

  ngOnInit(): void {
    this.loadTaxes();
    this.applyTaxFilters();
    this.setupScrollListener();
  }

  ngOnDestroy(): void {
    if (this.scrollHandler) {
      window.removeEventListener('scroll', this.scrollHandler);
    }
  }

  scrollToSection(sectionId: string, event: Event): void {
    event.preventDefault();
    const element = document.getElementById(sectionId);
    if (element) {
      const headerOffset = 120;
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
      this.activeSection = sectionId;
    }
  }

  setupScrollListener(): void {
    this.scrollHandler = () => {
      const sections = ['accueil', 'taxes', 'services', 'process', 'faq', 'contact'];
      const scrollPosition = window.scrollY + 150;

      for (let i = sections.length - 1; i >= 0; i--) {
        const section = document.getElementById(sections[i]);
        if (section) {
          const sectionTop = section.offsetTop;
          const sectionHeight = section.offsetHeight;
          if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            this.activeSection = sections[i];
            break;
          }
        }
      }
    };
    window.addEventListener('scroll', this.scrollHandler);
  }

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

  applyTaxFilters(): void {
    const term = this.taxSearch.toLowerCase().trim();
    this.filteredFeaturedTaxes = this.featuredTaxes.filter((tax) => {
      const matchesSearch =
        !term ||
        tax.categorie.toLowerCase().includes(term) ||
        tax.description.toLowerCase().includes(term) ||
        tax.service_ref.toLowerCase().includes(term);
      const matchesPeriod =
        !this.periodiciteFilter ||
        tax.periodicite.toLowerCase().includes(this.periodiciteFilter.toLowerCase());
      const matchesService =
        !this.serviceFilter ||
        tax.service_ref.toLowerCase().includes(this.serviceFilter.toLowerCase());
      return matchesSearch && matchesPeriod && matchesService;
    });
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

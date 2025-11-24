import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../services/api.service';

@Component({
  selector: 'app-relances',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './relances.component.html',
  styleUrl: './relances.component.scss'
})
export class RelancesComponent implements OnInit {
  private apiService = inject(ApiService);

  relances: any[] = [];
  loading = false;
  error = '';
  
  // Filtres
  filters = {
    type_relance: '',
    statut: '',
    contribuable_id: null as number | null,
    date_debut: '',
    date_fin: ''
  };

  // Pagination
  currentPage = 0;
  pageSize = 20;
  total = 0;

  // Statistiques
  stats: any = null;

  // Modal de création
  showCreateModal = false;
  contribuables: any[] = [];
  searchContribuableTerm = '';
  selectedContribuable: any = null;
  affectationsTaxes: any[] = [];
  selectedAffectationTaxe: any = null;
  
  // Formulaire de création
  newRelance = {
    contribuable_id: null as number | null,
    affectation_taxe_id: null as number | null,
    type_relance: 'sms',
    message: '',
    montant_due: 0,
    date_echeance: '',
    date_planifiee: this.getLocalDateTimeString(),
    canal_envoi: '',
    notes: ''
  };

  ngOnInit(): void {
    this.loadRelances();
    this.loadStats();
  }

  loadRelances(): void {
    this.loading = true;
    this.error = '';

    const params: any = {
      skip: this.currentPage * this.pageSize,
      limit: this.pageSize
    };

    if (this.filters.type_relance) params.type_relance = this.filters.type_relance;
    if (this.filters.statut) params.statut = this.filters.statut;
    if (this.filters.contribuable_id) params.contribuable_id = this.filters.contribuable_id;
    if (this.filters.date_debut) params.date_debut = this.filters.date_debut;
    if (this.filters.date_fin) params.date_fin = this.filters.date_fin;

    this.apiService.getRelances(params).subscribe({
      next: (response) => {
        if (response.items) {
          this.relances = response.items;
          this.total = response.total;
        } else {
          this.relances = response;
          this.total = response.length;
        }
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Erreur lors du chargement des relances';
        this.loading = false;
      }
    });
  }

  loadStats(): void {
    const params: any = {};
    if (this.filters.date_debut) params.date_debut = this.filters.date_debut;
    if (this.filters.date_fin) params.date_fin = this.filters.date_fin;

    this.apiService.getStatistiquesRelances(params).subscribe({
      next: (data) => {
        this.stats = data;
      },
      error: (err) => {
        console.error('Erreur chargement stats:', err);
      }
    });
  }

  applyFilters(): void {
    this.currentPage = 0;
    this.loadRelances();
    this.loadStats();
  }

  resetFilters(): void {
    this.filters = {
      type_relance: '',
      statut: '',
      contribuable_id: null,
      date_debut: '',
      date_fin: ''
    };
    this.applyFilters();
  }

  genererRelancesAutomatiques(): void {
    if (!confirm('Voulez-vous générer des relances automatiques pour les contribuables en retard ?')) {
      return;
    }
    
    const envoyerAuto = confirm('Voulez-vous ENVOYER automatiquement les SMS maintenant ?\n\nOK = Générer et envoyer les SMS\nAnnuler = Générer seulement (envoi manuel plus tard)');

    this.loading = true;
    this.apiService.genererRelancesAutomatiques({
      jours_retard_min: 7,
      type_relance: 'sms',
      limite: 50,
      envoyer_automatiquement: envoyerAuto
    }).subscribe({
      next: (relances) => {
        const envoyees = relances.filter((r: any) => r.statut === 'envoyee').length;
        const echecs = relances.filter((r: any) => r.statut === 'echec').length;
        
        let message = `${relances.length} relance(s) générée(s)`;
        if (envoyerAuto) {
          message += `\n${envoyees} SMS envoyé(s) avec succès`;
          if (echecs > 0) {
            message += `\n${echecs} échec(s) d'envoi`;
          }
        }
        
        alert(message);
        this.loadRelances();
        this.loadStats();
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Erreur lors de la génération des relances';
        this.loading = false;
      }
    });
  }

  envoyerRelance(id: number): void {
    if (!confirm('Marquer cette relance comme envoyée ?')) {
      return;
    }

    this.apiService.envoyerRelance(id).subscribe({
      next: () => {
        this.loadRelances();
        this.loadStats();
      },
      error: (err) => {
        this.error = err.error?.detail || 'Erreur lors de l\'envoi';
      }
    });
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadRelances();
  }

  getTotalPages(): number {
    return Math.ceil(this.total / this.pageSize);
  }

  getStatutClass(statut: string): string {
    const classes: { [key: string]: string } = {
      'en_attente': 'bg-yellow-100 text-yellow-800',
      'envoyee': 'bg-green-100 text-green-800',
      'echec': 'bg-red-100 text-red-800',
      'annulee': 'bg-gray-100 text-gray-800'
    };
    return classes[statut] || 'bg-gray-100 text-gray-800';
  }

  getTypeRelanceLabel(type: string): string {
    const labels: { [key: string]: string } = {
      'sms': 'SMS',
      'email': 'Email',
      'appel': 'Appel téléphonique',
      'courrier': 'Courrier',
      'visite': 'Visite'
    };
    return labels[type] || type;
  }

  openCreateModal(): void {
    this.showCreateModal = true;
    this.selectedContribuable = null;
    this.selectedAffectationTaxe = null;
    this.searchContribuableTerm = '';
    this.newRelance = {
      contribuable_id: null,
      affectation_taxe_id: null,
      type_relance: 'sms',
      message: '',
      montant_due: 0,
      date_echeance: '',
      date_planifiee: this.getLocalDateTimeString(),
      canal_envoi: '',
      notes: ''
    };
  }

  closeCreateModal(): void {
    this.showCreateModal = false;
  }

  searchContribuables(): void {
    if (!this.searchContribuableTerm || this.searchContribuableTerm.length < 2) {
      this.contribuables = [];
      return;
    }

    this.apiService.getContribuables({
      search: this.searchContribuableTerm,
      limit: 20,
      actif: true
    }).subscribe({
      next: (data) => {
        this.contribuables = Array.isArray(data) ? data : (data.items || []);
      },
      error: (err) => {
        console.error('Erreur recherche contribuables:', err);
        this.contribuables = [];
      }
    });
  }

  selectContribuable(contribuable: any): void {
    this.selectedContribuable = contribuable;
    this.newRelance.contribuable_id = contribuable.id;
    this.searchContribuableTerm = `${contribuable.nom} ${contribuable.prenom || ''}`.trim();
    this.contribuables = [];
    
    // Charger les affectations de taxes du contribuable
    this.loadAffectationsTaxes(contribuable.id);
    
    // Définir le canal d'envoi selon le type
    if (this.newRelance.type_relance === 'sms') {
      this.newRelance.canal_envoi = contribuable.telephone || '';
    } else if (this.newRelance.type_relance === 'email') {
      this.newRelance.canal_envoi = contribuable.email || '';
    }
  }

  loadAffectationsTaxes(contribuableId: number): void {
    // Récupérer les affectations actives du contribuable via l'API des contribuables
    // Note: Les affectations peuvent ne pas être incluses par défaut, on les récupère séparément si nécessaire
    this.apiService.getContribuable(contribuableId).subscribe({
      next: (contribuable) => {
        // Si les affectations sont déjà dans la réponse
        if (contribuable.affectations_taxes) {
          this.affectationsTaxes = contribuable.affectations_taxes.filter((at: any) => at.actif);
        } else {
          // Sinon, on peut récupérer les taxes du contribuable via les affectations
          // Pour l'instant, on laisse vide et l'utilisateur peut saisir manuellement le montant
          this.affectationsTaxes = [];
        }
      },
      error: (err) => {
        console.error('Erreur chargement affectations:', err);
        this.affectationsTaxes = [];
      }
    });
  }

  selectAffectationTaxe(): void {
    if (this.selectedAffectationTaxe) {
      this.newRelance.affectation_taxe_id = this.selectedAffectationTaxe.id;
      this.newRelance.montant_due = this.selectedAffectationTaxe.montant_custom || this.selectedAffectationTaxe.taxe?.montant || 0;
      
      // Générer un message par défaut
      if (!this.newRelance.message) {
        const taxeNom = this.selectedAffectationTaxe.taxe?.nom || 'taxe';
        const montant = this.newRelance.montant_due;
        this.newRelance.message = `Rappel : Vous avez une ${taxeNom} de ${montant} FCFA à payer.`;
      }
    } else {
      this.newRelance.affectation_taxe_id = null;
    }
  }

  onTypeRelanceChange(): void {
    if (this.selectedContribuable) {
      if (this.newRelance.type_relance === 'sms') {
        this.newRelance.canal_envoi = this.selectedContribuable.telephone || '';
      } else if (this.newRelance.type_relance === 'email') {
        this.newRelance.canal_envoi = this.selectedContribuable.email || '';
      } else {
        this.newRelance.canal_envoi = '';
      }
    }
  }

  createRelance(): void {
    // Validation
    if (!this.newRelance.contribuable_id) {
      this.error = 'Veuillez sélectionner un contribuable';
      return;
    }

    if (!this.newRelance.type_relance) {
      this.error = 'Veuillez sélectionner un type de relance';
      return;
    }

    if (!this.newRelance.montant_due || this.newRelance.montant_due <= 0) {
      this.error = 'Le montant dû doit être supérieur à 0';
      return;
    }

    if (!this.newRelance.date_planifiee) {
      this.error = 'Veuillez sélectionner une date planifiée';
      return;
    }

    this.loading = true;
    this.error = '';

    const relanceData = {
      contribuable_id: this.newRelance.contribuable_id,
      affectation_taxe_id: this.newRelance.affectation_taxe_id || null,
      type_relance: this.newRelance.type_relance,
      message: this.newRelance.message || undefined,
      montant_due: this.newRelance.montant_due,
      date_echeance: this.newRelance.date_echeance
        ? new Date(this.newRelance.date_echeance).toISOString()
        : undefined,
      date_planifiee: this.newRelance.date_planifiee
        ? new Date(this.newRelance.date_planifiee).toISOString()
        : new Date().toISOString(),
      canal_envoi: this.newRelance.canal_envoi || undefined,
      notes: this.newRelance.notes || undefined
    };

    this.apiService.createRelance(relanceData).subscribe({
      next: () => {
        this.loading = false;
        this.closeCreateModal();
        this.loadRelances();
        this.loadStats();
        alert('Relance créée avec succès !');
      },
      error: (err) => {
        this.error = err.error?.detail || 'Erreur lors de la création de la relance';
        this.loading = false;
      }
    });
  }

  private getLocalDateTimeString(date: Date = new Date()): string {
    const tzOffset = date.getTimezoneOffset() * 60000;
    return new Date(date.getTime() - tzOffset).toISOString().slice(0, 16);
  }
}


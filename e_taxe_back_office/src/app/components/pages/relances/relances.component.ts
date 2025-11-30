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

  // Formulaire multi-contribuables
  newRelance = {
    type_relance: 'sms',
    message: '',
    montant_due: 0,
    date_echeance: '',
    date_planifiee: this.getLocalDateTimeString(),
    notes: '',
    contribuables: [] as Array<{
      contribuable?: any;
      contribuable_id: number | null;
      telephone_override?: string;
      montant_due?: number | null;
      date_echeance?: string;
      message?: string;
      notes?: string;
    }>
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
    this.searchContribuableTerm = '';
    this.newRelance = {
      type_relance: 'sms',
      message: '',
      montant_due: 0,
      date_echeance: '',
      date_planifiee: this.getLocalDateTimeString(),
      notes: '',
      contribuables: [
        {
          contribuable_id: null,
          telephone_override: '',
          montant_due: null,
          date_echeance: '',
          message: '',
          notes: ''
        }
      ]
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

  addDestinataire(): void {
    this.newRelance.contribuables.push({
      contribuable_id: null,
      telephone_override: '',
      montant_due: null,
      date_echeance: '',
      message: '',
      notes: ''
    });
  }

  removeDestinataire(index: number): void {
    if (this.newRelance.contribuables.length > 1) {
      this.newRelance.contribuables.splice(index, 1);
    }
  }

  searchContribuablesFor(index: number): void {
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
      error: () => {
        this.contribuables = [];
      }
    });
  }

  selectContribuableFor(index: number, contribuable: any): void {
    const destinataire = this.newRelance.contribuables[index];
    destinataire.contribuable = contribuable;
    destinataire.contribuable_id = contribuable.id;
    destinataire.telephone_override = contribuable.telephone || '';
    destinataire.montant_due = destinataire.montant_due ?? this.newRelance.montant_due ?? 0;

    if (!destinataire.message && this.newRelance.message) {
      destinataire.message = this.newRelance.message;
    }

    this.searchContribuableTerm = `${contribuable.nom} ${contribuable.prenom || ''}`.trim();
    this.contribuables = [];
  }

  createRelancesManuelles(): void {
    if (!this.newRelance.type_relance) {
      this.error = 'Veuillez sélectionner un type de relance';
      return;
    }

    if (!this.newRelance.date_planifiee) {
      this.error = 'Veuillez sélectionner une date planifiée';
      return;
    }

    if (!this.newRelance.contribuables.length) {
      this.error = 'Ajoutez au moins un destinataire';
      return;
    }

    const payload = {
      type_relance: this.newRelance.type_relance,
      message: this.newRelance.message || undefined,
      montant_due: this.newRelance.montant_due || undefined,
      date_echeance: this.newRelance.date_echeance ? new Date(this.newRelance.date_echeance).toISOString() : undefined,
      date_planifiee: new Date(this.newRelance.date_planifiee).toISOString(),
      notes: this.newRelance.notes || undefined,
      contribuables: this.newRelance.contribuables.map((dest) => {
        if (!dest.contribuable_id) {
          throw new Error('Un destinataire n’a pas de contribuable sélectionné');
        }
        return {
          contribuable_id: dest.contribuable_id,
          telephone_override: dest.telephone_override || undefined,
          montant_due: dest.montant_due || this.newRelance.montant_due,
          date_echeance: dest.date_echeance ? new Date(dest.date_echeance).toISOString() : undefined,
          message: dest.message || this.newRelance.message,
          notes: dest.notes || undefined,
        };
      }),
    };

    this.loading = true;
    this.error = '';

    this.apiService.createRelancesManuelles(payload).subscribe({
      next: () => {
        this.loading = false;
        this.closeCreateModal();
        this.loadRelances();
        this.loadStats();
        alert('Relances créées avec succès !');
      },
      error: (err) => {
        this.error = err.error?.detail || 'Erreur lors de la création des relances';
        this.loading = false;
      },
    });
  }

  hasSelectedContribuables(): boolean {
    return this.newRelance.contribuables.some((dest) => !!dest.contribuable);
  }

  private getLocalDateTimeString(date: Date = new Date()): string {
    const tzOffset = date.getTimezoneOffset() * 60000;
    return new Date(date.getTime() - tzOffset).toISOString().slice(0, 16);
  }
}


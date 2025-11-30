import {Component, model, ModelSignal, OnInit, inject} from '@angular/core';
import {BadgeComponent} from '../../badge/badge.component';
import {PaginationComponent} from '../../pagination/pagination.component';
import {dateFormater, hiddenLetters, parseMount} from '../../../../utils/utils';
import {dates, paiementLogo, statusBilling} from '../../../../utils/seeder';
import {ApiService} from '../../../../services/api.service';
import {CommonModule} from '@angular/common';
import {Collecte} from '../../../../interfaces/collecte.interface';

@Component({
  selector: 'app-transactions-table',
  imports: [
    BadgeComponent,
    CommonModule,
    PaginationComponent
  ],
  standalone : true,
  templateUrl: './transactions-table.component.html',
  styleUrl: './transactions-table.component.scss'
})
export class TransactionsTableComponent implements OnInit {
  activeModalItem : ModelSignal<boolean> = model<boolean>(false);
  private apiService = inject(ApiService);
  
  collectes: Collecte[] = [];
  loading: boolean = true;
  selectedCollecte: Collecte | null = null;
  
  // Pagination
  currentPage: number = 1;
  pageSize: number = 10;
  totalItems: number = 0;
  totalPages: number = 1;

  // Filtres
  filters: any = {
    telephone: '',
    dateDebut: '',
    dateFin: '',
    statut: '',
    collecteur_id: undefined,
    contribuable_id: undefined,
    taxe_id: undefined
  };

  protected readonly hiddenLetters = hiddenLetters;
  protected readonly dateFormater = dateFormater;
  protected readonly dates = dates;
  protected readonly Math = Math;
  protected readonly parseMount = parseMount;
  protected readonly paiementLogo = paiementLogo;
  protected readonly statusBilling = statusBilling;

  ngOnInit(): void {
    this.loadCollectes();
  }

  loadCollectes(): void {
    this.loading = true;
    const params: any = {
      skip: (this.currentPage - 1) * this.pageSize,
      limit: this.pageSize
    };

    // Ajouter les filtres
    if (this.filters.statut) {
      params.statut = this.filters.statut;
    }
    if (this.filters.dateDebut) {
      params.date_debut = this.filters.dateDebut;
    }
    if (this.filters.dateFin) {
      params.date_fin = this.filters.dateFin;
    }
    if (this.filters.telephone) {
      params.telephone = this.filters.telephone;
    }
    if (this.filters.collecteur_id) {
      params.collecteur_id = this.filters.collecteur_id;
    }
    if (this.filters.contribuable_id) {
      params.contribuable_id = this.filters.contribuable_id;
    }
    if (this.filters.taxe_id) {
      params.taxe_id = this.filters.taxe_id;
    }

    this.apiService.getCollectes(params).subscribe({
      next: (data: Collecte[]) => {
        this.collectes = data;
        this.totalItems = data.length === this.pageSize ? (this.currentPage * this.pageSize) + 1 : (this.currentPage - 1) * this.pageSize + data.length;
        this.totalPages = Math.ceil(this.totalItems / this.pageSize);
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des collectes:', err);
        this.loading = false;
      }
    });
  }

  applyFilters(filters: any): void {
    this.filters = { ...filters };
    this.currentPage = 1; // Réinitialiser à la première page
    this.loadCollectes();
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadCollectes();
  }

  onPageSizeChange(size: number): void {
    this.pageSize = size;
    this.currentPage = 1;
    this.loadCollectes();
  }

  onActiveModalItem(active : boolean, collecte?: Collecte) {
    if (collecte) {
      this.selectedCollecte = collecte;
    }
    this.activeModalItem.set(active);
  }
  
  getSelectedCollecte(): Collecte | null {
    return this.selectedCollecte;
  }

  getStatusBadgeClass(statut: string): string {
    switch(statut) {
      case 'completed':
      case 'validee': // Support de l'ancienne valeur
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }

  getTimeFromDate(dateStr: string): string {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleTimeString('fr-FR', {hour: '2-digit', minute: '2-digit'});
  }

  getCollecteLocation(collecte: Collecte): {
    latitude: number;
    longitude: number;
    accuracy?: number;
    source: 'collecte' | 'contribuable';
  } | null {
    const collecteLocation = collecte.location;
    if (
      collecteLocation &&
      this.isValidCoordinate(collecteLocation.latitude) &&
      this.isValidCoordinate(collecteLocation.longitude)
    ) {
      return {
        latitude: collecteLocation.latitude,
        longitude: collecteLocation.longitude,
        accuracy: collecteLocation.accuracy,
        source: 'collecte'
      };
    }

    const contribLat = collecte.contribuable?.latitude;
    const contribLng = collecte.contribuable?.longitude;
    if (this.isValidCoordinate(contribLat) && this.isValidCoordinate(contribLng)) {
      return {
        latitude: contribLat!,
        longitude: contribLng!,
        source: 'contribuable'
      };
    }

    return null;
  }

  private isValidCoordinate(value?: number): boolean {
    return value !== null && value !== undefined && !Number.isNaN(value);
  }
}

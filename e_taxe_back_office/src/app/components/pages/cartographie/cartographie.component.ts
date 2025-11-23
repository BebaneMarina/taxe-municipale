import { Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MapInteractiveComponent } from '../../items/map-interactive/map-interactive.component';
import { ContenerComponent } from '../../items/contener/contener.component';
import { H1Component } from '../../items/texts/h1/h1.component';
import { ApiService } from '../../../services/api.service';

@Component({
  selector: 'app-cartographie',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MapInteractiveComponent,
    ContenerComponent,
    H1Component
  ],
  templateUrl: './cartographie.component.html',
  styleUrl: './cartographie.component.scss'
})
export class CartographieComponent {
  @ViewChild(MapInteractiveComponent) mapComponent!: MapInteractiveComponent;
  
  // Filtres de recherche
  searchTerm: string = '';
  filterPaye: string = 'all'; // 'all', 'paye', 'non-paye'
  filterQuartier: string = '';
  filterCollecteur: string = '';
  
  // Résultats filtrés
  filteredContribuables: any[] = [];
  allContribuables: any[] = [];
  
  // Options pour les filtres
  quartiers: any[] = [];
  collecteurs: any[] = [];
  
  // Pagination
  currentPage: number = 1;
  itemsPerPage: number = 10;
  
  showFilters: boolean = true;
  showResults: boolean = true;
  
  // Debounce pour la recherche
  private searchTimeout: any = null;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadFilterOptions();
  }

  loadFilterOptions(): void {
    // Charger les quartiers
    this.apiService.getQuartiers(undefined, true).subscribe({
      next: (data: any[]) => {
        this.quartiers = data;
      },
      error: (err: any) => {
        console.error('Erreur chargement quartiers:', err);
      }
    });

    // Charger les collecteurs
    this.apiService.getCollecteurs({ actif: true }).subscribe({
      next: (data: any) => {
        this.collecteurs = Array.isArray(data) ? data : (data.items || []);
      },
      error: (err: any) => {
        console.error('Erreur chargement collecteurs:', err);
      }
    });
  }

  onContribuablesLoaded(contribuables: any[]): void {
    this.allContribuables = contribuables;
    this.applyFilters();
  }

  applyFilters(): void {
    // Debounce pour éviter trop de mises à jour
    if (this.searchTimeout) {
      clearTimeout(this.searchTimeout);
    }
    
    this.searchTimeout = setTimeout(() => {
      this._applyFilters();
    }, 300);
  }

  private _applyFilters(): void {
    let filtered = [...this.allContribuables];

    // Filtre par recherche textuelle
    if (this.searchTerm && this.searchTerm.trim()) {
      const search = this.searchTerm.toLowerCase().trim();
      filtered = filtered.filter(c => 
        c.nom?.toLowerCase().includes(search) ||
        c.prenom?.toLowerCase().includes(search) ||
        c.telephone?.includes(search) ||
        c.nom_activite?.toLowerCase().includes(search) ||
        c.adresse?.toLowerCase().includes(search)
      );
    }

    // Filtre par statut de paiement
    if (this.filterPaye === 'paye') {
      filtered = filtered.filter(c => c.a_paye === true);
    } else if (this.filterPaye === 'non-paye') {
      filtered = filtered.filter(c => c.a_paye === false);
    }

    // Filtre par quartier
    if (this.filterQuartier) {
      filtered = filtered.filter(c => 
        c.quartier === this.filterQuartier || 
        c.quartier_id?.toString() === this.filterQuartier
      );
    }

    // Filtre par collecteur
    if (this.filterCollecteur) {
      filtered = filtered.filter(c => 
        c.collecteur?.includes(this.filterCollecteur) ||
        c.collecteur_id?.toString() === this.filterCollecteur
      );
    }

    this.filteredContribuables = filtered;
    this.currentPage = 1;

    // Mettre à jour la carte avec les résultats filtrés de manière stable
    if (this.mapComponent) {
      // Utiliser requestAnimationFrame pour une mise à jour fluide
      requestAnimationFrame(() => {
        this.mapComponent.setFilteredContribuables(filtered);
      });
    }
  }

  clearFilters(): void {
    this.searchTerm = '';
    this.filterPaye = 'all';
    this.filterQuartier = '';
    this.filterCollecteur = '';
    this.applyFilters();
  }

  get totalPages(): number {
    return Math.ceil(this.filteredContribuables.length / this.itemsPerPage);
  }

  get paginatedContribuables(): any[] {
    const start = (this.currentPage - 1) * this.itemsPerPage;
    const end = start + this.itemsPerPage;
    return this.filteredContribuables.slice(start, end);
  }

  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
    }
  }

  zoomToContribuable(contribuable: any): void {
    if (this.mapComponent && contribuable.latitude && contribuable.longitude) {
      this.mapComponent.zoomToPoint(
        parseFloat(contribuable.latitude),
        parseFloat(contribuable.longitude)
      );
    }
  }

  toggleFilters(): void {
    this.showFilters = !this.showFilters;
  }

  toggleResults(): void {
    this.showResults = !this.showResults;
  }

  getStats(): any {
    const total = this.allContribuables.length;
    const payes = this.allContribuables.filter(c => c.a_paye === true).length;
    const nonPayes = this.allContribuables.filter(c => c.a_paye === false).length;
    const filtered = this.filteredContribuables.length;
    
    return { total, payes, nonPayes, filtered };
  }
}

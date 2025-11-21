import { Component, OnInit, inject } from '@angular/core';
import { ApiService } from '../../../services/api.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContenerComponent } from '../../items/contener/contener.component';
import { PaginationComponent } from '../../items/pagination/pagination.component';
import { Taxe } from '../../../interfaces/taxe.interface';
import { ModalComponent } from '../../items/modal/modal.component';
import { CreateTaxeComponent } from '../../items/modals/create-taxe/create-taxe.component';
import { DetailsTaxesComponent } from '../../items/modals/details-taxes/details-taxes.component';
import { DecimalPipe } from '@angular/common';

@Component({
  selector: 'app-taxes',
  imports: [CommonModule, FormsModule, ContenerComponent, PaginationComponent, ModalComponent, CreateTaxeComponent, DetailsTaxesComponent, DecimalPipe],
  standalone: true,
  templateUrl: './taxes.component.html',
  styleUrl: './taxes.component.scss'
})
export class TaxesComponent implements OnInit {
  private apiService = inject(ApiService);
  
  taxes: Taxe[] = [];
  allTaxes: Taxe[] = []; // Pour le filtrage côté client
  loading: boolean = true;
  searchTerm: string = '';
  activeModal: boolean = false;
  activeModalEdit: boolean = false;
  activeModalDetails: boolean = false;
  selectedTaxe: Taxe | null = null;
  
  // Pagination
  currentPage: number = 1;
  pageSize: number = 10;
  totalItems: number = 0;
  totalPages: number = 1;

  ngOnInit(): void {
    this.loadTaxes();
  }

  loadTaxes(): void {
    this.loading = true;
    // Charger toutes les taxes pour le filtrage
    const params: any = { 
      limit: 1000  // Charger toutes les taxes
    };
    
    this.apiService.getTaxes(params).subscribe({
      next: (data: Taxe[]) => {
        this.allTaxes = data;
        this.totalItems = data.length;
        this.applyFilters();
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des taxes:', err);
        this.loading = false;
      }
    });
  }

  applyFilters(): void {
    let filtered = this.allTaxes;
    
    if (this.searchTerm) {
      filtered = filtered.filter(t => 
        t.nom.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        t.code.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        (t.description && t.description.toLowerCase().includes(this.searchTerm.toLowerCase()))
      );
    }
    
    this.totalItems = filtered.length;
    this.totalPages = Math.ceil(this.totalItems / this.pageSize);
    
    // Appliquer la pagination
    const startIndex = (this.currentPage - 1) * this.pageSize;
    const endIndex = startIndex + this.pageSize;
    this.taxes = filtered.slice(startIndex, endIndex);
  }

  onSearch(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.applyFilters(); // Appliquer les filtres avec la nouvelle page
  }

  onPageSizeChange(size: number): void {
    this.pageSize = size;
    this.currentPage = 1;
    this.loadTaxes();
  }

  onActiveModal(value: boolean): void {
    this.activeModal = value;
    if (!value) {
      this.loadTaxes(); // Recharger après fermeture
    }
  }

  onActiveModalDetails(value: boolean, taxe?: Taxe): void {
    this.selectedTaxe = taxe || null;
    this.activeModalDetails = value;
  }

  viewDetails(taxe: Taxe): void {
    this.selectedTaxe = taxe;
    this.activeModalDetails = true;
  }

  onActiveModalEdit(value: boolean): void {
    this.activeModalEdit = value;
    if (!value) {
      this.selectedTaxe = null;
      this.loadTaxes(); // Recharger après fermeture
    }
  }

  editTaxe(taxe: Taxe): void {
    this.selectedTaxe = taxe;
    this.activeModalEdit = true;
  }

  toggleActif(taxe: Taxe): void {
    this.apiService.updateTaxe(taxe.id, { actif: !taxe.actif }).subscribe({
      next: () => {
        this.loadTaxes();
      },
      error: (err) => {
        console.error('Erreur lors de la mise à jour:', err);
      }
    });
  }

  deleteTaxe(taxe: Taxe): void {
    if (confirm(`Êtes-vous sûr de vouloir supprimer la taxe "${taxe.nom}" ?`)) {
      this.apiService.deleteTaxe(taxe.id).subscribe({
        next: () => {
          this.loadTaxes();
        },
        error: (err) => {
          console.error('Erreur lors de la suppression:', err);
        }
      });
    }
  }

  getPeriodiciteLabel(periodicite: string): string {
    const labels: { [key: string]: string } = {
      'journaliere': 'Journalière',
      'hebdomadaire': 'Hebdomadaire',
      'mensuelle': 'Mensuelle',
      'trimestrielle': 'Trimestrielle'
    };
    return labels[periodicite] || periodicite;
  }

  formatNumber(value: number): string {
    if (isNaN(value) || value === null || value === undefined) {
      return '0';
    }
    return new Intl.NumberFormat('fr-FR', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  }
}


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

@Component({
  selector: 'app-taxes',
  imports: [CommonModule, FormsModule, ContenerComponent, PaginationComponent, ModalComponent, CreateTaxeComponent, DetailsTaxesComponent],
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
    const params: any = { 
      skip: (this.currentPage - 1) * this.pageSize,
      limit: this.pageSize
    };
    
    this.apiService.getTaxes(params).subscribe({
      next: (data: Taxe[]) => {
        this.allTaxes = data;
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
        t.code.toLowerCase().includes(this.searchTerm.toLowerCase())
      );
    }
    
    this.taxes = filtered;
    this.totalItems = filtered.length;
    this.totalPages = Math.ceil(this.totalItems / this.pageSize);
  }

  onSearch(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadTaxes();
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
}


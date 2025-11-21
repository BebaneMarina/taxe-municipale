import { Component, OnInit, inject } from '@angular/core';
import { ApiService } from '../../../services/api.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ContenerComponent } from '../../items/contener/contener.component';
import { PaginationComponent } from '../../items/pagination/pagination.component';
import { Collecteur } from '../../../interfaces/collecteur.interface';

@Component({
  selector: 'app-gestion-collecteurs',
  imports: [CommonModule, FormsModule, ContenerComponent, PaginationComponent],
  standalone: true,
  templateUrl: './gestion-collecteurs.component.html',
  styleUrl: './gestion-collecteurs.component.scss'
})
export class GestionCollecteursComponent implements OnInit {
  private apiService = inject(ApiService);
  
  collecteurs: Collecteur[] = [];
  loading: boolean = true;
  searchTerm: string = '';
  
  // Pagination
  currentPage: number = 1;
  pageSize: number = 10;
  totalItems: number = 0;
  totalPages: number = 1;

  ngOnInit(): void {
    this.loadCollecteurs();
  }

  loadCollecteurs(): void {
    this.loading = true;
    const params: any = { 
      skip: (this.currentPage - 1) * this.pageSize,
      limit: this.pageSize
    };
    if (this.searchTerm) {
      params.search = this.searchTerm;
    }
    
    this.apiService.getCollecteurs(params).subscribe({
      next: (data: Collecteur[]) => {
        this.collecteurs = data;
        this.totalItems = data.length === this.pageSize ? (this.currentPage * this.pageSize) + 1 : (this.currentPage - 1) * this.pageSize + data.length;
        this.totalPages = Math.ceil(this.totalItems / this.pageSize);
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des collecteurs:', err);
        this.loading = false;
      }
    });
  }

  onSearch(): void {
    this.currentPage = 1;
    this.loadCollecteurs();
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadCollecteurs();
  }

  onPageSizeChange(size: number): void {
    this.pageSize = size;
    this.currentPage = 1;
    this.loadCollecteurs();
  }

  toggleStatut(collecteur: Collecteur): void {
    const newStatut = collecteur.statut === 'active' ? 'desactive' : 'active';
    this.apiService.updateCollecteur(collecteur.id, { statut: newStatut }).subscribe({
      next: () => {
        this.loadCollecteurs();
      },
      error: (err) => {
        console.error('Erreur lors de la mise à jour:', err);
      }
    });
  }

  toggleConnexion(collecteur: Collecteur): void {
    if (collecteur.etat === 'connecte') {
      this.apiService.deconnexionCollecteur(collecteur.id).subscribe({
        next: () => {
          this.loadCollecteurs();
        },
        error: (err) => {
          console.error('Erreur lors de la déconnexion:', err);
        }
      });
    } else {
      this.apiService.connexionCollecteur(collecteur.id).subscribe({
        next: () => {
          this.loadCollecteurs();
        },
        error: (err) => {
          console.error('Erreur lors de la connexion:', err);
        }
      });
    }
  }

  getStatutBadgeClass(statut: string): string {
    return statut === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
  }

  getEtatBadgeClass(etat: string): string {
    return etat === 'connecte' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800';
  }
}

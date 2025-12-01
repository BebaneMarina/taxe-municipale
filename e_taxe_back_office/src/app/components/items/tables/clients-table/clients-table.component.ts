import {Component, model, ModelSignal, OnInit, inject, Output, EventEmitter} from '@angular/core';
import {hiddenLetters, dateFormater} from '../../../../utils/utils';
import {paiementLogo} from '../../../../utils/seeder';
import { BadgeComponent } from "../../badge/badge.component";
import { ModalComponent } from "../../modal/modal.component";
import { CreateClientComponent } from "../../modals/create-client/create-client.component";
import { DetailsTaxesComponent } from "../../modals/details-taxes/details-taxes.component";
import { PaginationComponent } from "../../pagination/pagination.component";
import {ApiService} from '../../../../services/api.service';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {Contribuable} from '../../../../interfaces/contribuable.interface';

@Component({
  selector: 'app-clients-table',
  standalone : true,
  imports: [BadgeComponent, ModalComponent, CreateClientComponent, DetailsTaxesComponent, CommonModule, FormsModule, PaginationComponent],
  templateUrl: './clients-table.component.html',
  styleUrl: './clients-table.component.scss'
})
export class ClientsTableComponent implements OnInit {
[x: string]: any;
  activeModal : ModelSignal<boolean> = model<boolean>(false);
  activeModalDetailsTaxe:ModelSignal<boolean> = model<boolean>(false);
  activeModalQRCode: ModelSignal<boolean> = model<boolean>(false);
  
  @Output() clientCreated = new EventEmitter<void>();
  
  private apiService = inject(ApiService);
  
  selectedContribuable: Contribuable | null = null;
  qrCodeImageUrl: string = '';
  generatingQR: boolean = false;
  downloadingQR: boolean = false;
  loadingQRImage: boolean = false;
  
  contribuables: Contribuable[] = [];
  loading: boolean = true;
  searchTerm: string = '';
  
  // Pagination
  currentPage: number = 1;
  pageSize: number = 10;
  totalItems: number = 0;
  totalPages: number = 1;

  protected readonly hiddenLetters = hiddenLetters;
  protected readonly paiementLogo = paiementLogo;
  protected readonly dateFormater = dateFormater;

  ngOnInit(): void {
    this.loadContribuables();
  }

  loadContribuables(): void {
    this.loading = true;
    const params: any = { 
      skip: (this.currentPage - 1) * this.pageSize,
      limit: this.pageSize
    };
    if (this.searchTerm) {
      params.search = this.searchTerm;
    }
    
    this.apiService.getContribuables(params).subscribe({
      next: (data: Contribuable[]) => {
        this.contribuables = data;
        // Pour l'instant, on estime le total. Dans un vrai cas, l'API devrait retourner le total
        this.totalItems = data.length === this.pageSize ? (this.currentPage * this.pageSize) + 1 : (this.currentPage - 1) * this.pageSize + data.length;
        this.totalPages = Math.ceil(this.totalItems / this.pageSize);
        this.loading = false;
      },
      error: (err) => {
        console.error('Erreur lors du chargement des contribuables:', err);
        this.loading = false;
      }
    });
  }

  onSearch(): void {
    this.currentPage = 1;
    this.loadContribuables();
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadContribuables();
  }

  onPageSizeChange(size: number): void {
    this.pageSize = size;
    this.currentPage = 1;
    this.loadContribuables();
  }

  onActiveModal(value : boolean) : void
  {
    this.activeModal.set(value);
  }
  
  onactiveModalDetailsTaxe(value : boolean):void{
    this.activeModalDetailsTaxe.set(value);
  }

  onClientCreated(): void {
    this.clientCreated.emit();
    this.activeModal.set(false);
    this.loadContribuables();
  }

  showQRCode(contribuable: Contribuable): void {
    this.selectedContribuable = contribuable;
    if (contribuable.qr_code) {
      this.loadQRCodeImage(contribuable.id);
      this.activeModalQRCode.set(true);
    } else {
      this.generateQRCode(contribuable);
    }
  }

  loadQRCodeImage(contribuableId: number): void {
    this.loadingQRImage = true;
    this.apiService.getQRCodeImage(contribuableId, 400, true).subscribe({
      next: (blob: Blob) => {
        this.loadingQRImage = false;
        // Créer une URL blob pour l'image
        this.qrCodeImageUrl = window.URL.createObjectURL(blob);
      },
      error: (err) => {
        console.error('Erreur lors du chargement de l\'image QR code:', err);
        this.loadingQRImage = false;
        alert('Erreur lors du chargement de l\'image QR code');
      }
    });
  }

  generateQRCode(contribuable: Contribuable): void {
    this.generatingQR = true;
    this.apiService.generateQRCode(contribuable.id).subscribe({
      next: (response) => {
        this.generatingQR = false;
        if (response.qr_code) {
          contribuable.qr_code = response.qr_code;
          this.loadQRCodeImage(contribuable.id);
          this.activeModalQRCode.set(true);
        }
      },
      error: (err) => {
        console.error('Erreur lors de la génération du QR code:', err);
        this.generatingQR = false;
        alert('Erreur lors de la génération du QR code');
      }
    });
  }

  downloadQRCode(): void {
    if (!this.selectedContribuable) return;
    
    this.downloadingQR = true;
    this.apiService.downloadQRCode(this.selectedContribuable.id, 400, true).subscribe({
      next: (blob: Blob) => {
        this.downloadingQR = false;
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        const nomComplet = `${this.selectedContribuable?.nom}_${this.selectedContribuable?.prenom || ''}`.trim().replace(' ', '_');
        link.download = `QR_Code_${nomComplet}_${this.selectedContribuable?.id}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      },
      error: (err) => {
        console.error('Erreur lors du téléchargement du QR code:', err);
        this.downloadingQR = false;
        alert('Erreur lors du téléchargement du QR code');
      }
    });
  }

  closeQRCodeModal(): void {
    // Libérer l'URL blob pour éviter les fuites mémoire
    if (this.qrCodeImageUrl) {
      window.URL.revokeObjectURL(this.qrCodeImageUrl);
    }
    this.activeModalQRCode.set(false);
    this.selectedContribuable = null;
    this.qrCodeImageUrl = '';
  }

  handleImageError(event: any): void {
    console.error('Erreur lors du chargement de l\'image QR code:', event);
    alert('Erreur lors de l\'affichage de l\'image QR code');
  }
}

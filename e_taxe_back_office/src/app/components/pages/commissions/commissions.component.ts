import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../services/api.service';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-commissions',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './commissions.component.html',
  styleUrl: './commissions.component.scss'
})
export class CommissionsComponent implements OnInit {
  private apiService = inject(ApiService);
  private readonly backendBaseUrl = environment.apiUrl.replace(/\/api\/?$/, '');
  private readonly uploadsBaseUrl = `${this.backendBaseUrl}/uploads`;

  today = new Date().toISOString().substring(0, 10);
  selectedDate = this.today;
  selectedFormat: 'json' | 'csv' | 'pdf' = 'json';
  formats = [
    { label: 'JSON (technique)', value: 'json' },
    { label: 'CSV (Excel)', value: 'csv' },
    { label: 'PDF (lecture)', value: 'pdf' },
  ];

  files = signal<any[]>([]);
  commissions = signal<any[]>([]);
  generating = signal<boolean>(false);
  loading = signal<boolean>(true);
  loadingCommissions = signal<boolean>(false);
  message = signal<string | null>(null);

  ngOnInit(): void {
    this.loadFiles();
    this.loadCommissions();
  }

  loadFiles(): void {
    this.loading.set(true);
    this.apiService.listCommissionFiles().subscribe({
      next: (items) => {
        this.files.set(items || []);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.message.set("Impossible de charger les fichiers de commission");
      }
    });
  }

  getFileUrl(file: any): string {
    const chemin: string = file?.chemin || '';
    const normalized = chemin.startsWith('/') ? chemin.slice(1) : chemin;
    return `${this.uploadsBaseUrl}/${normalized}`;
  }

  generateFile(): void {
    this.generating.set(true);
    this.message.set(null);
    this.apiService.genererCommissions(this.selectedDate, this.selectedFormat).subscribe({
      next: () => {
        this.generating.set(false);
        this.message.set(`Fichier ${this.selectedFormat.toUpperCase()} généré`);
        this.loadFiles();
        this.loadCommissions();
      },
      error: (err) => {
        this.generating.set(false);
        this.message.set(err?.error?.detail || "Échec de la génération");
      }
    });
  }

  loadCommissions(): void {
    this.loadingCommissions.set(true);
    this.apiService.getCommissionsDetails(this.selectedDate).subscribe({
      next: (data) => {
        this.commissions.set(data || []);
        this.loadingCommissions.set(false);
      },
      error: () => {
        this.commissions.set([]);
        this.loadingCommissions.set(false);
      }
    });
  }
}


import { CommonModule } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../../services/api.service';

@Component({
  selector: 'app-journal-caisse',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './journal-caisse.component.html',
  styleUrl: './journal-caisse.component.scss'
})
export class JournalCaisseComponent implements OnInit {
  private apiService = inject(ApiService);

  caisses: any[] = [];
  operations: any[] = [];
  selectedId: number | undefined;
  message: string | null = null;

  ngOnInit(): void {
    this.apiService.getCaisses({ limit: 50 }).subscribe({
      next: (res) => {
        this.caisses = res?.items || [];
        if (this.caisses.length) {
          this.selectedId = this.caisses[0].id;
          this.loadOperations();
        }
      },
      error: () => this.message = 'Impossible de charger les caisses',
    });
  }

  loadOperations(): void {
    if (!this.selectedId) {
      return;
    }
    this.apiService.getOperationsCaisse(this.selectedId, { limit: 50 }).subscribe({
      next: (ops) => this.operations = ops || [],
      error: () => this.message = 'Impossible de charger les opérations'
    });
  }

  get selectedCaisse() {
    return this.caisses.find(c => c.id === this.selectedId);
  }
}


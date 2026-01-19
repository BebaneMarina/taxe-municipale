import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../services/api.service';

@Component({
  selector: 'app-travaux',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './travaux.component.html',
  styleUrl: './travaux.component.scss'
})
export class TravauxComponent implements OnInit {
  private apiService = inject(ApiService);

  today = new Date().toISOString().substring(0, 10);
  selectedDate = this.today;

  loading = signal<boolean>(true);
  closing = signal<boolean>(false);
  journal = signal<any | null>(null);
  message = signal<string | null>(null);
  
  collectes = signal<any[]>([]);
  operations = signal<any[]>([]);
  relances = signal<any[]>([]);
  loadingDetails = signal<boolean>(false);

  ngOnInit(): void {
    this.loadJournal();
  }

  loadJournal(): void {
    this.loading.set(true);
    this.loadingDetails.set(true);
    this.message.set(null);
    this.apiService.getJournalCurrent(this.selectedDate).subscribe({
      next: (response) => {
        this.journal.set(response);
        this.loading.set(false);
        this.loadDetails();
      },
      error: (err) => {
        this.loading.set(false);
        this.loadingDetails.set(false);
        this.message.set(err?.error?.detail || 'Impossible de charger les travaux du jour');
      }
    });
  }

  loadDetails(): void {
    this.loadingDetails.set(true);
    const dateStr = this.selectedDate;
    
    // Charger collectes
    this.apiService.getCollectesJour(dateStr).subscribe({
      next: (data) => this.collectes.set(data || []),
      error: () => this.collectes.set([])
    });
    
    // Charger opérations
    this.apiService.getOperationsJour(dateStr).subscribe({
      next: (data) => this.operations.set(data || []),
      error: () => this.operations.set([])
    });
    
    // Charger relances
    this.apiService.getRelancesJour(dateStr).subscribe({
      next: (data) => {
        this.relances.set(data || []);
        this.loadingDetails.set(false);
      },
      error: () => {
        this.relances.set([]);
        this.loadingDetails.set(false);
      }
    });
  }

  cloturerJournee(): void {
    this.closing.set(true);
    this.message.set(null);
    this.apiService.cloturerJournal(this.selectedDate).subscribe({
      next: (response) => {
        this.journal.set(response);
        this.closing.set(false);
        this.message.set('La journée a été clôturée avec succès.');
      },
      error: (err) => {
        this.closing.set(false);
        this.message.set(err?.error?.detail || 'Échec de la clôture');
      }
    });
  }
}

